"""
Property Name Audit Script

Audits all existing documents in MinIO and database to validate property names.
Generates a comprehensive report of mismatches and recommendations.
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import sqlite3
from datetime import datetime

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from utils.validation_integration import ValidationIntegration
from utils.property_name_extractor import PropertyNameExtractor
from utils.alias_resolver import AliasResolver

logger = logging.getLogger(__name__)

class PropertyNameAuditor:
    """Audits property names across all documents and database"""
    
    def __init__(self, db_path: str = "reims.db"):
        self.db_path = db_path
        self.validation_integration = ValidationIntegration(db_path)
        self.extractor = PropertyNameExtractor()
        self.alias_resolver = AliasResolver(db_path)
    
    def audit_all_documents(self) -> Dict[str, Any]:
        """Audit all documents in the system"""
        print("🔍 Starting property name audit...")
        
        # Get all documents from database
        documents = self._get_all_documents()
        print(f"📄 Found {len(documents)} documents to audit")
        
        # Get all properties from database
        properties = self._get_all_properties()
        print(f"🏢 Found {len(properties)} properties in database")
        
        # Audit each document
        audit_results = {
            'total_documents': len(documents),
            'total_properties': len(properties),
            'audit_timestamp': datetime.now().isoformat(),
            'documents_audited': [],
            'property_mismatches': [],
            'recommendations': [],
            'statistics': {
                'exact_matches': 0,
                'fuzzy_matches': 0,
                'mismatches': 0,
                'extraction_failures': 0,
                'needs_review': 0
            }
        }
        
        for i, doc in enumerate(documents, 1):
            print(f"🔍 Auditing document {i}/{len(documents)}: {doc['original_filename']}")
            
            try:
                # Extract property name from document
                extraction_result = self.extractor.extract_from_pdf(doc['file_path'])
                if extraction_result:
                    extraction_result = extraction_result[0] if extraction_result else None
                
                if not extraction_result:
                    audit_results['statistics']['extraction_failures'] += 1
                    audit_results['documents_audited'].append({
                        'document_id': doc['document_id'],
                        'filename': doc['original_filename'],
                        'status': 'extraction_failed',
                        'message': 'Could not extract property name',
                        'needs_review': True
                    })
                    continue
                
                # Validate against database
                validation_result = self.validation_integration.validator.validate_property_name(
                    extraction_result.name,
                    doc['document_id'],
                    doc.get('property_id')
                )
                
                # Record audit result
                audit_result = {
                    'document_id': doc['document_id'],
                    'filename': doc['original_filename'],
                    'extracted_name': extraction_result.name,
                    'database_name': validation_result.database_name,
                    'property_id': validation_result.property_id,
                    'confidence': validation_result.confidence,
                    'status': validation_result.status,
                    'needs_review': validation_result.needs_review,
                    'suggestions': validation_result.suggestions
                }
                
                audit_results['documents_audited'].append(audit_result)
                
                # Update statistics
                if validation_result.status == 'exact':
                    audit_results['statistics']['exact_matches'] += 1
                elif validation_result.status == 'fuzzy':
                    audit_results['statistics']['fuzzy_matches'] += 1
                elif validation_result.status == 'mismatch':
                    audit_results['statistics']['mismatches'] += 1
                
                if validation_result.needs_review:
                    audit_results['statistics']['needs_review'] += 1
                
                # Check for property mismatches
                if validation_result.status == 'mismatch':
                    audit_results['property_mismatches'].append({
                        'document_id': doc['document_id'],
                        'filename': doc['original_filename'],
                        'extracted_name': extraction_result.name,
                        'expected_property': doc.get('property_name', 'Unknown'),
                        'confidence': validation_result.confidence,
                        'suggestions': validation_result.suggestions
                    })
                
            except Exception as e:
                logger.error(f"Error auditing document {doc['document_id']}: {e}")
                audit_results['documents_audited'].append({
                    'document_id': doc['document_id'],
                    'filename': doc['original_filename'],
                    'status': 'error',
                    'message': f'Audit error: {str(e)}',
                    'needs_review': True
                })
                audit_results['statistics']['extraction_failures'] += 1
        
        # Generate recommendations
        audit_results['recommendations'] = self._generate_recommendations(audit_results)
        
        return audit_results
    
    def _get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    d.document_id, d.original_filename, d.file_path, d.property_id,
                    p.name as property_name
                FROM documents d
                LEFT JOIN properties p ON d.property_id = p.id
                ORDER BY d.upload_timestamp DESC
            """)
            
            documents = []
            for row in cursor.fetchall():
                documents.append({
                    'document_id': row[0],
                    'original_filename': row[1],
                    'file_path': row[2],
                    'property_id': row[3],
                    'property_name': row[4]
                })
            
            conn.close()
            return documents
            
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            return []
    
    def _get_all_properties(self) -> List[Dict[str, Any]]:
        """Get all properties from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, address, city, state
                FROM properties
                ORDER BY id
            """)
            
            properties = []
            for row in cursor.fetchall():
                properties.append({
                    'id': row[0],
                    'name': row[1],
                    'address': row[2],
                    'city': row[3],
                    'state': row[4]
                })
            
            conn.close()
            return properties
            
        except Exception as e:
            logger.error(f"Error getting properties: {e}")
            return []
    
    def _generate_recommendations(self, audit_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on audit results"""
        recommendations = []
        
        # Check for common mismatches
        mismatches = audit_results['property_mismatches']
        if mismatches:
            # Group by extracted name
            name_groups = {}
            for mismatch in mismatches:
                name = mismatch['extracted_name']
                if name not in name_groups:
                    name_groups[name] = []
                name_groups[name].append(mismatch)
            
            # Generate recommendations for each group
            for extracted_name, docs in name_groups.items():
                if len(docs) > 1:  # Multiple documents with same extracted name
                    recommendations.append({
                        'type': 'bulk_alias',
                        'priority': 'high',
                        'title': f'Add alias for "{extracted_name}"',
                        'description': f'Found {len(docs)} documents with property name "{extracted_name}"',
                        'action': f'Add alias "{extracted_name}" to appropriate property',
                        'affected_documents': len(docs)
                    })
        
        # Check for low confidence matches
        low_confidence = [
            doc for doc in audit_results['documents_audited']
            if doc.get('confidence', 0) < 0.8 and doc.get('status') != 'extraction_failed'
        ]
        
        if low_confidence:
            recommendations.append({
                'type': 'manual_review',
                'priority': 'medium',
                'title': 'Review low confidence matches',
                'description': f'Found {len(low_confidence)} documents with low confidence matches',
                'action': 'Manually review and correct property assignments',
                'affected_documents': len(low_confidence)
            })
        
        # Check for extraction failures
        extraction_failures = audit_results['statistics']['extraction_failures']
        if extraction_failures > 0:
            recommendations.append({
                'type': 'extraction_improvement',
                'priority': 'medium',
                'title': 'Improve property name extraction',
                'description': f'Failed to extract property names from {extraction_failures} documents',
                'action': 'Review extraction patterns and improve PDF text extraction',
                'affected_documents': extraction_failures
            })
        
        return recommendations
    
    def generate_report(self, audit_results: Dict[str, Any]) -> str:
        """Generate human-readable audit report"""
        report = []
        report.append("=" * 80)
        report.append("PROPERTY NAME AUDIT REPORT")
        report.append("=" * 80)
        report.append(f"Audit Date: {audit_results['audit_timestamp']}")
        report.append(f"Total Documents: {audit_results['total_documents']}")
        report.append(f"Total Properties: {audit_results['total_properties']}")
        report.append("")
        
        # Statistics
        stats = audit_results['statistics']
        report.append("AUDIT STATISTICS:")
        report.append(f"  Exact Matches: {stats['exact_matches']}")
        report.append(f"  Fuzzy Matches: {stats['fuzzy_matches']}")
        report.append(f"  Mismatches: {stats['mismatches']}")
        report.append(f"  Extraction Failures: {stats['extraction_failures']}")
        report.append(f"  Needs Review: {stats['needs_review']}")
        report.append("")
        
        # Success rate
        total_processed = stats['exact_matches'] + stats['fuzzy_matches'] + stats['mismatches']
        if total_processed > 0:
            success_rate = (stats['exact_matches'] + stats['fuzzy_matches']) / total_processed
            report.append(f"SUCCESS RATE: {success_rate:.1%}")
        else:
            report.append("SUCCESS RATE: N/A (no documents processed)")
        report.append("")
        
        # Property mismatches
        if audit_results['property_mismatches']:
            report.append("PROPERTY MISMATCHES:")
            for mismatch in audit_results['property_mismatches']:
                report.append(f"  Document: {mismatch['filename']}")
                report.append(f"    Extracted: {mismatch['extracted_name']}")
                report.append(f"    Expected: {mismatch['expected_property']}")
                report.append(f"    Confidence: {mismatch['confidence']:.2f}")
                report.append("")
        
        # Recommendations
        if audit_results['recommendations']:
            report.append("RECOMMENDATIONS:")
            for i, rec in enumerate(audit_results['recommendations'], 1):
                report.append(f"  {i}. {rec['title']} ({rec['priority']} priority)")
                report.append(f"     {rec['description']}")
                report.append(f"     Action: {rec['action']}")
                report.append("")
        
        return "\n".join(report)
    
    def save_audit_results(self, audit_results: Dict[str, Any], filename: str = None):
        """Save audit results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"property_name_audit_{timestamp}.json"
        
        import json
        
        with open(filename, 'w') as f:
            json.dump(audit_results, f, indent=2, default=str)
        
        print(f"📄 Audit results saved to: {filename}")
        return filename

def main():
    """Main audit function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Audit property names in REIMS system')
    parser.add_argument('--db', default='reims.db', help='Database path')
    parser.add_argument('--output', help='Output file for audit results')
    parser.add_argument('--report', help='Generate human-readable report file')
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run audit
    auditor = PropertyNameAuditor(args.db)
    audit_results = auditor.audit_all_documents()
    
    # Save results
    if args.output:
        auditor.save_audit_results(audit_results, args.output)
    else:
        auditor.save_audit_results(audit_results)
    
    # Generate report
    report = auditor.generate_report(audit_results)
    print("\n" + report)
    
    if args.report:
        with open(args.report, 'w') as f:
            f.write(report)
        print(f"📄 Report saved to: {args.report}")

if __name__ == "__main__":
    main()

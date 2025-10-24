"""
CLI Validation Tool
Command-line tool for validating imports
"""

import argparse
import sys
from backend.utils.rentroll_validator import RentRollValidator
from backend.utils.document_validator import DocumentValidator


def main():
    parser = argparse.ArgumentParser(
        description='Validate data import from MinIO file to database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate rent roll import
  python validate_import.py --property-id 3 --document-type rent_roll --file "Financial Statements/2025/Rent Rolls/Hammond Rent Roll April 2025.pdf"
  
  # Validate financial statement
  python validate_import.py --property-id 3 --document-type financial_statement --file "Financial Statements/2024/Balance Sheets/Hammond Aire 2024 Balance Sheet.pdf"
  
  # Save validation report
  python validate_import.py --property-id 3 --document-type rent_roll --file "..." --output report.json
        """
    )
    
    parser.add_argument(
        '--property-id',
        type=int,
        required=True,
        help='Property ID in database'
    )
    
    parser.add_argument(
        '--document-type',
        choices=['rent_roll', 'financial_statement', 'lease', 'document'],
        required=True,
        help='Type of document to validate'
    )
    
    parser.add_argument(
        '--file',
        required=True,
        help='File path in MinIO (e.g., "Financial Statements/2025/Rent Rolls/file.pdf")'
    )
    
    parser.add_argument(
        '--output',
        help='Output path for validation report (optional)'
    )
    
    parser.add_argument(
        '--db',
        default='reims.db',
        help='Path to database file (default: reims.db)'
    )
    
    args = parser.parse_args()
    
    print(f"\n{'='*80}")
    print(f"IMPORT VALIDATION TOOL")
    print(f"{'='*80}")
    print(f"Property ID: {args.property_id}")
    print(f"Document Type: {args.document_type}")
    print(f"File: {args.file}")
    print(f"Database: {args.db}")
    print(f"{'='*80}\n")
    
    # Select appropriate validator
    if args.document_type == 'rent_roll':
        validator = RentRollValidator(
            minio_file_path=args.file,
            property_id=args.property_id,
            db_path=args.db
        )
    else:
        validator = DocumentValidator(
            minio_file_path=args.file,
            property_id=args.property_id,
            db_path=args.db
        )
    
    # Run validation
    try:
        report = validator.validate_all()
        
        # Save report if requested
        if args.output:
            validator.save_report(args.output)
        
        # Exit with appropriate code
        if report.passed:
            print("\n✅ VALIDATION PASSED - Import is accurate")
            sys.exit(0)
        else:
            print("\n❌ VALIDATION FAILED - Import has discrepancies")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ ERROR: Validation failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()






"""
Property Name Alias Resolution Module

Resolves property names using aliases and abbreviations to match documents
to the correct properties in the database.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
import sqlite3

logger = logging.getLogger(__name__)

@dataclass
class AliasMatch:
    """Result of alias resolution"""
    property_id: int
    property_name: str
    matched_alias: str
    alias_type: str
    confidence: float
    match_method: str  # 'exact', 'fuzzy', 'abbreviation', 'alias'

class AliasResolver:
    """Resolves property names using aliases and abbreviations"""
    
    def __init__(self, db_path: str = "reims.db"):
        self.db_path = db_path
    
    def resolve_property_name(self, name: str) -> Optional[AliasMatch]:
        """
        Resolve a property name using aliases and abbreviations
        
        Args:
            name: Property name to resolve
            
        Returns:
            AliasMatch if found, None otherwise
        """
        try:
            # Clean the input name
            cleaned_name = name.strip()
            
            # Try exact match first
            exact_match = self._find_exact_match(cleaned_name)
            if exact_match:
                return exact_match
            
            # Try fuzzy match
            fuzzy_match = self._find_fuzzy_match(cleaned_name)
            if fuzzy_match:
                return fuzzy_match
            
            # Try abbreviation resolution
            abbr_match = self._resolve_abbreviation(cleaned_name)
            if abbr_match:
                return abbr_match
            
            return None
            
        except Exception as e:
            logger.error(f"Error resolving property name '{name}': {e}")
            return None
    
    def _find_exact_match(self, name: str) -> Optional[AliasMatch]:
        """Find exact match in aliases"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Look for exact match in aliases
            cursor.execute("""
                SELECT pna.property_id, p.name, pna.alias_name, pna.alias_type
                FROM property_name_aliases pna
                JOIN properties p ON pna.property_id = p.id
                WHERE LOWER(pna.alias_name) = LOWER(?)
            """, (name,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return AliasMatch(
                    property_id=row[0],
                    property_name=row[1],
                    matched_alias=row[2],
                    alias_type=row[3],
                    confidence=1.0,
                    match_method='exact'
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in exact match lookup: {e}")
            return None
    
    def _find_fuzzy_match(self, name: str) -> Optional[AliasMatch]:
        """Find fuzzy match in aliases"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all aliases
            cursor.execute("""
                SELECT pna.property_id, p.name, pna.alias_name, pna.alias_type
                FROM property_name_aliases pna
                JOIN properties p ON pna.property_id = p.id
            """)
            
            aliases = cursor.fetchall()
            conn.close()
            
            best_match = None
            best_confidence = 0.0
            
            for property_id, property_name, alias_name, alias_type in aliases:
                similarity = self._calculate_similarity(name, alias_name)
                
                if similarity > 0.8 and similarity > best_confidence:
                    best_confidence = similarity
                    best_match = AliasMatch(
                        property_id=property_id,
                        property_name=property_name,
                        matched_alias=alias_name,
                        alias_type=alias_type,
                        confidence=similarity,
                        match_method='fuzzy'
                    )
            
            return best_match
            
        except Exception as e:
            logger.error(f"Error in fuzzy match lookup: {e}")
            return None
    
    def _resolve_abbreviation(self, name: str) -> Optional[AliasMatch]:
        """Resolve abbreviation to full property name"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Look for abbreviation match
            cursor.execute("""
                SELECT pna.property_id, p.name, pna.alias_name, pna.alias_type
                FROM property_name_aliases pna
                JOIN properties p ON pna.property_id = p.id
                WHERE pna.alias_type = 'abbreviation'
                AND LOWER(pna.alias_name) = LOWER(?)
            """, (name,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return AliasMatch(
                    property_id=row[0],
                    property_name=row[1],
                    matched_alias=row[2],
                    alias_type=row[3],
                    confidence=0.9,
                    match_method='abbreviation'
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in abbreviation resolution: {e}")
            return None
    
    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names"""
        from difflib import SequenceMatcher
        
        # Normalize names
        norm1 = name1.lower().strip()
        norm2 = name2.lower().strip()
        
        # Sequence matcher similarity
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Check for substring matches
        if norm1 in norm2 or norm2 in norm1:
            similarity = max(similarity, 0.8)
        
        return similarity
    
    def get_property_aliases(self, property_id: int) -> List[Dict[str, Any]]:
        """Get all aliases for a property"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT alias_name, alias_type, is_primary
                FROM property_name_aliases
                WHERE property_id = ?
                ORDER BY is_primary DESC, alias_type, alias_name
            """, (property_id,))
            
            aliases = []
            for row in cursor.fetchall():
                aliases.append({
                    'alias_name': row[0],
                    'alias_type': row[1],
                    'is_primary': bool(row[2])
                })
            
            conn.close()
            return aliases
            
        except Exception as e:
            logger.error(f"Error getting aliases for property {property_id}: {e}")
            return []
    
    def add_alias(self, property_id: int, alias_name: str, alias_type: str = 'common_name') -> bool:
        """Add a new alias for a property"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO property_name_aliases 
                (property_id, alias_name, alias_type, is_primary)
                VALUES (?, ?, ?, FALSE)
            """, (property_id, alias_name, alias_type))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Added alias '{alias_name}' for property {property_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding alias '{alias_name}' for property {property_id}: {e}")
            return False
    
    def remove_alias(self, property_id: int, alias_name: str) -> bool:
        """Remove an alias for a property"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM property_name_aliases 
                WHERE property_id = ? AND alias_name = ?
            """, (property_id, alias_name))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Removed alias '{alias_name}' for property {property_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing alias '{alias_name}' for property {property_id}: {e}")
            return False
    
    def get_all_aliases(self) -> Dict[int, List[Dict[str, Any]]]:
        """Get all aliases for all properties"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT property_id, alias_name, alias_type, is_primary
                FROM property_name_aliases
                ORDER BY property_id, is_primary DESC, alias_type, alias_name
            """)
            
            aliases_by_property = {}
            for row in cursor.fetchall():
                property_id = row[0]
                if property_id not in aliases_by_property:
                    aliases_by_property[property_id] = []
                
                aliases_by_property[property_id].append({
                    'alias_name': row[1],
                    'alias_type': row[2],
                    'is_primary': bool(row[3])
                })
            
            conn.close()
            return aliases_by_property
            
        except Exception as e:
            logger.error(f"Error getting all aliases: {e}")
            return {}
    
    def search_aliases(self, search_term: str) -> List[AliasMatch]:
        """Search for properties by alias name"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Search for aliases containing the search term
            cursor.execute("""
                SELECT pna.property_id, p.name, pna.alias_name, pna.alias_type
                FROM property_name_aliases pna
                JOIN properties p ON pna.property_id = p.id
                WHERE LOWER(pna.alias_name) LIKE LOWER(?)
                ORDER BY pna.is_primary DESC, pna.alias_type
            """, (f'%{search_term}%',))
            
            matches = []
            for row in cursor.fetchall():
                similarity = self._calculate_similarity(search_term, row[2])
                
                matches.append(AliasMatch(
                    property_id=row[0],
                    property_name=row[1],
                    matched_alias=row[2],
                    alias_type=row[3],
                    confidence=similarity,
                    match_method='search'
                ))
            
            conn.close()
            
            # Sort by confidence
            return sorted(matches, key=lambda x: x.confidence, reverse=True)
            
        except Exception as e:
            logger.error(f"Error searching aliases: {e}")
            return []

# Convenience functions
def resolve_property_name(name: str) -> Optional[AliasMatch]:
    """Resolve property name using aliases - convenience function"""
    resolver = AliasResolver()
    return resolver.resolve_property_name(name)

def get_property_aliases(property_id: int) -> List[Dict[str, Any]]:
    """Get aliases for a property - convenience function"""
    resolver = AliasResolver()
    return resolver.get_property_aliases(property_id)

def add_property_alias(property_id: int, alias_name: str, alias_type: str = 'common_name') -> bool:
    """Add alias for a property - convenience function"""
    resolver = AliasResolver()
    return resolver.add_alias(property_id, alias_name, alias_type)

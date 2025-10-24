"""
Test ESP Property Name Validation

Tests that ESP documents now validate correctly after the property name fix.
"""

import sys
sys.path.append('backend')
from utils.validation_integration import ValidationIntegration
from utils.alias_resolver import AliasResolver

def test_esp_validation():
    """Test ESP property name validation"""
    
    print("🧪 Testing ESP property name validation...")
    
    # Test alias resolution
    resolver = AliasResolver()
    
    # Test various ESP name variations
    test_names = [
        "Eastern Shore Plaza",
        "ESP", 
        "Eastern Shore",
        "Empire State Plaza"  # Should resolve to Eastern Shore Plaza
    ]
    
    print("\n📋 Testing alias resolution:")
    for name in test_names:
        match = resolver.resolve_property_name(name)
        if match:
            print(f"  '{name}' -> Property {match.property_id}: {match.property_name} (confidence: {match.confidence})")
        else:
            print(f"  '{name}' -> No match")
    
    # Test validation integration
    integration = ValidationIntegration()
    
    print("\n📊 Validation statistics:")
    stats = integration.get_validation_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ ESP validation test completed")

if __name__ == "__main__":
    test_esp_validation()

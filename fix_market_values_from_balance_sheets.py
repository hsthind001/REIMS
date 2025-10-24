#!/usr/bin/env python3
"""
Fix market values in database using correct Property & Equipment values from balance sheets
"""
import sqlite3
from datetime import datetime

# Correct values from balance sheets (Total Property & Equipment)
CORRECT_VALUES = {
    1: {  # Empire State Plaza
        'name': 'Empire State Plaza',
        'property_equipment': 21855251.93,
        'noi': 2087905.14,
        'market_value_noi': 26098814.25  # NOI / 0.08
    },
    2: {  # Wendover Commons
        'name': 'Wendover Commons',
        'property_equipment': 21865409.62,
        'noi': 1860030.71,
        'market_value_noi': 23250383.88  # NOI / 0.08
    },
    3: {  # Hammond Aire
        'name': 'Hammond Aire',
        'property_equipment': 32163869.08,
        'noi': 400000.00,  # Manually corrected value
        'market_value_noi': 5000000.00  # Use manual correction
    },
    6: {  # The Crossings of Spring Hill
        'name': 'The Crossings of Spring Hill',
        'property_equipment': 26693670.71,
        'noi': 280000.00,  # Manually corrected value
        'market_value_noi': 3500000.00  # Use manual correction
    }
}

def fix_market_values():
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    print("=== FIXING MARKET VALUES FROM BALANCE SHEETS ===")
    print("Using Property & Equipment values (net book value) instead of Total Assets")
    print()
    
    for prop_id, data in CORRECT_VALUES.items():
        # Use NOI-based value for Hammond Aire and TCSH (manually corrected)
        # Use Property & Equipment for ESP and Wendover
        if prop_id in [3, 6]:
            market_value = data['market_value_noi']
            method = "NOI-based (manually corrected)"
        else:
            market_value = data['property_equipment']
            method = "Property & Equipment (balance sheet)"
        
        cursor.execute("""
            UPDATE properties
            SET current_market_value = ?
            WHERE id = ?
        """, (market_value, prop_id))
        
        cap_rate = (data['noi'] / market_value * 100) if market_value > 0 else 0
        print(f"✅ {data['name']}: ${market_value:,.2f} ({method}) - Cap Rate: {cap_rate:.1f}%")
    
    conn.commit()
    conn.close()
    print()
    print("✅ All market values updated successfully!")

if __name__ == "__main__":
    fix_market_values()

#!/usr/bin/env python3
"""
Verify market values are correct and cap rates are reasonable
"""
import sqlite3

def verify_market_values():
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    print("=== MARKET VALUE VERIFICATION ===")
    print("Checking all properties for reasonable cap rates (5-12%)")
    print()
    
    cursor.execute("""
        SELECT id, name, current_market_value, annual_noi
        FROM properties
        ORDER BY id
    """)
    
    all_good = True
    for row in cursor.fetchall():
        prop_id, name, market_value, noi = row
        if market_value and noi and market_value > 0:
            cap_rate = (noi / market_value * 100)
            status = "✅" if 5.0 <= cap_rate <= 12.0 else "⚠️"
            if not (5.0 <= cap_rate <= 12.0):
                all_good = False
            print(f"{status} {name}: MV=${market_value:,.2f}, NOI=${noi:,.2f}, Cap={cap_rate:.1f}%")
        else:
            print(f"❌ {name}: Missing market value or NOI data")
            all_good = False
    
    conn.close()
    
    print()
    if all_good:
        print("🎉 All properties have reasonable cap rates!")
    else:
        print("⚠️  Some properties need attention")
    
    return all_good

if __name__ == "__main__":
    verify_market_values()

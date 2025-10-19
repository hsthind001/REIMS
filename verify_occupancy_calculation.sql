-- ============================================================================
-- SQL Queries to Verify Occupancy Calculation
-- Property: The Crossings of Spring Hill
-- ============================================================================

-- Query 1: Find the property ID and basic info
SELECT 
    id,
    name,
    address,
    city,
    state,
    total_units,
    occupied_units,
    occupancy_rate
FROM properties
WHERE name LIKE '%Crossings of Spring Hill%';

-- ============================================================================

-- Query 2: Count stores by status for this property
-- (Replace 'PROPERTY_ID' with the actual ID from Query 1)
SELECT 
    property_id,
    status,
    COUNT(*) as unit_count
FROM stores
WHERE property_id = (
    SELECT id FROM properties WHERE name LIKE '%Crossings of Spring Hill%' LIMIT 1
)
GROUP BY property_id, status
ORDER BY status;

-- ============================================================================

-- Query 3: Calculate occupancy rate from stores table
SELECT 
    p.name as property_name,
    COUNT(*) as total_units,
    SUM(CASE WHEN s.status = 'occupied' THEN 1 ELSE 0 END) as occupied_units,
    SUM(CASE WHEN s.status = 'vacant' THEN 1 ELSE 0 END) as vacant_units,
    SUM(CASE WHEN s.status = 'under_lease' THEN 1 ELSE 0 END) as under_lease_units,
    SUM(CASE WHEN s.status = 'maintenance' THEN 1 ELSE 0 END) as maintenance_units,
    ROUND(
        (SUM(CASE WHEN s.status = 'occupied' THEN 1 ELSE 0 END) * 100.0) / COUNT(*),
        2
    ) as calculated_occupancy_rate,
    p.occupancy_rate as stored_occupancy_rate
FROM properties p
LEFT JOIN stores s ON p.id = s.property_id
WHERE p.name LIKE '%Crossings of Spring Hill%'
GROUP BY p.id, p.name, p.occupancy_rate;

-- ============================================================================

-- Query 4: List all units for this property with their status
SELECT 
    unit_number,
    unit_name,
    status,
    tenant_name,
    sqft,
    monthly_rent,
    lease_start_date,
    lease_end_date
FROM stores
WHERE property_id = (
    SELECT id FROM properties WHERE name LIKE '%Crossings of Spring Hill%' LIMIT 1
)
ORDER BY unit_number;

-- ============================================================================

-- Query 5: Verify occupancy calculation matches (should return TRUE)
SELECT 
    p.name,
    p.occupancy_rate as stored_rate,
    ROUND(
        (COUNT(CASE WHEN s.status = 'occupied' THEN 1 END) * 100.0) / COUNT(*),
        2
    ) as calculated_rate,
    CASE 
        WHEN ABS(p.occupancy_rate - ROUND(
            (COUNT(CASE WHEN s.status = 'occupied' THEN 1 END) * 100.0) / COUNT(*),
            2
        )) < 0.01 THEN 'MATCH'
        ELSE 'MISMATCH'
    END as verification
FROM properties p
LEFT JOIN stores s ON p.id = s.property_id
WHERE p.name LIKE '%Crossings of Spring Hill%'
GROUP BY p.id, p.name, p.occupancy_rate;


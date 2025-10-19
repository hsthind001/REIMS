# REIMS Database Migrations

SQL migrations for REIMS database schema.

## Overview

This directory contains SQL migration files that create and modify the REIMS database schema. Migrations are tracked in a `schema_migrations` table to prevent duplicate application.

---

## Migration Files

### 001_create_properties.sql

Creates the core `properties` table with:

**Columns (38):**
- Basic info: id, name, description
- Location: address, city, state, zip, latitude, longitude
- Physical: total_sqft, year_built, property_type, property_class
- Financial (Acquisition): acquisition_cost, acquisition_date
- Financial (Current): current_value, last_appraised_date, estimated_market_value
- Debt: loan_balance, original_loan_amount, interest_rate, loan_maturity_date, dscr
- Income: annual_noi, annual_revenue
- Occupancy: total_units, occupied_units, occupancy_rate
- Status: status, has_active_alerts
- Audit: created_at, updated_at, created_by, updated_by

**Indexes (9):**
- idx_properties_status
- idx_properties_city_state
- idx_properties_property_type
- idx_properties_occupancy_rate
- idx_properties_created_at
- idx_properties_has_alerts
- idx_properties_current_value
- idx_properties_coordinates
- idx_properties_class

**Constraints (8):**
- Occupancy rate: 0-100%
- Square footage: > 0
- Acquisition date: not in future
- Year built: 1800 to current year + 5
- Occupied units: <= total units
- Status: valid values
- Property type: valid values
- Property class: A, B, C, D

**Triggers:**
- Auto-update `updated_at` on row modification

---

## Running Migrations

### Method 1: Using Python Migration Runner (Recommended)

```bash
# List all migrations
python backend/db/migrations/run_migration.py --list

# Run a specific migration
python backend/db/migrations/run_migration.py 001_create_properties.sql

# Run all pending migrations
python backend/db/migrations/run_migration.py --all

# View migration history
python backend/db/migrations/run_migration.py --history

# Force reapply a migration
python backend/db/migrations/run_migration.py 001_create_properties.sql --force
```

### Method 2: Using psql (Direct SQL)

```bash
# Run migration directly
psql -U postgres -d reims -f backend/db/migrations/001_create_properties.sql

# Or with environment variables
psql -h localhost -U $DATABASE_USER -d $DATABASE_NAME -f backend/db/migrations/001_create_properties.sql
```

### Method 3: Using Python Script with Database Module

```python
import asyncio
from backend.db import init_db, close_db, execute

async def run_migration():
    await init_db()
    
    # Read SQL file
    with open('backend/db/migrations/001_create_properties.sql', 'r') as f:
        sql = f.read()
    
    # Execute migration
    await execute(sql)
    print("✅ Migration completed")
    
    await close_db()

asyncio.run(run_migration())
```

---

## Migration Tracking

Migrations are tracked in the `schema_migrations` table:

```sql
CREATE TABLE schema_migrations (
    id SERIAL PRIMARY KEY,
    migration_name VARCHAR(255) UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT true,
    error_message TEXT
);
```

**Check applied migrations:**
```sql
SELECT * FROM schema_migrations ORDER BY applied_at DESC;
```

---

## Verifying Migration

After running the migration, verify it succeeded:

```bash
# Check if table exists
psql -U postgres -d reims -c "\d properties"

# Check table structure
psql -U postgres -d reims -c "\d+ properties"

# Check indexes
psql -U postgres -d reims -c "\di properties*"

# Check constraints
psql -U postgres -d reims -c "SELECT conname, contype FROM pg_constraint WHERE conrelid = 'properties'::regclass;"

# Count records (should be 0 initially)
psql -U postgres -d reims -c "SELECT COUNT(*) FROM properties;"
```

Or using Python:

```python
import asyncio
from backend.db import init_db, close_db, fetch_all, fetch_val

async def verify_migration():
    await init_db()
    
    # Check if table exists
    exists = await fetch_val("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'properties'
        )
    """)
    print(f"✅ Table exists: {exists}")
    
    # Count columns
    column_count = await fetch_val("""
        SELECT COUNT(*) 
        FROM information_schema.columns 
        WHERE table_name = 'properties'
    """)
    print(f"📊 Columns: {column_count}")
    
    # List indexes
    indexes = await fetch_all("""
        SELECT indexname 
        FROM pg_indexes 
        WHERE tablename = 'properties'
    """)
    print(f"🔍 Indexes: {len(indexes)}")
    for idx in indexes:
        print(f"   - {idx['indexname']}")
    
    await close_db()

asyncio.run(verify_migration())
```

---

## Sample Data

After creating the table, you can insert sample data:

```sql
INSERT INTO properties (
    name, address, city, state, zip_code,
    total_sqft, year_built, property_type, property_class,
    acquisition_cost, acquisition_date,
    current_value, annual_noi, annual_revenue,
    total_units, occupied_units, occupancy_rate,
    status
) VALUES (
    'Downtown Office Commons',
    '123 Main Street',
    'Los Angeles',
    'CA',
    '90012',
    50000.00,
    2015,
    'office',
    'A',
    12500000.00,
    '2018-03-15',
    15000000.00,
    850000.00,
    1200000.00,
    50,
    45,
    90.00,
    'active'
);
```

Or using Python:

```python
from backend.db import fetch_val

property_id = await fetch_val("""
    INSERT INTO properties (
        name, address, city, state, property_type,
        total_sqft, occupancy_rate, current_value, status
    ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9
    ) RETURNING id
""",
    'Downtown Office Commons',
    '123 Main Street',
    'Los Angeles',
    'CA',
    'office',
    50000.00,
    90.00,
    15000000.00,
    'active'
)

print(f"✅ Property created with ID: {property_id}")
```

---

## Rollback

To rollback the migration (delete the table):

```sql
-- WARNING: This will delete all data!
DROP TABLE IF EXISTS properties CASCADE;

-- Remove from migrations tracking
DELETE FROM schema_migrations WHERE migration_name = '001_create_properties.sql';
```

---

## Best Practices

1. **Always backup before running migrations in production**
   ```bash
   pg_dump -U postgres reims > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Test migrations in development first**
   ```bash
   # Create test database
   createdb reims_test
   
   # Run migration on test database
   DATABASE_NAME=reims_test python backend/db/migrations/run_migration.py 001_create_properties.sql
   ```

3. **Use transactions for complex migrations**
   ```sql
   BEGIN;
   -- Your migration SQL here
   COMMIT;
   -- Or ROLLBACK if something goes wrong
   ```

4. **Verify migration success**
   - Check table structure
   - Verify indexes exist
   - Test constraints
   - Run sample queries

5. **Document breaking changes**
   - Add comments to migration files
   - Update README with important notes
   - Communicate changes to team

---

## Troubleshooting

### Error: "relation already exists"

The table already exists. Use `--force` to reapply or drop the table first.

```bash
python backend/db/migrations/run_migration.py 001_create_properties.sql --force
```

### Error: "permission denied"

Database user doesn't have sufficient privileges.

```sql
-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE reims TO your_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
```

### Error: "database does not exist"

Create the database first:

```bash
createdb reims
# Or
psql -U postgres -c "CREATE DATABASE reims;"
```

### Error: "connection refused"

PostgreSQL is not running or connection parameters are wrong.

1. Check PostgreSQL status
2. Verify `.env` file configuration
3. Test connection: `psql -U postgres -d reims`

---

## Next Steps

After creating the properties table:

1. **Create related tables:**
   - `leases` - Tenant lease information
   - `tenants` - Tenant details
   - `documents` - Property documents
   - `alerts` - Property alerts
   - `transactions` - Financial transactions

2. **Add foreign keys:**
   - Link leases to properties
   - Link tenants to leases
   - Link documents to properties

3. **Create views:**
   - Property portfolio summary
   - Occupancy analytics
   - Financial performance

4. **Set up functions:**
   - Calculate occupancy rate
   - Calculate DSCR
   - Update property metrics

---

## Schema Documentation

Full schema documentation is available in:
- Column comments in SQL file
- Table structure queries
- ER diagrams (to be created)

---

### 007_create_audit_log.sql

Creates the comprehensive `audit_log` table for complete system traceability:

**Purpose:**
- Complete audit trail for compliance (BR-007)
- Track WHO did WHAT, WHEN, and WHY
- Support regulatory export requirements
- Enable rollback with old_values/new_values
- Security reviews and debugging

**Columns (21):**
- **Action Info:** action, action_category
- **Business Requirements:** br_id, br_description
- **References:** property_id, document_id, alert_id (FK)
- **User Context:** user_id, user_email, user_role, ip_address, user_agent
- **Change Tracking:** old_values (JSONB), new_values (JSONB), details (JSONB)
- **Status:** success, error_message
- **Session:** session_id, request_id
- **Timestamp:** timestamp (auto-generated)

**Indexes (8):**
- idx_audit_timestamp (DESC) - Primary temporal index
- idx_audit_user_id, idx_audit_user_timestamp - User activity
- idx_audit_action - Action type queries
- idx_audit_br_id - Business requirement tracking
- idx_audit_property_id, idx_audit_property_timestamp - Property audits
- idx_audit_document_id - Document tracking

**Key Features:**
- JSONB for flexible old_values/new_values tracking
- INET type for IP address storage
- Foreign keys with ON DELETE SET NULL (preserve audit on entity deletion)
- Immutable (never delete records)
- Supports table partitioning for high-volume deployments (> 1M rows)

**Usage Examples:**
```sql
-- Log a document upload
INSERT INTO audit_log (
  action, action_category, br_id, user_email, user_role,
  property_id, document_id, new_values, session_id
) VALUES (
  'DOCUMENT_UPLOAD', 'document', 'BR-001', 
  'analyst@reims.com', 'analyst',
  '123e4567-e89b-12d3-a456-426614174000',
  '789e4567-e89b-12d3-a456-426614174999',
  '{"filename": "Q3_financials.pdf", "size_bytes": 245678}'::jsonb,
  'session-abc123'
);

-- Query audit trail for a property
SELECT timestamp, action, user_email, new_values
FROM audit_log
WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
ORDER BY timestamp DESC
LIMIT 20;

-- Generate compliance report
SELECT DATE(timestamp) as date, action_category, COUNT(*) as count
FROM audit_log
WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(timestamp), action_category
ORDER BY date DESC;
```

**Verification:**
```bash
python backend/db/migrations/verify_audit_log_table.py
```

---

### 008_create_anomaly_detection.sql

Creates the `anomaly_detection_results` table for statistical anomaly detection:

**Purpose:**
- Store historical anomaly detection analysis results
- Support BR-008 (anomaly detection engine)
- Statistical outlier detection (Z-score method)
- Trend shift detection (CUSUM method)
- Nightly job (2 AM) populates this table

**Columns (27):**
- **Metric Info:** metric_name, metric_history_start_date, metric_history_end_date, data_points_analyzed
- **Z-Score Analysis:** zscore_detected, zscore_threshold, zscore_values[], zscore_anomalies
- **CUSUM Analysis:** cusum_detected, cusum_threshold, cusum_direction, cusum_anomalies
- **Results:** anomalies_found, anomaly_confidence, anomaly_type
- **Anomaly Details (Arrays):** anomaly_values[], anomaly_dates[], anomaly_descriptions[]
- **Business Impact:** requires_review, requires_alert
- **Analysis Params:** lookback_months, analysis_method
- **Timing:** analysis_date, analysis_timestamp, analysis_duration_seconds

**Indexes (7):**
- idx_anomaly_property_id - Property-specific queries
- idx_anomaly_metric_name - Metric-specific analysis
- idx_anomaly_detected - Filter by detection status
- idx_anomaly_analysis_date (DESC) - Temporal queries
- idx_anomaly_property_metric - Combined lookups (most common)
- idx_anomaly_requires_review - Review queue (partial index)
- idx_anomaly_requires_alert - Alert generation (partial index)

**CHECK Constraints (10):**
- Confidence: 0.00 to 1.00
- Thresholds: positive values
- Data points: positive
- Lookback months: positive
- Analysis duration: non-negative
- CUSUM direction: upward, downward, both
- Anomaly type: outlier, trend_shift, level_change, seasonal, multiple
- Analysis method: z_score, cusum, combination, ml_model, ensemble
- Analysis date: not in future

**Key Features:**
- PostgreSQL array columns for multi-anomaly storage
- Partial indexes for review/alert queues (performance optimization)
- UNNEST support for expanding arrays in queries
- Z-score and CUSUM statistical methods
- Configurable thresholds and lookback windows

**Usage Examples:**
```sql
-- Insert NOI anomaly detection result
INSERT INTO anomaly_detection_results (
  property_id, metric_name,
  zscore_detected, zscore_threshold, zscore_values, zscore_anomalies,
  anomalies_found, anomaly_confidence, anomaly_type,
  anomaly_values, anomaly_dates, anomaly_descriptions,
  requires_review, analysis_method, analysis_date
) VALUES (
  '123e4567-e89b-12d3-a456-426614174000', 'noi',
  true, 2.5, ARRAY[0.5, 1.2, 3.8, 1.1], 1,
  true, 0.85, 'outlier',
  ARRAY[85000.00], ARRAY['2024-03-15'::DATE], 
  ARRAY['NOI dropped 35% below expected'],
  true, 'z_score', CURRENT_DATE
);

-- Query recent anomalies for a property
SELECT 
  analysis_date, metric_name, anomaly_type, anomaly_confidence,
  UNNEST(anomaly_descriptions) as description
FROM anomaly_detection_results
WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
  AND anomalies_found = true
  AND analysis_date >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY analysis_date DESC;

-- Get properties requiring review
SELECT p.name, adr.metric_name, adr.anomaly_confidence
FROM anomaly_detection_results adr
JOIN properties p ON p.id = adr.property_id
WHERE adr.requires_review = true
  AND adr.analysis_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY adr.anomaly_confidence DESC;
```

**Array Operations:**
```sql
-- Expand arrays to individual rows
SELECT 
  property_id,
  UNNEST(anomaly_dates) as anomaly_date,
  UNNEST(anomaly_values) as anomaly_value,
  UNNEST(anomaly_descriptions) as description
FROM anomaly_detection_results
WHERE anomalies_found = true;

-- Array length and statistics
SELECT 
  metric_name,
  AVG(ARRAY_LENGTH(zscore_values, 1)) as avg_data_points,
  AVG(zscore_anomalies::FLOAT / ARRAY_LENGTH(zscore_values, 1)) as avg_anomaly_rate
FROM anomaly_detection_results
WHERE zscore_detected = true
GROUP BY metric_name;
```

**Verification:**
```bash
python backend/db/migrations/verify_anomaly_detection_table.py
```

---

### 009_create_exit_strategy.sql

Creates the `exit_strategy_analysis` table for property exit strategy intelligence:

**Purpose:**
- Store exit strategy analysis for hold, refinance, and sale scenarios
- Support BR-004 (exit strategy intelligence)
- On-demand analysis (user-initiated, not scheduled)
- Compare multiple disposition strategies
- Track historical analysis results

**Columns (35):**
- **Analysis Info:** analysis_date, analysis_timestamp
- **Market Data:** market_cap_rate, market_mortgage_rate, property_condition_adjustment, location_premium
- **HOLD Scenario (6):** hold_projected_noi_5yr[], hold_irr, hold_total_return, hold_terminal_value, hold_pros[], hold_cons[]
- **REFINANCE Scenario (8):** refinance_new_loan_amount, refinance_new_rate, refinance_cash_out, refinance_monthly_savings, refinance_new_dscr, refinance_feasible, refinance_pros[], refinance_cons[]
- **SALE Scenario (8):** sale_estimated_price, sale_transaction_costs, sale_loan_payoff, sale_net_proceeds, sale_total_return_pct, sale_annualized_return, sale_pros[], sale_cons[]
- **Recommendation:** recommended_strategy, recommendation_confidence, recommendation_rationale
- **Metadata:** analyst_id, analysis_complete, updated_at

**Indexes (5):**
- idx_exit_property_id - Property-specific analysis
- idx_exit_analysis_date (DESC) - Temporal queries
- idx_exit_recommendation - Filter by strategy
- idx_exit_property_date - Combined lookup (common pattern)
- idx_exit_confidence - High-confidence recommendations (partial index >= 0.70)

**CHECK Constraints (12):**
- Market rates: positive values
- Property condition: 0.90 to 1.10 (90% to 110%)
- Location premium: positive
- Hold IRR: -1.00 to 1.00 (-100% to 100%)
- Refinance rate: positive
- Refinance DSCR: positive (>= 1.25 for CMBS feasibility)
- Sale returns: reasonable ranges
- Recommendation confidence: 0.00 to 1.00
- Valid strategies: hold, refinance, sale, insufficient_data
- Analysis date: not in future

**Trigger:**
- Auto-updates `updated_at` on row modification

**Key Features:**
- Three complete scenarios with pros/cons arrays
- IRR (Internal Rate of Return) calculations
- DSCR (Debt Service Coverage Ratio) for refinance feasibility
- 5-year NOI projections array
- Confidence-based recommendations (>= 0.70 preferred)
- Historical tracking of analysis over time

**Usage Examples:**
```sql
-- Insert complete exit strategy analysis
INSERT INTO exit_strategy_analysis (
  property_id, analysis_date,
  market_cap_rate, market_mortgage_rate,
  hold_projected_noi_5yr, hold_irr, hold_total_return,
  hold_pros, hold_cons,
  refinance_new_loan_amount, refinance_new_dscr, refinance_feasible,
  refinance_pros, refinance_cons,
  sale_estimated_price, sale_net_proceeds, sale_annualized_return,
  sale_pros, sale_cons,
  recommended_strategy, recommendation_confidence, recommendation_rationale
) VALUES (
  '123e4567-e89b-12d3-a456-426614174000', CURRENT_DATE,
  0.065, 0.055,
  ARRAY[850000, 875000, 900000, 925000, 950000], 0.082, 2500000,
  ARRAY['Strong fundamentals', 'Consistent cash flow'],
  ARRAY['Capital tied up'],
  10000000, 1.45, true,
  ARRAY['Unlock equity', 'Lower payments'],
  ARRAY['Closing costs'],
  14500000, 4775000, 0.078,
  ARRAY['Immediate liquidity', 'Strong market'],
  ARRAY['Capital gains tax'],
  'hold', 0.85, 'Strong fundamentals with consistent NOI growth'
);

-- Query most recent analysis for a property
SELECT 
  analysis_date, recommended_strategy, recommendation_confidence,
  hold_irr, sale_annualized_return, refinance_feasible
FROM exit_strategy_analysis
WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
ORDER BY analysis_date DESC
LIMIT 1;

-- Find properties recommended for sale
SELECT 
  p.name, esa.sale_estimated_price, esa.sale_net_proceeds,
  esa.sale_annualized_return, esa.recommendation_confidence
FROM exit_strategy_analysis esa
JOIN properties p ON p.id = esa.property_id
WHERE esa.recommended_strategy = 'sale'
  AND esa.recommendation_confidence >= 0.70
  AND esa.analysis_date >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY esa.sale_annualized_return DESC;

-- Find refinancing opportunities
SELECT 
  p.name, esa.refinance_cash_out, esa.refinance_monthly_savings,
  esa.refinance_new_dscr
FROM exit_strategy_analysis esa
JOIN properties p ON p.id = esa.property_id
WHERE esa.recommended_strategy = 'refinance'
  AND esa.refinance_feasible = true
  AND esa.refinance_new_dscr >= 1.25
ORDER BY esa.refinance_cash_out DESC;
```

**Scenario Comparison:**
```sql
-- Compare all three scenarios side-by-side
SELECT 
  'Hold' as scenario,
  hold_irr as return_rate,
  hold_total_return as value,
  UNNEST(hold_pros) as advantages
FROM exit_strategy_analysis
WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
  AND analysis_date = (SELECT MAX(analysis_date) 
                       FROM exit_strategy_analysis 
                       WHERE property_id = '123e4567-e89b-12d3-a456-426614174000')
UNION ALL
SELECT 
  'Sale' as scenario,
  sale_annualized_return as return_rate,
  sale_net_proceeds as value,
  UNNEST(sale_pros) as advantages
FROM exit_strategy_analysis
WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
  AND analysis_date = (SELECT MAX(analysis_date) 
                       FROM exit_strategy_analysis 
                       WHERE property_id = '123e4567-e89b-12d3-a456-426614174000');
```

**NOI Projections:**
```sql
-- Expand 5-year NOI projections
SELECT 
  property_id,
  analysis_date,
  UNNEST(hold_projected_noi_5yr) as projected_noi,
  generate_series(1, ARRAY_LENGTH(hold_projected_noi_5yr, 1)) as year
FROM exit_strategy_analysis
WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
ORDER BY analysis_date DESC, year;
```

**Verification:**
```bash
python backend/db/migrations/verify_exit_strategy_table.py
```

---

### 010_create_financial_summary.sql

Creates the `property_financial_summary` table - a denormalized table for fast dashboard queries:

**Purpose:**
- Pre-calculated financial metrics for performance optimization
- Eliminate joins for dashboard KPI queries
- Aggregate data from multiple source tables
- Updated daily/monthly via batch processing
- One record per property per month

**Columns (33):**
- **Summary Period:** summary_date, summary_month (auto-generated)
- **Income Metrics (4):** gross_revenue, total_expenses, noi, noi_margin
- **Debt Metrics (3):** annual_debt_service, dscr, ltv
- **Occupancy Metrics (5):** total_units, occupied_units, occupancy_rate, leased_not_occupied, vacant_units
- **Tenant Metrics (3):** tenant_count, average_lease_term_months, expiring_leases_12mo
- **Performance Metrics (3):** cap_rate, roi_pct, days_on_market
- **Area Breakdown (3):** expense_per_sqft, revenue_per_sqft, rent_per_occupied_sqft
- **Quality Indicators (3):** avg_rent_per_unit, rent_growth_pct_yoy, expense_ratio
- **Risk Flags (3):** below_market_rent, above_average_expense, lease_expiration_risk
- **Audit (2):** calculated_at, data_complete

**Indexes (9):**
- idx_summary_property_id - Property lookups
- idx_summary_date (DESC) - Temporal queries
- idx_summary_month (DESC) - Month-based queries
- idx_summary_below_market - Below market rent (partial index)
- idx_summary_high_expense - High expenses (partial index)
- idx_summary_lease_risk - Lease expiration risk (partial index)
- idx_summary_occupancy (DESC) - Occupancy ranking
- idx_summary_dscr (DESC) - DSCR ranking
- idx_summary_noi (DESC) - NOI ranking

**CHECK Constraints (18):**
- Occupancy rate: 0.00 to 1.00
- NOI margin: -1.00 to 1.00
- DSCR: positive
- LTV: 0.00 to 1.00
- Cap rate: -1.00 to 1.00
- ROI: -100 to 1000
- Expense ratio: 0.00 to 1.00
- Occupied units <= total units
- Non-negative: vacant_units, days_on_market, tenant_count, expiring_leases, per_sqft metrics
- Positive: average_lease_term_months
- Summary month format: YYYY-MM
- Summary date: not in future

**UNIQUE Constraint:**
- (property_id, summary_month) - One summary per property per month

**Trigger:**
- Auto-generates `summary_month` from `summary_date` (YYYY-MM format)

**Key Features:**
- **Denormalized design** - no joins required for dashboard queries
- **Pre-calculated metrics** - NOI, DSCR, cap rate, occupancy all ready
- **Risk flags** - boolean indicators for quick filtering
- **UPSERT support** - ON CONFLICT for batch updates
- **Historical tracking** - month-over-month comparisons
- **Portfolio aggregations** - SUM/AVG across all properties

**Usage Examples:**
```sql
-- Insert/update financial summary
INSERT INTO property_financial_summary (
  property_id, summary_date,
  gross_revenue, total_expenses, noi, noi_margin,
  dscr, occupancy_rate, tenant_count,
  below_market_rent, lease_expiration_risk
) VALUES (
  '123e4567-e89b-12d3-a456-426614174000', CURRENT_DATE,
  1200000.00, 350000.00, 850000.00, 0.708,
  1.42, 0.92, 46,
  false, true
)
ON CONFLICT (property_id, summary_month)
DO UPDATE SET
  noi = EXCLUDED.noi,
  occupancy_rate = EXCLUDED.occupancy_rate,
  calculated_at = CURRENT_TIMESTAMP;

-- Dashboard KPI query (NO JOINS!)
SELECT 
  p.name as property_name,
  pfs.noi, pfs.occupancy_rate, pfs.dscr, pfs.cap_rate,
  pfs.expiring_leases_12mo,
  pfs.below_market_rent, pfs.above_average_expense
FROM property_financial_summary pfs
JOIN properties p ON p.id = pfs.property_id
WHERE pfs.summary_month = TO_CHAR(CURRENT_DATE, 'YYYY-MM')
ORDER BY pfs.noi DESC;

-- Properties with risk flags
SELECT 
  p.name, pfs.noi, pfs.occupancy_rate,
  CASE 
    WHEN pfs.below_market_rent THEN 'Below Market Rent'
    WHEN pfs.above_average_expense THEN 'High Expenses'
    WHEN pfs.lease_expiration_risk THEN 'Lease Risk'
  END as risk_type
FROM property_financial_summary pfs
JOIN properties p ON p.id = pfs.property_id
WHERE (pfs.below_market_rent = true 
    OR pfs.above_average_expense = true 
    OR pfs.lease_expiration_risk = true)
  AND pfs.summary_month = TO_CHAR(CURRENT_DATE, 'YYYY-MM');
```

**Portfolio Aggregation:**
```sql
-- Portfolio-wide metrics
SELECT 
  COUNT(*) as property_count,
  SUM(noi) as total_noi,
  AVG(occupancy_rate) as avg_occupancy,
  AVG(dscr) as avg_dscr,
  AVG(cap_rate) as avg_cap_rate,
  SUM(CASE WHEN below_market_rent THEN 1 ELSE 0 END) as below_market_count,
  SUM(CASE WHEN lease_expiration_risk THEN 1 ELSE 0 END) as lease_risk_count
FROM property_financial_summary
WHERE summary_month = TO_CHAR(CURRENT_DATE, 'YYYY-MM')
  AND data_complete = true;
```

**Historical Trends:**
```sql
-- Month-over-month comparison
WITH current_month AS (
  SELECT * FROM property_financial_summary 
  WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
    AND summary_month = TO_CHAR(CURRENT_DATE, 'YYYY-MM')
),
previous_month AS (
  SELECT * FROM property_financial_summary 
  WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
    AND summary_month = TO_CHAR(CURRENT_DATE - INTERVAL '1 month', 'YYYY-MM')
)
SELECT 
  c.summary_month,
  c.noi as current_noi,
  p.noi as previous_noi,
  ((c.noi - p.noi) / p.noi * 100) as noi_change_pct,
  c.occupancy_rate - p.occupancy_rate as occupancy_change
FROM current_month c
CROSS JOIN previous_month p;
```

**Verification:**
```bash
python backend/db/migrations/verify_financial_summary_table.py
```

---

### 011_create_metrics_log.sql

Creates the `metrics_log` table for storing historical Prometheus metrics snapshots:

**Purpose:**
- Archive Prometheus metrics for long-term trend analysis
- Store metrics beyond Prometheus retention period
- Optional: Prometheus scrapes `/metrics` endpoint directly
- Enable historical analysis and trend detection
- Support compliance/audit requirements for system metrics

**Columns (8):**
- **Identification:** metric_name, metric_type (counter, gauge, histogram, summary)
- **Labels:** labels (JSONB) - flexible label storage
- **Value & Time:** metric_value, recorded_at
- **Context:** application, environment

**Indexes (7):**
- idx_metrics_name_time - Primary query pattern (metric + time range)
- idx_metrics_recorded_at (DESC) - Temporal queries
- idx_metrics_name_labels - Metric + label queries
- idx_metrics_labels_gin - GIN index for flexible JSONB queries
- idx_metrics_application (DESC) - Application-specific queries
- idx_metrics_environment (DESC) - Environment filtering
- idx_metrics_type (DESC) - Metric type queries

**CHECK Constraints (4):**
- metric_type: counter, gauge, histogram, summary
- application: backend, frontend, worker, storage_service, queue_service, nginx
- environment: development, staging, production, test
- recorded_at: not in future (with 1-minute buffer)

**Key Features:**
- **JSONB labels** - Flexible schema for Prometheus labels
- **GIN index** - Fast JSONB containment queries
- **Time-series optimized** - Indexes for time-range queries
- **Data retention** - cleanup_old_metrics() function
- **Partitioning support** - Optional for > 10M rows
- **Batch insert** - Efficient multi-row inserts

**Cleanup Function:**
```sql
-- Delete metrics older than 90 days
SELECT cleanup_old_metrics(90);

-- Schedule monthly cleanup (requires pg_cron)
SELECT cron.schedule('cleanup-metrics', '0 2 1 * *', 
  'SELECT cleanup_old_metrics(90);');
```

**Usage Examples:**
```sql
-- Insert API request counter
INSERT INTO metrics_log (
  metric_name, metric_type, labels, metric_value,
  application, environment
) VALUES (
  'api_requests_total', 'counter',
  '{"method": "GET", "endpoint": "/api/properties", "status": "200"}'::jsonb,
  12543,
  'backend', 'production'
);

-- Query metrics for specific endpoint over time
SELECT 
  recorded_at,
  metric_value,
  labels->>'method' as method,
  labels->>'status' as status
FROM metrics_log
WHERE metric_name = 'api_requests_total'
  AND labels->>'endpoint' = '/api/properties'
  AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY recorded_at DESC;

-- Average latency per endpoint (last hour)
SELECT 
  labels->>'endpoint' as endpoint,
  AVG(metric_value) as avg_latency_seconds,
  MIN(metric_value) as min_latency,
  MAX(metric_value) as max_latency,
  COUNT(*) as samples
FROM metrics_log
WHERE metric_name = 'api_latency_seconds'
  AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
GROUP BY labels->>'endpoint'
ORDER BY avg_latency_seconds DESC;
```

**JSONB Label Queries:**
```sql
-- Query by label value (arrow operator)
SELECT * FROM metrics_log
WHERE labels->>'endpoint' = '/api/analytics'
  AND labels->>'status' = '200';

-- Query using containment (faster with GIN index)
SELECT * FROM metrics_log
WHERE labels @> '{"status": "500"}'::jsonb
  AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '1 hour';

-- Multiple label conditions
SELECT * FROM metrics_log
WHERE labels->>'method' = 'POST'
  AND labels->>'endpoint' LIKE '/api/%'
  AND labels @> '{"status": "200"}'::jsonb;
```

**Time-Series Analysis:**
```sql
-- Request rate per minute
SELECT 
  DATE_TRUNC('minute', recorded_at) as minute,
  labels->>'endpoint' as endpoint,
  MAX(metric_value) - MIN(metric_value) as requests_per_minute
FROM metrics_log
WHERE metric_name = 'api_requests_total'
  AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
GROUP BY DATE_TRUNC('minute', recorded_at), labels->>'endpoint'
ORDER BY minute DESC;

-- 5-minute aggregation buckets
SELECT 
  DATE_TRUNC('minute', recorded_at) - 
    EXTRACT(MINUTE FROM recorded_at)::INTEGER % 5 * INTERVAL '1 minute' as bucket,
  AVG(metric_value) as avg_latency,
  MAX(metric_value) as max_latency
FROM metrics_log
WHERE metric_name = 'api_latency_seconds'
  AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
GROUP BY bucket
ORDER BY bucket DESC;
```

**Error Rate Analysis:**
```sql
-- Calculate error rate (5xx / total)
WITH total AS (
  SELECT DATE_TRUNC('hour', recorded_at) as hour,
         MAX(metric_value) as count
  FROM metrics_log
  WHERE metric_name = 'api_requests_total'
    AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
  GROUP BY DATE_TRUNC('hour', recorded_at)
),
errors AS (
  SELECT DATE_TRUNC('hour', recorded_at) as hour,
         MAX(metric_value) as count
  FROM metrics_log
  WHERE metric_name = 'api_requests_total'
    AND labels->>'status' LIKE '5%'
    AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
  GROUP BY DATE_TRUNC('hour', recorded_at)
)
SELECT 
  t.hour,
  t.count as total_requests,
  COALESCE(e.count, 0) as error_requests,
  ROUND((COALESCE(e.count, 0)::NUMERIC / NULLIF(t.count, 0)) * 100, 2) as error_rate_pct
FROM total t
LEFT JOIN errors e ON t.hour = e.hour
ORDER BY t.hour DESC;
```

**Batch Insert:**
```sql
-- Efficient multi-row insert
INSERT INTO metrics_log (metric_name, metric_type, labels, metric_value, application, environment)
VALUES 
  ('api_requests_total', 'counter', '{"endpoint": "/api/properties"}'::jsonb, 1000, 'backend', 'production'),
  ('api_latency_seconds', 'gauge', '{"endpoint": "/api/properties"}'::jsonb, 0.123, 'backend', 'production'),
  ('db_connections_active', 'gauge', '{"pool": "main"}'::jsonb, 5, 'backend', 'production');
```

**Verification:**
```bash
python backend/db/migrations/verify_metrics_log_table.py
```

---

### 012_create_performance_logs.sql

Creates the `performance_logs` table for request performance tracking and SLA monitoring:

**Purpose:**
- Track request performance for optimization
- Identify slow endpoints and bottlenecks
- SLA monitoring (target: 90% requests < 500ms)
- Database, cache, and external service performance analysis
- Support performance optimization efforts

**Columns (21):**
- **Request Info:** request_id (UNIQUE), endpoint, method
- **Timing:** start_time, end_time, duration_ms (auto-calculated)
- **Database:** db_queries_count, db_time_ms
- **Cache:** cache_hits, cache_misses, cache_time_ms
- **External Services:** external_service_calls, external_service_time_ms
- **Response:** status_code, response_size_bytes
- **User Context:** user_id, ip_address
- **Flags:** is_slow (> 1000ms), is_error (>= 400)
- **Audit:** logged_at

**Indexes (10):**
- idx_perf_endpoint_time - Primary pattern (endpoint + time)
- idx_perf_duration (DESC) - Slow request identification
- idx_perf_slow (DESC) - Partial index for slow requests
- idx_perf_errors (DESC) - Partial index for errors
- idx_perf_logged_at (DESC) - Temporal queries
- idx_perf_start_time (DESC) - Time-series analysis
- idx_perf_user_id - User-specific performance
- idx_perf_status_code - Status analysis
- idx_perf_method - Method-specific queries
- idx_perf_db_time (DESC) - Database bottlenecks

**CHECK Constraints (12):**
- method: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS
- status_code: 100-599
- duration_ms: non-negative
- end_time >= start_time
- All count/time metrics: non-negative
- response_size_bytes: non-negative

**UNIQUE Constraint:**
- request_id - Each request logged once

**Trigger:**
- Auto-calculates `duration_ms` from start/end time
- Auto-sets `is_slow` flag (> 1000ms)
- Auto-sets `is_error` flag (status >= 400)

**Materialized View:**
- `performance_summary_hourly` - Pre-aggregated hourly stats
- Includes: avg, p50, p95, p99, max duration
- Slow/error counts, cache hit rate, total response bytes
- Refresh function: `refresh_performance_summary()`

**Cleanup Function:**
```sql
-- Delete logs older than 30 days
SELECT cleanup_old_performance_logs(30);
```

**Usage Examples:**
```sql
-- Insert performance log (auto-calculate duration and flags)
INSERT INTO performance_logs (
  request_id, endpoint, method,
  start_time, end_time,
  db_queries_count, db_time_ms,
  cache_hits, cache_misses,
  status_code, response_size_bytes
) VALUES (
  'req-abc123', '/api/properties', 'GET',
  '2025-10-12 10:30:00', '2025-10-12 10:30:00.245',
  5, 120,
  3, 1,
  200, 15234
);

-- Identify slow endpoints
SELECT 
  endpoint,
  COUNT(*) as slow_count,
  AVG(duration_ms) as avg_duration_ms,
  MAX(duration_ms) as max_duration_ms
FROM performance_logs
WHERE is_slow = true
  AND start_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY endpoint
ORDER BY slow_count DESC;

-- SLA compliance report (% requests < 500ms)
SELECT 
  endpoint,
  COUNT(*) as total_requests,
  COUNT(*) FILTER (WHERE duration_ms < 500) as fast_requests,
  ROUND((COUNT(*) FILTER (WHERE duration_ms < 500)::NUMERIC / COUNT(*)) * 100, 2) as sla_compliance_pct
FROM performance_logs
WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY endpoint
ORDER BY sla_compliance_pct ASC;
```

**Bottleneck Analysis:**
```sql
-- Database bottlenecks
SELECT 
  endpoint,
  AVG(duration_ms) as avg_total_ms,
  AVG(db_time_ms) as avg_db_ms,
  ROUND((AVG(db_time_ms)::NUMERIC / AVG(duration_ms)) * 100, 2) as db_time_pct,
  AVG(db_queries_count) as avg_queries
FROM performance_logs
WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
  AND db_time_ms IS NOT NULL
GROUP BY endpoint
ORDER BY db_time_pct DESC;

-- Cache effectiveness
SELECT 
  endpoint,
  SUM(cache_hits) as hits,
  SUM(cache_misses) as misses,
  ROUND((SUM(cache_hits)::NUMERIC / NULLIF(SUM(cache_hits + cache_misses), 0)) * 100, 2) as hit_rate_pct
FROM performance_logs
WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY endpoint
ORDER BY hit_rate_pct ASC;

-- External service impact
SELECT 
  endpoint,
  AVG(duration_ms) as avg_total_ms,
  AVG(external_service_time_ms) as avg_external_ms,
  AVG(external_service_calls) as avg_calls,
  ROUND((AVG(external_service_time_ms)::NUMERIC / AVG(duration_ms)) * 100, 2) as external_pct
FROM performance_logs
WHERE external_service_calls > 0
GROUP BY endpoint
ORDER BY external_pct DESC;
```

**Percentile Analysis:**
```sql
-- P50, P95, P99 latencies
SELECT 
  endpoint,
  COUNT(*) as requests,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_ms) as p50_ms,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) as p95_ms,
  PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY duration_ms) as p99_ms
FROM performance_logs
WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY endpoint
ORDER BY p99_ms DESC;
```

**Error Analysis:**
```sql
-- Error rate by endpoint
SELECT 
  endpoint,
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE is_error = true) as errors,
  ROUND((COUNT(*) FILTER (WHERE is_error = true)::NUMERIC / COUNT(*)) * 100, 2) as error_rate_pct,
  STRING_AGG(DISTINCT status_code::TEXT, ', ') as error_statuses
FROM performance_logs
WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY endpoint
HAVING COUNT(*) FILTER (WHERE is_error = true) > 0
ORDER BY error_rate_pct DESC;
```

**Time-Series Analysis:**
```sql
-- 15-minute performance buckets
SELECT 
  DATE_TRUNC('minute', start_time) - 
    EXTRACT(MINUTE FROM start_time)::INTEGER % 15 * INTERVAL '1 minute' as bucket,
  endpoint,
  COUNT(*) as requests,
  AVG(duration_ms) as avg_ms,
  COUNT(*) FILTER (WHERE is_slow = true) as slow_count
FROM performance_logs
WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL '4 hours'
GROUP BY bucket, endpoint
ORDER BY bucket DESC, avg_ms DESC;
```

**Materialized View Usage:**
```sql
-- Fast dashboard queries using pre-aggregated data
SELECT * FROM performance_summary_hourly
WHERE hour >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
  AND endpoint = '/api/analytics'
ORDER BY hour DESC;

-- Refresh summary (run hourly via cron)
SELECT refresh_performance_summary();
```

**Verification:**
```bash
python backend/db/migrations/verify_performance_logs_table.py
```

---

### 013_create_users.sql

Creates the `users` table for authentication, authorization, and role-based access control:

**Purpose:**
- User authentication and authorization
- Role-based access control (RBAC)
- Account security (MFA, locking, password policies)
- Required by BR-008 (security & access control)
- Support for committee membership tracking
- Audit trail of user activity

**Columns (23):**
- **Account:** email (UNIQUE), username (UNIQUE), password_hash
- **Profile:** first_name, last_name, phone
- **Role & Permissions:** role, permissions[], committee_member
- **Status:** is_active, is_email_verified, email_verified_at
- **Security:** last_login, last_login_ip, failed_login_attempts, account_locked_until
- **MFA:** mfa_enabled, mfa_secret
- **Audit:** created_at, updated_at, created_by, password_changed_at

**Indexes (9):**
- idx_users_email_lower - Case-insensitive email lookup (UNIQUE)
- idx_users_username_lower - Case-insensitive username (UNIQUE)
- idx_users_role - Role-based queries
- idx_users_active - Active users (partial index)
- idx_users_email_verified - Unverified emails (partial index)
- idx_users_locked - Locked accounts (partial index)
- idx_users_mfa - MFA-enabled users (partial index)
- idx_users_last_login (DESC) - Activity tracking
- idx_users_committee - Committee members (partial index)

**CHECK Constraints (11):**
- role: supervisor, analyst, viewer, admin
- email_format: Valid email regex
- username_format: Alphanumeric, underscore, hyphen (3-100 chars)
- password_hash_format: bcrypt ($2a$, $2b$, $2y$)
- failed_login_attempts: Non-negative
- account_locked: Future timestamp if set
- email_verified_timestamp: Only if verified
- mfa_secret: Only if MFA enabled
- phone_format: International format support
- email/username: Not empty after trim

**Triggers (2):**
- `update_user_timestamp` - Auto-updates `updated_at`
- `track_password_change` - Auto-sets `password_changed_at`, resets failed attempts

**Security Functions (4):**
```sql
-- Check if account is locked (auto-unlocks if expired)
SELECT is_account_locked('user-uuid');

-- Record failed login (auto-locks after 5 attempts)
SELECT record_failed_login('user@example.com');

-- Record successful login (resets attempts, updates last_login)
SELECT record_successful_login('user-uuid', '192.168.1.100'::INET);

-- Get user permissions based on role
SELECT * FROM get_user_permissions('user-uuid');
```

**Role Hierarchy:**
| Role | Can Create | Can Read | Can Update | Can Delete | Can Approve | Can Admin |
|------|------------|----------|------------|------------|-------------|-----------|
| **admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **supervisor** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **analyst** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **viewer** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |

**Usage Examples:**
```sql
-- Create a new user (with bcrypt hash)
INSERT INTO users (
  email, username, password_hash,
  first_name, last_name, role
) VALUES (
  'john.doe@reims.com', 'johndoe',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYb7YgP5.rO',
  'John', 'Doe', 'supervisor'
);

-- Authenticate user (login)
SELECT id, email, password_hash, role, is_active
FROM users
WHERE LOWER(email) = LOWER('john.doe@reims.com')
  AND is_active = true;
-- Then verify with: bcrypt.verify(plain_password, password_hash)

-- Enable MFA
UPDATE users
SET mfa_enabled = true,
    mfa_secret = 'JBSWY3DPEHPK3PXP' -- Base32 TOTP secret
WHERE id = 'user-uuid';

-- Grant permissions
UPDATE users
SET permissions = ARRAY['upload_documents', 'export_reports']
WHERE id = 'user-uuid';

-- Deactivate user (soft delete)
UPDATE users
SET is_active = false
WHERE id = 'user-uuid';
```

**Security Features:**
```sql
-- Account locking (5 failed attempts = 30 min lock)
SELECT record_failed_login('user@example.com');
-- After 5 attempts, account_locked_until is set

-- Password expiry report (90+ days)
SELECT email, password_changed_at,
       CURRENT_TIMESTAMP - password_changed_at as password_age
FROM users
WHERE password_changed_at < CURRENT_TIMESTAMP - INTERVAL '90 days'
  AND is_active = true
ORDER BY password_changed_at ASC;

-- Users without email verification
SELECT email, created_at
FROM users
WHERE is_email_verified = false
  AND created_at < CURRENT_TIMESTAMP - INTERVAL '7 days'
ORDER BY created_at ASC;
```

**Committee Queries:**
```sql
-- List committee members
SELECT 
  committee_member,
  COUNT(*) as member_count,
  STRING_AGG(first_name || ' ' || last_name, ', ') as members
FROM users
WHERE committee_member IS NOT NULL
  AND is_active = true
GROUP BY committee_member;
```

**Activity Report:**
```sql
-- User activity by role
SELECT 
  role,
  COUNT(*) as total_users,
  COUNT(*) FILTER (WHERE is_active = true) as active_users,
  COUNT(*) FILTER (WHERE last_login >= CURRENT_TIMESTAMP - INTERVAL '30 days') as active_last_30d,
  COUNT(*) FILTER (WHERE mfa_enabled = true) as mfa_count
FROM users
GROUP BY role
ORDER BY total_users DESC;
```

**Best Practices:**
1. **Never store plain text passwords** - Always use bcrypt ($2b$12$ or higher)
2. **Use parameterized queries** - Prevent SQL injection
3. **Implement rate limiting** - Prevent brute force attacks
4. **Enforce MFA** - For supervisors and admins
5. **Regular password rotation** - 90-day policy recommended
6. **Audit access logs** - Track login attempts and activity
7. **Email verification** - Require before full access
8. **Soft delete** - Set is_active=false instead of DELETE

**Password Hashing (Python example):**
```python
import bcrypt

# Hash password (during registration)
password = "user_password"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
password_hash = hashed.decode('utf-8')  # Store in database

# Verify password (during login)
if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
    print("Password correct")
else:
    print("Password incorrect")
```

**Verification:**
```bash
python backend/db/migrations/verify_users_table.py
```

---

### 014_create_sessions.sql

Creates the `user_sessions` table for session management, JWT tokens, and refresh tokens:

**Purpose:**
- Manage JWT access tokens and refresh tokens
- Track active user sessions across devices
- Support session validation and revocation
- Enable "logout from all devices" functionality
- Session cleanup and expiry management
- Device/browser tracking for security

**Columns (14):**
- **Session:** session_token (UNIQUE), refresh_token
- **Device:** ip_address, user_agent, device_type, device_name
- **Timing:** created_at, expires_at, last_activity
- **Status:** is_active, revoked_at, revoked_reason
- **Audit:** user_id (FK to users)

**Indexes (8):**
- idx_sessions_user_id - User's sessions (with is_active)
- idx_sessions_token - Session token lookup (partial, active only)
- idx_sessions_refresh_token - Refresh token lookup (partial)
- idx_sessions_expires_at - Expired session cleanup
- idx_sessions_active - Active sessions (partial, with last_activity)
- idx_sessions_created_at (DESC) - Recent sessions
- idx_sessions_device_type - Device analytics
- idx_sessions_revoked - Revoked sessions audit (partial)

**CHECK Constraints (5):**
- device_type: desktop, mobile, tablet, api, unknown
- session_token: Not empty
- expires_at: After created_at
- revoked_at: After created_at (if set)
- revoked_not_active: If revoked, must be inactive

**Session Management Functions (7):**
```sql
-- Create new session (login)
SELECT create_session(
  user_id, session_token, refresh_token,
  ip_address, user_agent, device_type,
  expires_in_hours  -- default 8 hours
);

-- Validate session token (returns is_valid, user_id, expires_at)
SELECT * FROM validate_session('jwt.token.here');

-- Revoke session (logout)
SELECT revoke_session('jwt.token.here', 'user_logout');

-- Revoke all user sessions (logout from all devices)
SELECT revoke_all_user_sessions(user_id, 'logout_all_devices');

-- Get user's active sessions
SELECT * FROM get_user_active_sessions(user_id);

-- Refresh session (extend expiry, issue new tokens)
SELECT refresh_session(
  old_refresh_token, new_session_token,
  new_refresh_token, extend_hours
);

-- Cleanup expired sessions (retention policy)
SELECT cleanup_expired_sessions(days_to_keep);  -- default 30 days
```

**Token Expiry:**
- **JWT tokens:** 8 hours (configurable)
- **Refresh tokens:** 7 days (configurable)
- **Session cleanup:** 30 days after expiry (default)

**Usage Examples:**
```sql
-- Login: Create session
SELECT create_session(
  '123e4567-e89b-12d3-a456-426614174000'::UUID,
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',  -- JWT token
  'refresh_token_abc123...',
  '192.168.1.100'::INET,
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
  'desktop',
  8  -- expires in 8 hours
);

-- Validate on each request
SELECT * FROM validate_session('jwt.token.here');
-- Returns: session_id, user_id, is_valid, expires_at

-- Logout
SELECT revoke_session('jwt.token.here', 'user_logout');

-- Logout from all devices
SELECT revoke_all_user_sessions(
  '123e4567-e89b-12d3-a456-426614174000',
  'logout_all_devices'
);

-- List user's active sessions
SELECT 
  device_type, device_name, ip_address,
  created_at, last_activity, expires_at
FROM get_user_active_sessions('123e4567-e89b-12d3-a456-426614174000');
```

**Token Refresh Flow:**
```sql
-- When JWT expires, use refresh token to get new tokens
SELECT refresh_session(
  'old_refresh_token',
  'new_jwt_token',
  'new_refresh_token',
  8  -- extend 8 hours
);
-- Returns: new_session_id
-- Old session automatically revoked with reason 'token_refreshed'
```

**Session Analytics:**
```sql
-- Active sessions by device type
SELECT 
  device_type,
  COUNT(*) as session_count,
  COUNT(*) FILTER (WHERE is_active = true) as active_count
FROM user_sessions
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY device_type;

-- Concurrent sessions per user
SELECT 
  u.email,
  COUNT(*) as active_sessions,
  STRING_AGG(s.device_type, ', ') as devices
FROM user_sessions s
JOIN users u ON u.id = s.user_id
WHERE s.is_active = true
  AND s.expires_at > CURRENT_TIMESTAMP
GROUP BY u.id, u.email
HAVING COUNT(*) > 1;

-- Recent logins
SELECT 
  u.email, s.created_at as login_time,
  s.ip_address, s.device_type
FROM user_sessions s
JOIN users u ON u.id = s.user_id
WHERE s.created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY s.created_at DESC;
```

**Security Features:**
- **Token uniqueness:** Each session has unique token
- **Automatic expiry:** Enforced at database level
- **Revocation support:** Immediate session invalidation
- **Device tracking:** IP, user agent, device type
- **Last activity:** Track session usage
- **Cleanup policy:** Auto-delete old expired sessions

**Best Practices:**
1. **Store token hashes** - Don't store raw JWT tokens (optional)
2. **Short JWT expiry** - 8 hours recommended
3. **Longer refresh tokens** - 7 days for convenience
4. **Monitor concurrent sessions** - Flag suspicious activity
5. **Regular cleanup** - Run cleanup_expired_sessions daily
6. **Track devices** - Help users identify sessions
7. **Revoke on password change** - Force re-authentication

**Integration with JWT (Python example):**
```python
import jwt
from datetime import datetime, timedelta

# Create JWT token
payload = {
    'user_id': str(user_id),
    'email': user_email,
    'role': user_role,
    'exp': datetime.utcnow() + timedelta(hours=8)
}
jwt_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

# Store in database
cursor.execute("""
    SELECT create_session(%s, %s, %s, %s, %s, %s, 8)
""", (user_id, jwt_token, refresh_token, ip_address, user_agent, device_type))

# Validate JWT on request
try:
    decoded = jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])
    # Also check database session
    cursor.execute("SELECT * FROM validate_session(%s)", (jwt_token,))
    session = cursor.fetchone()
    if session['is_valid']:
        # Proceed with request
        pass
except jwt.ExpiredSignatureError:
    # Token expired, require refresh
    pass
```

**Verification:**
```bash
python backend/db/migrations/verify_sessions_table.py
```

---

**REIMS Development Team**  
October 12, 2025



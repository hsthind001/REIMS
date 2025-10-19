-- Migration 011: Create Metrics Log Table
-- Purpose: Store historical Prometheus metrics snapshots for long-term analysis
-- Optional: Prometheus scrapes /metrics endpoint directly, this is for archival
-- Date: 2025-10-12

-- ============================================================================
-- METRICS_LOG TABLE: Historical metrics snapshots for trend analysis
-- ============================================================================

CREATE TABLE IF NOT EXISTS metrics_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Metric Identification
  metric_name VARCHAR(255) NOT NULL, -- 'api_requests_total', 'api_latency_seconds', etc.
  metric_type VARCHAR(50), -- 'counter', 'gauge', 'histogram', 'summary'
  labels JSONB, -- Flexible label storage: {method: 'GET', endpoint: '/api/analytics', status: '200'}
  
  -- Value & Time
  metric_value DECIMAL(18, 6), -- Support both integers and decimals
  recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  -- Context
  application VARCHAR(50), -- 'backend', 'frontend', 'worker', 'storage_service'
  environment VARCHAR(50) -- 'development', 'staging', 'production'
);

-- ============================================================================
-- INDEXES: Optimized for time-series queries
-- ============================================================================

-- Primary query pattern: metric name + time range
CREATE INDEX idx_metrics_name_time ON metrics_log(metric_name, recorded_at DESC);

-- Temporal queries (all metrics in time range)
CREATE INDEX idx_metrics_recorded_at ON metrics_log(recorded_at DESC);

-- Metric name + labels for specific queries
CREATE INDEX idx_metrics_name_labels ON metrics_log(metric_name, labels);

-- JSONB GIN index for flexible label queries
CREATE INDEX idx_metrics_labels_gin ON metrics_log USING GIN(labels);

-- Application-specific queries
CREATE INDEX idx_metrics_application ON metrics_log(application, recorded_at DESC);

-- Environment-specific queries
CREATE INDEX idx_metrics_environment ON metrics_log(environment, recorded_at DESC);

-- Metric type queries
CREATE INDEX idx_metrics_type ON metrics_log(metric_type, recorded_at DESC);

-- ============================================================================
-- CONSTRAINTS: Basic data validation
-- ============================================================================

-- Metric type must be valid Prometheus type
ALTER TABLE metrics_log
  ADD CONSTRAINT chk_metric_type 
  CHECK (metric_type IS NULL OR metric_type IN ('counter', 'gauge', 'histogram', 'summary'));

-- Valid application names
ALTER TABLE metrics_log
  ADD CONSTRAINT chk_application 
  CHECK (application IS NULL OR application IN ('backend', 'frontend', 'worker', 'storage_service', 'queue_service', 'nginx'));

-- Valid environments
ALTER TABLE metrics_log
  ADD CONSTRAINT chk_environment 
  CHECK (environment IS NULL OR environment IN ('development', 'staging', 'production', 'test'));

-- Recorded_at should not be in the future
ALTER TABLE metrics_log
  ADD CONSTRAINT chk_recorded_at 
  CHECK (recorded_at <= CURRENT_TIMESTAMP + INTERVAL '1 minute');

-- ============================================================================
-- TABLE PARTITIONING: Optional, for high-volume metrics (> 10M rows)
-- ============================================================================

-- Uncomment to enable time-based partitioning
-- This example shows daily partitioning
-- 
-- CREATE TABLE metrics_log_2025_10_12 PARTITION OF metrics_log
-- FOR VALUES FROM ('2025-10-12 00:00:00') TO ('2025-10-13 00:00:00');
-- 
-- CREATE TABLE metrics_log_2025_10_13 PARTITION OF metrics_log
-- FOR VALUES FROM ('2025-10-13 00:00:00') TO ('2025-10-14 00:00:00');
-- 
-- Note: Requires converting metrics_log to a partitioned table first:
-- CREATE TABLE metrics_log (...) PARTITION BY RANGE (recorded_at);

-- ============================================================================
-- DATA RETENTION POLICY
-- ============================================================================

-- Function to clean up old metrics (optional)
CREATE OR REPLACE FUNCTION cleanup_old_metrics(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
  rows_deleted INTEGER;
BEGIN
  DELETE FROM metrics_log
  WHERE recorded_at < CURRENT_TIMESTAMP - (days_to_keep || ' days')::INTERVAL;
  
  GET DIAGNOSTICS rows_deleted = ROW_COUNT;
  
  RAISE NOTICE 'Deleted % old metric records (older than % days)', rows_deleted, days_to_keep;
  
  RETURN rows_deleted;
END;
$$ LANGUAGE plpgsql;

-- Example: Schedule cleanup to run monthly via pg_cron or external scheduler
-- SELECT cron.schedule('cleanup-metrics', '0 2 1 * *', 'SELECT cleanup_old_metrics(90);');

-- ============================================================================
-- TABLE COMMENTS: Documentation for database administrators
-- ============================================================================

COMMENT ON TABLE metrics_log IS 'Historical Prometheus metrics snapshots for long-term trend analysis. Optional: Prometheus scrapes /metrics endpoint directly. This table stores archived snapshots for analysis beyond Prometheus retention period.';

COMMENT ON COLUMN metrics_log.metric_name IS 'Prometheus metric name (e.g., api_requests_total, api_latency_seconds)';
COMMENT ON COLUMN metrics_log.metric_type IS 'Prometheus metric type: counter, gauge, histogram, summary';
COMMENT ON COLUMN metrics_log.labels IS 'JSONB object containing metric labels (e.g., {method: "GET", endpoint: "/api/properties"})';
COMMENT ON COLUMN metrics_log.metric_value IS 'Numeric metric value';
COMMENT ON COLUMN metrics_log.recorded_at IS 'When this metric was recorded (typically UTC)';
COMMENT ON COLUMN metrics_log.application IS 'Application component: backend, frontend, worker, storage_service';
COMMENT ON COLUMN metrics_log.environment IS 'Deployment environment: development, staging, production';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify table creation
DO $$
BEGIN
  IF EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'metrics_log'
  ) THEN
    RAISE NOTICE 'metrics_log table created successfully';
  ELSE
    RAISE EXCEPTION 'metrics_log table creation failed';
  END IF;
END $$;

-- ============================================================================
-- USAGE EXAMPLES (for developers)
-- ============================================================================

-- Example 1: Insert API request counter
-- INSERT INTO metrics_log (
--   metric_name, metric_type, labels, metric_value,
--   application, environment
-- ) VALUES (
--   'api_requests_total', 'counter',
--   '{"method": "GET", "endpoint": "/api/properties", "status": "200"}'::jsonb,
--   12543,
--   'backend', 'production'
-- );

-- Example 2: Insert API latency gauge
-- INSERT INTO metrics_log (
--   metric_name, metric_type, labels, metric_value,
--   application, environment
-- ) VALUES (
--   'api_latency_seconds', 'gauge',
--   '{"method": "POST", "endpoint": "/api/documents/upload"}'::jsonb,
--   0.245,
--   'backend', 'production'
-- );

-- Example 3: Insert database connection pool metric
-- INSERT INTO metrics_log (
--   metric_name, metric_type, labels, metric_value,
--   application, environment
-- ) VALUES (
--   'db_connections_active', 'gauge',
--   '{"pool": "main", "database": "reims"}'::jsonb,
--   8,
--   'backend', 'production'
-- );

-- Example 4: Query metrics for a specific endpoint over time
-- SELECT 
--   recorded_at,
--   metric_value,
--   labels->>'method' as method,
--   labels->>'status' as status
-- FROM metrics_log
-- WHERE metric_name = 'api_requests_total'
--   AND labels->>'endpoint' = '/api/properties'
--   AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
-- ORDER BY recorded_at DESC;

-- Example 5: Average latency per endpoint (last hour)
-- SELECT 
--   labels->>'endpoint' as endpoint,
--   labels->>'method' as method,
--   AVG(metric_value) as avg_latency_seconds,
--   MIN(metric_value) as min_latency_seconds,
--   MAX(metric_value) as max_latency_seconds,
--   COUNT(*) as sample_count
-- FROM metrics_log
-- WHERE metric_name = 'api_latency_seconds'
--   AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
-- GROUP BY labels->>'endpoint', labels->>'method'
-- ORDER BY avg_latency_seconds DESC;

-- Example 6: Request rate per minute
-- SELECT 
--   DATE_TRUNC('minute', recorded_at) as minute,
--   labels->>'endpoint' as endpoint,
--   MAX(metric_value) - MIN(metric_value) as requests_per_minute
-- FROM metrics_log
-- WHERE metric_name = 'api_requests_total'
--   AND labels->>'endpoint' = '/api/analytics'
--   AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
-- GROUP BY DATE_TRUNC('minute', recorded_at), labels->>'endpoint'
-- ORDER BY minute DESC;

-- Example 7: Top 10 most requested endpoints (today)
-- SELECT 
--   labels->>'endpoint' as endpoint,
--   labels->>'method' as method,
--   MAX(metric_value) - MIN(metric_value) as total_requests
-- FROM metrics_log
-- WHERE metric_name = 'api_requests_total'
--   AND recorded_at >= DATE_TRUNC('day', CURRENT_TIMESTAMP)
-- GROUP BY labels->>'endpoint', labels->>'method'
-- ORDER BY total_requests DESC
-- LIMIT 10;

-- Example 8: Error rate (5xx responses)
-- WITH total_requests AS (
--   SELECT 
--     DATE_TRUNC('hour', recorded_at) as hour,
--     MAX(metric_value) as count
--   FROM metrics_log
--   WHERE metric_name = 'api_requests_total'
--     AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
--   GROUP BY DATE_TRUNC('hour', recorded_at)
-- ),
-- error_requests AS (
--   SELECT 
--     DATE_TRUNC('hour', recorded_at) as hour,
--     MAX(metric_value) as count
--   FROM metrics_log
--   WHERE metric_name = 'api_requests_total'
--     AND labels->>'status' LIKE '5%'
--     AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
--   GROUP BY DATE_TRUNC('hour', recorded_at)
-- )
-- SELECT 
--   t.hour,
--   t.count as total_requests,
--   COALESCE(e.count, 0) as error_requests,
--   ROUND((COALESCE(e.count, 0)::NUMERIC / NULLIF(t.count, 0)) * 100, 2) as error_rate_pct
-- FROM total_requests t
-- LEFT JOIN error_requests e ON t.hour = e.hour
-- ORDER BY t.hour DESC;

-- Example 9: Batch insert multiple metrics (efficient)
-- INSERT INTO metrics_log (metric_name, metric_type, labels, metric_value, application, environment)
-- VALUES 
--   ('api_requests_total', 'counter', '{"endpoint": "/api/properties"}'::jsonb, 1000, 'backend', 'production'),
--   ('api_latency_seconds', 'gauge', '{"endpoint": "/api/properties"}'::jsonb, 0.123, 'backend', 'production'),
--   ('db_connections_active', 'gauge', '{"pool": "main"}'::jsonb, 5, 'backend', 'production');

-- Example 10: Query metrics by label (using JSONB operators)
-- SELECT 
--   metric_name,
--   metric_value,
--   labels,
--   recorded_at
-- FROM metrics_log
-- WHERE labels @> '{"status": "500"}'::jsonb  -- Contains this key-value
--   AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
-- ORDER BY recorded_at DESC;

-- Example 11: Time-series aggregation (5-minute buckets)
-- SELECT 
--   DATE_TRUNC('minute', recorded_at) - 
--     EXTRACT(MINUTE FROM recorded_at)::INTEGER % 5 * INTERVAL '1 minute' as time_bucket,
--   labels->>'endpoint' as endpoint,
--   AVG(metric_value) as avg_value,
--   MAX(metric_value) as max_value,
--   MIN(metric_value) as min_value
-- FROM metrics_log
-- WHERE metric_name = 'api_latency_seconds'
--   AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
-- GROUP BY time_bucket, labels->>'endpoint'
-- ORDER BY time_bucket DESC;

-- Example 12: Cleanup old metrics (manual execution)
-- SELECT cleanup_old_metrics(90); -- Delete metrics older than 90 days


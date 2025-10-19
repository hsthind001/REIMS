-- Migration 012: Create Performance Logs Table
-- Purpose: Track request performance for optimization and SLA monitoring
-- Target: 90% requests < 500ms
-- Date: 2025-10-12

-- ============================================================================
-- PERFORMANCE_LOGS TABLE: Request performance tracking and bottleneck detection
-- ============================================================================

CREATE TABLE IF NOT EXISTS performance_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Request Information
  request_id VARCHAR(100) NOT NULL UNIQUE,
  endpoint VARCHAR(255) NOT NULL, -- /api/analytics, /api/documents/upload
  method VARCHAR(10), -- GET, POST, PUT, DELETE, PATCH
  
  -- Timing
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NOT NULL,
  duration_ms INTEGER, -- Total request duration in milliseconds
  
  -- Database Performance
  db_queries_count INTEGER,
  db_time_ms INTEGER, -- Total time spent in database queries
  
  -- Cache Performance
  cache_hits INTEGER DEFAULT 0,
  cache_misses INTEGER DEFAULT 0,
  cache_time_ms INTEGER DEFAULT 0,
  
  -- External Services
  external_service_calls INTEGER DEFAULT 0,
  external_service_time_ms INTEGER DEFAULT 0,
  
  -- Response
  status_code INTEGER,
  response_size_bytes INTEGER,
  
  -- User Context
  user_id UUID,
  ip_address INET,
  
  -- Performance Flags
  is_slow BOOLEAN, -- Duration > 1000ms
  is_error BOOLEAN, -- Status >= 400
  
  -- Audit
  logged_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES: Optimized for performance analysis queries
-- ============================================================================

-- Primary query pattern: endpoint performance over time
CREATE INDEX idx_perf_endpoint_time ON performance_logs(endpoint, start_time DESC);

-- Slow request identification
CREATE INDEX idx_perf_duration ON performance_logs(duration_ms DESC);

-- Slow request filtering with time
CREATE INDEX idx_perf_slow ON performance_logs(is_slow, start_time DESC) WHERE is_slow = true;

-- Error request filtering
CREATE INDEX idx_perf_errors ON performance_logs(is_error, start_time DESC) WHERE is_error = true;

-- Temporal queries
CREATE INDEX idx_perf_logged_at ON performance_logs(logged_at DESC);
CREATE INDEX idx_perf_start_time ON performance_logs(start_time DESC);

-- User-specific performance
CREATE INDEX idx_perf_user_id ON performance_logs(user_id, start_time DESC);

-- Status code analysis
CREATE INDEX idx_perf_status_code ON performance_logs(status_code, start_time DESC);

-- Method-specific analysis
CREATE INDEX idx_perf_method ON performance_logs(method, start_time DESC);

-- Database performance queries
CREATE INDEX idx_perf_db_time ON performance_logs(db_time_ms DESC) WHERE db_time_ms IS NOT NULL;

-- ============================================================================
-- CONSTRAINTS: Data validation and business rules
-- ============================================================================

-- Valid HTTP methods
ALTER TABLE performance_logs
  ADD CONSTRAINT chk_method 
  CHECK (method IS NULL OR method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'));

-- Valid HTTP status codes
ALTER TABLE performance_logs
  ADD CONSTRAINT chk_status_code 
  CHECK (status_code IS NULL OR (status_code >= 100 AND status_code <= 599));

-- Duration must be non-negative
ALTER TABLE performance_logs
  ADD CONSTRAINT chk_duration_ms 
  CHECK (duration_ms IS NULL OR duration_ms >= 0);

-- End time must be after start time
ALTER TABLE performance_logs
  ADD CONSTRAINT chk_end_after_start 
  CHECK (end_time >= start_time);

-- Database metrics must be non-negative
ALTER TABLE performance_logs
  ADD CONSTRAINT chk_db_queries_count 
  CHECK (db_queries_count IS NULL OR db_queries_count >= 0);

ALTER TABLE performance_logs
  ADD CONSTRAINT chk_db_time_ms 
  CHECK (db_time_ms IS NULL OR db_time_ms >= 0);

-- Cache metrics must be non-negative
ALTER TABLE performance_logs
  ADD CONSTRAINT chk_cache_hits 
  CHECK (cache_hits >= 0);

ALTER TABLE performance_logs
  ADD CONSTRAINT chk_cache_misses 
  CHECK (cache_misses >= 0);

ALTER TABLE performance_logs
  ADD CONSTRAINT chk_cache_time_ms 
  CHECK (cache_time_ms >= 0);

-- External service metrics must be non-negative
ALTER TABLE performance_logs
  ADD CONSTRAINT chk_external_calls 
  CHECK (external_service_calls >= 0);

ALTER TABLE performance_logs
  ADD CONSTRAINT chk_external_time_ms 
  CHECK (external_service_time_ms >= 0);

-- Response size must be non-negative
ALTER TABLE performance_logs
  ADD CONSTRAINT chk_response_size 
  CHECK (response_size_bytes IS NULL OR response_size_bytes >= 0);

-- ============================================================================
-- TRIGGERS: Auto-calculate derived fields
-- ============================================================================

-- Function to calculate duration and set flags
CREATE OR REPLACE FUNCTION calculate_performance_metrics()
RETURNS TRIGGER AS $$
BEGIN
  -- Calculate duration if not provided
  IF NEW.duration_ms IS NULL AND NEW.end_time IS NOT NULL AND NEW.start_time IS NOT NULL THEN
    NEW.duration_ms = EXTRACT(EPOCH FROM (NEW.end_time - NEW.start_time)) * 1000;
  END IF;
  
  -- Set is_slow flag (> 1000ms)
  IF NEW.duration_ms IS NOT NULL THEN
    NEW.is_slow = (NEW.duration_ms > 1000);
  END IF;
  
  -- Set is_error flag (status >= 400)
  IF NEW.status_code IS NOT NULL THEN
    NEW.is_error = (NEW.status_code >= 400);
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-calculate metrics
CREATE TRIGGER trigger_calculate_performance_metrics
  BEFORE INSERT OR UPDATE ON performance_logs
  FOR EACH ROW
  EXECUTE FUNCTION calculate_performance_metrics();

-- ============================================================================
-- DATA RETENTION FUNCTION
-- ============================================================================

-- Function to clean up old performance logs
CREATE OR REPLACE FUNCTION cleanup_old_performance_logs(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
  rows_deleted INTEGER;
BEGIN
  DELETE FROM performance_logs
  WHERE logged_at < CURRENT_TIMESTAMP - (days_to_keep || ' days')::INTERVAL;
  
  GET DIAGNOSTICS rows_deleted = ROW_COUNT;
  
  RAISE NOTICE 'Deleted % old performance log records (older than % days)', rows_deleted, days_to_keep;
  
  RETURN rows_deleted;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- MATERIALIZED VIEW: Performance summary for dashboards
-- ============================================================================

-- Hourly performance summary
CREATE MATERIALIZED VIEW IF NOT EXISTS performance_summary_hourly AS
SELECT 
  DATE_TRUNC('hour', start_time) as hour,
  endpoint,
  method,
  COUNT(*) as request_count,
  AVG(duration_ms) as avg_duration_ms,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_ms) as p50_duration_ms,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) as p95_duration_ms,
  PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY duration_ms) as p99_duration_ms,
  MAX(duration_ms) as max_duration_ms,
  COUNT(*) FILTER (WHERE is_slow = true) as slow_requests_count,
  COUNT(*) FILTER (WHERE is_error = true) as error_requests_count,
  AVG(db_time_ms) as avg_db_time_ms,
  AVG(cache_hits::NUMERIC / NULLIF(cache_hits + cache_misses, 0)) as cache_hit_rate,
  SUM(response_size_bytes) as total_response_bytes
FROM performance_logs
GROUP BY DATE_TRUNC('hour', start_time), endpoint, method;

-- Index on materialized view
CREATE INDEX idx_perf_summary_hour ON performance_summary_hourly(hour DESC, endpoint);

-- Function to refresh performance summary
CREATE OR REPLACE FUNCTION refresh_performance_summary()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY performance_summary_hourly;
  RAISE NOTICE 'Performance summary refreshed';
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TABLE COMMENTS: Documentation for database administrators
-- ============================================================================

COMMENT ON TABLE performance_logs IS 'Request performance tracking for optimization and SLA monitoring. Target: 90% requests < 500ms. Used to identify slow endpoints and performance bottlenecks.';

COMMENT ON COLUMN performance_logs.request_id IS 'Unique request identifier for tracing';
COMMENT ON COLUMN performance_logs.endpoint IS 'API endpoint path (e.g., /api/analytics)';
COMMENT ON COLUMN performance_logs.method IS 'HTTP method: GET, POST, PUT, DELETE, PATCH';

COMMENT ON COLUMN performance_logs.start_time IS 'Request start timestamp';
COMMENT ON COLUMN performance_logs.end_time IS 'Request end timestamp';
COMMENT ON COLUMN performance_logs.duration_ms IS 'Total request duration in milliseconds (auto-calculated)';

COMMENT ON COLUMN performance_logs.db_queries_count IS 'Number of database queries executed';
COMMENT ON COLUMN performance_logs.db_time_ms IS 'Total time spent in database queries';

COMMENT ON COLUMN performance_logs.cache_hits IS 'Number of cache hits';
COMMENT ON COLUMN performance_logs.cache_misses IS 'Number of cache misses';
COMMENT ON COLUMN performance_logs.cache_time_ms IS 'Total time spent on cache operations';

COMMENT ON COLUMN performance_logs.external_service_calls IS 'Number of external service calls';
COMMENT ON COLUMN performance_logs.external_service_time_ms IS 'Total time spent on external service calls';

COMMENT ON COLUMN performance_logs.status_code IS 'HTTP response status code';
COMMENT ON COLUMN performance_logs.response_size_bytes IS 'Response body size in bytes';

COMMENT ON COLUMN performance_logs.user_id IS 'User who made the request';
COMMENT ON COLUMN performance_logs.ip_address IS 'Client IP address';

COMMENT ON COLUMN performance_logs.is_slow IS 'Whether request duration > 1000ms (auto-calculated)';
COMMENT ON COLUMN performance_logs.is_error IS 'Whether status code >= 400 (auto-calculated)';

COMMENT ON COLUMN performance_logs.logged_at IS 'When this log entry was created';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify table creation
DO $$
BEGIN
  IF EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'performance_logs'
  ) THEN
    RAISE NOTICE 'performance_logs table created successfully';
  ELSE
    RAISE EXCEPTION 'performance_logs table creation failed';
  END IF;
END $$;

-- ============================================================================
-- USAGE EXAMPLES (for developers)
-- ============================================================================

-- Example 1: Insert performance log (duration auto-calculated)
-- INSERT INTO performance_logs (
--   request_id, endpoint, method,
--   start_time, end_time,
--   db_queries_count, db_time_ms,
--   cache_hits, cache_misses,
--   status_code, response_size_bytes,
--   user_id, ip_address
-- ) VALUES (
--   'req-abc123', '/api/properties', 'GET',
--   '2025-10-12 10:30:00', '2025-10-12 10:30:00.245',
--   5, 120,
--   3, 1,
--   200, 15234,
--   'user-uuid-here', '192.168.1.100'
-- );

-- Example 2: Query slow endpoints
-- SELECT 
--   endpoint,
--   COUNT(*) as slow_count,
--   AVG(duration_ms) as avg_duration_ms,
--   MAX(duration_ms) as max_duration_ms
-- FROM performance_logs
-- WHERE is_slow = true
--   AND start_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
-- GROUP BY endpoint
-- ORDER BY slow_count DESC;

-- Example 3: SLA compliance report (% requests < 500ms)
-- SELECT 
--   endpoint,
--   COUNT(*) as total_requests,
--   COUNT(*) FILTER (WHERE duration_ms < 500) as fast_requests,
--   ROUND((COUNT(*) FILTER (WHERE duration_ms < 500)::NUMERIC / COUNT(*)) * 100, 2) as sla_compliance_pct
-- FROM performance_logs
-- WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
-- GROUP BY endpoint
-- ORDER BY sla_compliance_pct ASC;

-- Example 4: Identify database bottlenecks
-- SELECT 
--   endpoint,
--   AVG(duration_ms) as avg_total_duration_ms,
--   AVG(db_time_ms) as avg_db_time_ms,
--   ROUND((AVG(db_time_ms)::NUMERIC / AVG(duration_ms)) * 100, 2) as db_time_pct,
--   AVG(db_queries_count) as avg_db_queries
-- FROM performance_logs
-- WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
--   AND db_time_ms IS NOT NULL
-- GROUP BY endpoint
-- ORDER BY db_time_pct DESC;

-- Example 5: Cache effectiveness
-- SELECT 
--   endpoint,
--   SUM(cache_hits) as total_cache_hits,
--   SUM(cache_misses) as total_cache_misses,
--   ROUND((SUM(cache_hits)::NUMERIC / NULLIF(SUM(cache_hits + cache_misses), 0)) * 100, 2) as cache_hit_rate_pct
-- FROM performance_logs
-- WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
--   AND (cache_hits > 0 OR cache_misses > 0)
-- GROUP BY endpoint
-- ORDER BY cache_hit_rate_pct ASC;

-- Example 6: Percentile analysis (P50, P95, P99)
-- SELECT 
--   endpoint,
--   COUNT(*) as request_count,
--   PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_ms) as p50_ms,
--   PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) as p95_ms,
--   PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY duration_ms) as p99_ms
-- FROM performance_logs
-- WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
-- GROUP BY endpoint
-- ORDER BY p99_ms DESC;

-- Example 7: Error rate analysis
-- SELECT 
--   endpoint,
--   COUNT(*) as total_requests,
--   COUNT(*) FILTER (WHERE is_error = true) as error_requests,
--   ROUND((COUNT(*) FILTER (WHERE is_error = true)::NUMERIC / COUNT(*)) * 100, 2) as error_rate_pct,
--   STRING_AGG(DISTINCT status_code::TEXT, ', ') as error_statuses
-- FROM performance_logs
-- WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
-- GROUP BY endpoint
-- HAVING COUNT(*) FILTER (WHERE is_error = true) > 0
-- ORDER BY error_rate_pct DESC;

-- Example 8: Time-series performance (15-minute buckets)
-- SELECT 
--   DATE_TRUNC('minute', start_time) - 
--     EXTRACT(MINUTE FROM start_time)::INTEGER % 15 * INTERVAL '1 minute' as time_bucket,
--   endpoint,
--   COUNT(*) as request_count,
--   AVG(duration_ms) as avg_duration_ms,
--   COUNT(*) FILTER (WHERE is_slow = true) as slow_count
-- FROM performance_logs
-- WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL '4 hours'
-- GROUP BY time_bucket, endpoint
-- ORDER BY time_bucket DESC, avg_duration_ms DESC;

-- Example 9: User-specific performance
-- SELECT 
--   user_id,
--   COUNT(*) as request_count,
--   AVG(duration_ms) as avg_duration_ms,
--   COUNT(*) FILTER (WHERE is_error = true) as error_count
-- FROM performance_logs
-- WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
--   AND user_id IS NOT NULL
-- GROUP BY user_id
-- ORDER BY request_count DESC
-- LIMIT 10;

-- Example 10: External service impact
-- SELECT 
--   endpoint,
--   AVG(duration_ms) as avg_total_duration_ms,
--   AVG(external_service_time_ms) as avg_external_time_ms,
--   AVG(external_service_calls) as avg_external_calls,
--   ROUND((AVG(external_service_time_ms)::NUMERIC / AVG(duration_ms)) * 100, 2) as external_time_pct
-- FROM performance_logs
-- WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
--   AND external_service_calls > 0
-- GROUP BY endpoint
-- ORDER BY external_time_pct DESC;

-- Example 11: Query using materialized view (faster for dashboards)
-- SELECT * FROM performance_summary_hourly
-- WHERE hour >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
--   AND endpoint = '/api/analytics'
-- ORDER BY hour DESC;

-- Example 12: Cleanup old logs (manual)
-- SELECT cleanup_old_performance_logs(30); -- Delete logs older than 30 days

-- Example 13: Refresh performance summary (run periodically)
-- SELECT refresh_performance_summary();


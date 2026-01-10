# Debugging Prompt: API 500 Error - Database Connection Failure

## Issue Context
- **Issue Description**: API returning 500 errors
- **Error Message**: Internal Server Error: Database connection failed
- **Environment**: production
- **Language**: Python
- **Urgency**: critical
- **Include Logs**: true
- **Include Solutions**: true

## Debugging Strategy

### 1. Immediate Assessment

**Critical Production Issue - Database Connection Failure**

This is a **critical production issue** requiring immediate attention. The API is returning 500 errors due to database connection failures.

### 2. Diagnostic Steps

#### Step 1: Verify Database Service Status
```bash
# Check if database service is running
systemctl status postgresql  # or mysql, mongodb, etc.
# Or for containerized databases
docker ps | grep -i database
```

#### Step 2: Check Database Connection Parameters
- Verify connection string/hostname
- Check credentials (username/password)
- Verify port accessibility
- Confirm network connectivity between API and database

#### Step 3: Review Application Logs
```bash
# Check application logs for detailed error messages
tail -f /var/log/app/error.log
# Or container logs
docker logs <api-container> --tail 100 -f
```

Look for:
- Connection timeout errors
- Authentication failures
- Network unreachable errors
- Connection pool exhaustion

#### Step 4: Test Database Connectivity
```python
# Quick connectivity test
import psycopg2  # or appropriate driver
try:
    conn = psycopg2.connect(
        host="your-host",
        database="your-db",
        user="your-user",
        password="your-password"
    )
    print("Connection successful")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
```

### 3. Common Root Causes

#### A. Database Service Down
- **Symptom**: Connection refused errors
- **Solution**: Restart database service
- **Prevention**: Set up monitoring and auto-restart

#### B. Connection Pool Exhausted
- **Symptom**: "Too many connections" or timeout errors
- **Solution**: 
  - Increase max_connections
  - Review connection pool settings in application
  - Ensure connections are properly closed
- **Prevention**: Implement connection pooling with limits

#### C. Network Issues
- **Symptom**: Connection timeout
- **Solution**: 
  - Check firewall rules
  - Verify network routes
  - Test network connectivity (ping, telnet)
- **Prevention**: Network monitoring and redundancy

#### D. Authentication Failures
- **Symptom**: "Authentication failed" errors
- **Solution**: 
  - Verify credentials
  - Check password expiration
  - Review user permissions
- **Prevention**: Credential rotation policies

#### E. Resource Exhaustion
- **Symptom**: Database out of memory/disk
- **Solution**: 
  - Free up disk space
  - Increase memory limits
  - Optimize queries
- **Prevention**: Resource monitoring and alerts

### 4. Immediate Mitigation Steps

1. **Check Database Health**
   ```bash
   # PostgreSQL
   psql -h localhost -U postgres -c "SELECT version();"
   
   # MySQL
   mysql -h localhost -u root -p -e "SELECT VERSION();"
   ```

2. **Review Connection Pool Configuration**
   ```python
   # Example: Check connection pool settings
   # In your application config
   MAX_CONNECTIONS = 20
   CONNECTION_TIMEOUT = 30
   ```

3. **Enable Detailed Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   # Enable database driver logging
   ```

4. **Implement Circuit Breaker Pattern**
   ```python
   # Prevent cascading failures
   # Return cached data or graceful degradation
   ```

### 5. Long-term Solutions

#### A. Connection Pooling
- Use connection pool managers (SQLAlchemy, psycopg2 pool)
- Set appropriate pool size and timeout
- Monitor pool usage metrics

#### B. Health Checks
- Implement database health check endpoints
- Set up monitoring alerts
- Automated failover mechanisms

#### C. Retry Logic with Exponential Backoff
```python
import time
from functools import wraps

def retry_db_connection(max_retries=3, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except DatabaseError as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = backoff_factor ** attempt
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator
```

#### D. Monitoring and Alerting
- Set up database connection metrics
- Alert on connection failure rates
- Monitor connection pool utilization
- Track query performance

### 6. Log Analysis Checklist

When reviewing logs, look for:
- [ ] Connection timeout timestamps
- [ ] Error frequency patterns
- [ ] Correlation with other system events
- [ ] User impact (affected endpoints)
- [ ] Recovery time after failures

### 7. Prevention Checklist

- [ ] Database connection pooling configured
- [ ] Connection limits set appropriately
- [ ] Health checks implemented
- [ ] Monitoring and alerting in place
- [ ] Retry logic with backoff
- [ ] Circuit breaker pattern
- [ ] Graceful degradation strategy
- [ ] Regular connection testing
- [ ] Database backup and recovery procedures
- [ ] Documentation of connection parameters

### 8. Emergency Rollback Plan

If issue persists:
1. Check if recent deployments affected database configuration
2. Review recent database migrations
3. Consider rolling back recent changes
4. Activate maintenance mode if needed
5. Notify stakeholders of service degradation

## Next Steps

1. **Immediate**: Verify database service status and connectivity
2. **Short-term**: Review logs and identify root cause
3. **Medium-term**: Implement monitoring and alerting
4. **Long-term**: Review architecture for resilience

## Additional Resources

- Database connection best practices
- Connection pooling strategies
- Monitoring database health
- Error handling patterns
- Circuit breaker implementation

---

**Note**: This debugging prompt was generated based on the provided context. For production issues, always prioritize:
1. Service restoration
2. Impact assessment
3. Root cause analysis
4. Prevention measures

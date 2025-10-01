# 📊 Scouter Monitoring Guide

Complete guide for monitoring receipt processing performance, costs, and quality with Prometheus + Grafana.

---

## 🚀 Quick Start (2 Minutes)

### 1. Start Monitoring Stack

```bash
# Start Prometheus + Grafana with Docker
docker compose up -d
```

### 2. Create Dashboards Automatically

```bash
# One-time setup: creates pre-built dashboard
python setup_grafana_dashboards.py
```

### 3. Start Scouter

```bash
# Starts the app (monitoring auto-starts too)
./start.sh
```

### 4. Access Dashboard

```
http://localhost:3000
Login: admin/admin
```

**Done!** Your dashboard is ready with 11 panels tracking everything.

---

## 📈 What You Get

### Pre-Built Dashboard Panels

Your automated dashboard includes:

| Panel | What It Shows |
|-------|---------------|
| **Processing Duration (P95)** | How long 95% of receipts take end-to-end |
| **Throughput** | Receipts processed per minute (success + failed) |
| **Step Duration Breakdown** | Time spent in each step (upload, OCR, AI, validation) |
| **Concurrent Processing** | Number of receipts being processed right now |
| **Average Confidence Score** | AI confidence in extracted data (0-1) |
| **AI Cost per Hour** | Real-time OpenAI API spending |
| **Human Review Rate** | % of receipts requiring manual review |
| **Success Rate** | % of successfully processed receipts (color-coded) |
| **Total Receipts** | Cumulative count of processed receipts |
| **Total AI Tokens** | Cumulative OpenAI tokens consumed |
| **Total AI Cost** | Cumulative estimated costs |

### Real-Time Metrics

Every receipt processed generates metrics for:

- ⏱️ **Timing**: Overall + per-step duration (P50, P95, P99)
- ✅ **Success/Failure**: Total + failures by step
- 🎯 **Quality**: AI confidence scores, review rates
- 💰 **Cost**: Tokens used, estimated API costs
- 📊 **Resources**: Concurrent processing, upload sizes

---

## 🔗 Access URLs

After running `./start.sh`:

| Service | URL | Purpose |
|---------|-----|---------|
| **Grafana Dashboard** | http://localhost:3000 | Visualize metrics |
| **Prometheus** | http://localhost:9090 | Query raw metrics |
| **Metrics API** | http://localhost:5001/metrics | Raw Prometheus format |
| **Scouter App** | http://localhost:5001 | Receipt processing |

---

## 📊 Available Metrics

### Overall Pipeline Metrics
- `receipt_processing_duration_seconds` - Total end-to-end time (histogram)
- `receipt_processing_success_total` - Successfully processed (counter)
- `receipt_processing_failed_total{step}` - Failed by step (counter)
- `receipt_processing_in_progress` - Currently processing (gauge)

### Per-Step Performance
- `receipt_step_duration_seconds{step="upload|ocr|ai|validation"}` - Duration per step (histogram)

> 💡 **See [PERFORMANCE_ANALYSIS.md](PERFORMANCE_ANALYSIS.md) for detailed queries and bottleneck identification**

### Quality Metrics
- `receipt_confidence_score` - AI confidence 0-1.0 (histogram)
- `receipt_human_review_required_total` - Receipts needing review (counter)

### Cost Tracking
- `receipt_ai_tokens_used_total{token_type}` - OpenAI tokens (counter)
- `receipt_ai_cost_estimate_usd` - Estimated costs (counter)

### Additional Metrics
- `receipt_upload_size_bytes` - Image sizes (histogram)

### Service-Specific Error Metrics
- `s3_upload_errors_total{error_code, error_type}` - S3 upload failures by HTTP code and error type
- `document_ai_errors_total{error_code, error_type}` - Document AI failures by HTTP code and error type
- `openai_errors_total{error_code, error_type}` - OpenAI API failures by HTTP code and error type

**Common Error Codes:**
- **S3:** 403 (AccessDenied), 404 (NoSuchBucket), 503 (ServiceUnavailable)
- **Document AI:** 400 (InvalidArgument), 403 (PermissionDenied), 429 (ResourceExhausted), 500 (Internal), 503 (Unavailable)
- **OpenAI:** 400 (BadRequest), 401 (Unauthorized), 429 (RateLimitExceeded), 500 (InternalError), 503 (ServiceUnavailable)

---

## 🔍 Useful Prometheus Queries

### Average Processing Time
```promql
rate(receipt_processing_duration_seconds_sum[5m]) / rate(receipt_processing_duration_seconds_count[5m])
```

### Success Rate (%)
```promql
100 * rate(receipt_processing_success_total[5m]) / 
(rate(receipt_processing_success_total[5m]) + rate(receipt_processing_failed_total[5m]))
```

### Cost per Receipt
```promql
rate(receipt_ai_cost_estimate_usd[1h]) / rate(receipt_processing_success_total[1h])
```

### Slowest Step
```promql
topk(1, sum by (step) (rate(receipt_step_duration_seconds_sum[5m])) / 
sum by (step) (rate(receipt_step_duration_seconds_count[5m])))
```

### Throughput (receipts/min)
```promql
rate(receipt_processing_success_total[1m]) * 60
```

### P95 Latency
```promql
histogram_quantile(0.95, rate(receipt_processing_duration_seconds_bucket[5m]))
```

### Service Error Rates

**S3 Upload Errors by Type:**
```promql
sum by (error_type) (rate(s3_upload_errors_total[5m]))
```

**Document AI Errors by Code:**
```promql
sum by (error_code, error_type) (rate(document_ai_errors_total[5m]))
```

**OpenAI Errors by Type:**
```promql
sum by (error_type) (rate(openai_errors_total[5m]))
```

**Total Service Errors:**
```promql
sum(rate(s3_upload_errors_total[5m])) + 
sum(rate(document_ai_errors_total[5m])) + 
sum(rate(openai_errors_total[5m]))
```

**Most Common Error:**
```promql
topk(1, 
  sum by (service, error_type) (
    label_replace(rate(s3_upload_errors_total[5m]), "service", "S3", "", "") or
    label_replace(rate(document_ai_errors_total[5m]), "service", "DocumentAI", "", "") or
    label_replace(rate(openai_errors_total[5m]), "service", "OpenAI", "", "")
  )
)
```

---

## 🛠️ Docker Commands

```bash
# Start monitoring
docker compose up -d

# Stop monitoring
docker compose down

# View logs
docker compose logs -f prometheus
docker compose logs -f grafana

# Restart services
docker compose restart

# Check status
docker compose ps

# Remove everything (including data)
docker compose down -v
```

---

## 🐛 Troubleshooting

### Dashboard Shows "No Data"

**Check 1: Are metrics being generated?**
```bash
curl http://localhost:5001/metrics | grep receipt_processing
```
Should show metrics with values > 0 after processing receipts.

**Check 2: Is Prometheus scraping?**
```bash
curl -s 'http://localhost:9090/api/v1/targets' | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'
```
Should show `"health": "up"` for the scouter job.

Or visit: http://localhost:9090/targets (should show "scouter (1/1 up)")

**Check 3: Have you processed any receipts?**
- Metrics only appear after processing at least one receipt
- Go to http://localhost:5001 and upload a test receipt

**Check 4: Is Prometheus querying correctly?**
Visit: http://localhost:9090/graph

Try query:
```promql
receipt_processing_success_total
```

If it shows data but Grafana doesn't, recreate dashboards:
```bash
python setup_grafana_dashboards.py
```

### Prometheus Can't Reach Scouter

**Problem:** Targets page shows "down"

**Solution:**
```bash
# Recreate containers with proper networking
docker compose down
docker compose up -d

# Wait 10 seconds, then check
curl -s 'http://localhost:9090/api/v1/query?query=up' | jq
```

The `value` should be `"1"` (not `"0"`).

### Grafana Won't Load

**Problem:** http://localhost:3000 doesn't respond

**Solution:**
```bash
# Check if container is running
docker compose ps

# If not running, start it
docker compose up -d grafana

# Check logs for errors
docker compose logs grafana

# If still broken, recreate
docker compose down
docker compose up -d
```

### Dashboard Creation Failed

**Problem:** `setup_grafana_dashboards.py` fails

**Solution 1: Wait for Grafana**
```bash
sleep 30
python setup_grafana_dashboards.py
```

**Solution 2: Check Grafana health**
```bash
curl http://localhost:3000/api/health
```
Should return `{"database":"ok"}`

**Solution 3: Verify credentials**
Default is admin/admin. If you changed it, update the script:
```python
GRAFANA_PASSWORD = "your-password"
```

### Port Conflicts

**Problem:** Port 3000 or 9090 already in use

**Solution:**
```bash
# Find what's using the port
lsof -i:3000
lsof -i:9090

# Stop conflicting services
pkill grafana-server
pkill prometheus

# Or change ports in docker-compose.yml:
# ports:
#   - "3001:3000"  # Grafana on 3001
#   - "9091:9090"  # Prometheus on 9091
```

---

## 🎯 Recommended Alerts

### High Failure Rate
```yaml
alert: HighReceiptFailureRate
expr: |
  rate(receipt_processing_failed_total[5m]) / 
  (rate(receipt_processing_success_total[5m]) + rate(receipt_processing_failed_total[5m])) > 0.1
for: 5m
annotations:
  summary: "Receipt processing failure rate > 10%"
```

### Slow Processing
```yaml
alert: SlowReceiptProcessing
expr: |
  histogram_quantile(0.95, rate(receipt_processing_duration_seconds_bucket[5m])) > 60
for: 10m
annotations:
  summary: "P95 processing time > 60 seconds"
```

### High AI Costs
```yaml
alert: HighAICosts
expr: |
  rate(receipt_ai_cost_estimate_usd[1h]) > 10
for: 15m
annotations:
  summary: "AI costs > $10/hour"
```

### Low Confidence Scores
```yaml
alert: LowConfidenceScores
expr: |
  rate(receipt_confidence_score_sum[5m]) / rate(receipt_confidence_score_count[5m]) < 0.7
for: 15m
annotations:
  summary: "Average confidence score < 70%"
```

### Service-Specific Errors

```yaml
alert: HighS3ErrorRate
expr: |
  rate(s3_upload_errors_total[5m]) > 0.05
for: 10m
annotations:
  summary: "S3 upload error rate > 5%"

alert: DocumentAIQuotaExceeded
expr: |
  rate(document_ai_errors_total{error_code="429"}[5m]) > 0
for: 5m
annotations:
  summary: "Document AI quota/rate limit exceeded"

alert: OpenAIRateLimitHit
expr: |
  rate(openai_errors_total{error_code="429"}[5m]) > 0
for: 5m
annotations:
  summary: "OpenAI rate limit exceeded"

alert: OpenAIAuthFailure
expr: |
  rate(openai_errors_total{error_code="401"}[5m]) > 0
for: 1m
annotations:
  summary: "OpenAI authentication failure - check API key"
```

To add alerts:
1. Grafana → Alerting → Alert rules → New alert rule
2. Set query and condition
3. Add notification channel (email, Slack, etc.)

---

## 📝 Testing Metrics

### Manual Test Script

```bash
# Test metrics endpoint
curl http://localhost:5001/metrics

# Should see these metrics with data:
# receipt_processing_success_total 1.0
# receipt_processing_duration_seconds_sum X.X
# receipt_step_duration_seconds_count{step="upload"} 1.0
# receipt_ai_tokens_used_total X.0
```

### Automated Test
```bash
python test_metrics.py
```

This verifies:
- ✅ Metrics endpoint is accessible
- ✅ All expected metrics are present
- ✅ Metrics format is valid
- ✅ Prometheus can parse the data

---

## 🔒 Production Considerations

### Change Default Password

Edit `docker-compose.yml`:
```yaml
environment:
  - GF_SECURITY_ADMIN_PASSWORD=your-strong-password
```

Then recreate:
```bash
docker compose down
docker compose up -d
```

### Add Resource Limits

Edit `docker-compose.yml`:
```yaml
services:
  prometheus:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
  grafana:
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 256M
```

### Enable HTTPS

```yaml
grafana:
  environment:
    - GF_SERVER_PROTOCOL=https
    - GF_SERVER_CERT_FILE=/etc/grafana/cert.pem
    - GF_SERVER_CERT_KEY=/etc/grafana/key.pem
  volumes:
    - ./certs/cert.pem:/etc/grafana/cert.pem:ro
    - ./certs/key.pem:/etc/grafana/key.pem:ro
```

### Backup Dashboards

```bash
# Export dashboard
curl -s http://admin:admin@localhost:3000/api/dashboards/uid/<DASHBOARD_UID> > dashboard-backup.json

# Or backup entire Grafana volume
docker run --rm -v scouter_grafana_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/grafana-backup.tar.gz -C /data .
```

### Long-Term Storage

For production, configure Prometheus remote write to services like:
- Thanos (open-source)
- Cortex (open-source)
- Grafana Cloud (managed)
- AWS Managed Prometheus (managed)

---

## 🎨 Dashboard Customization

### Edit Existing Panels

1. Open dashboard: http://localhost:3000
2. Click panel title → Edit
3. Modify query, visualization, or settings
4. Save dashboard

### Add New Panel

1. Click "+ Add" → Visualization
2. Select data source: Prometheus
3. Enter query (see Useful Queries above)
4. Configure visualization type (graph, stat, etc.)
5. Save

### Create New Dashboard

1. Click "+" → Dashboard
2. Add panels with custom queries
3. Save with descriptive name

### Export/Import Dashboard

**Export:**
- Dashboard settings → JSON Model → Copy JSON

**Import:**
- Dashboards → Import → Paste JSON

---

## 📚 Additional Resources

### Learn Prometheus
- Query language (PromQL): https://prometheus.io/docs/prometheus/latest/querying/basics/
- Best practices: https://prometheus.io/docs/practices/naming/
- Functions reference: https://prometheus.io/docs/prometheus/latest/querying/functions/

### Learn Grafana
- Dashboard creation: https://grafana.com/docs/grafana/latest/dashboards/
- Alerting: https://grafana.com/docs/grafana/latest/alerting/
- Panel types: https://grafana.com/docs/grafana/latest/panels-visualizations/

---

## 🎯 Quick Commands Reference

```bash
# Complete setup (first time)
docker compose up -d
python setup_grafana_dashboards.py
./start.sh

# Daily usage
./start.sh                      # Start everything
open http://localhost:3000      # Open dashboard

# Maintenance
docker compose logs -f          # View logs
docker compose restart          # Restart services
docker compose ps               # Check status

# Testing
curl http://localhost:5001/metrics              # Raw metrics
curl http://localhost:9090/targets              # Prometheus targets
python test_metrics.py                          # Run tests

# Cleanup
docker compose down             # Stop (keep data)
docker compose down -v          # Stop + remove data
```

---

## ✅ Success Checklist

After setup, verify:

- [ ] `docker compose ps` shows 2 containers running
- [ ] http://localhost:9090/targets shows "scouter (1/1 up)"
- [ ] http://localhost:3000 loads Grafana
- [ ] http://localhost:5001 loads Scouter
- [ ] `curl http://localhost:5001/metrics` returns data
- [ ] Grafana has "Prometheus" datasource
- [ ] Grafana has "Scouter Receipt Processing" dashboard
- [ ] Upload a receipt and see metrics update in dashboard

---

**🎉 All set! Your monitoring stack is ready to track receipt processing performance, costs, and quality in real-time!**


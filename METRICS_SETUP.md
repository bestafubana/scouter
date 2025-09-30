# Scouter Metrics Setup Guide 📊

## Quick Start

### 1. Install Dependencies

The Prometheus client is already in `requirements.txt`. If you need to reinstall:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Install Monitoring Tools (Optional)

```bash
# macOS
brew install prometheus grafana

# Linux
sudo apt-get install prometheus grafana
```

### 3. Start Scouter

```bash
./start.sh
```

**The start script will automatically:**
- ✅ Start MailHog (email testing)
- ✅ Start Prometheus (if installed) - creates `prometheus.yml` if missing
- ✅ Start Grafana (if installed)
- ✅ Start Scouter application

**You'll see output like:**
```
📧 Starting MailHog for email testing...
✅ MailHog started successfully

📊 Starting Prometheus for metrics...
✅ Prometheus started successfully
📈 Prometheus UI: http://localhost:9090

📈 Starting Grafana for dashboards...
✅ Grafana started successfully
📊 Grafana UI: http://localhost:3000

🚀 Starting authentication server on http://localhost:5001
🔗 Quick Links:
   • Scouter App: http://localhost:5001/index.html
   • MailHog: http://localhost:8025
   • Prometheus: http://localhost:9090
   • Grafana: http://localhost:3000
```

Metrics are automatically exposed at: **http://localhost:5001/metrics**

### 4. View Raw Metrics

```bash
curl http://localhost:5001/metrics
```

## Manual Setup (Optional - start.sh does this automatically)

### Setup Prometheus

If you installed Prometheus but want to customize the config:

#### macOS

```bash
# Install
brew install prometheus

# Edit the auto-generated prometheus.yml or create custom config
cat > prometheus.yml <<'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'scouter'
    static_configs:
      - targets: ['localhost:5001']
    metrics_path: '/metrics'
    scrape_interval: 5s
EOF

# Restart with ./start.sh or manually:
prometheus --config.file=prometheus.yml
```

### Linux

```bash
# Download
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*

# Create config (same as above)
cat > prometheus.yml <<'EOF'
...
EOF

# Start
./prometheus --config.file=prometheus.yml
```

**Access Prometheus UI:** http://localhost:9090

## Setup Grafana (5 minutes)

### macOS

```bash
# Install & Start
brew install grafana
brew services start grafana
```

### Linux

```bash
# Install
sudo apt-get install -y grafana

# Start
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

**Access Grafana:** http://localhost:3000 (admin/admin)

### Configure Grafana

1. **Add Data Source:**
   - Go to Configuration → Data Sources
   - Click "Add data source"
   - Select "Prometheus"
   - URL: `http://localhost:9090`
   - Click "Save & Test"

2. **Import Dashboard:**
   - Click "+" → "Import"
   - Paste the dashboard JSON from below
   - Select your Prometheus data source
   - Click "Import"

## Quick Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Scouter Receipt Processing",
    "timezone": "browser",
    "panels": [
      {
        "title": "Processing Duration (P50, P95, P99)",
        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(receipt_processing_duration_seconds_bucket[5m]))",
            "legendFormat": "P50"
          },
          {
            "expr": "histogram_quantile(0.95, rate(receipt_processing_duration_seconds_bucket[5m]))",
            "legendFormat": "P95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(receipt_processing_duration_seconds_bucket[5m]))",
            "legendFormat": "P99"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Throughput (receipts/min)",
        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8},
        "targets": [
          {
            "expr": "rate(receipt_processing_success_total[1m]) * 60",
            "legendFormat": "Success"
          },
          {
            "expr": "rate(receipt_processing_failed_total[1m]) * 60",
            "legendFormat": "Failed"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Step Duration Breakdown",
        "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8},
        "targets": [
          {
            "expr": "rate(receipt_step_duration_seconds_sum[5m]) / rate(receipt_step_duration_seconds_count[5m])",
            "legendFormat": "{{step}}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "AI Cost per Hour",
        "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8},
        "targets": [
          {
            "expr": "rate(receipt_ai_cost_estimate_usd[1h])",
            "legendFormat": "Cost USD/hour"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Confidence Score Distribution",
        "gridPos": {"x": 0, "y": 16, "w": 12, "h": 8},
        "targets": [
          {
            "expr": "rate(receipt_confidence_score_sum[5m]) / rate(receipt_confidence_score_count[5m])",
            "legendFormat": "Average Confidence"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Concurrent Processing",
        "gridPos": {"x": 12, "y": 16, "w": 12, "h": 8},
        "targets": [
          {
            "expr": "receipt_processing_in_progress",
            "legendFormat": "In Progress"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

## Useful Prometheus Queries

### Performance

```promql
# Average processing time (last 5 min)
rate(receipt_processing_duration_seconds_sum[5m]) / rate(receipt_processing_duration_seconds_count[5m])

# P95 processing time
histogram_quantile(0.95, rate(receipt_processing_duration_seconds_bucket[5m]))

# Slowest step
topk(1, sum by (step) (rate(receipt_step_duration_seconds_sum[5m])) / sum by (step) (rate(receipt_step_duration_seconds_count[5m])))

# Throughput (receipts per minute)
rate(receipt_processing_success_total[1m]) * 60
```

### Quality

```promql
# Success rate
rate(receipt_processing_success_total[5m]) / (rate(receipt_processing_success_total[5m]) + rate(receipt_processing_failed_total[5m]))

# Average confidence score
rate(receipt_confidence_score_sum[5m]) / rate(receipt_confidence_score_count[5m])

# Human review rate
rate(receipt_human_review_required_total[1h]) / rate(receipt_processing_success_total[1h])
```

### Costs

```promql
# AI cost per hour
rate(receipt_ai_cost_estimate_usd[1h])

# Daily AI cost
increase(receipt_ai_cost_estimate_usd[24h])

# Tokens per receipt
rate(receipt_ai_tokens_used_total[5m]) / rate(receipt_processing_success_total[5m])
```

### Errors

```promql
# Failure rate by step
sum by (step) (rate(receipt_processing_failed_total[5m]))

# Error percentage
rate(receipt_processing_failed_total[5m]) / (rate(receipt_processing_success_total[5m]) + rate(receipt_processing_failed_total[5m])) * 100
```

## Testing Metrics

### 1. Test Script

```bash
python test_metrics.py
```

Expected output:
```
🎉 All metrics tests passed!
```

### 2. Upload a Receipt

1. Go to http://localhost:5001
2. Upload a receipt image
3. Wait for processing to complete

### 3. Query Metrics

In Prometheus (http://localhost:9090/graph):
```promql
receipt_processing_duration_seconds
```

You should see your test receipt's timing!

## Available Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `receipt_processing_duration_seconds` | Histogram | Total end-to-end time |
| `receipt_step_duration_seconds{step}` | Histogram | Per-step timing (upload, ocr, ai, validation) |
| `receipt_processing_success_total` | Counter | Successful receipts |
| `receipt_processing_failed_total{step}` | Counter | Failed receipts by step |
| `receipt_processing_in_progress` | Gauge | Currently processing |
| `receipt_confidence_score` | Histogram | AI confidence (0-1.0) |
| `receipt_ai_tokens_used_total{token_type}` | Counter | OpenAI tokens consumed |
| `receipt_ai_cost_estimate_usd` | Counter | Estimated API costs |
| `receipt_upload_size_bytes` | Histogram | Image file sizes |
| `receipt_human_review_required_total` | Counter | Low confidence receipts |

## Troubleshooting

### Metrics endpoint returns 404

Restart Scouter:
```bash
./start.sh
```

### Prometheus can't scrape metrics

Check Scouter is running:
```bash
curl http://localhost:5001/metrics
```

Check Prometheus config has correct target:
```yaml
targets: ['localhost:5001']  # Match your Scouter port
```

### Grafana shows "No data"

1. Check Prometheus is scraping: http://localhost:9090/targets
2. Verify metrics exist: http://localhost:9090/graph
3. Check Grafana data source connection: Configuration → Data Sources

### Missing metrics after upgrade

Reinstall dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

## Next Steps

1. **Set Up Alerts:**
   - Create `alerts.yml` with threshold rules
   - Configure notification channels (Slack, email)

2. **Optimize Performance:**
   - Identify bottlenecks using step duration metrics
   - Monitor P95/P99 latencies
   - Track failure patterns

3. **Cost Management:**
   - Set budget alerts on AI costs
   - Monitor token usage trends
   - Optimize prompts based on cost metrics

4. **Production Deployment:**
   - Use Prometheus remote storage for long-term retention
   - Set up Grafana dashboards for each team
   - Configure alerting and on-call rotations

## Support

- Full documentation: See `README.md` → "Performance Monitoring"
- Prometheus docs: https://prometheus.io/docs/
- Grafana docs: https://grafana.com/docs/


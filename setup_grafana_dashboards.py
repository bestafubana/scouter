#!/usr/bin/env python3
"""
Automatically configure Grafana with Prometheus data source and create dashboards
"""

import json
import time
import requests
from requests.auth import HTTPBasicAuth

# Configuration
GRAFANA_URL = "http://localhost:3000"
GRAFANA_USER = "admin"
GRAFANA_PASSWORD = "admin"
PROMETHEUS_URL = "http://prometheus:9090"  # Docker internal network
# PROMETHEUS_URL = "http://localhost:9090"  # For native Prometheus

def wait_for_grafana(max_attempts=30):
    """Wait for Grafana to be ready"""
    print("⏳ Waiting for Grafana to be ready...")
    for i in range(max_attempts):
        try:
            response = requests.get(f"{GRAFANA_URL}/api/health", timeout=2)
            if response.status_code == 200:
                print("✅ Grafana is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
        print(f"   Attempt {i+1}/{max_attempts}...")
    return False

def add_prometheus_datasource():
    """Add Prometheus as a data source"""
    print("\n📊 Adding Prometheus data source...")
    
    # Check if datasource already exists
    response = requests.get(
        f"{GRAFANA_URL}/api/datasources/name/Prometheus",
        auth=HTTPBasicAuth(GRAFANA_USER, GRAFANA_PASSWORD)
    )
    
    if response.status_code == 200:
        print("✅ Prometheus data source already exists")
        return response.json()['uid']
    
    datasource = {
        "name": "Prometheus",
        "type": "prometheus",
        "url": PROMETHEUS_URL,
        "access": "proxy",
        "isDefault": True,
        "jsonData": {
            "httpMethod": "POST",
            "timeInterval": "15s"
        }
    }
    
    response = requests.post(
        f"{GRAFANA_URL}/api/datasources",
        auth=HTTPBasicAuth(GRAFANA_USER, GRAFANA_PASSWORD),
        json=datasource,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code in [200, 409]:
        uid = response.json().get('datasource', {}).get('uid') or response.json().get('uid')
        print(f"✅ Prometheus data source added (UID: {uid})")
        return uid
    else:
        print(f"❌ Failed to add data source: {response.text}")
        return None

def create_scouter_dashboard(datasource_uid):
    """Create the main Scouter monitoring dashboard"""
    print("\n📈 Creating Scouter Receipt Processing dashboard...")
    
    dashboard = {
        "dashboard": {
            "title": "Scouter Receipt Processing",
            "tags": ["scouter", "receipts", "ai"],
            "timezone": "browser",
            "schemaVersion": 16,
            "version": 0,
            "refresh": "5s",
            "panels": [
                # Row 1: Overview Metrics
                {
                    "title": "Processing Duration (P95)",
                    "type": "graph",
                    "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
                    "targets": [{
                        "expr": "histogram_quantile(0.95, rate(receipt_processing_duration_seconds_bucket[5m]))",
                        "legendFormat": "P95",
                        "refId": "A",
                        "datasource": {"type": "prometheus", "uid": datasource_uid}
                    }],
                    "yaxes": [{"format": "s", "label": "Seconds"}, {"format": "short"}]
                },
                {
                    "title": "Throughput (receipts/min)",
                    "type": "graph",
                    "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8},
                    "targets": [{
                        "expr": "rate(receipt_processing_success_total[1m]) * 60",
                        "legendFormat": "Success",
                        "refId": "A",
                        "datasource": {"type": "prometheus", "uid": datasource_uid}
                    }, {
                        "expr": "rate(receipt_processing_failed_total[1m]) * 60",
                        "legendFormat": "Failed",
                        "refId": "B",
                        "datasource": {"type": "prometheus", "uid": datasource_uid}
                    }],
                    "yaxes": [{"format": "short", "label": "Receipts/min"}, {"format": "short"}]
                },
                
                # Row 2: Step Breakdown
                {
                    "title": "Step Duration Breakdown",
                    "type": "graph",
                    "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8},
                    "targets": [{
                        "expr": "sum by (step) (rate(receipt_step_duration_seconds_sum[5m])) / sum by (step) (rate(receipt_step_duration_seconds_count[5m]))",
                        "legendFormat": "{{step}}",
                        "refId": "A",
                        "datasource": {"type": "prometheus", "uid": datasource_uid}
                    }],
                    "yaxes": [{"format": "s", "label": "Seconds"}, {"format": "short"}]
                },
                {
                    "title": "Concurrent Processing",
                    "type": "graph",
                    "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8},
                    "targets": [{
                        "expr": "receipt_processing_in_progress",
                        "legendFormat": "In Progress",
                        "refId": "A",
                        "datasource": {"type": "prometheus", "uid": datasource_uid}
                    }],
                    "yaxes": [{"format": "short", "label": "Count"}, {"format": "short"}]
                },
                
                # Row 3: Quality & Cost
                {
                    "title": "Average Confidence Score",
                    "type": "graph",
                    "gridPos": {"x": 0, "y": 16, "w": 8, "h": 8},
                    "targets": [{
                        "expr": "rate(receipt_confidence_score_sum[5m]) / rate(receipt_confidence_score_count[5m])",
                        "legendFormat": "Confidence",
                        "refId": "A",
                        "datasource": {"type": "prometheus", "uid": datasource_uid}
                    }],
                    "yaxes": [{"format": "percentunit", "label": "Confidence", "min": 0, "max": 1}, {"format": "short"}]
                },
                {
                    "title": "AI Cost per Hour",
                    "type": "graph",
                    "gridPos": {"x": 8, "y": 16, "w": 8, "h": 8},
                    "targets": [{
                        "expr": "rate(receipt_ai_cost_estimate_usd[1h])",
                        "legendFormat": "Cost/hour",
                        "refId": "A",
                        "datasource": {"type": "prometheus", "uid": datasource_uid}
                    }],
                    "yaxes": [{"format": "currencyUSD", "label": "USD/hour"}, {"format": "short"}]
                },
                {
                    "title": "Human Review Rate",
                    "type": "graph",
                    "gridPos": {"x": 16, "y": 16, "w": 8, "h": 8},
                    "targets": [{
                        "expr": "rate(receipt_human_review_required_total[1h]) / rate(receipt_processing_success_total[1h])",
                        "legendFormat": "Review Rate",
                        "refId": "A",
                        "datasource": {"type": "prometheus", "uid": datasource_uid}
                    }],
                    "yaxes": [{"format": "percentunit", "label": "Rate", "min": 0, "max": 1}, {"format": "short"}]
                },
                
                # Row 4: Success Rate & Stats
                {
                    "title": "Success Rate",
                    "type": "stat",
                    "gridPos": {"x": 0, "y": 24, "w": 6, "h": 4},
                    "targets": [{
                        "expr": "rate(receipt_processing_success_total[5m]) / (rate(receipt_processing_success_total[5m]) + rate(receipt_processing_failed_total[5m]))",
                        "refId": "A",
                        "datasource": {"type": "prometheus", "uid": datasource_uid}
                    }],
                    "options": {
                        "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                        "textMode": "value_and_name"
                    },
                    "fieldConfig": {
                        "defaults": {
                            "unit": "percentunit",
                            "min": 0,
                            "max": 1,
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"value": 0, "color": "red"},
                                    {"value": 0.8, "color": "yellow"},
                                    {"value": 0.95, "color": "green"}
                                ]
                            }
                        }
                    }
                },
                {
                    "title": "Total Receipts Processed",
                    "type": "stat",
                    "gridPos": {"x": 6, "y": 24, "w": 6, "h": 4},
                    "targets": [{
                        "expr": "receipt_processing_success_total",
                        "refId": "A",
                        "datasource": {"type": "prometheus", "uid": datasource_uid}
                    }],
                    "options": {
                        "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                        "textMode": "value_and_name"
                    },
                    "fieldConfig": {
                        "defaults": {"unit": "short"}
                    }
                },
                {
                    "title": "Total AI Tokens Used",
                    "type": "stat",
                    "gridPos": {"x": 12, "y": 24, "w": 6, "h": 4},
                    "targets": [{
                        "expr": "receipt_ai_tokens_used_total",
                        "refId": "A",
                        "datasource": {"type": "prometheus", "uid": datasource_uid}
                    }],
                    "options": {
                        "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                        "textMode": "value_and_name"
                    },
                    "fieldConfig": {
                        "defaults": {"unit": "short"}
                    }
                },
                {
                    "title": "Total AI Cost",
                    "type": "stat",
                    "gridPos": {"x": 18, "y": 24, "w": 6, "h": 4},
                    "targets": [{
                        "expr": "receipt_ai_cost_estimate_usd",
                        "refId": "A",
                        "datasource": {"type": "prometheus", "uid": datasource_uid}
                    }],
                    "options": {
                        "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                        "textMode": "value_and_name"
                    },
                    "fieldConfig": {
                        "defaults": {"unit": "currencyUSD"}
                    }
                }
            ]
        },
        "overwrite": True
    }
    
    response = requests.post(
        f"{GRAFANA_URL}/api/dashboards/db",
        auth=HTTPBasicAuth(GRAFANA_USER, GRAFANA_PASSWORD),
        json=dashboard,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Dashboard created successfully!")
        print(f"🔗 View at: {GRAFANA_URL}{result['url']}")
        return result['url']
    else:
        print(f"❌ Failed to create dashboard: {response.text}")
        return None

def main():
    print("🚀 Setting up Grafana for Scouter...")
    print(f"📍 Grafana URL: {GRAFANA_URL}")
    print(f"📍 Prometheus URL: {PROMETHEUS_URL}")
    print()
    
    # Wait for Grafana
    if not wait_for_grafana():
        print("❌ Grafana is not responding. Make sure it's running:")
        print("   docker compose up -d")
        print("   or: ./start-monitoring.sh")
        return 1
    
    # Add Prometheus datasource
    datasource_uid = add_prometheus_datasource()
    if not datasource_uid:
        print("❌ Failed to add Prometheus data source")
        return 1
    
    # Create dashboard
    dashboard_url = create_scouter_dashboard(datasource_uid)
    if not dashboard_url:
        print("❌ Failed to create dashboard")
        return 1
    
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print(f"\n🔗 Grafana Dashboard: {GRAFANA_URL}{dashboard_url}")
    print(f"🔗 Prometheus: http://localhost:9090")
    print(f"\n💡 Login: admin/admin (you'll be prompted to change password)")
    print("\n📊 The dashboard includes:")
    print("   • Processing duration (P95)")
    print("   • Throughput (receipts/minute)")
    print("   • Step duration breakdown")
    print("   • Concurrent processing")
    print("   • Confidence scores")
    print("   • AI costs")
    print("   • Success rate")
    print("\n🎉 Start processing receipts to see real-time metrics!")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())


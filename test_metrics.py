#!/usr/bin/env python3
"""
Test script to verify Prometheus metrics are working correctly
"""

import sys
from metrics import (
    receipt_processing_duration,
    receipt_processing_success_total,
    receipt_processing_failed_total,
    receipt_processing_in_progress,
    receipt_step_duration,
    receipt_confidence_score,
    receipt_ai_tokens_used,
    receipt_ai_cost_estimate,
    receipt_upload_size_bytes,
    receipt_human_review_required,
    get_metrics
)

def test_metrics():
    """Test all metrics can be incremented and collected"""
    print("🧪 Testing Prometheus Metrics...\n")
    
    # Test 1: Increment counters
    print("✅ Testing counters...")
    receipt_processing_success_total.inc()
    receipt_processing_failed_total.labels(step='upload').inc()
    receipt_ai_tokens_used.labels(token_type='total').inc(450)
    receipt_ai_cost_estimate.inc(0.0203)
    receipt_human_review_required.inc()
    print("   Counters incremented successfully")
    
    # Test 2: Update gauges
    print("✅ Testing gauges...")
    receipt_processing_in_progress.inc()
    receipt_processing_in_progress.dec()
    print("   Gauges updated successfully")
    
    # Test 3: Observe histograms
    print("✅ Testing histograms...")
    receipt_processing_duration.observe(5.2)
    receipt_step_duration.labels(step='upload').observe(1.2)
    receipt_step_duration.labels(step='ocr').observe(2.5)
    receipt_step_duration.labels(step='ai').observe(1.8)
    receipt_step_duration.labels(step='validation').observe(0.3)
    receipt_confidence_score.observe(0.91)
    receipt_upload_size_bytes.observe(524288)
    print("   Histograms recorded successfully")
    
    # Test 4: Generate metrics output
    print("✅ Testing metrics export...")
    metrics_data, content_type = get_metrics()
    print(f"   Content-Type: {content_type}")
    print(f"   Metrics size: {len(metrics_data)} bytes")
    
    # Test 5: Verify metrics content
    print("\n📊 Sample Metrics Output:\n")
    print("-" * 80)
    lines = metrics_data.decode('utf-8').split('\n')
    
    # Show a sample of the metrics
    for line in lines[:50]:
        if line and not line.startswith('#'):
            print(line)
    
    print("-" * 80)
    print(f"\n✅ Total metrics lines: {len(lines)}")
    
    # Verify key metrics are present
    metrics_text = metrics_data.decode('utf-8')
    required_metrics = [
        'receipt_processing_duration_seconds',
        'receipt_processing_success_total',
        'receipt_processing_failed_total',
        'receipt_processing_in_progress',
        'receipt_step_duration_seconds',
        'receipt_confidence_score',
        'receipt_ai_tokens_used_total',
        'receipt_ai_cost_estimate_usd'
    ]
    
    print("\n🔍 Verifying Required Metrics:")
    all_present = True
    for metric in required_metrics:
        present = metric in metrics_text
        status = "✅" if present else "❌"
        print(f"   {status} {metric}")
        if not present:
            all_present = False
    
    if all_present:
        print("\n🎉 All metrics tests passed! Prometheus integration is working correctly.")
        return 0
    else:
        print("\n❌ Some metrics are missing. Check the implementation.")
        return 1

if __name__ == '__main__':
    sys.exit(test_metrics())


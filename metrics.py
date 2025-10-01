"""
Prometheus Metrics for Scouter Receipt Processing

This module defines all Prometheus metrics for monitoring receipt processing performance.
Metrics are automatically exposed at /metrics endpoint.
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# ============================================================================
# Overall Pipeline Metrics
# ============================================================================

receipt_processing_duration = Histogram(
    'receipt_processing_duration_seconds',
    'Total end-to-end receipt processing time',
    buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

receipt_processing_success_total = Counter(
    'receipt_processing_success_total',
    'Total number of successfully processed receipts'
)

receipt_processing_failed_total = Counter(
    'receipt_processing_failed_total',
    'Total number of failed receipt processing attempts',
    ['step']  # Label to track which step failed
)

receipt_processing_in_progress = Gauge(
    'receipt_processing_in_progress',
    'Number of receipts currently being processed'
)

# ============================================================================
# Per-Step Performance Metrics
# ============================================================================

receipt_step_duration = Histogram(
    'receipt_step_duration_seconds',
    'Duration of each processing step',
    ['step'],  # upload, ocr, ai, validation
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# ============================================================================
# Quality Metrics
# ============================================================================

receipt_confidence_score = Histogram(
    'receipt_confidence_score',
    'AI confidence scores for processed receipts',
    buckets=[0.0, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.99, 1.0]
)

# ============================================================================
# Cost Tracking Metrics
# ============================================================================

receipt_ai_tokens_used = Counter(
    'receipt_ai_tokens_used_total',
    'Total OpenAI tokens consumed',
    ['token_type']  # prompt, completion
)

receipt_ai_cost_estimate = Counter(
    'receipt_ai_cost_estimate_usd',
    'Estimated OpenAI API cost in USD'
)

# ============================================================================
# Additional Useful Metrics
# ============================================================================

receipt_upload_size_bytes = Histogram(
    'receipt_upload_size_bytes',
    'Size of uploaded receipt images',
    buckets=[10_000, 50_000, 100_000, 500_000, 1_000_000, 5_000_000, 10_000_000]
)

receipt_human_review_required = Counter(
    'receipt_human_review_required_total',
    'Receipts requiring human review due to low confidence'
)

receipt_verification_duration = Histogram(
    'receipt_verification_duration_seconds',
    'Time taken by users to verify receipts',
    buckets=[1, 5, 10, 30, 60, 300, 600, 1800]
)

# ============================================================================
# Service-Specific Error Metrics
# ============================================================================

# S3 Upload Errors
# Common error codes: 403 (AccessDenied), 404 (NoSuchBucket), 503 (ServiceUnavailable)
s3_upload_errors_total = Counter(
    's3_upload_errors_total',
    'S3 upload failures by error code',
    ['error_code', 'error_type']  # e.g., error_code='403', error_type='AccessDenied'
)

# Google Document AI Errors  
# Common error codes: 400 (InvalidArgument), 403 (PermissionDenied), 429 (ResourceExhausted), 500 (Internal), 503 (Unavailable)
document_ai_errors_total = Counter(
    'document_ai_errors_total',
    'Google Document AI failures by error code',
    ['error_code', 'error_type']  # e.g., error_code='429', error_type='RESOURCE_EXHAUSTED'
)

# OpenAI API Errors
# Common error codes: 400 (BadRequest), 401 (Unauthorized), 429 (RateLimitExceeded), 500 (InternalError), 503 (ServiceUnavailable)
openai_errors_total = Counter(
    'openai_errors_total',
    'OpenAI API failures by error code',
    ['error_code', 'error_type']  # e.g., error_code='429', error_type='rate_limit_exceeded'
)

# ============================================================================
# Helper Functions
# ============================================================================

def get_metrics():
    """
    Generate Prometheus metrics in the correct format.
    Returns: (content, content_type)
    """
    return generate_latest(), CONTENT_TYPE_LATEST


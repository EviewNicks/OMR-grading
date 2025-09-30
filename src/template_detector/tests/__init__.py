"""
Testing framework untuk Template Detection system

Test modules:
- test_detection: Unit tests untuk detection algorithms
- test_segmentation: Unit tests untuk segmentation pipeline
- test_integration: Integration tests untuk end-to-end pipeline
- test_performance: Performance benchmarking tests
"""

# Test configuration
TEST_DATA_PATH = "test_data/"
EXPECTED_ACCURACY_THRESHOLD = 0.85
PERFORMANCE_TIMEOUT = 30  # seconds

__all__ = [
    'TEST_DATA_PATH',
    'EXPECTED_ACCURACY_THRESHOLD',
    'PERFORMANCE_TIMEOUT'
]
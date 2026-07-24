"""Canonical image preprocessing.

Placeholder module for T-001 scaffold. The single resize/center-crop/normalize
implementation shared by training, evaluation, ONNX-export validation, and serving
lands in T-020 (see docs/ml/AUGMENTATION_STRATEGY.md §parity). Divergence between
training and serving preprocessing is the classic silent bug this package exists to
prevent; parity is test-enforced (docs/testing/ML_TESTS.md).
"""

__version__ = "0.0.0"

# Augmentation Strategy

Albumentations, training-time only. Goal: close the domain gap between Food-101
(restaurant/foodspotting photos) and our real inputs (phone photos in kitchens,
stores, mixed lighting) without damaging label validity.

## Baseline recipe (all experiments unless varied)

| Transform | Params (initial) | Rationale |
|---|---|---|
| RandomResizedCrop | scale (0.65–1.0), ratio (0.8–1.25), size per model | Framing variation; floor at 0.65 so the dish stays identifiable |
| HorizontalFlip | p=0.5 | Food is left-right symmetric in label semantics |
| Rotate | limit ±20°, p=0.5, border=reflect | Handheld tilt; beyond ~25° plates look unnatural |
| ColorJitter | brightness/contrast 0.25, saturation 0.2, hue 0.02, p=0.7 | Kitchen vs store vs daylight lighting. **Hue kept tiny** — color is a food-identity feature (see forbidden list) |
| GaussianBlur | σ up to 1.2, p=0.15 | Mild focus misses |
| GaussNoise | var 10–40, p=0.15 | Low-light sensor noise |
| ImageCompression | JPEG quality 60–95, p=0.3 | Upload/re-encode artifacts |
| CoarseDropout (occlusion) | ≤4 holes, ≤10% area each, p=0.25 | Fork/garnish/hand occlusion |
| Perspective | scale ≤0.06, p=0.2 | Off-axis phone angles |
| Normalize | ImageNet mean/std | Pretrained-weights convention; MUST match serving preprocessing exactly (ML_TESTS parity) |

## Experimental variations (EXPERIMENT_PLAN)

- **Light vs heavy policy** (E6): baseline vs stronger (RandAugment-style magnitudes).
- **MixUp** α=0.2 (E9) and **CutMix** α=1.0 (E10): regularization + calibration
  effects; evaluated with ECE, not just accuracy.
- **Test-time augmentation** (E12): center + 4-crop + flip averaging; accuracy gain
  vs latency cost on CPU — likely rejected for serving, reported anyway.

## Forbidden / constrained augmentations (label-validity guardrails)

- **VerticalFlip:** upside-down plated food is out-of-distribution and never occurs.
- **Large hue shifts / channel shuffle / ToGray:** color separates classes (e.g.,
  guacamole vs hummus, red vs white sauces). Hue limited to ±0.02.
- **Heavy elastic/grid distortion:** deforms food geometry into unrecognizability;
  textures are class evidence.
- **Extreme crops (scale <0.5):** a corner of rice tells nothing; label becomes wrong.
- **Solarize/invert/posterize at high magnitude:** unrealistic sensor behavior.
- **Rotate90/180:** same as vertical flip rationale for plated food.

Rule of thumb encoded in review: *an augmented sample must still be an image a human
would label as the same class, taken by a plausible phone camera.* A visual audit
notebook renders 64 augmented samples per policy for human review before any policy
is used in a tracked experiment.

## Serving-preprocessing parity

Val/test/serving pipeline: Resize(shorter side → S) → CenterCrop(model size) →
Normalize(ImageNet). Implemented ONCE in `packages/…/preprocessing.py`, imported by
training, evaluation, ONNX-export validation, and the API. Parity is test-enforced
(ML_TESTS: same input bytes → identical tensors, train-eval transform divergence
only via the documented augmentation list).

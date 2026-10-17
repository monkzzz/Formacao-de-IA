// Training scope stays visible; supplemental results never stand in for MNIST-only work.
export const CNN_MODELS = Object.freeze({
  mnist: {
    name: "MNIST only · course model",
    scope: "Required exercise: trained on MNIST with training-only affine and noise augmentation. No supplementary dataset.",
    data: "MNIST · 55,000 train / 5,000 validation",
  },
  "mnist-supplementary-v1": {
    name: "MNIST + supplementary data · extension",
    scope: "Optional extension: MNIST + EMNIST Digits + independently generated CAPTCHA-style examples. Keep this experiment separate from the required MNIST-only submission. EMNIST is handwriting, not collected CAPTCHA data.",
    data: "MNIST + EMNIST Digits + synthetic CAPTCHA-style examples",
  },
  "captcha-v3": {
    name: "Preserved residual CNN · MNIST + synthetic data",
    scope: "Previous default, preserved unchanged. Trained on MNIST and synthetic CAPTCHA-style examples; it is not MNIST-only.",
    data: "MNIST + independent synthetic CAPTCHA-style examples",
  },
});

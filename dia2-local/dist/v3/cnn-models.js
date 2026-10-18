// Training scope stays visible; supplemental results never stand in for MNIST-only work.
export const CNN_MODELS = Object.freeze({
  mnist: {
    name: "MNIST only · course model",
    scope: "Required exercise: trained on MNIST with training-only affine and noise augmentation. No supplementary dataset.",
    data: "MNIST · 55,000 train / 5,000 validation",
  },
  "captcha-v3": {
    name: "Preserved residual CNN · MNIST + synthetic data",
    scope: "Previous default, preserved unchanged. Trained on MNIST and synthetic CAPTCHA-style examples; it is not MNIST-only.",
    data: "MNIST + independent synthetic CAPTCHA-style examples",
  },
});

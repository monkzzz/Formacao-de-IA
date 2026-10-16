"""Small CNN with operations implemented independently in browser JavaScript."""

import torch
from torch import nn
from torch.nn import functional as F


class DigitCNN(nn.Module):
    """28×28 → conv16/pool → conv32/pool → dense128 → ten logits."""

    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.fc1 = nn.Linear(32 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)
        self.dropout = nn.Dropout(.25)

    def features(self, x):
        first = F.max_pool2d(F.relu(self.conv1(x)), 2)
        second = F.max_pool2d(F.relu(self.conv2(first)), 2)
        hidden = F.relu(self.fc1(second.flatten(1)))
        return first, second, hidden

    def forward(self, x):
        _, _, hidden = self.features(x)
        return self.fc2(self.dropout(hidden))


def augment(x):
    """Training-only affine variation and mild noise; no challenge input used."""
    n = len(x)
    angle = (torch.rand(n) * 2 - 1) * .20
    scale = .90 + torch.rand(n) * .20
    theta = torch.zeros((n, 2, 3))
    theta[:, 0, 0] = angle.cos() * scale
    theta[:, 0, 1] = -angle.sin() * scale
    theta[:, 1, 0] = angle.sin() * scale
    theta[:, 1, 1] = angle.cos() * scale
    theta[:, :, 2] = (torch.rand(n, 2) * 2 - 1) * .10
    grid = F.affine_grid(theta, x.size(), align_corners=False)
    transformed = F.grid_sample(x, grid, align_corners=False)
    return (transformed + torch.randn_like(transformed) * .025).clamp(0, 1)

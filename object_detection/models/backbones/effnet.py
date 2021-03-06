import torch.nn as nn
import torch
import torchvision
from torch import Tensor
from object_detection.entities import FP
from efficientnet_pytorch.model import EfficientNet
from typing_extensions import Literal
from typing import Any

SIDEOUT: Any = {  # phi: (stages, channels)
    0: ([0, 2, 4, 10, 15], [16, 24, 40, 112, 320]),
    1: ([1, 4, 7, 15, 22], [16, 24, 40, 112, 320]),
    2: ([1, 4, 7, 15, 22], [16, 24, 48, 120, 352]),
    3: ([1, 4, 7, 17, 25], [24, 32, 48, 136, 384]),
    4: ([1, 5, 9, 21, 31], [24, 32, 56, 160, 448]),
    5: ([2, 7, 12, 26, 38], [24, 40, 64, 176, 512]),
    6: ([2, 8, 14, 30, 44], [32, 40, 72, 200, 576]),
    7: ([3, 10, 17, 37, 54], [32, 48, 80, 224, 640]),
}

Phi = Literal[
    0, 1, 2, 3, 4, 5, 6, 7,
]


class EfficientNetBackbone(nn.Module):
    def __init__(self, phi: Phi, out_channels: int, pretrained: bool = False):
        super().__init__()
        model_name = f"efficientnet-b{phi}"
        if pretrained:
            self.module = EfficientNet.from_pretrained(model_name)
        else:
            self.module = EfficientNet.from_name(model_name)
        self._sideout_stages, self.sideout_channels = SIDEOUT[phi]
        self.projects = nn.ModuleList(
            [
                nn.Conv2d(in_channels=i, out_channels=out_channels, kernel_size=1,)
                for i in self.sideout_channels
            ]
        )

    def forward(self, x: torch.Tensor) -> FP:
        m = self.module
        x = m._swish(m._bn0(m._conv_stem(x)))
        feats = []
        for idx, block in enumerate(m._blocks):
            drop_connect_rate = m._global_params.drop_connect_rate
            if drop_connect_rate:
                drop_connect_rate *= float(idx) / len(m._blocks)
            x = block(x, drop_connect_rate=drop_connect_rate)
            if idx in self._sideout_stages:
                feats.append(x)

        p3, p4, p5, p6, p7 = feats
        return (
            self.projects[0](p3),
            self.projects[1](p4),
            self.projects[2](p5),
            self.projects[3](p6),
            self.projects[4](p7),
        )

import torch

from torch.nn.modules import Module
from torch.nn import *
import numpy as np


class AttentionLayer(Module):
    def __init__(self, channels, in_dim):
        super().__init__()
        self.atten = Parameter(torch.Tensor(np.diag([1] * in_dim)), requires_grad=True)

    def forward(self, x):
        return torch.matmul(x, self.atten)


class GCNLayer(Module):
    def __init__(self, channels, in_dim):
        super().__init__()
        adj = [
            [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1]
        ]
        self.A = Parameter(torch.Tensor(adj), requires_grad=False)
        self.W = Parameter(torch.randn(size=(in_dim, in_dim)), requires_grad=True)
        # torch.nn.init.normal_(self.W)

    def forward(self, x):
        # print(x.size(), self.attention.size())
        # res = torch.mm(self.D, self.A)
        # res = torch.mm(res, self.D)
        # res = self.A * x
        res = torch.matmul(x, self.W)
        # sf = Softmax(dim=3)
        # res = sf(res)
        # res = res.permute(0, 1, 3, 2)
        # res = torch.matmul(x, res)
        # res = ax * x
        # res = torch.matmul(x, self.W)
        return res


class IntensifyLayer(Module):
    def __init__(self, decay_rate, N):
        super(IntensifyLayer, self).__init__()
        self.decay_rate = decay_rate
        self.N = N

    def forward(self, x):
        return x + self.decay_rate * (x - 1. / self.N)


class KeyPointLearner(Module):
    """
    input 1 shape = (batch, keypoints_num, 3)
    input 1 shape = (batch, keypoints_num, keypoints_num)
    """

    def __init__(self, keypoints_num=26, intensify_num=0.3):
        super().__init__()
        self.attention = AttentionLayer(1, keypoints_num)
        self.softmax = Softmax(2)
        self.linear_intensify = [
            IntensifyLayer(decay_rate=intensify_num, N=26),
        ]

        self.linear_intensify = Sequential(*self.linear_intensify)

        self.gcn = GCNLayer(1, keypoints_num)

        self.kpm_model = [

            self.gcn,
            BatchNorm2d(1),
            # GCNLayer(1, keypoints_num),
            ReLU(),

            self.gcn,
            BatchNorm2d(1),
            # GCNLayer(1, keypoints_num),
            ReLU(),

            self.gcn,
            BatchNorm2d(1),
            # GCNLayer(1, keypoints_num),
            ReLU(),
        ]

        self.end_model = [
            # BatchNorm2d(1),
            Flatten(),
            Linear(keypoints_num, 13),
            ReLU(),
            Linear(13, 3, bias=True),
            Softmax(dim=1),
        ]

        self.end_model = Sequential(*self.end_model)

        self.kpm_model = Sequential(*self.kpm_model)

    def forward(self, kp, kpm):

        kp = self.linear_intensify(kp)

        kp = self.softmax(kp)

        res = self.kpm_model(kpm)
        res = torch.matmul(res.transpose(-2, -1), kp)

        res = self.end_model(res)
        return res


if __name__ == '__main__':
    kp = torch.randn(size=(100, 1, 26, 3))
    kpm = torch.randn(size=(100, 1, 26, 26))
    kpl = KeyPointLearner(26)
    result = kpl(kp, kpm)
    print(result.size())

import torch
import torch.nn as nn

concat_size = 512 + 256

class MLP(nn.Module):
    def __init__(self):
        super(MLP, self).__init__()

        mix_mlp = [nn.Linear(concat_size*2, 1000),
                   nn.ReLU(),
                   nn.Dropout(0.2),
                   nn.Linear(1000, 100),
                   nn.ReLU(),
                   nn.Linear(100, 1)]

        self.mlp = nn.ModuleList(mix_mlp)

    def load(self, filename=None, parameters=None):
        if filename is not None:
            parameters = torch.load(filename)
        if parameters is None:
            raise NotImplementedError("load is a filename or a list of parameters (state_dict)")

        self.load_state_dict(parameters)

    def save(self, filename):
        torch.save(self.state_dict(), filename)

    def forward(self, x):
        x1, x2 = x
        x = torch.cat([x1, x2], dim=1)

        for layer in self.mlp:
            x = layer(x)

        return torch.sigmoid(x)

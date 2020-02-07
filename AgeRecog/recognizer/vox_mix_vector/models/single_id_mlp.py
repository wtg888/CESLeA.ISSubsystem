import torch
import torch.nn as nn

vector_size = 512 + 400
num_class = 5994

class MLP(nn.Module):
    def __init__(self):
        super(MLP, self).__init__()

        mix_mlp = [nn.Linear(vector_size, 1000),
                   nn.ReLU(),
                   nn.Dropout(0.1),
                   nn.Linear(1000, 1000),
                   nn.ReLU()]

        classifier = [nn.Dropout(0.1),
                      nn.Linear(1000, 5994)]

        self.mlp = nn.ModuleList(mix_mlp)
        self.classifier = nn.ModuleList(classifier)

    def load(self, filename=None, parameters=None):
        if filename is not None:
            parameters = torch.load(filename)
        if parameters is None:
            raise NotImplementedError("load is a filename or a list of parameters (state_dict)")

        self.load_state_dict(parameters)

    def save(self, filename):
        torch.save(self.state_dict(), filename)

    def forward(self, x, return_vector=False):
        x = x.unsqueeze(dim=1)
        for layer in self.mlp:
            x = layer(x)
        new_vector = x.squeeze(dim=1)
        for layer in self.classifier:
            x = layer(x)

        x = x.squeeze(dim=1)
        if return_vector:
            return torch.sigmoid(x), torch.sigmoid(new_vector)
        else:
            return torch.sigmoid(x)

import os
import time
import numpy as np

import torch
from torch import nn

os.environ["CUDA_VISIBLE_DEVICES"] = "1"
from models.simple_mlp import MLP as model

from inputs.id_input import TrainGenerator, ValidGenerator, TestGenerator
from torch.utils.tensorboard import SummaryWriter

from scipy.optimize import brentq
from sklearn.metrics import roc_curve
from scipy.interpolate import interp1d


n_epoch = 1000


def calculate_eer(y, y_score, pos):

    fpr, tpr, thresholds = roc_curve(y, y_score, pos_label=pos)
    eer = brentq(lambda x : 1. - x - interp1d(fpr, tpr)(x), 0., 1.)
    thresh = interp1d(fpr, thresholds)(eer)

    return eer, thresh


def create_folder(fd):
    if not os.path.exists(fd):
        os.makedirs(fd)


def train(generator, model, optimizer, epoch, summary):
    mse = nn.MSELoss()

    last_step = 10000*epoch

    start = time.time()
    for i in range(1000):
        step = last_step+i
        batch1, batch2, target = generator.get_batch(128)
        # print(batch1.shape)

        batch1 = torch.tensor(batch1, dtype=torch.float32).cuda()
        batch2 = torch.tensor(batch2, dtype=torch.float32).cuda()
        target = torch.tensor(target, dtype=torch.float32).cuda()

        pred = model([batch1, batch2])
        inv_pred = model([batch2, batch1])
        if len(pred.shape)==2:
            pred = pred.squeeze(dim=1)

        loss = mse(pred, target)
        inv_loss = mse(inv_pred, target)
        if i%100==0:
            summary.add_scalar('loss', loss.item(), step)

        consistency = mse(loss, inv_loss)
        loss += consistency
        if i%100==0:
            summary.add_scalar('consistency', loss.item(), step)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    epoch_time = time.time() - start
    print("epoch: %d, time: %.2f, loss:%.4f" % (epoch, epoch_time, loss))


def eval(generator, model, summary, batch_size=8):
    batch1, batch2, target = generator.get_all()
    eval_len = len(target)

    total_pred = []
    for i in range(eval_len//batch_size):
        temp_batch1 = torch.tensor(batch1[i*batch_size:(i+1)*batch_size], dtype=torch.float32).cuda()
        temp_batch2 = torch.tensor(batch2[i*batch_size:(i+1)*batch_size], dtype=torch.float32).cuda()
        total_pred.append(model([temp_batch1, temp_batch2]).detach().cpu())
    total_pred = np.reshape(np.concatenate(total_pred, axis=0), [-1])
    eer, thresh = calculate_eer(target, total_pred, 1)
    print(eer)

    return eer


if __name__ == '__main__':
    store_dir = os.path.join("stored_data", "mlp_consistency")
    saved_model_dir = os.path.join(store_dir, "model")
    saved_pred_dir = os.path.join(store_dir, "predictions")
    create_folder(store_dir)
    create_folder(saved_model_dir)
    create_folder(saved_pred_dir)
    summary = SummaryWriter(os.path.join(store_dir, "summary"))

    model = model()
    num_gpu = torch.cuda.device_count()
    model = model.cuda()

    print(model)
    trainable_params = 0
    for param in filter(lambda p: p.requires_grad, model.parameters()):
        trainable_params += int(param.view(-1).shape[0])
    print("trainable parameters: %.2fM" % (trainable_params/1e6))

    # ##############
    # Train
    # ##############
    optim_kwargs = {"lr": 0.0001, "betas": (0.9, 0.999)}
    optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), **optim_kwargs)


    state = {
        'model': {"name": model.__class__.__name__,
                  'args': '',
                  'state_dict': model.state_dict()},
        'optimizer': {"name": optimizer.__class__.__name__,
                      'args': '',
                      "kwargs": optim_kwargs,
                      'state_dict': optimizer.state_dict()},
    }

    train_generator = TrainGenerator()
    test_generator = ValidGenerator()

    min_eer = 1.

    for epoch in range(n_epoch):
        model = model.train()
        train(train_generator, model, optimizer, epoch, summary)

        model = model.eval()
        eer = eval(test_generator, model, summary)

        # if cfg.checkpoint_epochs is not None and (epoch + 1) % cfg.checkpoint_epochs == 0:
        if eer<min_eer:
            min_eer = eer
            model_fname = os.path.join(saved_model_dir, "best")
            torch.save(state, model_fname)
            print("Saving this model: {}".format(model_fname))

    print('best eer: ', min_eer)

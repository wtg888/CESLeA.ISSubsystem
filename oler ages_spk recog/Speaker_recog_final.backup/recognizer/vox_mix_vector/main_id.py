import os
import time
import numpy as np

import torch
from torch import nn

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
from models.single_id_mlp import MLP

from inputs.single_id_input import TrainGenerator, ValidGenerator, TestGenerator
from torch.utils.tensorboard import SummaryWriter

from scipy.optimize import brentq
from sklearn.metrics import roc_curve
from scipy.interpolate import interp1d


n_epoch = 200


def calculate_eer(y, y_score, pos):

    fpr, tpr, thresholds = roc_curve(y, y_score, pos_label=pos)
    eer = brentq(lambda x : 1. - x - interp1d(fpr, tpr)(x), 0., 1.)
    thresh = interp1d(fpr, thresholds)(eer)

    return eer, thresh


def create_folder(fd):
    if not os.path.exists(fd):
        os.makedirs(fd)

'''
class AMS(nn.Module):
    def __init__(self, in_featurs, out_features, params):
        r = 6./(float(in_featurs+out_features))
        self.w = nn.Parameter(torch.tensor(np.random.uniform(-r, r, [in_featurs, out_features]))).cuda()

        self.softmax = nn.Softmax(dim=1)

    def forward(self, features, labels, num_outputs):
        # w_norm = tf.nn.l2_normalize(w, dim=0)
        # logits = tf.matmul(features, w_norm)
        w_norm = self.w.norm(dim=0, keepdim=True)
        logits = features.matmul(w_norm)

        # ordinal = tf.to_int32(tf.range(shape_list(features)[0]))
        # ordinal_labels = tf.stack([ordinal, labels], axis=1)
        # sel_logits = tf.gather_nd(logits, ordinal_labels)
        ordinal = torch.range(0, features.shape[0])
        labels = labels.argmax(axis=1)
        ordinal_labels = torch.stack([ordinal, labels], dim=1)
        sel_logits = torch.gather(logits, ordinal_labels)

        # The angle between x and the target w_i.
        eps = 1e-12
        # features_norm = tf.maximum(tf.norm(features, axis=1), eps)
        # cos_theta_i = tf.div(sel_logits, features_norm)
        # cos_theta_i = tf.clip_by_value(cos_theta_i, -1 + eps, 1 - eps)  # for numerical steady
        # phi_i = cos_theta_i - params.amsoftmax_m

        features_norm = torch.relu(features.norm(dim=0, keepdim=True)+eps)
        cos_theta_i = torch.div(sel_logits, features_norm)
        cos_theta_i = torch.clamp(cos_theta_i, -1+eps, 1-eps)
        phi_i = cos_theta_i - AMS_M


        # logits = ||x||(cos(theta) - m)
        # scaled_logits = tf.multiply(phi_i, features_norm)
        scaled_logits = torch.mul(phi_i, features_norm)

        # logits_amsoftmax = tf.add(logits,
        #                           tf.scatter_nd(ordinal_labels,
        #                                         tf.subtract(scaled_logits, sel_logits),
        #                                         tf.shape(logits, out_type=tf.int32)))
        logits_amsoftmax = torch.add(logits,
                                     torch.scatter(1,
                                                   ordinal_labels,
                                                   torch.sub(scaled_logits, sel_logits)))

        # amsoftmax_lambda = tf.maximum(params.amsoftmax_lambda_min,
        #                               params.amsoftmax_lambda_base * (
        #                                       1.0 + params.amsoftmax_lambda_gamma * tf.to_float(
        #                                   params.global_step)) ** (-params.amsoftmax_lambda_power))
        amsoftmax_lambda = torch.max(params.amsoftmax_lambda_min,
                                      params.amsoftmax_lambda_base *
                                     (1.0 + params.amsoftmax_lambda_gamma * params.global_step) **
                                     (-params.amsoftmax_lambda_power))
        fa = 1.0 / (1.0 + amsoftmax_lambda)
        fs = 1.0 - fa
        updated_logits = fs * logits + fa * logits_amsoftmax


        # loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=updated_logits)

        return self.softmax()
'''

def train(generator, model, optimizer, epoch, summary):
    mse = nn.MSELoss()
    bce = nn.BCELoss()

    last_step = 10000*epoch

    start = time.time()
    for i in range(1000):
        step = last_step+i
        batch, target = generator.get_batch(128)
        # print(batch.shape)

        batch = torch.tensor(batch, dtype=torch.float32).cuda()
        target = torch.tensor(target, dtype=torch.float32).cuda()

        pred = model(batch)
        if len(pred.shape)==2:
            pred = pred.squeeze(dim=1)

        loss = bce(pred, target)
        if i%100==0:
            summary.add_scalar('loss', loss.item(), step)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    epoch_time = time.time() - start
    print("epoch: %d, time: %.2f, loss:%f" % (epoch, epoch_time, loss))


def valid(generator, model, summary, batch_size=128):
    batch, target = generator.get_all()
    eval_len = len(target)

    total_pred = []
    for i in range(eval_len//batch_size+1):
        temp_batch = torch.tensor(batch[i*batch_size:(i+1)*batch_size], dtype=torch.float32).cuda()
        total_pred.append(model(temp_batch).detach().cpu())

    total_pred = np.concatenate(total_pred, axis=0)
    total_pred = np.argmax(total_pred, axis=1)
    target = np.argmax(target, axis=1)

    acc = np.array(total_pred==target, dtype=np.float32)
    acc = np.mean(acc)
    # print(acc)

    eer, thresh = calculate_eer(target, total_pred, 1)
    # print(eer)

    return acc


def eval(generator, model, summary, batch_size=128):
    batch1, batch2, target = generator.get_all()
    eval_len = len(target)
    sim = nn.CosineSimilarity(dim=1)

    total_pred = []
    x_pred = []
    i_pred = []
    mix_pred = []
    for i in range(eval_len//batch_size+1):
        temp_batch1 = torch.tensor(batch1[i*batch_size:(i+1)*batch_size], dtype=torch.float32).cuda()
        temp_batch2 = torch.tensor(batch2[i*batch_size:(i+1)*batch_size], dtype=torch.float32).cuda()

        pred1, vector1 = model(temp_batch1, return_vector=True)
        pred2, vector2 = model(temp_batch2, return_vector=True)

        total_pred.append(sim(vector1, vector2).detach().cpu())
        x_pred.append(sim(temp_batch1[:, 0:512], temp_batch2[:, 0:512]).detach().cpu())
        i_pred.append(sim(temp_batch1[:, 512:], temp_batch2[:, 512:]).detach().cpu())
        mix_pred.append(sim(temp_batch1, temp_batch2).detach().cpu())

        # total_pred.append(sim(temp_batch1, temp_batch2).detach().cpu())
        # print(total_pred[-1])
    total_pred = np.concatenate(total_pred, axis=0)
    eer, thresh = calculate_eer(target, total_pred, 1)

    x_pred = np.concatenate(x_pred, axis=0)
    x_eer, x_thres = calculate_eer(target, x_pred, 1)
    # print(d_eer)
    #
    i_pred = np.concatenate(i_pred, axis=0)
    i_eer, i_thres = calculate_eer(target, i_pred, 1)
    # print(i_eer)
    #
    mix_pred = np.concatenate(mix_pred, axis=0)
    mix_eer, mix_thres = calculate_eer(target, mix_pred, 1)
    # print(mix_eer)
    #
    print('model eer: %.4f, ivector eer: %.4f, xvector eer: %.4f, mix_eer: %.4f' %(eer, i_eer, x_eer, mix_eer))
    return eer


if __name__ == '__main__':
    store_dir = os.path.join("stored_data", "cnn")
    saved_model_dir = os.path.join(store_dir, "model")
    saved_pred_dir = os.path.join(store_dir, "predictions")
    model_fname = os.path.join(saved_model_dir, "best")
    create_folder(store_dir)
    create_folder(saved_model_dir)
    create_folder(saved_pred_dir)
    summary = SummaryWriter(os.path.join(store_dir, "summary"))

    model = MLP()
    num_gpu = torch.cuda.device_count()
    model = model.cuda()

    print(model)
    trainable_params = 0
    for param in filter(lambda p: p.requires_grad, model.parameters()):
        trainable_params += int(param.view(-1).shape[0])
    print("trainable parameters: %.2fM" % (trainable_params/1e6))

    optim_kwargs = {"lr": 0.0001, "betas": (0.9, 0.999)}
    optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), **optim_kwargs)

    state = {
        'model': {"name": model.__class__.__name__,
                  'args': '',
                  'state_dict': model.state_dict()},
    }

    train_generator = TrainGenerator()
    valid_generator = ValidGenerator()
    test_generator = TestGenerator()

    best_acc = 0.

    for epoch in range(1, n_epoch+1):
        model = model.train()
        train(train_generator, model, optimizer, epoch, summary)

        model = model.eval()
        acc = eval(valid_generator, model, summary)

        if acc>best_acc:
            best_acc = acc
            # torch.save(state, model_fname)
            model.save(model_fname)
            print("Saving this model: {}".format(model_fname))

        if epoch%10 == 0:
            model = model.eval()
            eer = eval(test_generator, model, summary)


    model = MLP()
    num_gpu = torch.cuda.device_count()
    model = model.cuda()
    # model.load(model_fname)
    model = model.eval()
    eer = eval(test_generator, model, summary)

    print('best id classification acc: ', best_acc)
    print('eer: ', eer)

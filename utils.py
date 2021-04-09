import json
import os
import torch
import numpy as np
import torch.nn as nn
from torch.utils import data
from torch.utils.tensorboard import SummaryWriter

def load_params(configs, file_name):
    current_path = os.path.dirname(os.path.abspath(__file__))
    ''' replay_name from flags.replay_name '''
    with open(os.path.join(current_path, 'grad_data', '{}.json'.format(file_name)), 'r') as fp:
        configs = json.load(fp)
    return configs


def save_params(configs, time_data):
    current_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_path, 'grad_data', '{}.json'.format(time_data)), 'w') as fp:
        json.dump(configs, fp, indent=2)

def load_model(model,file_path,file_name):
    model.load_state_dict(torch.load(os.path.join(file_path,'grad_data','checkpoint_'+file_name+'.pt')))
    return model

class EarlyStopping:
    """주어진 patience 이후로 train loss가 개선되지 않으면 학습을 조기 중지"""

    def __init__(self, file_path,time_data,config,patience=7, verbose=False, delta=0,):
        """
        Args:
            patience (int): train loss가 개선된 후 기다리는 기간
                            Default: 7
            verbose (bool): True일 경우 각 train loss의 개선 사항 메세지 출력
                            Default: False
            delta (float): 개선되었다고 인정되는 monitered quantity의 최소 변화
                            Default: 0
            path (str): checkpoint저장 경로
                            Default: 'checkpoint.pt'
        """
        self.config=config
        self.patience = patience
        self.verbose = verbose
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.val_loss_min = np.Inf
        self.delta = delta
        self.path = os.path.join(file_path,'grad_data','checkpoint_{}.pt'.format(time_data))

    def __call__(self, val_loss, model):

        score = val_loss

        if self.best_score is None:
            self.best_score = score
        elif score > self.best_score + self.delta:

            self.counter += 1
            if self.config['nn_type']!='vgg16' and self.config['nn_type']!='resnet20':
                print(
                    f'EarlyStopping counter: {self.counter} out of {self.patience}')
                if self.counter >= self.patience:
                    self.early_stop = True
            print(
                f'Eval loss not decreased ({self.val_loss_min:.6f} --> {val_loss:.6f}).')
        else:
            self.best_score = score
            self.save_checkpoint(val_loss,model)
            self.counter = 0
            
    def save_checkpoint(self, val_loss, model):
        '''validation loss가 감소하면 모델을 저장한다.'''
        if self.verbose:
            print(
                f'Eval loss decreased ({self.val_loss_min:.6f} --> {val_loss:.6f}).  Saving model ...')
        torch.save(model.state_dict(), self.path)
        self.val_loss_min = val_loss

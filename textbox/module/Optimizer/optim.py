# @Time   : 2020/11/14
# @Author : Junyi Li
# @Email  : lijunyi@ruc.edu.cn

r"""
Optimizer
#####################
"""

import numpy as np


class ScheduledOptim():
    r"""A simple wrapper class for learning rate scheduling
    """

    def __init__(self, optimizer, init_lr, d_model, n_warmup_steps):
        self._optimizer = optimizer
        self.init_lr = init_lr
        self.d_model = d_model
        self.n_warmup_steps = n_warmup_steps
        self.n_steps = 0

    def step(self):
        self._update_learning_rate()
        self._optimizer.step()

    def zero_grad(self):
        self._optimizer.zero_grad()

    def state_dict(self):
        return self._optimizer.state_dict()

    def _get_lr_scale(self):
        d_model = self.d_model
        n_steps, n_warmup_steps = self.n_steps, self.n_warmup_steps
        return (d_model ** -0.5) * min(n_steps ** (-0.5), n_steps * n_warmup_steps ** (-1.5))

    def _update_learning_rate(self):
        r"""Learning rate scheduling per step"""
        self.n_steps += 1
        lr = self.init_lr * self._get_lr_scale()

        for param_group in self._optimizer.param_groups:
            param_group['lr'] = lr


class InverseSquareRootOptim():
    r"""A simple wrapper class for learning rate scheduling
    """

    def __init__(self, optimizer, lr, init_lr, n_warmup_steps):
        self._optimizer = optimizer
        self.lr = lr
        self.init_lr = init_lr
        self.n_warmup_steps = n_warmup_steps
        self.warmup_lr_step = (lr - init_lr) / n_warmup_steps
        self.decay_factor = self.lr * self.n_warmup_steps ** 0.5
        self.n_steps = 0

    def zero_grad(self):
        self._optimizer.zero_grad()

    def state_dict(self):
        return (self._optimizer.state_dict(), self.n_steps)

    def load_state_dict(self, state_dict):
        opt, self.n_steps = state_dict
        self._optimizer.load_state_dict(opt)

    def step(self):
        self._update_learning_rate()
        self._optimizer.step()

    def _get_lr(self):
        self.n_steps += 1
        if self.n_steps <= self.n_warmup_steps:
            return self.init_lr + self.n_steps * self.warmup_lr_step
        return self.decay_factor * self.n_steps ** -0.5

    def _update_learning_rate(self):
        r"""Learning rate scheduling per step"""
        lr = self._get_lr()

        for param_group in self._optimizer.param_groups:
            param_group['lr'] = lr

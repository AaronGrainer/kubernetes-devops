import random

import numpy as np
import torch
import torch.backends.cudnn as cudnn


def set_seed(seed):
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    cudnn.deterministic = True
    cudnn.benchmark = False

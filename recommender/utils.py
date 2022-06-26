import random
import shutil
from pathlib import Path

import pandas as pd
import torch
from torch.nn import functional as F

from common import config


def mask_list(l1, p=0.8):
    l1 = [a if random.random() < p else config.MASK for a in l1]
    return l1


def mask_last_elements_list(l1, val_context_size: int = config.VAL_CONTEXT_SIZE):
    l1 = l1[:-val_context_size] + mask_list(l1[-val_context_size:], p=config.MASK_PROBABILITY)
    return l1


def map_column(df: pd.DataFrame, col_name: str):
    """Maps column values to integers

    Args:
        df (pd.DataFrame): _description_
        col_name (str): _description_
    """
    values = sorted(list(df[col_name].unique()))
    mapping = {k: i + 2 for i, k in enumerate(values)}
    inverse_mapping = {v: k for k, v in mapping.items()}

    df[col_name + "_mapped"] = df[col_name].map(mapping)

    return df, mapping, inverse_mapping


def get_context(
    df: pd.DataFrame,
    split: str,
    context_size: int = config.DEFAULT_CONTEXT_SIZE,
    val_context_size: str = config.VAL_CONTEXT_SIZE,
):
    """Create a training / validation samples

    Validation samples are the last horizon_size rows

    Args:
        df (pd.DataFrame): Data
        split (str): train | val | test
        context_size (int, optional): Size of the context. Defaults to config.DEFAULT_CONTEXT_SIZE.
        val_context_size (str, optional): Validation context size. Defaults to config.VAL_CONTEXT_SIZE.
    """
    if split == "train":
        end_index = random.randint(10, df.shape[0] - val_context_size)
    elif split in ["val", "test"]:
        end_index = df.shape[0]
    else:
        raise ValueError

    start_index = max(0, end_index - context_size)

    context = df[start_index:end_index]

    return context


def pad_list(list_integers, history_size: int, pad_val: int = config.PAD, mode: str = "left"):
    """List to pad

    Args:
        list_integers (_type_): _description_
        history_size (int): _description_
        pad_val (int, optional): _description_. Defaults to config.PAD.
        mode (str, optional): _description_. Defaults to "left".
    """
    if len(list_integers) < history_size:
        if mode == "left":
            list_integers = [pad_val] * (history_size - len(list_integers)) + list_integers
        else:
            list_integers = list_integers + [pad_val] * (history_size - len(list_integers))

    return list_integers


def masked_accuracy(y_pred: torch.Tensor, y_true: torch.Tensor, mask: torch.Tensor):
    _, predicted = torch.max(y_pred, 1)

    y_true = torch.masked_select(y_true, mask)
    predicted = torch.masked_select(predicted, mask)

    accuracy = (y_true == predicted).double().mean()

    return accuracy


def masked_ce(y_pred, y_true, mask):
    loss = F.cross_entropy(y_pred, y_true, reduction="none")
    loss = loss * mask
    return loss.sum() / (mask.sum() + 1.0e-8)


def cleanup():
    checkpoint_path = Path(config.MODEL_DIR, "checkpoints")
    shutil.rmtree(checkpoint_path)

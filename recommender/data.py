import random

import torch

from common import config
from recommender.utils import (
    get_context,
    mask_last_elements_list,
    mask_list,
    pad_list,
)


class Dataset(torch.utils.data.Dataset):
    def __init__(self, groups, group_by, split, history_size=config.HISTORY_SIZE):
        self.groups = groups
        self.group_by = group_by
        self.split = split
        self.history_size = history_size

    def __len__(self):
        return len(self.groups)

    def __getitem__(self, idx):
        group = self.groups[idx]

        df = self.group_by.get_group(group)

        context = get_context(df, split=self.split)

        target_items = context["movieId_mapped"].tolist()

        if self.split == "train":
            source_items = mask_list(target_items)
        else:
            source_items = mask_last_elements_list(target_items)

        pad_mode = "left" if random.random() < 0.5 else "right"
        source_items = pad_list(source_items, history_size=self.history_size, mode=pad_mode)
        target_items = pad_list(target_items, history_size=self.history_size, mode=pad_mode)

        source_items = torch.tensor(source_items, dtype=torch.long)
        target_items = torch.tensor(target_items, dtype=torch.long)

        return source_items, target_items

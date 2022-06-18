import json
import zipfile

import torch
import wget
from mlflow.tracking import MlflowClient

from common.config import logger


def download(url, savepath):
    wget.download(url, str(savepath))


def unzip(zippath, savepath):
    zip = zipfile.ZipFile(zippath)
    zip.extractall(savepath)
    zip.close()


def recalls_and_ndcgs_for_ks(scores, labels, ks):
    metrics = {}

    scores = scores
    labels = labels
    answer_count = labels.sum(1)

    labels_float = labels.float()
    rank = (-scores).argsort(dim=1)
    cut = rank
    for k in sorted(ks, reverse=True):
        cut = cut[:, :k]
        hits = labels_float.gather(1, cut)
        metrics[f"Recall_{k}"] = (
            (hits.sum(1) / torch.min(torch.Tensor([k]).to(labels.device), labels.sum(1).float()))
            .mean()
            .cpu()
            .item()
        )

        position = torch.arange(2, 2 + k)
        weights = 1 / torch.log2(position.float())
        dcg = (hits * weights.to(hits.device)).sum(1)
        idcg = torch.Tensor([weights[: min(int(n), k)].sum() for n in answer_count]).to(dcg.device)
        ndcg = (dcg / idcg).mean()
        metrics[f"NDCG_{k}"] = ndcg.cpu().item()

    return metrics


def print_auto_logged_info(r):
    tags = {k: v for k, v in r.data.tags.items() if not k.startswith("mlflow.")}
    artifacts = [f.path for f in MlflowClient().list_artifacts(r.info.run_id, "model")]
    logger.info(f"run_id: {r.info.run_id}")
    logger.info(f"artifacts: {artifacts}")
    logger.info(f"params: {json.dumps(r.data.params, indent=2)}")
    logger.info(f"metrics: {json.dumps(r.data.metrics, indent=2)}")
    logger.info(f"tags: {json.dumps(tags, indent=2)}")

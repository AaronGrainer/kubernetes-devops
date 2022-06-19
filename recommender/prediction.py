from pathlib import Path
from typing import List

import torch

import mlflow
from common import config


def predict_bert(input: List):
    # run_id = open(Path(config.MODEL_DIR, "intent_run_id.txt")).read()
    run_id = "0972ddc1bb304be5a65ec2272825719a"
    model_uri = f"runs:/{run_id}/model"

    loaded_model = mlflow.pytorch.load_model(model_uri)
    device = torch.device("cpu")
    loaded_model.to(device)

    with torch.no_grad():
        logits = loaded_model(input)
        print("logits: ", logits, len(logits), len(logits[0]), len(logits[0][0]))

        # logits = logits.view(-1, logits.size(-1))  # (B * T) x V
        # print('logits: ', logits, len(logits), len(logits[0]))
        # pred = torch.argmax(logits)
        # print('pred: ', pred)
        logits = logits[:, -1, :]  # B x V
        print("logits: ", logits, len(logits), len(logits[0]))
        pred = torch.argmax(logits, dim=0)
        print("pred: ", pred)

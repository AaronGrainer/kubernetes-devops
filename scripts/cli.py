import json
import random
from pathlib import Path

import pandas as pd
import torch
import typer

from common import config
from recommender2 import prediction, trainer
from recommender.datasets.data import ML1MDataset
from recommender.datasets.dataloader import BertDataModule, BertTrainDataset
from recommender.model.model import Bert4RecModel
from recommender.prediction import predict_bert
from recommender.trainer import train_model

app = typer.Typer()


# Directories
BASE_DIR = Path(__file__).parent.parent.absolute()
ORDERS_FILEPATH = Path(BASE_DIR, "data", "orders.csv")
CUSTOMERS_FILEPATH = Path(BASE_DIR, "data", "train_customers.csv")
FULL_FILEPATH = Path(BASE_DIR, "data", "train_full.csv")
LOCATIONS_FILEPATH = Path(BASE_DIR, "data", "train_locations.csv")
VENDORS_FILEPATH = Path(BASE_DIR, "data", "vendors.csv")


@app.command()
def restaurent_eda():
    orders_pd = pd.read_csv(ORDERS_FILEPATH)
    print("orders_pd: ", orders_pd.head())

    customers_pd = pd.read_csv(CUSTOMERS_FILEPATH)
    print("customers_pd: ", customers_pd.head())

    full_pd = pd.read_csv(FULL_FILEPATH)
    print("full_pd: ", full_pd.head())

    locations_pd = pd.read_csv(LOCATIONS_FILEPATH)
    print("locations_pd: ", locations_pd.head())

    vendors_pd = pd.read_csv(VENDORS_FILEPATH)
    print("vendors_pd: ", vendors_pd.head())


@app.command()
def train():
    # train_model()
    trainer.train()


@app.command()
def predict():
    # input = torch.zeros(100, 1, dtype=torch.int64)
    # predict_bert(input)

    list_movies = [
        "Harry Potter and the Sorcerer's Stone (a.k.a. Harry Potter and the Philosopher's Stone) (2001)",
        "Harry Potter and the Chamber of Secrets (2002)",
        "Harry Potter and the Prisoner of Azkaban (2004)",
        "Harry Potter and the Goblet of Fire (2005)",
    ]
    top_movie = prediction.predict(list_movies)
    print("top_movie: ", top_movie)

    # list_movies = [
    #     "Black Panther (2017)",
    #     "Avengers, The (2012)",
    #     "Avengers: Infinity War - Part I (2018)",
    #     "Logan (2017)",
    #     "Spider-Man (2002)",
    #     "Spider-Man 3 (2007)",
    #     "Spider-Man: Far from Home (2019)"
    # ]
    # top_movie = prediction.predict(list_movies)
    # print('top_movie: ', top_movie)

    # list_movies = [
    #     "Zootopia (2016)",
    #     "Toy Story 3 (2010)",
    #     "Toy Story 4 (2019)",
    #     "Finding Nemo (2003)",
    #     "Ratatouille (2007)",
    #     "The Lego Movie (2014)",
    #     "Ghostbusters (a.k.a. Ghost Busters) (1984)",
    #     "Ace Ventura: When Nature Calls (1995)"
    # ]
    # top_movie = prediction.predict(list_movies)
    # print('top_movie: ', top_movie)


@app.command()
def main():
    model = Bert4RecModel()
    batch = [torch.zeros(128, 100, dtype=torch.int64), torch.zeros(128, 100, dtype=torch.int64)]
    seqs, labels = batch
    output = model(seqs)
    print("output: ", output)

    ml1m_dataset = ML1MDataset()
    dataset = ml1m_dataset.load_dataset()

    smap = dataset["smap"]
    item_count = len(smap)
    CLOZE_MASK_TOKEN = item_count + 1
    rng = random.Random(config.DATALOADER_RANDOM_SEED)
    bert_train_dataset = BertTrainDataset(
        dataset["train"],
        config.BERT_MAX_LEN,
        config.BERT_MASK_PROB,
        CLOZE_MASK_TOKEN,
        item_count,
        rng,
    )
    train_bert_dataloader = torch.utils.data.DataLoader(bert_train_dataset, batch_size=2)
    for x, y in train_bert_dataloader:
        print("x: ", x)
        print("y: ", y)
        break

    bert_data_module = BertDataModule()
    print("bert_data_module: ", bert_data_module)
    train_dataloader = bert_data_module.train_dataloader()
    val_dataloader = bert_data_module.val_dataloader()
    test_dataloader = bert_data_module.test_dataloader()

    # print("Train Dataloader")
    # for x, y in train_dataloader:
    #     print("x: ", x)
    #     print("y: ", y)
    #     break

    print("Val Dataloader")
    for x, y, z in val_dataloader:
        # print("x: ", x)
        # print("y: ", y)
        # print("z: ", z)

        with open("val_x.json", "w") as f:
            print("json.dumps(x.tolist()): ", json.dumps(x.tolist()))
            f.write(json.dumps(x.tolist(), indent=2))
        with open("val_y.json", "w") as f:
            f.write(json.dumps(y.tolist(), indent=2))
        with open("val_z.json", "w") as f:
            f.write(json.dumps(z.tolist(), indent=2))

        break

    with open("train.json", "w") as f:
        f.write(json.dumps(dataset["train"], indent=2))
    with open("val.json", "w") as f:
        f.write(json.dumps(dataset["val"], indent=2))
    with open("test.json", "w") as f:
        f.write(json.dumps(dataset["test"], indent=2))
    with open("smap.json", "w") as f:
        f.write(json.dumps(dataset["smap"], indent=2))
    with open("umap.json", "w") as f:
        f.write(json.dumps(dataset["umap"], indent=2))

    # print("Test Dataloader")
    # for x, y, z in test_dataloader:
    #     print("x: ", x)
    #     print("y: ", y)
    #     print("z: ", z)
    #     break


if __name__ == "__main__":
    app()

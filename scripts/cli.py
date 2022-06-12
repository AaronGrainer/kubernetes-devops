from pathlib import Path

import pandas as pd
import torch
import typer

from recommender.model.model import Bert4RecModel

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
    model = Bert4RecModel()
    batch = [torch.zeros(128, 100, dtype=torch.int64), torch.zeros(128, 100, dtype=torch.int64)]
    seqs, labels = batch
    output = model(seqs)
    print("output: ", output)


if __name__ == "__main__":
    app()
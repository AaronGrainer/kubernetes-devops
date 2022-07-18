import pandas as pd
import requests
import typer

from backend.utils import constant

# from recommender import prediction, trainer
from backend.utils.database import db_insert_documents
from common import config

app = typer.Typer()


# @app.command()
# def predict():
#     list_movies = [
#         "Harry Potter and the Sorcerer's Stone (a.k.a. Harry Potter and the Philosopher's Stone) (2001)",
#         "Harry Potter and the Chamber of Secrets (2002)",
#         "Harry Potter and the Prisoner of Azkaban (2004)",
#         "Harry Potter and the Goblet of Fire (2005)",
#     ]
#     top_movie = prediction.predict(list_movies)
#     print("top_movie: ", top_movie)

#     list_movies = [
#         "Black Panther (2017)",
#         "Avengers, The (2012)",
#         "Avengers: Infinity War - Part I (2018)",
#         "Logan (2017)",
#         "Spider-Man (2002)",
#         "Spider-Man 3 (2007)",
#         "Spider-Man: Far from Home (2019)"
#     ]
#     top_movie = prediction.predict(list_movies)
#     print('top_movie: ', top_movie)

#     list_movies = [
#         "Zootopia (2016)",
#         "Toy Story 3 (2010)",
#         "Toy Story 4 (2019)",
#         "Finding Nemo (2003)",
#         "Ratatouille (2007)",
#         "The Lego Movie (2014)",
#         "Ghostbusters (a.k.a. Ghost Busters) (1984)",
#         "Ace Ventura: When Nature Calls (1995)"
#     ]
#     top_movie = prediction.predict(list_movies)
#     print('top_movie: ', top_movie)


@app.command()
def predict_request():
    list_movies = [
        "Harry Potter and the Sorcerer's Stone (a.k.a. Harry Potter and the Philosopher's Stone) (2001)",
        "Harry Potter and the Chamber of Secrets (2002)",
        "Harry Potter and the Prisoner of Azkaban (2004)",
        "Harry Potter and the Goblet of Fire (2005)",
    ]
    data = {"user_movies": list_movies}
    response = requests.post("http://localhost:4000/recommend", json=data)
    print("response: ", response.status_code, response.json())


@app.command()
def upload_new_movie_list():

    data = pd.read_csv(config.MOVIELENS_RATING_DATA_DIR)
    data = data.head(100000)
    data.sort_values(by="timestamp", inplace=True)
    print("data: ", data)

    import time

    time.sleep(10)

    # db_insert_documents(constant.recommender, documents)


if __name__ == "__main__":
    app()

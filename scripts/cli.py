import pandas as pd
import requests
import typer
import wikipedia

# from recommender import prediction
from common import config, constant, database
from common.config import logger

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
def upload_recommender_dataset():
    logger.info("Inserting MovieLens dataset into Dataset")

    ratings = pd.read_csv(config.MOVIELENS_RATING_DATA_DIR)
    movies = pd.read_csv(config.MOVIELENS_MOVIE_DATA_DIR)

    ratings = ratings.head(100000)
    ratings.sort_values(by="timestamp", inplace=True)

    ratings, mapping, _ = map_column(ratings, col_name="movieId")
    ratings["timestamp"] = pd.to_datetime(ratings["timestamp"])

    ratings_dict = ratings.to_dict("records")
    logger.info(f"Inserting {len(ratings_dict)} rating documents")
    database.db_insert_documents(constant.RATING, ratings_dict)

    movies_dict = movies.to_dict("records")
    logger.info(f"Inserting {len(movies_dict)} movies documents")
    database.db_insert_documents(constant.MOVIE, movies_dict)

    logger.info("Successfully inserted the MovieLens dataset")


####################
# Utility Functions
####################


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


@app.command()
def create_mongo_field_index():
    """Create field index in mongo collection"""
    collection = database.get_mongo_collection("movie")
    collection.create_index([("title", "text")])


@app.command()
def call_wikipedia():
    """Call wikipedia to retrieve search summary"""
    movie_title = "Harry Potter and the Sorcerer's Stone"
    search_titles = wikipedia.search(movie_title, results=1)
    search_title = search_titles[0]
    print("search_title: ", search_title)
    result = wikipedia.summary(search_title)
    print("result: ", result)


if __name__ == "__main__":
    app()

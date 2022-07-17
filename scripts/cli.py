import psycopg2
import requests
import typer

from recommender import prediction, trainer

app = typer.Typer()


@app.command()
def train():
    trainer.train()


@app.command()
def predict():
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
def db():
    try:
        connection = psycopg2.connect(
            user="admin",
            password="password",
            host="127.0.0.1",
            port="5432",
            database="mlflow-tracking-server-db",
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM runs ORDER BY end_time desc")
        record = cursor.fetchone()

        mlflow_run_id = record[0]
        return mlflow_run_id
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


if __name__ == "__main__":
    app()

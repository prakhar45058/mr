"""Script to create and save a movie review in SQLite database."""
import argparse
import datetime
import os
import sqlite3
import subprocess
import tempfile
from itertools import islice

import isle


TODAY = datetime.date.today().isoformat()
EDITOR = os.getenv("EDITOR")
DATABASE = os.getenv("MOVIE_DATABASE")
STYLE = {
    "purple": "\033[95m",
    "cyan": "\033[96m",
    "darkcyan": "\033[36m",
    "blue": "\033[94m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "bold": "\033[1m",
    "underline": "\033[4m",
    "end": "\033[0m",
}

SELECT_MOVIE = "SELECT * FROM movies WHERE tmdb_id=:tmdb_id"
SELECT_REVIEW = "SELECT * FROM reviews WHERE movie_id=:movie_id"
UPDATE_REVIEW = (
    "UPDATE reviews SET review=:review, modification_date=:modification_date"
)
INSERT_MOVIE = (
    "INSERT INTO `movies` "
    "(tmdb_id, imdb_id, original_title, default_title, year, runtime) VALUES "
    "(:tmdb_id, :imdb_id, :original_title, :default_title, :year, :runtime);"
)
INSERT_REVIEW = (
    "INSERT INTO reviews "
    "(movie_id, review, modification_date, creation_date) VALUES "
    "(:movie_id, :review, :modification_date, :creation_date);"
)

con = sqlite3.connect(DATABASE)
con.row_factory = sqlite3.Row


def stylized(style, string):
    return f"{STYLE[style]}{string}{STYLE['end']}"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--title", type=str)
    parser.add_argument("-y", "--year", type=int, default=None)
    parser.add_argument("-n", type=int, default=3)
    return parser.parse_args()


def print_movies(movies):
    print(f"\n{stylized('bold', 'SEARCH RESULTS 🔎')}\n")
    for i, movie in enumerate(movies, 1):
        print(f"{i}. {movie.year or '----'} - {movie.title['original']}")


def ask_movie(movies):
    while True:
        i = input(
            f"\n{stylized('bold', 'Choose a movie (1 is by default):')} "
        )
        i = int(i) if i != "" else 1
        if i in range(1, len(movies) + 1):
            break
    return movies[i - 1]


def ask_review(init_text=""):
    """Opens a text editor and returns text after saving."""
    tmp = tempfile.NamedTemporaryFile(suffix=".md", mode="w")
    with open(tmp.name, mode="w") as file:
        file.write(init_text)
    subprocess.run([EDITOR, tmp.name])
    with open(tmp.name, mode="r") as file:
        return file.read()


def print_done():
    print(f"\n{stylized('bold', 'All done!')} ✨ 🍰 ✨")


def add_movie(movie: isle.Movie):
    row = con.execute(SELECT_MOVIE, {"tmdb_id": movie.tmdb_id}).fetchone()
    movie_id = row["id"] if row else row
    if not movie_id:
        cur = con.execute(
            INSERT_MOVIE,
            {
                "tmdb_id": movie.tmdb_id,
                "imdb_id": movie.imdb_id,
                "original_title": movie.title["original"],
                "default_title": movie.title["default"],
                "year": movie.year or "NULL",
                "runtime": movie.runtime or "NULL",
            },
        )
        movie_id = cur.lastrowid
    return movie_id


def add_review(movie_id):
    row = con.execute(SELECT_REVIEW, {"movie_id": movie_id}).fetchone()
    review_id = row["id"] if row else row
    if not review_id:
        review = ask_review()
        cur = con.execute(
            INSERT_REVIEW,
            {
                "movie_id": movie_id,
                "review": review,
                "modification_date": TODAY,
                "creation_date": TODAY,
            }
        )
        review_id = cur.lastrowid
    else:
        review = ask_review(row["review"])
        cur = con.execute(
            UPDATE_REVIEW,
            {
                "review": review,
                "modification_date": TODAY
            }
        )


if __name__ == "__main__":
    args = parse_args()
    movies = list(islice(isle.search_movie(args.title, year=args.year), args.n))

    print_movies(movies)
    movie = ask_movie(movies)

    try:
        movie_id = add_movie(movie)
        add_review(movie_id)
    except Exception as error:
        raise error
    else:
        con.commit()
    finally:
        con.close()

    print_done()

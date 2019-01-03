from setuptools import setup
from pathlib import Path


BASE = Path(__file__).parent
DESC = "Script to create and save a movie review in SQLite database."


def get_long_description() -> str:
    with open(BASE / "README.md", "r", encoding="utf-8") as f:
        return f.read()


setup(
    name="movie-review",
    version="1.0.1",
    license="MIT",
    author="Dima Koskin",
    author_email="dmksknn@gmail.com",
    description=DESC,
    url="https://github.com/dmkskn/mr",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    py_modules=["review"],
    install_requires=["isle"],
    entry_points={"console_scripts": ["review=review:main"]},
)

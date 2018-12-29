import csv
import logging
import multiprocessing
import os
import sys

import pandas as pd

from gensim.models import Word2Vec
from gensim.utils import simple_preprocess


class Corpus:
    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self.csv_reader = None

    def __enter__(self):
        self.file = open("../dataset/dataset.csv", "r")
        self.csv_reader = csv.DictReader(self.file, delimiter=",")
        csv.field_size_limit(sys.maxsize)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            row = next(self.csv_reader)
            body_text = row["bodyText"]

            if body_text != "":
                return body_text

        # StopIteration exception is propagated


def main():
    body_texts = _load_body_texts()
    corpus = _preprocess_body_texts(body_texts)

    _train_model(corpus)


def _load_body_texts():
    print("Started loading bodyTexts")

    df = pd.read_csv("../dataset/dataset.csv", sep=",", usecols=[
        "bodyText"
    ], dtype={
        "bodyText": str
    })

    print("Finished loading bodyTexts")
    return df["bodyText"].tolist()


def _preprocess_body_texts(body_texts):
    print("Started preprocessing bodyTexts")

    result = [
        simple_preprocess(body_text) for body_text in body_texts
        if pd.notnull(body_text)
    ]

    print("Finished preprocessing bodyTexts")
    return result


def _train_model(corpus):
    logging.basicConfig(
        format="%(levelname)s - %(asctime)s: %(message)s", datefmt="%H:%M:%S",
        level=logging.INFO
    )

    num_cores = multiprocessing.cpu_count()
    model = Word2Vec(size=100, window=5, min_count=5, workers=num_cores)

    model.build_vocab(corpus, progress_per=10000)
    model.train(corpus, total_examples=len(corpus), epochs=10)

    os.makedirs("../models", exist_ok=True)
    model.save("../models/bodyText_word2vec.model")


if __name__ == "__main__":
    main()
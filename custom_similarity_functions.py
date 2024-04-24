import numpy as np
import math
from enum import Enum
from sklearn.feature_extraction.text import CountVectorizer
from scipy.spatial import distance
from os.path import basename


class SimilarityFunc(Enum):
    Cosine = 1
    DiceIndex = 2
    JacardCoefficient = 3
    SimpsonIndex = 4
    # EditDistance = 5


def Cosine(a, b, N):
    # a = ",".join(set(a))
    # b = ",".join(set(b))
    corpus = [a, b]
    vectorizer = CountVectorizer(ngram_range=(N, N))
    full_vec = vectorizer.fit_transform(corpus)

    a_vec = full_vec.toarray()[0].tolist()
    b_vec = full_vec.toarray()[1].tolist()

    cosine = distance.cosine(a_vec, b_vec)
    return 1 - cosine


def Cosine_vec(a, b, N):
    a = a.split(",")
    b = b.split(",")
    a_vec = []
    b_vec = []

    for ngram in a:
        ngram = ngram.split(" ")
        new_ngram = []
        for digit in ngram:
            if len(digit) == 0:
                continue
            new_ngram.append(float(digit))
        if len(new_ngram) > 0:
            a_vec.append(new_ngram)

    for ngram in b:
        ngram = ngram.split(" ")
        new_ngram = []
        for digit in ngram:
            if len(digit) == 0:
                continue
            new_ngram.append(float(digit))
        if len(new_ngram) > 0:
            b_vec.append(new_ngram)

    if len(a_vec) < len(b_vec):
        a_vec, b_vec = b_vec, a_vec

    while len(a_vec) > len(b_vec):
        b_vec.append([0.0] * N)

    b_vec = np.array(b_vec)
    a_vec = np.array(a_vec)
    results = []

    rows_in_slice = 100

    slice_start = 0
    slice_end = slice_start + rows_in_slice

    while slice_end <= a_vec.shape[0]:
        # results.append(distance.cdist(a_vec[slice_start:slice_end], b_vec[slice_start:slice_end], 'cosine'))
        results.append(a_vec[slice_start:slice_end].dot(b_vec.T).max(axis=1))

    slice_start += rows_in_slice
    slice_end = slice_start + rows_in_slice

    result = np.concatenate(results)
    return result
    # return distance.cdist(a_vec, b_vec, 'cosine')


def DiceIndex(a, b):
    return 2 * len(np.intersect1d(a, b)) / (len(a) + len(b))


def JacardCoefficient(a, b):
    return len(np.intersect1d(a, b)) / (len(set(a + b)))


def SimpsonIndex(a, b):
    if len(a) < len(b):
        return len(np.intersect1d(a, b)) / len(a)
    return len(np.intersect1d(a, b)) / len(b)


def EditDistance(a, b):
    return None


def compare_all(file1, file2, birthmark):
    result = []

    with open(file1, "r") as f:
        birthmark1 = f.read()

    with open(file2, "r") as f:
        birthmark2 = f.read()

    n = 1

    if birthmark == "3-gram":
        n = 3

    if birthmark == "6-gram":
        n = 6

    # else:
    result.append(
        [
            basename(file1),
            basename(file2),
            "Cosine",
            str(Cosine(birthmark1.replace(",", " "), birthmark2.replace(",", " "), n)),
        ]
    )
    result.append(
        [
            basename(file1),
            basename(file2),
            "DiceIndex",
            str(DiceIndex(birthmark1.split(","), birthmark2.split(","))),
        ]
    )
    result.append(
        [
            basename(file1),
            basename(file2),
            "JacardCoefficient",
            str(JacardCoefficient(birthmark1.split(","), birthmark2.split(","))),
        ]
    )
    result.append(
        [
            basename(file1),
            basename(file2),
            "SimpsonIndex",
            str(SimpsonIndex(birthmark1.split(","), birthmark2.split(","))),
        ]
    )

    return result

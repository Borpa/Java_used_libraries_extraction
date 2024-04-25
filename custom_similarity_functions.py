import numpy as np
import math
from enum import Enum
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial import distance
from os.path import basename


class SimilarityFunc(Enum):
    Cosine = 1
    DiceIndex = 2
    JacardCoefficient = 3
    SimpsonIndex = 4
    # EditDistance = 5


def Cosine_by_chunk(a, b):
    b = np.array(b)
    a = np.array(a)

    if len(a) < len(b):
        a, b = b, a

    results = []
    chunksize = 5

    start = 0
    end = chunksize

    while end <= a.shape[0]:
        # results.append(distance.cdist(a_vec[slice_start:slice_end], b_vec[slice_start:slice_end], 'cosine'))
        #cosine_sim = a[start:end].dot(b.T).max(axis=1)
        cosine_sim = cosine_similarity(a[start:end], b)
        cosine_sim = [np.average(x) for x in cosine_sim]
        results.append(cosine_sim)

        # cosine_sim = 1 - distance.cdist(a[start:end], b)
        # results.append(cosine_sim)

        start += chunksize
        end = start + chunksize

    result = np.average(np.concatenate(results))
    return result


def Cosine(a, b, N=1):
    # a = ",".join(set(a))
    # b = ",".join(set(b))
    corpus = [a, b]
    vectorizer = CountVectorizer(ngram_range=(N, N))
    full_vec = vectorizer.fit_transform(corpus)

    a_vec = full_vec.toarray()[0].tolist()
    b_vec = full_vec.toarray()[1].tolist()

    results = []
    chunksize = 10

    start = 0
    end = chunksize

    if len(a_vec) < end:
        end = len(a_vec)

    while end < len(a_vec):
        x = a_vec[start:end]
        y = b_vec[start:end]
        cosine = distance.cosine(x, y)
        results.append(1-cosine)

        start += chunksize
        end += chunksize

    end = len(a_vec)
    cosine = distance.cosine(a_vec[start:end], b_vec[start:end])
    results.append(1-cosine)

    return np.average(results)


    #cosine = distance.cosine(a_vec, b_vec)
    #return 1 - cosine

    # return Cosine_by_chunk(a_vec, b_vec)


def Cosine_ngram(a, b, N=3):
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

    # if len(a_vec) < len(b_vec):
    #    a_vec, b_vec = b_vec, a_vec
    # while len(a_vec) > len(b_vec):
    #    b_vec.append([0.0] * N)

    return Cosine_by_chunk(a_vec, b_vec)
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

    if "-gram" in birthmark:
        result.append(
            [
                basename(file1),
                basename(file2),
                birthmark,
                "Cosine",
                str(Cosine_ngram(birthmark1, birthmark2)),
            ]
        )

    else:
        result.append(
            [
                basename(file1),
                basename(file2),
                birthmark,
                "Cosine",
                str(Cosine(birthmark1.replace(",", " "), birthmark2.replace(",", " "))),
            ]
        )
    result.append(
        [
            basename(file1),
            basename(file2),
            birthmark,
            "DiceIndex",
            str(DiceIndex(birthmark1.split(","), birthmark2.split(","))),
        ]
    )
    result.append(
        [
            basename(file1),
            basename(file2),
            birthmark,
            "JacardCoefficient",
            str(JacardCoefficient(birthmark1.split(","), birthmark2.split(","))),
        ]
    )
    result.append(
        [
            basename(file1),
            basename(file2),
            birthmark,
            "SimpsonIndex",
            str(SimpsonIndex(birthmark1.split(","), birthmark2.split(","))),
        ]
    )

    return result

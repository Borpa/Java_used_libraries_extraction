import numpy as np
import math
from enum import Enum
from sklearn.feature_extraction.text import CountVectorizer
from scipy.spatial import distance


class SimilarityFunc(Enum):
    Cosine = 1
    DiceIndex = 2
    JacardCoefficient = 3
    SimpsonIndex = 4
    EditDistance = 5


def Cosine(a, b, N):
    corpus = [a, b]
    vectorizer = CountVectorizer(ngram_range=(N, N))
    full_vec = vectorizer.fit_transform(corpus)

    a_vec = full_vec.toarray()[0].tolist()
    b_vec = full_vec.toarray()[1].tolist()

    cosine = distance.cosine(a_vec, b_vec)
    return 1 - cosine


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

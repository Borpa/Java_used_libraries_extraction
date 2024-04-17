import run_pochi as pochi
import custom_similarity_functions as simfunc
from statistics import fmean


def ngram_maker(used_classes, meta_info, N=3):
    result = []
    prefix = meta_info + ["uc_{}-gram".format(N)]

    if len(used_classes) - N < 0:
        result = used_classes[0 : len(used_classes)]
        result = prefix + result
        return result

    i = 0
    for i in range(len(used_classes) - N):
        ngram = used_classes[i : i + N]
        result.append(" ".join(ngram))
        i += 1

    result = prefix + result
    return result


def extract_ngrams(filename, N=3):
    uc_list = pochi.pochi_extract_birthmark(filename, "uc")

    result = []

    for uc_birthmark in uc_list:
        uc_birthmark = uc_birthmark.split(",")

        if len(uc_birthmark) <= 1:
            continue

        index = uc_birthmark.index("uc")
        meta_info = uc_birthmark[:index]
        used_classes = uc_birthmark[index + 1 :]

        result.append(ngram_maker(used_classes, meta_info, N))

    return result


def extrac_uc_list(filename, N=3):
    uc_list = pochi.pochi_extract_birthmark(filename, "uc")

    result = []

    for uc_birthmark in uc_list:
        uc_birthmark = uc_birthmark.split(",")

        if len(uc_birthmark) <= 1:
            continue

        index = uc_birthmark.index("uc")
        meta_info = uc_birthmark[:index]
        used_classes = uc_birthmark[index + 1 :]

        result.append((meta_info, used_classes))

    return result


def compare_cosine(filename1, filename2, N=3):
    uc_list1 = extrac_uc_list(filename1)
    uc_list2 = extrac_uc_list(filename2)
    similarity_list = []

    for meta_info1, uc1 in uc_list1:
        for meta_info2, uc2 in uc_list2:
            similarity_list.append(simfunc.Cosine(" ".join(uc1), " ".join(uc2), N))
    similarity_list = list(filter(lambda x: x > 0.25, similarity_list))
    return fmean(similarity_list)


def compare(filename1, filename2, func, N=3):
    similarity_func = None
    match func:
        case simfunc.SimilarityFunc.Cosine:
            return compare_cosine(filename1, filename2, N)
        case simfunc.SimilarityFunc.DiceIndex:
            similarity_func = simfunc.DiceIndex
        case simfunc.SimilarityFunc.JacardCoefficient:
            similarity_func = simfunc.JacardCoefficient
        case simfunc.SimilarityFunc.SimpsonIndex:
            similarity_func = simfunc.SimpsonIndex
        case simfunc.SimilarityFunc.EditDistance:
            similarity_func = simfunc.EditDistance

    uc_ngram_list1 = extract_ngrams(filename1, N)
    uc_ngram_list2 = extract_ngrams(filename2, N)

    similarity_list = []

    for uc_ngram1 in uc_ngram_list1:
        for uc_ngram2 in uc_ngram_list2:
            meta_index1 = 0
            meta_index2 = 0

            for item in uc_ngram1:
                if item.endswith("-gram"):
                    break
                meta_index1 += 1

            for item in uc_ngram2:
                if item.endswith("-gram"):
                    break
                meta_index2 += 1

            meta_info1 = uc_ngram1[:meta_index1]
            meta_info2 = uc_ngram2[:meta_index2]
            used_classes1 = uc_ngram1[meta_index1 + 1 :]
            used_classes2 = uc_ngram2[meta_index2 + 1 :]

            output_header = [
                "birthmark",  # uc_ngram
                "comparator",  # similarity_func
                "matcher",  # None/simple
                "class1",
                "class2",
                "similarity",
            ]

            similarity_list.append(similarity_func(used_classes1, used_classes2))

    similarity_list = list(filter(lambda x: x > 0.25, similarity_list))
    return fmean(similarity_list)
    # return meta_info1 + meta_info2 + [similarity_score]


def main():
    return None


if __name__ == "__main__":
    main()

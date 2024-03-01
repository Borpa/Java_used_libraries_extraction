import pandas as pd

BIRTHMARK_DATA_DIR = "./birthmarks/"
BIRTHMARK_DATA_FILE = "Cypher-Notepad-master_ChatGPT-1.0.2.csv"
GROUPBY_OUTPUT_FILENAME = "groupby_info"
AVG_SIMILARITY_OUTPUT_FILENAME = "avg_similarity"


def read_birthmark_data():
    df = pd.read_csv(BIRTHMARK_DATA_DIR + BIRTHMARK_DATA_FILE)
    return df


def retrieve_group_info(dataframe):
    dataframe = dataframe.loc[dataframe.similarity == 1]
    dataframe = dataframe[
        [
            "project1_file",
            "project2_file",
            "birthmark",
            "comparator",
            "matcher",
            "class1",
            "class2",
        ]
    ]

    groupby_info = dataframe.groupby(["class1", "class2"]).size()

    with open(GROUPBY_OUTPUT_FILENAME, mode="w") as f:
        f.write(groupby_info.to_string())


def calculate_avg_similarity(dataframe):
    column_list = [
        "project1",
        "project1_ver",
        "project2",
        "project2_ver",
        "birthmark",
        "comparator",
        "matcher",
        "similarity",
    ]

    dataframe = dataframe[column_list]
    groupby_columns = column_list.remove("similarity")

    avg_values = dataframe.groupby(groupby_columns).mean()
    with open(AVG_SIMILARITY_OUTPUT_FILENAME, mode="w") as f:
        f.write(avg_values.to_string())


def main():
    dataframe = read_birthmark_data()
    retrieve_group_info(dataframe)
    calculate_avg_similarity(dataframe)


if __name__ == "__main__":
    main()

import pandas as pd

BIRTHMARK_DATA_DIR = "./birthmarks/"
BIRTHMARK_DATA_FILE = "Cypher-Notepad-master_ChatGPT-1.0.2.csv"
OUTPUT_FILENAME = "groupby_info"


def main():
    df = pd.read_csv(BIRTHMARK_DATA_DIR + BIRTHMARK_DATA_FILE)
    df = df.loc[df.similarity == 1]
    df = df[
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

    groupby_info = df.groupby(["class1", "class2"]).size()

    with open(OUTPUT_FILENAME, mode="w") as f:
        f.write(groupby_info.to_string())


if __name__ == "__main__":
    main()

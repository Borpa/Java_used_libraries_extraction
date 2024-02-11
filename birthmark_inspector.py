import pandas as pd

BIRTHMARK_DATA = "./birthmarks/Cypher-Notepad-master_ChatGPT-1.0.2.csv"
OUTPUT_FILENAME = "groups"


def main():
    df = pd.read_csv(BIRTHMARK_DATA)
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

    groups_info = df.groupby(["class1", "class2"]).size()

    with open(OUTPUT_FILENAME, mode="w") as f:
        f.write(groups_info.to_string())


if __name__ == "__main__":
    main()

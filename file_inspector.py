import os


def inspect_dir(root_dir, output_file):
    for path, subdirs, files in os.walk(root_dir):
        for name in files:
            filename = os.path.join(path, name)
            filesize = os.path.getsize(filename)

            with open(output_file, mode="a") as f:
                f.write(",".join([filename, filesize]) + "\n")


def main():
    output_file = "test.csv"

    with open(output_file, mode="w") as f:
        f.write("file,size\n")

    inspect_dir()


if __name__ == "__main__":
    main()

import os


def inspect_dir(root_dir, output_file):
    for path, subdirs, files in os.walk(root_dir):
        for name in files:
            if not name.endswith(".class"):
                continue
            filename = os.path.join(path, name)
            filesize = str(os.path.getsize(filename))

            with open(output_file, mode="a") as f:
                f.write(",".join([filename, filesize]) + "\n")


def main():
    output_file = "project_files_size_data.csv"
    with open(output_file, mode="w") as f:
        f.write("file,size (B)\n")
    root_dir = "C:/Users/FedorovNikolay/source/Study/test_projects/current/"

    inspect_dir(root_dir, output_file)


if __name__ == "__main__":
    main()

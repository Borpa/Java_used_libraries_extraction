import os


def inspect_dir_by_num_of_lines(root_dir, output_file):
    with open(output_file, mode="w") as f:
        f.write("file,lines\n")

    for path, subdirs, files in os.walk(root_dir):
        for name in files:
            if not name.endswith(".java"):
                continue
            filename = os.path.join(path, name)
            lines = None

            with open(output_file, mode="a") as f:
                f.write(",".join([filename, lines]) + "\n")


def inspect_dir_by_num_instruct(root_dir, output_file):
    with open(output_file, mode="w") as f:
        f.write("file,instructions count\n")

    for path, subdirs, files in os.walk(root_dir):
        for name in files:
            if not name.endswith(".class"):
                continue
            filename = os.path.join(path, name)
            instruct_count = None

            with open(output_file, mode="a") as f:
                f.write(",".join([filename, instruct_count]) + "\n")


def inspect_dir_by_filesize(root_dir, output_file, postfix=".class"):
    with open(output_file, mode="w") as f:
        f.write("file,size (B)\n")

    for path, subdirs, files in os.walk(root_dir):
        for name in files:
            if not name.endswith(postfix):
                continue
            filename = os.path.join(path, name)
            filesize = str(os.path.getsize(filename))

            with open(output_file, mode="a") as f:
                f.write(",".join([filename, filesize]) + "\n")


def main():
    output_file = "project_files_size_data.csv"

    root_dir = "C:/Users/FedorovNikolay/source/Study/test_projects/current/"

    inspect_dir_by_filesize(root_dir, output_file)


if __name__ == "__main__":
    main()

import os
import command_runner
import re
from enum import Enum

HEADER_BASE = "project_type,project_name,project_version,filename,{},filepath\n"

HEADER_SIZE = HEADER_BASE.format("file_size(B)")
HEADER_LINE_COUNT = HEADER_BASE.format("line_count")
HEADER_INSTRUCT_COUNT = HEADER_BASE.format("instruction_count")


class Inspect_type(Enum):
    Size = 1
    Line_count = 2
    Instruct_count = 3


def get_instruct_count(classpath):
    command = "javap -c " + classpath
    disassembled_class = command_runner.run_bash_command(command)
    instruct_count = len(re.findall("\s+\d+:\s\w+"), disassembled_class)

    return instruct_count


def get_line_count(filepath):
    with open(filepath, "r") as f:
        line_count = len(f.readlines())

    return line_count


def get_filesize(filepath):
    return str(os.path.getsize(filepath))


def inspect_dir(root_dir, output_file, output_header, file_postfix, inspect_type):
    with open(output_file, mode="w") as f:
        f.write(output_header)

    if inspect_type == Inspect_type.Line_count:
        file_postfix = ".java"

    if inspect_type == Inspect_type.Instruct_count:
        file_postfix = ".class"

    for path, subdirs, files in os.walk(root_dir):
        for name in files:
            if not name.endswith(file_postfix):
                continue

            filepath = os.path.join(path, name)
            filepath = filepath.replace("\\", "/")

            filename = os.path.basename(filepath)
            path_list = filepath.replace(root_dir, "").split("/")
            project_type = path_list[0]
            project_name = path_list[1]
            project_version = path_list[2]

            match inspect_type:
                case Inspect_type.Size:
                    filesize = get_filesize(filepath)
                    output = ",".join(
                        [
                            project_type,
                            project_name,
                            project_version,
                            filename,
                            filesize,
                            filepath,
                        ]
                    )
                case Inspect_type.Line_count:
                    line_count = get_line_count(filepath)
                    output = ",".join(
                        [
                            project_type,
                            project_name,
                            project_version,
                            filename,
                            line_count,
                            filepath,
                        ]
                    )
                case Inspect_type.Instruct_count:
                    instruct_count = get_instruct_count(filepath)
                    output = ",".join(
                        [
                            project_type,
                            project_name,
                            project_version,
                            filename,
                            instruct_count,
                            filepath,
                        ]
                    )
                case _:
                    return None

            with open(output_file, mode="a") as f:
                f.write(output + "\n")


def main():
    output_file = "project_files_size_data.csv"
    root_dir = "C:/Users/FedorovNikolay/source/Study/test_projects/current/"

    inspect_dir(root_dir, output_file, HEADER_SIZE, ".class", Inspect_type.Size)


if __name__ == "__main__":
    main()

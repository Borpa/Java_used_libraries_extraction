import os
import command_runner
import re
from enum import Enum

HEADER_BASE = "project_type,project_name,project_version,filename,{},filepath\n"

VALUE_COLUMN_SIZE = "file_size(B)"
VALUE_COLUMN_LINE_COUNT = "line_count"
VALUE_COLUMN_INSTRUCT_COUNT = "instruction_count"

HEADER_SIZE = HEADER_BASE.format(VALUE_COLUMN_SIZE)
HEADER_LINE_COUNT = HEADER_BASE.format(VALUE_COLUMN_LINE_COUNT)
HEADER_INSTRUCT_COUNT = HEADER_BASE.format(VALUE_COLUMN_INSTRUCT_COUNT)


class Inspect_type(Enum):
    Size = 1 #file size in Bytes
    Line_count = 2
    Instruct_count = 3


def get_instruct_count(classpath):
    command = "javap -c " + classpath
    disassembled_class = command_runner.run_cmd_command(command)
    instruct_count = len(re.findall("\s+\d+:\s\w+", disassembled_class))

    return instruct_count


def get_line_count(filepath):
    with open(filepath, "r", encoding="utf8") as f:
        line_count = len(f.readlines())

    return line_count


def get_filesize(filepath):
    return str(os.path.getsize(filepath))


def inspect_dir(
    root_dir,
    output_file,
    inspect_type=Inspect_type.Size,
    file_extension=".java",
):
    match inspect_type:
        case Inspect_type.Size:
            output_header = HEADER_SIZE
        case Inspect_type.Line_count:
            output_header = HEADER_LINE_COUNT
            file_extension = ".java"
        case Inspect_type.Instruct_count:
            output_header = HEADER_INSTRUCT_COUNT
            file_extension = ".class"
        case _:
            return None

    with open(output_file, mode="w") as f:
        f.write(output_header)

    for path, subdirs, files in os.walk(root_dir):
        for name in files:
            if not name.endswith(file_extension):
                continue

            filepath = os.path.join(path, name)
            filepath = filepath.replace("\\", "/")

            filename = os.path.basename(filepath)
            path_list = filepath.replace(root_dir, "").split("/")
            project_type = path_list[0]
            project_name = path_list[1]
            project_version = path_list[2]

            output_base = ",".join(
                [
                    project_type,
                    project_name,
                    project_version,
                    filename,
                    "{}",
                    filepath,
                ]
            )

            match inspect_type:
                case Inspect_type.Size:
                    inspected_data = get_filesize(filepath)
                case Inspect_type.Line_count:
                    inspected_data = get_line_count(filepath)
                case Inspect_type.Instruct_count:
                    inspected_data = get_instruct_count(filepath)
                case _:
                    return None

            output = output_base.format(inspected_data)

            with open(output_file, mode="a") as f:
                f.write(output + "\n")


def main():
    output_file = "project_files_instruct_count.csv"
    # root_dir = "C:/Users/FedorovNikolay/source/Study/test_projects/current/"
    root_dir = "D:/Study/phd_research/test_projects/current/"

    inspect_dir(root_dir, output_file, inspect_type=Inspect_type.Instruct_count)


if __name__ == "__main__":
    main()

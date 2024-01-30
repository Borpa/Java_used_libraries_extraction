import subprocess

STIGMATA_LOCATION = (
    "d:/Study/phd_research/birthmark_extraction_software/stigmata-master/target/"
)
STIGMATA_VERSION = "stigmata-5.0-SNAPSHOT.jar"
BIRTHMARK_LIST = ["cvfv", "fmc", "fuc", "is", "kgram", "smc", "uc", "wsp"]

GIT_BASH_EXEC_PATH = "C:/Program Files/Git/bin/bash.exe"


def run_bash_command(command):
    output = subprocess.check_output(
        command, shell=False, executable=GIT_BASH_EXEC_PATH
    )
    output = output.decode()

    return output


def get_birthmark_list():
    return BIRTHMARK_LIST


def extract_compare(birthmark, file1, file2):
    command = " ".join(
        [
            "java -jar",
            STIGMATA_LOCATION + STIGMATA_VERSION,
            "compare",
            "extract",
            "-b",
            birthmark,
            file1,
            "extract",
            "-b",
            birthmark,
            file2,
        ]
    )
    command_output = run_bash_command(command)

    return command_output


def extract_compare_all(file1, file2):
    result = []
    for birthmark in BIRTHMARK_LIST:
        comparison = extract_compare(birthmark, file1, file2)
        result.append(comparison)

    return result

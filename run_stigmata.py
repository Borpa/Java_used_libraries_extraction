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


def extract_birthmark(file, birthmark):
    command = " ".join(
        [
            "java -jar",
            STIGMATA_LOCATION + STIGMATA_VERSION,
            "-b",
            birthmark,
            "extract",
            file,
        ]
    )
    command_output = run_bash_command(command)
    return command_output


def compare_birthmarks(birthmark1, birthmark2):
    command = " ".join(
        [
            "java -jar",
            STIGMATA_LOCATION + STIGMATA_VERSION,
            "compare",
            birthmark1,
            birthmark2,
        ]
    )
    command_output = run_bash_command(command)

    return command_output

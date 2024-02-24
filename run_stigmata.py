import subprocess

STIGMATA_LOCATION = (
    "D:/Study/phd_research/birthmark_extraction_software/stigmata-master/target/"
)
STIGMATA_VERSION = "stigmata-5.0-SNAPSHOT.jar"
BIRTHMARK_LIST = ["cvfv", "fmc", "fuc", "is", "kgram", "smc", "uc", "wsp"]

GIT_BASH_EXEC_PATH = "C:/Program Files/Git/bin/bash.exe"

SCRIPT_NAME = "stigmata_extract_compare.sh"


def run_bash_command(command):
    output = subprocess.check_output(
        command, shell=False, executable=GIT_BASH_EXEC_PATH
    )
    output = output.decode()

    return output


def run_cmd_command(command):
    proc = subprocess.Popen(
        command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    out, err = proc.communicate()
    output = out.decode()
    return output

def get_birthmark_list():
    return BIRTHMARK_LIST


def extract_compare(birthmark, file1, file2):
    #command = " ".join(
    #    [
    #        "java",
    #        "-jar",
    #        STIGMATA_LOCATION + STIGMATA_VERSION,
    #        "compare",
    #        "extract",
    #        "-b",
    #        birthmark,
    #        file1,
    #        "extract",
    #        "-b",
    #        birthmark,
    #        file2,
    #    ]
    #)
    command = " ".join([
        "sh",
        SCRIPT_NAME,
        STIGMATA_LOCATION + STIGMATA_VERSION,
        birthmark,
        file1,
        file2,
    ])

    command_output = run_bash_command(command)

    return command_output


def extract_compare_all(file1, file2):
    result = []
    for birthmark in BIRTHMARK_LIST:
        comparison = extract_compare(birthmark, file1, file2)
        result.append(comparison)

    return result

def run_stigmata(
    project1,
    project1_file_list,
    project2,
    project2_file_list,
    options=None,
):
    total_result = []
    for project1_file in project1_file_list:
        for project2_file in project2_file_list:
            # pair_result = stigmata.extract_compare_all(project1_file, project2_file)
            pair_result = extract_compare(
                "kgram", project1_file, project2_file
            )
            total_result.append(pair_result)

    return total_result

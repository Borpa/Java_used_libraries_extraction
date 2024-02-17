import subprocess

GIT_BASH_EXEC_PATH = "C:/Program Files/Git/bin/bash.exe"


def run_cmd_command(command):
    """
    Run cmd command and return the output.

    Parameters:
    ----------

    command : str
        cmd command

    """
    proc = subprocess.Popen(
        command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    out, err = proc.communicate()
    output = out.decode()
    return output


def run_bash_command(command):
    output = subprocess.check_output(
        command, shell=False, executable=GIT_BASH_EXEC_PATH
    )
    output = output.decode()

    return output

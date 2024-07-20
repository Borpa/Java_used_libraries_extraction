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
        command,
        shell=False,
        executable=GIT_BASH_EXEC_PATH,
    )
    output = output.decode()
    return output


def run_bash_command_no_output(command):
    output = subprocess.check_output(
        command,
        shell=False,
        executable=GIT_BASH_EXEC_PATH,
    )
    output = output.decode()


def run_bash_command_file_output(command, filename, filemode):
    file = open(filename, filemode)
    proc = subprocess.Popen(
        command,
        shell=False,
        stdin=subprocess.PIPE,
        stdout=file,
        executable=GIT_BASH_EXEC_PATH,
    )
    out, err = proc.communicate()

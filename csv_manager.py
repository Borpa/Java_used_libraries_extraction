import csv


def init_output_csv(header, filename):
    """
    Initialize output csv file for extracted dependencies

    Parameters:
    ----------

    header : str
        The header of the output csv

    filename : str
        output csv filename

    """
    with open(filename, "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)


def append_new_entry(filename, entry):
    with open(filename, "a", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(entry)


def append_new_entry_list(filename, entry_list):
    """
    Append new values to the output csv file

    Parameters:
    ----------

    filename : str
        output csv filename

    entry_list : list(list(str))
        list of new entries to the output file

    """
    with open(filename, "a", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        for entry in entry_list:
            writer.writerow(entry)

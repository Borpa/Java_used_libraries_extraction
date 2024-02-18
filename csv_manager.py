import csv
import os


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


def init_csv_file(filename, header, dir=None):
    if dir is not None:
        if not os.path.exists(dir):
            os.makedirs(dir)
        filename = dir + filename
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


def append_csv_data(filename, data, dir=None):
    filename = dir + filename
    with open(filename, "a", encoding="UTF8", newline="") as f:
        for row in data:
            writer = csv.writer(f)
            writer.writerow(row)

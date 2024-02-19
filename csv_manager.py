import csv
import os


def init_csv_file(filename, header, dir=None):
    if dir is not None:
        if not os.path.exists(dir):
            os.makedirs(dir)
        filename = dir + filename
    with open(filename, "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)


def append_single_entry(filename, entry, dir=None):
    filename = dir + filename
    try:
        with open(filename, "a", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(entry)
    except FileNotFoundError:
        print(FileNotFoundError)
        return


def append_csv_data(filename, data, dir=None):
    filename = dir + filename
    try:
        with open(filename, "a", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            for row in data:
                writer.writerow(row)
    except FileNotFoundError:
        print(FileNotFoundError)
        return
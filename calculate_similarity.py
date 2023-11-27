import json, csv
from itertools import repeat
from multiprocessing import Pool, freeze_support
import numpy as np
import itertools

def calculate_libraries(soft_list, full_list):
    result = list()

    for software in soft_list:
        file1 = software["filename"]
        file1_type = software["type"]
        file1_path = software["filepath"]
        imports_list1 = software["imports"]
        unique_libraries1 = software["unique_libraries"]
        project1 = software["project_name"]

        for comparison in full_list:
            project2 = comparison["project_name"]
            if (project1 == project2): continue

            file2 = comparison["filename"]
            file2_type = comparison["type"]
            file2_path = comparison["filepath"]
            imports_list2 = comparison["imports"]
            unique_libraries2 = comparison["unique_libraries"]

            if len(imports_list1) != 0:
                same_imports_perc = len(set(imports_list1) &
                                         set(imports_list2)) / len(imports_list1) * 100
            else:
                same_imports_perc = 0

            if  len(unique_libraries1) != 0:
                same_uniques_perc = len(set(unique_libraries1) &
                                         set(unique_libraries2)) / len(unique_libraries1) * 100
            else:
                same_uniques_perc = 0

            #if file1_type != file2_type and same_imports_perc < 70 or same_uniques_perc < 65: continue
            if file1_type != file2_type and same_imports_perc < 95: continue
            #if file1_type == file2_type and same_imports_perc > 30 or same_uniques_perc > 35: continue
            if file1_type == file2_type and same_imports_perc > 5: continue

            result.append([file1, file1_type, file2, file2_type, 
                             same_imports_perc, same_uniques_perc, 
                            project1, project2, file1_path, file2_path])

    return result

def main():
    with open("imported_libraries.json", "r") as f:
        data = json.load(f)

    software_list = data["software"]

    header = ["file1", "file1_type", "file2", "file2_type", "imports, %",
               "unique libraries, %", "project1", "project2", "file1_path", "file2_path"]

    soft_lists = np.array_split(software_list, 3)

    with Pool() as pool:
        result = pool.starmap(calculate_libraries,
                                                  zip(soft_lists, repeat(software_list)))

    result = list(itertools.chain.from_iterable(result))

    with open("lib_similarity.csv", "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for res in result:
            writer.writerow(res)

if __name__ == "__main__":
    freeze_support()
    main()
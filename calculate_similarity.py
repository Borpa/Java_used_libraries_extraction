import csv
from itertools import repeat
from multiprocessing import Pool, freeze_support
import numpy as np
from pandas import read_csv
import itertools

def calculate_similarity(project_nums, file_groups):
    result = list()

    for project_num in project_nums:
        if project_num == (len(file_groups) - 1): return result

        for i in range(project_num + 1, len(file_groups)):
            project1 = file_groups[project_num]
            project2 = file_groups[i]

            project1_imports = project1.imports.tolist()
            project1_imports = [i.replace("'","").strip('][').split(', ') for i in project1_imports]
            project1_imports = list(itertools.chain.from_iterable(project1_imports))

            project2_imports = project2.imports.tolist()
            project2_imports = [i.replace("'","").strip('][').split(', ') for i in project2_imports]
            project2_imports = list(itertools.chain.from_iterable(project2_imports))

            same_imports = set(project1_imports) & set(project2_imports)

            imports_ratio1 = len(same_imports) / len(project1_imports) * 100
            imports_ratio2 = len(same_imports) / len(project2_imports) * 100

            project1_type = project1.type.tolist()[0]
            project2_type = project2.type.tolist()[0]

            project1_name = project1.project.tolist()[0]
            project2_name = project2.project.tolist()[0]

            result.append([project1_name, project2_name,
                            project1_type, project2_type, imports_ratio1, imports_ratio2])
    return result

def main():
    csv_data = read_csv("imported_libraries.csv")

    project_groups = csv_data.groupby("project")["project"]    
    [project_groups.get_group(x) for x in project_groups.groups]
    projects = project_groups.unique().index.values

    num_of_projects = len(projects)
    
    file_groups = [x for _, x in csv_data.groupby("project")]

    file_groups_nums = [i for i in range(0, num_of_projects)]
    file_groups_nums = np.array_split(file_groups_nums, 3)

    with Pool() as pool:
        result = pool.starmap(calculate_similarity,
                                                  zip(file_groups_nums, repeat(file_groups)))
    
    header = ["project1", "project2", "project1_type",
               "project2_type", "imports_ratio1", "imports_ratio2"]

    result = list(itertools.chain.from_iterable(result))

    with open("lib_similarity.csv", "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for res in result:
            writer.writerow(res)

if __name__ == "__main__":
    freeze_support()
    main()
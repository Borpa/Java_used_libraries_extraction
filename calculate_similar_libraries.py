import json, csv

with open("imported_libraries.json", "r") as f:
    data = json.load(f)

software_list = data["software"]

#output = "file1\tfile2\timports %\tunique libraries %\n\n"

header = ["file1", "file1_type", "file2", "file2_type", "imports, %",
           "unique libraries, %", "file1_path", "file2_path"]

with open("lib_similarity.csv", "w", encoding="UTF8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)

for software in software_list:
    file1 = software["filename"]
    file1_type = software["type"]
    file1_path = software["filepath"]
    imports_list1 = software["imports"]
    unique_libraries1 = software["unique_libraries"]

    for comparison in software_list:
        if (software is comparison): continue

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

        #if (same_imports_perc == 0 and same_uniques_perc <= 50): continue

        #newline = "\t".join((file1, file2, str(same_imports_perc), str(same_uniques_perc), "\n"))
        #output += newline

        if file1_type != file2_type and same_imports_perc < 70 or same_uniques_perc < 65: continue
        if file1_type == file2_type and same_imports_perc > 30 or same_uniques_perc > 35: continue

        with open("lib_similarity.csv", "a", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([file1, file1_type, file2, file2_type, 
                             same_imports_perc, same_uniques_perc, file1_path, file2_path])


#with open("lib_similarity_list.txt", "w") as f:
#    f.write(output)


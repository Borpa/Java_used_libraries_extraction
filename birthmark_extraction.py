import os
import subprocess
import sys
import csv

import pandas as pd


def get_similar_pairs(threshold, num_of_pairs, similarity_data):
    df = pd.read_csv(similarity_data)
    project_groups = [x for _, x in df.groupby(["project1", "project2"])]

    top_results = []

    for group in project_groups:
        group = (
            group.loc[group["dependency_ratio"] >= threshold]
            .sort_values(by="dependency_ratio", ascending=False)
            .head(num_of_pairs)
        )
        top_results.append(group)

    return pd.concat(top_results)


def run_cmd_command(command):
    #(cd D:/Study/phd_research/birthmark_extraction_software/pochi-2.6.0/bin/ && ./pochi D:/Study/phd_research/birthmark_extraction_software/pochi-2.6.0/bin/extract_test_2.groovy D:/Study/phd_research/tested_software/text_editor/clopad_new/clopad/target/clopad-0.1.0-SNAPSHOT.jar D:/Study/phd_research/tested_software/ai_app/langchain4j-0.24.0/langchain4j-0.24.0/langchain4j/target/langchain4j-0.24.0.jar no-csv)
    #(cd D:/Study/phd_research/birthmark_extraction_software/pochi-2.6.0/bin/ && ./pochi D:/Study/phd_research/birthmark_extraction_software/pochi-2.6.0/bin/extract_test_2.groovy D:/Study/phd_research/tested_software/text_editor/clopad_new/clopad/target/clopad-0.1.0-SNAPSHOT.jar D:/Study/phd_research/tested_software/ai_app/langchain4j-0.24.0/langchain4j-0.24.0/langchain4j/target/langchain4j-0.24.0.jar no-csv)

    
    #total_command = ["C:\Program Files\Git\git-bash.exe", command]
    #print(total_command)
    #proc = subprocess.Popen(
    #    total_command,
    #    #bufsize=-1,
    #    #executable=None,
    #    stdin=subprocess.PIPE,
    #    stdout=subprocess.PIPE,
    #    #stderr=None,
    #    #preexec_fn=None,
    #    #close_fds=False,
    #    shell=True,
    #    # cwd="C:/Users/userName/Documents/dev",
    #)
    #proc.wait()


    # proc = subprocess.Popen(
    #    command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    # )
    #print(proc.communicate())
    #out, err = proc.communicate()
    #output = out.decode()

    #new_command = "ls"
    #new_command  = "sh D:/Study/phd_research/birthmark_extraction_software/pochi-2.6.0/bin/pochi -h"
    #output = os.system(new_command).decode()

    #print(new_command)
#
    #proc = subprocess.run(new_command, shell=False, capture_output=True)
    #output = proc.stdout.decode()

    new_command  = "sh D:/Study/phd_research/birthmark_extraction_software/pochi-2.6.0/bin/pochi D:/Study/phd_research/birthmark_extraction_software/pochi-2.6.0/bin/extract_test_2.groovy D:/Study/phd_research/tested_software/text_editor/clopad_new/clopad/target/clopad-0.1.0-SNAPSHOT.jar D:/Study/phd_research/tested_software/ai_app/langchain4j-0.24.0/langchain4j-0.24.0/langchain4j/target/langchain4j-0.24.0.jar no-csv"
    output= subprocess.check_output(
        new_command, shell=False, executable=r"C:\Program Files\Git\bin\bash.exe")

    print(output)

    return ""


def export_as_csv(filename, data):
    with open(filename, "w", encoding="UTF8", newline="") as f:
        for row in data:
            writer = csv.writer(f)
            writer.writerow(row)


def run_pochi(
    software_location,
    project1,
    project1_file_list,
    project2,
    project2_file_list,
    options=None,
):
    version = "pochi-2.6.0"
    full_path = software_location + version + "/bin/"
    # extraction_script = "pochi_scripts/extract-compare_all.groovy"
    pochi_script = "(cd " + full_path + " && ./pochi"
    #pochi_script = full_path + "pochi"
    extraction_script = full_path + "extract_test_2.groovy"
    total_output = []
    header = [
        "project1_file",
        "project2_file",
        "birthmark",
        "comparator",
        "matcher",
        "class1",
        "class2",
        "similarity",
    ]
    total_output.append(header)

    output_filename = "__".join([project1, project2])

    #for project1_file in project1_file_list:
    #    for project2_file in project2_file_list:
            # command = " ".join()
    
    #project1_file = "D:/Study/phd_research/tested_software/text_editor/clopad_new/clopad/target/clopad-0.1.0-SNAPSHOT.jar"
    #project2_file = "D:/Study/phd_research/tested_software/ai_app/langchain4j-0.24.0/langchain4j-0.24.0/langchain4j/target/langchain4j-0.24.0.jar"
    project1_file = "D:/Study/phd_research/birthmark_extraction_software/pochi-2.6.0/bin/example_soft/clopad-0.1.0-SNAPSHOT.jar"
    project2_file = "D:/Study/phd_research/birthmark_extraction_software/pochi-2.6.0/bin/example_soft/langchain4j-0.24.0.jar"

    command = " ".join([
        pochi_script,
        extraction_script,
        project1_file,
        project2_file,
        options+")",
    ])
    #print(command)
    output = run_cmd_command(command)
    #print(output)
    for line in output:
        line = line.split(",")
        newline = [project1_file, project2_file] + output
        total_output.append(newline)

    export_as_csv(output_filename, total_output)


def run_stigmara(software_location, program_1, program_2, options):
    version = "stigmata-master/target/"
    full_path = software_location + version

    return None


def get_project_jar_list(main_dir, project_type, project_name):
    project_type = project_type.replace("/", "")
    target_dir = main_dir + project_type + "/" + project_name + "/"
    jar_list = []

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".jar"):
                if "src" not in root and "lib" not in root:
                    filepath = os.path.join(root, file).replace("\\", "/")
                    jar_list.append(filepath)
    return jar_list


if __name__ == "__main__":
    # option = sys.argv[0]

    similarity_data = "file_similarity.csv"
    birthmark_software = "D:/Study/phd_research/birthmark_extraction_software/"
    tested_software = "D:/Study/phd_research/tested_software/"

    pochi_output_header = [
        "birthmark",
        "comparator",
        "matcher",
        "file1",
        "file2",
        "result",
    ]

    similarity_groups = get_similar_pairs(70, 3, similarity_data)
    project_pairs = similarity_groups[
        ["project1", "project2", "project1_type", "project2_type"]
    ]
    project_pairs = project_pairs.drop_duplicates()

    # print(project_pairs)

    # for index, row in project_pairs.iterrows():
    # project1_list = get_project_jar_list(
    #    tested_software, row.project1_type, row.project1
    # )
    # project2_list = get_project_jar_list(
    #    tested_software, row.project2_type, row.project2
    # )

    project1_list = get_project_jar_list(tested_software, "/text_editor/", "clopad_new")
    project2_list = get_project_jar_list(
        tested_software, "/ai_app/", "langchain4j-0.24.0"
    )

    output = run_pochi(
        birthmark_software,
        "clopad_new",
        # row.project1,
        project1_list,
        "langchain4j-0.24.0",
        # row.project2,
        project2_list,
        "no-csv",
    )

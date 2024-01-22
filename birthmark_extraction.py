import os
import subprocess
import sys

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
    proc = subprocess.Popen(
        command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    out, err = proc.communicate()
    output = out.decode()
    return output


def run_pochi(software_location, program_1, program_2, options=None):
    version = "pochi-2.6.0"
    full_path = software_location + version + "/bin/"
    extraction_script = full_path + "extract-compare_all.groovy"
    pochi_script = full_path + "pochi"
    output_filename = "_".join([program_1, program_2, version])

    command = " ".join([pochi_script, extraction_script, program_1, program_2, options])
    command = command + " > " + output_filename
    output = run_cmd_command(command)

    return output


def run_stigmara(software_location, program_1, program_2, options):
    version = "stigmata-master/target"
    # java -jar stigmata-5.0-SNAPSHOT.jar -b cvfv -f xml --store-target MEMORY extract ./test-classes/resources/samplewar.war > test.xml
    return None


def get_project_jar_list(main_dir, project_type, project_name):
    project_type = project_type.replace("/", "")
    target_dir = main_dir + project_type + "/" + project_name + "/"
    jar_list = []

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".jar") and "src" not in root:
                jar_list.append(file)
    return jar_list

if __name__ == "__main__":
    option = sys.argv[0]

    similarity_data = "file_similarity.csv"
    birthmark_software = "../birthmark_extraction_software/"
    tested_software = "../tested_software/"

    similarity_groups = get_similar_pairs(70, 3, similarity_data)
    project_pairs = similarity_groups[
        ["project1", "project2", "project1_type", "project2_type"]
    ]
    project_pairs = project_pairs.drop_duplicates()

    print(project_pairs)

    for index, row in project_pairs.iterrows():
        project1_list = get_project_jar_list(tested_software, row.project1_type, row.project1)
        project2_list = get_project_jar_list(tested_software, row.project2_type, row.project2)

        if option == "pochi":
            output = run_pochi(birthmark_software, project1_list, project2_list)

    # print(project_pairs)
    # print(get_project_jar(tested_software, "/text_editor/", "clopad_new"))

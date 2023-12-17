import os, sys, subprocess, csv, io, re
from bs4 import BeautifulSoup
import pandas as pd 

def init_output_csv(header, filename):
    with open(filename, "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)

def append_new_entry(filename, entry_list):
    with open(filename, "a", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        for entry in entry_list:
            writer.writerow(entry)

def project_has_entry(output_filename, project_name):
    df = pd.read_csv(output_filename)
    has_entry = project_name in df["project"].unique()
    print(df["project"].unique())
    return has_entry

def get_project_type(filepath, type_list):
    project_type = "/empty_type/"
    for typ in type_list:
        if typ in filepath: 
            project_type = typ
            break
    return project_type

def create_entry_list(project_name, project_type, dep_list):
    entry_list = []
    for dep in dep_list:
        entry_list.append([project_name, dep, project_type])
    return entry_list

def run_cmd_command(command):
    proc = subprocess.Popen(command, shell=True, 
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = proc.communicate()
    output = out.decode()
    return output

def extract_deps_from_pom(filepath):
    with open(filepath, "r") as f:
        xml_data = f.read()
    bs_data = BeautifulSoup(xml_data, "xml")

    dep_list = []
    for dep in bs_data.find_all("dependency"):
        #dep_list.append({"dependency": dep.find("artifactId").text,
        #                 "version": dep.find("version").text})
        dep_list.append(dep.find("artifactId").text)

    return dep_list

def extract_deps_from_jar(filepath):
    print(filepath)
    jar_filename = os.path.basename(filepath)
    command = "jdeps -R --print-module-deps {}".format(filepath)
    output = run_cmd_command(command)

    if "Error: Missing dependencies:" not in output:
        print("ran new command")
        command = "jdeps -R {}".format(filepath)
        output = run_cmd_command(command)

    buffer = io.StringIO(output)
    line = buffer.readline()

    result = []

    while line:
        if "->" in line and "not found" in line or jar_filename in line:
            line = line.replace("->", "")
            entry = re.split("\s\s+",line)
            entry = [i for i in entry if i] #remove empty elements 
            
            if len(entry) != 3: 
                line = buffer.readline()
                continue

            #check if dependency is not included or if dependency is included in the .jar and is not standard 
            if entry[2] == "not found" or entry[2] == jar_filename and not entry[1].startswith("java"):
                result.append(entry[1])

        line = buffer.readline()

    return result

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(len(sys.argv))
        print("Incorrect number of arguments\n")
        exit()

    target_dir = sys.argv[1]

    #header = ["class", "dependency", "origin"]
    header = ["project", "dependency", "project_type"]
    output_filename = "dependencies.csv"

    project_types = ["/ai_app/", "/book_reader/", "/web_file_browser/", "/calculator/", 
                  "/emulator_environment/", "/graphic_editor/", "/dev_environment/", 
                  "/media_player/", "/terminal_interface/", "/text_editor/", "/text_voice_chat/"]

    init_output_csv(header, output_filename)

    for root, dirs, files in os.walk(target_dir):
        if "pom.xml" in files:
            file = "pom.xml"
            project_name = os.path.basename(root)
            filepath = os.path.join(root, file).replace("\\", "/")
            dep_list = extract_deps_from_pom(filepath)
            project_type = get_project_type(filepath, project_types)

            append_new_entry(output_filename, 
                             create_entry_list(project_name, project_type, dep_list))
            continue

        for file in files:
            if file.endswith(".jar"):
                project_name = os.path.basename(root)
                if project_name in ["src", "target", "lib"]: continue
                if project_has_entry(output_filename, project_name): continue

                filepath = os.path.join(root, file).replace("\\", "/")
                filename = file.replace(".jar", "")

                dep_list = extract_deps_from_jar(filepath)
                project_type = get_project_type(filepath, project_types)

                append_new_entry(output_filename, 
                                 create_entry_list(project_name, project_type, dep_list))
                continue

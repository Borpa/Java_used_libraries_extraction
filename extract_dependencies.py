import os, sys, subprocess, csv, io
from bs4 import BeautifulSoup

def init_output_csv(header, filename):
    with open(filename, "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)

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
        dep_list.append({"artifactId": dep.find("artifactId").text,
                         "version": dep.find("version").text})

    return dep_list

def extract_deps_from_jar(filepath):
    command = "jdeps --print-module-deps -R {}".format(filepath)
    output = run_cmd_command(command)

    if "Error: Missing dependencies:" not in output:
        command = "jdeps -R {}".format(filepath)
        output = run_cmd_command(command)

    buffer = io.StringIO(output)

    while buffer:


        buffer = buffer.readline()

    return output

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(len(sys.argv))
        print("Incorrect number of arguments\n")
        exit()

    target_dir = sys.argv[1]

    #header = ["class", "dependency", "origin"]
    header = ["package", "dependency", "origin"]
    output_filename = "dependencies.csv"

    file_types = ["/ai_app/", "/book_reader/", "/web_file_browser/", "/calculator/", 
                  "/emulator_environment/", "/graphic_editor/", "/dev_environment/", 
                  "/media_player/", "/terminal_interface/", "/text_editor/", "/text_voice_chat/"]

    init_output_csv(header, output_filename)

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file == "pom.xml":
                filepath = os.path.join(root, file).replace("\\", "/")
                project_name = os.path.basename(root)
                deps = extract_deps_from_pom(filepath)
                
                continue

            if file.endswith(".jar"):
                if "/src/" in root: continue

                filepath = os.path.join(root, file).replace("\\", "/")
                project_name = os.path.basename(root)
                filename = file.replace(".jar", "")

                output = extract_deps_from_jar(filepath)

                filetype = "/empty_filetype/"
                for typ in file_types:
                    if typ in filepath: 
                        filetype = typ
                        break
                continue

            output_filepath = "./output{0}{1}.txt".format(filetype, filename)
            os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
            with open(output_filepath, "w", encoding="UTF8", newline="") as f:
                f.write(str(output))

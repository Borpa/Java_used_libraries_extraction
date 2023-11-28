import os, sys, re, csv

if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print("Incorrect number of arguments\n")
    if len(sys.argv) == 2:
        mode = "w"
    else:
        mode = sys.argv[2]
    if mode not in ["w", "a"]:
        print("Incorrect argument\n")

    target_dir = sys.argv[1]

    data = {}
    
    csv_data = []

    header = ["filename", "type", "project", "imports", "uniques_libraries", "filepath"]

    if mode == "w":
        with open("imported_libraries.csv", "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)

    file_types = ["/ai_app/", "/book_reader/", "/browser/", "/calculator/", "/emulator/", 
                  "/graphic_editor/", "/ide/", "/media_player/", "/terminal/", "/text_editor/", "/text_voice_chat/"]

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".java"):
                filepath = os.path.join(root, file).replace("\\", "/")
                imports = []
                unique_libraries = []

                imported_libraries = ""
                with open(filepath, "r",  errors="replace") as f:
                    line = f.readline()
                    while line:
                        if "{" in line: break

                        if "import " in line and "=" not in line:
                            line = line.replace("import ", "").replace("static ", "")

                            line = line.replace(";\n", "")
                            imports.append(line)

                            classname_index = line.rfind(".")
                            library = line[:classname_index]

                            if library not in unique_libraries:
                                unique_libraries.append(library)

                        line = f.readline()

                for typ in file_types:
                    if typ in filepath:
                        typ = typ.replace("/", "") 
                        filetype = typ
                        break

                reg = r"({})[/]([_\d.\w-]+)[/]".format(filetype)
                project_name = re.search(reg, filepath).group()

                csv_data.append([file, filetype, project_name, imports, unique_libraries, filepath])

    with open("imported_libraries.csv", "a", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        for data in csv_data:
            writer.writerow(data)
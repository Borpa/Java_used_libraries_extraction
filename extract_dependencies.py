import os, sys, subprocess, csv

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(len(sys.argv))
        print("Incorrect number of arguments\n")
        exit()

    target_dir = sys.argv[1]

    #header = ["class", "dependency", "origin"]
    header = ["package", "dependency", "origin"]

    file_types = ["/ai_app/", "/book_reader/", "/web_file_browser/", "/calculator/", 
                  "/emulator_environment/", "/graphic_editor/", "/dev_environment/", 
                  "/media_player/", "/terminal_interface/", "/text_editor/", "/text_voice_chat/"]

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".jar"):
                filepath = os.path.join(root, file).replace("\\", "/")
                filename = file.replace(".jar", "")

                command = "jdeps --print-module-deps -R {}".format(filepath)
                #output = os.system(command)

                proc = subprocess.Popen(command, shell=True, 
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                out, err = proc.communicate()
                output = out.decode()

                filetype = "/empty_filetype/"
                for typ in file_types:
                    if typ in filepath: 
                        filetype = typ
                        break

                output_filepath = "./output{0}{1}.txt".format(filetype, filename)
                os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
                with open(output_filepath, "w", encoding="UTF8", newline="") as f:
                    f.write(str(output))

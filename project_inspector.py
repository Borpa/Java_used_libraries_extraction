import os

PROJECT_TYPES = [
    "/ai_app/",
    "/book_reader/",
    "/web_file_browser/",
    "/calculator/",
    "/emulator_environment/",
    "/graphic_editor/",
    "/dev_environment/",
    "/media_player/",
    "/terminal_app/",
    "/text_editor/",
    "/text_voice_chat/",
    "/ebook_manager/",
]

JAR_STOPWORDS = [
    "src",
    "lib",
    ".mvn",
    "dist",
    "gradle",
    "platform",
    "webcommon",
    "wrapper",
    "mediaplayer_lib",
    "plugins",
]


def get_full_jar_list(dir):
    jar_path_list = []

    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".jar"):
                stopword_flag = False
                for stopword in JAR_STOPWORDS:
                    if stopword in root:
                        stopword_flag = True
                        break
                if not stopword_flag:
                    filepath = os.path.join(root, file).replace("\\", "/")
                    jar_path_list.append(filepath)
    return jar_path_list


def get_project_name(filepath, project_types=PROJECT_TYPES):
    for project_type in project_types:
        if project_type in filepath:
            project_name_start = filepath.index(project_type) + len(project_type)
            project_name = filepath[project_name_start:]
            try:
                project_name_end = project_name.index("/")
                project_name = project_name[:project_name_end]
            except IndexError:
                project_name = project_name
            break
    return project_name


def get_project_list(main_dir, project_type):
    project_type = project_type.replace("/", "")
    full_path = main_dir + project_type
    return os.listdir(full_path)


def get_project_version_list(main_dir, project_name, project_type):
    project_type = project_type.replace("/", "")
    full_path = main_dir + project_type + "/" + project_name
    return os.listdir(full_path)


def get_project_ver(filepath, project_name):
    project_name = project_name + "/"
    project_ver_start = filepath.index(project_name) + len(project_name)
    project_ver = filepath[project_ver_start:]
    try:
        project_ver_end = project_ver.index("/")
        project_ver = project_ver[:project_ver_end]
    except IndexError:
        project_ver = project_ver
    return project_ver


def get_project_type(filepath, type_list=PROJECT_TYPES):
    """
    Get the type of the project from provided list of types.
    Returns "empty_project" if not found.

    Parameters:
    ----------

    filepath : str
        filepath to the project file

    type_list : list(str)
        list of possible project types

    """
    project_type = "/empty_type/"
    for typ in type_list:
        if typ in filepath:
            project_type = typ
            break
    return project_type


def get_projects_filelist(project_path, project_ver=None):
    if project_ver is not None:
        project_path = project_path + project_ver
    filelist = []
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith(".java"):
                filepath = os.path.join(root, file).replace("\\", "/")
                filelist.append(filepath)
    return filelist


def get_projects_path_list(target_dir):
    project_list = []
    dirs_flag = True
    for root, dirs, files in os.walk(target_dir):
        depth = root[len(target_dir) + len(os.path.sep) :].count(os.path.sep)
        if depth == 0:
            if dirs_flag:
                dirs_flag = False  # skip first entry that contains names of the directories from upper level
                continue
            for dir in dirs:
                project_path = os.path.join(root, dir).replace("\\", "/")
                project_list.append(project_path)
        if depth != 0:
            continue
    return project_list


def get_project_jar_list(main_dir, project_type, project_name, project_ver=""):
    project_type = project_type.replace("/", "")
    target_dir = main_dir + project_type + "/" + project_name + "/" + project_ver
    jar_list = []

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".jar"):
                stopword_flag = False
                for stopword in JAR_STOPWORDS:
                    if stopword in root:
                        stopword_flag = True
                        break
                if not stopword_flag:
                    filepath = os.path.join(root, file).replace("\\", "/")
                    jar_list.append(filepath)
    return jar_list


def get_project_types_list():
    return PROJECT_TYPES


def get_src_dir(project_file):
    file_dir = os.path.dirname(project_file)
    for dir in os.listdir(file_dir):
        if dir == "src":
            return file_dir + "/src"
    
    #check if src dir is in the parent dir
    file_dir = os.path.dirname(file_dir)
    for dir in os.listdir(file_dir):
        if dir == "src":
            return file_dir + "/src"

    return None
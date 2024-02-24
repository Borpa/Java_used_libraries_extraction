from multiprocessing import freeze_support

import run_pochi as pochi
from extract_project_dependencies import TESTED_SOFTWARE_DIR

def main():
    # run_pochi_for_similar_proj()

    # project1 = "FrankCYB_JavaGPT"
    # project1_type = "/ai_app/"
    # project1_ver = "v1.3.2"
    # project2 = "LiLittleCat_ChatGPT"
    # project2_type = "/ai_app/"
    # project2_ver = "v1.0.3"
    # output = run_pochi_for_pair(
    #    project1,
    #    project1_type,
    #    project2,
    #    project2_type,
    #    project1_version=project1_ver,
    #    project2_version=project2_ver,
    # )

    pochi.run_pochi_for_all(dir=TESTED_SOFTWARE_DIR, is_multiproc=True)
    # run_pochi_single_project("pH-7_Simple-Java-Calculator", "/calculator/")


if __name__ == "__main__":
    freeze_support()
    main()

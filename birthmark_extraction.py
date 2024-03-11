from multiprocessing import freeze_support

import gc
import run_pochi as pochi
import run_stigmata as stigmata
import time

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

    #pochi.run_pochi_for_all(dir=TESTED_SOFTWARE_DIR, is_multiproc=True)
    # run_pochi_single_project("pH-7_Simple-Java-Calculator", "/calculator/")

    # pochi.run_pochi_category_pair("/ai_app/", "/calculator/")

    gc.enable()

    #proj_types = ["/ebook_manager/", "/terminal_app/"]
    #proj_type = "/web_file_browser/"
    #for proj_type in proj_types:
    #pochi.run_pochi_single_category(proj_type, distinct_projects=True, is_multiproc=True)
    #pochi.run_pochi_single_category(proj_type, distinct_projects=False, is_multiproc=True)

    #file = "D:\\Study\phd_research\\test_projects\\calculator\\pH-7_Simple-Java-Calculator\\latest_20240206\\Simple-Java-Calculator-master\\SimpleJavaCalculator.jar"
    #output = pochi.pochi_extract_birthmark(file, "3-gram")
    #with open("test", mode="w") as f:
    #    f.write(str(output))



    #category = "/calculator/"
    #start = time.time()
    #pochi.run_pochi_single_category_script_output(category, True, True)
    #end = time.time()
    #print("{} distinct runtime: ".format(category), end - start)
    #
    #start = time.time()
    #pochi.run_pochi_single_category(category, True, True)
    #end = time.time()
    #print("{} distinct runtime for standard: ".format(category), end - start)

    category_list = ["/text_editor/", "/web_file_browser/", "/ai_app/", "/terminal_app/", "/ebook_manager/"]
    for category in category_list:
        start = time.time()
        try:
            pochi.run_pochi_single_category(category, True, True)
        except Exception as e:
            print(e)
        end = time.time()
        print("{} distinct runtime: ".format(category), end - start)
        start = time.time()
        try:
            pochi.run_pochi_single_category(category, False, True)
        except Exception as e:
            print(e)
        end = time.time()
        print("{} versions runtime: ".format(category), end - start)

if __name__ == "__main__":
    freeze_support()
    main()

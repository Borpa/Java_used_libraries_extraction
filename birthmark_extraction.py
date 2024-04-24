from multiprocessing import freeze_support

import gc
import run_pochi as pochi
import run_stigmata as stigmata
import time


def main():
    gc.enable()

    category_list = [
        "/calculator/",
        "/ai_app/",
        "/terminal_app/",
        "/emulator_environment/",
        "/text_editor/",
    ]
    birthmark_list = ["uc", "fuc", "3-gram", "6-gram"]
    for category in category_list:
        pochi.extract_birthmarks(birthmark_list, category)

    pochi.compare_external_birthmarks_distinct(category_list, birthmark_list)
    pochi.compare_external_birthmarks_versions(category_list, birthmark_list)
    
    #for category in category_list:
    #    start = time.time()
    #    try:
    #        pochi.run_pochi_single_category(category, True, False)
    #    except Exception as e:
    #        print(e)
    #    end = time.time()
    #    print("{} distinct runtime: ".format(category), end - start)
    #    start = time.time()
    #    try:
    #        pochi.run_pochi_single_category(category, False, False)
    #    except Exception as e:
    #        print(e)
    #    end = time.time()
    #    print("{} versions runtime: ".format(category), end - start)


if __name__ == "__main__":
    freeze_support()
    main()

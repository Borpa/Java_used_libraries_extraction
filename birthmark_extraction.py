from multiprocessing import freeze_support

import gc
import run_pochi as pochi
import run_stigmata as stigmata
import time


def main():
    gc.enable()

    category_list = [
        "/emulator_environment/",
        "/dev_environment/",
        "/ebook_manager/",
        "/graphic_editor/",
        "/media_player/",
        "/terminal_app/",
        "/web_file_browser/",
    ]
    for category in category_list:
        start = time.time()
        try:
            pochi.run_pochi_single_category(category, True, False)
        except Exception as e:
            print(e)
        end = time.time()
        print("{} distinct runtime: ".format(category), end - start)
        start = time.time()
        try:
            pochi.run_pochi_single_category(category, False, False)
        except Exception as e:
            print(e)
        end = time.time()
        print("{} versions runtime: ".format(category), end - start)


if __name__ == "__main__":
    freeze_support()
    main()

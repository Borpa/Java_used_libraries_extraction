from multiprocessing import freeze_support

import gc
import run_pochi as pochi


def main():
    gc.enable()

    pochi.run_pochi_single_category("/calculator/", False, False)
    pochi.run_pochi_single_category("/calculator/", True, False)

    pochi.run_pochi_single_category("/text_editor/", True, False)
    pochi.run_pochi_single_category("/text_editor/", False, False)

    pochi.run_pochi_single_category("/terminal_app/", True, False)
    pochi.run_pochi_single_category("/terminal_app/", False, False)

    pochi.run_pochi_single_category("/emulator_environment/", True, False)
    pochi.run_pochi_single_category("/emulator_environment/", False, False)

    pochi.run_pochi_single_category("/ai_app/", True, False)
    pochi.run_pochi_single_category("/ai_app/", False, False)


if __name__ == "__main__":
    freeze_support()
    main()

# main/main.py

from Logger_Dev0 import ao3_functions as ao3


def run():
    print("Starting the main application...\n")

    # Call functions from different modules
    print("Calling main_file's main function:")
    print(ao3.dummy_func(3))
    

if __name__ == "__main__":
    run()

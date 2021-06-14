from p9_tools import config
import os
from p9_tools.insertion import insertion


# construction of a hierarchy
def construct_hierarchy(csv_file=config.csv, file_path=config.path, definitions_path=config.definitions):
    for file_name in os.listdir(file_path):
        if file_name.endswith(".in"):
            insertion.main(csv_file, file_name, 1, file_path, definitions_path, hierarchy=True)


construct_hierarchy()

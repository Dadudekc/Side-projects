import os
import argparse
import json
import logging
from treelib import Tree

class DirectoryStructureCreator:
    def __init__(self, base_path, config_file=None, interactive=False, verbose=False):
        self.base_path = base_path
        self.config_file = config_file
        self.interactive = interactive
        self.verbose = verbose
        self.setup_logging()
        self.tree = Tree()
        self.tree.create_node("Project Root", self.base_path)  # root node

    def setup_logging(self):
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

    def create_project_structure(self, structure):
        for dir_path in structure:
            path = os.path.join(self.base_path, dir_path)
            try:
                os.makedirs(path, exist_ok=True)
                # Add node to the tree, parent is the base path unless specified
                self.tree.create_node(dir_path, path, parent=self.base_path)
                logging.info(f"Created directory: {path}")
            except Exception as e:
                logging.error(f"Failed to create {path}: {str(e)}")

    def show_directory_tree(self):
        self.tree.show()

    def load_structure(self):
        try:
            with open(self.config_file, 'r') as file:
                structure = json.load(file)
            return structure
        except FileNotFoundError:
            logging.error("Configuration file not found. Please provide a valid path.")
            exit(1)
        except json.JSONDecodeError:
            logging.error("Invalid JSON format. Please ensure the configuration file is correctly formatted.")
            exit(1)

    def interactive_setup(self):
        directories = []
        print("Enter directory paths (relative to the base path). Type 'done' to finish:")
        while True:
            directory = input("> ")
            if directory.lower() == 'done':
                break
            directories.append(directory)
        return directories

    def execute(self):
        if self.interactive:
            if not self.base_path:
                self.base_path = input("Enter the base path for the project structure: ")
            directories = self.interactive_setup()
        elif self.config_file:
            directories = self.load_structure()
        else:
            logging.error("No configuration file provided and not in interactive mode. Use -i for interactive setup or provide a config file.")
            exit(1)

        self.create_project_structure(directories)
        logging.info("Project structure created successfully!")
        self.show_directory_tree()

def parse_arguments():
    parser = argparse.ArgumentParser(description="Create a directory structure for any project based on a configuration file or interactive input.")
    parser.add_argument("base_path", nargs='?', type=str, help="The base path where the project structure should be created.")
    parser.add_argument("config_file", nargs='?', type=str, help="Path to the JSON configuration file that defines the directory structure.")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode to setup directory structure manually.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity for debugging purposes.")
    return parser.parse_args()

def main():
    args = parse_arguments()
    creator = DirectoryStructureCreator(args.base_path, args.config_file, args.interactive, args.verbose)
    creator.execute()

if __name__ == '__main__':
    main()

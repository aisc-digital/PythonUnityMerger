import os
import fnmatch

def search_for_string_in_files(root_dir, search_string):
    found_files = []

    for root, _, files in os.walk(root_dir):
        for filename in fnmatch.filter(files, '*.meta'):
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    contents = file.read()
                    if search_string in contents:
                        found_files.append(file_path)
            except IOError:
                pass

    return found_files

if __name__ == "__main__":
    search_dir = input("Enter the directory to start the search: ")
    search_string = input("Enter the string to search for: ")

    found_files = search_for_string_in_files(search_dir, search_string)

    if found_files:
        print("Files containing the string:")
        for file_path in found_files:
            print(file_path)
    else:
        print("No files containing the string found.")
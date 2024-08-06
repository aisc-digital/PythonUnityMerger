#   _____  _    __
# ,´     \/ \ _`,    Author: Christian Grund
# |  C/  /  / __     Company: AISC GmbH
#  \_/__/__/ /_      mailto: cg@aisc.digital
#

from copy import copy
from difflib import Differ

import yaml, os, fnmatch

from UnityMerger.UnityYamlTools import UnityYamlTools
from unityData.unityFileBlock import UnityFileBlock


class Listmerger:
    def __init__(self, project):
        self.project = project
    @staticmethod
    def highlight_string_at_idxs(string, indexes):
        # hl = "\x1b[38;5;160m"  # 8-bit
        hl = "\x1b[91m"
        reset = "\x1b[0m"
        words_with_hl = []
        for string_idx, word in enumerate(string.split(" ")):
            if string_idx in indexes:
                words_with_hl.append(hl + word + reset)
            else:
                words_with_hl.append(word)
        return " ".join(words_with_hl)

    # Return indexes of the additions to s2 compared to s1
    @staticmethod
    def get_indexes_of_additions(s1, s2):
        diffs = list(Differ().compare(s1.split(" "), s2.split(" ")))
        indexes = []
        adj_idx = 0  # Adjust index to compensate for removed words
        for diff_idx, diff in enumerate(diffs):
            if diff[:1] == "+":
                indexes.append(diff_idx - adj_idx)
            elif diff[:1] == "-":
                adj_idx += 1
        return indexes


    @staticmethod
    def display_in_columns(left_text, right_text):
        left_lines = left_text.split('\n')
        right_lines = right_text.split('\n')

        max_width_left = max(len(line) for line in left_lines)
        max_width_right = max(len(line) for line in right_lines)

        for left_line, right_line in zip(left_lines, right_lines):
            left_padding = ' ' * (max_width_left - len(left_line.replace("\x1b[91m","").replace("\x1b[0m","")))
            right_padding = ' ' * (max_width_right - len(right_line.replace("\x1b[91m","").replace("\x1b[0m","")))

            print(f"{left_line}{left_padding}  {right_line}{right_padding}")

    @staticmethod
    def yesno(text) -> bool:
        choice = None
        while(choice != "y" and choice != "n"):
            choice = input(text + " [y/n]").strip().lower()
        return choice == "y"

    @staticmethod
    def ab(text) -> bool:
        choice = None
        while(choice != "a" and choice != "b"):
            choice = input(text + " [a/b]").strip().lower()
        return choice == "a"

    @staticmethod
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


    def recursiveMerge(self, objM, objT, path):
        if (objM == objT):
            return objM
        if type(objM) == type(objT) and type(objM) == dict:
            return self.mergeDict(objM, objT, path)
        elif type(objM) == type(objT) and type(objM) == list:
            return self.mergeList(objM, objT, path)
        else:
            return self.mergeOther(objM, objT, path)


    def loadObject(self, id, dict):
        datablockM = {k:v for k,v in dict.items() if str(id) in k}
        firstItem = list(datablockM.values())[0]
        firstItem = firstItem[firstItem.find("\n")+1:]
        return yaml.load(firstItem, yaml.Loader)
    def getPathNameFromDictKey(self,k:str, obj):
        return k
    def mergeDict(self, objM, objT, path):
        out = dict()
        for k in objM.keys():
            if not (k in objT.keys()):
                print(objM[k])
                if(self.yesno(path + "/" + k + " is in MINE but not in THEIRS. Do you wanna keep it?")):
                    out[k] = objM[k]
        for k in objT.keys():
            if not (k in objM.keys()):
                print(objT[k])
                if(self.yesno(path + "/" + k + " is in THEIRS but not in MINE. Do you wanna keep it?")):
                    out[k] = objT[k]
        for k in objM.keys():
            if (k in objT.keys()):
                out[k] = self.recursiveMerge(objM[k], objT[k], path + "/" + self.getPathNameFromDictKey(k, objM[k]))
        return out


    def mergeList(self, objM, objT, path):
        setA = set([str(a) for a in objM])
        setB = set([str(a) for a in objT])
        if (setA == setB):
            UnityYamlTools.VisualizeHierarchyPath(path)
            if(Listmerger.ab(path + " has a different *ordering* in [a]MINE and in [b]THERIS. Which *ordering* do you wanna keep?")):
                return objM
            else:
                return objT

        out = list()
        for item in objM:
            if item in objT:
                out.append(item)
        for item in objM:
            if not (item in objT):
                print(item)
                if(Listmerger.yesno("The above in " + path + " is in MINE but not in THEIRS. Do you wanna keep it?")):
                    out.append(item)
        for item in objT:
            if not (item in objM):
                print(item)
                if(Listmerger.yesno("The above in " + path + " is in THEIRS but not in MINE. Do you wanna keep it?")):
                    out.append(item)
        return out

    def mergeOther(this, objM, objT, path):
        printM = str(objM)
        printT = str(objT)

        addition_idxs_M = Listmerger.get_indexes_of_additions(printT, printM)
        hl_M = Listmerger.highlight_string_at_idxs(printM, addition_idxs_M)

        addition_idxs_T = Listmerger.get_indexes_of_additions(printM, printT)
        hl_T = Listmerger.highlight_string_at_idxs(printT, addition_idxs_T)

        Listmerger.display_in_columns(f"Value in dictionary MINE:\n {hl_M}", f"Value in dictionary THERIS:\n {hl_T}")
        print("Path: " + path)
        if(Listmerger.ab("Enter 'A' to keep value from MINE, 'B' to keep value from THEIRS: ")):
            return objM
        else:
            return objT


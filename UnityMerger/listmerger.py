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


class listmerger:
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


    def __init__(self):
        pass

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


    def recursiveMerge(self, objA, objB, path):
        if (objA == objB):
            return objA
        if type(objA) == type(objB) and type(objA) == dict:
            return self.mergeDict(objA, objB, path)
        elif type(objA) == type(objB) and type(objA) == list:
            return self.mergeList(objA, objB, path)
        else:
            return self.mergeOther(objA, objB, path)


    def loadObject(self, id, dict):
        datablockA = {k:v for k,v in dict.items() if str(id) in k}
        firstItem = list(datablockA.values())[0]
        firstItem = firstItem[firstItem.find("\n")+1:]
        return yaml.load(firstItem, yaml.Loader)
    def getPathNameFromDictKey(self,k:str, obj):
        return k
    def mergeDict(self,objA, objB, path):
        out = dict()
        for k in objA.keys():
            if not (k in objB.keys()):
                print(objA[k])
                if(self.yesno(path + "/" + k + " is in A but not in B. Do you wanna keep it?")):
                    out[k] = objA[k]
        for k in objB.keys():
            if not (k in objA.keys()):
                print(objB[k])
                if(self.yesno(path + "/" + k + " is in B but not in A. Do you wanna keep it?")):
                    out[k] = objB[k]
        for k in objA.keys():
            if (k in objB.keys()):
                out[k] = self.recursiveMerge(objA[k], objB[k], path + "/" + self.getPathNameFromDictKey(k, objA[k]))
        return out


    def mergeList(self,objA, objB, path):
        setA = set([str(a) for a in objA])
        setB = set([str(a) for a in objB])
        if (setA == setB):
            if(listmerger.ab(path + " has a different ordering in A and in B. Which ordering do you wanna keep?")):
                return objA
            else:
                return objB

        out = list()
        for item in objA:
            if item in objB:
                out.append(item)
        for item in objA:
            if not (item in objB):
                print(item)
                if(listmerger.yesno("The above in "+ path +" is in A but not in B. Do you wanna keep it?")):
                    out.append(item)
        for item in objB:
            if not (item in objA):
                print(item)
                if(listmerger.yesno("The above in "+ path +" is in B but not in A. Do you wanna keep it?")):
                    out.append(item)
        return out

    def mergeOther(this,objA,objB,path):
        printA = str(objA)
        printB = str(objB)

        addition_idxs_A = listmerger.get_indexes_of_additions(printB, printA)
        hl_A = listmerger.highlight_string_at_idxs(printA, addition_idxs_A)

        addition_idxs_B = listmerger.get_indexes_of_additions(printA, printB)
        hl_B = listmerger.highlight_string_at_idxs(printB, addition_idxs_B)

        listmerger.display_in_columns(f"Value in dictionary A:\n {hl_A}", f"Value in dictionary B:\n {hl_B}")
        print("Path: " + path)
        if(listmerger.ab("Enter 'A' to keep value from A, 'B' to keep value from B: ")):
            return objA
        else:
            return objB


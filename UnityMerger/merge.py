import base64
import copy
import random
import re
import shutil
import sys
from io import StringIO
from typing import List

import yaml
from collections import OrderedDict
from difflib import Differ
from time import strftime, gmtime

from UnityMerger.listmerger import listmerger
from unityData.unityFile import UnityFile
from unityData.unityFileBlock import UnityFileBlock
from unityData.unityProject import UnityProject


class Merge:
    @staticmethod
    def extract_mine_and_theirs(file_path) -> (str, str):
        mine_lines = []
        theirs_lines = []

        section = None

        with open(file_path, 'r') as conflict_file:
            for line in conflict_file:
                if line.startswith('<<<<<<<'):
                    section = 'mine'
                    continue
                elif line.startswith('======='):
                    section = 'theirs'
                    continue
                elif line.startswith('>>>>>>>'):
                    section = None
                    continue


                if section == 'mine':
                    mine_lines.append(line)
                elif section == 'theirs':
                    theirs_lines.append(line)
                else:
                    mine_lines.append(line)
                    theirs_lines.append(line)

        mine_content = ''.join(mine_lines)
        theirs_content = ''.join(theirs_lines)

        return mine_content, theirs_content

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
    def handleMergeConflict(value_a:UnityFileBlock, value_b:UnityFileBlock):
        print("")
        print("#####################################")
        print(f"Conflict for \n{value_a.hierarchyPath}\n{value_b.hierarchyPath}:")

        if value_a.blocktype == value_b.blocktype and value_a.blocktype == "PrefabInstance":
            lmr = listmerger()
            a_without_mod = copy.deepcopy(value_a.object)
            b_without_mod = copy.deepcopy(value_a.object)

            a_without_mod["PrefabInstance"]["m_Modification"]["m_Modifications"] = list()
            b_without_mod["PrefabInstance"]["m_Modification"]["m_Modifications"] = list()

            NewYaml = lmr.recursiveMerge(a_without_mod,b_without_mod, "")

            #modifications:
            mod_a = copy.deepcopy(value_a["m_Modification.m_Modifications"])
            mod_b = copy.deepcopy(value_b["m_Modification.m_Modifications"])
            mod_out = list()

            dict_a = {str(x["target"])+str(x["propertyPath"]) : x for x in mod_a}
            dict_b = {str(x["target"])+str(x["propertyPath"]) : x for x in mod_b}

            for ka,va in dict_a.items():

                path = value_a.hierarchyPath + "//" + value_a.searchReferencePath(va["target"]["guid"],va["target"]["fileID"])
                ref = value_a.searchReference(va["target"]["guid"],va["target"]["fileID"])
                refobj = value_a.project.getReferenceFromGUID(ref["guid"]).blocks[ref["fileID"]]

                if ka in dict_b:
                    vb = dict_b[ka]
                    if va == vb:
                        mod_out.append(va)
                    else:
                        print("#####")
                        listmerger.display_in_columns("Value in A:\n" + str(va["value"]) + "\n" + str(va["objectReference"]) , f"Value in B:\n" + str(vb["value"]) + "\n" + str(vb["objectReference"]) + "\n")
                        print("Property: [" + refobj.blocktype + "]"+ va["propertyPath"])
                        print("Path: "+path)
                        print()
                        if(listmerger.ab("Values for A and B differ: which one do you wanna keep")):
                            mod_out.append(va)
                        else:
                            mod_out.append(vb)
                else:
                    print("#####")
                    print("Property: [" + refobj.blocktype + "]" + va["propertyPath"])
                    print("Path: "+path)
                    print(va)
                    if(listmerger.yesno(f"modification for {path} is in A but not in B. Do you wanna keep it?")):
                        mod_out.append(va)

            for kb,vb in dict_b.items():

                path = value_b.hierarchyPath + "//" + value_b.searchReferencePath(vb["target"]["guid"],vb["target"]["fileID"])
                ref = value_b.searchReference(vb["target"]["guid"],vb["target"]["fileID"])
                refobj = value_b.project.getReferenceFromGUID(ref["guid"]).blocks[ref["fileID"]]

                if kb in dict_a:
                        continue # already handled above
                else:
                    print("#####")
                    print("Property: [" + refobj.blocktype + "]" + vb["propertyPath"])
                    print("Path: "+path)
                    print(vb)
                    if(listmerger.yesno(f"modification for {path} is in A but not in B. Do you wanna keep it?")):
                        mod_out.append(vb)

            NewYaml["PrefabInstance"]["m_Modification"]["m_Modifications"] = mod_out
        else:
            lmr = listmerger()
            NewYaml = lmr.recursiveMerge(value_a.object,value_b.object, "");
        yamlstring = StringIO()

        yaml.safe_dump(NewYaml,yamlstring,sort_keys=False, default_flow_style=None, default_style="")
        yamlstring.seek(0)
        retval = yamlstring.read()
        yamlstring.close()
        headline = value_a.block.split("\n",1)[0]
        ufb = UnityFileBlock(value_a.project,None,value_a.uid,headline + "\n" + retval)
        return ufb

    @staticmethod
    def merge_UnityFiles(mineFile,theirsFile) -> List[UnityFileBlock]:
        mergedBlocks:List[UnityFileBlock] = list()

        mineKeys = set(mineFile.blocks.keys())
        theirsKeys = set(theirsFile.blocks.keys())

        onlyMineKeys = mineKeys.difference(theirsKeys)
        onlyTheirsKeys = theirsKeys.difference(mineKeys)
        bothKeys = mineKeys.intersection(theirsKeys)

        mergedBlocks.extend([mineFile.blocks[k] for k in onlyMineKeys])
        mergedBlocks.extend([theirsFile.blocks[k] for k in onlyTheirsKeys])

        for key in bothKeys:
            mineBlock:UnityFileBlock = mineFile.blocks[key]
            theirsBlock:UnityFileBlock = theirsFile.blocks[key]

            if mineBlock.block == theirsBlock.block:
                mergedBlocks.append(mineBlock)
            else:
                m = Merge.handleMergeConflict(mineBlock, theirsBlock)
                mergedBlocks.append(m)
        return mergedBlocks

    # Return string with the escape sequences at specific indexes to highlight
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
    def createMineTheirsFiles(conflict_file_path):
        mine_content, theirs_content = Merge.extract_mine_and_theirs(conflict_file_path)

        with open(conflict_file_path + ".meta") as meta:
            metacontent = meta.read()

        with open(conflict_file_path + "_MINE", "w") as mf:
            mf.write(mine_content)
        with open(conflict_file_path + "_THEIRS", "w") as tf:
            tf.write(theirs_content)

        mineGUID = base64.b16encode(random.getrandbits(128).to_bytes(16, byteorder='little')).decode().lower()
        theirsGUID = base64.b16encode(random.getrandbits(128).to_bytes(16, byteorder='little')).decode().lower()

        with open(conflict_file_path + "_MINE.meta", "w") as mf:
            mf.write(re.sub(r'guid: [0-9a-f]+', f'guid: {mineGUID}',metacontent))
        with open(conflict_file_path + "_THEIRS.meta", "w") as tf:
            tf.write(re.sub(r'guid: [0-9a-f]+', f'guid: {theirsGUID}',metacontent))

        return mineGUID, theirsGUID

if __name__ == "__main__":
    pass
'''
    from UnityYamlTools import UnityYamlTools
    if len(sys.argv) != 3:
        print("Usage: python merge_conflict_parser.py <file_path> <project_config>")
        sys.exit(1)

    conflict_file_path = sys.argv[1]
    projectConfig = sys.argv[2]

    project = UnityProject(projectConfig)
    mineGUID, theirsGUID = Merge.createMineTheirsFiles(conflict_file_path)

    mineFile = project.getReferenceFromGUID(mineGUID)
    theirFile = project.getReferenceFromGUID(theirsGUID)

    #merged = Merge.merge_dicts(mine_blocks, theirs_blocks)
    Merge.merge_UnityFiles(mineFile,theirFile)

    shutil.move(conflict_file_path, conflict_file_path + "_" + strftime("%Y%m%d_%H%M%S", gmtime()))

    f = open(conflict_file_path + "_tmp", "w")
    data = merged[""]

    merged.pop("");

    for k,v in sorted(merged.items(),key=lambda a:int(a[0].split(" ")[2].replace("&",""))):
        if k == "":
            continue
        data += v
    f.write(data)
    f.close()

    shutil.move(conflict_file_path + "_tmp", conflict_file_path)

    print("Mine content:")
    print(mine_content)

    print("\nTheirs content:")
    print(theirs_content)
'''
#   _____  _    __
# ,´     \/ \ _`,    Author: Christian Grund
# |  C/  /  / __     Company: AISC GmbH
#  \_/__/__/ /_      mailto: cg@aisc.digital
#

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

from UnityMerger.MonoBehaviourMerger import MonoBehaviourMerger
from UnityMerger.TransformMerger import TransformMerger
from UnityMerger.UnityYamlTools import UnityYamlTools
from UnityMerger.listmerger import Listmerger
from UnityMerger.prefabmerger import PrefabMerger
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
    def handleMergeConflict(value_m:UnityFileBlock, value_t:UnityFileBlock):
        print("")
        print("#####################################")
        print("Conflict for")

        UnityYamlTools.VisualizeHierarchyPath(value_m.hierarchyPath)
        if value_m.hierarchyPath != value_t.hierarchyPath:
            print("-> Path in B")
            UnityYamlTools.VisualizeHierarchyPath(value_t.hierarchyPath)

        if value_m.blocktype == value_t.blocktype and value_m.blocktype == "PrefabInstance":
            pm = PrefabMerger(value_m, value_t)
            NewYaml = pm.mergePrefab()
        elif value_m.blocktype == value_t.blocktype and value_m.blocktype == "MonoBehaviour":
            mbm = MonoBehaviourMerger(value_m, value_t)
            NewYaml = mbm.merge()
        elif value_m.blocktype == value_t.blocktype and value_m.blocktype == "Transform":
            tm = TransformMerger(value_m, value_t)
            NewYaml = tm.merge()
        else:
            lmr = Listmerger(value_m.project)
            NewYaml = lmr.recursiveMerge(value_m.object, value_t.object, "");
        yamlstring = StringIO()

        yaml.safe_dump(NewYaml,yamlstring,sort_keys=False, default_flow_style=None, default_style="")
        yamlstring.seek(0)
        retval = yamlstring.read()
        yamlstring.close()
        headline = value_m.block.split("\n", 1)[0]
        ufb = UnityFileBlock(value_m.project, None, value_m.uid, headline + "\n" + retval)
        return ufb

    @staticmethod
    def merge_UnityFiles(mineFile,theirsFile) -> List[UnityFileBlock]:
        mergedBlocks:List[UnityFileBlock] = list()

        # Generate lists of all block IDs
        mineKeys = set(mineFile.blocks.keys())
        theirsKeys = set(theirsFile.blocks.keys())

        # Generate lists of differing blocks
        onlyMineKeys = mineKeys.difference(theirsKeys)
        onlyTheirsKeys = theirsKeys.difference(mineKeys)
        bothKeys = mineKeys.intersection(theirsKeys)

        # Blocks which do only appear in one of both are merged directly.
        mergedBlocks.extend([mineFile.blocks[k] for k in onlyMineKeys])
        mergedBlocks.extend([theirsFile.blocks[k] for k in onlyTheirsKeys])

        # Blocks which are in both, need to be compared and merged
        for key in bothKeys:
            mineBlock:UnityFileBlock = mineFile.blocks[key]
            theirsBlock:UnityFileBlock = theirsFile.blocks[key]

            if mineBlock.block == theirsBlock.block:
                # equal blocks
                mergedBlocks.append(mineBlock)
            else:
                # unequal blocks -> MERGE CONFLICT
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

        cfp_split = conflict_file_path.rsplit('.',1)
        mineFileName = cfp_split[0] + "_MINE." + cfp_split[1]
        theirsFileName = cfp_split[0] + "_THEIRS." + cfp_split[1]

        with open(mineFileName, "w") as mf:
            mf.write(mine_content)
        with open(theirsFileName, "w") as tf:
            tf.write(theirs_content)

        #to create valid Unity Files, we add meta files with random GUIDs. This enables us to open MINE and THERIS in Unity
        mineGUID = base64.b16encode(random.getrandbits(128).to_bytes(16, byteorder='little')).decode().lower()
        theirsGUID = base64.b16encode(random.getrandbits(128).to_bytes(16, byteorder='little')).decode().lower()

        with open(mineFileName + ".meta", "w") as mf:
            mf.write(re.sub(r'guid: [0-9a-f]+', f'guid: {mineGUID}',metacontent))
        with open(theirsFileName + ".meta", "w") as tf:
            tf.write(re.sub(r'guid: [0-9a-f]+', f'guid: {theirsGUID}',metacontent))

        return mineGUID, theirsGUID, mineFileName, theirsFileName

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
#
#   @ author: Christian Grund, AISC GmbH
#   @ mailto: cg@aisc.digital
#
import re
from typing import List

from unityData import unityFileBlock
from unityData.unityFileBlock import UnityFileBlock

META_GUID_REGEX = re.compile("^guid: ([0-9a-f]*)$")


class UnityFile:
    def __init__(self, project, guid:str, fileName:str):
        self.guid = guid
        self._blocks: List[UnityFileBlock] = None
        self.project = project
        if fileName.endswith(".meta"):
            self.metaFilePath = fileName
            self.fileName = fileName[:-5]
        else:
            self.metaFilePath = fileName + ".meta"
            self.fileName = fileName
    @property
    def blocks(self) -> dict[int,unityFileBlock]:
        if self._blocks == None:
            self._blocks = dict()
            with open(self.fileName) as file:
                content = file.read()
            text_blocks, line_numbers = self._split_into_text_blocks(content)
            for k,v in text_blocks.items():
                if v == None or v == "" or v.startswith("%YAML "):
                    continue
                self._blocks[int(k)] = UnityFileBlock(self.project, self, int(k),v)
        return self._blocks

    def _split_into_text_blocks(self, multiline_string: str):
        text_blocks = {"": ""}
        line_numbers = [(0, None), ]
        lines = multiline_string.split('\n')
        current_key = ""
        lineNumber = -1
        current_block = []

        blockBeginningPattern = re.compile(r"^--- !u![0-9]+ &(\d+)")

        for line in lines:
            lineNumber += 1
            match = blockBeginningPattern.match(line)
            if match:
                current_key = match.group(1)
                if current_key in text_blocks:
                    print("WARNING: " + current_key + " already exists!")
                text_blocks[current_key] = ""
                line_numbers += (lineNumber, current_key)
            text_blocks[current_key] += line + "\n"
        return text_blocks, line_numbers



    @staticmethod
    def fromFile(project, fileName) -> "UnityFile":
        with open(fileName, 'r') as file:
            for line in file:
                match = META_GUID_REGEX.match(line)
                if match:
                    return UnityFile(project, match.group(1), fileName)


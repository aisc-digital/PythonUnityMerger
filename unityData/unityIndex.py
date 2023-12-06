#
#   @ author: Christian Grund, AISC GmbH
#   @ mailto: cg@aisc.digital
#

import glob
import os
import re
from typing import Dict



from unityData.unityFile import UnityFile

class UnityIndex:
    def __init__(self, projectConfig:"UnityProject"):
        self.project: "UnityProject" = projectConfig
        self.index: Dict[str, UnityFile] = dict()
        self.reindex()


    def getReferenceFromGUID(self, guid: str) -> UnityFile:
        if guid in self.index:
            return self.index[guid]
        else:
            return None

    def getReferenceFromPath(self, path:str) -> UnityFile:
        if not path.endswith(".meta"):
            path += ".meta"
        nonIndexedReference = UnityFile.fromFile(self.project, path)
        ref = self.getReferenceFromGUID(nonIndexedReference.guid);
        if ref == None or ref.metaFilePath != path:
            self.reindex()
            ref = self.getReferenceFromGUID(nonIndexedReference.guid);
        return ref

    def reindex(self):
        search_pattern = os.path.join(self.project.AssetFolder, f'**/*.meta')
        found_files = glob.glob(search_pattern, recursive=True)

        search_pattern = os.path.join(self.project.PackagesFolder, f'**/*.meta')
        found_files += glob.glob(search_pattern, recursive=True)

        search_pattern = os.path.join(self.project.LibraryFolder, f'**/*.meta')
        found_files += glob.glob(search_pattern, recursive=True)
        for file in found_files:
            unityReference = UnityFile.fromFile(self.project, file)
            self.index[unityReference.guid] = unityReference

if __name__ == "__main__":
    import sys
    from unityData.unityProject import UnityProject

    conf = UnityProject.createNewConfig(sys.argv[1])
    ui = UnityIndex(UnityProject(conf))
    ui.reindex()
    for k,v in ui.index.items():
        print(k,v.filePath)
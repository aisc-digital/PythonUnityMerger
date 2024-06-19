#   _____  _    __
# ,´     \/ \ _`,    Author: Christian Grund
# |  C/  /  / __     Company: AISC GmbH
#  \_/__/__/ /_      mailto: cg@aisc.digital
#
import os
import pathlib
import shutil
from configparser import ConfigParser
from typing import List

from UnityMerger.listmerger import listmerger
from UnityMerger.merge import Merge
from unityData.unityFileBlock import UnityFileBlock
from unityData.unityProject import UnityProject


class MergeUnityFile:
    def __init__(self, projectconf, file):
        self.projectconf = projectconf
        self.file = file

        if os.path.isdir(projectconf):
            if os.path.exists(os.path.join(projectconf,"UnityToolPackConfig.cfg")):
                self.projectconf = os.path.join(projectconf,"UnityToolPackConfig.cfg")
            else:
                if(os.path.exists(os.path.join(projectconf,"Assets")) and os.path.exists(os.path.join(projectconf,"Packages")) and os.path.exists(os.path.join(projectconf,"Library"))):
                    config = ConfigParser()
                    config['PATHS'] = {
                        'assetfolder': 'Assets',
                        'libraryfolder': 'Library',
                        'packagesfolder': 'Packages'
                    }
                    # Write the configuration to a file
                    with open(os.path.join(projectconf,"UnityToolPackConfig.cfg"), 'w') as configfile:
                        config.write(configfile)
                    self.projectconf = os.path.join(projectconf,"UnityToolPackConfig.cfg")
                else:
                    print("The folder does not seem to be a Unity Project")
                    raise FileNotFoundError;

    def resolveInteractive(self):
        mineGUID, theirsGUID, mineFileName, theirsFilename = Merge.createMineTheirsFiles(self.file)
        project = UnityProject(self.projectconf)
        mineFile = project.getReferenceFromGUID(mineGUID)
        theirFile = project.getReferenceFromGUID(theirsGUID)

        #merged = Merge.merge_dicts(mine_blocks, theirs_blocks)
        mergedBlocks:List[UnityFileBlock] = Merge.merge_UnityFiles(mineFile,theirFile)
        mergedBlocks.sort(key=lambda x:x.uid)
        outText = "".join([b.block for b in mergedBlocks])
        with open(self.file + "_merged", "w") as merged:
            with open(mineFile.fileName) as mine:
                for line in mine:
                    if line.startswith("%"):
                        merged.write(line)
                    else:
                        break
                merged.write(outText)
        print("##################################")
        print("+++ Merge Finished +++")

        if(listmerger.yesno("Do you want to overwrite " + self.file + " now?")):
            shutil.move(self.file + "_merged", self.file)
        todelete = [mineFileName, mineFileName + ".meta", theirsFilename, theirsFilename + ".meta"]
        print("\n")
        if(listmerger.yesno("Do you want to delete the following files now?\n" + "\n".join(todelete))):
            for f in todelete:
                pathlib.Path.unlink(f)
        pass
if __name__ == "__main__":
    import sys

    print("""                                         
    _____  _    __   AISC Unity Tool Pack
  ,´     \/ \ _`,    Merge Tool
  |  C/  /  / __     
   \_/__/__/ /_      by Christian Grund, AISC GmbH

#####################################################
""")

    if(len(sys.argv != 3)):
        print("""
 Usage:        
   using ProjectConfigFile:
     mergeUnityFile.py [ProjectConfig] [FileWithMergeConflicts]
    
   using Directory
     mergeUnityFile.py [UnityProjectPath] [FileWithMergeConflicts]
     note: this will automatically generate a config file UnityToolPackConfig.cfg in your Unity Project Directory 
""")

    muf = MergeUnityFile(sys.argv[1], sys.argv[2])
    muf.resolveInteractive()
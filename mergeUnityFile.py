#
#   @ author: Christian Grund, AISC GmbH
#   @ mailto: cg@aisc.digital
#
import pathlib
import shutil
from typing import List

from UnityMerger.listmerger import listmerger
from UnityMerger.merge import Merge
from unityData.unityFileBlock import UnityFileBlock
from unityData.unityProject import UnityProject


class MergeUnityFile:
    def __init__(self, projectconf, file):
        self.projectconf = projectconf
        self.file = file

    def resolveInteractive(self):
        mineGUID, theirsGUID = Merge.createMineTheirsFiles(self.file)
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
        todelete = [self.file + "_MINE", self.file + "_MINE.meta", self.file + "_THEIRS", self.file + "_THEIRS.meta"]
        print("\n")
        if(listmerger.yesno("Do you want to delete the following files now?\n" + "\n".join(todelete))):
            for f in todelete:
                pathlib.Path.unlink(f)
        pass
if __name__ == "__main__":
    import sys
    muf = MergeUnityFile(sys.argv[1], sys.argv[2])
    muf.resolveInteractive()
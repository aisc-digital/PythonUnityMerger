#
#   @ author: Christian Grund, AISC GmbH
#   @ mailto: cg@aisc.digital
#
from typing import List

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
        pass
if __name__ == "__main__":
    import sys
    muf = MergeUnityFile(sys.argv[1], sys.argv[2])
    muf.resolveInteractive()
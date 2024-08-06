import os.path

from UnityMerger.UnityYamlTools import UnityYamlTools
from UnityMerger.listmerger import Listmerger


class MonoBehaviourMerger:
    @staticmethod
    def PrintMBHeader(basename:str):
        UnityYamlTools.printTabbar("MonoBehaviour")
        print ( u" \u25bc \u2338    " + basename + " " * (60-len(basename)-14) +u"\u23FA \u2253 \u22EE \n")

    def __init__(self, value_a, value_b):
        self.value_a = value_a
        self.value_b = value_b
        self.mb_a = value_a.object["MonoBehaviour"]
        self.mb_b = value_b.object["MonoBehaviour"]
        self.script_a = self.mb_a["m_Script"]
        self.script_b = self.mb_b["m_Script"]
        self.mbPath_a = self.value_a.project.getReferenceFromGUID(self.script_a["guid"]).fileName
        self.mbPath_b = self.value_a.project.getReferenceFromGUID(self.script_b["guid"]).fileName
    def merge(self):
        lmr = Listmerger(self.value_a.project)
        out = dict()
        k = "MonoBehaviour"
        basename = self.mbPath_a.split("/")[-1]
        MonoBehaviourMerger.PrintMBHeader(basename)
        out[k] = lmr.recursiveMerge(self.mb_a, self.mb_b,"")
        print ("MonoBehaviour merged.")
        return out

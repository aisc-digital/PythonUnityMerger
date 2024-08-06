import os.path

from UnityMerger.UnityYamlTools import UnityYamlTools
from UnityMerger.listmerger import Listmerger


class TransformMerger:
    def __init__(self, value_a, value_b):
        self.value_a = value_a
        self.value_b = value_b
        self.t_a = value_a.object["Transform"]
        self.t_b = value_b.object["Transform"]
        self.lmr = Listmerger(self.value_a.project)

    def merge(self):
        out = dict()
        basename = "Transform"
        UnityYamlTools.printTabbar("Transform")
        print ( u" \u25bc \u22B9    " + basename + " " * (60-len(basename)-14) +u"\u23FA \u2253 \u22EE \n")
        out["Transform"] = self.mergeDict(self.t_a,self.t_b, "")
        print ("MonoBehaviour merged.")
        return out


    def mergeDict(self, objM, objT, path):
        out = dict()
        for k in objM.keys():
            if not (k in objT.keys()):
                print("UNEXPECTED BEHAVIOUR: Different Keys in Transform. Adding new key...")
                out[k] = objM[k]
        for k in objT.keys():
            if not (k in objM.keys()):
                print("UNEXPECTED BEHAVIOUR: Different Keys in Transform. Adding new key...")
                out[k] = objT[k]
        for k in objM.keys():
            if (k in objT.keys()):
                out[k] = self.mergeTransformEntity(objM[k], objT[k], k)
        return out

    def mergeTransformEntity(self, a, b, key):
        if(a==b):
            return a
        if key == "m_Children":
            return self.lmr.mergeList(a,b,key)
        return self.lmr.mergeOther(a,b,key)

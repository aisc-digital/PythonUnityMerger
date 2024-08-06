import copy

from UnityMerger.MonoBehaviourMerger import MonoBehaviourMerger
from UnityMerger.UnityYamlTools import UnityYamlTools
from UnityMerger.listmerger import Listmerger
from unityData.unityProject import UnityProject


class PrefabMerger:
    def __init__(self, value_m, value_t):
        self.project = value_m.project
        self.value_m = value_m
        self.value_t = value_t
        self.listmerger = Listmerger(self.project)
    def mergePrefab(self):
        a_without_mod = copy.deepcopy(self.value_m.object)
        b_without_mod = copy.deepcopy(self.value_m.object)

        a_without_mod["PrefabInstance"]["m_Modification"]["m_Modifications"] = list()
        b_without_mod["PrefabInstance"]["m_Modification"]["m_Modifications"] = list()

        NewYaml = self.listmerger.recursiveMerge(a_without_mod,b_without_mod, "")

        #modifications:
        mod_m = copy.deepcopy(self.value_m["m_Modification.m_Modifications"])
        mod_t = copy.deepcopy(self.value_t["m_Modification.m_Modifications"])
        mod_out = list()

        dict_m = {str(x["target"])+str(x["propertyPath"]) : x for x in mod_m}
        dict_t = {str(x["target"])+str(x["propertyPath"]) : x for x in mod_t}

        for km,vm in dict_m.items():

            path = self.value_m.hierarchyPath + "/" + self.value_m.searchReferencePath(vm["target"]["guid"], vm["target"]["fileID"])
            ref = self.value_m.searchReference(vm["target"]["guid"], vm["target"]["fileID"])
            if(ref != None):
                refobj = self.project.getReferenceFromGUID(ref["guid"]).blocks[ref["fileID"]]
            else:
                refobj = "+UNKNOWN+"

            if km in dict_t:
                vt = dict_t[km]
                if vm == vt:
                    mod_out.append(vm)
                else:
                    print("#####")
                    UnityYamlTools.VisualizeHierarchyPath(path)
                    MonoBehaviourMerger.PrintMBHeader(refobj.blocktype)
                    print("Property: " + vm["propertyPath"])
                    Listmerger.display_in_columns("Value in MINE:\n" + str(vm["value"]) + "\n" + str(vm["objectReference"]), f"Value in THEIRS:\n" + str(vt["value"]) + "\n" + str(vt["objectReference"]) + "\n")
                    print()
                    if(Listmerger.ab("Values for [a]MINE and [b]THEIRS differ: which one do you wanna keep")):
                        mod_out.append(vm)
                    else:
                        mod_out.append(vt)
            else:
                print("#####")
                UnityYamlTools.VisualizeHierarchyPath(path)
                MonoBehaviourMerger.PrintMBHeader(refobj.blocktype)
                print("Property: " + vm["propertyPath"])
                print("Value: " + vm["value"] + "/" + "Reference: " + vm["objectReference"])
                if(Listmerger.yesno(f"modification for {path} is in MINE but not in THEIRS. Do you wanna keep it?")):
                    mod_out.append(vm)

        for kt,vt in dict_t.items():
            if kt in dict_m:
                continue # already handled above

            path = self.value_t.hierarchyPath + "/" + self.value_t.searchReferencePath(vt["target"]["guid"], vt["target"]["fileID"])
            ref = self.value_t.searchReference(vt["target"]["guid"], vt["target"]["fileID"])
            if(ref != None):
                refobj = self.project.getReferenceFromGUID(ref["guid"]).blocks[ref["fileID"]]
            else:
                refobj = "+UNKNOWN+"

            print("#####")
            UnityYamlTools.VisualizeHierarchyPath(path)
            MonoBehaviourMerger.PrintMBHeader(refobj.blocktype)
            print("Property:  " + vt["propertyPath"])
            print("Value:     " + str(vt["value"]) + "/n" + "Reference: " + str(vt["objectReference"]))
            if(Listmerger.yesno(f"modification for {path} is in THEIRS but not in MINE. Do you wanna keep it?")):
                mod_out.append(vt)
        NewYaml["PrefabInstance"]["m_Modification"]["m_Modifications"] = mod_out
        return NewYaml

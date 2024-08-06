#   _____  _    __
# ,´     \/ \ _`,    Author: Christian Grund
# |  C/  /  / __     Company: AISC GmbH
#  \_/__/__/ /_      mailto: cg@aisc.digital
#

from __future__ import annotations

import copy
import os

import yaml
import typing

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unityData.unityProject import UnityProject
    from unityData.unityFile import UnityFile


class UnityFileBlock:
    def __init__(self, project: 'UnityProject', file: 'UnityFile', uid: int, block: str):
        self.block:str = block
        self.uid:int = uid
        self._isStripped:bool = False
        self._object = None
        self.file:'UnityFile' = file
        self.project = project

    def _parse(self):
        block = self.block
        if(block.startswith("--- !u!")):
            splt = block.split("\n",1)
            block = splt[1]
            self._isStripped = "stripped" in splt[0]
        self._object = yaml.load(block, yaml.Loader)


    @property
    def isTransform(self):
        return self.blocktype == "Transform" or self.blocktype == "RectTransform"

    @property
    def object(self):
        if self._object == None:
            self._parse()
        return self._object

    @property
    def objectContent(self):
        return list(self.object.values())[0]

    @property
    def isStripped(self) -> bool:
        if self._isStripped == None:
            self._parse()
        return self._isStripped

    @property
    def blocktype(self) -> str:
        return list(self.object.keys())[0]

    @property
    def gameObject(self):
        if self.file == None:
            return None
        if self.blocktype == "GameObject":
            return self
        if "m_GameObject.fileID" in self:
            id = self["m_GameObject.fileID"]
            if id == 0:
                return None
            if id in self.file.blocks:
                return self.file.blocks[id]
            else:
                print ("Missing Block ID " + str(id))
                return None
        if self.blocktype == "PrefabInstance":
            #print ("PrefabInstance does not have a GameObject")
            return None
        else:
            #print ("Error: Does not have a GameObject")
            return None

    @property
    def transform(self):
        if self.file == None:
            return None
        if self.isTransform:
            return self
        gameObject = self.gameObject
        if gameObject != None:
            if "m_Component" in self.gameObject:
                for comp in self.gameObject["m_Component"]:
                    compID = comp["component"]["fileID"]
                    compBlock = self.file.blocks[compID]
                    if compBlock.isTransform:
                        return compBlock
        #print("Object does not have a Transform", "STRIPPED" if self.isStripped else "")
        return None

    @property
    def parent(self):
        if self.file == None:
            return None
        if self.blocktype == "PrefabInstance":
            if "m_Modification.m_TransformParent.fileID" in self:
                id = self["m_Modification.m_TransformParent.fileID"]
                if id == 0:
                    return None
                if id in self.file.blocks:
                    return self.file.blocks[id]
                else:
                    print ("Missing Block ID " + str(id))
                    return None
        transform = self.transform
        if transform == None:
            return None
        if "m_Father.fileID" in transform:
            id = transform["m_Father.fileID"]
            if id == 0:
                return None
            if id in self.file.blocks:
                return self.file.blocks[id]
            else:
                print ("Missing Block ID " + str(id))
                return None
        #print ("Transform does not have a m_Father component")
        return None


    @property
    def children(self):
        if self.file == None:
            return None
        transform = self.transform
        if transform == None:
            return []
        childrenIDs = transform["m_Children"]
        return [self.file.blocks[id["fileID"]] for id in childrenIDs]
    @property
    def name(self, withType = False):
        name = ""
        if self.blocktype == "PrefabInstance":
            sourcePrefabGUID = self["m_SourcePrefab.guid"]
            return "[" + os.path.basename(self.project.getReferenceFromGUID(sourcePrefabGUID).fileName) + "]"

        gameObject = self.gameObject
        if gameObject != None and "m_Name" in gameObject:
            name += gameObject["m_Name"]
        if withType == True or name == "":
            name += "["+self.blocktype+"]"

            if "m_Script" in self:
                scriptGUID = self["m_Script.guid"]
                scriptref = self.project.getReferenceFromGUID(scriptGUID)
                if scriptref != None:
                    name += "[" + os.path.basename(self.project.getReferenceFromGUID(scriptGUID).fileName) + "]"

        return name

    @property
    def hierarchyPath(self):
        parent = self.parent
        if parent == None:
            return self.name
        else:
            return parent.hierarchyPath + "/" + self.name


    def searchReference(self, guid, fileID):
        searchList = list()
        searchList.append({"guid":guid, "fileID":fileID, "prefabNestPath":list()})

        while (len(searchList)!=0):
            elem = searchList.pop(0)
            prefabFile = self.project.getReferenceFromGUID(elem["guid"])
            if elem["fileID"] in prefabFile.blocks:
                return elem
            nestedPrefabFiles = [v for v in prefabFile.blocks.values() if v.blocktype == "PrefabInstance"]
            for npf in nestedPrefabFiles:
                nestedID = self.nestedPrefabID(npf.uid, elem["fileID"])
                nestedGUID = npf["m_SourcePrefab.guid"]
                path = elem["prefabNestPath"] + [{"guid":elem["guid"], "fileID":npf.uid}]
                searchList.append({"guid":nestedGUID, "fileID":nestedID,"prefabNestPath":path})
        return None


    def searchReferencePath(self, guid, fileID):
        ref = self.searchReference(guid, fileID)
        if(ref == None):
            return "+UNKNOWN+"
        else:
            leaf = self.project.getReferenceFromGUID(ref["guid"])
            path = leaf.blocks[ref["fileID"]].hierarchyPath
        for pnp in ref["prefabNestPath"]:
            nest = self.project.getReferenceFromGUID(pnp["guid"])
            path = nest.blocks[pnp["fileID"]].hierarchyPath + "//" + path
        return path

    def unstripped(self):
        if not self.isStripped:
            return None
        prefabInstanceID = self["m_PrefabInstance.fileID"]
        prefabReferenceGUID = self["m_CorrespondingSourceObject.guid"]
        prefabReferencefileID = self["m_CorrespondingSourceObject.fileID"]
        ref = self.searchReference(prefabReferenceGUID, prefabReferencefileID)
        originBlock = self.project.getReferenceFromGUID(ref["guid"]).blocks[ref["fileID"]]
        unstrippedBlock = copy.copy(originBlock)

        for nestedPrefab in reversed(ref["prefabNestPath"]):
            nestedGUID = nestedPrefab["guid"]
            nestedFileID = nestedPrefab["fileID"]
            nestedFile = self.project.getReferenceFromGUID(nestedGUID)
            nestedBlock = nestedFile.blocks[nestedFileID]
            modifications = nestedBlock["m_Modification.m_Modifications"]
            for mod in modifications:
                if mod["target"]["fileID"] != unstrippedBlock.uid:
                    continue
                if type(unstrippedBlock[mod["propertyPath"]]) == dict and "fileID" in unstrippedBlock[mod["propertyPath"]]:
                    unstrippedBlock[mod["propertyPath"]] = mod["objectReference"]
                else:
                    unstrippedBlock[mod["propertyPath"]] = mod["value"]
            unstrippedBlock.uid = self.nestedPrefabID(unstrippedBlock.uid, nestedPrefab["fileID"])
            unstrippedBlock.file = nestedFile

        modifications = self.file.blocks[prefabInstanceID]["m_Modification.m_Modifications"]
        for mod in modifications:
            if mod["target"]["fileID"] != unstrippedBlock.uid:
                continue
            if type(unstrippedBlock[mod["propertyPath"]]) == dict and "fileID" in unstrippedBlock[mod["propertyPath"]]:
                unstrippedBlock[mod["propertyPath"]] = mod["objectReference"]
            else:
                unstrippedBlock[mod["propertyPath"]] = mod["value"]
        unstrippedBlock.uid = self.uid
        unstrippedBlock.file = self.file
        return unstrippedBlock



    def __getitem__(self, key):
        splt = key.split(".")
        obj = self.objectContent
        for s in splt:
            obj = obj[s]
        return obj

    def __setitem__(self, key, value):
        splt = key.split(".")
        obj = self.objectContent
        for s in splt[:-1]:
            obj = obj[s]
        obj[splt[-1]] = value

    def __contains__(self, item):
        splt = item.split(".")
        obj = self.objectContent
        for s in splt:
            if s in obj:
                obj = obj[s]
            else:
                return False
        return True

    def __repr__(self):
        return self.hierarchyPath + " (" + self.blocktype + ")"

    @staticmethod
    def nestedPrefabID(FileID_of_nested_PrefabInstance, FileID_of_object_in_nested_Prefab):
        #fileID for nested prefabs and also variants are generated based on the prefab instance and the corresponding object
        #https://forum.unity.com/threads/how...orrespondingsourceobject.726704/#post-4851011
        return (FileID_of_nested_PrefabInstance ^ FileID_of_object_in_nested_Prefab) & 0x7fffffffffffffff

#   _____  _    __
# ,´     \/ \ _`,    Author: Christian Grund
# |  C/  /  / __     Company: AISC GmbH
#  \_/__/__/ /_      mailto: cg@aisc.digital
#

import configparser
import os.path

from unityData.unityIndex import UnityIndex
class UnityProject:

    def __init__(self, configFile):
        self.configFile = configFile
        self.config = configparser.ConfigParser()
        self.config.read(configFile)
        self.index = UnityIndex(self)

    def readPath(self, path):
        path_location = os.path.dirname(self.configFile)
        if os.path.isabs(path):
            return path
        else:
            # Join the path_location and file_location to create an absolute path
            absolute_path = os.path.abspath(os.path.join(path_location, path))
            return absolute_path

    def getReferenceFromPath(self, path):
        return self.index.getReferenceFromPath(path)

    def getReferenceFromGUID(self, guid):
        return self.index.getReferenceFromGUID(guid)

    @property
    def AssetFolder(self):
        return self.readPath(self.config["PATHS"]["AssetFolder"])

    @property
    def PackagesFolder(self):
        return self.readPath(self.config["PATHS"]["PackagesFolder"])
    @property
    def LibraryFolder(self):
        return self.readPath(self.config["PATHS"]["LibraryFolder"])
    @staticmethod
    def createNewConfig(AssetFolderPath):
        config = configparser.ConfigParser();
        config["PATHS"] = {'AssetFolder':'Assets',
                           'LibraryFolder':'Library',
                           'PackagesFolder':'Packages'}
        configFilePath = os.path.normpath(os.path.join(AssetFolderPath,"..","UnityToolPackConfig.cfg"))
        with open(configFilePath,'w') as f:
            config.write(f)
        return configFilePath



if __name__ == '__main__':
    conf = UnityProject.createNewConfig("/Users/christian/git/AITechDemo/AITechDemo/Assets")
    project = UnityProject(conf)
    fileref = project.getReferenceFromPath("/Users/christian/git/AITechDemo/AITechDemo/Assets/Scenes/DanceHero/DanceHero.unity")
    for k,v in fileref.blocks.items():
        print(k,v.hierarchyPath)
    pass
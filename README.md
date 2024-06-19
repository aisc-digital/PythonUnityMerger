# Python Unity Tool Pack #
by Christian Grund, AISC GmbH

## Merge Untiy File ##

Resolve Merge conflicts interactivly.

### Usage ###
   #### using ProjectConfigFile: ####
     mergeUnityFile.py [ProjectConfig] [FileWithMergeConflicts]
    
   #### using Unity Project Path ####
     mergeUnityFile.py [UnityProjectPath] [FileWithMergeConflicts]
    
note: this will automatically generate a config file UnityToolPackConfig.cfg in your Unity Project Directory
     
### Example ###

If you have an override of the text of a TMP object inside a prefab, it will ask me something like this:

      Canvases/VerticalCanvas/ScrollRect/Viewport/Content/VerticalLayout/2col (1)/rightCol/[MenuItem Numeric.prefab]:
      #####
      Value in A:    Value in B:
      99             81
      {'fileID': 0}  {'fileID': 0}
      Property: [MonoBehaviour]m_text
      Path: Canvases/VerticalCanvas/ScrollRect/Viewport/Content/VerticalLayout/2col (1)/rightCol/[MenuItem Numeric.prefab]//[MenuItemWithoutImage.prefab]//MenuItemWithoutImage/Text/Subtitle
      Values for A and B differ: which one do you wanna keep [a/b]

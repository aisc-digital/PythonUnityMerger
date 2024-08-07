Python Unity Merger
======================

by Christian Grund, AISC GmbH

Overview
--------

The Python Unity Merger is a tool for interactively resolving merge conflicts in Unity projects. It provides an efficient way to resolve git merge conflicts in Unity files, ensuring smooth collaboration during development.

Features
--------

*   **Interactive Conflict Resolution**: Users can resolve merge conflicts in Unity projects interactively.
*   **Automatic Configuration File**: Automatically generates a configuration file when the path to a Unity project is provided.
*   **YAML Tools**: Support for processing Unity YAML files.
*   **List Merger**: Functions for merging and displaying list differences.
*   **Automatic Indexing**: Ability to index GUIDs from the `.meta` files to give propper information about the conflicting values.

Installation
------------

1.  **Clone the Repository**:
    
        git clone <repository-url>
    
2.  **Navigate to the Project Directory**:
    
        cd PythonUnityMerger
    
3.  **Create and Activate Virtual Environment**:
    
        python -m venv venv
        source venv/bin/activate   # On Windows: venv\Scripts\activate
    
4.  **Install Dependencies**:
    
        pip install -r requirements.txt
    

Usage
-----

### Merging Unity Files

#### Using Unity Project Path

    python mergeUnityFile.py [UnityProjectPath] [FileWithMergeConflicts]

*   `UnityProjectPath`: Path to the Unity project folder.
*   `FileWithMergeConflicts`: Path to the file with merge conflicts.

#### Using a Project Configuration File (alternative)
Using a config file you can edit the location of the Assets, Packages and Library folder. Further configurations may come in future.

    python mergeUnityFile.py [ProjectConfig] [FileWithMergeConflicts]

*   `ProjectConfig`: Path to the project configuration file.
*   `FileWithMergeConflicts`: Path to the file with merge conflicts.


**Note**: When using the Unity project path, a configuration file `UnityToolPackConfig.cfg` will be automatically generated in the Unity project directory.

### Interactive Selection

Merge conflicts are presented interactivly to be able to perfrom a qualified choice. Thus you will be asked for every conflict point individually while being provided with propper information.

```
╭───────────╮
┘ Hierarchy └───────────────────────────────────────────────
 ▼ ⬡ Canvases
  ▼ ⬡ MainCanvas
   ▼ ⬡ Scroll View
    ▼ ⬡ Viewport
     ▼ ⬡ Toggles
      ▼ ⬢ [AppToggle.prefab]
          AppToggle
╭───────────────╮
┘ MonoBehaviour └───────────────────────────────────────────
 ▼ ⌸    RectTransform                                 ⏺ ≓ ⋮ 

Property: m_AnchorMax.y
Value in MINE:  Value in THEIRS:
0               1               
{'fileID': 0}   {'fileID': 0}   

Values for [a]MINE and [b]THEIRS differ: which one do you wanna keep? [a/b]

```

Author
------

Christian Grund, AISC GmbH  
Email: [cg@aisc.digital](mailto:cg@aisc.digital)

#   _____  _    __
# ,´     \/ \ _`,    Author: Christian Grund
# |  C/  /  / __     Company: AISC GmbH
#  \_/__/__/ /_      mailto: cg@aisc.digital
#

class UnityYamlTools:
    @staticmethod
    def split_into_text_blocks(multiline_string:str):
        text_blocks = {"": ""}
        line_numbers = [(0, None),]
        lines = multiline_string.split('\n')
        current_key = ""
        lineNumber = -1
        current_block = []

        for line in lines:
            lineNumber += 1
            if line.startswith('--- !u!'):
                current_key = line.strip()
                if current_key in text_blocks:
                    print("WARNING: " + current_key + " already exists!")
                text_blocks[current_key] = ""
                line_numbers += (lineNumber, current_key)
            text_blocks[current_key] += line + "\n"
        return text_blocks, line_numbers

    @staticmethod
    def printTabbar(name:str, width:int=60):
        l = len(name)
        print(u"\u256d" + u"\u2500" * (l+2) + u"\u256e")
        print(u"\u2518" +  " "+ name + " " + u"\u2514" + u"\u2500" * (width - l - 4))

    @staticmethod
    def VisualizeHierarchyPath(path:str):
        spath = path.split("/")
        UnityYamlTools.printTabbar("Hierarchy")
        indent = -1
        showHexOnNext = True
        for i in range(len(spath)):
            elem = spath[i]
            hexagon = u'\u2b22' if elem.startswith("[") else u'\u2b21'
            triangle = u'\u25bc' if i < len(spath)-1 else ' '
            if i!=0 and spath[i-1].startswith("["):
                hexagon = " "
                triangle = " "
            else:
                indent += 1
            print(" " + " " * indent + triangle + ' ' + hexagon + ' ' + spath[i])
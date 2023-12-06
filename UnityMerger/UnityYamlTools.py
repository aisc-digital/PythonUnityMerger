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
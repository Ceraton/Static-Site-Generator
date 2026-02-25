from enum import Enum

class TextType(Enum):
    TEXT = "text"
    BOLD = "**Bold text**"
    ITALIC = "_Italic text_"
    CODE = "`Code text`"
    LINK = "[anchor text](url)"
    IMAGE = "![alt text](url)"



class TextNode():
    def __init__(self, text, texttype: TextType, url=None):
        self.text = text
        self.text_type = texttype
        self.url = url

    

    def __eq__(self, other):
        if self.text == other.text and \
            self.text_type == other.text_type and\
            self.url == other.url:
            return True
        else:
            return False

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type}, {self.url})"

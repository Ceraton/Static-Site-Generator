
class HTMLNode():
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        if not self.props:
            return ""
        else:
            return f"href={self.props["href"]} target={self.props["target"]}"
    
    def __eq__(self, other):
        return (
            self.tag == other.tag and
            self.value == other.value and
            self.children == other.children and
            self.props == other.props
        )

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"
    

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)
        self.tag = tag
        self.value = value
        self.props = props
    
    def to_html(self):
        if self.value is None:
            raise ValueError
        if self.tag is None:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def props_to_html(self):
        if not self.props:
            return ""
        if "href" in self.props:
            if self.props["href"] and not self.props["target"]:
                return f"href={self.props["href"]}"
            else:
                return f"href={self.props["href"]} target={self.props["target"]}"
        if "src" in self.props:
            if self.props["src"] and not self.props["alt"]:
                return f"img={self.props["src"]}"
            else:
                return f"img={self.props["src"]} alt={self.props["alt"]}"

    def __repr__(self):
        return f"LeafNode({self.tag}, {self.value}, {self.props})"
    
class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)
        self.tag = tag
        self.children = children
        self.props = props

    def to_html(self):
        if self.tag is None:
            raise ValueError("Missing tag")
        if self.children is None:
            raise ValueError("Missing children")
        result = f"<{self.tag}{self.props_to_html()}>"
        for child in self.children  :
            result += child.to_html()
        
        result += f"</{self.tag}>"
        return result
    

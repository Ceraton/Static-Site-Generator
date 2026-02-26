from htmlnode import HTMLNode, ParentNode, LeafNode
from textnode import TextNode, TextType

import re
from enum import Enum

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDEREDLIST = "unordered_list"
    ORDEREDLIST = "ordered_list"

def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
        case _:
            raise ValueError(f"Invalid text type: {text_node.text_type}")
        
def split_nodes_delimiter(old_nodes, delimiter, text_type):
    if not delimiter:
        raise SyntaxError("Markdown Syntax invlid")
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        parts = node.text.split(delimiter)

        if len(parts) % 2 == 0:
            raise ValueError("Invalid markdown segments")
        
        for i in range(len(parts)):
            if parts[i] == "":
                continue
            if i % 2 == 0:
                new_nodes.append(TextNode(parts[i], TextType.TEXT))
            else:
                new_nodes.append(TextNode(parts[i], text_type))
        
    return new_nodes

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
        
def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        original_text = node.text
        images = extract_markdown_images(original_text)

        if len(images) == 0:
            new_nodes.append(node)
            continue

        for image in images:
            sections = original_text.split(f"![{image[0]}]({image[1]})", 1)
            if len(sections) != 2:
                raise ValueError("Markdown not looking so good")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))
            original_text = sections[1]

        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    
    return new_nodes



def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        original_text = node.text
        links = extract_markdown_links(original_text)
        
        if len(links) == 0:
            new_nodes.append(node)
            continue
            
        for link in links:
            sections = original_text.split(f"[{link[0]}]({link[1]})", 1)

            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))

            new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            
            original_text = sections[1]
            
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
            
    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]

    
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)

    return nodes

def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    blocks = [block.strip() for block in blocks]
    blocks = [block for block in blocks if block != ""]
    return blocks

def block_to_block_type(block):
    if re.match(r"^#{1,6} ", block):
        return BlockType.HEADING
    
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    
    lines = block.split("\n")
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE
    
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDEREDLIST
    
    is_ordered = True
    for i, line in enumerate(lines):
        if not line.startswith(f"{i + 1}. "):
            is_ordered = False
            break

    if is_ordered:
        return BlockType.ORDEREDLIST
    
    return BlockType.PARAGRAPH
    
def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []

    for block in blocks:
        children.append(block_to_html_node(block))
    return ParentNode("div", children)

def block_to_html_node(block):
    block_type = block_to_block_type(block)
    match block_type:
        case BlockType.HEADING:
            return heading_to_html_node(block)
        case BlockType.CODE:
            return code_to_html_node(block)
        case BlockType.QUOTE:
            return quote_to_html_node(block)
        case BlockType.UNORDEREDLIST:
            return unordered_list_to_html_node(block)
        case BlockType.ORDEREDLIST:
            return ordered_list_to_html_node(block)
        case BlockType.PARAGRAPH:
            return paragraph_to_html_node(block)
        case _:
            raise ValueError(f"Unknown block type: {block_type}")

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    return [text_node_to_html_node(node) for node in text_nodes]

def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    text = block[level + 1:]
    return ParentNode(f"h{level}", text_to_children(text))

def code_to_html_node(block):
    lines = block.split("\n")

    content_lines = lines[1:-1]

    stripped = [line.strip() for line in content_lines]
    text = "\n".join(stripped) + "\n"
    return ParentNode("pre", [LeafNode("code", text)])

def quote_to_html_node(block):
    lines = block.split("\n")
    stripped = [line.lstrip(">").strip() for line in lines]
    text = " ".join(stripped)
    return ParentNode("blockquote", text_to_children(text))

def unordered_list_to_html_node(block):
    lines = block.split("\n")
    items = [ParentNode("li", text_to_children(line[2:])) for line in lines]
    return ParentNode("ul", items)

def ordered_list_to_html_node(block):
    lines = block.split("\n")
    items = [ParentNode("li", text_to_children(line.split(". ", 1)[1])) for line in lines]
    return ParentNode("ol", items)

def paragraph_to_html_node(block):
    lines = block.split("\n")
    text = " ".join(line.strip() for line in lines)
    return ParentNode("p", text_to_children(text))

def extract_title(markdown):
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    raise Exception("Missing header")


import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextNode, TextType
from functions import *

class TestFunctions(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

class TestSplitDelimiter(unittest.TestCase):
    def test_split_nodes_delimiter(self):
        # 1. Basic Case: Single delimited word
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_split_nodes_multiple(self):
        # 2. Multiple Case: Two separate delimited sections
        node = TextNode("This has **bold** and **more bold**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This has ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("more bold", TextType.BOLD),
            ],
        )

    def test_split_nodes_start_end(self):
        # 3 & 4. Beginning and End: Delimiters at the very edges
        node = TextNode("*italic* at start and end *italic*", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertEqual(
            new_nodes,
            [
                TextNode("italic", TextType.ITALIC),
                TextNode(" at start and end ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
            ],
        )

    def test_split_nodes_unclosed(self):
        # 5. Unclosed Case: Should raise a ValueError
        node = TextNode("This is **unclosed bold", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_split_nodes_multiple_nodes(self):
        # Bonus: Ensure it handles a list of multiple input nodes
        node1 = TextNode("Node one `code`", TextType.TEXT)
        node2 = TextNode("Node two", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node1, node2], "`", TextType.CODE)
        self.assertEqual(
            len(new_nodes),
            3
        )

class TestMarkdownExtraction(unittest.TestCase):
    def test_extract_markdown_images(self):
        # 1. Basic test with two images
        text = "This is text with an ![image](https://i.imgur.com/zceBglk.png) and ![another](https://i.imgur.com/df9jS9.png)"
        matches = extract_markdown_images(text)
        self.assertEqual(
            matches, 
            [("image", "https://i.imgur.com/zceBglk.png"), ("another", "https://i.imgur.com/df9jS9.png")]
        )

    def test_extract_markdown_links(self):
        # 2. Basic test with two links
        text = "This is text with a [link](https://www.google.com) and [another](https://www.example.com)"
        matches = extract_markdown_links(text)
        self.assertEqual(
            matches, 
            [("link", "https://www.google.com"), ("another", "https://www.example.com")]
        )

    def test_extract_links_ignores_images(self):
        # 3. Ensure links extractor ignores image syntax (the '!') 
        # Your regex in image_cf295a.png uses a negative lookbehind (?<!!) to handle this!
        text = "This has a [link](https://google.com) and an ![image](https://i.imgur.com/zceBglk.png)"
        matches = extract_markdown_links(text)
        self.assertEqual(matches, [("link", "https://google.com")])

    def test_extract_images_ignores_links(self):
        # 4. Ensure images extractor ignores plain links
        text = "This has a [link](https://google.com) and an ![image](https://i.imgur.com/zceBglk.png)"
        matches = extract_markdown_images(text)
        self.assertEqual(matches, [("image", "https://i.imgur.com/zceBglk.png")])

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)   

class TestSplitNodes(unittest.TestCase):
    def test_split_image(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zceBglk.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zceBglk.png"),
            ],
            new_nodes,
        )

    def test_split_image_multiple(self):
        node = TextNode(
            "![first](https://link1.png) middle ![second](https://link2.png) end",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("first", TextType.IMAGE, "https://link1.png"),
                TextNode(" middle ", TextType.TEXT),
                TextNode("second", TextType.IMAGE, "https://link2.png"),
                TextNode(" end", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_link_multiple(self):
        node = TextNode(
            "Click [here](https://google.com) and [there](https://bing.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("Click ", TextType.TEXT),
                TextNode("here", TextType.LINK, "https://google.com"),
                TextNode(" and ", TextType.TEXT),
                TextNode("there", TextType.LINK, "https://bing.com"),
            ],
            new_nodes,
        )

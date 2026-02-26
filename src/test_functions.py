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

    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )

class TestMarkdownToBlocks(unittest.TestCase):

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )
    
    def test_markdown_to_blocks_single_block(self):
        md = """Just a single paragraph with no extra newlines."""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Just a single paragraph with no extra newlines."])

    def test_markdown_to_blocks_empty_string(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_only_newlines(self):
        md = "\n\n\n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_excessive_newlines(self):
        md = """First block



    Second block"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["First block", "Second block"])

    def test_markdown_to_blocks_strips_whitespace(self):
        md = """   Block with leading spaces   

    Another block with spaces   """
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Block with leading spaces", "Another block with spaces"])

    def test_markdown_to_blocks_heading(self):
        md = """# Heading 1

    Some paragraph text."""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["# Heading 1", "Some paragraph text."])

    def test_markdown_to_blocks_code_block(self):
        md = "Some intro text\n\n```\ndef hello():\n    print(\"hello\")\n```\n\nSome closing text"
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "Some intro text",
                "```\ndef hello():\n    print(\"hello\")\n```",
                "Some closing text",
            ],
        )

    def test_markdown_to_blocks_ordered_list(self):
        md = "1. First item\n2. Second item\n3. Third item"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["1. First item\n2. Second item\n3. Third item"])

    def test_markdown_to_blocks_multiple_block_types(self):
        md = "# My Document\n\nThis is a paragraph.\n\n- Item one\n- Item two\n\n1. Step one\n2. Step two"
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "# My Document",
                "This is a paragraph.",
                "- Item one\n- Item two",
                "1. Step one\n2. Step two",
            ],
        )

class TestBlockToBlockType(unittest.TestCase):

    # HEADING tests
    def test_heading_h1(self):
        self.assertEqual(block_to_block_type("# Hello"), BlockType.HEADING)

    def test_heading_h3(self):
        self.assertEqual(block_to_block_type("### Hello"), BlockType.HEADING)

    def test_heading_h6(self):
        self.assertEqual(block_to_block_type("###### Hello"), BlockType.HEADING)

    def test_heading_no_space(self):
        # Missing space after # -> paragraph
        self.assertEqual(block_to_block_type("#Hello"), BlockType.PARAGRAPH)

    def test_heading_seven_hashes(self):
        # 7 # characters is not a valid heading
        self.assertEqual(block_to_block_type("####### Hello"), BlockType.PARAGRAPH)

    # CODE tests
    def test_code_block(self):
        self.assertEqual(block_to_block_type("```\nsome code\n```"), BlockType.CODE)

    def test_code_block_missing_closing(self):
        self.assertEqual(block_to_block_type("```\nsome code"), BlockType.PARAGRAPH)

    # QUOTE tests
    def test_quote_single_line(self):
        self.assertEqual(block_to_block_type("> some quote"), BlockType.QUOTE)

    def test_quote_no_space(self):
        # > without space is still valid
        self.assertEqual(block_to_block_type(">some quote"), BlockType.QUOTE)

    def test_quote_multiline(self):
        self.assertEqual(block_to_block_type("> line1\n> line2"), BlockType.QUOTE)

    def test_quote_missing_gt_on_line(self):
        # One line doesn't start with > -> paragraph
        self.assertEqual(block_to_block_type("> line1\nline2"), BlockType.PARAGRAPH)

    # UNORDERED LIST tests
    def test_unordered_list_single(self):
        self.assertEqual(block_to_block_type("- item"), BlockType.UNORDEREDLIST)

    def test_unordered_list_multiline(self):
        self.assertEqual(block_to_block_type("- item1\n- item2\n- item3"), BlockType.UNORDEREDLIST)

    def test_unordered_list_missing_space(self):
        # "-item" without space -> paragraph
        self.assertEqual(block_to_block_type("-item"), BlockType.PARAGRAPH)

    # ORDERED LIST tests
    def test_ordered_list_single(self):
        self.assertEqual(block_to_block_type("1. item"), BlockType.ORDEREDLIST)

    def test_ordered_list_multiline(self):
        self.assertEqual(block_to_block_type("1. item1\n2. item2\n3. item3"), BlockType.ORDEREDLIST)

    def test_ordered_list_wrong_start(self):
        # Must start at 1
        self.assertEqual(block_to_block_type("2. item1\n3. item2"), BlockType.PARAGRAPH)

    def test_ordered_list_skips_number(self):
        # Skips from 1 to 3 -> paragraph
        self.assertEqual(block_to_block_type("1. item1\n3. item2"), BlockType.PARAGRAPH)

    # PARAGRAPH tests
    def test_paragraph(self):
        self.assertEqual(block_to_block_type("Just some text"), BlockType.PARAGRAPH)

    def test_paragraph_multiline(self):
        self.assertEqual(block_to_block_type("line one\nline two"), BlockType.PARAGRAPH)

class TestMarkdownToHtml(unittest.TestCase):

    def test_paragraphs(self):
        md = """
    This is **bolded** paragraph
    text in a p
    tag here

    This is another paragraph with _italic_ text and `code` here

    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
    ```
    This is text that _should_ remain
    the **same** even with inline stuff
    ```
    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

class TestExtractTitle(unittest.TestCase):

    def test_simple_title(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_title_with_extra_spaces(self):
        self.assertEqual(extract_title("#  Hello  "), "Hello")

    def test_title_not_first_line(self):
        self.assertEqual(extract_title("some text\n# Hello\nmore text"), "Hello")

    def test_h2_not_valid(self):
        # Only h1 counts as the title
        self.assertRaises(Exception, extract_title, "## Not a title")

    def test_no_heading_raises(self):
        self.assertRaises(Exception, extract_title, "just some text")

    def test_hash_in_text_not_heading(self):
        # A # mid-sentence should not match
        self.assertRaises(Exception, extract_title, "some#thing weird")

    def test_empty_string_raises(self):
        self.assertRaises(Exception, extract_title, "")

    def test_title_with_inline_markdown(self):
        # Bold inside heading should still return the raw text
        self.assertEqual(extract_title("# Hello **world**"), "Hello **world**")
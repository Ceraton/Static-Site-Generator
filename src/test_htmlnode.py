import unittest

from htmlnode import HTMLNode, LeafNode


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = HTMLNode("<p></p>", "This is a paragraph")
        node2 = HTMLNode("<p></p>", "This is a paragraph")
        self.assertEqual(node, node2)
    
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    

if __name__ == "__main__":
    unittest.main()
from textnode import TextNode, TextType
from functions import markdown_to_html_node, extract_title
import os, shutil, sys

def copy_static(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.mkdir(dst)

    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)

        if os.path.isfile(src_path):
            print(f"Copying {src_path, dst_path}")
            shutil.copy(src_path, dst_path)
        else:
            copy_static(src_path, dst_path)

def generate_page(from_path, template_path, dest_path, base_path="/"):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path) as f:
        markdown = f.read()
    with open(template_path) as f:
        template = f.read()
    
    content_html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)
    page = (template
            .replace("{{ Title }}", title)
            .replace("{{ Content }}", content_html)
            .replace('href="/', f'href="{base_path}')
            .replace('src="/', f'src="{base_path}')
    )
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w") as f:
        f.write(page)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, base_path="/"):
    for entry in os.listdir(dir_path_content):
        src_path = os.path.join(dir_path_content, entry)
        dest_path = os.path.join(dest_dir_path, entry)

        if os.path.isfile(src_path) and entry.endswith(".md"):
            dest_path = dest_path.replace(".md", ".html")
            generate_page(src_path, template_path, dest_path, base_path)
        elif os.path.isdir(src_path):
            generate_pages_recursive(src_path, template_path, dest_path, base_path)

def main():
    base_path = sys.argv[1] if len(sys.argv) > 1 else "/"
    copy_static("static", "docs")
    generate_pages_recursive("content", "template.html", "docs", base_path)




if __name__ == "__main__":
    main()
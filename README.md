# Static Site Generator

A lightweight static site generator written in Python that converts Markdown content into a fully functional HTML website.

🌐 **Live Demo**: [https://ceraton.github.io/Static-Site-Generator/](https://ceraton.github.io/Static-Site-Generator/)

---

## Features

- Converts Markdown to HTML — headings, paragraphs, code blocks, quotes, and ordered/unordered lists
- Inline Markdown support — bold, italic, inline code, links, and images
- Recursively generates pages from nested content directories, preserving structure
- Injects generated content into a reusable HTML template
- Clean builds — wipes and rebuilds the output directory every time
- Configurable base path for subdirectory deployments (e.g. GitHub Pages)

## Getting Started

### Prerequisites

- Python 3.10+

### Run Locally

```bash
git clone https://github.com/ceraton/Static-Site-Generator.git
cd Static-Site-Generator
./main.sh
```

Visit [http://localhost:8888](http://localhost:8888) in your browser.

## How It Works

1. Static assets are copied from `static/` to `public/`
2. Markdown files in `content/` are parsed into an HTML node tree
3. The generated HTML and page title are injected into `template.html`
4. Finished pages are written to `public/`, mirroring the content directory structure

import os
import sys
import re

try:
    import markdown
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"])
    import markdown

try:
    import mdx_math
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-markdown-math"])
    import mdx_math

# Read the markdown
with open('research_paper.md', 'r', encoding='utf-8') as f:
    md_text = f.read()

# Convert to HTML
html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'toc', 'mdx_math'])

# Replace the standard <h1> with the Anthropic-style editorial Hero section
hero_html = """
<header class="hero">
    <h1>Predictive Modeling of Search Engine Visibility Decay: A Machine Learning Approach for Proactive SEO</h1>
    
    <div class="author-block">
        <div class="author-name">Nishit Patel</div>
        <div class="author-details">Machine Learning Capstone<br>FlyRank ML Internship &bull; August 2026</div>
    </div>
</header>
"""
# Replace the first <h1> block
html_content = re.sub(r'<h1>.*?</h1>', hero_html, html_content, count=1, flags=re.DOTALL)

# HTML Template
html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Predictive Modeling of Search Engine Visibility Decay</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Lora:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
    
    <!-- MathJax Configuration -->
    <script>
      MathJax = {{
        tex: {{
          inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
          displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
        }},
        svg: {{
          fontCache: 'global'
        }}
      }};
    </script>
    <script type="text/javascript" id="MathJax-script" async
      src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">
    </script>

    <style>
        :root {{
            /* Anthropic-inspired Editorial Palette */
            --bg-color: #FAF8F5;
            --section-bg: #FFFFFF;
            --text-primary: #1C1C1C;
            --text-secondary: #5F5F5F;
            --border-color: #E7E2DA;
            --accent: #8B6F47;
            --accent-hover: #735A37;
            --link-color: #7A5E3A;
            --code-bg: #F4F2EE;
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.65;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        .layout {{
            display: flex;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            position: relative;
        }}

        /* Sidebar / TOC */
        .sidebar {{
            width: 260px;
            flex-shrink: 0;
            padding: 4rem 2.5rem 4rem 0;
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
            border-right: 1px solid var(--border-color);
            display: none;
        }}

        @media (min-width: 1000px) {{
            .sidebar {{ display: block; }}
        }}

        .toc-title {{
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 1.5rem;
            font-family: 'Inter', sans-serif;
        }}

        .toc-list {{
            list-style: none;
            padding: 0;
            margin: 0;
            font-size: 0.9rem;
        }}

        .toc-list li {{
            margin-bottom: 0.75rem;
        }}

        .toc-list a {{
            color: var(--text-secondary);
            text-decoration: none;
            transition: color 0.2s ease;
            display: block;
            line-height: 1.4;
        }}

        .toc-list a:hover, .toc-list a.active {{
            color: var(--text-primary);
            font-weight: 500;
        }}

        /* Main Content */
        .main-content {{
            flex-grow: 1;
            max-width: 860px;
            padding: 4rem 0 6rem 0;
            margin: 0 auto;
        }}

        @media (min-width: 1000px) {{
            .main-content {{ padding: 5rem 3rem 8rem 4rem; margin: 0; }}
        }}

        /* Typography */
        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-primary);
            font-family: 'Lora', serif;
            font-weight: 500;
            margin-top: 3.5rem;
            margin-bottom: 1.25rem;
            line-height: 1.3;
        }}

        h2 {{
            font-size: 1.75rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.75rem;
        }}

        h3 {{ font-size: 1.35rem; margin-top: 2.5rem; }}
        
        p {{
            margin-bottom: 1.5rem;
            font-size: 1.05rem;
        }}

        strong {{
            font-weight: 600;
        }}

        /* Hero Section */
        .hero {{
            margin-bottom: 4rem;
            padding-bottom: 2.5rem;
        }}

        .hero h1 {{
            font-size: 2.4rem;
            margin-top: 0;
            margin-bottom: 2rem;
            font-weight: 500;
            letter-spacing: -0.02em;
            line-height: 1.25;
            border: none;
            color: var(--text-primary);
        }}

        .author-block {{
            margin-bottom: 0;
            margin-top: 2rem;
        }}
        
        .author-name {{
            font-size: 1.1rem;
            color: var(--text-primary);
            font-weight: 500;
            margin-bottom: 0.2rem;
        }}
        
        .author-details {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            line-height: 1.6;
        }}

        /* Links */
        .main-content a {{
            color: var(--link-color);
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.2s ease, color 0.2s ease;
        }}
        
        .main-content a:hover {{
            color: var(--accent-hover);
            border-bottom-color: var(--accent-hover);
        }}

        /* Code Blocks */
        pre {{
            background: var(--code-bg);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 1.25rem;
            overflow-x: auto;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            margin: 2rem 0;
            color: var(--text-primary);
        }}

        code {{
            font-family: 'JetBrains Mono', monospace;
            background: var(--code-bg);
            padding: 0.2rem 0.3rem;
            border-radius: 3px;
            font-size: 0.85em;
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }}

        pre code {{
            background: transparent;
            padding: 0;
            border: none;
        }}

        /* Academic Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 2.5rem 0;
            font-size: 0.95rem;
            font-family: 'Inter', sans-serif;
            background: var(--section-bg);
        }}

        th, td {{
            padding: 1rem 1.25rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}

        th {{
            color: var(--text-primary);
            font-weight: 600;
            border-bottom: 2px solid var(--text-primary);
            border-top: 2px solid var(--text-primary);
        }}

        tr:last-child td {{
            border-bottom: 2px solid var(--border-color);
        }}

        /* Champion Model Highlight */
        tbody tr.champion-row td {{
            background-color: var(--bg-color);
            font-weight: 500;
        }}

        /* Lists */
        ul, ol {{
            padding-left: 1.5rem;
            margin-bottom: 1.5rem;
            font-size: 1.05rem;
        }}

        li {{
            margin-bottom: 0.5rem;
        }}

        /* Images / Figures */
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 3rem auto 1rem auto;
            border: 1px solid var(--border-color);
            background: var(--section-bg);
            padding: 0.5rem;
        }}
        
        /* Figure Captions */
        img + em {{
            display: block;
            text-align: center;
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-top: 0.5rem;
            margin-bottom: 3rem;
            font-family: 'Lora', serif;
            font-style: italic;
        }}

        /* Math display block adjustments */
        .MathJax_Display {{
            margin: 2.5rem 0 !important;
            overflow-x: auto;
            overflow-y: hidden;
        }}

        /* Footer */
        footer {{
            margin-top: 6rem;
            padding-top: 2.5rem;
            border-top: 1px solid var(--border-color);
            font-size: 0.85rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            color: var(--text-secondary);
        }}

        .footer-left {{
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }}

        .footer-right a {{
            color: var(--link-color);
            text-decoration: none;
            transition: color 0.2s;
        }}
        
        .footer-left a {{
            color: var(--text-secondary);
            text-decoration: underline;
        }}

        .footer-left a:hover, .footer-right a:hover {{
            color: var(--accent-hover);
            text-decoration: underline;
        }}

        @media (min-width: 600px) {{
            footer {{
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="layout">
        <aside class="sidebar">
            <div class="toc-title">Contents</div>
            <ul class="toc-list" id="toc">
                <!-- TOC populated by JS -->
            </ul>
        </aside>

        <main class="main-content">
            {html_content}

            <footer>
                <div class="footer-left">
                    <div>Built and authored by Nishit Patel</div>
                    <div>Built on the <a href="https://flyrank.ai" target="_blank">FlyRank ML Internship Dataset</a></div>
                </div>
                <div class="footer-right">
                    <a href="https://github.com/nish-debug15/search-health-prediction" target="_blank">GitHub Repository</a>
                </div>
            </footer>
        </main>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            // Subtly highlight the Champion Model row in tables
            const tds = document.querySelectorAll('td');
            tds.forEach(td => {{
                if (td.textContent.includes('(Champion)')) {{
                    td.parentElement.classList.add('champion-row');
                }}
            }});

            // Build TOC
            const headings = document.querySelectorAll('.main-content h2');
            const toc = document.getElementById('toc');
            const headingElements = [];

            headings.forEach((heading, index) => {{
                if (!heading.id) {{
                    const text = heading.textContent;
                    const cleanText = text.replace(/^\d+\.\s*/, '');
                    heading.id = cleanText.toLowerCase().replace(/[^a-z0-9]+/g, '-');
                }}
                
                headingElements.push(heading);

                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = '#' + heading.id;
                a.textContent = heading.textContent.replace(/^\d+\.\s*/, '');
                li.appendChild(a);
                toc.appendChild(li);
            }});

            // Active section highlighting
            const observer = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        const id = entry.target.id;
                        document.querySelectorAll('.toc-list a').forEach(a => {{
                            a.classList.remove('active');
                            if (a.getAttribute('href') === '#' + id) {{
                                a.classList.add('active');
                            }}
                        }});
                    }}
                }});
            }}, {{ rootMargin: "-10% 0px -80% 0px" }});

            headingElements.forEach(heading => observer.observe(heading));
            
            // Extract alt text from images to use as captions
            const images = document.querySelectorAll('.main-content img');
            images.forEach(img => {{
                if (img.alt) {{
                    const caption = document.createElement('em');
                    caption.textContent = img.alt;
                    img.parentNode.insertBefore(caption, img.nextSibling);
                }}
            }});
        }});
    </script>
</body>
</html>
"""

os.makedirs('docs', exist_ok=True)
with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("Generated Anthropic-style editorial docs/index.html")

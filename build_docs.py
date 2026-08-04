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

# Convert to HTML (mdx_math ensures math equations are escaped from markdown parsing)
html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'toc', 'mdx_math'])

# We want to replace the standard <h1> with our custom Hero section
hero_html = """
<header class="hero">
    <h1>Predictive Modeling of Search Engine Visibility Decay:<br>A Machine Learning Approach for Proactive SEO</h1>
    
    <div class="author-block">
        <div class="author-name">Nishit Patel</div>
        <div class="author-details">Machine Learning Research Project</div>
        <div class="author-details">FlyRank ML Internship &bull; August 2026</div>
        <div class="author-links">
            <a href="https://github.com/nish-debug15/search-health-prediction" target="_blank">GitHub</a> | <a href="#" target="_blank">LinkedIn</a>
        </div>
    </div>
    
    <div class="metadata-row">
        <div class="meta-item"><strong>Dataset:</strong> FlyRank Internship Warehouse</div>
        <div class="meta-item"><strong>Model:</strong> Random Forest</div>
        <div class="meta-item"><strong>Primary Metric:</strong> Macro F1 = 0.4871</div>
    </div>
</header>
"""
# Replace the first <h1> block
html_content = re.sub(r'<h1>.*?</h1>', hero_html, html_content, count=1, flags=re.DOTALL)

# Let's wrap the HTML in a professional academic documentation template
html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Predictive Modeling of Search Engine Visibility Decay</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    
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
            --bg-color: #0f172a;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --border-color: #334155;
            --accent: #38bdf8;
            --surface: #1e293b;
            --code-bg: #0b1121;
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            background-color: var(--bg-color);
            color: var(--text-secondary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.7;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
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
            width: 250px;
            flex-shrink: 0;
            padding: 3rem 2rem 3rem 0;
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
            border-right: 1px solid var(--border-color);
            display: none;
        }}

        @media (min-width: 900px) {{
            .sidebar {{ display: block; }}
        }}

        .toc-title {{
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 1rem;
        }}

        .toc-list {{
            list-style: none;
            padding: 0;
            margin: 0;
            font-size: 0.9rem;
        }}

        .toc-list li {{
            margin-bottom: 0.5rem;
        }}

        .toc-list a {{
            color: var(--text-secondary);
            text-decoration: none;
            transition: color 0.2s;
            display: block;
            line-height: 1.4;
        }}

        .toc-list a:hover, .toc-list a.active {{
            color: var(--accent);
        }}

        /* Main Content */
        .main-content {{
            flex-grow: 1;
            max-width: 850px;
            padding: 3rem 0 5rem 0;
            margin: 0 auto;
        }}

        @media (min-width: 900px) {{
            .main-content {{ padding: 4rem 3rem 6rem 3rem; margin: 0; }}
        }}

        /* Typography */
        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-primary);
            font-weight: 600;
            margin-top: 3rem;
            margin-bottom: 1rem;
            line-height: 1.3;
        }}

        h2 {{
            font-size: 1.5rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
        }}

        h3 {{ font-size: 1.25rem; }}
        
        p {{
            margin-bottom: 1.25rem;
        }}

        strong {{
            color: var(--text-primary);
        }}

        /* Hero Section */
        .hero {{
            margin-bottom: 3rem;
            padding-bottom: 2rem;
            border-bottom: 1px solid var(--border-color);
        }}

        .hero h1 {{
            font-size: 1.85rem;
            margin-top: 0;
            margin-bottom: 1.5rem;
            font-weight: 700;
            letter-spacing: -0.01em;
            line-height: 1.4;
        }}

        .author-block {{
            margin-bottom: 1.5rem;
        }}
        
        .author-name {{
            font-size: 1.15rem;
            color: var(--text-primary);
            font-weight: 600;
            margin-bottom: 0.2rem;
        }}
        
        .author-details {{
            font-size: 0.95rem;
            color: var(--text-secondary);
        }}
        
        .author-links {{
            margin-top: 0.5rem;
            font-size: 0.9rem;
        }}

        .metadata-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
            background: var(--surface);
            padding: 1rem 1.5rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            font-size: 0.9rem;
            margin-top: 1rem;
        }}

        .meta-item strong {{
            color: var(--text-primary);
            margin-right: 0.25rem;
        }}

        /* Links */
        a {{
            color: var(--accent);
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}

        /* Code Blocks */
        pre {{
            background: var(--code-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 1.25rem;
            overflow-x: auto;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            margin: 1.5rem 0;
            color: var(--text-primary);
        }}

        code {{
            font-family: 'JetBrains Mono', monospace;
            background: var(--code-bg);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-size: 0.85em;
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }}

        pre code {{
            background: transparent;
            padding: 0;
            border: none;
        }}

        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
            font-size: 0.9rem;
        }}

        th, td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}

        th {{
            color: var(--text-primary);
            font-weight: 600;
            border-bottom: 2px solid var(--border-color);
        }}

        /* Lists */
        ul, ol {{
            padding-left: 1.5rem;
            margin-bottom: 1.5rem;
        }}

        li {{
            margin-bottom: 0.5rem;
        }}

        /* Images / Figures */
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            background-color: #ffffff;
            padding: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            display: block;
            margin: 2rem auto;
            border: 1px solid var(--border-color);
        }}
        
        img + em {{
            display: block;
            text-align: center;
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: -1rem;
            margin-bottom: 2rem;
        }}

        /* Math display block adjustments */
        .MathJax_Display {{
            margin: 2em 0 !important;
            overflow-x: auto;
            overflow-y: hidden;
        }}

        /* Footer */
        footer {{
            margin-top: 5rem;
            padding-top: 2rem;
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
            color: var(--accent);
            text-decoration: none;
        }}
        
        .footer-left a {{
            color: var(--text-secondary);
            text-decoration: underline;
        }}

        .footer-left a:hover, .footer-right a:hover {{
            text-decoration: none;
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
            // Build TOC
            const headings = document.querySelectorAll('.main-content h2');
            const toc = document.getElementById('toc');
            const headingElements = [];

            headings.forEach((heading, index) => {{
                // Create ID for heading if not exists
                if (!heading.id) {{
                    const text = heading.textContent;
                    // Remove leading numbers like "1. "
                    const cleanText = text.replace(/^\d+\.\s*/, '');
                    heading.id = cleanText.toLowerCase().replace(/[^a-z0-9]+/g, '-');
                }}
                
                headingElements.push(heading);

                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = '#' + heading.id;
                // Remove numbers for TOC display to look cleaner
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

print("Generated professional academic docs/index.html with fixed footer")

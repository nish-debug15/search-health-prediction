import os
import sys
import re

try:
    import markdown
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"])
    import markdown

# Read the markdown
with open('research_paper.md', 'r', encoding='utf-8') as f:
    md_text = f.read()

# Convert to HTML
html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'toc'])

# We want to replace the standard <h1> with our custom Hero section
hero_html = """
<header class="hero">
    <h1>Predictive Modeling of Search Engine Visibility Decay: A Machine Learning Approach for Proactive SEO</h1>
    <p class="subtitle">A Time-Aware Machine Learning Study on the FlyRank Search Intelligence Dataset</p>
    <div class="meta">
        <span class="author">Antigravity</span> &bull; <time datetime="2026-08-04">August 4, 2026</time>
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
            margin-bottom: 4rem;
            padding-bottom: 2rem;
            border-bottom: 1px solid var(--border-color);
        }}

        .hero h1 {{
            font-size: 2.25rem;
            margin-top: 0;
            margin-bottom: 1rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }}

        .hero .subtitle {{
            font-size: 1.25rem;
            color: var(--text-secondary);
            margin-bottom: 1.5rem;
        }}

        .hero .meta {{
            font-size: 0.95rem;
            color: var(--text-secondary);
        }}

        .hero .meta .author {{
            color: var(--text-primary);
            font-weight: 500;
        }}

        /* Links */
        .main-content a {{
            color: var(--accent);
            text-decoration: none;
        }}
        
        .main-content a:hover {{
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

        /* Math Equations */
        .math {{
            display: block;
            text-align: center;
            font-family: 'JetBrains Mono', monospace;
            margin: 1.5rem 0;
            padding: 1rem;
            color: var(--text-primary);
        }}
        
        /* Footer */
        footer {{
            margin-top: 5rem;
            padding-top: 2rem;
            border-top: 1px solid var(--border-color);
            font-size: 0.85rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-secondary);
        }}
        
        footer a {{
            color: var(--text-secondary);
        }}
        
        footer a:hover {{
            color: var(--accent);
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
                <div>
                    &copy; 2026 Antigravity. Built on the <a href="https://flyrank.ai" target="_blank">FlyRank ML Internship Dataset</a>.
                </div>
                <div>
                    <a href="https://github.com/nish-debug15/search-health-prediction" target="_blank">GitHub Repository</a>
                </div>
            </footer>
        </main>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            // Format Math formulas
            const ps = document.querySelectorAll('.main-content p');
            ps.forEach(p => {{
                if (p.textContent.trim().startsWith('$$') && p.textContent.trim().endsWith('$$')) {{
                    p.classList.add('math');
                    p.innerHTML = p.innerHTML.replace(/\$\$/g, '');
                }} else if (p.textContent.includes('$\le$')) {{
                    p.innerHTML = p.innerHTML.replace(/\$\\le\$/g, '≤');
                }} else if (p.textContent.includes('$\ge$')) {{
                    p.innerHTML = p.innerHTML.replace(/\$\\ge\$/g, '≥');
                }}
            }});
            
            const tds = document.querySelectorAll('td');
            tds.forEach(td => {{
                if (td.innerHTML.includes('$\\le$')) {{
                    td.innerHTML = td.innerHTML.replace(/\$\\le\$/g, '≤');
                }}
                if (td.innerHTML.includes('$\\ge$')) {{
                    td.innerHTML = td.innerHTML.replace(/\$\\ge\$/g, '≥');
                }}
            }});
            
            const lis = document.querySelectorAll('li');
            lis.forEach(li => {{
                if (li.innerHTML.includes('$\\ge$')) {{
                    li.innerHTML = li.innerHTML.replace(/\$\\ge\$/g, '≥');
                }}
            }});

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
        }});
    </script>
</body>
</html>
"""

os.makedirs('docs', exist_ok=True)
with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("Generated professional academic docs/index.html")

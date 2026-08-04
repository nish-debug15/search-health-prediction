import os
import sys

# Ensure pip dependencies are available
try:
    import markdown
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"])
    import markdown

# Read the markdown
with open('research_paper.md', 'r', encoding='utf-8') as f:
    md_text = f.read()

# Convert to HTML (including tables extension)
html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])

# Wrap in premium HTML template
html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Predictive Modeling of Search Engine Visibility Decay</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Outfit:wght@500;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0f111a;
            --surface-color: rgba(255, 255, 255, 0.03);
            --surface-border: rgba(255, 255, 255, 0.08);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-primary: #3b82f6;
            --accent-secondary: #8b5cf6;
            --accent-gradient: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            --table-border: rgba(255,255,255,0.1);
            --code-bg: #1e293b;
        }}

        body {{
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            line-height: 1.8;
            margin: 0;
            padding: 0;
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
        }}

        /* Dynamic Background */
        body::before {{
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.07) 0%, rgba(15, 17, 26, 0) 40%);
            z-index: -1;
            pointer-events: none;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 5rem 2rem;
        }}

        /* Typography */
        h1, h2, h3, h4 {{
            font-family: 'Outfit', sans-serif;
            color: #ffffff;
            margin-top: 3.5rem;
            margin-bottom: 1.5rem;
            line-height: 1.3;
        }}

        h1 {{
            font-size: 3.5rem;
            font-weight: 800;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 4rem;
            text-align: center;
            letter-spacing: -0.02em;
        }}

        h2 {{
            font-size: 2rem;
            border-bottom: 1px solid var(--surface-border);
            padding-bottom: 0.75rem;
            position: relative;
            letter-spacing: -0.01em;
        }}
        
        h2::after {{
            content: '';
            position: absolute;
            left: 0;
            bottom: -1px;
            width: 60px;
            height: 3px;
            background: var(--accent-gradient);
            border-radius: 3px;
        }}

        p {{
            margin-bottom: 1.75rem;
            color: var(--text-secondary);
            font-size: 1.05rem;
        }}

        strong {{
            color: var(--text-primary);
            font-weight: 600;
        }}

        /* Code and Preformatted text */
        pre {{
            background: var(--code-bg);
            border: 1px solid var(--surface-border);
            border-radius: 12px;
            padding: 1.5rem;
            overflow-x: auto;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            box-shadow: 0 20px 40px -15px rgba(0,0,0,0.5);
            margin: 2rem 0;
        }}

        code {{
            font-family: 'JetBrains Mono', monospace;
            background: rgba(255, 255, 255, 0.08);
            padding: 0.2rem 0.4rem;
            border-radius: 6px;
            font-size: 0.9em;
            color: #bae6fd;
        }}

        pre code {{
            background: transparent;
            padding: 0;
            color: #e2e8f0;
        }}

        /* Lists */
        ul, ol {{
            color: var(--text-secondary);
            margin-bottom: 2rem;
            padding-left: 1.5rem;
            font-size: 1.05rem;
        }}

        li {{
            margin-bottom: 0.75rem;
        }}

        li::marker {{
            color: var(--accent-primary);
        }}

        /* Tables */
        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 2.5rem 0;
            background: var(--surface-color);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(12px);
            border: 1px solid var(--surface-border);
        }}

        th, td {{
            padding: 1.25rem 1.5rem;
            text-align: left;
            border-bottom: 1px solid var(--table-border);
            font-size: 0.95rem;
        }}

        th {{
            background: rgba(255,255,255,0.03);
            font-weight: 700;
            color: var(--text-primary);
            font-family: 'Outfit', sans-serif;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.05em;
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr:hover td {{
            background: rgba(255,255,255,0.04);
            transition: background 0.3s ease;
        }}
        
        /* Math/Equations */
        .math {{
            font-family: 'JetBrains Mono', monospace;
            display: block;
            text-align: center;
            margin: 2rem 0;
            padding: 1.5rem;
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            color: #bae6fd;
            border: 1px dashed rgba(255,255,255,0.1);
        }}

        /* Links */
        a {{
            color: #60a5fa;
            text-decoration: none;
            position: relative;
            font-weight: 500;
        }}

        a::after {{
            content: '';
            position: absolute;
            width: 100%;
            height: 1px;
            bottom: -2px;
            left: 0;
            background-color: #60a5fa;
            transform: scaleX(0);
            transform-origin: bottom right;
            transition: transform 0.3s ease-out;
        }}

        a:hover::after {{
            transform: scaleX(1);
            transform-origin: bottom left;
        }}

        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .content-section {{
            animation: fadeIn 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }}
        
        /* Interactive hover states for data table rows */
        tbody tr {{
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        tbody tr:hover {{
            transform: scale(1.01);
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            z-index: 10;
            position: relative;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="content-section">
            {html_content}
        </div>
    </div>
    
    <script>
        // Simple script to format Math formulas inside the HTML output from markdown
        document.addEventListener('DOMContentLoaded', () => {{
            // Find paragraphs that are entirely math formulas
            const ps = document.querySelectorAll('p');
            ps.forEach(p => {{
                if (p.textContent.trim().startsWith('$$') && p.textContent.trim().endsWith('$$')) {{
                    p.classList.add('math');
                    // Remove the $$ signs
                    p.innerHTML = p.innerHTML.replace(/\$\$/g, '');
                }} else if (p.textContent.includes('$\le$')) {{
                    p.innerHTML = p.innerHTML.replace(/\$\\le\$/g, '≤');
                }} else if (p.textContent.includes('$\ge$')) {{
                    p.innerHTML = p.innerHTML.replace(/\$\\ge\$/g, '≥');
                }}
            }});
            
            // Format table cells with inline math
            const tds = document.querySelectorAll('td');
            tds.forEach(td => {{
                if (td.innerHTML.includes('$\\le$')) {{
                    td.innerHTML = td.innerHTML.replace(/\$\\le\$/g, '≤');
                }}
                if (td.innerHTML.includes('$\\ge$')) {{
                    td.innerHTML = td.innerHTML.replace(/\$\\ge\$/g, '≥');
                }}
            }});
            
            // Format list items with math
            const lis = document.querySelectorAll('li');
            lis.forEach(li => {{
                if (li.innerHTML.includes('$\\ge$')) {{
                    li.innerHTML = li.innerHTML.replace(/\$\\ge\$/g, '≥');
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

print("Generated docs/index.html")

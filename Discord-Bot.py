import discord
from discord.ext import commands
import json
import os
import asyncio
from datetime import datetime
import re

_bot_auth_ = "--Enter Discord Bot Auth Key Here--" 
SITE_URL = "https://theinternetarcade.com"
SITE_NAME = "The Internet Arcade"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'articles.json')
IMAGE_DIR = os.path.join(BASE_DIR, 'assets', 'media', 'image')
SITEMAP_FILE = os.path.join(BASE_DIR, 'sitemap.xml')

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def slugify(text):
    if not text: return "untitled"
    text = text.lower()
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')

def extract_youtube_id(url):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None

async def get_input(ctx, prompt, timeout=1200.0):
    """Helper to handle 'skip', 'back' and timeouts."""
    await ctx.send(prompt)
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        msg = await bot.wait_for('message', check=check, timeout=timeout)
        content = msg.content
        if content.lower() == 'skip': return "SKIP_SIGNAL"
        if content.lower() == 'back': return "BACK_SIGNAL"
        return msg
    except asyncio.TimeoutError:
        return "TIMEOUT_SIGNAL"

def update_sitemap():
    pages = [
        {"loc": "/", "priority": "1.0", "changefreq": "daily"},
        {"loc": "/quizzes.html", "priority": "0.8", "changefreq": "weekly"},
        {"loc": "/contact.html", "priority": "0.5", "changefreq": "monthly"},
    ]
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        for art in articles:
            pages.append({
                "loc": art['link'],
                "lastmod": art['date'],
                "priority": "0.7",
                "changefreq": "monthly"
            })
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for page in pages:
        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{SITE_URL}{page["loc"]}</loc>')
        if 'lastmod' in page:
            xml_lines.append(f'    <lastmod>{page["lastmod"]}</lastmod>')
        xml_lines.append(f'    <changefreq>{page["changefreq"]}</changefreq>')
        xml_lines.append(f'    <priority>{page["priority"]}</priority>')
        xml_lines.append('  </url>')
    xml_lines.append('</urlset>')
    with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml_lines))

def generate_html_file(article_data):
    quote_html = ""
    if article_data.get('quote'):
        author_html = f'<cite style="display: block; text-align: right; font-size: 1rem; margin-top: 15px; font-style: normal; opacity: 0.8;">— {article_data["quote_author"]}</cite>' if article_data.get('quote_author') else ""
        quote_html = f'<blockquote>"{article_data["quote"]}"{author_html}</blockquote>'

    authors_note_html = f'<div class="authors-note-box"><h3>AUTHOR\'S NOTE</h3><p>{article_data["authors_note"]}</p></div>' if article_data.get('authors_note') else ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{article_data['excerpt']}">
    <title>{article_data['title']} | {SITE_NAME}</title>
    <link rel="stylesheet" href="/assets/css/style.css">
    <link rel="stylesheet" href="/assets/css/articles.css">
</head>
<body>
    <div id="header-placeholder"></div>
    <main>
        <article class="article-container">
            <h1>{article_data['title']}</h1>
            <div class="meta-wrapper">
                <div class="meta-tag">DATE: {article_data['date']}</div>
                <div class="meta-tag">AUTHOR: {article_data['author']}</div>
                <div class="meta-tag">Category: {article_data['category']}</div>
            </div>
            <div class="article-body">
                <p>{article_data['excerpt']}</p>
                {quote_html}
    """
    for i, item in enumerate(article_data['content'], 1):
        media_html = f'<iframe width="100%" height="100%" src="https://www.youtube.com/embed/{item["media_content"]}" frameborder="0" allowfullscreen></iframe>' if item.get('media_type') == 'youtube' else f'<img src="/assets/media/image/{item["media_content"]}" style="width: 100%; height: 100%; object-fit: cover;">'
        html += f"""
                <div class="meme-entry">
                    <h2>{item['heading']}</h2>
                    <div class="main-image-wrapper" style="width: {item.get('width', 500)}px; height: {item.get('height', 500)}px; border: 5px solid #000;">
                        {media_html}
                    </div>
                    <p>{item['text']}</p>
                </div>"""
    
    html += f"""{authors_note_html}<div class="back-container"><a href="/index.html" class="back-btn">⬅ Back Home</a></div></div></article></main>
    <div id="footer-placeholder"></div>
    <script src="/assets/js/global.js"></script>
    <script src="/assets/js/article.js"></script>
</body></html>"""

    relative_path = article_data['link'].lstrip('/')
    full_path = os.path.join(BASE_DIR, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(html)
    return full_path

# --- COMMANDS ---

@bot.command(name="setf")
async def set_featured(ctx, article_id: int):
    """Sets a specific article as featured and updates the JSON data."""
    if not os.path.exists(DATA_FILE):
        return await ctx.send("No articles found to feature.")

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    found = False
    for art in articles:
        if art['id'] == article_id:
            art['isFeatured'] = True
            found = True
            title = art['title']
        else:
            art['isFeatured'] = False

    if not found:
        return await ctx.send(f"❌ Could not find article with ID: {article_id}")

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=4)

    update_sitemap()
    await ctx.send(f"⭐ **Featured Article Updated!**\nID: {article_id}\nTitle: {title}")

@bot.command(name="update-domain")
async def update_domain(ctx, new_domain: str):
    """Updates domain and asks for a new Brand Name to apply across the project."""
    global SITE_URL, SITE_NAME
    
    # Standardize domain
    clean_domain = new_domain.replace("https://", "").replace("http://", "").lower()
    new_site_url = f"https://{clean_domain}"
    
    # Ask for Brand Name
    brand_res = await get_input(ctx, "What is the new **Brand Name**? (e.g., *The Gaming Arcade*)")
    if isinstance(brand_res, str): return # Timeout or signal
    new_brand_name = brand_res.content

    # Values to replace
    old_domain_val = SITE_URL.replace("https://", "").replace("http://", "")
    old_brand_val = SITE_NAME
    
    modified_count = 0
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(('.html', '.json', '.xml', '.js', '.css', '.py')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    updated = text.replace(old_domain_val, clean_domain)
                    updated = updated.replace(old_brand_val, new_brand_name)
                    # Broad replacement for the arcade name specifically
                    updated = updated.replace("Internet Arcade", new_brand_name)
                    
                    if updated != text:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(updated)
                        modified_count += 1
                except: continue

    # Update current session
    SITE_URL = new_site_url
    SITE_NAME = new_brand_name
    update_sitemap()
    
    await ctx.send(
        f"✅ **Update Complete!**\n"
        f"**Domain:** `{clean_domain}`\n**Brand:** `{new_brand_name}`\n"
        f"**Files Modified:** {modified_count}"
    )

@bot.command()
async def remove(ctx, article_id: int):
    if not os.path.exists(DATA_FILE): return await ctx.send("No articles found.")
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    target = next((a for a in articles if a['id'] == article_id), None)
    if not target: return await ctx.send(f"Could not find article with ID: {article_id}")
    html_rel_path = target['link'].lstrip('/')
    html_full_path = os.path.join(BASE_DIR, html_rel_path)
    if os.path.exists(html_full_path):
        os.remove(html_full_path)
    new_articles = [a for a in articles if a['id'] != article_id]
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_articles, f, indent=4)
    update_sitemap()
    await ctx.send(f"✅ **Article {article_id} removed.**")

@bot.command()
async def post(ctx):
    data = {
        "title": "Untitled", "excerpt": "", "author": "Staff", "category": "News",
        "quote": "", "quote_author": "", "authors_note": "", "featured": "no",
        "image": "default-thumbnail.jpg", "content": []
    }
    steps = ["title", "excerpt", "author", "category", "want_quote", "quote", "quote_author", "want_note", "authors_note", "featured", "featured_img", "num_items"]
    step = 0
    while step < len(steps):
        current = steps[step]
        if current in ["quote", "quote_author"] and data.get("want_quote") != "yes":
            step += 1; continue
        if current == "authors_note" and data.get("want_note") != "yes":
            step += 1; continue
        prompts = {
            "title": "Enter **Headline**.", "excerpt": "Enter **Excerpt**.", "author": "Enter **Author Name**.", "category": "Enter **Category**.",
            "want_quote": "Include a **Quote Box**? (yes/skip)", "quote": "Enter **Quote Content**.", "quote_author": "Enter **Quote Author**.",
            "want_note": "Include an **Author's Note**? (yes/skip)", "authors_note": "Enter **Author's Note**.",
            "featured": "Is this **Featured**? (yes/skip)", "featured_img": "Upload **Featured Image** or 'skip'.", "num_items": "How many **Media Items**? (Number)"
        }
        res = await get_input(ctx, f"[Step {step+1}/{len(steps)}] {prompts[current]}")
        if res == "TIMEOUT_SIGNAL": return await ctx.send("Timed out.")
        if res == "BACK_SIGNAL": step = max(0, step - 1); continue
        content = res.content if hasattr(res, 'content') else ""
        if current == "featured_img":
            if hasattr(res, 'attachments') and res.attachments:
                att = res.attachments[0]
                fname = f"featured-{slugify(data['title'])}.{att.filename.split('.')[-1]}"
                await att.save(os.path.join(IMAGE_DIR, fname))
                data["image"] = fname
        elif current == "num_items":
            try: data["num_items"] = int(content)
            except: data["num_items"] = 0
        else:
            data[current] = content.lower() if "want_" in current else content
        step += 1
    for i in range(1, data.get("num_items", 0) + 1):
        await ctx.send(f"--- **Media Item {i}** ---")
        h_res = await get_input(ctx, "Heading:")
        t_res = await get_input(ctx, "Text:")
        type_res = await get_input(ctx, "Type (image/youtube):")
        m_content = ""
        if "youtube" in type_res.content.lower():
            link_res = await get_input(ctx, "YouTube Link:")
            m_content = extract_youtube_id(link_res.content) or "INVALID"
        else:
            img_res = await get_input(ctx, "Upload Image:")
            if hasattr(img_res, 'attachments') and img_res.attachments:
                att = img_res.attachments[0]
                m_content = f"{slugify(h_res.content)}-{i}.{att.filename.split('.')[-1]}"
                await att.save(os.path.join(IMAGE_DIR, m_content))
        data["content"].append({
            "heading": h_res.content, "text": t_res.content, "media_type": type_res.content.lower(),
            "media_content": m_content, "width": 500, "height": 500, "source": SITE_NAME
        })
    await finalize_article(ctx, data)

async def finalize_article(ctx, data):
    articles = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            articles = json.load(f)
    if data.get('featured') == 'yes':
        for art in articles: art['isFeatured'] = False
    new_id = max([art['id'] for art in articles] + [0]) + 1
    new_article = {
        "id": new_id, "title": data['title'], "excerpt": data['excerpt'], "category": data['category'],
        "author": data['author'], "quote": data['quote'], "quote_author": data['quote_author'],
        "authors_note": data['authors_note'], "date": datetime.now().strftime("%Y-%m-%d"),
        "image": data['image'], "link": f"/articles/{datetime.now().year}/{slugify(data['title'])}.html",
        "isFeatured": data.get('featured') == 'yes', "content": data['content']
    }
    articles.append(new_article)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=4)
    generate_html_file(new_article)
    update_sitemap()
    await ctx.send(f"✅ **Published!** ID: {new_id}\nURL: {SITE_URL}{new_article['link']}")

bot.run(_bot_auth_)

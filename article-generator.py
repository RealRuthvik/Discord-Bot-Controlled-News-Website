import discord
from discord.ext import commands
import json
import os
import asyncio
from datetime import datetime
import re

# ================= CONFIGURATION =================
# SECURITY WARNING: Never share your token publicly.
TOKEN = "" 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'articles.json')
IMAGE_DIR = os.path.join(BASE_DIR, 'media', 'image')

# Ensure directories exist
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= HELPER FUNCTIONS =================

def slugify(text):
    """Converts 'Hello World!' to 'hello-world'"""
    text = text.lower()
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')

def generate_html_file(article_data):
    """Generates the HTML string and saves it to a file."""
    
    # 1. PREPARE OPTIONAL HTML SNIPPETS
    
    quote_html = ""
    if article_data.get('quote'):
        quote_html = f"""
                <blockquote>
                    "{article_data['quote']}"
                </blockquote>
        """

    authors_note_html = ""
    if article_data.get('authors_note'):
        authors_note_html = f"""
                <div class="authors-note-box">
                    <h3>AUTHOR'S NOTE</h3>
                    <p>{article_data['authors_note']}</p>
                </div>
        """

    # 2. GENERATE FULL HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article_data['title']}</title>
    <link rel="stylesheet" href="/css/style.css">
    
    <style>
        /* --- ARTICLE SPECIFIC "POP" STYLES --- */

        main {{
            display: flex;
            justify-content: center;
            padding-bottom: 80px;
        }}

        .article-container {{
            background-color: var(--bg-card);
            /* Cream/White */
            border: 4px solid var(--border-color);
            padding: 3rem;
            max-width: 800px;
            width: 100%;
            margin-top: 20px;
            /* THE BIG POP: Deep Purple Hard Shadow */
            box-shadow: 15px 15px 0px var(--accent-purple);
            position: relative;
            /* Ensure images don't overflow the rounded corners or borders */
            box-sizing: border-box;
        }}

        /* --- HEADER SECTION --- */
        h1 {{
            font-size: 3rem;
            line-height: 1;
            margin-bottom: 20px;
            color: var(--text-dark);
            text-transform: uppercase;
            text-shadow: 3px 3px 0px var(--bg-header);
            word-wrap: break-word; /* Prevents long words from breaking layout */
        }}

        .meta-wrapper {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-bottom: 30px;
            font-family: monospace;
            font-size: 1rem;
        }}

        .meta-tag {{
            background-color: var(--bg-main);
            /* Yellow */
            border: 2px solid var(--border-color);
            padding: 5px 15px;
            font-weight: 900;
            box-shadow: 3px 3px 0px var(--border-color);
            transform: rotate(-1deg);
        }}

        .meta-tag:nth-child(even) {{
            transform: rotate(2deg);
            background-color: var(--accent-blue);
            /* Blue */
        }}

        .meta-tag:nth-child(3) {{
            background-color: var(--accent-red);
            /* Red */
            color: white;
        }}

        /* --- IMAGE SECTION --- */
        .main-image-container {{
            margin-bottom: 40px;
            position: relative;
        }}

        .list-image {{
            width: 100%;
            height: auto;
            overflow: hidden;
        }}

        .hero-image {{
            height: 500px;
        }}

        .main-image-wrapper {{
            width: 100%;
            background-color: var(--text-dark);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--bg-card);
            font-size: 1.5rem;
            font-weight: bold;
            border: 4px solid var(--border-color);
            text-transform: uppercase;
            box-sizing: border-box; /* Ensures border doesn't add to width */
        }}

        .image-caption {{
            background-color: var(--text-dark);
            color: white;
            padding: 5px 10px;
            font-family: monospace;
            font-size: 0.9rem;
            display: inline-block;
            margin-top: -10px;
            position: relative;
            z-index: 2;
            max-width: 100%; /* Prevents caption from overflowing */
        }}

        /* LINK FIX */
        .image-caption a {{
            color: inherit;
            text-decoration: none;
            font-weight: bold;
            border-bottom: 1px dashed white;
        }}

        .image-caption a:hover {{
            opacity: 0.8;
            border-bottom: 1px solid white;
        }}

        /* --- CONTENT TYPOGRAPHY --- */
        .article-body p {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 1.15rem;
            line-height: 1.6;
            margin-bottom: 1.5rem;
            color: #333;
        }}

        .highlight-text {{
            background-color: var(--accent-green);
            padding: 0 5px;
            font-weight: bold;
            box-decoration-break: clone;
            -webkit-box-decoration-break: clone;
        }}

        blockquote {{
            background-color: var(--bg-header);
            /* Pink */
            color: var(--text-dark);
            border: 4px solid var(--border-color);
            margin: 40px 0;
            padding: 25px;
            font-size: 1.4rem;
            font-style: italic;
            font-weight: 900;
            line-height: 1.3;
            box-shadow: 8px 8px 0px var(--border-color);
            position: relative;
        }}

        blockquote::before {{
            content: "“";
            font-size: 8rem;
            position: absolute;
            top: -60px;
            left: -20px;
            color: var(--text-dark);
            opacity: 0.2;
            font-family: serif;
        }}

        /* --- NEW STYLES FOR LISTICLE FORMAT --- */

        .meme-entry {{
            margin-bottom: 50px;
            padding-bottom: 30px;
            border-bottom: 4px dashed var(--border-color);
        }}

        .article-body h2 {{
            font-size: 1.8rem;
            text-transform: uppercase;
            color: var(--text-dark);
            background-color: var(--accent-blue);
            display: inline-block;
            padding: 10px 15px;
            border: 3px solid var(--border-color);
            box-shadow: 5px 5px 0px var(--bg-main);
            margin-top: 20px;
            margin-bottom: 25px;
            transform: rotate(-1deg);
        }}

        /* --- AUTHORS NOTE BOX --- */
        .authors-note-box {{
            background-color: var(--accent-green);
            border: 4px solid var(--border-color);
            padding: 20px;
            text-align: center;
            transform: rotate(-1.5deg);
            margin-top: 50px;
            box-shadow: 6px 6px 0px var(--border-color);
            outline: 2px dashed var(--border-color);
            outline-offset: -10px;
        }}

        .authors-note-box h3 {{
            font-size: 1.5rem;
            margin-bottom: 10px;
            text-decoration: underline;
            text-decoration-thickness: 3px;
        }}

        /* --- BACK BUTTON --- */
        .back-container {{
            text-align: center;
            margin-top: 40px;
        }}

        .back-btn {{
            background-color: var(--text-dark);
            color: white;
            padding: 15px 30px;
            font-weight: 900;
            text-decoration: none;
            text-transform: uppercase;
            border: 3px solid transparent;
            font-size: 1.1rem;
            display: inline-block;
            transition: 0.2s;
        }}

        .back-btn:hover {{
            background-color: var(--bg-main);
            color: var(--text-dark);
            border: 3px solid var(--border-color);
            box-shadow: 5px 5px 0px var(--border-color);
        }}

        /* =========================================
           MOBILE OPTIMIZATION (THE FIX)
           ========================================= */
        @media(max-width: 600px) {{
            .article-container {{
                padding: 1.5rem;
                /* Smaller padding */
                box-shadow: 8px 8px 0px var(--accent-purple);
                width: 95%;
                /* Ensure it fits in viewport */
                margin-left: auto;
                margin-right: auto;
            }}

            h1 {{
                font-size: 2rem;
            }}

            blockquote {{
                font-size: 1.1rem;
                padding: 15px;
            }}

            .article-body h2 {{
                font-size: 1.2rem;
                padding: 5px 10px;
            }}

            /* --- THE IMAGE FIX --- */
            /* This overrides the inline styles you set in HTML */
            .main-image-wrapper {{
                width: 100% !important;
                /* Forces full width of phone screen */
                height: auto !important;
                /* Unlocks fixed height so it doesn't stretch */
                margin-left: 0 !important;
                margin-right: 0 !important;
                aspect-ratio: auto !important;
            }}

            /* Ensure image fills the container */
            .main-image-wrapper img {{
                width: 100% !important;
                height: auto !important;
                object-fit: contain !important;
            }}
        }}
    </style>
</head>
<body>
    <div id="header-placeholder"></div>
    <main>
        <article class="article-container">
            <h1>{article_data['title']}</h1>
            <div class="meta-wrapper">
                <div class="meta-tag">DATE: {article_data['date']}</div>
                <div class="meta-tag">AUTHOR: {article_data['author']}</div>
                <div class="meta-tag">MOOD: {article_data['category']}</div>
            </div>
            <div class="article-body">
                <p>{article_data['excerpt']}</p>
                
                {quote_html}
    """

    # Add Dynamic Content (The Images/List Items)
    # NOTE: prepending /media/image/ here because JSON only has filename
    for i, item in enumerate(article_data['content'], 1):
        # Get dimensions, defaulting to 500 if missing (for backward compatibility)
        width = item.get('width', 500)
        height = item.get('height', 500)

        html += f"""
                <div class="meme-entry" id="meme-{i}">
                    <h2>#{i} {item['heading']}</h2>
                    <div class="main-image-container">
                        <div class="main-image-wrapper list-image" style="width: {width}px; height: {height}px; margin: 0; border: 5px solid #000;">
                            <img src="/media/image/{item['image']}" alt="{item['heading']}" style="width: 100%; height: 100%; object-fit: cover; display: block;">
                        </div>
                        <div class="image-caption">Source: {item['source']}</div>
                    </div>
                    <p>{item['text']}</p>
                </div>
        """

    # Add Author's Note and Footer
    html += f"""
                {authors_note_html}

                <div class="back-container"><a href="/index.html" class="back-btn">Back Home</a></div>
            </div>
        </article>
    </main>
    <div id="footer-placeholder"></div>
    <script src="/js/global.js"></script>
</body>
</html>
    """

    # Determine Path and Save
    relative_path = article_data['link'].lstrip('/')
    full_path = os.path.join(BASE_DIR, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    return full_path
# ================= THE BOT COMMAND =================

@bot.command()
async def post(ctx):
    """Interactive wizard to create a full article with professional tone."""
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        # --- STEP 1: GENERAL METADATA ---
        await ctx.send("Initiating article creation process. Please enter the article **Headline**.")
        msg = await bot.wait_for('message', check=check, timeout=120.0)
        title = msg.content

        await ctx.send("Please enter the **Excerpt** (introduction text).")
        msg = await bot.wait_for('message', check=check, timeout=120.0)
        excerpt = msg.content

        await ctx.send("Please enter the **Author Name**.")
        msg = await bot.wait_for('message', check=check, timeout=120.0)
        author = msg.content

        await ctx.send("Please enter the **Category**.")
        msg = await bot.wait_for('message', check=check, timeout=120.0)
        category = msg.content

        # --- STEP 2: OPTIONAL BOXES ---
        
        quote_text = ""
        await ctx.send("Do you wish to include a **Quote Box**? (Yes/No)")
        msg = await bot.wait_for('message', check=check, timeout=60.0)
        if msg.content.lower() in ['yes', 'y']:
            await ctx.send("Please enter the content for the quote.")
            msg = await bot.wait_for('message', check=check, timeout=120.0)
            quote_text = msg.content

        authors_note_text = ""
        await ctx.send("Do you wish to include an **Author's Note** at the end? (Yes/No)")
        msg = await bot.wait_for('message', check=check, timeout=60.0)
        if msg.content.lower() in ['yes', 'y']:
            await ctx.send("Please enter the content for the author's note.")
            msg = await bot.wait_for('message', check=check, timeout=120.0)
            authors_note_text = msg.content

        # --- STEP 3: IS FEATURED CHECK ---
        await ctx.send("Is this a **Featured Article**? (Yes/No)\n*Note: Answering 'Yes' will remove 'Featured' status from any existing article.*")
        msg = await bot.wait_for('message', check=check, timeout=60.0)
        is_featured = msg.content.lower() in ['yes', 'y']

        # --- STEP 4: FEATURED IMAGE (MAIN) ---
        await ctx.send("Please upload the **Featured Image** for the article thumbnail (to be stored in JSON).")
        msg = await bot.wait_for('message', check=check, timeout=120.0)
        
        if not msg.attachments:
            await ctx.send("No attachment detected. Process aborted.")
            return
            
        # Save Featured Image
        featured_attachment = msg.attachments[0]
        f_ext = featured_attachment.filename.split('.')[-1]
        featured_filename = f"featured-{slugify(title)}.{f_ext}"
        featured_save_path = os.path.join(IMAGE_DIR, featured_filename)
        await featured_attachment.save(featured_save_path)
        
        await ctx.send("Featured image saved successfully.")

        # --- STEP 5: IMAGE COUNT ---
        await ctx.send("Please enter the number of list items (images) to include.")
        msg = await bot.wait_for('message', check=check, timeout=120.0)
        try:
            num_images = int(msg.content)
        except ValueError:
            await ctx.send("Invalid input. A numeric value is required. Process aborted.")
            return

        # --- STEP 6: LOOP FOR CONTENT ---
        content_list = []
        
        for i in range(1, num_images + 1):
            await ctx.send(f"--- **Item {i}** ---\nPlease enter the **Heading** for this item.")
            msg = await bot.wait_for('message', check=check, timeout=120.0)
            heading = msg.content

            await ctx.send(f"Please enter the **Description Text** for: {heading}")
            msg = await bot.wait_for('message', check=check, timeout=300.0)
            text = msg.content

            await ctx.send("Please enter the **Image Source** (e.g., specific website or photographer).")
            msg = await bot.wait_for('message', check=check, timeout=60.0)
            source = msg.content

            # --- Ask for Image Dimensions ---
            await ctx.send(f"Please enter the **Width** for image {i} in pixels (e.g., 500).")
            msg = await bot.wait_for('message', check=check, timeout=60.0)
            try:
                img_width = int(msg.content)
            except ValueError:
                await ctx.send("Invalid input. Defaulting width to 500.")
                img_width = 500

            await ctx.send(f"Please enter the **Height** for image {i} in pixels (e.g., 500).")
            msg = await bot.wait_for('message', check=check, timeout=60.0)
            try:
                img_height = int(msg.content)
            except ValueError:
                await ctx.send("Invalid input. Defaulting height to 500.")
                img_height = 500
            # --------------------------------

            await ctx.send(f"Please upload the **Image** for item {i}.")
            msg = await bot.wait_for('message', check=check, timeout=120.0)

            if not msg.attachments:
                await ctx.send("No attachment detected. Skipping this item.")
                continue

            # Save List Item Image
            attachment = msg.attachments[0]
            file_ext = attachment.filename.split('.')[-1]
            safe_filename = f"{slugify(heading)}-{i}.{file_ext}"
            save_path = os.path.join(IMAGE_DIR, safe_filename)
            await attachment.save(save_path)

            # Store ONLY filename in JSON as requested
            content_list.append({
                "heading": heading,
                "text": text,
                "source": source,
                "image": safe_filename,
                "width": img_width,  # Store width
                "height": img_height # Store height
            })
            
            await ctx.send("Item saved.")

        # --- STEP 7: UPDATE JSON ---
        current_year = datetime.now().year
        slug = slugify(title)
        
        # Load existing articles
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                articles = json.load(f)
        else:
            articles = []

        # LOGIC TO TOGGLE FEATURED STATUS
        # If the user selected Yes (is_featured = True), we must un-feature all others
        if is_featured:
            for art in articles:
                if art.get('isFeatured', False):
                    art['isFeatured'] = False

        new_id = 1
        if articles:
            new_id = max(art['id'] for art in articles) + 1

        new_article = {
            "id": new_id,
            "title": title,
            "excerpt": excerpt,
            "category": category,
            "author": author,
            "quote": quote_text,   
            "authors_note": authors_note_text,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "image": featured_filename, 
            "link": f"/articles/{current_year}/{slug}.html",
            "isFeatured": is_featured, # Uses the user's choice
            "content": content_list
        }

        articles.append(new_article)

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=4)

        # --- STEP 8: GENERATE HTML ---
        html_path = generate_html_file(new_article)

        # --- DONE ---
        embed = discord.Embed(title="Article Published", color=discord.Color.blue())
        embed.add_field(name="Headline", value=title, inline=False)
        embed.add_field(name="Featured?", value=str(is_featured), inline=True)
        embed.add_field(name="Output Path", value=f"`{html_path}`", inline=False)
        await ctx.send(embed=embed)

    except asyncio.TimeoutError:
        await ctx.send("Operation timed out due to inactivity.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        print(e)
        
# Run Bot
bot.run(TOKEN)
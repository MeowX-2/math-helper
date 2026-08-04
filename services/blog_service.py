"""
HintSpark — Blog Service Module
================================
Manages JSON storage, retrieval, filtering, and read-time estimations for math articles.
"""

import os
import json
import time
import math
from datetime import datetime

# Path to local JSON storage for blog posts
DATA_FILE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data', 'blogs.json'))


def load_blogs():
    """
    Load blog entries from local JSON storage file.
    Returns an empty list if the file does not exist or fails to parse.
    """
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading blogs data: {e}")
        return []


def save_blogs(blogs):
    """
    Save list of blog objects into local JSON storage file using atomic file replacement.
    Prevents file corruption on unexpected interruptions or concurrent writes.
    """
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    temp_file = DATA_FILE + '.tmp'
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(blogs, f, indent=2, ensure_ascii=False)
        os.replace(temp_file, DATA_FILE)
    except Exception as e:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass
        raise e


def delete_blog(blog_id):
    """
    Delete a math article by its ID.
    Returns True if removed, False if not found.
    """
    blogs = load_blogs()
    original_count = len(blogs)
    filtered = [b for b in blogs if str(b.get('id')) != str(blog_id)]
    if len(filtered) < original_count:
        save_blogs(filtered)
        return True
    return False


def calculate_read_time(content):
    """
    Calculate estimated reading time based on word count and inline/display LaTeX math blocks.
    """
    if not content:
        return "1 min read"
        
    words = len(content.split())
    display_math = content.count('$$') // 2
    raw_dollars = content.count('$') - (display_math * 4)
    inline_math = max(0, raw_dollars // 2)

    total_seconds = (words / 150.0 * 60) + (inline_math * 15) + (display_math * 30)
    minutes = max(1, math.ceil(total_seconds / 60))
    return f"{minutes} min read"


def get_filtered_blogs(category='All', search='', tag=''):
    """
    Fetch articles filtered by category, tag, and search keyword, sorted by date descending.
    """
    category = (category or 'All').strip()
    search = (search or '').strip().lower()
    tag = (tag or '').strip().lower()
    blogs = load_blogs()

    if category and category != 'All':
        blogs = [
            b for b in blogs
            if b.get('category', '').lower() == category.lower()
            or any(category.lower() == t.lower() for t in b.get('tags', []))
        ]

    if tag and tag != 'all':
        blogs = [
            b for b in blogs
            if any(tag.lower() == t.lower() for t in b.get('tags', []))
            or b.get('category', '').lower() == tag.lower()
        ]
        
    if search:
        blogs = [
            b for b in blogs
            if search in b.get('title', '').lower()
            or search in b.get('subtitle', '').lower()
            or search in b.get('content', '').lower()
            or search in b.get('author', '').lower()
            or any(search in t.lower() for t in b.get('tags', []))
        ]

    blogs.sort(key=lambda x: x.get('id', '0'), reverse=True)
    return blogs


def create_new_blog(data):
    """
    Create and save a new math article.
    """
    title = data.get('title', '').strip()
    subtitle = data.get('subtitle', '').strip()
    author = data.get('author', '').strip() or 'Anonymous Math Writer'
    category = data.get('category', 'General').strip()
    tags_raw = data.get('tags', [])
    content = data.get('content', '').strip()

    if not title or not content:
        raise ValueError('Title and content are required.')

    if isinstance(tags_raw, str):
        tags = [t.strip() for t in tags_raw.split(',') if t.strip()]
    else:
        tags = [str(t).strip() for t in tags_raw if str(t).strip()]

    blogs = load_blogs()
    new_blog = {
        'id': str(int(time.time() * 1000)),
        'title': title,
        'subtitle': subtitle,
        'author': author,
        'category': category,
        'tags': tags if tags else [category],
        'date': datetime.now().strftime('%B %d, %Y'),
        'read_time': calculate_read_time(content),
        'content': content
    }
    blogs.insert(0, new_blog)
    save_blogs(blogs)
    return new_blog

import re

with open('css/main.css', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Search box mobile alignment
# Find the .search-box under @media (max-width: 768px)
search_box_old = """    .search-box {
        padding: 15px;
        margin: 0 10px;
        max-width: calc(100vw - 20px);
        width: 100%;
        overflow: hidden;
    }"""
search_box_new = """    .search-box {
        padding: 15px;
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
        overflow: hidden;
    }"""
content = content.replace(search_box_old, search_box_new)

# Fix 2: Remove display:none for hero-video-bg, .footer-video-bg on mobile
video_hide_old = """    .hero-video-bg, .footer-video-bg {
        display: none !important; /* Hide heavy videos on mobile to prevent layout lag */
    }"""
video_hide_new = """    .hero-video-bg, .footer-video-bg {
        /* display: none !important; Removed to allow videos on mobile */
        pointer-events: none;
    }"""
content = content.replace(video_hide_old, video_hide_new)

with open('css/main.css', 'w', encoding='utf-8') as f:
    f.write(content)

print("CSS updated")

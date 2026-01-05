import os
import uuid
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from datetime import datetime

# --- Configuration ---
BASE_URL = "https://yourdomain.com"  # Replace with your actual domain
LIMIT_PER_SITEMAP = 5000
PUBLIC_DIR = "."  # Directory containing your website files
EXTENSIONS_TO_INCLUDE = ('.html', '.php')
OUTPUT_DIR = "."

def get_all_files(directory):
    """Fetch all file paths that end with the specified extensions"""
    files_list = []
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories and system folders
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '.github', '.git']]
        for file in files:
            if file.endswith(EXTENSIONS_TO_INCLUDE):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, directory)
                
                # Handle index files as root URLs
                if relative_path == "index.html" or relative_path == "index.php":
                    url_path = ""
                else:
                    url_path = relative_path.replace("\\", "/")
                
                files_list.append(f"{BASE_URL}/{url_path}")
    return files_list

def create_sitemap_file(urls, filename):
    """Create a sub-sitemap XML file"""
    urlset = Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for url in urls:
        url_el = SubElement(urlset, 'url')
        loc = SubElement(url_el, 'loc')
        loc.text = url
        lastmod = SubElement(url_el, 'lastmod')
        lastmod.text = datetime.now().strftime('%Y-%m-%d')
    
    tree = ElementTree(urlset)
    tree.write(os.path.join(OUTPUT_DIR, filename), encoding='utf-8', xml_declaration=True)

def create_index_sitemap(sitemap_files, filename):
    """Create the main Sitemap Index file"""
    sitemapindex = Element('sitemapindex', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for s_file in sitemap_files:
        sitemap_el = SubElement(sitemapindex, 'sitemap')
        loc = SubElement(sitemap_el, 'loc')
        loc.text = f"{BASE_URL}/{s_file}"
        lastmod = SubElement(sitemap_el, 'lastmod')
        lastmod.text = datetime.now().strftime('%Y-%m-%d')
    
    tree = ElementTree(sitemapindex)
    tree.write(os.path.join(OUTPUT_DIR, filename), encoding='utf-8', xml_declaration=True)

def create_robots_txt(main_sitemap_url):
    """Automatically generate robots.txt and link the main sitemap"""
    content = f"User-agent: *\nAllow: /\n\nSitemap: {main_sitemap_url}\n"
    with open(os.path.join(OUTPUT_DIR, "robots.txt"), "w") as f:
        f.write(content)
    print("robots.txt generated successfully.")

def main():
    print("Starting Sitemap and Robots generation...")
    all_urls = list(set(get_all_files(PUBLIC_DIR))) # set to prevent duplicates
    print(f"Found {len(all_urls)} URLs.")

    # Split URLs into chunks (5000 links each)
    chunks = [all_urls[i:i + LIMIT_PER_SITEMAP] for i in range(0, len(all_urls), LIMIT_PER_SITEMAP)]
    
    generated_files = []
    for i, chunk in enumerate(chunks):
        # Generate random filename
        random_name = f"sitemap-{uuid.uuid4().hex[:8]}.xml"
        create_sitemap_file(chunk, random_name)
        generated_files.append(random_name)
        print(f"Sub-sitemap created: {random_name}")

    # Create Main Sitemap Index
    main_sitemap_name = "sitemap.xml"
    create_index_sitemap(generated_files, main_sitemap_name)
    print(f"Main index {main_sitemap_name} created.")

    # Generate Robots.txt
    create_robots_txt(f"{BASE_URL}/{main_sitemap_name}")

if __name__ == "__main__":
    main()

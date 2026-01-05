import os
import uuid
import urllib.request
import glob
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from datetime import datetime

# --- الإعدادات ---
BASE_URL = "https://yourdomain.com"  # استبدله برابط موقعك الحقيقي
LIMIT_PER_SITEMAP = 5000
PUBLIC_DIR = "."  # المجلد الذي يحتوي على ملفات الموقع
EXTENSIONS_TO_INCLUDE = ('.html', '.php')
OUTPUT_DIR = "."

def get_all_files(directory):
    """جلب كافة المسارات للملفات التي تنتهي بالامتدادات المحددة"""
    files_list = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '.github', '.git']]
        for file in files:
            if file.endswith(EXTENSIONS_TO_INCLUDE):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, directory)
                
                if relative_path == "index.html" or relative_path == "index.php":
                    url_path = ""
                else:
                    url_path = relative_path.replace("\\", "/")
                
                files_list.append(f"{BASE_URL}/{url_path}")
    return list(set(files_list))

def create_sitemap_file(urls, filename):
    """إنشاء ملف XML لسايت ماب فرعي"""
    urlset = Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for url in urls:
        url_el = SubElement(urlset, 'url')
        loc = SubElement(url_el, 'loc')
        loc.text = url
        lastmod = SubElement(url_el, 'lastmod')
        lastmod.text = datetime.now().strftime('%Y-%m-%d')
    
    tree = ElementTree(urlset)
    tree.write(os.path.join(OUTPUT_DIR, filename), encoding='utf-8', xml_declaration=True)

def create_index_sitemap(filename):
    """إنشاء ملف Sitemap Index الرئيسي عبر البحث عن كافة ملفات السايت ماب الفرعية في المجلد"""
    sitemapindex = Element('sitemapindex', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    
    # البحث عن جميع ملفات xml التي تبدأ بكلمة sitemap-
    sitemap_files = glob.glob(os.path.join(OUTPUT_DIR, "sitemap-*.xml"))
    
    for s_path in sitemap_files:
        s_file = os.path.basename(s_path)
        sitemap_el = SubElement(sitemapindex, 'sitemap')
        loc = SubElement(sitemap_el, 'loc')
        loc.text = f"{BASE_URL}/{s_file}"
        lastmod = SubElement(sitemap_el, 'lastmod')
        lastmod.text = datetime.now().strftime('%Y-%m-%d')
    
    tree = ElementTree(sitemapindex)
    tree.write(os.path.join(OUTPUT_DIR, filename), encoding='utf-8', xml_declaration=True)
    print(f"تم تحديث المؤشر الرئيسي ليشمل {len(sitemap_files)} ملف فرعي.")

def create_robots_txt(main_sitemap_url):
    """إنشاء ملف robots.txt وربط السايت ماب الرئيسي"""
    content = f"User-agent: *\nAllow: /\n\nSitemap: {main_sitemap_url}\n"
    with open(os.path.join(OUTPUT_DIR, "robots.txt"), "w") as f:
        f.write(content)
    print("تم إنشاء ملف robots.txt بنجاح.")

def ping_search_engines(sitemap_url):
    """إرسال إشعار لمحركات البحث بوجود تحديث"""
    print("جاري إخطار محركات البحث...")
    bing_url = f"https://www.bing.com/ping?sitemap={sitemap_url}"
    try:
        urllib.request.urlopen(bing_url)
        print("تم إخطار Bing بنجاح.")
    except Exception as e:
        print(f"فشل إخطار Bing: {e}")

def main():
    print("بدء عملية توليد الملفات للأرشفة...")
    all_urls = get_all_files(PUBLIC_DIR)
    
    if not all_urls:
        print("لم يتم العثور على روابط للأرشفة.")
        return

    # تقسيم الروابط (5000 رابط لكل ملف)
    chunks = [all_urls[i:i + LIMIT_PER_SITEMAP] for i in range(0, len(all_urls), LIMIT_PER_SITEMAP)]
    
    for i, chunk in enumerate(chunks):
        random_name = f"sitemap-{uuid.uuid4().hex[:8]}.xml"
        create_sitemap_file(chunk, random_name)

    main_sitemap_name = "sitemap.xml"
    
    # التعديل هنا: السكربت الآن يبحث عن كل الملفات الموجودة في المجلد ويضيفها
    create_index_sitemap(main_sitemap_name)
    
    create_robots_txt(f"{BASE_URL}/{main_sitemap_name}")
    ping_search_engines(f"{BASE_URL}/{main_sitemap_name}")
    print("اكتملت جميع العمليات!")

if __name__ == "__main__":
    main()

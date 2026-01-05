import os
import uuid
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from datetime import datetime

# --- الإعدادات ---
BASE_URL = "https://v3.reactnavigation.org/"  # استبدله برابط موقعك
LIMIT_PER_SITEMAP = 5000
PUBLIC_DIR = "."  # المجلد الذي يحتوي على ملفات الموقع (مثلاً 'public' أو '.')
EXTENSIONS_TO_INCLUDE = ('.html', '.php') # الامتدادات المطلوبة
OUTPUT_DIR = "." # مكان حفظ ملفات السايت ماب

def get_all_files(directory):
    """جلب كافة المسارات للملفات التي تنتهي بالامتدادات المحددة"""
    files_list = []
    for root, dirs, files in os.walk(directory):
        # تخطي المجلدات المخفية ومجلدات النظام
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        for file in files:
            if file.endswith(EXTENSIONS_TO_INCLUDE):
                full_path = os.path.join(root, file)
                # تحويل المسار إلى رابط URL
                relative_path = os.path.relpath(full_path, directory)
                if relative_path == "index.html":
                    url_path = ""
                else:
                    url_path = relative_path.replace("\\", "/")
                
                files_list.append(f"{BASE_URL}/{url_path}")
    return files_list

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

def create_index_sitemap(sitemap_files, filename):
    """إنشاء ملف Sitemap Index الرئيسي"""
    sitemapindex = Element('sitemapindex', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for s_file in sitemap_files:
        sitemap_el = SubElement(sitemapindex, 'sitemap')
        loc = SubElement(sitemap_el, 'loc')
        loc.text = f"{BASE_URL}/{s_file}"
        lastmod = SubElement(sitemap_el, 'lastmod')
        lastmod.text = datetime.now().strftime('%Y-%m-%d')
    
    tree = ElementTree(sitemapindex)
    tree.write(os.path.join(OUTPUT_DIR, filename), encoding='utf-8', xml_declaration=True)

def main():
    print("جاري بدء عملية توليد السايت ماب...")
    all_urls = get_all_files(PUBLIC_DIR)
    print(f"تم العثور على {len(all_urls)} رابط.")

    # تقسيم الروابط إلى مجموعات (كل مجموعة 5000 رابط)
    chunks = [all_urls[i:i + LIMIT_PER_SITEMAP] for i in range(0, len(all_urls), LIMIT_PER_SITEMAP)]
    
    generated_files = []
    for i, chunk in enumerate(chunks):
        # توليد اسم عشوائي للملف
        random_name = f"sitemap-{uuid.uuid4().hex[:8]}.xml"
        create_sitemap_file(chunk, random_name)
        generated_files.append(random_name)
        print(f"تم إنشاء الملف الفرعي: {random_name}")

    # إنشاء الملف الرئيسي
    create_index_sitemap(generated_files, "sitemap.xml")
    print("تم إنشاء ملف sitemap.xml الرئيسي بنجاح.")

if __name__ == "__main__":
    main()

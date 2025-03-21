import requests
from bs4 import BeautifulSoup
import re

SOCIAL_MEDIA_DOMAINS = ["facebook.com", "instagram.com", "youtube.com"]
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"\+?[\d\s().-]{9,}\d")

def is_invalid_link(url):
    return any(domain in url for domain in SOCIAL_MEDIA_DOMAINS) or url.endswith("#") or EMAIL_PATTERN.match(url)

def extract_info_from_section(section, keyword):
    if not section:
        return None
    element = section.find(string=re.compile(rf'\b{keyword}\b', re.I))
    if element:
        parent = element.parent
        parts = re.split(rf'{keyword}:?', parent.get_text(), flags=re.I)
        if len(parts) > 1:
            return parts[1].strip()
    return None

def extract_kazakhstan_info(kz_section):
    if not kz_section:
        return None, set(), None

    address = extract_info_from_section(kz_section, r'Юридический адрес')
    phones = set()
    phone_tags = kz_section.find_all(string=re.compile(r'Тел\.|Phone:', re.I))
    for tag in phone_tags:
        phones.update(PHONE_PATTERN.findall(tag))
    
    website = None
    site_tag = kz_section.find('a', href=True, string=re.compile(r'Веб-сайт|Website', re.I))
    if site_tag:
        website = site_tag['href']
    else:
        site_tag = kz_section.find(string=re.compile(r'Веб-сайт|Website', re.I))
        if site_tag:
            website = site_tag.find_next('a')['href'] if site_tag.find_next('a') else None
    
    return address, phones, website

def extract_international_info(int_section):
    if not int_section:
        return None, None, set(), None

    hq = extract_info_from_section(int_section, r'Штаб-квартира|Headquarters')
    legal = extract_info_from_section(int_section, r'Юридический адрес|Legal Address')
    
    phones = set()
    phone_tags = int_section.find_all(string=re.compile(r'Тел\.|Phone:', re.I))
    for tag in phone_tags:
        phones.update(PHONE_PATTERN.findall(tag))
    
    website = None
    site_tag = int_section.find('a', href=True, string=re.compile(r'Веб-сайт|Website', re.I))
    if site_tag:
        website = site_tag['href']
    else:
        site_tag = int_section.find(string=re.compile(r'Веб-сайт|Website', re.I))
        if site_tag:
            website = site_tag.find_next('a')['href'] if site_tag.find_next('a') else None
    
    return hq, legal, phones, website

def parse_federation_page(url):
    if is_invalid_link(url):
        return [None] * 9

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return [None] * 9
    except Exception as e:
        print(f"Ошибка при загрузке {url}: {str(e)}")
        return [None] * 9

    soup = BeautifulSoup(response.text, 'html.parser')
    
    kz_section = soup.find(lambda tag: tag.name in ['div', 'section'] and re.search(r'Казахстанская федерация', tag.text, re.I))
    int_section = soup.find(lambda tag: tag.name in ['div', 'section'] and re.search(r'Международная федерация|International Federation', tag.text, re.I))

    address_kz, phones_kz, website_kz = extract_kazakhstan_info(kz_section)
    hq_int, legal_int, phones_int, website_int = extract_international_info(int_section)

    president_kz = extract_info_from_section(kz_section, r'Президент') if kz_section else None
    gen_sec = extract_info_from_section(kz_section, r'Генеральный секретарь') if kz_section else None
    exec_dir = extract_info_from_section(kz_section, r'Исполнительный директор') if kz_section else None
    president_int = extract_info_from_section(int_section, r'Президент') if int_section else None

    return (website_kz, website_int, president_kz, president_int, gen_sec, exec_dir, address_kz, hq_int, legal_int)

def get_federation_links():
    url = 'https://olympic.kz/ru/federations'
    response = requests.get(url)
    if response.status_code != 200:
        return [], []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    federations = [f.text.strip() for f in soup.find_all('h3')]
    links = []
    
    for item in soup.find_all('a', class_='federations-list-item'):
        link = item['href']
        if not link.startswith('http'):
            link = 'https://olympic.kz' + link
        if not is_invalid_link(link):
            links.append(link)
    
    return federations, links

if __name__ == '__main__':
    names, links = get_federation_links()
    print(f"Найдено {len(names)} федераций.")
    
    for name, link in zip(names, links):
        data = parse_federation_page(link)
        print("----------------------------------------")
        print(f"Федерация: {name}")
        print("Казахстанская федерация:")
        print(f"  Сайт: {data[0] or 'Нет информации'}")
        print(f"  Президент: {data[2] or 'Нет информации'}")
        print(f"  Генеральный секретарь: {data[4] or 'Нет информации'}")
        print(f"  Исполнительный директор: {data[5] or 'Нет информации'}")
        print(f"  Юридический адрес: {data[6] or 'Нет информации'}")
        print("Международная федерация:")
        print(f"  Штаб-квартира: {data[7] or 'Нет информации'}")
        print(f"  Юридический адрес: {data[8] or 'Нет информации'}")
        print("----------------------------------------")

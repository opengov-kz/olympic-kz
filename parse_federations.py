import requests
from bs4 import BeautifulSoup
import re

# Список соцсетей и email-доменов, которые игнорируем
SOCIAL_MEDIA_DOMAINS = ["facebook.com", "instagram.com", "youtube.com"]
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# Функция проверки, является ли ссылка ненужной (соцсети, #, email)
def is_invalid_link(url):
    return (
        any(domain in url for domain in SOCIAL_MEDIA_DOMAINS) or
        url.endswith("#") or
        EMAIL_PATTERN.match(url)  # Проверка на email
    )

# Функция для парсинга страницы федерации
def parse_federation_page(url):
    if is_invalid_link(url):
        return None, None, None, None

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Ошибка: Не удалось загрузить страницу {url}. Код статуса: {response.status_code}")
        return None, None, None, None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Поиск ссылок федераций
    federation_items = soup.find_all('div', class_='game-header__desc-item')
    kazakhstan_federation, international_federation = None, None

    if len(federation_items) >= 2:
        first_link = federation_items[0].find('a', href=True)
        second_link = federation_items[1].find('a', href=True)

        if first_link and not is_invalid_link(first_link['href']):
            kazakhstan_federation = first_link['href']
        if second_link and not is_invalid_link(second_link['href']):
            international_federation = second_link['href']

    # Поиск президента Казахстанской федерации
    president_kz = None

    # 1. Проверяем <div> с классом person__desc (как на сайте)
    president_kz_tag = soup.find('div', class_='person__desc')
    if president_kz_tag:
        name_tag = president_kz_tag.find('span', class_='person__name')
        position_tag = president_kz_tag.find('span', class_='person__position')
        if name_tag and position_tag and 'Президент' in position_tag.text:
            president_kz = name_tag.text.strip()

    # 2. Проверяем, если имя президента написано внутри <p><strong>Президент: ...</strong></p>
    if not president_kz:
        president_kz_tag = soup.find('p', string=re.compile(r'Президент:', re.I))
        if president_kz_tag:
            president_kz = president_kz_tag.text.replace("Президент:", "").strip()

    # 3. Проверяем случай <div>ФИО Президент</div> (и убираем "Вице-президент"!)
    if not president_kz:
        all_divs = soup.find_all('div')
        for div in all_divs:
            text = div.get_text(strip=True)
            if 'Президент' in text and 'Вице-президент' not in text and 'первый вице-президент' not in text.lower():
                president_kz = re.sub(r'\b(Президент|Президент:)\b', '', text).strip()
                break

    # Убираем ошибки, если в тексте остаётся слишком много данных
    if president_kz and len(president_kz) > 50:
        president_kz = president_kz.split("\n")[0].strip()

    # Поиск президента международной федерации
    president_international = None
    president_tags = soup.find_all('p')

    for tag in president_tags:
        text = tag.get_text(strip=True)
        if 'Президент:' in text:
            president_international = text.split('Президент:')[-1].strip()
            break

    return kazakhstan_federation, international_federation, president_kz, president_international

# Функция для получения списка федераций и их ссылок
def get_federation_links():
    url = 'https://olympic.kz/ru/federations'
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Ошибка: Не удалось загрузить главную страницу. Код статуса: {response.status_code}")
        return [], []

    soup = BeautifulSoup(response.text, 'html.parser')

    federations = soup.find_all('h3')
    federation_names = [federation.text.strip() for federation in federations]

    links = []
    federation_items = soup.find_all('a', class_='federations-list-item')

    for item in federation_items:
        link = item['href']
        if not link.startswith('http'):
            link = 'https://olympic.kz' + link  # Добавляем базовый URL

        if is_invalid_link(link):
            continue  # Пропускаем ненужные ссылки

        links.append(link)

    return federation_names, links

# Основной код
if __name__ == '__main__':
    federation_names, federation_links = get_federation_links()
    print(f"Найдено {len(federation_names)} федераций.")

    for name, link in zip(federation_names, federation_links):
        kazakhstan_link, international_link, president_kz, president_international = parse_federation_page(link)

        print("----------------------------------------")
        print(f"Федерация: {name}")
        print("Казахстанская федерация:")
        print(f"  Сайт: {kazakhstan_link if kazakhstan_link else 'Нет ссылки'}")
        print(f"  Президент: {president_kz if president_kz else 'Нет информации'}")
        print("Международная федерация:")
        print(f"  Сайт: {international_link if international_link else 'Нет ссылки'}")
        print(f"  Президент: {president_international if president_international else 'Нет информации'}")
        print("----------------------------------------")


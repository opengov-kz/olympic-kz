import requests
from bs4 import BeautifulSoup

# Функция для получения данных о федерации
def parse_federation_page(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Ошибка: Не удалось загрузить страницу {url}. Код статуса: {response.status_code}")
        return None, None, None, None, None, None, None, None, None, None, None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    #блок с информацией о казахстанской федерации
    kazakhstan_info = soup.find('section', id='section-local_description')
    kazakhstan_president = None
    kazakhstan_vice_president = None
    kazakhstan_link = None
    kazakhstan_contacts = {}

    if kazakhstan_info:
        #президент и вице-президент
        for p in kazakhstan_info.find_all('p'):
            text = p.text.strip()
            if "Президент:" in text:
                kazakhstan_president = text.replace("Президент:", "").strip()
            elif "Вице – президент:" in text:
                kazakhstan_vice_president = text.replace("Вице – президент:", "").strip()
        
        # ссылка на сайт казахстанской федерации
        website_link = kazakhstan_info.find('a', href=True)
        if website_link:
            kazakhstan_link = website_link['href']

        # контактная информация
        for p in kazakhstan_info.find_all('p'):
            text = p.text.strip()
            if "Юридический адрес:" in text:
                kazakhstan_contacts['Юридический адрес'] = text.replace("Юридический адрес:", "").strip()
            elif "Телефон:" in text:
                kazakhstan_contacts['Телефон'] = text.replace("Телефон:", "").strip()
            elif "e-mail:" in text:
                kazakhstan_contacts['Email'] = text.replace("e-mail:", "").strip()

    #информация о международной федерации
    international_info = soup.find('section', id='section-world_description')
    international_president = None
    international_link = None
    international_contacts = {}

    if international_info:
        #президент международной федерации
        for p in international_info.find_all('p'):
            text = p.text.strip()
            if "Президент:" in text:
                international_president = text.replace("Президент:", "").strip()
        
        #ссылку международной федерации
        website_link = international_info.find('a', href=True)
        if website_link:
            international_link = website_link['href']

        #контактная информация
        for p in international_info.find_all('p'):
            text = p.text.strip()
            if "Юридический адрес:" in text:
                international_contacts['Юридический адрес'] = text.replace("Юридический адрес:", "").strip()
            elif "Тел.:" in text:
                international_contacts['Телефон'] = text.replace("Тел.:", "").strip()
            elif "Факс:" in text:
                international_contacts['Факс'] = text.replace("Факс:", "").strip()

    # олимпийские медали
    medals_info = soup.find('div', class_='medals')
    medals = {'Золото': 0, 'Серебро': 0, 'Бронза': 0}

    if medals_info:
        for medal in medals_info.find_all('div', class_='medals-item'):
            medal_type = medal.find('div', class_='medals-item__name').text.strip()
            medal_count = medal.find('div', class_='medals-item__circle').text.strip()
            medals[medal_type] = int(medal_count)

    return (
        kazakhstan_link, international_link,
        kazakhstan_president, kazakhstan_vice_president, international_president,
        kazakhstan_contacts, international_contacts,
        medals['Золото'], medals['Серебро'], medals['Бронза']
    )

# Функция для получения списка федераций и их ссылок
def get_federation_links():
    url = 'https://olympic.kz/ru/federations'
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Ошибка: Не удалось загрузить главную страницу. Код статуса: {response.status_code}")
        return [], []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    federations = soup.find_all('h3')
    
    #названия федераций
    federation_names = [federation.text.strip() for federation in federations]
    
    #ссылки на страницы федераций
    links = []
    federation_items = soup.find_all('a', class_='federations-list-item')
    for item in federation_items:
        link = item['href']
        if not link.startswith('http'):
            link = 'https://olympic.kz' + link 
        links.append(link)

    return federation_names, links

# Основной код
if __name__ == '__main__':
    # список названий федераций и их ссылок
    federation_names, federation_links = get_federation_links()
    print(f"Найдено {len(federation_names)} федераций.")

    # парсим данные для каждой федерации
    for name, link in zip(federation_names, federation_links):
        # парсим страницу федерации
        (
            kazakhstan_link, international_link,
            kazakhstan_president, kazakhstan_vice_president, international_president,
            kazakhstan_contacts, international_contacts,
            gold_medals, silver_medals, bronze_medals
        ) = parse_federation_page(link)
        
        # формируем вывод
        print("------------")
        print(f"федерация: {name}")
        print("Казахстанская федерация:")
        if kazakhstan_link:
            print(f"  Сайт: {kazakhstan_link}")
        else:
            print("  Сайт: Нет ссылки")
        if kazakhstan_president:
            print(f"  Президент: {kazakhstan_president}")
        else:
            print("  Президент: Нет информации")
        if kazakhstan_vice_president:
            print(f"  Вице-президент: {kazakhstan_vice_president}")
        else:
            print("  Вице-президент: Нет информации")
        if kazakhstan_contacts:
            for key, value in kazakhstan_contacts.items():
                print(f"  {key}: {value}")
        else:
            print("  Контактная информация: Нет данных")
        print("Международная федерация:")
        if international_link:
            print(f"  Сайт: {international_link}")
        else:
            print("  Сайт: Нет ссылки")
        if international_president:
            print(f"  Президент: {international_president}")
        else:
            print("  Президент: Нет информации")
        if international_contacts:
            for key, value in international_contacts.items():
                print(f"  {key}: {value}")
        else:
            print("  Контактная информация: Нет данных")
        print("Олимпийские медали: [")
        print(f"  Золото: {gold_medals}")
        print(f"  Серебро: {silver_medals}")
        print(f"  Бронза: {bronze_medals}")
        

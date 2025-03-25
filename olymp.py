import requests
from bs4 import BeautifulSoup
import re
import csv

base_url = "https://www.olympedia.org/countries/KAZ"
headers = {"User-Agent": "Mozilla/5.0"}

# Получаем список всех олимпийских лет
response = requests.get(base_url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

edition_links = []
for a in soup.find_all("a", href=True):
    if "/countries/KAZ/editions/" in a["href"]:
        full_link = "https://www.olympedia.org" + a["href"]
        edition_links.append(full_link)

print(f"Найдено {len(edition_links)} олимпийских соревнований")

# Файл для сохранения всех данных
csv_path = "olympics_all_years.csv"
data = [["Год", "Атлет(ы)","Вид спорта", "Дисциплина", "Место",  "Медаль"]]

def get_year_from_title(url):
    """ Получает год из заголовка страницы """
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string  
    match = re.search(r"(\d{4})", title)  
    return match.group(1) if match else "Unknown"

def parse_olympic_data(url):
    """ Парсит страницу Олимпиады и извлекает результаты Казахстана """
    year = get_year_from_title(url)
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    tables = soup.find_all("table")
    sport = None  

    for table in tables:
        rows = table.find_all("tr")

        for row in rows:
            sport_header = row.find("h2")
            if sport_header:
                sport = sport_header.text.strip()
                continue  

            cols = row.find_all("td")
            if len(cols) >= 4:  # Проверяем, что в строке достаточно данных
                discipline = cols[0].text.strip()  
                place = cols[2].text.strip() if len(cols) > 2 else "—"  
                medal = cols[3].text.strip() if len(cols) > 3 else "—"  

                if "Gold" in medal:
                    medal = "Золото"
                elif "Silver" in medal:
                    medal = "Серебро"
                elif "Bronze" in medal:
                    medal = "Бронза"
                else:
                    medal = "—"

                # Извлекаем имена спортсменов
                athletes = []
                athlete_cells = cols[1].find_all("a")  # Теперь чётко берём из 2-го столбца
                for a in athlete_cells:
                    name = a.text.strip()
                    if name and "Kazakhstan" not in name:
                        athletes.append(name)

                if athletes:
                    data.append([year, " • ".join(athletes), sport, discipline, place,  medal])

# Обходим все Олимпиады
for link in edition_links:
    print(f"Парсим данные: {link}")
    parse_olympic_data(link)

# Сохранение в общий CSV
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(data)

print(f"Все данные сохранены в {csv_path}")

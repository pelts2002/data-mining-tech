import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# --- 1. Загружаем страницу ---
url = "https://en.wikipedia.org/wiki/List_of_Formula_One_World_Drivers%27_Champions"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
response.raise_for_status()

# --- 2. Парсим HTML через BeautifulSoup ---
soup = BeautifulSoup(response.text, "html.parser")
html = str(soup)

# --- 3. Читаем таблицы через pandas ---
tables = pd.read_html(html)
print(f"Найдено таблиц: {len(tables)}")

# --- 4. Находим таблицу с сезонами ---
df = None
for i, t in enumerate(tables):
    if any("Season" in str(c) for c in t.columns) and any("Driver" in str(c) for c in t.columns):
        print(f"✅ Найдена таблица под номером {i}")
        df = t
        break

# --- 5. Преобразуем MultiIndex в плоский список ---
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [f"{a}".strip() + (" / " + f"{b}".strip() if b else "") for a, b in df.columns]

# --- 6. Находим нужные колонки ---
def find_col_like(df, keyword):
    for c in df.columns:
        if keyword.lower() in c.lower():
            return c
    return None
col_season = find_col_like(df, "Season")
col_driver = find_col_like(df, "Driver")
col_age = find_col_like(df, "Age")
col_wins = find_col_like(df, "Wins")
col_chassis = find_col_like(df, "Chassis")
col_engine = find_col_like(df, "Engine")
col_rounds = find_col_like(df, "round")

# --- 7. Конструктор ---
if col_chassis and col_engine:
    df["Constructor"] = df[col_chassis] + " / " + df[col_engine]
col_constructor = "Constructor"

# --- 8. Преобразуем числовые данные ---
df[col_age] = pd.to_numeric(df[col_age], errors="coerce")
df[col_wins] = pd.to_numeric(df[col_wins], errors="coerce")

# --- 9. Вопрос 1 ---
print("\n---- Вопрос 1: Возраст чемпионов ----")
print("Средний:", df[col_age].mean())
print("Минимальный:", df[col_age].min())
print("Максимальный:", df[col_age].max())

# --- 10. Вопрос 2 ---
print("\n---- Вопрос 2: Топ конструкторов ----")
print(df.groupby(col_constructor).size().sort_values(ascending=False).head(10))

# --- 11. Вопрос 3 ---
print("\n---- Вопрос 3: Топ гонщиков ----")
print(df.groupby(col_driver).size().sort_values(ascending=False).head(10))

# --- 12. Вопрос 4: Чемпионы с менее чем 30% побед в сезоне ---
print("\n---- Вопрос 4: Чемпионы с менее чем 30% побед в сезоне ----")
# Используем колонку 'Clinched[17] / Clinched[17]' для определения количества гонок в сезоне
col_title_clinched = 'Clinched[17] / Clinched[17]'
def extract_race_info(text):
    if pd.isna(text):
        return None
    text = str(text)
    # Ищем паттерны типа "10 of 17", "race 8 out of 16" и т.д.
    matches = re.findall(r'(\d+)\s*(?:of|out of|/)\s*(\d+)', text)
    if matches:
        return int(matches[0][1])  # возвращаем общее количество гонок
    return None
# Извлекаем информацию о гонках
df['Total_Races'] = df[col_title_clinched].apply(extract_race_info)
if df['Total_Races'].isna().any():
    # Удаляем строки, где не удалось определить количество гонок
    df_clean = df.dropna(subset=['Total_Races']).copy()
else:
    df_clean = df.copy()
# Вычисляем процент побед
df_clean['Win_Percentage'] = (df_clean[col_wins] / df_clean['Total_Races']) * 100
# Находим гонщиков с менее чем 30% побед
low_win_champions = df_clean[df_clean['Win_Percentage'] < 30]
if not low_win_champions.empty:
    print("Гонщики, ставшие чемпионами с менее чем 30% побед в сезоне:")
    for _, row in low_win_champions.iterrows():
        print(f"{row[col_driver]} ({row[col_season]}): {int(row[col_wins])}/{int(row['Total_Races'])} побед ({row['Win_Percentage']:.1f}%)")
else:
    print("Не найдено гонщиков с менее чем 30% побед")

# --- 13. Вопрос 5: Максимальный перерыв между чемпионствами ---
print("\n---- Вопрос 5: Максимальный перерыв между последовательными чемпионствами ----")
# Очищаем данные от строк с некорректными значениями Season
df_clean_season = df[pd.to_numeric(df[col_season], errors='coerce').notna()].copy()
df_clean_season[col_season] = pd.to_numeric(df_clean_season[col_season])
# Группируем по гонщикам и собираем года их чемпионств
champions_by_driver = df_clean_season.groupby(col_driver)[col_season].apply(list).reset_index()
# Оставляем только тех, у кого 2 или более титулов
multiple_champions = champions_by_driver[champions_by_driver[col_season].apply(len) >= 2]
max_break = 0
max_break_driver = ""
max_break_period = ""
for _, row in multiple_champions.iterrows():
    driver = row[col_driver]
    years = sorted(row[col_season])  # сортируем года по возрастанию
    # Вычисляем перерывы между последовательными чемпионствами
    for i in range(1, len(years)):
        break_years = years[i] - years[i-1] - 1  # перерыв в годах между титулами
        if break_years > max_break:
            max_break = break_years
            max_break_driver = driver
            max_break_period = f"{years[i-1]}-{years[i]}"
print(f"Максимальный перерыв между последовательными чемпионствами: {max_break} лет")
print(f"Гонщик: {max_break_driver}")
print(f"Период: {max_break_period}")
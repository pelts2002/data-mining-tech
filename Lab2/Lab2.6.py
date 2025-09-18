import requests

# качаем файл
mbox = requests.get('https://www.py4e.com/code3/mbox.txt').text
# делаем список строк
all_lines = mbox.split('\n')

# словарь кто сколько раз писал
d = {}

for line in all_lines:
    if line.startswith("From "):  # ищем строки где автор
        parts = line.split()
        if len(parts) > 1:
            em = parts[1]  # берем сам адрес
            if em not in d:
                d[em] = 0
            d[em] += 1  # считаем

# ищем кто написал больше всего
mxk = None
mxv = -1
for k,v in d.items():
    if v > mxv:
        mxv = v
        mxk = k

# выводим всех и самого активного
print("все авторы и сколько писем:")
for k,v in d.items():
    print(k,v)

print("больше всех писал:")
print(mxk, mxv)

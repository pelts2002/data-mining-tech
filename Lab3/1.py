import numpy as np
import matplotlib.pyplot as plt

# читаем названия стран (первый столбец как строки)
strani = np.genfromtxt("global-electricity-generation.csv", delimiter=",", dtype=str, skip_header=1, usecols=0)

# читаем данные генерации (без стран)
dannieGen = np.genfromtxt("global-electricity-generation.csv", delimiter=",", dtype=float, skip_header=1, usecols=range(1,31))

# читаем данные потребления (без стран)
dannieCons = np.genfromtxt("global-electricity-consumption.csv", delimiter=",", dtype=float, skip_header=1, usecols=range(1,31))

# последние 5 лет
posled5gen = np.nanmean(dannieGen[:,-5:], axis=1)
posled5cons = np.nanmean(dannieCons[:,-5:], axis=1)

# 3.1 суммарное потребление по всем странам за каждый год
vsego_po_godam_cons = np.nansum(dannieCons, axis=0)

# 3.2 макс производство одной страны за один год
maxGen = np.nanmax(dannieGen)

# 3.3 страны >500 млрд
bolshe500 = strani[posled5gen > 500]

# 3.4 топ 10% по потреблению
kvantil = np.quantile(posled5cons, 0.9)
top10proc = strani[posled5cons >= kvantil]

# 3.5 2021 > 10 * 1992
god1992 = dannieGen[:,0]
god2021 = dannieGen[:,-1]
tenraz = strani[god2021 > god1992*10]

# 3.6 тратили >100 и произвели меньше чем тратили
sumGen = np.nansum(dannieGen, axis=1)
sumCons = np.nansum(dannieCons, axis=1)
krutie = strani[(sumCons > 100) & (sumGen < sumCons)]

# 3.7 макс потребление в 2020
cons2020 = dannieCons[:,-2]
max2020 = strani[np.argmax(cons2020)]

# выводы
print("3.1 Суммарное потребление за каждый год:", vsego_po_godam_cons)
print("")
print("3.2 Макс производство одной страны за один год:", maxGen)
print("")
print("3.3 >500 млрд производство (среднее за 5 лет):", bolshe500)
print("")
print("3.4 Топ 10% стран по потреблению (среднее за 5 лет):", top10proc)
print("")
print("3.5 В 2021 >10 раз чем в 1992:", tenraz)
print("")
print("3.6 Потребили >100 и произвели меньше:", krutie)
print("")
print("3.7 Больше всех потратил в 2020:", max2020)

# график
plt.plot(vsego_po_godam_cons)
plt.title("Суммарное потребление по годам")
plt.xlabel("Годы (с 1992)")
plt.ylabel("Потребление (млрд кВт*ч)")
plt.show()
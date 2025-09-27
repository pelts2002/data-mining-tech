import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import solve

# читаем наш CSV файл, разделитель ;, всё как строки
dd = np.genfromtxt("data2.csv", delimiter=";", dtype=str)

# создаём пустые списки для скидок и прибыли
xik = []
yik = []

# идём по всем строкам из файла
for a, b in dd:
    a = a.replace("п»ї","")  # убираем мусор из первой ячейки (BOM)
    try:
        q = float(a)  # пытаемся превратить скидку в число
    except:
        # если не число, то там типа 01.фев, 01.мар и т.д.
        # делаем словарь месяцев
        mes = {"янв":1,"фев":2,"мар":3,"апр":4,"май":5,"июн":6,
               "июл":7,"авг":8,"сен":9,"окт":10,"ноя":11,"дек":12}
        z = a.split(".")  # делим строку по точке
        try:
            q = float(mes[z[1]])  # берём номер месяца
        except:
            q = 0  # если вообще странно, ставим 0
    xik.append(q)        # добавляем скидку в список
    yik.append(float(b)) # добавляем прибыль в список

# превращаем списки в numpy массивы
xx = np.array(xik)
yy = np.array(yik)

# выбираем точки для квадратика: первая, середина, последняя
p1 = 0
p2 = len(xx)//2
p3 = len(xx)-1

# строим систему уравнений для квадратичного полинома
A2 = np.array([[xx[p1]**2, xx[p1], 1],
               [xx[p2]**2, xx[p2], 1],
               [xx[p3]**2, xx[p3], 1]])
b2 = np.array([yy[p1], yy[p2], yy[p3]])

# решаем систему и получаем коэффициенты a, b, c
koef2 = solve(A2,b2)  
print("коэф квадр:", koef2)

# считаем значения полинома на всех точках
f2 = koef2[0]*xx**2 + koef2[1]*xx + koef2[2]

# считаем RSS (квадратичное отклонение)
rss2 = np.sum((yy - f2)**2)
print("RSS квадр=", rss2)

# теперь кубический полином, выбираем ещё одну точку
p4 = len(xx)//3*2

A3 = np.array([[xx[p1]**3, xx[p1]**2, xx[p1], 1],
               [xx[p2]**3, xx[p2]**2, xx[p2], 1],
               [xx[p3]**3, xx[p3]**2, xx[p3], 1],
               [xx[p4]**3, xx[p4]**2, xx[p4], 1]])
b3 = np.array([yy[p1], yy[p2], yy[p3], yy[p4]])

# решаем систему для кубика
koef3 = solve(A3,b3)
print("коэф куб:", koef3)

# считаем значения кубического полинома
f3 = koef3[0]*xx**3 + koef3[1]*xx**2 + koef3[2]*xx + koef3[3]

# RSS для кубика
rss3 = np.sum((yy - f3)**2)
print("RSS куб=", rss3)

# рисуем графики
plt.scatter(xx,yy,color="red",label="исходные") # точки из файла
plt.plot(xx,f2,label="квадрат")                 # квадратичная линия
plt.plot(xx,f3,label="кубик")                   # кубическая линия
plt.legend()
plt.show()

# выбираем лучший вариант (меньше RSS)
if rss2<rss3:
    print("лучше квадратичный")
    pred6 = koef2[0]*6**2 + koef2[1]*6 + koef2[2]  # считаем прибыль при скидке 6
    pred8 = koef2[0]*8**2 + koef2[1]*8 + koef2[2]  # при 8%
else:
    print("лучше кубический")
    pred6 = koef3[0]*6**3 + koef3[1]*6**2 + koef3[2]*6 + koef3[3]
    pred8 = koef3[0]*8**3 + koef3[1]*8**2 + koef3[2]*8 + koef3[3]

# выводим прогнозы
print("при 6% =", pred6)
print("при 8% =", pred8)
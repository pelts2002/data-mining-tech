n = int(input())  # сколько записей в блокноте
sp = []
for i in range(n):
    x = input().split()  # дата пицца цена
    d = x[0]
    p = x[1]
    c = int(x[2])
    sp.append([d,p,c])  # сохраняем все в список

# а) сколько раз пиццу заказали
cnt = {}
for s in sp:
    if s[1] not in cnt:
        cnt[s[1]] = 0
    cnt[s[1]] += 1

pizza_list = sorted(cnt.items(), key=lambda z: -z[1])  # сорт по убыванию
print("а)")
for k,v in pizza_list:
    print(k,v)

# б) сколько денег в каждый день
den = {}
for s in sp:
    if s[0] not in den:
        den[s[0]] = 0
    den[s[0]] += s[2]

days = sorted(den.items(), key=lambda z: z[0])  # сорт по дате
print("б)")
for k,v in days:
    print(k,v)

# в) самый дорогой заказ
mx = sp[0]
for s in sp:
    if s[2] > mx[2]:
        mx = s
print("в)")
print(mx[0], mx[1], mx[2])  # дата пицца цена

# г) средняя цена заказа
suma = 0
for s in sp:
    suma += s[2]
avg = suma / len(sp)
print("г)")
print(round(avg,2))

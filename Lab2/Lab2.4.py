a = input().split()  # читаем имена
n = int(input())  # кол-во покупок
d = {}
for x in a:
    d[x] = 0  # у всех пока 0 потрачено
for i in range(n):
    q = input().split()  # читаем кто сколько потратил
    nm = q[0]
    s = int(q[1])
    d[nm] += s  # добавляем к его сумме

sm = 0
for v in d.values():
    sm += v  # считаем общий расход
sr = sm / len(d)  # сколько в среднем должен каждый

lst1 = []  # кто должен получить деньги
lst2 = []  # кто должен отдать деньги
for k,v in d.items():
    raz = round(v - sr,2)  # разница с нормой
    if raz > 0:
        lst1.append([k,raz])  # этот чел в плюсе
    elif raz < 0:
        lst2.append([k,-raz])  # этот в минусе

ans = []  # тут будут переводы
i = 0
j = 0
while i < len(lst1) and j < len(lst2):
    mn = min(lst1[i][1], lst2[j][1])  # сколько перевести
    ans.append([lst2[j][0], lst1[i][0], mn])  # кто->кому->сколько
    lst1[i][1] -= mn
    lst2[j][1] -= mn
    if lst1[i][1] == 0:
        i += 1  # этот больше не должен
    if lst2[j][1] == 0:
        j += 1  # этот больше не должен

print(len(ans))  # сколько переводов всего
for x in ans:
    print(x[0], x[1], f"{x[2]:.2f}")  # выводим результат

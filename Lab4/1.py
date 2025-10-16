import pandas as pd
import matplotlib.pyplot as plt

# загружаем данные
df = pd.read_csv("athlete_events.csv")

# считаем сколько значений в каждом столбце
print("Сколько значений в каждом столбце:")
print(df.count())

print("\nИнфо про данные:")
print(df.info())

# ищем где пропуски и где их больше всего
nulls = df.isnull().sum()
print("\nПропуски в данных:")
print(nulls)
print("\nБольше всего пропусков тут:", nulls.idxmax())

# статистика по возрасту, росту, весу
print("\nСтатистика по Age, Height, Weight:")
print(df[["Age","Height","Weight"]].describe())

# 1) самый молодой участник 1992
igra1992 = df[df["Year"]==1992]
minvozr = igra1992["Age"].min()
molodoi = igra1992[igra1992["Age"]==minvozr]
print("\nСамый молодой в 1992 году:")
print(molodoi[["Name","Age","Sport"]])

# 2) все виды спорта
print("\nСписок всех видов спорта:")
print(df["Sport"].unique())

# 3) средний рост теннисисток в 2000
tennis2000 = df[(df["Year"]==2000) & (df["Sex"]=="F") & (df["Sport"]=="Tennis")]
print("\nСредний рост теннисисток в 2000:", tennis2000["Height"].mean())

# 4) сколько золотых медалей Китай в настольном теннисе 2008
china2008 = df[(df["Year"]==2008) & (df["Sport"]=="Table Tennis") & (df["Team"]=="China") & (df["Medal"]=="Gold")]
print("\nЗолота у Китая в настольном теннисе в 2008:", len(china2008))

# 5) изменение числа видов спорта 2004 vs 1988
sport1988 = df[(df["Year"]==1988) & (df["Season"]=="Summer")]["Sport"].nunique()
sport2004 = df[(df["Year"]==2004) & (df["Season"]=="Summer")]["Sport"].nunique()
print("\nРазница видов спорта (2004 - 1988):", sport2004 - sport1988)

# 6) гистограмма возраста мужчин-керлингистов 2014
curling2014 = df[(df["Year"]==2014) & (df["Sport"]=="Curling") & (df["Sex"]=="M")]
plt.hist(curling2014["Age"].dropna(), bins=10)
plt.title("Возраст мужчин-керлингистов 2014")
plt.xlabel("Возраст")
plt.ylabel("Количество")
plt.show()

# 7) зимняя олимпиада 2006: по странам, медали и возраст
zim06 = df[(df["Year"]==2006) & (df["Season"]=="Winter")]
gr = zim06.groupby("NOC").agg({"Medal":"count", "Age":"mean"})
gr = gr[gr["Medal"]>0]
print("\nСтраны с медалями и средним возрастом 2006:")
print(gr)

# 8) сводная таблица медалей по странам в 2006
pivot = pd.pivot_table(zim06, index="NOC", columns="Medal", values="ID", aggfunc="count", fill_value=0)
print("\nСводная таблица по медалям 2006:")
print(pivot)
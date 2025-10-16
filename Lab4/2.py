import os, glob
import pandas as pd
import numpy as np

# Ищем файл telecom_churn.csv в нескольких местах
fn = 'telecom_churn.csv'
cands = [fn, os.path.join('/mnt/data', fn), os.path.join('.', fn), os.path.join('data', fn), os.path.join('..', fn)]
found = None
for p in cands:
    if os.path.exists(p):
        found = p
        break
if not found:
    # ищем похожие csv файлы
    lst = glob.glob('*.csv') + glob.glob('data/*.csv') + glob.glob('/mnt/data/*.csv')
    for f in lst:
        if 'telecom' in os.path.basename(f).lower() or 'churn' in os.path.basename(f).lower():
            found = f
            break

if not found:
    print("Файл 'telecom_churn.csv' не найден в окружении.")
    print("Положите файл рядом со скриптом или в /mnt/data/ и назовите 'telecom_churn.csv',\nили укажите точный путь и перезапустите.")
    print("Текущая директория:", os.getcwd())
    print("Содержимое текущей директории:", os.listdir('.'))
else:
    print("Найден файл:", found)
    # Загружаем только нужные столбцы (но сначала посмотрим шапку, чтобы адаптироваться к именам)
    preview = pd.read_csv(found, nrows=5)
    print("\nПревью столбцов (первые 5 строк) ->", list(preview.columns))

    # нормализуем имена столбцов (уберём пробелы в начале/конце, приведём к нижнему регистру)
    colmap = {c: c.strip() for c in preview.columns}
    df_full = pd.read_csv(found)
    df_full.rename(columns=lambda x: x.strip(), inplace=True)

    # Список столбцов, которые нам нужны (в возможных вариантах написания)
    want_variants = {
        'State': ['state'],
        'Area code': ['area code','area_code','areacode','area'],
        'International plan': ['international plan','international_plan','international','intl plan','intl'],
        'Number vmail messages': ['number vmail messages','number_vmail_messages','vmail','number vmail'],
        'Total day minutes': ['total day minutes','total_day_minutes','day minutes','total_day_min'],
        'Total day calls': ['total day calls','total_day_calls','day calls'],
        'Total eve minutes': ['total eve minutes','total_eve_minutes','eve minutes'],
        'Total eve calls': ['total eve calls','total_eve_calls','eve calls'],
        'Total night minutes': ['total night minutes','total_night_minutes','night minutes'],
        'Total night calls': ['total night calls','total_night_calls','night calls'],
        'Customer service calls': ['customer service calls','customer_service_calls','custservcalls','customer service','customer calls'],
        'Churn': ['churn','churn?','churned','churn_flag','churn?']
    }

    # функция для поиска реального имени колонки по варианту
    def find_col(df_cols, variants):
        dfc = [c.lower() for c in df_cols]
        for v in variants:
            v_low = v.lower()
            # полный матч
            for i,c in enumerate(dfc):
                if c == v_low:
                    return df_cols[i]
            # убираем пробелы/подчёркивания
            for i,c in enumerate(dfc):
                if c.replace(' ', '').replace('_','') == v_low.replace(' ','').replace('_',''):
                    return df_cols[i]
            # contains
            for i,c in enumerate(dfc):
                if v_low in c:
                    return df_cols[i]
        return None

    cols_found = {}
    for nice, variants in want_variants.items():
        real = find_col(list(df_full.columns), variants)
        cols_found[nice] = real
    print("\nНайденные соответствия столбцов:")
    for k,v in cols_found.items():
        print(f"  {k} -> {v}")

    # Проверяем, что ключевые столбцы найдены (Churn и Customer service calls и International plan и суммарные минуты/звонки)
    required = ['Churn','Customer service calls','International plan','Total day minutes','Total eve minutes','Total night minutes','Total day calls','Total eve calls','Total night calls']
    miss = [r for r in required if cols_found.get(r) is None]
    if miss:
        print("\nВнимание: не найдены некоторые ожидаемые столбцы:", miss)
        print("Попытка продолжить с теми столбцами, которые найдены. Если данных мало — загрузите ожидаемый файл.")
    # Создаём DataFrame с нужными столбцами, если они есть
    use_cols = [v for v in cols_found.values() if v is not None]
    df = df_full[use_cols].copy()
    # Переименуем колонки на удобные имена
    rename_map = {v:k for k,v in cols_found.items() if v is not None}
    df.rename(columns=rename_map, inplace=True)

    # 1) Общая информация
    print("\n1) Общая информация о датафрейме (info и пропуски):")
    # info() печатает в STDOUT, чтобы было аккуратно — используем print с описанием
    print(df.info())
    print("\nСумма пропусков по столбцам:")
    print(df.isna().sum())

    # 2) value_counts по Churn и проценты
    print("\n2) Сколько клиентов активны и сколько потеряно (value_counts):")
    if 'Churn' in df.columns:
        vc = df['Churn'].value_counts(dropna=False)
        vc_pct = df['Churn'].value_counts(normalize=True, dropna=False) * 100
        print(vc)
        print("\nПроцентное распределение (в процентах):")
        print(vc_pct.round(2))
    else:
        print("Столбец Churn отсутствует — нельзя посчитать распределение.")

    # 3) Добавим столбец средняя продолжительность одного звонка:
    # Суммарная длительность всех звонков = total_day_minutes + total_eve_minutes + total_night_minutes
    # Суммарное кол-во звонков = total_day_calls + total_eve_calls + total_night_calls
    # Берём названия столбцов, которые у нас есть (если нет — заполняем нулями)
    for col in ['Total day minutes','Total eve minutes','Total night minutes','Total day calls','Total eve calls','Total night calls']:
        if col not in df.columns:
            df[col] = 0.0  # если нет — 0, чтобы не падать

    df['total_minutes_all'] = df['Total day minutes'] + df['Total eve minutes'] + df['Total night minutes']
    df['total_calls_all'] = df['Total day calls'] + df['Total eve calls'] + df['Total night calls']

    # избегаем деления на ноль
    df['avg_call_dur'] = df['total_minutes_all'] / df['total_calls_all']
    # если calls == 0 -> inf или NaN, заменим на 0
    df.loc[df['total_calls_all']==0, 'avg_call_dur'] = 0.0

    print("\n3) Топ-10 клиентов по средней продолжительности одного звонка (по убыванию):")
    top10 = df.sort_values('avg_call_dur', ascending=False).head(10)
    print(top10[['avg_call_dur','total_minutes_all','total_calls_all']].to_string(index=False))

    # 4) Группировка по Churn и средняя длительность одного звонка
    if 'Churn' in df.columns:
        grp = df.groupby('Churn')['avg_call_dur'].mean().reset_index().rename(columns={'avg_call_dur':'mean_avg_call_dur'})
        print("\n4) Средняя продолжительность одного звонка по группам Churn:")
        print(grp.to_string(index=False))
    else:
        print("\n4) Нельзя сгруппировать по Churn — столбец отсутствует.")

    # 5) Группировка по Churn и среднее количество звонков в службу поддержки
    if 'Churn' in df.columns and 'Customer service calls' in df.columns:
        grp2 = df.groupby('Churn')['Customer service calls'].mean().reset_index().rename(columns={'Customer service calls':'mean_custserv_calls'})
        print("\n5) Среднее количество звонков в службу поддержки по Churn:")
        print(grp2.to_string(index=False))
    else:
        print("\n5) Нужные столбцы отсутствуют для этой операции.")

    # 6) Таблица сопряженности (crosstab) между Churn и Customer service calls
    if 'Churn' in df.columns and 'Customer service calls' in df.columns:
        ct = pd.crosstab(df['Customer service calls'], df['Churn'], margins=False)
        print("\n6) Таблица сопряженности (Customer service calls x Churn):")
        print(ct.to_string())
        # вычислим процент оттока в каждой строке (по числу клиентов с данным числом звонков)
        ct_pct = ct.div(ct.sum(axis=1), axis=0).fillna(0)
        # если названия колонок содержают булевы значения, приведём их к строке 'True'/'False' для доступа
        print("\nПроцент оттока в разрезе количества звонков (в строках):")
        print((ct_pct * 100).round(2).to_string())
        # где процент оттока > 40%?
        # найдем значения customer service calls, где churn True процент > 40%
        if True in ct_pct.columns or 'True' in ct_pct.columns or 1 in ct_pct.columns:
            # определить колонки, обозначающие отток: ищем колонку, которая соответствует True/1/'True' 
            churn_cols = [c for c in ct_pct.columns if str(c).lower() in ['true','1','t','y','yes'] or isinstance(c, bool) and c is True]
            if not churn_cols:
                # возможно столбец имеет метку 'True' в строковом виде
                churn_cols = [c for c in ct_pct.columns if str(c).lower()=='true']
            if churn_cols:
                churn_col = churn_cols[0]
                high = (ct_pct[churn_col] > 0.4)
                high_idx = list(ct_pct.index[high])
                print("\nЗначения 'Customer service calls', при которых процент оттока > 40%:", high_idx)
            else:
                # если не нашли явного столбца True — попробуем выбрать любой столбец с меткой, равной True при приведении
                print("\nНе удалось явно определить столбец, обозначающий отток (True).")
        else:
            print("\nНе найден столбец, соответствующий значению True у Churn в crosstab.")
    else:
        print("\n6) Нужные столбцы (Churn и Customer service calls) отсутствуют для crosstab.")

    # 7) Связь Churn и International plan
    if 'Churn' in df.columns and 'International plan' in df.columns:
        ct2 = pd.crosstab(df['International plan'], df['Churn'], margins=False)
        print("\n7) Таблица сопряженности (International plan x Churn):")
        print(ct2.to_string())
        ct2_pct = ct2.div(ct2.sum(axis=1), axis=0).fillna(0)
        print("\nПроцент оттока внутри групп International plan (в процентах):")
        print((ct2_pct * 100).round(2).to_string())
    else:
        print("\n7) Нужные столбцы для анализа International plan отсутствуют.")

    # 8) Простая прогностическая метрика на основе Customer service calls и International plan
    # Предсказываем CHURN=True, если Customer service calls >= 3 OR International plan == 'yes' (варианты Yes/YES/true/True учитываются)
    print("\n8) Построим простой прогноз (школьный эвристический):")
    def is_yes(x):
        if pd.isna(x): return False
        s = str(x).strip().lower()
        return s in ['yes','y','true','t','1','on']

    # нормализуем International plan в булевую колонку
    if 'International plan' in df.columns:
        df['int_plan_bool'] = df['International plan'].apply(is_yes)
    else:
        df['int_plan_bool'] = False

    # гарантируем что Customer service calls числовой
    if 'Customer service calls' in df.columns:
        df['Customer service calls'] = pd.to_numeric(df['Customer service calls'], errors='coerce').fillna(0).astype(int)
    else:
        df['Customer service calls'] = 0

    # предсказание по правилу
    df['pred_churn'] = ((df['Customer service calls'] >= 3) | (df['int_plan_bool'] == True))

    # реальные метки — приведём к булевому виду (True/False)
    def to_bool_churn(x):
        if pd.isna(x): return False
        if isinstance(x, bool): return x
        s = str(x).strip().lower()
        if s in ['true','t','yes','y','1','churn','true.']:
            return True
        if s in ['false','f','no','n','0','active','false.']:
            return False
        # если это число: 1 -> True, 0 -> False
        try:
            v = float(s)
            return v != 0.0
        except:
            return False

    df['real_churn_bool'] = df['Churn'].apply(to_bool_churn) if 'Churn' in df.columns else False

    # confusion matrix components
    TP = ((df['pred_churn']==True) & (df['real_churn_bool']==True)).sum()   # true positives
    TN = ((df['pred_churn']==False) & (df['real_churn_bool']==False)).sum()
    FP = ((df['pred_churn']==True) & (df['real_churn_bool']==False)).sum()  # false positives (Type I)
    FN = ((df['pred_churn']==False) & (df['real_churn_bool']==True)).sum()  # false negatives (Type II)
    total = len(df)
    print(f"Всего записей: {total}. TP={TP}, TN={TN}, FP={FP}, FN={FN}")

    # Ошибка первого рода (false positive rate) обычно = FP / (FP + TN) — доля отрицательных, ошибочно отмеченных как положительные
    # Ошибка второго рода (false negative rate) = FN / (FN + TP) — доля положительных, ошибочно промаркированных как отрицательные
    fpr = FP / (FP + TN) if (FP + TN) > 0 else np.nan
    fnr = FN / (FN + TP) if (FN + TP) > 0 else np.nan
    print("\nПроцент ошибок:")
    print(f"  Ошибка первого рода (FP rate) = {fpr*100:.2f}% (FP / (FP+TN))")
    print(f"  Ошибка второго рода (FN rate) = {fnr*100:.2f}% (FN / (FN+TP))")

    # Также покажем простую таблицу сравнения предикта и реального
    conf = pd.crosstab(df['real_churn_bool'], df['pred_churn'])
    print("\nТаблица сопряженности (реально x предсказано):")
    print(conf.to_string())

    # Выведем примеры ошибок (несколько строк)
    print("\nНесколько примеров ложноположительных (предсказали churn, но на самом деле нет):")
    print(df[(df['pred_churn']==True)&(df['real_churn_bool']==False)].head(5)[['Customer service calls','International plan','pred_churn','real_churn_bool','avg_call_dur']].to_string(index=False))

    print("\nНесколько примеров ложноотрицательных (предсказали не churn, но на самом деле churn):")
    print(df[(df['pred_churn']==False)&(df['real_churn_bool']==True)].head(5)[['Customer service calls','International plan','pred_churn','real_churn_bool','avg_call_dur']].to_string(index=False))

    # Отобразим df небольшой выборкой пользователю
    try:
        from caas_jupyter_tools import display_dataframe_to_user
        display_dataframe_to_user("Telecom churn sample with predictions", df.head(200))
    except Exception:
        pass

    print("\nАнализ завершён.")
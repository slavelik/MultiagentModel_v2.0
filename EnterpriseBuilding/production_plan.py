import pandas as pd

# 1. Загрузка исходных данных с минутным разрешением
path = 'EnterpriseBuilding/data/Steel_industry_data.csv'
df = pd.read_csv(path, parse_dates=['datetime'], dayfirst=True).set_index('datetime')

# 2. Отбираем записи, попадающие в последние 15 минут каждого часа (минуты 45–59)
df_last15 = df[(df.index.minute >= 45) & (df.index.minute < 60)].copy()

# 3. Для планового датасета сдвигаем эти метки времени на год вперёд
df_plan = df_last15.copy()
df_plan.index = df_plan.index + pd.offsets.DateOffset(years=3)
df_plan.index = df_plan.index.floor('H')
# 4. Оставляем только нужные столбцы
df_plan = df_plan[['Load_Type', 'Motor_and_Transformer_Load_kVarh']]

df_plan.to_csv('EnterpriseBuilding/data/production_plan.csv')

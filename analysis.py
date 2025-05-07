# analysis.py
import pandas as pd
import matplotlib.pyplot as plt

# Загрузка данных
model_df = pd.read_csv('output/model_data.csv', parse_dates=['datetime'])
agent_df = pd.read_csv('output/agent_data.csv')  # datetime нет в agent_data

# Объединяем agent_df с моделью по Step для получения datetime
agent_df = agent_df.merge(
    model_df[['Step', 'datetime']],
    on='Step'
)

# Приводим datetime к datetime-типу
agent_df['datetime'] = pd.to_datetime(agent_df['datetime'])

# Создаем дополнительные периодные колонки
agent_df['year']  = agent_df['datetime'].dt.year
agent_df['month'] = agent_df['datetime'].dt.to_period('M')
agent_df['week']  = agent_df['datetime'].dt.to_period('W')
agent_df['date']  = agent_df['datetime'].dt.date

# Расчёт потребления по периодам
yearly  = agent_df.groupby(['year',  'AgentType'])['consumption'].sum().unstack(fill_value=0)
monthly = agent_df.groupby(['month', 'AgentType'])['consumption'].sum().unstack(fill_value=0)
weekly  = agent_df.groupby(['week',  'AgentType'])['consumption'].sum().unstack(fill_value=0)
daily   = agent_df.groupby(['date',  'AgentType'])['consumption'].sum().unstack(fill_value=0)

# Сохранение результатов
yearly.to_csv('output/yearly_consumption.csv')
monthly.to_csv('output/monthly_consumption.csv')
weekly.to_csv('output/weekly_consumption.csv')
daily.to_csv('output/daily_consumption.csv')

print("Saved consumption summaries:")
print(" Yearly -> output/yearly_consumption.csv")
print(" Monthly -> output/monthly_consumption.csv")
print(" Weekly -> output/weekly_consumption.csv")
print(" Daily -> output/daily_consumption.csv")

# Построение графиков
# 1. Потребление по годам
plt.figure(figsize=(8,6))
yearly.plot(kind='bar', stacked=True)
plt.title('Yearly Consumption by Agent Type (Wh)')
plt.xlabel('Year')
plt.ylabel('Consumption (Wh)')
plt.tight_layout()
plt.savefig('output/yearly_consumption.png')
plt.close()

# 2. Потребление по месяцам (первые 12)
plt.figure(figsize=(10,6))
monthly.head(12).plot(kind='bar', stacked=True)
plt.title('Monthly Consumption by Agent Type (Wh)')
plt.xlabel('Month')
plt.ylabel('Consumption (Wh)')
plt.tight_layout()
plt.savefig('output/monthly_consumption.png')
plt.close()

# 3. Число сотрудников офиса и госпитализированных во времени
plt.figure(figsize=(10,4))
plt.plot(model_df['datetime'], model_df['office_population'], label='Office Population')
plt.plot(model_df['datetime'], model_df['hospitalized'], label='Hospitalized')
plt.title('Office Population and Hospitalized Over Time')
plt.xlabel('Time')
plt.ylabel('Count')
plt.legend()
plt.tight_layout()
plt.savefig('output/population_hospitalized.png')
plt.close()

# 4. Ежедневное потребление жилых зданий
res_df = agent_df[agent_df['AgentType'] == 'ResidentialBuildingAgent']
res_daily = res_df.groupby(res_df['datetime'].dt.date)['consumption'].sum()
plt.figure(figsize=(10,4))
plt.plot(res_daily.index, res_daily.values)
plt.title('Daily Residential Consumption (Wh)')
plt.xlabel('Date')
plt.ylabel('Consumption (Wh)')
plt.tight_layout()
plt.savefig('output/daily_residential.png')
plt.close()

print("Analysis complete. Charts saved in 'output' folder.")

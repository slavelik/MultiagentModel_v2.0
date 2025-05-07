from datetime import datetime
import pandas as pd
import holidays
from meteostat import Stations, Hourly
import os

# 1. Задаём интервал: с 2024-01-01 00:00 до 2024-12-31 23:00
start = datetime(2021, 1, 1, 0)
end   = datetime(2021, 12, 31, 23)

stations = Stations()
station  = stations.nearby(51.6755, 39.2103).fetch(1)
station_id = station.index[0]

# 3. Загружаем почасовые данные с выбранной станции
data = Hourly(station_id, start, end)
df   = data.fetch()

# 4. Оставляем и переименовываем только нужные колонки
df = df[['temp']].rename(columns={'temp': 'T_out'})

# 5. Переводим индекс в колонку и сбрасываем индекс
df = df.reset_index().rename(columns={'time': 'datetime'})

# 6. Формируем признак выходного дня (суббота/воскресенье или праздник)
ru_holidays = holidays.Russia(years=2021)
df['day_off'] = df['datetime'].apply(
    lambda x: (x.weekday() >= 5) or (x.date() in ru_holidays)
)

# 7. Откбираем финальные колонки и сохраняем
df = df[['datetime', 'day_off', 'T_out']]
base = os.path.dirname(__file__)
data_path = os.path.join(base, 'data', 'environment_data.csv')
df.to_csv(data_path, index=False)

import os 
import time
import pandas as pd

if __name__ == '__main__':
    from datetime import datetime
    from model import EnergyConsumptionModel

    # Параметры симуляции
    START = datetime(2021, 1, 1, 0, 0)
    STEPS = 24 * 30  # симуляция на одну неделю

    # Инициализируем и запускаем модель
    model = EnergyConsumptionModel(
        n_enterprises=1,
        n_offices=4,
        n_hospitals=2,
        n_malls=2,
        n_modern_residential=20,
        n_residential=12,
        start_datetime=START,
        weather_path=os.path.join('data', 'environment_data.csv')
    )
    # Засекаем время выполнения симуляции
    start_time = time.time()
    for step in range(STEPS):
        model.step()
    elapsed = time.time() - start_time

    print(f"Simulation completed in {elapsed:.2f} seconds.")

     # 1) Модельные переменные
    model_df = model.datacollector.get_model_vars_dataframe()
    model_df.reset_index(inplace=True)                # превращаем индекс Step в колонку
    model_df.rename(columns={'index': 'Step'}, inplace=True)
    model_df.to_csv('output/model_data.csv', index=False)

    # 2) Агентные переменные
    agent_df = model.datacollector.get_agent_vars_dataframe()
    agent_df.reset_index(inplace=True)               # добавляет колонки Step и AgentID
    agent_df.to_csv('output/agent_data.csv', index=False)

    model_df = pd.read_csv('output/model_data.csv', parse_dates=['datetime'])
    agent_df = pd.read_csv('output/agent_data.csv')  # теперь здесь есть Step

    # Связываем по Step
    agent_df = agent_df.merge(model_df[['Step','datetime']], on='Step')

    print('Data saved to output/model_data.csv and output/agent_data.csv')

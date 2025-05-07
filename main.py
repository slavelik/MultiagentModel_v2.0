import os 
import time
import pandas as pd

if __name__ == '__main__':
    from datetime import datetime
    from model import EnergyConsumptionModel

    # Параметры симуляции
    START = datetime(2021, 1, 1, 0, 0)
    STEPS = 24 * 365  # симуляция на одну неделю

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

    # 1) Переносим model vars в DataFrame и сохраняем
    model_df = model.datacollector.get_model_vars_dataframe()
    model_df.reset_index(inplace=True)                      # превращаем индекс Step в колонку
    model_df.rename(columns={'index': 'Step'}, inplace=True)
    # Убедимся, что колонки в порядке:
    model_df = model_df[['Step', 'datetime', 'office_population', 'hospitalized', 'patients_total']]
    model_df.to_csv('output/model_data.csv', index=False)

    # 2) Переносим agent vars, добавляем datetime и сохраняем
    agent_df = model.datacollector.get_agent_vars_dataframe()
    agent_df.reset_index(inplace=True)                      # добавляет колонки Step и agent_id
    # Переименуем agent_id в AgentID
    agent_df.rename(columns={'agent_id': 'AgentID'}, inplace=True)
    # Подтягиваем datetime из model_df по Step
    agent_df = agent_df.merge(model_df[['Step', 'datetime']], on='Step')
    # Переупорядочим колонки
    agent_df = agent_df[['Step', 'datetime', 'AgentID', 'AgentType', 'consumption']]
    agent_df.to_csv('output/agent_data.csv', index=False)

    print('Data saved to output/model_data.csv and output/agent_data.csv')

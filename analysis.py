import os
import pandas as pd
import matplotlib.pyplot as plt
import calendar

# Улучшенный анализ энергопотребления и параметров модели
# Отрисовка паттернов:
# - день по часам
# - неделя по часам
# - месяц по дням
# - год по месяцам
# Более эстетичные графики и информативные подписи на осях

# plt.style.use('seaborn-darkgrid')

def ensure_dir(path):
    if path and not os.path.exists(path):
        os.makedirs(path)


def save_plot_and_csv(series, xlabel, ylabel, title, csv_path, plot_path, xticks=None, xticklabels=None):
    """
    Сохраняет серию в CSV и строит график с кастомными xticks.
    """
    ensure_dir(os.path.dirname(csv_path))
    # Сохраняем CSV
    series.to_csv(csv_path, header=[ylabel])

    # Рисуем график
    plt.figure(figsize=(10, 4))
    ax = series.plot()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if xticks is not None and xticklabels is not None:
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels, rotation=45, ha='right')
    else:
        plt.xticks(rotation=45)
    plt.tight_layout()
    ensure_dir(os.path.dirname(plot_path))
    plt.savefig(plot_path)
    plt.close()


def analyze_patterns(ts, name, output_dir, agg_func='mean'):
    ylabel = 'consumption' if 'consumption' in name else name
    
    # 1) День по часам (0–23)
    daily = ts.groupby(ts.index.hour).agg(agg_func)
    hours = list(range(24))
    hour_labels = [f"{h}:00" for h in hours]
    save_plot_and_csv(
        daily,
        xlabel='Hour of Day',
        ylabel=ylabel,
        title=f'{name} — Daily Pattern',
        csv_path=os.path.join(output_dir, f'{name}_daily.csv'),
        plot_path=os.path.join(output_dir, f'{name}_daily.png'),
        xticks=hours,
        xticklabels=hour_labels
    )

    # 2) Неделя по часам (0–167)
    week_index = ts.index.dayofweek * 24 + ts.index.hour
    weekly = ts.groupby(week_index).agg(agg_func)
    ticks = [i * 24 for i in range(7)]  # 0,24,...,144
    day_labels = [calendar.day_abbr[i] for i in range(7)]
    save_plot_and_csv(
        weekly,
        xlabel='Hour of Week',
        ylabel=ylabel,
        title=f'{name} — Weekly Pattern',
        csv_path=os.path.join(output_dir, f'{name}_weekly.csv'),
        plot_path=os.path.join(output_dir, f'{name}_weekly.png'),
        xticks=ticks,
        xticklabels=day_labels
    )

    # 3) Месяц по дням (1–31)
    monthly = ts.groupby(ts.index.day).agg(agg_func)
    days = list(range(1, monthly.index.max() + 1))
    day_labels = [str(d) for d in days]
    save_plot_and_csv(
        monthly,
        xlabel='Day of Month',
        ylabel=ylabel,
        title=f'{name} — Monthly Pattern',
        csv_path=os.path.join(output_dir, f'{name}_monthly.csv'),
        plot_path=os.path.join(output_dir, f'{name}_monthly.png'),
        xticks=days,
        xticklabels=day_labels
    )

    # 4) Год по месяцам (1–12)
    yearly = ts.groupby(ts.index.month).agg(agg_func)
    months = list(range(1, 13))
    month_labels = [calendar.month_abbr[m] for m in months]
    save_plot_and_csv(
        yearly,
        xlabel='Month',
        ylabel=ylabel,
        title=f'{name} — Yearly Pattern',
        csv_path=os.path.join(output_dir, f'{name}_yearly.csv'),
        plot_path=os.path.join(output_dir, f'{name}_yearly.png'),
        xticks=months,
        xticklabels=month_labels
    )


def main():
    agent_path = os.path.join('output', 'agent_data.csv')
    model_path = os.path.join('output', 'model_data.csv')

    df_agent = pd.read_csv(agent_path, parse_dates=['datetime']).set_index('datetime')
    df_model = pd.read_csv(model_path, parse_dates=['datetime']).set_index('datetime')

    # Общий расход энергии
    total = df_agent['consumption']
    analyze_patterns(
        total,
        name='total_consumption',
        output_dir=os.path.join('analysis', 'consumption'),
        agg_func='sum'
    )

    # По типам агентов
    for agent_type, group in df_agent.groupby('AgentType'):
        ts = group['consumption']
        safe = agent_type.lower()
        analyze_patterns(
            ts,
            name=f'{safe}_consumption',
            output_dir=os.path.join('analysis', safe + '_consumption'),
            agg_func='sum'
        )

    # Параметры модели
    for col in ['office_population', 'hospitalized', 'patients_total']:
        ts = df_model[col]
        analyze_patterns(
            ts,
            name=col,
            output_dir=os.path.join('analysis', col),
            agg_func='mean'
        )

    # Проценты изменений параметров
    pct = df_model[['office_population', 'hospitalized', 'patients_total']].pct_change().dropna()
    changes_dir = os.path.join('analysis', 'changes')
    ensure_dir(changes_dir)
    pct.to_csv(os.path.join(changes_dir, 'model_params_pct_change.csv'))

    print("Analysis completed. Результаты сохранены в папке 'analysis/'.")

if __name__ == '__main__':
    main()

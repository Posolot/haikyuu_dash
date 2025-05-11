import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
from math import pi

def load_and_clean_data():
    df = pd.read_csv("haikyuu_characters.csv")
    for col in ['Рост', 'Вес']:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.extract(r'(\d+)', expand=False),
            errors='coerce'
        )
    position_map = {
        'нападающий': 'Нападающий'
    }
    df['Позиция'] = (
        df['Позиция']
        .str.strip()
        .str.title()
        .replace(position_map)
    )
    return df.dropna(subset=['Рост', 'Вес', 'Позиция',"Сила", "Прыжки", "Выносливость", "Стратегия", "Техника", "Скорость"])

df = load_and_clean_data()

character_selector1 = widgets.Dropdown(options=df['Имя'], description='Персонаж 1')
character_selector2 = widgets.Dropdown(options=df['Имя'], description='Персонаж 2')

top_n_widget = widgets.IntSlider(value=10, min=5, max=20, description='Топ N')
bins_widget = widgets.IntSlider(value=15, min=5, max=30, step=10, description='Бинов')
metric_widget = widgets.Dropdown(options=['Рост', 'Вес'], value='Рост', description='Метрика')
pie_top_widget = widgets.IntSlider(value=6, min=1, max=10, description='Top позиций')

output1 = widgets.Output()
output2 = widgets.Output()
output3 = widgets.Output()
output4 = widgets.Output()

def update_dashboard(change=None):
    with output1:
        clear_output(wait=True)
        characteristics = ["Сила", "Прыжки", "Выносливость", "Стратегия", "Техника", "Скорость"]
        
        def get_character_data(name):
            row = df[df['Имя'] == name]
            data = []
            for feature in characteristics:
                val = row[feature].values
                if len(val) == 0 or pd.isnull(val[0]):
                    data.append(0)
                else:
                    try:
                        data.append(float(val[0]))
                    except:
                        data.append(0)
            return data
        
        def get_name_with_stats(name):
            row = df[df['Имя'] == name]
            growth = row['Рост'].values[0] if not row['Рост'].isnull().values[0] else 0
            weight = row['Вес'].values[0] if not row['Вес'].isnull().values[0] else 0
            return f"{name} ({growth}/{weight})"
        
        name1 = character_selector1.value
        name2 = character_selector2.value
        data1 = get_character_data(name1)
        data2 = get_character_data(name2)
        legend_name1 = get_name_with_stats(name1)
        legend_name2 = get_name_with_stats(name2)

        data1 += data1[:1]
        data2 += data2[:1]
        N = len(characteristics)
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
        ax.set_theta_offset(pi / 2)
        ax.set_theta_direction(-1)
        plt.xticks(angles[:-1], characteristics)
        ax.set_rlabel_position(0)
        plt.yticks([1,2,3,4,5], color="grey", size=7)
        plt.ylim(0, 5)
        ax.plot(angles, data1, linewidth=2, linestyle='solid', label=legend_name1)
        ax.fill(angles, data1, alpha=0.25)
        ax.plot(angles, data2, linewidth=2, linestyle='solid', label=legend_name2)
        ax.fill(angles, data2, alpha=0.25)
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.show()

    with output2:
        clear_output(wait=True)
        position_counts = df['Позиция'].value_counts()
        top_counts = position_counts.head(pie_top_widget.value)
        others_sum = position_counts.iloc[pie_top_widget.value:].sum()
        labels = list(top_counts.index) + ['Другие']
        values = list(top_counts.values) + [others_sum]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
        fig.update_layout(title='Топ позиций по кол-ву персонажей')
        fig.show()
    with output3:
        clear_output(wait=True)
        fig2 = go.Figure(data=[go.Histogram(x=df['Рост'], nbinsx=bins_widget.value)])
        fig2.update_layout(title='Гистограмма по кол-ву персонажей на промежуток роста', xaxis_title='Рост (см)', yaxis_title='Количество')
        fig2.show()
    with output4:
        clear_output(wait=True)
        top_df = df.nlargest(top_n_widget.value, metric_widget.value)
        fig3 = go.Figure(data=[go.Bar(x=top_df['Имя'], y=top_df[metric_widget.value])])
        fig3.update_layout(title=f'Топ-{top_n_widget.value} по {metric_widget.value}', xaxis_tickangle=-45)
        fig3.show()

for widget in [character_selector1, character_selector2, pie_top_widget, bins_widget, metric_widget, top_n_widget]:
    widget.observe(update_dashboard, names='value')

update_dashboard()
box1 = widgets.VBox([widgets.Label("Сравнение персонажей (радарный график)"), output1])
box2 = widgets.VBox([widgets.Label("Круговая диаграмма по позициям"), widgets.HBox([pie_top_widget]), output2])
box3 = widgets.VBox([widgets.Label("Гистограмма по кол-ву персонажей на промежуток роста"), widgets.HBox([bins_widget]), output3])
box4 = widgets.VBox([widgets.Label("Топ по росту/весу"), widgets.HBox([metric_widget, top_n_widget]), output4])

dashboard = widgets.VBox([widgets.HBox([character_selector1, character_selector2]), box1, box2, box3, box4])

display(dashboard)

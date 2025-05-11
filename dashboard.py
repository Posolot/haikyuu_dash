import pandas as pd
import plotly.express as px
import ipywidgets as widgets
from IPython.display import display, clear_output
import plotly.graph_objects as go

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
    return df.dropna(subset=['Рост', 'Вес', 'Позиция'])

df = load_and_clean_data()
top_n_widget = widgets.IntSlider(value=10, min=5, max=20, description='Топ N')
bins_widget = widgets.IntSlider(value=15, min=5, max=30,step=10, description='Бинов')
metric_widget = widgets.Dropdown(options=['Рост', 'Вес'], value='Рост', description='Метрика')
pie_top_widget = widgets.IntSlider(value=6, min=1, max=10, description='Top позиций')

output1 = widgets.Output()
output2 = widgets.Output()
output3 = widgets.Output()
output4 = widgets.Output()

def update_dashboard(change=None):
    with output1:
        clear_output(wait=True)
        counts = df['Позиция'].value_counts()
        top_counts = counts.head(pie_top_widget.value)
        others_sum = counts.iloc[pie_top_widget.value:].sum()
        labels = list(top_counts.index) + ['Другие']
        values = list(top_counts.values) + [others_sum]
        fig1 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
        fig1.update_layout(title='Топ позиций по кол-ву персонажей')
        fig1.show()

    with output2:
        clear_output(wait=True)
        fig2 = go.Figure(data=[go.Histogram(x=df['Рост'], nbinsx=bins_widget.value)])
        fig2.update_layout(title='Гистограмма по росту', xaxis_title='Рост (см)', yaxis_title='Количество')
        fig2.show()

    with output3:
        clear_output(wait=True)
        top_df = df.nlargest(top_n_widget.value, metric_widget.value)
        fig3 = go.Figure(data=[go.Bar(x=top_df['Имя'], y=top_df[metric_widget.value])])
        fig3.update_layout(title=f'Топ-{top_n_widget.value} по {metric_widget.value}у', xaxis_tickangle=-45)
        fig3.show()

    with output4:
        clear_output(wait=True)
        fig4 = px.scatter(df, x='Имя', y='Рост', color='Позиция')
        fig4.update_layout(title='Точечная диаграмма по росту', xaxis_tickangle=90)
        fig4.show()

for widget in [pie_top_widget, bins_widget, metric_widget, top_n_widget]:
    widget.observe(update_dashboard, names='value')

update_dashboard()
box1 = widgets.VBox([widgets.Label("Точечная диаграмма по росту"), widgets.HBox([]), output4])
box2 = widgets.VBox([widgets.Label("Круговая диаграмма по позициям"), widgets.HBox([pie_top_widget]), output1])
box3 = widgets.VBox([widgets.Label("Гистограмма по росту"), widgets.HBox([bins_widget]), output2])
box4 = widgets.VBox([widgets.Label("Топ по росту/весу"), widgets.HBox([metric_widget, top_n_widget]), output3])


dashboard = widgets.VBox([box1, box2, box3, box4])

display(dashboard)


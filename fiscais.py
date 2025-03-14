import pandas as pd
import folium
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def mapa():
    try:
        # Usando o CSV da mesma pasta (subido para o GitHub)
        csv_path = 'coordenadas2.csv'
        df = pd.read_csv(csv_path, sep=',', encoding='utf-8')

        # Criando o mapa
        mapa = folium.Map(location=[-23.5489, -46.6388], zoom_start=7)

        # Adicionando marcadores com cores baseadas no status
        for index, row in df.iterrows():
            # Verificar se os campos obrigatórios existem
            if pd.isna(row['Latitude']) or pd.isna(row['Longitude']) or pd.isna(row['Status']):
                continue  # Pula linhas com dados faltando

            popup_text = f"{row.get('Nome', 'Sem Nome')}<br>Data: {row.get('Data', 'Sem Data')}<br>Atividade: {row.get('Atividade', 'Sem Atividade')}"
           
            # Definindo a cor com base no status
            status = str(row['Status']).lower().strip()
            if status == 'finalizada':
                marker_color = 'green'
            elif status == 'em_andamento':
                marker_color = 'blue'
            elif status == 'cancelada':
                marker_color = 'red'
            else:
                marker_color = 'gray'  # Cor padrão

            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                popup=popup_text,
                icon=folium.Icon(color=marker_color)
            ).add_to(mapa)

        # Adicionando a legenda
        legend_html = '''
        <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; padding: 10px; background-color: white; border: 2px solid gray; border-radius: 5px;">
            <p><strong>Legenda</strong></p>
            <p><i class="fa fa-map-marker fa-2x" style="color:green"></i> Ação Finalizada</p>
            <p><i class="fa fa-map-marker fa-2x" style="color:blue"></i> Ação em Andamento</p>
            <p><i class="fa fa-map-marker fa-2x" style="color:red"></i> Ação Cancelada</p>
        </div>
        '''
        mapa.get_root().html.add_child(folium.Element(legend_html))

        # Renderizar o mapa como HTML
        return render_template_string(f'<html><body>{mapa._repr_html_()}</body></html>')

    except Exception as e:
        return f"Erro ao carregar o mapa: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

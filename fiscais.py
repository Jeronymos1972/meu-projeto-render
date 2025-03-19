# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/19Tml6dNa4BPyavHhVbXUL7K3FwWraHBp
"""

import pandas as pd
import folium
from flask import Flask
import os
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

@app.route('/')
def mapa():
    try:
        # Configurar as credenciais
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('GOOGLE_CREDENTIALS', scope) if not creds:creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope) # Ou use os.environ.get('GOOGLE_CREDENTIALS')
        client = gspread.authorize(creds)

        # Abrir a planilha
        sheet = client.open("Acompanhamento_Fiscais").sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce').dt.strftime('%d-%m-%Y')

        # Criando o mapa
        mapa = folium.Map(location=[-23.5489, -46.6388], zoom_start=7)

        # Adicionando marcadores com cores baseadas no status
        for index, row in df.iterrows():
            if pd.isna(row['Latitude']) or pd.isna(row['Longitude']) or pd.isna(row['Status']):
                continue

            popup_text = f"<div style='font-size: 18px;'>{row.get('Nome', 'Sem Nome')}<br>Data: {row.get('Data', 'N/A')}<br>Atividade: {row.get('Atividade', 'Sem Atividade')}<br>Localização: Lat: {row.get('Latitude', 'N/A')}, Lon: {row.get('Longitude', 'N/A')}</div>"

            status = str(row['Status']).lower().strip()
            if status == 'finalizada':
                marker_color = 'green'
            elif status == 'em_andamento':
                marker_color = 'blue'
            elif status == 'cancelada':
                marker_color = 'red'
            elif status == 'programada':
                marker_color = 'orange'
            else:
                marker_color = 'gray'

            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=marker_color)
            ).add_to(mapa)

        # Adicionando o título no topo
        title_html = '''
        <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); z-index: 1000; padding: 10px; background-color: #f0f0f0; border: 2px solid gray; border-radius: 5px;">
            <h1 style="font-size: 24px; color: #333; margin: 0; text-align: center;">Acompanhamento de Fiscais</h1>
        </div>
        '''

        # Criando a legenda em forma de tabela
        table_rows = ''
        for index, row in df.iterrows():
            status = str(row['Status']).lower().strip()
            color = 'green' if status == 'finalizada' else 'blue' if status == 'em_andamento' else 'red' if status == 'cancelada' else 'orange' if status == 'programada' else 'gray'
            table_rows += f'''
            <tr>
                <td><i class="fa fa-map-marker" style="color:{color}"></i> {row.get('Nome', 'N/A')}</td>
                <td>{str(row.get('Status', 'N/A')).capitalize() if pd.notna(row.get('Status')) else 'N/A'}</td>
                <td>{row.get('Contratada', 'N/A')}</td>
                <td>{row.get('Data', 'N/A')}</td>
            </tr>
            '''

        legend_html = '''
        <div style="position: fixed; top: 60px; right: 10px; z-index: 1000; padding: 10px; background-color: white; border: 2px solid gray; border-radius: 5px; max-width: 400px; max-height: 300px; overflow-y: auto;">
            <p><strong>Status do Serviço</strong></p>
            <table style="border-collapse: collapse; width: 100%;">
                <thead>
                    <tr style="background-color: #f0f0f0;">
                        <th style="border: 1px solid #ddd; padding: 8px;">Funcionário</th>
                        <th style="border: 1px solid #ddd; padding: 8px;">Status</th>
                        <th style="border: 1px solid #ddd; padding: 8px;">Contratada</th>
                        <th style="border: 1px solid #ddd; padding: 8px;">Data</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        '''.format(table_rows=table_rows)

        # Adicionando a escala dinâmica
        scale_html = '''
        <div id="scale" style="position: fixed; bottom: 10px; right: 10px; z-index: 1000; padding: 5px; background-color: white; border: 2px solid gray; border-radius: 5px;">
            <p><strong>Escala</strong></p>
            <p id="scale-value">Carregando...</p>
        </div>
        <script>
            function updateScale() {
                var map = document.querySelector('.folium-map');
                if (map && map._leaflet_map) {
                    var zoom = map._leaflet_map.getZoom();
                    var scale = Math.pow(2, 18 - zoom) * 100;
                    document.getElementById('scale-value').innerText = '1 cm ≈ ' + (scale > 1000 ? (scale / 1000).toFixed(1) + ' km' : scale.toFixed(1) + ' m');
                }
            }
            window.addEventListener('load', function() {
                updateScale(); // Inicializa a escala ao carregar
                var map = document.querySelector('.folium-map');
                if (map && map._leaflet_map) {
                    map.addEventListener('zoomend', updateScale);
                }
            });
        </script>
        '''

        # Adicionando título, legenda e escala ao mapa
        mapa.get_root().html.add_child(folium.Element(title_html))
        mapa.get_root().html.add_child(folium.Element(legend_html))
        mapa.get_root().html.add_child(folium.Element(scale_html))

        # Retornando o HTML do mapa
        return mapa._repr_html_()

    except Exception as e:
        return f"Erro ao carregar o mapa: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

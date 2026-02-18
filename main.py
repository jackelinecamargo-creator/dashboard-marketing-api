
# ============================================================================
# API FLASK - GERADOR DE DASHBOARD DE MARKETING
# ============================================================================
# Versão: 1.0 - Otimizado para Replit
# Criado por: Otimiza.AI
# ============================================================================

from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import io
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
    <head><title>API Dashboard Marketing</title></head>
    <body style="font-family: Arial; padding: 50px; text-align: center;">
        <h1>🚀 API Dashboard Marketing - iFood</h1>
        <p style="color: green; font-size: 24px;">✅ Status: Online</p>
        <hr>
        <h3>Endpoint Principal:</h3>
        <p><code>POST /gerar-dashboard</code></p>
        <h3>Payload esperado:</h3>
        <pre style="background: #f4f4f4; padding: 20px; text-align: left; display: inline-block;">
{
  "squad": "ADS",
  "ano": 2025
}
        </pre>
        <p style="margin-top: 30px; color: gray;">API configurada e funcionando! 🎉</p>
    </body>
    </html>
    '''

@app.route('/gerar-dashboard', methods=['POST'])
def gerar_dashboard():
    try:
        # Receber dados
        data = request.json
        squad = data.get('squad')
        ano = int(data.get('ano'))
        
        # Validar inputs
        if not squad or not ano:
            return jsonify({
                'success': False,
                'error': 'Parâmetros obrigatórios: squad, ano'
            }), 400
        
        # Carregar CSV do servidor (arquivo estático no Replit)
        csv_path = 'bh_jan25_dez25.csv'
        
        if not os.path.exists(csv_path):
            return jsonify({
                'success': False,
                'error': f'CSV não encontrado: {csv_path}. Faça upload do arquivo.'
            }), 404
        
        # Ler CSV
        with open(csv_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()
        
        # Processar dashboard
        resultado = processar_dashboard(csv_content, squad, ano)
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'tipo': type(e).__name__
        }), 500

def processar_dashboard(csv_content, squad, ano):
    """Processa CSV e gera dashboard"""
    
    # Mapeamento Squad → Request Types
    SQUAD_MAPPING = {
        'ADS': ['ADS', 'ADS - Projetos especiais'],
        'Growth Core': ['Brand House', 'Canais WhastApp', 'Clube iFood', 
                        'Conexão', 'Food Delivery', 'Food Delivery - App', 
                        'Institucional'],
        'Multicategorias': ['Groceries'],
        'Entregadores': ['Comms para entregadores'],
        'Fintech': ['iFood Benefícios', 'iFood Pago'],
        'B2B Marketplace': ['B2B - CRM - Marketplace', 'B2B - CRM - Restaurantes', 
                            'B2B - Fast Jobs', 'B2B - MKT e Comms', 
                            'B2B - MKT Multicategorias']
    }
    
    # Validar squad
    if squad not in SQUAD_MAPPING:
        squads_validas = ', '.join(SQUAD_MAPPING.keys())
        raise ValueError(f"Squad '{squad}' não reconhecida. Válidas: {squads_validas}")
    
    # Carregar CSV
    csv_data = pd.read_csv(io.StringIO(csv_content))
    
    # Converter dias para numérico
    csv_data['Dias Primeira entrega'] = pd.to_numeric(
        csv_data['Dias Primeira entrega'], 
        errors='coerce'
    )
    
    # Filtrar dados
    request_types = SQUAD_MAPPING[squad]
    filtered_df = csv_data[
        (csv_data['Request Type'].isin(request_types)) & 
        (csv_data['Ano'] == ano)
    ].copy()
    
    if len(filtered_df) == 0:
        raise ValueError(f"Nenhum dado encontrado para squad '{squad}' em {ano}")
    
    # Gerar dashboard
    dashboard_rows = gerar_tabelas(filtered_df, request_types)
    
    # Estatísticas
    total_briefings = filtered_df['Briefing'].nunique()
    total_entregas = int(filtered_df['Total'].sum())
    
    return {
        'success': True,
        'squad': squad,
        'ano': ano,
        'linhas_processadas': len(filtered_df),
        'request_types': request_types,
        'total_briefings': total_briefings,
        'total_entregas': total_entregas,
        'dashboard': dashboard_rows
    }

def gerar_tabelas(filtered_df, request_types):
    """Gera as 10 tabelas do dashboard"""
    
    meses = ['JAN./25', 'FEV./25', 'MAR./25', 'ABR./25', 'MAI./25', 'JUN./25',
             'JUL./25', 'AGO./25', 'SET./25', 'OUT./25', 'NOV./25', 'DEZ./25']
    
    output_rows = []
    
    # TABELA 1: GERAL
    output_rows.append(['Geral'] + meses)
    
    briefings_row = ['Briefings']
    for mes in meses:
        mes_data = filtered_df[filtered_df['Mês'] == mes]
        count = mes_data['Briefing'].nunique()
        briefings_row.append(count)
    output_rows.append(briefings_row)
    
    entregas_row = ['Entregáveis']
    for mes in meses:
        mes_data = filtered_df[filtered_df['Mês'] == mes]
        total = int(mes_data['Total'].sum())
        entregas_row.append(total)
    output_rows.append(entregas_row)
    
    output_rows.append([''] * 13)
    
    # TABELA 2: ENTREGÁVEIS/REQUEST TYPE
    output_rows.append(['Entregáveis/Request Type'] + meses)
    
    for rt in request_types:
        row = [rt]
        for mes in meses:
            mes_data = filtered_df[
                (filtered_df['Request Type'] == rt) & 
                (filtered_df['Mês'] == mes)
            ]
            total = int(mes_data['Total'].sum())
            row.append(total)
        output_rows.append(row)
    
    total_row = ['Total']
    for mes in meses:
        mes_data = filtered_df[filtered_df['Mês'] == mes]
        total = int(mes_data['Total'].sum())
        total_row.append(total)
    output_rows.append(total_row)
    
    output_rows.append([''] * 13)
    
    # TABELA 3: ENTREGÁVEIS/CATEGORIA
    output_rows.append(['Entregáveis/Categoria'] + meses)
    
    categorias_dict = {}
    
    for mes in meses:
        mes_data = filtered_df[filtered_df['Mês'] == mes]
        
        for _, row_data in mes_data.iterrows():
            area = row_data['Área'] if pd.notna(row_data['Área']) else None
            cat = row_data['Categoria'] if pd.notna(row_data['Categoria']) else None
            
            if area and cat:
                label = f"{area} - {cat}"
            elif area and not cat:
                label = f"{area} - Sem categoria"
            else:
                label = "Sem informação"
            
            if label not in categorias_dict:
                categorias_dict[label] = {m: 0 for m in meses}
            
            categorias_dict[label][mes] += row_data['Total']
    
    categorias_sorted = sorted(
        categorias_dict.items(), 
        key=lambda x: sum(x[1].values()), 
        reverse=True
    )
    
    for label, valores in categorias_sorted:
        row = [label]
        for mes in meses:
            row.append(int(valores[mes]))
        output_rows.append(row)
    
    total_row = ['Total']
    for mes in meses:
        mes_data = filtered_df[filtered_df['Mês'] == mes]
        total = int(mes_data['Total'].sum())
        total_row.append(total)
    output_rows.append(total_row)
    
    output_rows.append([''] * 13)
    
    # TABELA 4: TOP 3 CAMPANHAS TÁTICAS
    output_rows.append(['Top 3 Campanhas Táticas'] + meses)
    
    for rank in range(1, 4):
        row = [f'{rank}ª campanha']
        
        for mes in meses:
            mes_data = filtered_df[
                (filtered_df['Mês'] == mes) & 
                (filtered_df['Peças Tático'] > 0)
            ]
            
            if len(mes_data) > 0:
                campanhas = mes_data.groupby('Campanha')['Peças Tático'].sum()
                campanhas = campanhas.sort_values(ascending=False)
                campanhas = campanhas[campanhas.index.notna()]
                
                if len(campanhas) >= rank:
                    campanha_nome = campanhas.index[rank-1]
                    pecas = int(campanhas.iloc[rank-1])
                    row.append(f"{campanha_nome} ({pecas} peças)")
                else:
                    row.append('')
            else:
                row.append('')
        
        output_rows.append(row)
    
    output_rows.append([''] * 13)
    
    # TABELA 5: TOP 3 CAMPANHAS ESTRATÉGICAS
    output_rows.append(['Top 3 Campanhas Estratégicas'] + meses)
    
    for rank in range(1, 4):
        row = [f'{rank}ª campanha']
        
        for mes in meses:
            mes_data = filtered_df[
                (filtered_df['Mês'] == mes) & 
                (filtered_df['Peças Estratégico'] > 0)
            ]
            
            if len(mes_data) > 0:
                campanhas = mes_data.groupby('Campanha')['Peças Estratégico'].sum()
                campanhas = campanhas.sort_values(ascending=False)
                campanhas = campanhas[campanhas.index.notna()]
                
                if len(campanhas) >= rank:
                    campanha_nome = campanhas.index[rank-1]
                    pecas = int(campanhas.iloc[rank-1])
                    row.append(f"{campanha_nome} ({pecas} peças)")
                else:
                    row.append('')
            else:
                row.append('')
        
        output_rows.append(row)
    
    output_rows.append([''] * 13)
    
    # TABELA 6: TIPOS DE PEÇA
    output_rows.append(['Tipos de Peça'] + meses)
    
    tipos_pecas = {
        'KV': ['KV'],
        'PERFORMANCE': ['Banner estático', 'Banner animado', 'Títulos', 'Copy', 
                       'Descrições', 'Vídeo', 'Dark post'],
        'APP': ['Bisnaga', 'Capa Principal', 'Capa Interna', 'Waiting', 'Inapp',
                'Componente Mercado', 'TP Premium', 'Dora', 'Announcements', 
                'Brandpage', 'Cover', 'Logo', 'Brand block', 'Wallet', 'Floater',
                'Medium Banner', 'Banner Item'],
        'CRM': ['E-mail marketing', 'Notificação App', 'Push', 'Push Tabloide',
                'Whatsapp', 'SMS'],
        'OFF/Materiais': ['Guia', 'Bag', 'Sacolas', 'Folder', 'Adesivos', 
                          'Embalagem', 'Peça impressa', 'Id visual para eventos',
                          'Social post', 'Post animado', 'Post estático', 'PPT',
                          'Material rico'],
        'Peças DX': ['WPP - texto', 'WPP - imagem', 'WPP - vídeo', 
                     'inApp - botão braze', 'inApp - 2 slides ou mais', 'inApp - Outros',
                     'Push - texto', 'Push - imagem', 'Push - Outros', 
                     'CN - imagem', 'CN - GIF', 'CN - Outros', 'Weduka',
                     'Portal do entregador', 'Youtube - thumb', 'Youtube - descrição',
                     'Youtube - vídeo', 'Melhor canal', 'HTML'],
        'Peças B2B': ['Banner Portal do Parceiro', 'Notificações Portal do Parceiro:',
                      'Pop-up Portal do Parceiro (PP)', 'GIF'],
        'Outros': ['Outros']
    }
    
    for tipo, colunas in tipos_pecas.items():
        row = [tipo]
        
        for mes in meses:
            mes_data = filtered_df[filtered_df['Mês'] == mes]
            total = 0
            
            for col in colunas:
                if col in mes_data.columns:
                    total += mes_data[col].fillna(0).sum()
            
            if tipo == 'Peças DX':
                dx_data = mes_data[mes_data['Request Type'] == 'Comms para entregadores']
                if len(dx_data) > 0:
                    if 'Announcements' in dx_data.columns:
                        total += dx_data['Announcements'].fillna(0).sum()
                    if 'Push' in dx_data.columns:
                        total += dx_data['Push'].fillna(0).sum()
            
            row.append(int(total))
        
        output_rows.append(row)
    
    total_row = ['Total']
    for mes in meses:
        mes_data = filtered_df[filtered_df['Mês'] == mes]
        total = int(mes_data['Total'].sum())
        total_row.append(total)
    output_rows.append(total_row)
    
    output_rows.append([''] * 13)
    
    # TABELA 7: ESTRATÉGICAS VS TÁTICAS
    output_rows.append(['Estratégicas vs Táticas'] + meses)
    
    taticas_row = ['Entregáveis Táticos']
    for mes in meses:
        mes_data = filtered_df[filtered_df['Mês'] == mes]
        total = int(mes_data['Peças Tático'].fillna(0).sum())
        taticas_row.append(total)
    output_rows.append(taticas_row)
    
    estrategicas_row = ['Entregáveis Estratégicos']
    for mes in meses:
        mes_data = filtered_df[filtered_df['Mês'] == mes]
        total = int(mes_data['Peças Estratégico'].fillna(0).sum())
        estrategicas_row.append(total)
    output_rows.append(estrategicas_row)
    
    media_taticas = ['Prazo médio (horas) - Táticos']
    for mes in meses:
        mes_data = filtered_df[
            (filtered_df['Mês'] == mes) & 
            (filtered_df['Brief Tático'] == 1)
        ]
        if len(mes_data) > 0:
            media = mes_data['Dias Primeira entrega'].mean()
            media_taticas.append(round(media, 1) if pd.notna(media) else 0)
        else:
            media_taticas.append(0)
    output_rows.append(media_taticas)
    
    media_estrategicas = ['Prazo médio (horas) - Estratégicos']
    for mes in meses:
        mes_data = filtered_df[
            (filtered_df['Mês'] == mes) & 
            (filtered_df['Brief Estratégico'] == 1)
        ]
        if len(mes_data) > 0:
            media = mes_data['Dias Primeira entrega'].mean()
            media_estrategicas.append(round(media, 1) if pd.notna(media) else 0)
        else:
            media_estrategicas.append(0)
    output_rows.append(media_estrategicas)
    
    total_row = ['Total']
    for mes in meses:
        mes_data = filtered_df[filtered_df['Mês'] == mes]
        total = int(mes_data['Total'].sum())
        total_row.append(total)
    output_rows.append(total_row)
    
    output_rows.append([''] * 13)
    
    # TABELA 8: COMPLEXIDADE
    output_rows.append(['Complexidade'] + meses)
    
    for complexidade in ['Baixa', 'Média', 'Alta']:
        row = [f'Peças {complexidade}']
        col_name = f'Peças {complexidade}'
        
        for mes in meses:
            mes_data = filtered_df[filtered_df['Mês'] == mes]
            total = int(mes_data[col_name].fillna(0).sum())
            row.append(total)
        
        output_rows.append(row)
    
    for complexidade in ['Baixa', 'Média', 'Alta']:
        row = [f'Prazo médio (horas) - {complexidade}']
        
        for mes in meses:
            mes_data = filtered_df[
                (filtered_df['Mês'] == mes) & 
                (filtered_df['Complexidade'] == complexidade)
            ]
            if len(mes_data) > 0:
                media = mes_data['Dias Primeira entrega'].mean()
                row.append(round(media, 1) if pd.notna(media) else 0)
            else:
                row.append(0)
        
        output_rows.append(row)
    
    total_row = ['Total']
    for mes in meses:
        mes_data = filtered_df[filtered_df['Mês'] == mes]
        baixa = mes_data['Peças Baixa'].fillna(0).sum()
        media = mes_data['Peças Média'].fillna(0).sum()
        alta = mes_data['Peças Alta'].fillna(0).sum()
        total_row.append(int(baixa + media + alta))
    output_rows.append(total_row)
    
    output_rows.append([''] * 13)
    
    # TABELA 9: AJUSTES
    output_rows.append(['Ajustes'] + meses)
    
    internos_row = ['Ajustes internos']
    for mes in meses:
        mes_data = filtered_df[filtered_df['Mês'] == mes]
        total = int(mes_data['Ajustes internos'].fillna(0).sum())
        internos_row.append(total)
    output_rows.append(internos_row)
    
    parceiros_row = ['Ajustes parceiros']
    for mes in meses:
        mes_data = filtered_df[filtered_df['Mês'] == mes]
        total = int(mes_data['Ajustes parceiros'].fillna(0).sum())
        parceiros_row.append(total)
    output_rows.append(parceiros_row)
    
    total_row = ['Total']
    for mes in meses:
        mes_data = filtered_df[filtered_df['Mês'] == mes]
        internos = mes_data['Ajustes internos'].fillna(0).sum()
        parceiros = mes_data['Ajustes parceiros'].fillna(0).sum()
        total_row.append(int(internos + parceiros))
    output_rows.append(total_row)
    
    output_rows.append([''] * 13)
    
    # TABELA 10: ADVOLVE
    output_rows.append(['Advolve'] + meses)
    
    advolve_row = ['Briefings com IA']
    for mes in meses:
        mes_data = filtered_df[filtered_df['Mês'] == mes]
        total = int(mes_data['Advolve'].fillna(0).sum())
        advolve_row.append(total)
    output_rows.append(advolve_row)
    
    media_row = ['Prazo médio (horas)']
    for mes in meses:
        mes_data = filtered_df[
            (filtered_df['Mês'] == mes) & 
            (filtered_df['Advolve'] > 0)
        ]
        if len(mes_data) > 0:
            media = mes_data['Dias Primeira entrega'].mean()
            media_row.append(round(media, 1) if pd.notna(media) else 0)
        else:
            media_row.append(0)
    output_rows.append(media_row)
    
    return output_rows

if __name__ == '__main__':
    # Configuração para Replit
    app.run(host='0.0.0.0', port=5000, debug=True)

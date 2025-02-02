import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Configuração de estilo
COLORS = {
    'primary': '#2c3e50',
    'secondary': '#3498db',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'background': '#ecf0f1'
}

# Carregar e preparar dados
df = pd.read_excel("./dados/Caixa.xlsx", sheet_name="CJan", header=1)
# Limpar espaços em branco dos nomes das colunas
df.columns = df.columns.str.strip()
df["Data"] = pd.to_datetime(df["Data"])
df["Semana"] = df["Data"].dt.isocalendar().week
df["Mês"] = df["Data"].dt.month
df["Ano"] = df["Data"].dt.year

# Após carregar o DataFrame, adicione este código para debug:
print("Colunas disponíveis no DataFrame:", df.columns.tolist())

# Substituir NaN por 0 nas colunas numéricas
colunas_numericas = ['Pgto Dinheiro', 'Pgto Pix', 'A Cobrar', 'Saida']
df[colunas_numericas] = df[colunas_numericas].fillna(0)

def calcular_metricas(df, periodo=None, data=None):
    if data is not None:
        df = df[df["Data"].dt.date == data]
    elif periodo == 'semana':
        semana_atual = df["Semana"].max()
        df = df[df["Semana"] == semana_atual]
    
    metricas = {
        'servicos': len(df[df[['Pgto Dinheiro', 'Pgto Pix', 'A Cobrar']].sum(axis=1) > 0]),
        'pix': df['Pgto Pix'].sum(),
        'dinheiro': df['Pgto Dinheiro'].sum(),
        'a_cobrar': df['A Cobrar'].sum(),
        'saidas': df['Saida'].sum(),
    }
    
    metricas['total_recebido'] = metricas['pix'] + metricas['dinheiro']
    metricas['caixa'] = 1000 + metricas['dinheiro'] - metricas['saidas']  # Saldo inicial + entradas - saídas
    metricas['resultado'] = metricas['total_recebido'] - metricas['saidas']
    
    # Calcular percentuais
    total_movimentacao = metricas['total_recebido'] + metricas['a_cobrar']
    if total_movimentacao > 0:
        metricas['perc_pix'] = (metricas['pix'] / total_movimentacao) * 100
        metricas['perc_dinheiro'] = (metricas['dinheiro'] / total_movimentacao) * 100
        metricas['perc_a_cobrar'] = (metricas['a_cobrar'] / total_movimentacao) * 100
    else:
        metricas['perc_pix'] = metricas['perc_dinheiro'] = metricas['perc_a_cobrar'] = 0
    
    return metricas

def criar_dashboard():
    fig = make_subplots(
        rows=5, cols=2,
        specs=[
            [{"type": "indicator", "colspan": 2}, None],
            [{"type": "indicator", "colspan": 2}, None],
            [{"type": "domain"}, {"type": "xy"}],
            [{"type": "table"}, {"type": "xy"}],
            [{"type": "table", "colspan": 2}, None]
        ],
        vertical_spacing=0.08,
        subplot_titles=(
            "<b>Resultado do Período</b>",
            "<b>Situação do Caixa</b>",
            "<b>Distribuição dos Recebimentos</b>",
            "<b>Volume de Serviços por Semana</b>",
            "<b>Ranking dos Principais Clientes</b>",
            "<b>Histórico de Saídas</b>",
            "<b>Detalhamento das Operações</b>"
        )
    )

    metricas = calcular_metricas(df)
    
    # Indicador de Resultado
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=metricas['resultado'],
        title={"text": "Resultado do Período"},
        delta={'reference': 0, 'relative': True},
        number={'prefix': "R$", 'valueformat': ',.2f'},
        domain={'row': 0, 'column': 0}
    ), row=1, col=1)

    # Indicador de Caixa
    fig.add_trace(go.Indicator(
        mode="number",
        value=metricas['caixa'],
        title={"text": "Saldo em Caixa"},
        number={'prefix': "R$", 'valueformat': ',.2f'},
        domain={'row': 1, 'column': 0}
    ), row=2, col=1)

    # Gráfico de Pizza com valores e percentuais
    labels = ['PIX', 'Dinheiro', 'A Cobrar']
    values = [metricas['pix'], metricas['dinheiro'], metricas['a_cobrar']]
    percentuais = [metricas['perc_pix'], metricas['perc_dinheiro'], metricas['perc_a_cobrar']]
    
    fig.add_trace(go.Pie(
        labels=[f"{l}<br>{v:.1f}%" for l, v in zip(labels, percentuais)],
        values=values,
        hole=.3,
        marker_colors=[COLORS['secondary'], COLORS['success'], COLORS['warning']],
        textinfo='value+percent',
        hovertemplate="<b>%{label}</b><br>" +
                     "Valor: R$%{value:.2f}<br>" +
                     "<extra></extra>"
    ), row=3, col=1)

    # Gráfico de barras semanal com totais
    df_semanal = df.groupby('Semana').agg({
        'Pgto Pix': 'sum',
        'Pgto Dinheiro': 'sum',
        'A Cobrar': 'sum'
    }).reset_index()
    
    df_semanal['Total'] = df_semanal['Pgto Pix'] + df_semanal['Pgto Dinheiro']
    
    fig.add_trace(go.Bar(
        x=df_semanal['Semana'],
        y=df_semanal['Total'],
        marker_color=COLORS['secondary'],
        name="Total por Semana",
        text=df_semanal['Total'].apply(lambda x: f'R${x:,.2f}'),
        textposition='auto',
    ), row=3, col=2)

    # Tabela de top clientes com mais detalhes
    top_clientes = df.groupby('Cliente').agg({
        'Pgto Pix': 'sum',
        'Pgto Dinheiro': 'sum',
        'A Cobrar': 'sum'
    }).reset_index()
    
    top_clientes['Total'] = top_clientes['Pgto Pix'] + top_clientes['Pgto Dinheiro']
    top_clientes = top_clientes.nlargest(5, 'Total')
    
    fig.add_trace(go.Table(
        header=dict(
            values=['<b>Cliente</b>', '<b>PIX</b>', '<b>Dinheiro</b>', '<b>A Cobrar</b>', '<b>Total</b>'],
            fill_color=COLORS['primary'],
            align='center',
            font=dict(color='white')
        ),
        cells=dict(
            values=[
                top_clientes['Cliente'],
                top_clientes['Pgto Pix'].map('R${:,.2f}'.format),
                top_clientes['Pgto Dinheiro'].map('R${:,.2f}'.format),
                top_clientes['A Cobrar'].map('R${:,.2f}'.format),
                top_clientes['Total'].map('R${:,.2f}'.format)
            ],
            fill_color=[[COLORS['background'], 'white'] * 5],
            align='center'
        )
    ), row=4, col=1)

    # Gráfico de saídas acumulado
    df_saidas = df.groupby('Data').agg({
        'Saida': 'sum'
    }).reset_index()
    df_saidas['Saida_Acumulada'] = df_saidas['Saida'].cumsum()
    
    fig.add_trace(go.Scatter(
        x=df_saidas['Data'],
        y=df_saidas['Saida_Acumulada'],
        mode='lines+markers',
        name="Saídas Acumuladas",
        line=dict(color=COLORS['danger']),
        fill='tozeroy'
    ), row=4, col=2)

    # Tabela detalhada com formatação melhorada
    df_detalhado = df[df[['Pgto Dinheiro', 'Pgto Pix', 'A Cobrar', 'Saida']].sum(axis=1) > 0].copy()
    df_detalhado['Total'] = df_detalhado['Pgto Pix'] + df_detalhado['Pgto Dinheiro']
    
    fig.add_trace(go.Table(
        header=dict(
            values=['<b>Data</b>', '<b>Cliente</b>', '<b>PIX</b>', 
                   '<b>Dinheiro</b>', '<b>A Cobrar</b>', '<b>Total</b>'],
            fill_color=COLORS['primary'],
            align='center',
            font=dict(color='white')
        ),
        cells=dict(
            values=[
                df_detalhado['Data'].dt.strftime('%d/%m/%Y'),
                df_detalhado['Cliente'],
                df_detalhado['Pgto Pix'].map('R${:,.2f}'.format),
                df_detalhado['Pgto Dinheiro'].map('R${:,.2f}'.format),
                df_detalhado['A Cobrar'].map('R${:,.2f}'.format),
                df_detalhado['Total'].map('R${:,.2f}'.format)
            ],
            fill_color=[[COLORS['background'], 'white'] * len(df_detalhado)],
            align='center'
        )
    ), row=5, col=1)

    # Atualizar layout
    fig.update_layout(
        template="plotly_white",
        height=1500,
        showlegend=True,
        title=dict(
            text="<b>Dashboard Financeiro</b><br><sup>Análise completa do fluxo de caixa</sup>",
            font=dict(size=24, color=COLORS['primary']),
            x=0.5,
            y=0.99
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig

# Gerar e salvar o dashboard
fig = criar_dashboard()
fig.write_html(
    "dashboard_final.html",
    include_plotlyjs=True,
    config={
        'responsive': True,
        'displayModeBar': False,
        'scrollZoom': False
    }
)

print("Dashboard atualizado gerado com sucesso! Abra 'dashboard_final.html' no navegador.")
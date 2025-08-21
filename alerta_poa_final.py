import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import folium
from folium import Element
from streamlit_folium import st_folium
import json
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import warnings
import random
from branca.element import Element
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Alerta POA - Sistema Avançado",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #ff4b4b;
}
.alert-high {
    background-color: #ffebee;
    border-left: 4px solid #f44336;
    padding: 1rem;
    margin: 0.5rem 0;
}
.alert-medium {
    background-color: #fff3e0;
    border-left: 4px solid #ff9800;
    padding: 1rem;
    margin: 0.5rem 0;
}
.alert-low {
    background-color: #e8f5e8;
    border-left: 4px solid #4caf50;
    padding: 1rem;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# Função para carregar dados
@st.cache_data
def load_data():
    """Carrega os dados de criminalidade"""
    try:
        df = pd.read_csv('c:/Users/haneg/TESTE/ALERTA-POA-/data/crime_data.csv')
        st.sidebar.success("✅ Dados carregados com sucesso")
        
        # Renomear colunas para compatibilidade com o código existente se necessário
        if 'data' in df.columns:
            df = df.rename(columns={
                'data': 'Data Registro',
                'bairro': 'Bairro',
                'tipo_crime': 'Descricao do Fato'
            })
        df['Data Registro'] = pd.to_datetime(df['Data Registro'])
        
        # Adicionar coluna de hora simulada baseada na data para análise temporal
        # Simula distribuição de crimes ao longo do dia (probabilidades somam 1.0)
        np.random.seed(42)  # Para resultados consistentes
        probs = [0.02, 0.01, 0.01, 0.01, 0.02, 0.03, 0.04, 0.05,
                 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.11,
                 0.10, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03]
        # Normalizar para garantir que soma seja 1.0
        probs = np.array(probs) / np.sum(probs)
        df['Hora'] = np.random.choice(range(24), size=len(df), p=probs)
        
        # Função para determinar período do dia baseado na hora
        def get_periodo(hora):
            if 6 <= hora < 12:
                return 'Manhã'
            elif 12 <= hora < 18:
                return 'Tarde'
            else:
                return 'Noite'
        
        # Adicionar coluna 'Periodo do Dia'
        df['Periodo do Dia'] = df['Hora'].apply(get_periodo)
        
        return df
    except FileNotFoundError:
        st.error("Arquivo de dados não encontrado.")
        return pd.DataFrame()

# Thresholds de segurança baseados em padrões internacionais
# Baseado em dados da ONU, NeighborhoodScout e padrões internacionais de criminalidade
SAFETY_THRESHOLDS = {
    'muito_seguro': 50,      # < 50 crimes por 100k habitantes (padrão países nórdicos)
    'seguro': 150,           # 50-150 crimes por 100k (padrão países desenvolvidos)
    'perigoso': 400,         # 150-400 crimes por 100k (média mundial urbana)
    'muito_perigoso': 400    # > 400 crimes por 100k (alto risco)
}

# População estimada por bairro (dados aproximados baseados em censo IBGE)
POPULACAO_BAIRROS = {
    "Centro Histórico": 40000, "Praia de Belas": 15000, "Cidade Baixa": 25000,
    "Menino Deus": 35000, "Bom Fim": 30000, "Moinhos de Vento": 45000,
    "Floresta": 20000, "Santana": 28000, "Petrópolis": 32000, "Mont Serrat": 18000,
    "Farroupilha": 22000, "Rio Branco": 25000, "Partenon": 50000, "Sarandi": 35000,
    "Centro": 40000, "Azenha": 15000, "Auxiliadora": 25000, "Independência": 30000
}

def calculate_crime_rate_per_100k(crimes_count, population):
    """Calcula taxa de criminalidade por 100.000 habitantes"""
    if population == 0:
        return 0
    return (crimes_count / population) * 100000

def classify_safety_level(crime_rate):
    """Classifica nível de segurança baseado na taxa de criminalidade"""
    if crime_rate < SAFETY_THRESHOLDS['muito_seguro']:
        return 'muito_seguro'
    elif crime_rate < SAFETY_THRESHOLDS['seguro']:
        return 'seguro'
    elif crime_rate < SAFETY_THRESHOLDS['perigoso']:
        return 'perigoso'
    else:
        return 'muito_perigoso'

def get_safety_color(safety_level):
    """Retorna cor baseada no nível de segurança"""
    colors = {
        'muito_seguro': '#006400',    # Verde escuro
        'seguro': '#90EE90',          # Verde claro
        'perigoso': '#FFA500',        # Laranja
        'muito_perigoso': '#8B0000'   # Vermelho extremo
    }
    return colors.get(safety_level, '#808080')

def get_safety_label(safety_level):
    """Retorna rótulo em português para o nível de segurança"""
    labels = {
        'muito_seguro': 'Muito Seguro',
        'seguro': 'Seguro',
        'perigoso': 'Perigoso',
        'muito_perigoso': 'Muito Perigoso'
    }
    return labels.get(safety_level, 'Indefinido')

# Função para carregar estatísticas dos bairros
@st.cache_data
def load_neighborhood_stats(df):
    if df.empty:
        # Dados simulados se não houver dados
        return {
            "Centro Histórico": 45, "Praia de Belas": 28, "Cidade Baixa": 22,
            "Menino Deus": 18, "Bom Fim": 15, "Moinhos de Vento": 12, 
            "Floresta": 20, "Santana": 16, "Petrópolis": 14, "Mont Serrat": 11,
            "Farroupilha": 13, "Rio Branco": 9, "Partenon": 25, "Sarandi": 24
        }
    
    # Calcular estatísticas dos bairros diretamente dos dados
    bairros_stats = df.groupby('Bairro').size().to_dict()
    return bairros_stats

def calculate_risk_score(df, bairros_stats):
    """Calcula score de risco baseado em múltiplos fatores"""
    current_hour = datetime.now().hour
    current_day = datetime.now().weekday()
    
    # Análise por horário (usando a coluna Hora simulada)
    if 'Hora' in df.columns:
        hourly_risk = df.groupby('Hora').size()
        hour_risk = hourly_risk.get(current_hour, 0) / hourly_risk.max() if len(hourly_risk) > 0 else 0
    else:
        hour_risk = 0.5  # Valor padrão se não houver dados de hora
    
    # Análise por dia da semana
    if 'Data Registro' in df.columns:
        daily_risk = df.groupby(df['Data Registro'].dt.dayofweek).size()
        day_risk = daily_risk.get(current_day, 0) / daily_risk.max() if len(daily_risk) > 0 else 0
    else:
        day_risk = 0.5  # Valor padrão se não houver dados de data
    
    # Score combinado (0-100)
    risk_score = (hour_risk * 0.6 + day_risk * 0.4) * 100
    
    return min(100, max(0, risk_score))

def generate_alerts(df, bairros_stats, risk_score):
    """Gera alertas baseados nos dados"""
    alerts = []
    
    # Alerta de risco atual
    if risk_score > 70:
        alerts.append({
            'level': 'high',
            'title': '🔴 ALERTA ALTO',
            'message': f'Risco atual de assalto: {risk_score:.1f}%. Evite sair sozinho(a) neste horário.'
        })
    elif risk_score > 40:
        alerts.append({
            'level': 'medium',
            'title': '🟡 ALERTA MÉDIO',
            'message': f'Risco moderado: {risk_score:.1f}%. Mantenha-se atento(a) aos arredores.'
        })
    else:
        alerts.append({
            'level': 'low',
            'title': '🟢 RISCO BAIXO',
            'message': f'Risco atual: {risk_score:.1f}%. Período relativamente seguro.'
        })
    
    # Top 3 bairros mais perigosos
    top_dangerous = sorted(bairros_stats.items(), key=lambda x: x[1], reverse=True)[:3]
    alerts.append({
        'level': 'medium',
        'title': '⚠️ BAIRROS DE MAIOR RISCO',
        'message': f"Evite: {', '.join([b[0] for b in top_dangerous])}"
    })
    
    # Horário mais perigoso
    if not df.empty:
        dangerous_hour = df.groupby('Hora').size().idxmax()
        alerts.append({
            'level': 'medium',
            'title': '🕐 HORÁRIO DE MAIOR RISCO',
            'message': f'Maior incidência entre {dangerous_hour}h-{dangerous_hour+1}h'
        })
    
    return alerts

def create_prediction_model(df):
    """Cria modelo preditivo simples"""
    if df.empty:
        return None, None
    
    # Preparar dados para predição
    df_model = df.copy()
    df_model['day_of_year'] = df_model['Data Registro'].dt.dayofyear
    df_model['weekday'] = df_model['Data Registro'].dt.dayofweek
    df_model['month'] = df_model['Data Registro'].dt.month
    
    # Contar assaltos por dia
    daily_counts = df_model.groupby(df_model['Data Registro'].dt.date).size().reset_index()
    daily_counts.columns = ['date', 'count']
    daily_counts['date'] = pd.to_datetime(daily_counts['date'])
    daily_counts['day_of_year'] = daily_counts['date'].dt.dayofyear
    daily_counts['weekday'] = daily_counts['date'].dt.dayofweek
    daily_counts['month'] = daily_counts['date'].dt.month
    
    if len(daily_counts) < 10:
        return None, None
    
    # Modelo simples de regressão linear
    X = daily_counts[['day_of_year', 'weekday', 'month']]
    y = daily_counts['count']
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Predições para próximos 7 dias
    future_dates = []
    future_features = []
    
    last_date = daily_counts['date'].max()
    for i in range(1, 8):
        future_date = last_date + timedelta(days=i)
        future_dates.append(future_date)
        future_features.append([
            future_date.dayofyear,
            future_date.weekday(),
            future_date.month
        ])
    
    predictions = model.predict(future_features)
    predictions = np.maximum(0, predictions)  # Não pode ser negativo
    
    return future_dates, predictions

# Dados geográficos simplificados dos bairros (polígonos aproximados)
# Baseado em coordenadas aproximadas dos limites dos bairros de Porto Alegre
BAIRROS_POLYGONS = {
    "Centro Histórico": [[-30.0200, -51.2350], [-30.0200, -51.2200], [-30.0350, -51.2200], [-30.0350, -51.2350]],
    "Cidade Baixa": [[-30.0350, -51.2200], [-30.0350, -51.2100], [-30.0400, -51.2100], [-30.0400, -51.2200]],
    "Bom Fim": [[-30.0300, -51.2150], [-30.0300, -51.2050], [-30.0380, -51.2050], [-30.0380, -51.2150]],
    "Menino Deus": [[-30.0450, -51.2250], [-30.0450, -51.2150], [-30.0550, -51.2150], [-30.0550, -51.2250]],
    "Moinhos de Vento": [[-30.0200, -51.2150], [-30.0200, -51.2050], [-30.0300, -51.2050], [-30.0300, -51.2150]],
    "Floresta": [[-30.0150, -51.2450], [-30.0150, -51.2350], [-30.0250, -51.2350], [-30.0250, -51.2450]],
    "Santana": [[-30.0350, -51.2350], [-30.0350, -51.2250], [-30.0450, -51.2250], [-30.0450, -51.2350]],
    "Petrópolis": [[-30.0450, -51.2450], [-30.0450, -51.2350], [-30.0550, -51.2350], [-30.0550, -51.2450]],
    "Mont Serrat": [[-30.0550, -51.2550], [-30.0550, -51.2450], [-30.0650, -51.2450], [-30.0650, -51.2550]],
    "Farroupilha": [[-30.0250, -51.2150], [-30.0250, -51.2050], [-30.0350, -51.2050], [-30.0350, -51.2150]],
    "Praia de Belas": [[-30.0350, -51.2450], [-30.0350, -51.2350], [-30.0450, -51.2350], [-30.0450, -51.2450]],
    "Rio Branco": [[-30.0050, -51.2250], [-30.0050, -51.2150], [-30.0150, -51.2150], [-30.0150, -51.2250]],
    "Partenon": [[-30.0400, -51.2050], [-30.0400, -51.1950], [-30.0500, -51.1950], [-30.0500, -51.2050]],
    "Sarandi": [[-30.0100, -51.2350], [-30.0100, -51.2250], [-30.0200, -51.2250], [-30.0200, -51.2350]],
    "Lomba do Pinheiro": [[-30.1200, -51.1200], [-30.1200, -51.1100], [-30.1300, -51.1100], [-30.1300, -51.1200]],
    "Restinga": [[-30.1500, -51.1000], [-30.1500, -51.0900], [-30.1600, -51.0900], [-30.1600, -51.1000]],
    "Rubem Berta": [[-29.9800, -51.1800], [-29.9800, -51.1700], [-29.9900, -51.1700], [-29.9900, -51.1800]],
    "Cavalhada": [[-30.0800, -51.2400], [-30.0800, -51.2300], [-30.0900, -51.2300], [-30.0900, -51.2400]],
    "Cristal": [[-30.0700, -51.2200], [-30.0700, -51.2100], [-30.0800, -51.2100], [-30.0800, -51.2200]],
    "Ipanema": [[-30.0900, -51.2500], [-30.0900, -51.2400], [-30.1000, -51.2400], [-30.1000, -51.2500]],
    "Nonoai": [[-30.0600, -51.1900], [-30.0600, -51.1800], [-30.0700, -51.1800], [-30.0700, -51.1900]],
    "Vila Nova": [[-30.0500, -51.1800], [-30.0500, -51.1700], [-30.0600, -51.1700], [-30.0600, -51.1800]],
    "Tristeza": [[-30.1100, -51.2300], [-30.1100, -51.2200], [-30.1200, -51.2200], [-30.1200, -51.2300]],
    "Camaquã": [[-30.1000, -51.2200], [-30.1000, -51.2100], [-30.1100, -51.2100], [-30.1100, -51.2200]],
    "Belém Novo": [[-30.1300, -51.2500], [-30.1300, -51.2400], [-30.1400, -51.2400], [-30.1400, -51.2500]],
    "Glória": [[-30.0100, -51.2100], [-30.0100, -51.2000], [-30.0200, -51.2000], [-30.0200, -51.2100]],
    "Auxiliadora": [[-30.0150, -51.2000], [-30.0150, -51.1900], [-30.0250, -51.1900], [-30.0250, -51.2000]],
    "Higienópolis": [[-30.0250, -51.2000], [-30.0250, -51.1900], [-30.0350, -51.1900], [-30.0350, -51.2000]],
    "Independência": [[-30.0350, -51.2000], [-30.0350, -51.1900], [-30.0450, -51.1900], [-30.0450, -51.2000]],
    "Azenha": [[-30.0450, -51.2000], [-30.0450, -51.1900], [-30.0550, -51.1900], [-30.0550, -51.2000]],
    "Marcílio Dias": [[-30.0550, -51.2000], [-30.0550, -51.1900], [-30.0650, -51.1900], [-30.0650, -51.2000]],
    "Navegantes": [[-29.9900, -51.2100], [-29.9900, -51.2000], [-30.0000, -51.2000], [-30.0000, -51.2100]],
    "Humaitá": [[-29.9800, -51.2000], [-29.9800, -51.1900], [-29.9900, -51.1900], [-29.9900, -51.2000]],
    "Anchieta": [[-29.9700, -51.1900], [-29.9700, -51.1800], [-29.9800, -51.1800], [-29.9800, -51.1900]],
    "Passo da Areia": [[-29.9600, -51.1800], [-29.9600, -51.1700], [-29.9700, -51.1700], [-29.9700, -51.1800]],
    "São Geraldo": [[-29.9500, -51.1700], [-29.9500, -51.1600], [-29.9600, -51.1600], [-29.9600, -51.1700]],
    "Jardim Botânico": [[-30.0700, -51.1800], [-30.0700, -51.1700], [-30.0800, -51.1700], [-30.0800, -51.1800]],
    "Três Figueiras": [[-30.0600, -51.1700], [-30.0600, -51.1600], [-30.0700, -51.1600], [-30.0700, -51.1700]],
    "Chácara das Pedras": [[-30.0500, -51.1600], [-30.0500, -51.1500], [-30.0600, -51.1500], [-30.0600, -51.1600]],
    "Boa Vista": [[-30.0400, -51.1500], [-30.0400, -51.1400], [-30.0500, -51.1400], [-30.0500, -51.1500]],
    "Jardim Lindóia": [[-30.0300, -51.1400], [-30.0300, -51.1300], [-30.0400, -51.1300], [-30.0400, -51.1400]],
    "Jardim do Salso": [[-30.0200, -51.1300], [-30.0200, -51.1200], [-30.0300, -51.1200], [-30.0300, -51.1300]],
    "Jardim Carvalho": [[-30.0100, -51.1200], [-30.0100, -51.1100], [-30.0200, -51.1100], [-30.0200, -51.1200]],
    "Vila Assunção": [[-30.0000, -51.1100], [-30.0000, -51.1000], [-30.0100, -51.1000], [-30.0100, -51.1100]],
    "Pedra Redonda": [[-29.9900, -51.1000], [-29.9900, -51.0900], [-30.0000, -51.0900], [-30.0000, -51.1000]],
    "Serraria": [[-29.9800, -51.0900], [-29.9800, -51.0800], [-29.9900, -51.0800], [-29.9900, -51.0900]],
    "Jardim Sabará": [[-29.9700, -51.0800], [-29.9700, -51.0700], [-29.9800, -51.0700], [-29.9800, -51.0800]],
    "Mário Quintana": [[-29.9600, -51.0700], [-29.9600, -51.0600], [-29.9700, -51.0600], [-29.9700, -51.0700]],
    "Coronel Aparício Borges": [[-29.9500, -51.0600], [-29.9500, -51.0500], [-29.9600, -51.0500], [-29.9600, -51.0600]],
    "Lami": [[-30.1400, -51.2600], [-30.1400, -51.2500], [-30.1500, -51.2500], [-30.1500, -51.2600]],
    "Chapéu do Sol": [[-30.1300, -51.2400], [-30.1300, -51.2300], [-30.1400, -51.2300], [-30.1400, -51.2400]],
    "Ponta Grossa": [[-30.1200, -51.2300], [-30.1200, -51.2200], [-30.1300, -51.2200], [-30.1300, -51.2300]],
    "Teresópolis": [[-30.0800, -51.1600], [-30.0800, -51.1500], [-30.0900, -51.1500], [-30.0900, -51.1600]],
    "Medianeira": [[-30.0900, -51.1500], [-30.0900, -51.1400], [-30.1000, -51.1400], [-30.1000, -51.1500]],
    "Santa Tereza": [[-30.0700, -51.1500], [-30.0700, -51.1400], [-30.0800, -51.1400], [-30.0800, -51.1500]],
    "Morro Santana": [[-30.0600, -51.1400], [-30.0600, -51.1300], [-30.0700, -51.1300], [-30.0700, -51.1400]],
    "Protásio Alves": [[-30.0500, -51.1300], [-30.0500, -51.1200], [-30.0600, -51.1200], [-30.0600, -51.1300]],
    "Jardim Itu": [[-30.0400, -51.1200], [-30.0400, -51.1100], [-30.0500, -51.1100], [-30.0500, -51.1200]],
    "Vila Ipiranga": [[-30.0300, -51.1100], [-30.0300, -51.1000], [-30.0400, -51.1000], [-30.0400, -51.1100]],
    "Agronomia": [[-30.0200, -51.1000], [-30.0200, -51.0900], [-30.0300, -51.0900], [-30.0300, -51.1000]],
    "Jardim São Pedro": [[-30.0100, -51.0900], [-30.0100, -51.0800], [-30.0200, -51.0800], [-30.0200, -51.0900]],
    "Bom Jesus": [[-30.0000, -51.0800], [-30.0000, -51.0700], [-30.0100, -51.0700], [-30.0100, -51.0800]],
    "Guarujá": [[-29.9900, -51.0700], [-29.9900, -51.0600], [-30.0000, -51.0600], [-30.0000, -51.0700]],
    "Espírito Santo": [[-29.9800, -51.0600], [-29.9800, -51.0500], [-29.9900, -51.0500], [-29.9900, -51.0600]],
    "São João": [[-29.9700, -51.0500], [-29.9700, -51.0400], [-29.9800, -51.0400], [-29.9800, -51.0500]],
    "Parque dos Maias": [[-29.9600, -51.0400], [-29.9600, -51.0300], [-29.9700, -51.0300], [-29.9700, -51.0400]],
    "Ilhas": [[-29.9500, -51.0300], [-29.9500, -51.0200], [-29.9600, -51.0200], [-29.9600, -51.0300]],
    "Arquipélago": [[-29.9400, -51.0200], [-29.9400, -51.0100], [-29.9500, -51.0100], [-29.9500, -51.0200]],
    "Hípica": [[-30.0800, -51.2000], [-30.0800, -51.1900], [-30.0900, -51.1900], [-30.0900, -51.2000]],
    "Aberta dos Morros": [[-30.1000, -51.1800], [-30.1000, -51.1700], [-30.1100, -51.1700], [-30.1100, -51.1800]],
    "Serafina Corrêa": [[-30.1100, -51.1600], [-30.1100, -51.1500], [-30.1200, -51.1500], [-30.1200, -51.1600]],
    "Cascata": [[-30.1200, -51.1400], [-30.1200, -51.1300], [-30.1300, -51.1300], [-30.1300, -51.1400]],
    "Passo das Pedras": [[-29.9400, -51.1600], [-29.9400, -51.1500], [-29.9500, -51.1500], [-29.9500, -51.1600]],
    "Sarandi": [[-30.0100, -51.2350], [-30.0100, -51.2250], [-30.0200, -51.2250], [-30.0200, -51.2350]],
    "Mathias Velho": [[-29.9300, -51.1500], [-29.9300, -51.1400], [-29.9400, -51.1400], [-29.9400, -51.1500]],
    "Farrapos": [[-29.9800, -51.2200], [-29.9800, -51.2100], [-29.9900, -51.2100], [-29.9900, -51.2200]]
}

def create_advanced_map(bairros_stats):
    """Cria mapa avançado com coloração por bairros baseada em níveis de segurança"""
    m = folium.Map(
        location=[-30.0346, -51.2087],
        zoom_start=12,
        tiles='OpenStreetMap',
        prefer_canvas=True
    )
    
    # Carregar dados GeoJSON dos bairros
    try:
        with open('data/GeoJSON', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
    except Exception as e:
        st.error(f"Erro ao carregar dados geográficos: {e}")
        return m
    
    # Calcular estatísticas para melhor distribuição de cores
    if bairros_stats:
        max_crimes = max(bairros_stats.values())
        min_crimes = min(bairros_stats.values())
        avg_crimes = sum(bairros_stats.values()) / len(bairros_stats.values())
    else:
        max_crimes = 50
        min_crimes = 0
        avg_crimes = 25
    
    # Adicionar polígonos dos bairros com cores baseadas no nível de segurança
    for feature in geojson_data['features']:
        bairro_geojson = feature['properties']['NOME']
        # Normalizar nome do bairro para corresponder aos dados de crime
        bairro = bairro_geojson.title()
        crimes_count = bairros_stats.get(bairro, 0)
        population = POPULACAO_BAIRROS.get(bairro, 30000)  # População padrão se não encontrada
        
        # Calcular taxa de criminalidade por 100k habitantes
        crime_rate = calculate_crime_rate_per_100k(crimes_count, population)
        
        # Classificar nível de segurança com lógica melhorada
        if crimes_count == 0:
            safety_level = 'muito_seguro'
        elif crimes_count <= avg_crimes * 0.5:
            safety_level = 'seguro'
        elif crimes_count <= avg_crimes * 1.5:
            safety_level = 'perigoso'
        else:
            safety_level = 'muito_perigoso'
        
        # Obter cor e rótulo
        color = get_safety_color(safety_level)
        safety_label = get_safety_label(safety_level)
        
        # Criar popup com informações detalhadas
        popup_html = f"""
        <div style="font-family: Arial; width: 200px;">
            <h4 style="margin: 0; color: {color};">{bairro}</h4>
            <hr style="margin: 5px 0;">
            <p><b>Nível de Segurança:</b> {safety_label}</p>
            <p><b>Crimes Registrados:</b> {crimes_count}</p>
            <p><b>Taxa por 100k hab:</b> {crime_rate:.1f}</p>
            <p><b>População Estimada:</b> {population:,}</p>
        </div>
        """
        
        # Adicionar polígono ao mapa usando GeoJSON
        folium.GeoJson(
            feature,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{bairro}: {safety_label} ({crime_rate:.1f}/100k)",
            style_function=lambda x, color=color: {
                'fillColor': color,
                'color': 'white',  # Bordas brancas para maior contraste
                'weight': 2,       # Bordas mais espessas
                'fillOpacity': 0.8,
                'opacity': 1.0
            }
        ).add_to(m)
    
    # Adicionar legenda
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 140px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4 style="margin: 0 0 10px 0;">Níveis de Segurança</h4>
    <p style="margin: 5px 0;"><i class="fa fa-square" style="color:#006400"></i> Muito Seguro (&lt;50/100k)</p>
    <p style="margin: 5px 0;"><i class="fa fa-square" style="color:#90EE90"></i> Seguro (50-150/100k)</p>
    <p style="margin: 5px 0;"><i class="fa fa-square" style="color:#FFA500"></i> Perigoso (150-400/100k)</p>
    <p style="margin: 5px 0;"><i class="fa fa-square" style="color:#8B0000"></i> Muito Perigoso (&gt;400/100k)</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

def export_report(df, bairros_stats, risk_score):
    """Gera relatório em formato texto"""
    report = f"""
# RELATÓRIO DE SEGURANÇA PÚBLICA - PORTO ALEGRE
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

## RESUMO EXECUTIVO
- Total de assaltos analisados: {len(df)}
- Risco atual: {risk_score:.1f}%
- Período analisado: {df['Data Registro'].min().strftime('%d/%m/%Y') if not df.empty else 'N/A'} a {df['Data Registro'].max().strftime('%d/%m/%Y') if not df.empty else 'N/A'}

## TOP 5 BAIRROS MAIS PERIGOSOS
"""
    
    top_bairros = sorted(bairros_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    for i, (bairro, count) in enumerate(top_bairros, 1):
        report += f"{i}. {bairro}: {count} assaltos\n"
    
    if not df.empty:
        report += f"""
## ANÁLISE TEMPORAL
- Tipo de crime mais comum: {df['Descricao do Fato'].mode()[0] if len(df) > 0 else 'N/A'}
- Período mais perigoso: {df['Periodo do Dia'].mode()[0] if len(df) > 0 else 'N/A'}
- Horário de maior risco: {df.groupby('Hora').size().idxmax()}h

## RECOMENDAÇÕES
1. Evitar os bairros listados acima, especialmente no período noturno
2. Manter atenção redobrada no horário de maior risco
3. Utilizar transporte seguro em áreas de alto risco
4. Reportar atividades suspeitas às autoridades
"""
    
    return report

def main():
    st.title("🚨 Alerta POA - Sistema Avançado de Segurança")
    st.markdown("### Análise Preditiva e Alertas em Tempo Real")
    
    # Carregar dados
    df = load_data()
    bairros_stats = load_neighborhood_stats(df)
    
    # Calcular risco atual
    risk_score = calculate_risk_score(df, bairros_stats)
    
    # Sidebar
    st.sidebar.header("🔍 Controles")
    
    # Filtros
    if not df.empty:
        crime_types = df['Descricao do Fato'].unique()
        selected_crimes = st.sidebar.multiselect(
            "Filtrar por Tipo de Crime",
            crime_types,
            default=crime_types[:5]
        )
        
        periods = df['Periodo do Dia'].unique()
        selected_periods = st.sidebar.multiselect(
            "Filtrar por Período",
            periods,
            default=periods
        )
        
        # Aplicar filtros
        filtered_df = df[
            (df['Descricao do Fato'].isin(selected_crimes)) &
            (df['Periodo do Dia'].isin(selected_periods))
        ]
    else:
        filtered_df = df
    
    # Gerar alertas
    alerts = generate_alerts(filtered_df, bairros_stats, risk_score)
    
    # Seção de alertas
    st.subheader("🚨 Alertas de Segurança")
    
    col_alert1, col_alert2 = st.columns(2)
    
    with col_alert1:
        for alert in alerts[:2]:
            if alert['level'] == 'high':
                st.markdown(f"""
                <div class="alert-high">
                    <h4>{alert['title']}</h4>
                    <p>{alert['message']}</p>
                </div>
                """, unsafe_allow_html=True)
            elif alert['level'] == 'medium':
                st.markdown(f"""
                <div class="alert-medium">
                    <h4>{alert['title']}</h4>
                    <p>{alert['message']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-low">
                    <h4>{alert['title']}</h4>
                    <p>{alert['message']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    with col_alert2:
        for alert in alerts[2:]:
            if alert['level'] == 'high':
                st.markdown(f"""
                <div class="alert-high">
                    <h4>{alert['title']}</h4>
                    <p>{alert['message']}</p>
                </div>
                """, unsafe_allow_html=True)
            elif alert['level'] == 'medium':
                st.markdown(f"""
                <div class="alert-medium">
                    <h4>{alert['title']}</h4>
                    <p>{alert['message']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-low">
                    <h4>{alert['title']}</h4>
                    <p>{alert['message']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Layout principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🗺️ Mapa de Risco Interativo")
        advanced_map = create_advanced_map(bairros_stats)
        map_data = st_folium(advanced_map, width=700, height=500)
    
    with col2:
        st.subheader("📊 Métricas em Tempo Real")
        
        # Métricas principais
        st.metric("🎯 Risco Atual", f"{risk_score:.1f}%")
        st.metric("📍 Total de Assaltos", len(filtered_df))
        
        if not filtered_df.empty:
            most_common = filtered_df['Descricao do Fato'].mode()[0]
            st.metric("🔝 Tipo Mais Comum", most_common)
        
        # Top 5 bairros perigosos
        st.subheader("🏘️ Ranking de Risco")
        top_bairros = sorted(bairros_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for i, (bairro, count) in enumerate(top_bairros, 1):
            if count > 20:
                emoji = "🔴"
            elif count > 15:
                emoji = "🟡"
            else:
                emoji = "🟢"
            st.write(f"{emoji} {i}. **{bairro}**: {count}")
    
    # Análise preditiva
    st.subheader("🔮 Análise Preditiva")
    
    future_dates, predictions = create_prediction_model(filtered_df)
    
    if future_dates and predictions is not None:
        col3, col4 = st.columns(2)
        
        with col3:
            # Gráfico de predição
            fig_pred = go.Figure()
            fig_pred.add_trace(go.Scatter(
                x=future_dates,
                y=predictions,
                mode='lines+markers',
                name='Predição',
                line=dict(color='red', width=3)
            ))
            fig_pred.update_layout(
                title="Predição de Assaltos - Próximos 7 Dias",
                xaxis_title="Data",
                yaxis_title="Número Previsto de Assaltos",
                height=300
            )
            st.plotly_chart(fig_pred, use_container_width=True)
        
        with col4:
            st.write("**Predições por Dia:**")
            for date, pred in zip(future_dates, predictions):
                day_name = date.strftime('%A')
                day_names = {
                    'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
                    'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
                }
                day_pt = day_names.get(day_name, day_name)
                st.write(f"📅 {date.strftime('%d/%m')} ({day_pt}): ~{pred:.0f} assaltos")
    else:
        st.info("Dados insuficientes para análise preditiva.")
    
    # Gráficos avançados
    st.subheader("📈 Análises Avançadas")
    
    if not filtered_df.empty:
        col5, col6 = st.columns(2)
        
        with col5:
            # Análise de correlação por horário e dia da semana
            filtered_df['weekday'] = filtered_df['Data Registro'].dt.dayofweek
            heatmap_data = filtered_df.groupby(['Hora', 'weekday']).size().reset_index(name='count')
            heatmap_pivot = heatmap_data.pivot(index='Hora', columns='weekday', values='count').fillna(0)
            
            dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
            heatmap_pivot.columns = dias_semana
            
            fig_heatmap = px.imshow(
                heatmap_pivot.T,
                labels=dict(x="Hora", y="Dia da Semana", color="Assaltos"),
                title="Mapa de Calor: Hora vs Dia da Semana",
                color_continuous_scale='Reds'
            )
            fig_heatmap.update_layout(height=400)
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        with col6:
            # Tendência mensal
            monthly_data = filtered_df.groupby(filtered_df['Data Registro'].dt.to_period('M')).size()
            fig_monthly = px.line(
                x=monthly_data.index.astype(str),
                y=monthly_data.values,
                title="Tendência Mensal de Assaltos",
                labels={'x': 'Mês', 'y': 'Número de Assaltos'}
            )
            fig_monthly.update_traces(line_color='red')
            fig_monthly.update_layout(height=400)
            st.plotly_chart(fig_monthly, use_container_width=True)
    
    # Exportar relatório
    st.subheader("📄 Exportar Relatório")
    
    if st.button("📊 Gerar Relatório Completo"):
        report = export_report(filtered_df, bairros_stats, risk_score)
        st.download_button(
            label="📥 Baixar Relatório",
            data=report,
            file_name=f"relatorio_seguranca_poa_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
        
        with st.expander("👁️ Visualizar Relatório"):
            st.text(report)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **🔗 Links Úteis:**
    - [Polícia Civil RS](https://pc.rs.gov.br/)
    - [Brigada Militar](https://bm.rs.gov.br/)
    - [Disque Denúncia: 181](tel:181)
    - [SAMU: 192](tel:192)
    - [Polícia: 190](tel:190)
    """)
    
    st.markdown("**Desenvolvido por:** Analista de Dados - Case de Sucesso para Porto Alegre")

if __name__ == "__main__":
    main()


import streamlit as st
import warnings

# Configurar warnings
warnings.filterwarnings('ignore')

def setup_page_config():
    """Configura as configurações da página Streamlit"""
    st.set_page_config(
        page_title="Alerta POA - Sistema Avançado",
        page_icon="🚨",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_custom_css():
    """Aplica CSS customizado para a aplicação"""
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

# Constantes da aplicação
APP_TITLE = "🚨 Alerta POA - Sistema Avançado de Segurança"
APP_SUBTITLE = "### Análise Preditiva e Alertas em Tempo Real"

# Caminhos dos arquivos de dados
DATA_PATHS = {
    'csv_data': '../data/distributed_crime_data.csv',
    'geojson_data': '../data/GeoJSON/bairros_poa.geojson'
}

# Coordenadas dos bairros de Porto Alegre
BAIRROS_COORDS = {
    "Centro": (-30.0277, -51.2287),
    "Cidade Baixa": (-30.0346, -51.2146),
    "Bom Fim": (-30.0346, -51.2087),
    "Menino Deus": (-30.0500, -51.2200),
    "Moinhos de Vento": (-30.0277, -51.2087),
    "Floresta": (-30.0200, -51.2400),
    "Santana": (-30.0400, -51.2300),
    "Petrópolis": (-30.0500, -51.2400),
    "Mont Serrat": (-30.0600, -51.2500),
    "Farroupilha": (-30.0300, -51.2100),
    "Praia de Belas": (-30.0400, -51.2400),
    "Rio Branco": (-30.0100, -51.2200)
}

# Dados simulados para fallback
DEFAULT_NEIGHBORHOOD_STATS = {
    "Centro": 25, "Cidade Baixa": 22, "Bom Fim": 18,
    "Menino Deus": 15, "Moinhos de Vento": 12, "Floresta": 20,
    "Santana": 16, "Petrópolis": 14, "Mont Serrat": 11,
    "Farroupilha": 13, "Praia de Belas": 17, "Rio Branco": 9
}

# Configurações do mapa
MAP_CONFIG = {
    'center_location': [-30.0346, -51.2087],
    'zoom_start': 12,
    'tiles': 'OpenStreetMap'
}

# Links úteis
USEFUL_LINKS = {
    'policia_civil': 'https://pc.rs.gov.br/',
    'brigada_militar': 'https://bm.rs.gov.br/',
    'disque_denuncia': 'tel:181',
    'samu': 'tel:192',
    'policia': 'tel:190'
}
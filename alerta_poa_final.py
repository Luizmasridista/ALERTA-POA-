import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
import json
import numpy as np
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

# Importar módulos refatorados
from modules import data_loader
from modules import security_analysis
from modules import mapping_utils
from modules import visualization
from modules import ui_components

# Configuração da página
st.set_page_config(
    page_title="Alerta POA - Sistema Avançado",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para layout responsivo
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #ff4b4b;
}

.tips-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}

.tip-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 1.5rem;
    color: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border: none;
}

.tip-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.tip-card.critical {
    background: linear-gradient(135deg, #ff416c 0%, #ff4757 100%);
}

.tip-card.high {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.tip-card.medium {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.tip-card.low {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.tip-header {
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.tip-content {
    font-size: 0.95rem;
    line-height: 1.4;
    opacity: 0.95;
}

.tip-priority {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
    margin-top: 0.5rem;
}

@media (max-width: 1200px) {
    .tips-container {
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    }
}

@media (max-width: 768px) {
    .tips-container {
        grid-template-columns: 1fr;
        gap: 0.75rem;
    }
    
    .tip-card {
        padding: 1rem;
        margin: 0 0.5rem;
    }
    
    .tip-header {
        font-size: 1.1rem;
    }
    
    .tip-content {
        font-size: 0.9rem;
    }
}

@media (max-width: 480px) {
    .tips-container {
        margin: 0.5rem 0;
    }
    
    .tip-card {
        padding: 0.75rem;
        margin: 0 0.25rem;
    }
    
    .tip-header {
        font-size: 1rem;
        flex-direction: column;
        align-items: flex-start;
        gap: 0.25rem;
    }
    
    .tip-content {
        font-size: 0.85rem;
        line-height: 1.3;
    }
    
    .tip-priority {
        font-size: 0.75rem;
        padding: 0.2rem 0.5rem;
    }
}
</style>
""", unsafe_allow_html=True)

# Funções de alertas e modelo preditivo removidas - agora em modules/security_analysis.py

# Funções de carregamento de dados removidas - agora em modules/data_loader.py

# Funções de mapeamento e visualização removidas - agora em modules/mapping_utils.py e modules/visualization.py

# Todas as funções de mapeamento, visualização e carregamento de dados foram movidas para os módulos correspondentes

# Todas as funções de visualização foram movidas para modules/visualization.py

def main():
    st.title("🚨 Alerta POA - Sistema Integrado de Segurança")
    
    # Carregar dados integrados usando os módulos
    df = data_loader.load_data()
    bairros_stats = data_loader.load_neighborhood_stats()
    df_seguranca = data_loader.load_security_index_data()
    
    # Calcular risco atual integrado
    if not df.empty and bairros_stats:
        # Calcular score médio baseado nos bairros com mais crimes
        top_bairro = max(bairros_stats.items(), key=lambda x: x[1])[0] if bairros_stats else "Centro"
        risk_data = security_analysis.calculate_risk_score(df, top_bairro)
        risk_score = risk_data['score_risco']
    else:
        risk_score = 0
    
    # Sidebar
    st.sidebar.header("🔍 Controles")
    
    # Filtros
    if not df.empty:
        crime_types = df['tipo_crime'].unique()
        selected_crimes = st.sidebar.multiselect(
            "Filtrar por Tipo de Crime",
            crime_types,
            default=crime_types[:5]
        )
        
        periods = df['periodo_dia'].unique()
        selected_periods = st.sidebar.multiselect(
            "Filtrar por Período",
            periods,
            default=periods
        )
        
        # Aplicar filtros com cache
        @st.cache_data(ttl=1800)  # Cache por 30 minutos
        def apply_filters(df_hash, crime_filters, period_filters):
            df_temp = data_loader.load_data()  # Recarregar dados
            
            # Filtrar por tipo de crime
            if crime_filters:
                df_temp = df_temp[df_temp['tipo_crime'].isin(crime_filters)]
            
            # Filtrar por período
            if period_filters:
                df_temp = df_temp[df_temp['periodo_dia'].isin(period_filters)]
                
            return df_temp
        
        df_hash = hash(str(df.values.tobytes()) if not df.empty else "empty")
        filtered_df = apply_filters(df_hash, selected_crimes, selected_periods)
    else:
        filtered_df = df
    
    # Gerar alertas
    alerts = security_analysis.generate_alerts(filtered_df, threshold_crimes=10, threshold_increase=0.3)
    
    # Seção de dicas úteis com layout responsivo
    st.subheader("💡 Dicas Úteis de Segurança")
    
    # Função para gerar dicas baseadas nos dados atuais
    def generate_contextual_tips(df, bairros_stats):
        contextual_tips = []
        
        # Dica baseada no bairro mais perigoso
        if bairros_stats:
            top_bairro = max(bairros_stats.items(), key=lambda x: x[1])[0]
            contextual_tips.append({
                'tipo': 'Área de Alto Risco',
                'bairro': top_bairro,
                'descricao': f'Redobrar cuidados na região do {top_bairro}. Evite circular sozinho(a) e prefira horários de maior movimento.',
                'prioridade': 'Alta'
            })
        
        # Dica baseada no horário mais perigoso
        if not df.empty and 'periodo_dia' in df.columns:
            periodo_perigoso = df['periodo_dia'].mode()[0] if len(df['periodo_dia'].dropna()) > 0 else 'Noite'
            contextual_tips.append({
                'tipo': 'Horário de Risco',
                'bairro': 'Todas as Regiões',
                'descricao': f'Maior incidência de crimes no período: {periodo_perigoso}. Reforce os cuidados neste horário.',
                'prioridade': 'Média'
            })
        
        # Dica baseada no tipo de crime mais comum
        if not df.empty and 'tipo_crime' in df.columns:
            crime_comum = df['tipo_crime'].mode()[0] if len(df['tipo_crime'].dropna()) > 0 else 'Roubo'
            if 'ROUBO' in crime_comum.upper():
                contextual_tips.append({
                    'tipo': 'Prevenção Específica',
                    'bairro': 'Foco em Roubos',
                    'descricao': 'Roubos são frequentes na região. Evite exibir objetos de valor e mantenha-se em locais movimentados.',
                    'prioridade': 'Alta'
                })
            elif 'FURTO' in crime_comum.upper():
                contextual_tips.append({
                    'tipo': 'Prevenção Específica',
                    'bairro': 'Foco em Furtos',
                    'descricao': 'Furtos são comuns. Mantenha pertences sempre à vista e evite deixar objetos em veículos.',
                    'prioridade': 'Média'
                })
        
        return contextual_tips
    
    # Gerar dicas contextuais baseadas nos dados
    contextual_tips = generate_contextual_tips(filtered_df, bairros_stats)
    
    # Adicionar dicas gerais de segurança
    general_tips = [
        {
            'tipo': 'Prevenção Geral',
            'bairro': 'Todas as Regiões',
            'descricao': 'Evite andar sozinho(a) durante a madrugada. Prefira locais bem iluminados e movimentados.',
            'prioridade': 'Média'
        },
        {
            'tipo': 'Segurança Pessoal',
            'bairro': 'Dica Universal',
            'descricao': 'Mantenha objetos de valor guardados. Evite usar celular em locais isolados.',
            'prioridade': 'Média'
        },
        {
            'tipo': 'Transporte Público',
            'bairro': 'Centros Urbanos',
            'descricao': 'Nos transportes públicos, mantenha-se atento aos pertences e evite dormir.',
            'prioridade': 'Baixa'
        },
        {
            'tipo': 'Emergência',
            'bairro': 'Porto Alegre',
            'descricao': 'Em caso de emergência: Polícia 190, SAMU 192, Bombeiros 193, Disque Denúncia 181.',
            'prioridade': 'Alta'
        },
        {
            'tipo': 'Tecnologia e Segurança',
            'bairro': 'Dica Digital',
            'descricao': 'Use aplicativos de localização compartilhada com familiares. Mantenha o celular carregado.',
            'prioridade': 'Baixa'
        },
        {
            'tipo': 'Vigilância Comunitária',
            'bairro': 'Bairros Residenciais',
            'descricao': 'Participe de grupos de WhatsApp do seu bairro para compartilhar informações de segurança.',
            'prioridade': 'Baixa'
        }
    ]
    
    # Combinar alertas reais com dicas contextuais e gerais
    all_tips = alerts.copy()
    
    # Priorizar dicas contextuais baseadas nos dados
    all_tips.extend(contextual_tips)
    
    # Adicionar dicas gerais se ainda houver espaço
    if len(all_tips) < 6:
        needed_tips = 6 - len(all_tips)
        all_tips.extend(general_tips[:needed_tips])
    
    # Limitar a 8 dicas para não sobrecarregar a interface
    all_tips = all_tips[:8]
    
    # Renderizar cards de dicas usando o componente UI
    ui_components.render_tip_cards(all_tips)
    
    # Adicionar informações adicionais em um expander
    ui_components.render_additional_info_expander()
    
    # Verificar se há dados de operações policiais integrados
    has_police_data = not df_seguranca.empty and all(col in df_seguranca.columns for col in ['mortes_intervencao_policial', 'prisoes_realizadas', 'policiais_envolvidos'])
    
    if has_police_data:
        st.subheader("🚔 Operações Policiais Integradas")
        ui_components.render_police_operations_metrics(filtered_df)
        
        # Análise de efetividade por bairro
        ui_components.render_neighborhood_effectiveness(filtered_df)
    
    # Estatísticas dos novos dados coletados
    ui_components.render_data_statistics(filtered_df)
    
    # Layout principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🗺️ Mapa de Risco Interativo")
        advanced_map = visualization.create_advanced_map(filtered_df, df_seguranca)
        map_data = st_folium(advanced_map, width=700, height=500)
    
    with col2:
        st.subheader("📊 Métricas em Tempo Real")
        
        # Métricas principais
        st.metric("🎯 Risco Atual", f"{risk_score:.1f}%")
        st.metric("📍 Total de Assaltos", len(filtered_df))
        
        if not filtered_df.empty:
            try:
                if 'tipo_crime' in filtered_df.columns and len(filtered_df['tipo_crime'].dropna()) > 0:
                    most_common = filtered_df['tipo_crime'].mode()[0].replace('_', ' ').title()
                    st.metric("🔝 Tipo Mais Comum", most_common)
                else:
                    st.metric("🔝 Tipo Mais Comum", "N/A")
            except (IndexError, ValueError):
                st.metric("🔝 Tipo Mais Comum", "N/A")
        
        # Top 5 bairros perigosos
        ui_components.render_neighborhood_ranking(bairros_stats)
    
    # Análise preditiva
    ui_components.render_prediction_analysis(filtered_df)
    
    # Análise detalhada por tipo de crime
    ui_components.render_crime_type_analysis(filtered_df)
    
    # Gráficos avançados
    ui_components.render_advanced_charts(filtered_df)
    
    # Exportar relatório e footer
    ui_components.render_export_section(filtered_df)
    ui_components.render_footer()

if __name__ == "__main__":
    main()


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

# CSS customizado para layout responsivo e melhor UX
st.markdown("""
<style>
/* Reset e base */
.main .block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Cards de métricas */
.metric-card {
    background-color: #ffffff;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #e9ecef;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    transition: box-shadow 0.2s ease;
}

.metric-card:hover {
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

/* Melhorias gerais de UI */
.stMetric {
    background-color: #ffffff;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #e9ecef;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* Headers e títulos */
h1, h2, h3 {
    color: #212529;
    font-weight: 600;
}

h1 {
    border-bottom: 3px solid #0d6efd;
    padding-bottom: 0.5rem;
    margin-bottom: 2rem;
}

h2 {
    margin-top: 2rem;
    margin-bottom: 1rem;
    color: #495057;
}

/* Sidebar improvements */
.css-1d391kg {
    background-color: #f8f9fa;
}

.css-1d391kg .css-1v0mbdj {
    border-radius: 8px;
    border: 1px solid #e9ecef;
}

/* Botões e elementos interativos */
.stButton > button {
    border-radius: 6px;
    border: 1px solid #0d6efd;
    background-color: #0d6efd;
    color: white;
    font-weight: 500;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background-color: #0b5ed7;
    border-color: #0a58ca;
    transform: translateY(-1px);
}

/* Expanders */
.streamlit-expanderHeader {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 6px;
    font-weight: 500;
}

/* Responsividade */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem;
    }
    
    .metric-card {
        padding: 1rem;
    }
    
    h1 {
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    h2 {
        font-size: 1.25rem;
        margin-top: 1.5rem;
    }
}

@media (max-width: 480px) {
    .main .block-container {
        padding: 0.5rem;
    }
    
    h1 {
        font-size: 1.25rem;
        text-align: center;
    }
}

/* Otimizações para o mapa e redução de carregamento */
.stApp > div[data-testid="stVerticalBlock"] > div.element-container > div.stColumn > div {
    transition: none !important;
}

/* Remover efeitos de carregamento desnecessários */
.stSpinner {
    display: none !important;
}

/* Otimizar renderização do mapa */
iframe[title="streamlit_folium.st_folium"] {
    border: none;
    transition: none !important;
    will-change: auto;
}

/* Reduzir sombreamento durante carregamento */
.stApp {
    background-color: #ffffff;
}

.main .block-container {
    background-color: #ffffff;
    transition: none !important;
}

/* Acessibilidade */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* Alto contraste */
@media (prefers-contrast: high) {
    .metric-card {
        border: 2px solid #000000;
    }
    
    .stMetric {
        border: 2px solid #000000;
    }
}

/* Modo escuro */
@media (prefers-color-scheme: dark) {
    .metric-card {
        background-color: #2d3748;
        border-color: #4a5568;
        color: #e2e8f0;
    }
    
    .stMetric {
        background-color: #2d3748;
        border-color: #4a5568;
        color: #e2e8f0;
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
    # Teste básico para verificar se a função main está sendo executada
    st.title("🚨 Alerta POA - Sistema Integrado de Segurança")
    st.write("✅ Sistema iniciado com sucesso!")
    st.write("📊 Esta é uma versão de teste para identificar problemas.")
    
    # Teste simples de métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Teste 1", "100")
    with col2:
        st.metric("Teste 2", "200")
    with col3:
        st.metric("Teste 3", "300")
    
    st.success("🎉 Se você está vendo esta mensagem, o sistema está funcionando!")
    
    # Comentar temporariamente o carregamento de dados
    # try:
    #     # Carregar dados integrados usando os módulos
    #     with st.spinner("Carregando dados de criminalidade..."):
    #         df = data_loader.load_data()
    #         st.write(f"✅ Dados de criminalidade carregados: {len(df)} registros")
    #     
    #     with st.spinner("Carregando estatísticas dos bairros..."):
    #         bairros_stats = data_loader.load_neighborhood_stats()
    #         st.write(f"✅ Estatísticas dos bairros carregadas: {len(bairros_stats)} bairros")
    #     
    #     with st.spinner("Carregando índice de segurança..."):
    #         df_seguranca = data_loader.load_security_index_data()
    #         st.write(f"✅ Dados de segurança carregados: {len(df_seguranca)} registros")
    # 
    # except Exception as e:
    #     st.error(f"❌ Erro crítico na inicialização: {str(e)}")
    #     import traceback
    #     st.code(traceback.format_exc())
    #     return
    
    return  # Retornar aqui para evitar executar o resto do código
    
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
        
        # Criar mapa otimizado (sem cache devido a problemas de serialização)
        # O cache é aplicado internamente nos dados, não no objeto mapa
        advanced_map = visualization.create_advanced_map(filtered_df, df_seguranca)
        
        # Configurações otimizadas do st_folium para evitar carregamento contínuo
        map_data = st_folium(
            advanced_map, 
            width=700, 
            height=500,
            returned_objects=["last_object_clicked"],  # Limitar objetos retornados
            feature_group_to_add=None,  # Não adicionar grupos de features dinamicamente
            use_container_width=False,  # Usar largura fixa
            key="risk_map"  # Chave única para evitar re-renderizações
        )
    
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
    
    # Seção de exportação de relatório
    st.subheader("📄 Exportar Relatório")
    if st.button("📥 Gerar Relatório de Segurança"):
        try:
            report = visualization.export_report(filtered_df)
            st.download_button(
                label="📄 Download Relatório",
                data=report,
                file_name=f"relatorio_seguranca_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            st.success("✅ Relatório gerado com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao gerar relatório: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; padding: 20px;'>"
        "🚨 <strong>Alerta POA</strong> - Sistema Avançado de Análise de Segurança Pública<br>"
        "Desenvolvido para auxiliar na tomada de decisões baseadas em dados"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()


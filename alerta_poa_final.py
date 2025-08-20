import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
import json
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import warnings
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
    try:
        df = pd.read_csv('/home/ubuntu/assaltos_porto_alegre.csv')
        df['Data Registro'] = pd.to_datetime(df['Data Registro'])
        return df
    except FileNotFoundError:
        st.error("Arquivo de dados não encontrado.")
        return pd.DataFrame()

# Função para carregar estatísticas dos bairros
@st.cache_data
def load_neighborhood_stats():
    try:
        with open('/home/ubuntu/bairros_stats.json', 'r') as f:
            stats = json.load(f)
        return stats
    except FileNotFoundError:
        # Dados simulados se não encontrar o arquivo
        return {
            "Centro": 25, "Cidade Baixa": 22, "Bom Fim": 18,
            "Menino Deus": 15, "Moinhos de Vento": 12, "Floresta": 20,
            "Santana": 16, "Petrópolis": 14, "Mont Serrat": 11,
            "Farroupilha": 13, "Praia de Belas": 17, "Rio Branco": 9
        }

def calculate_risk_score(df, bairros_stats):
    """Calcula score de risco baseado em múltiplos fatores"""
    current_hour = datetime.now().hour
    current_day = datetime.now().weekday()
    
    # Análise por horário
    hourly_risk = df.groupby('Hora').size()
    hour_risk = hourly_risk.get(current_hour, 0) / hourly_risk.max() if len(hourly_risk) > 0 else 0
    
    # Análise por dia da semana
    daily_risk = df.groupby(df['Data Registro'].dt.dayofweek).size()
    day_risk = daily_risk.get(current_day, 0) / daily_risk.max() if len(daily_risk) > 0 else 0
    
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

def create_advanced_map(bairros_stats):
    """Cria mapa avançado com marcadores dinâmicos"""
    m = folium.Map(
        location=[-30.0346, -51.2087],
        zoom_start=12,
        tiles='OpenStreetMap'
    )
    
    # Bairros principais com coordenadas aproximadas
    bairros_coords = {
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
    
    # Adicionar marcadores com cores baseadas no risco
    for bairro, coords in bairros_coords.items():
        count = bairros_stats.get(bairro, 0)
        
        # Definir cor baseada no número de assaltos
        if count > 20:
            color = 'red'
            icon = 'exclamation-sign'
        elif count > 15:
            color = 'orange'
            icon = 'warning-sign'
        elif count > 10:
            color = 'yellow'
            icon = 'info-sign'
        else:
            color = 'green'
            icon = 'ok-sign'
        
        folium.Marker(
            location=coords,
            popup=f"<b>{bairro}</b><br>{count} assaltos registrados",
            tooltip=f"{bairro}: {count} assaltos",
            icon=folium.Icon(color=color, icon=icon)
        ).add_to(m)
    
    # Adicionar círculos de calor
    for bairro, coords in bairros_coords.items():
        count = bairros_stats.get(bairro, 0)
        if count > 0:
            folium.CircleMarker(
                location=coords,
                radius=count,
                popup=f"{bairro}: {count}",
                color='red',
                fill=True,
                opacity=0.6,
                fillOpacity=0.4
            ).add_to(m)
    
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
    bairros_stats = load_neighborhood_stats()
    
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


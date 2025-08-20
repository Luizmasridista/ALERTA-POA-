"""Módulo de componentes de interface do usuário para o sistema Alerta POA.

Este módulo contém:
- Componentes de cards de dicas
- Componentes de métricas
- Componentes de visualização
- Utilitários de interface
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime


def render_tip_cards(all_tips):
    """Renderiza cards de dicas de segurança em carrossel horizontal rotativo.
    
    Args:
        all_tips (list): Lista de dicas/alertas para exibir
    """
    def get_alert_icon(tipo):
        """Retorna ícone baseado no tipo de alerta."""
        icons = {
            'Volume Alto': '📊',
            'Aumento Significativo': '📈',
            'Crimes Graves': '🚨',
            'Tendência Crescente': '⬆️',
            'Área de Risco': '⚠️',
            'Área de Alto Risco': '🔴',
            'Horário de Risco': '🕐',
            'Prevenção Específica': '🛡️',
            'Prevenção Geral': '🔒',
            'Segurança Pessoal': '👤',
            'Transporte Público': '🚌',
            'Emergência': '🚨',
            'Tecnologia e Segurança': '📱',
            'Vigilância Comunitária': '👥'
        }
        return icons.get(tipo, '🔔')
    
    def get_priority_color(prioridade):
        """Retorna cor baseada na prioridade."""
        colors = {
            'Crítica': '#ff416c',
            'Alta': '#f5576c',
            'Média': '#00f2fe',
            'Baixa': '#38f9d7'
        }
        return colors.get(prioridade, '#00f2fe')
    
    if all_tips:
        # Duplicar as dicas para criar efeito de loop infinito
        extended_tips = all_tips * 3  # Triplicar para garantir continuidade
        
        # CSS para o carrossel horizontal rotativo
        carousel_css = """
        <style>
        @keyframes scroll-horizontal {
            0% {
                transform: translateX(0);
            }
            100% {
                transform: translateX(-33.333%);
            }
        }
        
        .carousel-container {
            overflow: hidden;
            width: 100%;
            position: relative;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 20px 0;
            margin: 20px 0;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .carousel-track {
            display: flex;
            width: 300%;
            animation: scroll-horizontal 30s linear infinite;
            gap: 20px;
            padding: 0 20px;
        }
        
        .carousel-card {
            flex: 0 0 300px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }
        
        .carousel-card:hover {
            transform: translateY(-5px);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            font-size: 1.1rem;
            font-weight: bold;
            margin-bottom: 12px;
            color: #333;
        }
        
        .card-icon {
            font-size: 1.5rem;
            margin-right: 10px;
        }
        
        .card-description {
            font-size: 0.9rem;
            line-height: 1.5;
            color: #555;
            margin-bottom: 15px;
        }
        
        .card-priority {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            color: white;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .carousel-container::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            width: 50px;
            height: 100%;
            background: linear-gradient(to right, rgba(102, 126, 234, 1), transparent);
            z-index: 2;
            pointer-events: none;
        }
        
        .carousel-container::after {
            content: '';
            position: absolute;
            right: 0;
            top: 0;
            width: 50px;
            height: 100%;
            background: linear-gradient(to left, rgba(118, 75, 162, 1), transparent);
            z-index: 2;
            pointer-events: none;
        }
        </style>
        """
        
        # Renderizar CSS
        st.markdown(carousel_css, unsafe_allow_html=True)
        
        # Criar HTML do carrossel
        carousel_html = '<div class="carousel-container"><div class="carousel-track">'
        
        for tip in extended_tips:
            icon = get_alert_icon(tip['tipo'])
            color = get_priority_color(tip['prioridade'])
            
            carousel_html += f"""
            <div class="carousel-card">
                <div class="card-header">
                    <span class="card-icon">{icon}</span>
                    <div>
                        <div>{tip['tipo']}</div>
                        <div style="font-size: 0.8rem; color: #666; font-weight: normal;">{tip['bairro']}</div>
                    </div>
                </div>
                <div class="card-description">
                    {tip['descricao']}
                </div>
                <div class="card-priority" style="background: {color};">
                    {tip['prioridade']}
                </div>
            </div>
            """
        
        carousel_html += '</div></div>'
        
        # Renderizar carrossel
        st.markdown(carousel_html, unsafe_allow_html=True)
        
        # Adicionar informação sobre o carrossel
        st.markdown("""
        <div style="text-align: center; margin-top: 10px; color: #666; font-size: 0.8rem;">
            🔄 Carrossel rotativo com dicas de segurança atualizadas automaticamente
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.info("📊 Nenhum alerta disponível no momento.")


def render_metrics_section(risk_score, total_crimes, most_common_crime):
    """Renderiza seção de métricas principais.
    
    Args:
        risk_score (float): Score de risco atual
        total_crimes (int): Total de crimes
        most_common_crime (str): Tipo de crime mais comum
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "🎯 Risco Atual", 
            f"{risk_score:.1f}%",
            help="Score de risco calculado baseado em múltiplos fatores"
        )
    
    with col2:
        st.metric(
            "📍 Total de Crimes", 
            f"{total_crimes:,}",
            help="Total de crimes registrados no período selecionado"
        )
    
    with col3:
        st.metric(
            "🔝 Tipo Mais Comum", 
            most_common_crime,
            help="Tipo de crime com maior incidência"
        )


def render_neighborhood_ranking(bairros_stats, max_items=5):
    """Renderiza ranking de bairros por risco.
    
    Args:
        bairros_stats (dict): Estatísticas por bairro
        max_items (int): Número máximo de itens a exibir
    """
    st.subheader("🏘️ Ranking de Risco")
    
    if bairros_stats:
        top_bairros = sorted(bairros_stats.items(), key=lambda x: x[1], reverse=True)[:max_items]
        
        for i, (bairro, count) in enumerate(top_bairros, 1):
            if count > 20:
                emoji = "🔴"
                risk_level = "Alto"
            elif count > 15:
                emoji = "🟡"
                risk_level = "Médio"
            else:
                emoji = "🟢"
                risk_level = "Baixo"
            
            st.markdown(f"{emoji} **{i}. {bairro}**: {count} crimes - *{risk_level}*")
    else:
        st.info("📊 Dados de bairros não disponíveis")


def render_police_operations_metrics(df):
    """Renderiza métricas de operações policiais.
    
    Args:
        df (pd.DataFrame): DataFrame com dados de operações policiais
    """
    if df.empty:
        st.info("📊 Dados de operações policiais não disponíveis")
        return
    
    # Verificar se as colunas necessárias existem
    required_cols = ['mortes_intervencao_policial', 'prisoes_realizadas', 'policiais_envolvidos']
    if not all(col in df.columns for col in required_cols):
        st.warning("⚠️ Algumas métricas de operações policiais não estão disponíveis")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_mortes = df['mortes_intervencao_policial'].sum()
        st.metric(
            "Mortes por Intervenção", 
            f"{total_mortes}",
            help="Total de mortes por intervenção policial registradas"
        )
    
    with col2:
        total_prisoes = df['prisoes_realizadas'].sum()
        st.metric(
            "Prisões Realizadas", 
            f"{total_prisoes:,}",
            help="Total de prisões realizadas em operações policiais"
        )
    
    with col3:
        total_armas = df['apreensoes_armas'].sum() if 'apreensoes_armas' in df.columns else 0
        st.metric(
            "Armas Apreendidas", 
            f"{total_armas}",
            help="Total de armas apreendidas em operações"
        )
    
    with col4:
        total_drogas = df['apreensoes_drogas_kg'].sum() if 'apreensoes_drogas_kg' in df.columns else 0
        st.metric(
            "Drogas (kg)", 
            f"{total_drogas:,.1f}",
            help="Total de drogas apreendidas em quilogramas"
        )


def render_year_comparison_metrics(df):
    """Renderiza métricas de comparação anual.
    
    Args:
        df (pd.DataFrame): DataFrame com dados de criminalidade
    """
    if df.empty or 'ano' not in df.columns:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    df_2024 = df[df['ano'] == 2024]
    df_2025 = df[df['ano'] == 2025]
    
    with col1:
        st.metric(
            "Total 2024", 
            f"{len(df_2024):,}",
            help="Total de crimes registrados em 2024"
        )
    
    with col2:
        st.metric(
            "2025 (Jan-Ago)", 
            f"{len(df_2025):,}",
            help="Total de crimes registrados em 2025 (Janeiro a Agosto)"
        )
    
    with col3:
        # Projeção anual para 2025
        if len(df_2025) > 0:
            # Calcular projeção baseada nos 8 meses de dados
            projecao_2025 = (len(df_2025) / 8) * 12
            if len(df_2024) > 0:
                variacao_projetada = ((projecao_2025 - len(df_2024)) / len(df_2024)) * 100
                st.metric(
                    "Projeção 2025", 
                    f"{projecao_2025:,.0f}",
                    delta=f"{variacao_projetada:+.1f}%",
                    help="Projeção anual 2025 baseada nos dados de Jan-Ago"
                )
            else:
                st.metric(
                    "Projeção 2025", 
                    f"{projecao_2025:,.0f}",
                    help="Projeção anual 2025 baseada nos dados de Jan-Ago"
                )
    
    with col4:
        # Tipo de crime mais comum
        if 'tipo_crime' in df.columns:
            try:
                if len(df) > 0 and len(df['tipo_crime'].dropna()) > 0:
                    crime_mais_comum = df['tipo_crime'].mode()[0].replace('_', ' ').title()
                else:
                    crime_mais_comum = "N/A"
            except (IndexError, ValueError):
                crime_mais_comum = "N/A"
            
            st.metric(
                "Crime Mais Comum", 
                crime_mais_comum.replace('_', ' ').title() if crime_mais_comum != "N/A" else "N/A",
                help="Tipo de crime com maior incidência no período"
            )


def render_prediction_charts(future_dates, predictions):
    """Renderiza gráficos de predição.
    
    Args:
        future_dates (list): Lista de datas futuras
        predictions (list): Lista de predições
    """
    if future_dates and predictions:
        # Gráfico de predição
        fig_pred = px.line(
            x=[date.strftime('%d/%m') for date in future_dates],
            y=predictions,
            title="Predição de Crimes - Próximos 7 Dias",
            labels={'x': 'Data', 'y': 'Crimes Previstos'}
        )
        fig_pred.update_traces(line_color='orange')
        fig_pred.update_layout(height=400)
        st.plotly_chart(fig_pred, use_container_width=True)
    else:
        st.info("📊 Modelo preditivo não disponível com os dados atuais")


def render_additional_info_expander():
    """Renderiza expander com informações adicionais de segurança."""
    with st.expander("📋 Mais Informações de Segurança"):
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.markdown("""
            **🏠 Segurança Residencial:**
            - Mantenha portões e portas sempre trancados
            - Instale sistemas de iluminação externa
            - Evite postar viagens nas redes sociais
            - Conheça seus vizinhos e participe da vigilância comunitária
            """)
            
        with col_info2:
            st.markdown("""
            **🚗 Segurança no Trânsito:**
            - Mantenha vidros fechados e portas travadas
            - Evite parar em semáforos de áreas isoladas
            - Tenha rotas alternativas planejadas
            - Não reaja a assaltos, priorize sua segurança
            """)


def render_neighborhood_effectiveness(df):
    """Renderiza análise de efetividade por bairro.
    
    Args:
        df (pd.DataFrame): DataFrame com dados de criminalidade e operações
    """
    if df.empty:
        st.info("📊 Dados de efetividade não disponíveis")
        return
    
    st.subheader("🎯 Efetividade das Operações por Bairro")
    
    # Verificar se as colunas necessárias existem
    if 'bairro' not in df.columns:
        st.warning("⚠️ Dados de bairro não disponíveis para análise de efetividade")
        return
    
    # Agrupar dados por bairro
    bairros_stats = {}
    
    for bairro in df['bairro'].unique():
        if pd.isna(bairro):
            continue
            
        df_bairro = df[df['bairro'] == bairro]
        
        # Contar crimes
        total_crimes = len(df_bairro)
        
        # Contar operações (se existir coluna de operações)
        total_operacoes = 0
        if 'prisoes_realizadas' in df.columns:
            total_operacoes = df_bairro['prisoes_realizadas'].sum()
        
        # Calcular efetividade
        if total_crimes > 0 and total_operacoes > 0:
            ratio = total_operacoes / total_crimes
            if ratio >= 0.3:
                efetividade = 'Alta'
                cor = '🟢'
            elif ratio >= 0.15:
                efetividade = 'Média'
                cor = '🟡'
            else:
                efetividade = 'Baixa'
                cor = '🔴'
        else:
            efetividade = 'Não avaliável'
            cor = '⚪'
        
        bairros_stats[bairro] = {
            'crimes': total_crimes,
            'operacoes': total_operacoes,
            'efetividade': efetividade,
            'cor': cor
        }
    
    # Exibir top 10 bairros
    top_bairros = sorted(bairros_stats.items(), key=lambda x: x[1]['crimes'], reverse=True)[:10]
    
    if top_bairros:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🏘️ Bairros com Mais Crimes:**")
            for bairro, stats in top_bairros[:5]:
                st.markdown(f"{stats['cor']} **{bairro}**: {stats['crimes']} crimes - Efetividade: *{stats['efetividade']}*")
        
        with col2:
            st.markdown("**📊 Estatísticas de Efetividade:**")
            if len(top_bairros) > 5:
                for bairro, stats in top_bairros[5:10]:
                    st.markdown(f"{stats['cor']} **{bairro}**: {stats['crimes']} crimes - Efetividade: *{stats['efetividade']}*")
    else:
        st.info("📊 Dados insuficientes para análise de efetividade")


def render_data_statistics(df):
    """Renderiza estatísticas gerais dos dados.
    
    Args:
        df (pd.DataFrame): DataFrame com dados de criminalidade
    """
    if df.empty:
        st.info("📊 Dados estatísticos não disponíveis")
        return
    
    st.subheader("📈 Estatísticas dos Dados")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total de Registros",
            f"{len(df):,}",
            help="Total de registros no dataset atual"
        )
    
    with col2:
        # Período dos dados
        if 'Data Registro' in df.columns:
            try:
                df_temp = df.copy()
                df_temp['Data Registro'] = pd.to_datetime(df_temp['Data Registro'], errors='coerce')
                data_min = df_temp['Data Registro'].min()
                data_max = df_temp['Data Registro'].max()
                if pd.notna(data_min) and pd.notna(data_max):
                    periodo = (data_max - data_min).days
                    st.metric(
                        "Período (dias)",
                        f"{periodo}",
                        help=f"De {data_min.strftime('%d/%m/%Y')} até {data_max.strftime('%d/%m/%Y')}"
                    )
                else:
                    st.metric("Período (dias)", "N/A")
            except:
                st.metric("Período (dias)", "N/A")
        else:
            st.metric("Período (dias)", "N/A")
    
    with col3:
        # Bairros únicos
        if 'bairro' in df.columns:
            bairros_unicos = df['bairro'].nunique()
            st.metric(
                "Bairros Únicos",
                f"{bairros_unicos}",
                help="Número de bairros diferentes nos dados"
            )
        else:
            st.metric("Bairros Únicos", "N/A")
    
    with col4:
        # Tipos de crime únicos
        if 'tipo_crime' in df.columns:
            tipos_unicos = df['tipo_crime'].nunique()
            st.metric(
                "Tipos de Crime",
                f"{tipos_unicos}",
                help="Número de tipos diferentes de crime"
            )
        else:
            st.metric("Tipos de Crime", "N/A")
    
    # Informações adicionais
    with st.expander("📋 Detalhes dos Dados"):
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.markdown("**📊 Colunas Disponíveis:**")
            colunas = list(df.columns)
            for i in range(0, len(colunas), 2):
                if i + 1 < len(colunas):
                    st.markdown(f"• {colunas[i]} • {colunas[i+1]}")
                else:
                    st.markdown(f"• {colunas[i]}")
        
        with col_info2:
            st.markdown("**🔍 Qualidade dos Dados:**")
            total_registros = len(df)
            registros_completos = len(df.dropna())
            completude = (registros_completos / total_registros * 100) if total_registros > 0 else 0
            
            st.markdown(f"• Registros completos: {registros_completos:,} ({completude:.1f}%)")
            st.markdown(f"• Registros com dados faltantes: {total_registros - registros_completos:,}")
            
            if 'Data Registro' in df.columns:
                try:
                    df_temp = df.copy()
                    df_temp['Data Registro'] = pd.to_datetime(df_temp['Data Registro'], errors='coerce')
                    datas_validas = df_temp['Data Registro'].notna().sum()
                    st.markdown(f"• Datas válidas: {datas_validas:,} ({datas_validas/total_registros*100:.1f}%)")
                except:
                    st.markdown("• Datas válidas: N/A")


def render_prediction_analysis(df):
    """Renderiza análise preditiva de crimes.
    
    Args:
        df (pd.DataFrame): DataFrame com dados de criminalidade
    """
    if df.empty:
        st.info("📊 Dados insuficientes para análise preditiva")
        return
    
    st.subheader("🔮 Análise Preditiva")
    
    try:
        # Análise temporal simples
        if 'Data Registro' in df.columns:
            df_temp = df.copy()
            df_temp['Data Registro'] = pd.to_datetime(df_temp['Data Registro'], errors='coerce')
            df_temp = df_temp.dropna(subset=['Data Registro'])
            
            if len(df_temp) > 0:
                # Agrupar por data
                crimes_por_dia = df_temp.groupby(df_temp['Data Registro'].dt.date).size()
                
                if len(crimes_por_dia) >= 7:
                    # Calcular tendência dos últimos 7 dias
                    ultimos_7_dias = crimes_por_dia.tail(7)
                    media_recente = ultimos_7_dias.mean()
                    
                    # Comparar com média geral
                    media_geral = crimes_por_dia.mean()
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Média Últimos 7 Dias",
                            f"{media_recente:.1f}",
                            delta=f"{media_recente - media_geral:+.1f}",
                            help="Comparação com a média geral"
                        )
                    
                    with col2:
                        # Tendência
                        if media_recente > media_geral * 1.1:
                            tendencia = "📈 Crescente"
                            cor = "🔴"
                        elif media_recente < media_geral * 0.9:
                            tendencia = "📉 Decrescente"
                            cor = "🟢"
                        else:
                            tendencia = "➡️ Estável"
                            cor = "🟡"
                        
                        st.metric(
                            "Tendência",
                            tendencia,
                            help="Tendência baseada nos últimos 7 dias"
                        )
                    
                    with col3:
                        # Projeção simples para próximos 3 dias
                        projecao = media_recente * 3
                        st.metric(
                            "Projeção 3 Dias",
                            f"{projecao:.0f} crimes",
                            help="Projeção baseada na média recente"
                        )
                    
                    # Gráfico de tendência
                    if len(crimes_por_dia) > 1:
                        fig = px.line(
                            x=crimes_por_dia.index,
                            y=crimes_por_dia.values,
                            title="Tendência de Crimes por Dia",
                            labels={'x': 'Data', 'y': 'Número de Crimes'}
                        )
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("📊 Dados insuficientes para análise temporal (mínimo 7 dias)")
            else:
                st.info("📊 Dados de data inválidos para análise preditiva")
        else:
            st.info("📊 Coluna de data não encontrada para análise preditiva")
    
    except Exception as e:
        st.error(f"❌ Erro na análise preditiva: {str(e)}")


def render_crime_type_analysis(df):
    """Renderiza análise detalhada por tipo de crime.
    
    Args:
        df (pd.DataFrame): DataFrame com dados de criminalidade
    """
    if df.empty:
        st.info("📊 Dados insuficientes para análise por tipo de crime")
        return
    
    st.subheader("🔍 Análise por Tipo de Crime")
    
    if 'tipo_crime' not in df.columns:
        st.warning("⚠️ Coluna 'tipo_crime' não encontrada")
        return
    
    try:
        # Análise de tipos de crime
        crimes_por_tipo = df['tipo_crime'].value_counts().head(10)
        
        if len(crimes_por_tipo) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de barras
                fig_bar = px.bar(
                    x=crimes_por_tipo.values,
                    y=crimes_por_tipo.index,
                    orientation='h',
                    title="Top 10 Tipos de Crime",
                    labels={'x': 'Quantidade', 'y': 'Tipo de Crime'}
                )
                fig_bar.update_layout(height=400)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                # Gráfico de pizza
                fig_pie = px.pie(
                    values=crimes_por_tipo.values,
                    names=crimes_por_tipo.index,
                    title="Distribuição dos Tipos de Crime"
                )
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Tabela detalhada
            st.markdown("**📋 Detalhamento por Tipo:**")
            
            for i, (tipo, quantidade) in enumerate(crimes_por_tipo.head(5).items(), 1):
                porcentagem = (quantidade / len(df)) * 100
                
                if porcentagem >= 20:
                    emoji = "🔴"
                    nivel = "Muito Alto"
                elif porcentagem >= 10:
                    emoji = "🟡"
                    nivel = "Alto"
                elif porcentagem >= 5:
                    emoji = "🟠"
                    nivel = "Médio"
                else:
                    emoji = "🟢"
                    nivel = "Baixo"
                
                st.markdown(
                    f"{emoji} **{i}. {tipo.replace('_', ' ').title()}**: "
                    f"{quantidade} casos ({porcentagem:.1f}%) - *{nivel}*"
                )
            
            # Análise temporal por tipo (se houver dados de data)
            if 'Data Registro' in df.columns:
                st.markdown("**📈 Tendência Temporal dos Principais Crimes:**")
                
                df_temp = df.copy()
                df_temp['Data Registro'] = pd.to_datetime(df_temp['Data Registro'], errors='coerce')
                df_temp = df_temp.dropna(subset=['Data Registro'])
                
                if len(df_temp) > 0:
                    # Pegar os 3 tipos mais comuns
                    top_3_tipos = crimes_por_tipo.head(3).index
                    
                    df_top3 = df_temp[df_temp['tipo_crime'].isin(top_3_tipos)]
                    
                    if len(df_top3) > 0:
                        # Agrupar por data e tipo
                        crimes_temporal = df_top3.groupby([
                            df_top3['Data Registro'].dt.date,
                            'tipo_crime'
                        ]).size().reset_index(name='quantidade')
                        
                        if len(crimes_temporal) > 0:
                            fig_temporal = px.line(
                                crimes_temporal,
                                x='Data Registro',
                                y='quantidade',
                                color='tipo_crime',
                                title="Evolução Temporal dos Principais Tipos de Crime",
                                labels={'quantidade': 'Número de Crimes', 'Data Registro': 'Data'}
                            )
                            fig_temporal.update_layout(height=400)
                            st.plotly_chart(fig_temporal, use_container_width=True)
        else:
            st.info("📊 Nenhum tipo de crime encontrado nos dados")
    
    except Exception as e:
        st.error(f"❌ Erro na análise por tipo de crime: {str(e)}")


def render_advanced_charts(df):
    """Renderiza gráficos avançados de análise de criminalidade.
    
    Args:
        df (pd.DataFrame): DataFrame com dados de criminalidade
    """
    if df.empty:
        st.info("📊 Dados insuficientes para gráficos avançados")
        return
    
    st.subheader("📈 Análise Avançada")
    
    try:
        # Criar abas para diferentes tipos de análise
        tab1, tab2, tab3 = st.tabs(["📊 Distribuição Temporal", "🗺️ Análise Geográfica", "🔍 Correlações"])
        
        with tab1:
            st.markdown("**Distribuição de Crimes ao Longo do Tempo**")
            
            if 'Data Registro' in df.columns:
                df_temp = df.copy()
                df_temp['Data Registro'] = pd.to_datetime(df_temp['Data Registro'], errors='coerce')
                df_temp = df_temp.dropna(subset=['Data Registro'])
                
                if len(df_temp) > 0:
                    # Análise por hora do dia
                    if len(df_temp) > 10:
                        df_temp['Hora'] = df_temp['Data Registro'].dt.hour
                        crimes_por_hora = df_temp['Hora'].value_counts().sort_index()
                        
                        fig_hora = px.bar(
                            x=crimes_por_hora.index,
                            y=crimes_por_hora.values,
                            title="Distribuição de Crimes por Hora do Dia",
                            labels={'x': 'Hora', 'y': 'Número de Crimes'},
                            color=crimes_por_hora.values,
                            color_continuous_scale='Reds'
                        )
                        fig_hora.update_layout(height=400)
                        st.plotly_chart(fig_hora, use_container_width=True)
                    
                    # Análise por dia da semana
                    if len(df_temp) > 7:
                        df_temp['Dia_Semana'] = df_temp['Data Registro'].dt.day_name()
                        ordem_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        crimes_por_dia_semana = df_temp['Dia_Semana'].value_counts().reindex(ordem_dias, fill_value=0)
                        
                        fig_dia = px.line(
                            x=['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
                            y=crimes_por_dia_semana.values,
                            title="Padrão Semanal de Criminalidade",
                            labels={'x': 'Dia da Semana', 'y': 'Número de Crimes'},
                            markers=True
                        )
                        fig_dia.update_layout(height=400)
                        st.plotly_chart(fig_dia, use_container_width=True)
                else:
                    st.info("📊 Dados de data insuficientes para análise temporal")
            else:
                st.warning("⚠️ Coluna de data não encontrada")
        
        with tab2:
            st.markdown("**Análise por Localização**")
            
            if 'bairro' in df.columns:
                # Top bairros com mais crimes
                crimes_por_bairro = df['bairro'].value_counts().head(10)
                
                if len(crimes_por_bairro) > 0:
                    fig_bairro = px.bar(
                        x=crimes_por_bairro.values,
                        y=crimes_por_bairro.index,
                        orientation='h',
                        title="Top 10 Bairros com Mais Crimes",
                        labels={'x': 'Número de Crimes', 'y': 'Bairro'},
                        color=crimes_por_bairro.values,
                        color_continuous_scale='Reds'
                    )
                    fig_bairro.update_layout(height=500)
                    st.plotly_chart(fig_bairro, use_container_width=True)
                    
                    # Estatísticas dos bairros
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            "Bairro Mais Afetado",
                            crimes_por_bairro.index[0],
                            f"{crimes_por_bairro.iloc[0]} crimes"
                        )
                    
                    with col2:
                        concentracao = (crimes_por_bairro.iloc[0] / len(df)) * 100
                        st.metric(
                            "Concentração",
                            f"{concentracao:.1f}%",
                            "do total de crimes"
                        )
                else:
                    st.info("📊 Dados de bairro insuficientes")
            else:
                st.warning("⚠️ Coluna de bairro não encontrada")
        
        with tab3:
            st.markdown("**Análise de Correlações e Padrões**")
            
            # Análise de tipos de crime vs horário (se disponível)
            if 'tipo_crime' in df.columns and 'Data Registro' in df.columns:
                df_temp = df.copy()
                df_temp['Data Registro'] = pd.to_datetime(df_temp['Data Registro'], errors='coerce')
                df_temp = df_temp.dropna(subset=['Data Registro'])
                
                if len(df_temp) > 20:
                    df_temp['Hora'] = df_temp['Data Registro'].dt.hour
                    
                    # Pegar os 5 tipos de crime mais comuns
                    top_crimes = df_temp['tipo_crime'].value_counts().head(5).index
                    df_filtered = df_temp[df_temp['tipo_crime'].isin(top_crimes)]
                    
                    if len(df_filtered) > 0:
                        # Criar heatmap de crimes por hora e tipo
                        pivot_table = df_filtered.groupby(['Hora', 'tipo_crime']).size().unstack(fill_value=0)
                        
                        if not pivot_table.empty:
                            fig_heatmap = px.imshow(
                                pivot_table.T,
                                title="Padrão de Crimes por Hora e Tipo",
                                labels={'x': 'Hora', 'y': 'Tipo de Crime', 'color': 'Quantidade'},
                                color_continuous_scale='Reds'
                            )
                            fig_heatmap.update_layout(height=400)
                            st.plotly_chart(fig_heatmap, use_container_width=True)
                        
                        # Estatísticas de correlação
                        st.markdown("**📋 Insights dos Padrões:**")
                        
                        for crime_type in top_crimes[:3]:
                            crime_data = df_filtered[df_filtered['tipo_crime'] == crime_type]
                            if len(crime_data) > 0:
                                hora_mais_comum = crime_data['Hora'].mode().iloc[0] if len(crime_data['Hora'].mode()) > 0 else 'N/A'
                                st.markdown(f"• **{crime_type.replace('_', ' ').title()}**: Pico às {hora_mais_comum}h")
                else:
                    st.info("📊 Dados insuficientes para análise de correlações")
            else:
                st.warning("⚠️ Colunas necessárias não encontradas para análise de correlações")
    
    except Exception as e:
        st.error(f"❌ Erro na renderização de gráficos avançados: {str(e)}")


def render_custom_css():
    """Renderiza CSS customizado para melhorar a aparência."""
    st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff4b4b;
    }
    
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    
    .section-divider {
        border-top: 2px solid #e0e0e0;
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
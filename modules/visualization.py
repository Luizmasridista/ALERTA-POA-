"""Módulo para visualização e criação de mapas do sistema Alerta POA.

Este módulo contém:
- Criação de mapas interativos
- Geração de relatórios
- Visualizações de dados
- Exportação de informações
"""

import streamlit as st
import pandas as pd
import folium
import json
import os
from folium.plugins import HeatMap
from datetime import datetime

from .data_loader import load_geojson_data, load_bairros_sem_dados
from .mapping_utils import (
    map_bairro_name, get_color_based_on_synergistic_analysis,
    get_color_for_map_integrated, get_risk_level_for_map_integrated
)
from .security_analysis import calculate_synergistic_security_analysis


def create_advanced_map(df_crimes, df_operacoes=None, use_synergistic_analysis=True):
    """Cria mapa avançado com análise sinérgica.
    
    Args:
        df_crimes (pd.DataFrame): DataFrame com dados de crimes
        df_operacoes (pd.DataFrame): DataFrame com dados de operações policiais
        use_synergistic_analysis (bool): Se deve usar análise sinérgica
        
    Returns:
        folium.Map: Mapa interativo criado
    """
    # Criar mapa centrado em Porto Alegre
    m = folium.Map(
        location=[-30.0346, -51.2177],
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Carregar dados GeoJSON
    geojson_data = load_geojson_data()
    
    if geojson_data:
        # Enriquecer dados GeoJSON com análise sinérgica
        for feature in geojson_data['features']:
            bairro_nome = feature['properties'].get('nome', '')
            
            if use_synergistic_analysis and df_operacoes is not None:
                # Usar análise sinérgica
                analise = calculate_synergistic_security_analysis(
                    df_crimes, df_operacoes, bairro_nome
                )
                
                # Adicionar propriedades da análise sinérgica
                feature['properties'].update({
                    'total_crimes': analise['total_crimes'],
                    'total_operacoes': analise['total_operacoes'],
                    'score_sinergico': analise['score_sinergico'],
                    'nivel_risco': analise['nivel_risco'],
                    'cor_risco': analise['cor_risco'],
                    'recomendacoes': analise['recomendacoes'],
                    'analise_temporal': analise['analise_temporal'],
                    'padroes_crimes': analise['padroes_crimes']
                })
                
                cor = analise['cor_risco']
                
            else:
                # Usar análise tradicional
                if not df_crimes.empty:
                    crimes_bairro = df_crimes[df_crimes['bairro'].str.upper() == bairro_nome.upper()]
                    total_crimes = len(crimes_bairro)
                else:
                    total_crimes = 0
                
                feature['properties'].update({
                    'total_crimes': total_crimes,
                    'total_operacoes': 0,
                    'nivel_risco': get_risk_level_for_map_integrated(total_crimes)
                })
                
                cor = get_color_for_map_integrated(total_crimes)
        
        # Função de estilo para o mapa
        def style_function(feature):
            if use_synergistic_analysis:
                cor = feature['properties'].get('cor_risco', '#90EE90')
            else:
                total_crimes = feature['properties'].get('total_crimes', 0)
                cor = get_color_for_map_integrated(total_crimes)
            
            return {
                'fillColor': cor,
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            }
        
        # Função para criar popup
        def create_popup(feature):
            props = feature['properties']
            bairro = props.get('nome', 'Desconhecido')
            total_crimes = props.get('total_crimes', 0)
            total_operacoes = props.get('total_operacoes', 0)
            nivel_risco = props.get('nivel_risco', 'Baixo')
            
            popup_html = f"""
            <div style="font-family: Arial; width: 300px;">
                <h4 style="margin: 0; color: #2E86AB;">{bairro}</h4>
                <hr style="margin: 5px 0;">
                <p><strong>📊 Total de Crimes:</strong> {total_crimes}</p>
            """
            
            if use_synergistic_analysis:
                score_sinergico = props.get('score_sinergico', 0)
                popup_html += f"""
                <p><strong>🚔 Operações Policiais:</strong> {total_operacoes}</p>
                <p><strong>📈 Score Sinérgico:</strong> {score_sinergico}</p>
                <p><strong>⚠️ Nível de Risco:</strong> {nivel_risco}</p>
                """
                
                # Adicionar recomendações
                recomendacoes = props.get('recomendacoes', [])
                if recomendacoes:
                    popup_html += "<p><strong>💡 Recomendações:</strong></p><ul>"
                    for rec in recomendacoes[:3]:  # Limitar a 3 recomendações
                        popup_html += f"<li>{rec}</li>"
                    popup_html += "</ul>"
                
                # Adicionar análise temporal
                analise_temporal = props.get('analise_temporal', {})
                if analise_temporal:
                    crimes_mes = analise_temporal.get('crimes_ultimo_mes', 0)
                    ops_mes = analise_temporal.get('operacoes_ultimo_mes', 0)
                    popup_html += f"""
                    <hr style="margin: 5px 0;">
                    <p><strong>📅 Último Mês:</strong></p>
                    <p>• Crimes: {crimes_mes}</p>
                    <p>• Operações: {ops_mes}</p>
                    """
            else:
                popup_html += f"<p><strong>⚠️ Nível de Risco:</strong> {nivel_risco}</p>"
            
            popup_html += "</div>"
            return popup_html
        
        # Função para criar tooltip
        def create_tooltip(feature):
            props = feature['properties']
            bairro = props.get('nome', 'Desconhecido')
            total_crimes = props.get('total_crimes', 0)
            nivel_risco = props.get('nivel_risco', 'Baixo')
            
            return f"{bairro}: {total_crimes} crimes - {nivel_risco}"
        
        # Adicionar camada GeoJSON ao mapa
        folium.GeoJson(
            geojson_data,
            style_function=style_function,
            popup=folium.Popup(lambda feature: create_popup(feature), max_width=400),
            tooltip=folium.Tooltip(lambda feature: create_tooltip(feature))
        ).add_to(m)
        
    else:
        # Fallback: usar marcadores pontuais se GeoJSON não estiver disponível
        st.warning("⚠️ Arquivo GeoJSON não encontrado. Usando visualização alternativa.")
        
        if not df_crimes.empty and 'bairro' in df_crimes.columns:
            # Criar marcadores para bairros com crimes
            bairros_crimes = df_crimes['bairro'].value_counts()
            
            # Coordenadas aproximadas para alguns bairros principais
            coordenadas_bairros = {
                'CENTRO HISTÓRICO': [-30.0277, -51.2287],
                'CIDADE BAIXA': [-30.0346, -51.2177],
                'FLORESTA': [-30.0180, -51.2280],
                'SANTANA': [-30.0180, -51.2180],
                'BONFIM': [-30.0080, -51.2080]
            }
            
            for bairro, count in bairros_crimes.head(10).items():
                coords = coordenadas_bairros.get(bairro.upper(), [-30.0346, -51.2177])
                
                if use_synergistic_analysis and df_operacoes is not None:
                    analise = calculate_synergistic_security_analysis(
                        df_crimes, df_operacoes, bairro
                    )
                    cor = analise['cor_risco']
                    nivel_risco = analise['nivel_risco']
                    total_operacoes = analise['total_operacoes']
                else:
                    cor = get_color_for_map_integrated(count)
                    nivel_risco = get_risk_level_for_map_integrated(count)
                    total_operacoes = 0
                
                popup_text = f"""
                <b>{bairro}</b><br>
                Crimes: {count}<br>
                Operações: {total_operacoes}<br>
                Risco: {nivel_risco}
                """
                
                folium.CircleMarker(
                    location=coords,
                    radius=min(20, max(5, count / 2)),
                    popup=popup_text,
                    color='black',
                    fillColor=cor,
                    fillOpacity=0.7,
                    weight=1
                ).add_to(m)
    
    # Adicionar legenda
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>Níveis de Risco</h4>
    <p><i class="fa fa-circle" style="color:#8B0000"></i> Crítico</p>
    <p><i class="fa fa-circle" style="color:#FF0000"></i> Alto</p>
    <p><i class="fa fa-circle" style="color:#FFA500"></i> Médio</p>
    <p><i class="fa fa-circle" style="color:#FFFF00"></i> Baixo</p>
    <p><i class="fa fa-circle" style="color:#90EE90"></i> Muito Baixo</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m


def export_report(df_crimes, df_operacoes=None, bairros_selecionados=None):
    """Gera relatório de segurança em texto.
    
    Args:
        df_crimes (pd.DataFrame): DataFrame com dados de crimes
        df_operacoes (pd.DataFrame): DataFrame com dados de operações policiais
        bairros_selecionados (list): Lista de bairros para incluir no relatório
        
    Returns:
        str: Relatório em formato texto
    """
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("RELATÓRIO DE SEGURANÇA - ALERTA POA")
    report_lines.append(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    report_lines.append("=" * 60)
    report_lines.append("")
    
    if df_crimes.empty:
        report_lines.append("❌ Nenhum dado de criminalidade disponível.")
        return "\n".join(report_lines)
    
    # Estatísticas gerais
    total_crimes = len(df_crimes)
    total_operacoes = len(df_operacoes) if df_operacoes is not None and not df_operacoes.empty else 0
    
    report_lines.append("📊 ESTATÍSTICAS GERAIS")
    report_lines.append("-" * 30)
    report_lines.append(f"Total de crimes registrados: {total_crimes:,}")
    report_lines.append(f"Total de operações policiais: {total_operacoes:,}")
    
    if 'Data Registro' in df_crimes.columns:
        df_temp = df_crimes.copy()
        df_temp['Data Registro'] = pd.to_datetime(df_temp['Data Registro'])
        data_inicio = df_temp['Data Registro'].min().strftime('%d/%m/%Y')
        data_fim = df_temp['Data Registro'].max().strftime('%d/%m/%Y')
        report_lines.append(f"Período analisado: {data_inicio} a {data_fim}")
    
    report_lines.append("")
    
    # Análise por tipo de crime
    if 'tipo_crime' in df_crimes.columns:
        report_lines.append("🔍 CRIMES POR TIPO")
        report_lines.append("-" * 30)
        crimes_por_tipo = df_crimes['tipo_crime'].value_counts().head(10)
        for tipo, count in crimes_por_tipo.items():
            percentual = (count / total_crimes) * 100
            report_lines.append(f"{tipo}: {count:,} ({percentual:.1f}%)")
        report_lines.append("")
    
    # Análise por bairro
    if 'bairro' in df_crimes.columns:
        report_lines.append("🏘️ BAIRROS COM MAIOR INCIDÊNCIA")
        report_lines.append("-" * 30)
        
        bairros_crimes = df_crimes['bairro'].value_counts().head(15)
        
        for bairro, count in bairros_crimes.items():
            if bairros_selecionados and bairro not in bairros_selecionados:
                continue
                
            percentual = (count / total_crimes) * 100
            
            # Adicionar informações de operações se disponível
            ops_info = ""
            if df_operacoes is not None and not df_operacoes.empty:
                ops_bairro = df_operacoes[df_operacoes['bairro'].str.upper() == bairro.upper()]
                total_ops = len(ops_bairro)
                ops_info = f" | Operações: {total_ops}"
            
            report_lines.append(f"{bairro}: {count:,} crimes ({percentual:.1f}%){ops_info}")
        
        report_lines.append("")
    
    # Análise temporal
    if 'Data Registro' in df_crimes.columns:
        report_lines.append("📅 ANÁLISE TEMPORAL")
        report_lines.append("-" * 30)
        
        df_temp = df_crimes.copy()
        df_temp['Data Registro'] = pd.to_datetime(df_temp['Data Registro'])
        
        # Crimes por mês
        df_temp['mes_ano'] = df_temp['Data Registro'].dt.to_period('M')
        crimes_por_mes = df_temp['mes_ano'].value_counts().sort_index().tail(6)
        
        report_lines.append("Crimes por mês (últimos 6 meses):")
        for periodo, count in crimes_por_mes.items():
            report_lines.append(f"  {periodo}: {count:,} crimes")
        
        # Crimes por dia da semana
        if 'Dia da Semana' in df_temp.columns:
            report_lines.append("\nCrimes por dia da semana:")
            crimes_por_dia = df_temp['Dia da Semana'].value_counts()
            for dia, count in crimes_por_dia.items():
                report_lines.append(f"  {dia}: {count:,} crimes")
        
        report_lines.append("")
    
    # Recomendações gerais
    report_lines.append("💡 RECOMENDAÇÕES GERAIS")
    report_lines.append("-" * 30)
    
    if total_operacoes == 0:
        report_lines.append("• Implementar operações policiais preventivas")
    elif total_operacoes < total_crimes * 0.1:
        report_lines.append("• Aumentar frequência de operações policiais")
    
    if 'bairro' in df_crimes.columns:
        bairros_criticos = df_crimes['bairro'].value_counts().head(5)
        report_lines.append(f"• Focar atenção nos bairros: {', '.join(bairros_criticos.index[:3])}")
    
    report_lines.append("• Manter monitoramento contínuo dos indicadores")
    report_lines.append("• Implementar ações comunitárias de segurança")
    report_lines.append("")
    
    # Informações técnicas
    report_lines.append("ℹ️ INFORMAÇÕES TÉCNICAS")
    report_lines.append("-" * 30)
    report_lines.append(f"Sistema: Alerta POA v2.0")
    report_lines.append(f"Fonte dos dados: Dados integrados de criminalidade e operações policiais")
    report_lines.append(f"Método de análise: Análise sinérgica com ponderação por operações")
    report_lines.append("")
    
    report_lines.append("=" * 60)
    report_lines.append("Fim do relatório")
    report_lines.append("=" * 60)
    
    return "\n".join(report_lines)


def create_heatmap_data(df, lat_col=None, lon_col=None):
    """Cria dados para mapa de calor.
    
    Args:
        df (pd.DataFrame): DataFrame com dados de crimes
        lat_col (str): Nome da coluna de latitude
        lon_col (str): Nome da coluna de longitude
        
    Returns:
        list: Lista de coordenadas para o mapa de calor
    """
    heat_data = []
    
    if df.empty:
        return heat_data
    
    # Se não tiver coordenadas, usar coordenadas aproximadas dos bairros
    if lat_col not in df.columns or lon_col not in df.columns:
        # Coordenadas aproximadas para bairros principais
        coordenadas_bairros = {
            'CENTRO HISTÓRICO': [-30.0277, -51.2287],
            'CIDADE BAIXA': [-30.0346, -51.2177],
            'FLORESTA': [-30.0180, -51.2280],
            'SANTANA': [-30.0180, -51.2180],
            'BONFIM': [-30.0080, -51.2080],
            'MENINO DEUS': [-30.0400, -51.2200],
            'PRAIA DE BELAS': [-30.0500, -51.2300],
            'AZENHA': [-30.0350, -51.2100],
            'RIO BRANCO': [-30.0250, -51.2150],
            'NAVEGANTES': [-30.0100, -51.2200]
        }
        
        if 'bairro' in df.columns:
            for bairro, coords in coordenadas_bairros.items():
                crimes_bairro = len(df[df['bairro'].str.upper() == bairro])
                if crimes_bairro > 0:
                    # Adicionar múltiplos pontos baseado na quantidade de crimes
                    for _ in range(min(crimes_bairro, 50)):  # Limitar a 50 pontos por bairro
                        heat_data.append([coords[0], coords[1], 1])
    else:
        # Usar coordenadas reais se disponíveis
        for _, row in df.iterrows():
            if pd.notna(row[lat_col]) and pd.notna(row[lon_col]):
                heat_data.append([row[lat_col], row[lon_col], 1])
    
    return heat_data
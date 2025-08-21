"""Módulo para visualização e criação de mapas do sistema Alerta POA.

Este módulo contém:
- Criação de mapas interativos de análise de risco
- Sistema de tooltips informativos
- Geração de relatórios
- Visualizações de dados
- Exportação de informações

Versão: 2.0 - Completamente reescrito para maior modularidade e precisão
"""

import streamlit as st
import pandas as pd
import folium
import json
import os
from folium.plugins import HeatMap
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any

from .data_loader import load_geojson_data, load_bairros_sem_dados
from .mapping_utils import (
    map_bairro_name, get_color_based_on_synergistic_analysis,
    get_color_for_map_integrated, get_risk_level_for_map_integrated
)
from .security_analysis import calculate_synergistic_security_analysis


class RiskMapGenerator:
    """Classe principal para geração de mapas de análise de risco."""
    
    def __init__(self):
        """Inicializa o gerador de mapas de risco."""
        self.porto_alegre_coords = [-30.0346, -51.2177]
        self.default_zoom = 11
        self.geojson_data = None
        self._load_geojson()
    
    def _load_geojson(self) -> None:
        """Carrega dados GeoJSON dos bairros."""
        try:
            self.geojson_data = load_geojson_data()
        except Exception as e:
            st.error(f"Erro ao carregar dados GeoJSON: {e}")
            self.geojson_data = None
    
    def _calculate_neighborhood_stats(self, df_crimes: pd.DataFrame, 
                                    df_operacoes: Optional[pd.DataFrame] = None) -> Dict[str, Dict[str, Any]]:
        """Calcula estatísticas COMPLETAS por bairro usando análise sinérgica.
        
        Args:
            df_crimes: DataFrame com dados de crimes integrados
            df_operacoes: DataFrame com dados de operações policiais (legacy)
            
        Returns:
            Dict com estatísticas completas por bairro
        """
        stats = {}
        
        if df_crimes.empty:
            return stats
        
        # Agrupar crimes por bairro
        bairros_unicos = df_crimes['bairro'].unique()
        
        for bairro in bairros_unicos:
            if pd.isna(bairro) or bairro.strip() == '':
                continue
                
            bairro_normalizado = bairro.upper().strip()
            
            # Usar análise sinérgica completa da nova função
            try:
                analise_completa = calculate_synergistic_security_analysis(
                    df_crimes, df_operacoes, bairro
                )
                
                # Extrair dados da análise sinérgica
                stats[bairro_normalizado] = {
                    'nome_original': bairro,
                    'total_crimes': analise_completa['total_crimes'],
                    'total_operacoes': analise_completa['total_operacoes'],
                    'mortes_confronto': analise_completa['mortes_confronto'],
                    'prisoes_realizadas': analise_completa['prisoes_realizadas'],
                    'apreensoes_armas': analise_completa['apreensoes_armas'],
                    'apreensoes_drogas': analise_completa['apreensoes_drogas'],
                    'operacoes_ativas': analise_completa['operacoes_ativas'],
                    'efetividade_global': analise_completa['efetividade_global'],
                    'nivel_risco': analise_completa['nivel_risco'],
                    'cor': analise_completa['cor'],
                    'score_risco': analise_completa['score_sinergico'],
                    'recomendacoes': analise_completa['recomendacoes'],
                    'popup_content': analise_completa['popup_content']
                }
                
            except Exception as e:
                # Fallback para cálculo básico em caso de erro
                st.warning(f"Erro na análise sinérgica para {bairro}: {e}")
                crimes_bairro = df_crimes[df_crimes['bairro'].str.upper().str.strip() == bairro_normalizado]
                total_crimes = len(crimes_bairro)
                
                stats[bairro_normalizado] = {
                    'nome_original': bairro,
                    'total_crimes': total_crimes,
                    'total_operacoes': 0,
                    'mortes_confronto': 0,
                    'prisoes_realizadas': 0,
                    'apreensoes_armas': 0,
                    'apreensoes_drogas': 0,
                    'operacoes_ativas': 0,
                    'efetividade_global': 0,
                    'nivel_risco': self._calculate_risk_level(total_crimes, 0, 0),
                    'cor': self._calculate_risk_color(total_crimes, 0, 0),
                    'score_risco': self._calculate_risk_score(total_crimes, 0, 0),
                    'recomendacoes': [],
                    'popup_content': ''
                }
        
        return stats
    
    def _calculate_risk_score(self, crimes: int, operacoes: int, mortes: int) -> float:
        """Calcula score numérico de risco.
        
        Args:
            crimes: Número de crimes
            operacoes: Número de operações policiais
            mortes: Número de mortes em confronto
            
        Returns:
            Score de risco (0-100)
        """
        # Score base dos crimes
        score = crimes * 1.0
        
        # Penalidade severa por mortes
        if mortes > 0:
            score += mortes * 50
        
        # Redução por efetividade das operações
        if operacoes > 0 and crimes > 0:
            efetividade = min(0.4, operacoes / crimes)
            score *= (1 - efetividade)
        
        return min(100, score)
    
    def _calculate_risk_level(self, crimes: int, operacoes: int, mortes: int) -> str:
        """Determina nível de risco textual.
        
        Args:
            crimes: Número de crimes
            operacoes: Número de operações policiais
            mortes: Número de mortes em confronto
            
        Returns:
            Nível de risco com emoji
        """
        score = self._calculate_risk_score(crimes, operacoes, mortes)
        
        if score >= 80:
            return "⚫ Crítico"
        elif score >= 60:
            return "🔴 Muito Alto"
        elif score >= 40:
            return "🟠 Alto"
        elif score >= 25:
            return "🟡 Médio-Alto"
        elif score >= 15:
            return "🟡 Médio"
        elif score >= 8:
            return "🟢 Baixo-Médio"
        elif score >= 3:
            return "🟢 Baixo"
        else:
            return "🟢 Muito Baixo"
    
    def _calculate_risk_color(self, crimes: int, operacoes: int, mortes: int) -> str:
        """Determina cor do risco.
        
        Args:
            crimes: Número de crimes
            operacoes: Número de operações policiais
            mortes: Número de mortes em confronto
            
        Returns:
            Código de cor hexadecimal
        """
        score = self._calculate_risk_score(crimes, operacoes, mortes)
        
        if score >= 80:
            return '#2B0000'  # Preto avermelhado - Crítico
        elif score >= 60:
            return '#8B0000'  # Vermelho escuro - Muito Alto
        elif score >= 40:
            return '#FF0000'  # Vermelho - Alto
        elif score >= 25:
            return '#FF4500'  # Laranja vermelho - Médio-Alto
        elif score >= 15:
            return '#FFA500'  # Laranja - Médio
        elif score >= 8:
            return '#FFD700'  # Dourado - Baixo-Médio
        elif score >= 3:
            return '#FFFF00'  # Amarelo - Baixo
        else:
            return '#90EE90'  # Verde claro - Muito Baixo
    
    def _create_tooltip(self, bairro_stats: Dict[str, Any]) -> str:
        """Cria tooltip RICO E INFORMATIVO usando TODOS os dados disponíveis.
        
        Args:
            bairro_stats: Estatísticas do bairro com todos os indicadores
            
        Returns:
            Tooltip HTML rico com todos os dados
        """
        nome = bairro_stats.get('NOME', bairro_stats.get('nome_original', 'Desconhecido'))
        crimes = bairro_stats['total_crimes']
        operacoes = bairro_stats['total_operacoes']
        mortes = bairro_stats['mortes_confronto']
        prisoes = bairro_stats.get('prisoes_realizadas', 0)
        armas = bairro_stats.get('apreensoes_armas', 0)
        drogas = bairro_stats.get('apreensoes_drogas', 0)
        ops_ativas = bairro_stats.get('operacoes_ativas', 0)
        efetividade = bairro_stats.get('efetividade_global', 0)
        nivel = bairro_stats['nivel_risco']
        score = bairro_stats['score_risco']
        
        # Criar indicadores visuais
        indicadores = []
        if mortes > 0:
            indicadores.append(f"💀 {mortes}")
        if prisoes > 0:
            indicadores.append(f"🔒 {prisoes}")
        if armas > 0:
            indicadores.append(f"🔫 {armas}")
        if drogas > 0:
            indicadores.append(f"💊 {drogas:.1f}kg")
        if ops_ativas > 0:
            indicadores.append(f"🚨 {ops_ativas}")
        
        # Tooltip rico com dados estruturados
        tooltip_parts = [
            f"📍 <strong>{nome}</strong>",
            f"📊 {crimes} crimes | 👮 {operacoes} policiais"
        ]
        
        if indicadores:
            tooltip_parts.append(" | ".join(indicadores))
        
        if efetividade > 0:
            tooltip_parts.append(f"📈 Efetividade: {efetividade:.1f}%")
        
        tooltip_parts.extend([
            f"⚠️ {nivel} (Score: {score:.1f})"
        ])
        
        return "<br>".join(tooltip_parts)
    
    def _create_popup(self, bairro_stats: Dict[str, Any]) -> str:
        """Cria popup ULTRA DETALHADO com TODOS os indicadores integrados.
        
        Args:
            bairro_stats: Estatísticas completas do bairro com todos os indicadores
            
        Returns:
            HTML do popup rico e informativo
        """
        nome = bairro_stats.get('NOME', bairro_stats.get('nome_original', 'Desconhecido'))
        crimes = bairro_stats['total_crimes']
        operacoes = bairro_stats['total_operacoes']
        mortes = bairro_stats['mortes_confronto']
        prisoes = bairro_stats.get('prisoes_realizadas', 0)
        armas = bairro_stats.get('apreensoes_armas', 0)
        drogas = bairro_stats.get('apreensoes_drogas', 0)
        ops_ativas = bairro_stats.get('operacoes_ativas', 0)
        efetividade = bairro_stats.get('efetividade_global', 0)
        nivel = bairro_stats['nivel_risco']
        score = bairro_stats['score_risco']
        
        # Usar recomendações da análise sinérgica se disponível
        recomendacoes = bairro_stats.get('recomendacoes', self._get_recommendations(score, operacoes, crimes))
        
        popup_html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; width: 420px; padding: 8px;">
            <h4 style="color: #1f4e79; margin: 0 0 12px 0; padding-bottom: 8px; border-bottom: 2px solid #e1e5e9; font-size: 16px;">
                📍 {nome}
            </h4>
            
            <!-- Seção de Crimes e Operações -->
            <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                <h5 style="color: #495057; margin: 0 0 8px 0; font-size: 14px;">📊 Estatísticas de Segurança</h5>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; font-size: 12px;">
                    <div><strong>📊 Crimes:</strong> {crimes}</div>
                    <div><strong>👮 Policiais:</strong> {int(operacoes)}</div>
                    <div><strong>🔒 Prisões:</strong> {int(prisoes)}</div>
                    <div><strong>💀 Mortes:</strong> {int(mortes)}</div>
                    <div><strong>🔫 Armas:</strong> {int(armas)}</div>
                    <div><strong>💊 Drogas:</strong> {drogas:.1f}kg</div>
                </div>
            </div>
            
            <!-- Seção de Operações Ativas -->
            <div style="background: #e8f4fd; padding: 10px; border-radius: 6px; margin-bottom: 10px;">
                <h5 style="color: #0066cc; margin: 0 0 6px 0; font-size: 13px;">🚨 Operações & Efetividade</h5>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px;">
                    <div><strong>Op. Ativas:</strong> {int(ops_ativas)}</div>
                    <div><strong>Efetividade:</strong> {efetividade:.1f}%</div>
                </div>
            </div>
            
            <!-- Score e Nível de Risco -->
            <div style="background: #f0f0f0; padding: 10px; border-radius: 6px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 14px; font-weight: bold; color: #495057;">⚠️ {nivel}</div>
                        <div style="font-size: 12px; color: #666;">📈 Score de Risco: {score:.1f}</div>
                    </div>
                </div>
            </div>
        """
        
        # Seção de Recomendações
        if recomendacoes:
            popup_html += """
            <div style="background: #e8f4fd; padding: 10px; border-radius: 6px; border-left: 3px solid #0066cc;">
                <strong style="color: #0066cc; font-size: 13px;">💡 Recomendações Estratégicas:</strong>
                <ul style="margin: 6px 0 0 0; padding-left: 18px; font-size: 11px; color: #333; line-height: 1.4;">
            """
            
            for rec in recomendacoes[:4]:  # Máximo 4 recomendações  
                popup_html += f"<li style='margin-bottom: 3px;'>{rec}</li>"
            
            popup_html += "</ul></div>"
        
        popup_html += "</div>"
        
        return popup_html
    
    def _get_recommendations(self, score: float, operacoes: int, crimes: int) -> List[str]:
        """Gera recomendações baseadas no score de risco.
        
        Args:
            score: Score de risco
            operacoes: Número de operações
            crimes: Número de crimes
            
        Returns:
            Lista de recomendações
        """
        recomendacoes = []
        
        if score >= 60:
            recomendacoes.extend([
                "Aumentar patrulhamento imediatamente",
                "Implementar operações preventivas urgentes",
                "Reforçar iluminação e segurança pública"
            ])
        elif score >= 40:
            recomendacoes.extend([
                "Intensificar patrulhamento na região",
                "Implementar ações comunitárias",
                "Monitorar pontos críticos"
            ])
        elif score >= 25:
            recomendacoes.extend([
                "Manter vigilância regular",
                "Implementar ações preventivas",
                "Fortalecer policiamento comunitário"
            ])
        else:
            recomendacoes.append("Manter ações preventivas atuais")
        
        # Recomendações específicas
        if operacoes == 0 and crimes > 10:
            recomendacoes.append("Considerar implementar operações policiais")
        
        if crimes > 50 and operacoes < crimes * 0.1:
            recomendacoes.append("Aumentar frequência de operações")
        
        return recomendacoes
    
    def _create_legend(self) -> str:
        """Cria legenda HTML para o mapa.
        
        Returns:
            HTML da legenda
        """
        return """
        <div style="position: fixed; 
                    bottom: 20px; right: 20px; width: 240px; 
                    background: rgba(255, 255, 255, 0.95); 
                    border: 2px solid #333; 
                    border-radius: 12px;
                    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
                    z-index: 9999; 
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 12px; 
                    padding: 16px">
        <h4 style="margin: 0 0 12px 0; color: #1f4e79; text-align: center; 
                   border-bottom: 2px solid #e1e5e9; padding-bottom: 8px; font-size: 14px;">
            🗺️ Níveis de Risco
        </h4>
        <div style="display: flex; flex-direction: column; gap: 6px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 18px; height: 18px; background: #2B0000; border-radius: 50%; border: 1px solid #000;"></div>
                <span style="font-weight: 500;">⚫ Crítico</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 18px; height: 18px; background: #8B0000; border-radius: 50%; border: 1px solid #000;"></div>
                <span style="font-weight: 500;">🔴 Muito Alto</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 18px; height: 18px; background: #FF0000; border-radius: 50%; border: 1px solid #000;"></div>
                <span style="font-weight: 500;">🟠 Alto</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 18px; height: 18px; background: #FF4500; border-radius: 50%; border: 1px solid #000;"></div>
                <span style="font-weight: 500;">🟡 Médio-Alto</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 18px; height: 18px; background: #FFA500; border-radius: 50%; border: 1px solid #000;"></div>
                <span style="font-weight: 500;">🟡 Médio</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 18px; height: 18px; background: #FFD700; border-radius: 50%; border: 1px solid #000;"></div>
                <span style="font-weight: 500;">🟢 Baixo-Médio</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 18px; height: 18px; background: #FFFF00; border-radius: 50%; border: 1px solid #000;"></div>
                <span style="font-weight: 500;">🟢 Baixo</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 18px; height: 18px; background: #90EE90; border-radius: 50%; border: 1px solid #000;"></div>
                <span style="font-weight: 500;">🟢 Muito Baixo</span>
            </div>
        </div>
        <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid #e1e5e9; 
                    font-size: 10px; color: #6c757d; text-align: center; line-height: 1.3;">
            Baseado em crimes, operações<br>policiais e mortes em confronto
        </div>
        </div>
        """
    
    def create_risk_map(self, df_crimes: pd.DataFrame, 
                       df_operacoes: Optional[pd.DataFrame] = None) -> folium.Map:
        """Cria mapa de análise de risco com LOADING OTIMIZADO e dados COMPLETOS.
        
        Args:
            df_crimes: DataFrame com dados de crimes integrados
            df_operacoes: DataFrame com dados de operações policiais
            
        Returns:
            Mapa Folium otimizado e responsivo
        """
        # Criar mapa base com configurações otimizadas para performance
        m = folium.Map(
            location=self.porto_alegre_coords,
            zoom_start=self.default_zoom,
            tiles='OpenStreetMap',
            prefer_canvas=True,  # Melhor performance
            control_scale=True,
            zoom_control=True,
            scrollWheelZoom=True,
            dragging=True,
            tap=False,  # Desabilitar tap para melhor performance
            tap_tolerance=10,  # Reduzir tolerância
            world_copy_jump=False,  # Evitar cópias do mundo
            close_popup_on_click=True,
            bounce_at_zoom_limits=True,
            keyboard=False,  # Desabilitar controle por teclado para performance
            double_click_zoom=True,
            box_zoom=False,  # Desabilitar box zoom para performance
            max_bounds=None,  # Sem limites para navegação mais fluida
            min_zoom=9,  # Zoom mínimo para evitar muito zoom out
            max_zoom=18  # Zoom máximo para evitar muito zoom in
        )
        
        # OTIMIZAÇÃO: Usar progress bar para indicar progresso do carregamento
        with st.spinner('🗺️ Processando dados de segurança...'):
            neighborhood_stats = self._calculate_neighborhood_stats(df_crimes, df_operacoes)
        
        if not neighborhood_stats:
            st.warning("⚠️ Nenhum dado de criminalidade disponível para visualização.")
            return m
        
        # Progress feedback para o usuário
        with st.spinner(f'🎨 Renderizando mapa com {len(neighborhood_stats)} bairros...'):
            # Adicionar camadas GeoJSON se disponível
            if self.geojson_data:
                self._add_geojson_layer(m, neighborhood_stats)
            else:
                self._add_marker_layer(m, neighborhood_stats)
            
            # Adicionar legenda otimizada
            legend_html = self._create_legend()
            m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    
    def _style_function(self, feature):
        """Função de estilo para features GeoJSON."""
        return {
            'fillColor': feature['properties'].get('cor', '#90EE90'),
            'color': '#333333',
            'weight': 1.5,
            'fillOpacity': 0.8,
            'opacity': 1
        }
    
    def _highlight_function(self, feature):
        """Função de destaque para features GeoJSON."""
        return {
            'fillColor': feature['properties'].get('cor', '#90EE90'),
            'color': '#000000',
            'weight': 3,
            'fillOpacity': 0.9,
            'opacity': 1
        }
    
    def _add_geojson_layer(self, m: folium.Map, stats: Dict[str, Dict[str, Any]]) -> None:
        """Adiciona camada GeoJSON ao mapa.
        
        Args:
            m: Mapa Folium
            stats: Estatísticas por bairro
        """
        # Enriquecer dados GeoJSON com estatísticas
        for feature in self.geojson_data['features']:
            bairro_nome = feature['properties'].get('NOME', '').upper().strip()
            
            if bairro_nome in stats:
                feature['properties'].update(stats[bairro_nome])
            else:
                # Bairro sem dados
                feature['properties'].update({
                    'total_crimes': 0,
                    'total_operacoes': 0,
                    'mortes_confronto': 0,
                    'nivel_risco': '🟢 Muito Baixo',
                    'cor': '#90EE90',
                    'score_risco': 0
                })
        
        # Adicionar camada GeoJSON com TOOLTIPS RICOS e dados COMPLETOS
        geojson_layer = folium.GeoJson(
            self.geojson_data,
            style_function=self._style_function,
            highlight_function=self._highlight_function,
            popup=folium.GeoJsonPopup(
                fields=[
                    'NOME', 'total_crimes', 'total_operacoes', 'prisoes_realizadas',
                    'apreensoes_armas', 'apreensoes_drogas', 'efetividade_global', 
                    'nivel_risco', 'score_risco'
                ],
                aliases=[
                    'Bairro:', 'Crimes:', 'Policiais:', 'Prisões:',
                    'Armas Apreendidas:', 'Drogas (kg):', 'Efetividade (%):', 
                    'Nível de Risco:', 'Score:'
                ],
                localize=True,
                sticky=True,
                labels=True,
                max_width=450,  # Aumentar largura para mais informações
                style="background-color: white; border: 2px solid #333; border-radius: 8px; font-family: 'Segoe UI', Arial, sans-serif;"
            ),
            tooltip=folium.GeoJsonTooltip(
                fields=[
                    'NOME', 'total_crimes', 'prisoes_realizadas', 'apreensoes_armas',
                    'efetividade_global', 'nivel_risco'
                ],
                aliases=[
                    'Bairro:', 'Crimes:', 'Prisões:', 'Armas:',
                    'Efetividade:', 'Risco:'
                ],
                localize=True,
                sticky=True,
                labels=True,
                style="background-color: rgba(255, 255, 255, 0.95); border: 1px solid #333; border-radius: 6px; font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; padding: 8px;"
            )
        )
        geojson_layer.add_to(m)
    
    def _add_marker_layer(self, m: folium.Map, stats: Dict[str, Dict[str, Any]]) -> None:
        """Adiciona camada de marcadores como fallback.
        
        Args:
            m: Mapa Folium
            stats: Estatísticas por bairro
        """
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
        
        for bairro_norm, bairro_stats in stats.items():
            coords = coordenadas_bairros.get(bairro_norm, self.porto_alegre_coords)
            
            folium.CircleMarker(
                location=coords,
                radius=min(25, max(8, bairro_stats['total_crimes'] / 3)),
                popup=folium.Popup(self._create_popup(bairro_stats), max_width=350),
                tooltip=self._create_tooltip(bairro_stats),
                color='#333333',
                fillColor=bairro_stats['cor'],
                fillOpacity=0.8,
                weight=2
            ).add_to(m)


# Instância global do gerador
_risk_map_generator = RiskMapGenerator()


def create_risk_map(df_crimes: pd.DataFrame, df_operacoes: Optional[pd.DataFrame] = None) -> folium.Map:
    """Função principal para criar mapa de risco.
    
    Args:
        df_crimes: DataFrame com dados de crimes
        df_operacoes: DataFrame com dados de operações policiais
        
    Returns:
        Mapa Folium configurado
    """
    return _risk_map_generator.create_risk_map(df_crimes, df_operacoes)


def create_advanced_map(df_crimes: pd.DataFrame, df_operacoes: Optional[pd.DataFrame] = None, 
                       use_synergistic_analysis: bool = True) -> folium.Map:
    """Função de compatibilidade para criar mapa avançado.
    
    Args:
        df_crimes: DataFrame com dados de crimes
        df_operacoes: DataFrame com dados de operações policiais
        use_synergistic_analysis: Parâmetro de compatibilidade (ignorado)
        
    Returns:
        Mapa Folium configurado
    """
    return create_risk_map(df_crimes, df_operacoes)


def export_report(df_crimes: pd.DataFrame, df_operacoes: Optional[pd.DataFrame] = None, 
                 bairros_selecionados: Optional[List[str]] = None) -> str:
    """Gera relatório de segurança em texto.
    
    Args:
        df_crimes: DataFrame com dados de crimes
        df_operacoes: DataFrame com dados de operações policiais
        bairros_selecionados: Lista de bairros para incluir no relatório
        
    Returns:
        Relatório em formato texto
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
    
    # Análise por bairro usando o novo sistema
    if 'bairro' in df_crimes.columns:
        neighborhood_stats = _risk_map_generator._calculate_neighborhood_stats(df_crimes, df_operacoes)
        
        report_lines.append("🏘️ ANÁLISE DE RISCO POR BAIRRO")
        report_lines.append("-" * 30)
        
        # Ordenar por score de risco
        sorted_neighborhoods = sorted(
            neighborhood_stats.items(),
            key=lambda x: x[1]['score_risco'],
            reverse=True
        )
        
        for bairro_norm, stats in sorted_neighborhoods[:15]:
            if bairros_selecionados and stats['nome_original'] not in bairros_selecionados:
                continue
            
            nome = stats['nome_original']
            crimes = stats['total_crimes']
            operacoes = stats['total_operacoes']
            mortes = stats['mortes_confronto']
            nivel = stats['nivel_risco']
            score = stats['score_risco']
            
            report_lines.append(
                f"{nome}: {crimes} crimes, {operacoes} operações, "
                f"{mortes} mortes - {nivel} (Score: {score:.1f})"
            )
        
        report_lines.append("")
    
    # Recomendações gerais
    report_lines.append("💡 RECOMENDAÇÕES GERAIS")
    report_lines.append("-" * 30)
    
    if total_operacoes == 0:
        report_lines.append("• Implementar operações policiais preventivas")
    elif total_operacoes < total_crimes * 0.1:
        report_lines.append("• Aumentar frequência de operações policiais")
    
    report_lines.append("• Manter monitoramento contínuo dos indicadores")
    report_lines.append("• Implementar ações comunitárias de segurança")
    report_lines.append("• Focar recursos nos bairros de maior risco")
    report_lines.append("")
    
    # Informações técnicas
    report_lines.append("ℹ️ INFORMAÇÕES TÉCNICAS")
    report_lines.append("-" * 30)
    report_lines.append(f"Sistema: Alerta POA v2.0 - Módulo de Visualização Reescrito")
    report_lines.append(f"Método de análise: Score integrado de risco")
    report_lines.append(f"Fatores considerados: Crimes, operações policiais, mortes em confronto")
    report_lines.append("")
    
    report_lines.append("=" * 60)
    report_lines.append("Fim do relatório")
    report_lines.append("=" * 60)
    
    return "\n".join(report_lines)


def create_heatmap_data(df: pd.DataFrame, lat_col: Optional[str] = None, 
                       lon_col: Optional[str] = None) -> List[List[float]]:
    """Cria dados para mapa de calor.
    
    Args:
        df: DataFrame com dados de crimes
        lat_col: Nome da coluna de latitude
        lon_col: Nome da coluna de longitude
        
    Returns:
        Lista de coordenadas para o mapa de calor
    """
    heat_data = []
    
    if df.empty:
        return heat_data
    
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
    
    # Se não tiver coordenadas, usar coordenadas aproximadas dos bairros
    if not lat_col or not lon_col or lat_col not in df.columns or lon_col not in df.columns:
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
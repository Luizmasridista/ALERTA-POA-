"""Módulo de utilitários para mapeamento de nomes de bairros e funções de visualização.

Este módulo contém:
- Função de mapeamento de nomes de bairros
- Funções para determinação de cores no mapa
- Funções para determinação de níveis de risco
- Utilitários de visualização
"""

import streamlit as st
import pandas as pd
import folium
import json
import os
from folium.plugins import HeatMap


def map_bairro_name(bairro_name):
    """Mapeia nomes de bairros para corresponder aos nomes no GeoJSON.
    
    Args:
        bairro_name (str): Nome do bairro original
        
    Returns:
        str: Nome do bairro mapeado
    """
    if not bairro_name or pd.isna(bairro_name):
        return "Desconhecido"
    
    # Converter para string e normalizar
    bairro_name = str(bairro_name).strip().upper()
    
    # Mapeamento específico para corresponder ao GeoJSON
    mapping = {
        'CENTRO HISTÓRICO': 'CENTRO HISTÓRICO',
        'CENTRO HISTORICO': 'CENTRO HISTÓRICO',
        'CENTRO': 'CENTRO HISTÓRICO',
        'CIDADE BAIXA': 'CIDADE BAIXA',
        'FLORESTA': 'FLORESTA',
        'AZENHA': 'AZENHA',
        'PRAIA DE BELAS': 'PRAIA DE BELAS',
        'MENINO DEUS': 'MENINO DEUS',
        'SANTANA': 'SANTANA',
        'RIO BRANCO': 'RIO BRANCO',
        'BONFIM': 'BONFIM',
        'NAVEGANTES': 'NAVEGANTES',
        'HUMAITÁ': 'HUMAITÁ',
        'FARRAPOS': 'FARRAPOS',
        'SÃO GERALDO': 'SÃO GERALDO',
        'SÃO JOSÉ': 'VILA SÃO JOSÉ',
        'MARCÍLIO DIAS': 'MARCÍLIO DIAS',
        'AUXILIADORA': 'AUXILIADORA',
        'MOINHOS DE VENTO': 'MOINHOS DE VENTO',
        'MONT SERRAT': 'MONT SERRAT',
        'INDEPENDÊNCIA': 'INDEPENDÊNCIA',
        'HIGIENÓPOLIS': 'HIGIENÓPOLIS',
        'BOM FIM': 'BOM FIM',
        'JARDIM BOTÂNICO': 'JARDIM BOTÂNICO',
        'JARDIM BOTANICO': 'JARDIM BOTÂNICO',
        'RIO BRANCO': 'RIO BRANCO',
        'PETRÓPOLIS': 'PETRÓPOLIS',
        'PETROPOLIS': 'PETRÓPOLIS',
        'TRÊS FIGUEIRAS': 'TRÊS FIGUEIRAS',
        'TRES FIGUEIRAS': 'TRÊS FIGUEIRAS',
        'CHÁCARA DAS PEDRAS': 'CHÁCARA DAS PEDRAS',
        'CHACARA DAS PEDRAS': 'CHÁCARA DAS PEDRAS',
        'VILA MADALENA': 'VILA MADALENA',
        'BELA VISTA': 'BELA VISTA',
        'CAVALHADA': 'CAVALHADA',
        'CRISTAL': 'CRISTAL',
        'IPANEMA': 'IPANEMA',
        'NONOAI': 'NONOAI',
        'SERRARIA': 'SERRARIA',
        'VILA NOVA': 'VILA NOVA',
        'TERESÓPOLIS': 'TERESÓPOLIS',
        'TERESOPOLIS': 'TERESÓPOLIS',
        'PARTENON': 'PARTENON',
        'LOMBA DO PINHEIRO': 'LOMBA DO PINHEIRO',
        'RESTINGA': 'RESTINGA',
        'BELÉM NOVO': 'BELÉM NOVO',
        'BELEM NOVO': 'BELÉM NOVO',
        'BELÉM VELHO': 'BELÉM VELHO',
        'BELEM VELHO': 'BELÉM VELHO',
        'GLORIA': 'GLÓRIA',
        'GLÓRIA': 'GLÓRIA',
        'CRUZEIRO': 'CRUZEIRO',
        'SARANDI': 'SARANDI',
        'RUBEM BERTA': 'RUBEM BERTA',
        'ANCHIETA': 'ANCHIETA',
        'BOA VISTA': 'BOA VISTA',
        'MARIO QUINTANA': 'MÁRIO QUINTANA',
        'MÁRIO QUINTANA': 'MÁRIO QUINTANA',
        'PASSO DA AREIA': 'PASSO DA AREIA',
        'VILA IPIRANGA': 'VILA IPIRANGA',
        'JARDIM CARVALHO': 'JARDIM CARVALHO',
        'JARDIM LINDÓIA': 'JARDIM LINDÓIA',
        'JARDIM LINDOIA': 'JARDIM LINDÓIA',
        'JARDIM SÃO PEDRO': 'JARDIM SÃO PEDRO',
        'JARDIM SAO PEDRO': 'JARDIM SÃO PEDRO',
        'LAMI': 'LAMI',
        'ABERTA DOS MORROS': 'ABERTA DOS MORROS',
        'AGRONOMIA': 'AGRONOMIA',
        'ALTO PETRÓPOLIS': 'ALTO PETRÓPOLIS',
        'ALTO PETROPOLIS': 'ALTO PETRÓPOLIS',
        'ARQUIPÉLAGO': 'ARQUIPÉLAGO',
        'ARQUIPELAGO': 'ARQUIPÉLAGO',
        'ASSUNÇÃO': 'ASSUNÇÃO',
        'ASSUNCAO': 'ASSUNÇÃO',
        'CAMAQUÃ': 'CAMAQUÃ',
        'CAMAQUA': 'CAMAQUÃ',
        'CAMPO NOVO': 'CAMPO NOVO',
        'CAPELA': 'CAPELA',
        'CASCATA': 'CASCATA',
        'CORONEL APARÍCIO BORGES': 'CORONEL APARÍCIO BORGES',
        'CORONEL APARICIO BORGES': 'CORONEL APARÍCIO BORGES',
        'ESPÍRITO SANTO': 'ESPÍRITO SANTO',
        'ESPIRITO SANTO': 'ESPÍRITO SANTO',
        'EXTREMA': 'EXTREMA',
        'GUARUJÁ': 'GUARUJÁ',
        'GUARUJA': 'GUARUJÁ',
        'HÍPICA': 'HÍPICA',
        'HIPICA': 'HÍPICA',
        'ILHA DA PINTADA': 'ILHA DA PINTADA',
        'ILHA DAS FLORES': 'ILHA DAS FLORES',
        'ILHA DO PAVÃO': 'ILHA DO PAVÃO',
        'ILHA DO PAVAO': 'ILHA DO PAVÃO',
        'IPANEMA': 'IPANEMA',
        'JARDIM EUROPA': 'JARDIM EUROPA',
        'JARDIM FLORESTA': 'JARDIM FLORESTA',
        'JARDIM ÍPIS': 'JARDIM ÍPIS',
        'JARDIM IPIS': 'JARDIM ÍPIS',
        'JARDIM PLANALTO': 'JARDIM PLANALTO',
        'JARDIM SABARÁ': 'JARDIM SABARÁ',
        'JARDIM SABARA': 'JARDIM SABARÁ',
        'LAGEADO': 'LAGEADO',
        'MEDIANEIRA': 'MEDIANEIRA',
        'MORRO SANTANA': 'MORRO SANTANA',
        'PASSO DAS PEDRAS': 'PASSO DAS PEDRAS',
        'PEDRA REDONDA': 'PEDRA REDONDA',
        'PONTA GROSSA': 'PONTA GROSSA',
        'PROTÁSIO ALVES': 'PROTÁSIO ALVES',
        'PROTASIO ALVES': 'PROTÁSIO ALVES',
        'SANTA MARIA GORETTI': 'SANTA MARIA GORETTI',
        'SANTA TEREZA': 'SANTA TEREZA',
        'SANTA TERESA': 'SANTA TEREZA',
        'SANTO ANTÔNIO': 'SANTO ANTÔNIO',
        'SANTO ANTONIO': 'SANTO ANTÔNIO',
        'SÃO JOÃO': 'SÃO JOÃO',
        'SAO JOAO': 'SÃO JOÃO',
        'SAO JOSE': 'VILA SÃO JOSÉ',
        'SÃO SEBASTIÃO': 'SÃO SEBASTIÃO',
        'SAO SEBASTIAO': 'SÃO SEBASTIÃO',
        'SERAFINA CORRÊA': 'SERAFINA CORRÊA',
        'SERAFINA CORREA': 'SERAFINA CORRÊA',
        'TRISTEZA': 'TRISTEZA',
        'VILA ASSUNÇÃO': 'VILA ASSUNÇÃO',
        'VILA ASSUNCAO': 'VILA ASSUNÇÃO',
        'VILA CONCEIÇÃO': 'VILA CONCEIÇÃO',
        'VILA CONCEICAO': 'VILA CONCEIÇÃO',
        'VILA JARDIM': 'VILA JARDIM',
        'VILA JOÃO PESSOA': 'VILA JOÃO PESSOA',
        'VILA JOAO PESSOA': 'VILA JOÃO PESSOA'
    }
    
    return mapping.get(bairro_name, bairro_name)


def get_color_for_map_integrated(total_crimes, operacoes_policiais=0, mortes_confronto=0):
    """Determina cor para o mapa baseada em dados integrados incluindo mortes.
    
    Args:
        total_crimes (int): Número total de crimes
        operacoes_policiais (int): Número de operações policiais
        mortes_confronto (int): Número de mortes em confronto policial
        
    Returns:
        str: Código de cor hexadecimal
    """
    # Calcular score de risco integrado
    score_base = total_crimes
    
    # Penalidade por mortes em confronto (peso muito alto)
    if mortes_confronto > 0:
        score_base += mortes_confronto * 50  # Cada morte vale 50 crimes
    
    # Fator de redução baseado em operações policiais efetivas
    if operacoes_policiais > 0:
        efetividade = min(0.4, operacoes_policiais / max(1, total_crimes))  # Max 40% de redução
        score_base = score_base * (1 - efetividade)
    
    # Determinar cor baseada no score final
    if score_base >= 150:
        return '#4A0000'  # Vermelho muito escuro - Crítico
    elif score_base >= 100:
        return '#8B0000'  # Vermelho escuro - Muito Alto
    elif score_base >= 50:
        return '#FF0000'  # Vermelho - Alto
    elif score_base >= 25:
        return '#FF4500'  # Laranja vermelho - Médio-Alto
    elif score_base >= 10:
        return '#FFA500'  # Laranja - Médio
    elif score_base >= 5:
        return '#FFD700'  # Dourado - Baixo-Médio
    elif score_base >= 1:
        return '#FFFF00'  # Amarelo - Baixo
    else:
        return '#90EE90'  # Verde claro - Muito Baixo


def get_color_for_map_original(crime_count):
    """Determina cor para o mapa baseada apenas em contagem de crimes.
    
    Args:
        crime_count (int): Número de crimes
        
    Returns:
        str: Código de cor hexadecimal
    """
    if crime_count >= 100:
        return '#8B0000'  # Vermelho escuro - Muito Alto
    elif crime_count >= 50:
        return '#FF0000'  # Vermelho - Alto
    elif crime_count >= 25:
        return '#FF4500'  # Laranja vermelho - Médio-Alto
    elif crime_count >= 10:
        return '#FFA500'  # Laranja - Médio
    elif crime_count >= 5:
        return '#FFD700'  # Dourado - Baixo-Médio
    elif crime_count >= 1:
        return '#FFFF00'  # Amarelo - Baixo
    else:
        return '#90EE90'  # Verde claro - Muito Baixo


def get_risk_level_for_map_integrated(total_crimes, operacoes_policiais=0, mortes_confronto=0):
    """Determina nível de risco baseado em dados integrados incluindo mortes.
    
    Args:
        total_crimes (int): Número total de crimes
        operacoes_policiais (int): Número de operações policiais
        mortes_confronto (int): Número de mortes em confronto policial
        
    Returns:
        str: Nível de risco
    """
    # Calcular score de risco integrado
    score_base = total_crimes
    
    # Penalidade por mortes em confronto (peso muito alto)
    if mortes_confronto > 0:
        score_base += mortes_confronto * 50  # Cada morte vale 50 crimes
    
    # Fator de redução baseado em operações policiais efetivas
    if operacoes_policiais > 0:
        efetividade = min(0.4, operacoes_policiais / max(1, total_crimes))  # Max 40% de redução
        score_base = score_base * (1 - efetividade)
    
    # Determinar nível baseado no score final
    if score_base >= 150:
        return "⚫ Crítico"
    elif score_base >= 100:
        return "🔴 Muito Alto"
    elif score_base >= 50:
        return "🟠 Alto"
    elif score_base >= 25:
        return "🟡 Médio-Alto"
    elif score_base >= 10:
        return "🟡 Médio"
    elif score_base >= 5:
        return "🟢 Baixo-Médio"
    elif score_base >= 1:
        return "🟢 Baixo"
    else:
        return "🟢 Muito Baixo"


def get_risk_level_for_map_original(crime_count):
    """Determina nível de risco baseado apenas em contagem de crimes.
    
    Args:
        crime_count (int): Número de crimes
        
    Returns:
        str: Nível de risco
    """
    if crime_count >= 100:
        return "🔴 Muito Alto"
    elif crime_count >= 50:
        return "🟠 Alto"
    elif crime_count >= 25:
        return "🟡 Médio-Alto"
    elif crime_count >= 10:
        return "🟡 Médio"
    elif crime_count >= 5:
        return "🟢 Baixo-Médio"
    elif crime_count >= 1:
        return "🟢 Baixo"
    else:
        return "🟢 Muito Baixo"


def get_color_based_on_synergistic_analysis(analysis_data):
    """Determina cor baseada na análise sinérgica.
    
    Args:
        analysis_data (dict): Dados da análise sinérgica
        
    Returns:
        str: Código de cor hexadecimal
    """
    if not analysis_data:
        return '#90EE90'  # Verde claro para sem dados
    
    nivel_risco = analysis_data.get('nivel_risco', 'Baixo')
    
    color_map = {
        'Crítico': '#8B0000',      # Vermelho escuro
        'Muito Alto': '#FF0000',    # Vermelho
        'Alto': '#FF4500',          # Laranja vermelho
        'Médio-Alto': '#FFA500',    # Laranja
        'Médio': '#FFD700',         # Dourado
        'Baixo-Médio': '#FFFF00',   # Amarelo
        'Baixo': '#90EE90',         # Verde claro
        'Muito Baixo': '#00FF00'    # Verde
    }
    
    return color_map.get(nivel_risco, '#90EE90')
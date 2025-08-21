"""Módulo para carregamento e processamento de dados do sistema Alerta POA.

Este módulo contém todas as funções responsáveis por:
- Carregamento de dados de criminalidade
- Carregamento de dados de índice de segurança
- Carregamento de estatísticas dos bairros
- Carregamento de dados GeoJSON
- Carregamento de dados de bairros sem registros
"""

import streamlit as st
import pandas as pd
import json
import os
import glob


@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_data():
    """Carrega dados de criminalidade com cache.
    
    Tenta carregar dados integrados primeiro, depois fallback para dados originais.
    Padroniza nomes das colunas para compatibilidade.
    
    Returns:
        pd.DataFrame: DataFrame com dados de criminalidade processados
    """
    try:
        # Tentar carregar dados integrados primeiro
        if os.path.exists('data/dados_criminalidade_operacoes_integrado.csv'):
            df = pd.read_csv('data/dados_criminalidade_operacoes_integrado.csv')
        elif os.path.exists('data/dados_criminalidade_poa.csv'):
            df = pd.read_csv('data/dados_criminalidade_poa.csv')
        else:
            # Fallback para arquivos com timestamps se existirem
            arquivos_integrados = glob.glob('data/dados_criminalidade_operacoes_integrado_*.csv')
            if arquivos_integrados:
                arquivo_mais_recente = max(arquivos_integrados)
                df = pd.read_csv(arquivo_mais_recente)
            else:
                csv_files = glob.glob('data/dados_criminalidade_poa_*.csv')
                if not csv_files:
                    st.error("❌ Nenhum arquivo de dados encontrado no diretório data/")
                    return pd.DataFrame()
                csv_file = max(csv_files)
                df = pd.read_csv(csv_file)
        
        # Padronizar nomes das colunas para compatibilidade
        column_mapping = {
            'data_registro': 'Data Registro',
            'hora': 'Hora',
            'tipo_crime': 'tipo_crime',
            'bairro': 'bairro',
            'periodo_dia': 'periodo_dia',
            'municipio': 'Municipio',
            'ano': 'Ano',
            'dia_semana': 'Dia da Semana',
            'mes': 'Mes'
        }
        
        df = df.rename(columns=column_mapping)
        df['Data Registro'] = pd.to_datetime(df['Data Registro'])
        
        # Garantir que a coluna hora seja numérica
        if 'hora' in df.columns:
            df['hora'] = pd.to_numeric(df['hora'], errors='coerce')
        
        # Remover linhas com dados inválidos
        df = df.dropna(subset=['Data Registro'])
        
        return df
            
    except FileNotFoundError:
        st.error("❌ Arquivo de dados não encontrado.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_security_index_data():
    """Carrega dados de índice de segurança que incluem operações policiais.
    
    Returns:
        pd.DataFrame: DataFrame com dados de índice de segurança
    """
    try:
        # Tentar carregar arquivo principal primeiro
        if os.path.exists('data/indice_seguranca_bairros.csv'):
            df_seguranca = pd.read_csv('data/indice_seguranca_bairros.csv')
            return df_seguranca
        else:
            # Fallback para arquivos com timestamps se existirem
            arquivos_seguranca = glob.glob('data/indice_seguranca_bairros_*.csv')
            if arquivos_seguranca:
                arquivo_mais_recente = max(arquivos_seguranca)
                df_seguranca = pd.read_csv(arquivo_mais_recente)
                return df_seguranca
            else:
                return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados de índice de segurança: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_neighborhood_stats():
    """Carrega estatísticas dos bairros com cache.
    
    Primeiro tenta carregar dados de índice de segurança integrado,
    depois fallback para método original.
    
    Returns:
        dict: Dicionário com estatísticas dos bairros mapeadas
    """
    try:
        # Primeiro, tentar carregar dados de índice de segurança integrado
        df_seguranca = load_security_index_data()
        
        if not df_seguranca.empty:
            # Usar dados integrados com operações policiais
            mapped_stats = {}
            for _, row in df_seguranca.iterrows():
                bairro_nome = row['bairro']
                # Mapear nomes para corresponder ao GeoJSON
                from .mapping_utils import map_bairro_name
                mapped_name = map_bairro_name(bairro_nome)
                # Usar total_crimes como contagem base
                mapped_stats[mapped_name] = row['total_crimes']
            
            return mapped_stats
        
        # Fallback para método original se não houver dados integrados
        df = load_data()
        
        if df.empty:
            return {}
        
        # Usar a coluna 'bairro' que contém os bairros
        bairro_col = 'bairro'
        
        if bairro_col not in df.columns:
            return {}
        
        # Calcular estatísticas dos dados reais
        stats = df[bairro_col].value_counts().to_dict()
        
        # Criar mapeamento para nomes do GeoJSON
        mapped_stats = {}
        for bairro, count in stats.items():
            # Mapear nomes para corresponder ao GeoJSON
            from .mapping_utils import map_bairro_name
            mapped_name = map_bairro_name(bairro)
            if mapped_name in mapped_stats:
                mapped_stats[mapped_name] += count
            else:
                mapped_stats[mapped_name] = count
        
        return mapped_stats
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar estatísticas dos bairros: {str(e)}")
        return {}


@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_bairros_sem_dados():
    """Carrega informações dos bairros sem dados criminais com cache.
    
    Returns:
        dict: Dicionário com informações dos bairros sem dados
    """
    try:
        with open('relatorio_indicadores_criminais.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        bairros_sem_dados = {}
        for bairro in data.get('analise_bairros', []):
            nome = bairro['nome']
            status = bairro['status_seguranca']
            indicadores = bairro['indicadores_encontrados']
            observacao = bairro['observacao']
            
            bairros_sem_dados[nome] = {
                'status': status,
                'indicadores': indicadores,
                'observacao': observacao
            }
        
        return bairros_sem_dados
    except FileNotFoundError:
        return {}
    except Exception as e:
        st.warning(f"Erro ao carregar dados dos bairros sem dados: {e}")
        return {}


@st.cache_data(ttl=1800)  # Cache por 30 minutos
def load_geojson_data():
    """Carrega dados GeoJSON com cache.
    
    Returns:
        dict or None: Dados GeoJSON ou None se não encontrado
    """
    geojson_path = 'data/bairros_poa.geojson'
    if os.path.exists(geojson_path):
        with open(geojson_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None
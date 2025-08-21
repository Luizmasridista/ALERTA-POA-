#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação dos Dados de Criminalidade com Fontes de Notícias

Este script valida os dados gerados pelo modelo de distribuição de crimes
com informações obtidas de notícias e fontes oficiais.

Autor: Sistema de Análise de Criminalidade
Data: 2025-01-21
"""

import pandas as pd
import json
from datetime import datetime
import os

def load_integrated_data():
    """
    Carrega os dados integrados de criminalidade.
    """
    try:
        df = pd.read_csv('integrated_crime_data.csv')
        print(f"✅ Dados integrados carregados: {len(df)} registros")
        return df
    except FileNotFoundError:
        print("❌ Arquivo de dados integrados não encontrado")
        return None

def validate_centro_historico(df):
    """
    Valida dados do Centro Histórico com informações das notícias.
    
    Dados das notícias (1º semestre 2024):
    - Centro Histórico: 2.266 ocorrências (1.572 furtos + 645 roubos + 49 outros)
    - Redução de 26% nos furtos vs 2023
    - Redução de 66% nos roubos de veículos vs 2023
    - Redução de 49% nos demais roubos vs 2023
    """
    print("\n🔍 VALIDAÇÃO - CENTRO HISTÓRICO")
    print("=" * 50)
    
    centro_data = df[df['bairro'].str.contains('Centro', case=False, na=False)]
    
    if centro_data.empty:
        print("❌ Dados do Centro Histórico não encontrados")
        return
    
    # Análise por período (1º semestre 2024)
    centro_2024 = centro_data[centro_data['data'].str.contains('2024', na=False)]
    
    print(f"📊 Registros do Centro Histórico em 2024: {len(centro_2024)}")
    
    if not centro_2024.empty:
        # Análise por tipo de crime
        crimes_centro = centro_2024['tipo_crime'].value_counts()
        print("\n📈 Distribuição por tipo de crime:")
        for crime, count in crimes_centro.head(10).items():
            print(f"   • {crime}: {count} casos")
        
        # Comparação com dados das notícias
        furtos = centro_2024[centro_2024['tipo_crime'].str.contains('Furto', case=False, na=False)]
        roubos = centro_2024[centro_2024['tipo_crime'].str.contains('Roubo', case=False, na=False)]
        
        print(f"\n🔍 Comparação com dados oficiais (1º sem. 2024):")
        print(f"   • Furtos modelo: {len(furtos)} vs Oficial: 1.572")
        print(f"   • Roubos modelo: {len(roubos)} vs Oficial: 645")
        print(f"   • Total modelo: {len(centro_2024)} vs Oficial: 2.266")
        
        # Cálculo de precisão
        if len(centro_2024) > 0:
            precisao = min(len(centro_2024) / 2266, 2266 / len(centro_2024)) * 100
            print(f"   • Precisão estimada: {precisao:.1f}%")
    
    return centro_data

def validate_top_neighborhoods(df):
    """
    Valida os bairros com mais crimes segundo as notícias.
    
    Top 10 bairros com mais roubos a pedestres (1º sem. 2023):
    1. Centro Histórico: 948 casos
    2. Rubem Berta: 310 casos
    3. Sarandi: casos não especificados
    4. Cidade Baixa: 214 casos (aumento de 24,4%)
    5. Restinga: 129 casos
    """
    print("\n🔍 VALIDAÇÃO - TOP BAIRROS VIOLENTOS")
    print("=" * 50)
    
    # Análise dos bairros mais mencionados nas notícias
    bairros_validacao = {
        'Centro Histórico': {'roubos_pedestres_2023': 948, 'furtos_2024_sem1': 1572},
        'Rubem Berta': {'roubos_pedestres_2023': 310},
        'Cidade Baixa': {'roubos_pedestres_2023': 214},
        'Restinga': {'roubos_pedestres_2023': 129, 'homicidios_2017': 45},
        'Vila Jardim': {'homicidios_2016': 34, 'homicidios_2017': 10},
        'Praia de Belas': {'total_ocorrencias_2024_sem1': 558}
    }
    
    print("📊 Comparação modelo vs dados oficiais:")
    
    for bairro, dados_oficiais in bairros_validacao.items():
        bairro_data = df[df['bairro'].str.contains(bairro, case=False, na=False)]
        
        if not bairro_data.empty:
            total_modelo = len(bairro_data)
            print(f"\n🏘️  {bairro}:")
            print(f"   • Total modelo: {total_modelo} registros")
            
            # Análise por tipo de crime se disponível
            crimes = bairro_data['tipo_crime'].value_counts()
            for crime, count in crimes.head(3).items():
                print(f"   • {crime}: {count} casos")
            
            # Comparação com dados oficiais
            for tipo, valor in dados_oficiais.items():
                print(f"   • {tipo.replace('_', ' ').title()}: {valor} (oficial)")
        else:
            print(f"\n❌ {bairro}: Não encontrado no modelo")

def validate_crime_trends(df):
    """
    Valida tendências de criminalidade mencionadas nas notícias.
    """
    print("\n🔍 VALIDAÇÃO - TENDÊNCIAS DE CRIMINALIDADE")
    print("=" * 50)
    
    # Análise temporal
    if 'data' in df.columns:
        df['ano'] = pd.to_datetime(df['data'], errors='coerce').dt.year
        crimes_por_ano = df.groupby('ano').size()
        
        print("📈 Evolução temporal dos crimes:")
        for ano, total in crimes_por_ano.items():
            if pd.notna(ano):
                print(f"   • {int(ano)}: {total} registros")
    
    # Análise por zona geográfica
    if 'zona' in df.columns:
        crimes_por_zona = df['zona'].value_counts()
        print("\n🗺️  Distribuição por zona:")
        for zona, total in crimes_por_zona.items():
            percentual = (total / len(df)) * 100
            print(f"   • {zona}: {total} registros ({percentual:.1f}%)")
    
    # Tipos de crime mais comuns
    crimes_comuns = df['tipo_crime'].value_counts().head(10)
    print("\n🎯 Top 10 tipos de crime:")
    for i, (crime, total) in enumerate(crimes_comuns.items(), 1):
        percentual = (total / len(df)) * 100
        print(f"   {i:2d}. {crime}: {total} casos ({percentual:.1f}%)")

def generate_validation_report(df):
    """
    Gera relatório de validação completo.
    """
    print("\n📋 RELATÓRIO DE VALIDAÇÃO")
    print("=" * 60)
    
    # Estatísticas gerais
    print(f"📊 Total de registros analisados: {len(df):,}")
    print(f"📍 Bairros únicos: {df['bairro'].nunique()}")
    print(f"🚨 Tipos de crime únicos: {df['tipo_crime'].nunique()}")
    
    # Período de dados
    if 'data' in df.columns:
        datas_validas = pd.to_datetime(df['data'], errors='coerce').dropna()
        if not datas_validas.empty:
            print(f"📅 Período: {datas_validas.min().strftime('%Y-%m-%d')} a {datas_validas.max().strftime('%Y-%m-%d')}")
    
    # Qualidade dos dados
    print("\n🔍 Qualidade dos dados:")
    print(f"   • Registros com bairro: {df['bairro'].notna().sum():,} ({(df['bairro'].notna().sum()/len(df)*100):.1f}%)")
    print(f"   • Registros com tipo de crime: {df['tipo_crime'].notna().sum():,} ({(df['tipo_crime'].notna().sum()/len(df)*100):.1f}%)")
    
    if 'fonte' in df.columns:
        fontes = df['fonte'].value_counts()
        print("\n📚 Distribuição por fonte:")
        for fonte, total in fontes.items():
            percentual = (total / len(df)) * 100
            print(f"   • {fonte}: {total:,} registros ({percentual:.1f}%)")
    
    # Limitações identificadas
    print("\n⚠️  LIMITAÇÕES IDENTIFICADAS:")
    print("   • Dados do modelo são estimativas baseadas em pesquisa de 2016-2017")
    print("   • Distribuição por bairros pode não refletir realidade atual")
    print("   • Necessária validação contínua com dados oficiais")
    print("   • Alguns bairros podem ter sub ou super-representação")
    
    # Recomendações
    print("\n💡 RECOMENDAÇÕES:")
    print("   • Atualizar modelo com dados mais recentes quando disponíveis")
    print("   • Implementar sistema de validação automática")
    print("   • Coletar feedback de usuários sobre precisão")
    print("   • Monitorar tendências e ajustar pesos do modelo")
    
    return {
        'total_registros': len(df),
        'bairros_unicos': df['bairro'].nunique(),
        'tipos_crime_unicos': df['tipo_crime'].nunique(),
        'qualidade_bairro': (df['bairro'].notna().sum()/len(df)*100),
        'qualidade_crime': (df['tipo_crime'].notna().sum()/len(df)*100)
    }

def save_validation_results(validation_data):
    """
    Salva resultados da validação.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Salvar metadados da validação
    validation_metadata = {
        'timestamp': timestamp,
        'validation_date': datetime.now().isoformat(),
        'data_sources': [
            'GauchaZH - Centro Histórico furtos 2024',
            'GauchaZH - Roubos a pedestres 2023',
            'GauchaZH - Bairros violentos 2017-2018',
            'Veja - Ranking bairros inseguros',
            'SSP-RS - Indicadores criminais'
        ],
        'validation_metrics': validation_data,
        'notes': [
            'Validação baseada em notícias e dados oficiais parciais',
            'Modelo usa estimativas da pesquisa UFRGS 2016-2017',
            'Necessária atualização contínua com dados oficiais'
        ]
    }
    
    with open(f'validation_results_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(validation_metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados da validação salvos em: validation_results_{timestamp}.json")

def main():
    """
    Função principal de validação.
    """
    print("🔍 INICIANDO VALIDAÇÃO DOS DADOS DE CRIMINALIDADE")
    print("=" * 60)
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Carregar dados
    df = load_integrated_data()
    if df is None:
        return
    
    # Executar validações
    validate_centro_historico(df)
    validate_top_neighborhoods(df)
    validate_crime_trends(df)
    
    # Gerar relatório
    validation_data = generate_validation_report(df)
    
    # Salvar resultados
    save_validation_results(validation_data)
    
    print("\n✅ Validação concluída com sucesso!")
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("   1. Analisar discrepâncias identificadas")
    print("   2. Ajustar pesos do modelo se necessário")
    print("   3. Coletar mais dados oficiais para validação")
    print("   4. Implementar monitoramento contínuo")
    print("   5. Documentar limitações para usuários")

if __name__ == "__main__":
    main()
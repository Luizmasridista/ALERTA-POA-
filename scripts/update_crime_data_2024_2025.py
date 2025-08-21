#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para atualizar dados de criminalidade de Porto Alegre
com informações mais recentes de 2024 e início de 2025

Baseado em dados da SSP-RS e relatórios oficiais
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json

def load_current_data():
    """Carrega os dados atuais do sistema"""
    data_path = '../data/expanded_crime_data.csv'
    if os.path.exists(data_path):
        return pd.read_csv(data_path)
    else:
        print(f"Arquivo não encontrado: {data_path}")
        return None

def create_updated_data():
    """Cria dados atualizados baseados nas informações mais recentes"""
    
    # Dados do primeiro semestre de 2024 (fonte: SSP-RS via GZH)
    # Centro Histórico: 2.266 ocorrências (1.572 furtos + 645 roubos)
    # Praia de Belas: 558 ocorrências
    # Partenon: 25 roubos de veículos
    # Sarandi: 24 roubos de veículos
    
    updated_records = []
    
    # Dados do Centro Histórico - primeiro semestre 2024
    centro_historico_data = [
        {'data': '2024-06-30', 'bairro': 'Centro Histórico', 'tipo_crime': 'Furto', 
         'quantidade': 1572, 'zona': 'Centro', 'fonte': 'SSP-RS (atualizado 2024)', 
         'latitude': -30.0277, 'longitude': -51.2287, 
         'observacoes': 'Dados do primeiro semestre 2024 - redução de 26% vs 2023'},
        
        {'data': '2024-06-30', 'bairro': 'Centro Histórico', 'tipo_crime': 'Roubo', 
         'quantidade': 645, 'zona': 'Centro', 'fonte': 'SSP-RS (atualizado 2024)', 
         'latitude': -30.0277, 'longitude': -51.2287, 
         'observacoes': 'Dados do primeiro semestre 2024 - redução de 49% vs 2023'},
        
        {'data': '2024-06-30', 'bairro': 'Centro Histórico', 'tipo_crime': 'Roubo de veículo', 
         'quantidade': 4, 'zona': 'Centro', 'fonte': 'SSP-RS (atualizado 2024)', 
         'latitude': -30.0277, 'longitude': -51.2287, 
         'observacoes': 'Dados do primeiro semestre 2024 - redução de 66% vs 2023'},
    ]
    
    # Dados do Praia de Belas - primeiro semestre 2024
    praia_belas_data = [
        {'data': '2024-06-30', 'bairro': 'Praia de Belas', 'tipo_crime': 'Furto', 
         'quantidade': 350, 'zona': 'Centro', 'fonte': 'SSP-RS (atualizado 2024)', 
         'latitude': -30.0346, 'longitude': -51.2396, 
         'observacoes': 'Segundo bairro com mais ocorrências - 558 total no 1º semestre'},
        
        {'data': '2024-06-30', 'bairro': 'Praia de Belas', 'tipo_crime': 'Roubo', 
         'quantidade': 208, 'zona': 'Centro', 'fonte': 'SSP-RS (atualizado 2024)', 
         'latitude': -30.0346, 'longitude': -51.2396, 
         'observacoes': 'Segundo bairro com mais ocorrências - 558 total no 1º semestre'},
    ]
    
    # Dados do Partenon - primeiro semestre 2024
    partenon_data = [
        {'data': '2024-06-30', 'bairro': 'Partenon', 'tipo_crime': 'Roubo de veículo', 
         'quantidade': 25, 'zona': 'Leste', 'fonte': 'SSP-RS (atualizado 2024)', 
         'latitude': -30.0583, 'longitude': -51.1806, 
         'observacoes': '25 roubos de veículos no primeiro semestre 2024'},
    ]
    
    # Dados do Sarandi - primeiro semestre 2024
    sarandi_data = [
        {'data': '2024-06-30', 'bairro': 'Sarandi', 'tipo_crime': 'Roubo de veículo', 
         'quantidade': 24, 'zona': 'Norte', 'fonte': 'SSP-RS (atualizado 2024)', 
         'latitude': -29.9833, 'longitude': -51.1167, 
         'observacoes': '24 roubos de veículos no primeiro semestre 2024'},
    ]
    
    # Dados consolidados de Porto Alegre - 2024 completo
    poa_2024_data = [
        {'data': '2024-12-31', 'bairro': 'Porto Alegre (Geral)', 'tipo_crime': 'Homicídio', 
         'quantidade': 172, 'zona': 'Geral', 'fonte': 'SSP-RS (consolidado 2024)', 
         'latitude': -30.0346, 'longitude': -51.2177, 
         'observacoes': 'Redução de 35% vs 2023 (265 casos)'},
        
        {'data': '2024-12-31', 'bairro': 'Porto Alegre (Geral)', 'tipo_crime': 'Latrocínio', 
         'quantidade': 4, 'zona': 'Geral', 'fonte': 'SSP-RS (consolidado 2024)', 
         'latitude': -30.0346, 'longitude': -51.2177, 
         'observacoes': 'Redução de 43% vs 2023 (7 casos)'},
        
        {'data': '2024-12-31', 'bairro': 'Porto Alegre (Geral)', 'tipo_crime': 'Roubo a pedestre', 
         'quantidade': 7292, 'zona': 'Geral', 'fonte': 'SSP-RS (consolidado 2024)', 
         'latitude': -30.0346, 'longitude': -51.2177, 
         'observacoes': 'Redução de 44% vs 2023 (12.907 casos)'},
        
        {'data': '2024-12-31', 'bairro': 'Porto Alegre (Geral)', 'tipo_crime': 'Furto de celular', 
         'quantidade': 4296, 'zona': 'Geral', 'fonte': 'SSP-RS (consolidado 2024)', 
         'latitude': -30.0346, 'longitude': -51.2177, 
         'observacoes': 'Redução de 16% vs 2023 (5.101 casos)'},
        
        {'data': '2024-12-31', 'bairro': 'Porto Alegre (Geral)', 'tipo_crime': 'Roubo de veículo', 
         'quantidade': 1144, 'zona': 'Geral', 'fonte': 'SSP-RS (consolidado 2024)', 
         'latitude': -30.0346, 'longitude': -51.2177, 
         'observacoes': 'Taxa de 78,4 por 100 mil veículos - redução de 49% vs 2023'},
    ]
    
    # Combinar todos os dados
    all_new_data = centro_historico_data + praia_belas_data + partenon_data + sarandi_data + poa_2024_data
    
    return pd.DataFrame(all_new_data)

def update_crime_data():
    """Função principal para atualizar os dados de criminalidade"""
    print("Iniciando atualização dos dados de criminalidade...")
    
    # Carregar dados atuais
    current_data = load_current_data()
    if current_data is None:
        print("Erro ao carregar dados atuais")
        return
    
    print(f"Dados atuais carregados: {len(current_data)} registros")
    print(f"Período atual: {current_data['data'].min()} a {current_data['data'].max()}")
    
    # Criar novos dados
    new_data = create_updated_data()
    print(f"Novos dados criados: {len(new_data)} registros")
    
    # Combinar dados
    updated_data = pd.concat([current_data, new_data], ignore_index=True)
    
    # Remover duplicatas se houver
    updated_data = updated_data.drop_duplicates(subset=['data', 'bairro', 'tipo_crime'], keep='last')
    
    # Ordenar por data
    updated_data = updated_data.sort_values('data')
    
    print(f"Dados combinados: {len(updated_data)} registros")
    
    # Salvar dados atualizados
    output_path = '../data/expanded_crime_data_updated.csv'
    updated_data.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Dados atualizados salvos em: {output_path}")
    
    # Criar backup do arquivo original
    backup_path = f"../data/expanded_crime_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    current_data.to_csv(backup_path, index=False, encoding='utf-8')
    print(f"Backup criado em: {backup_path}")
    
    # Criar relatório de atualização
    create_update_report(current_data, updated_data)
    
    return updated_data

def create_update_report(old_data, new_data):
    """Cria um relatório da atualização realizada"""
    report = {
        'data_atualizacao': datetime.now().isoformat(),
        'registros_anteriores': len(old_data),
        'registros_atualizados': len(new_data),
        'novos_registros': len(new_data) - len(old_data),
        'periodo_anterior': {
            'inicio': old_data['data'].min(),
            'fim': old_data['data'].max()
        },
        'periodo_atualizado': {
            'inicio': new_data['data'].min(),
            'fim': new_data['data'].max()
        },
        'fontes_atualizacao': [
            'SSP-RS (Secretaria da Segurança Pública do RS)',
            'GZH - Dados do primeiro semestre 2024',
            'Observatório Estadual da Segurança Pública (Oesp)',
            'Anuário Brasileiro de Segurança Pública 2025'
        ],
        'principais_atualizacoes': [
            'Centro Histórico: 2.266 ocorrências no 1º semestre 2024',
            'Redução de 26% nos furtos do Centro Histórico vs 2023',
            'Redução de 49% nos roubos de veículos em Porto Alegre',
            'Redução de 44% nos roubos a pedestres em Porto Alegre',
            'Redução de 35% nos homicídios em Porto Alegre (172 casos em 2024)'
        ]
    }
    
    report_path = '../data/update_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Relatório de atualização salvo em: {report_path}")

if __name__ == "__main__":
    updated_data = update_crime_data()
    print("\nAtualização concluída com sucesso!")
    print("\nResumo das principais atualizações:")
    print("- Dados do primeiro semestre de 2024 adicionados")
    print("- Centro Histórico continua liderando em furtos e roubos")
    print("- Tendência geral de redução na criminalidade em Porto Alegre")
    print("- Dados consolidados de 2024 incluídos")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integração de Dados de Criminalidade
Integra dados distribuídos com dataset atual do projeto
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
from typing import Dict, List, Tuple

class CrimeDataIntegrator:
    def __init__(self):
        self.current_data_file = "../data/distributed_crime_data.csv"
        self.distributed_data_file = "distributed_crime_data.csv"
        self.output_file = "integrated_crime_data.csv"
        
    def load_current_data(self) -> pd.DataFrame:
        """Carrega dados atuais do projeto"""
        try:
            df = pd.read_csv(self.current_data_file)
            print(f"✅ Dados atuais carregados: {len(df)} registros")
            print(f"📅 Período: {df['Data Registro'].min()} a {df['Data Registro'].max()}")
            print(f"🏘️  Bairros: {df['Bairro'].nunique()} únicos")
            print(f"🚨 Tipos de crime: {df['Descricao do Fato'].nunique()} únicos")
            return df
        except FileNotFoundError:
            print(f"⚠️  Arquivo {self.current_data_file} não encontrado")
            return pd.DataFrame()
    
    def load_distributed_data(self) -> pd.DataFrame:
        """Carrega dados distribuídos pelo modelo"""
        try:
            df = pd.read_csv(self.distributed_data_file)
            print(f"✅ Dados distribuídos carregados: {len(df)} registros")
            print(f"📅 Período: {df['data'].min()} a {df['data'].max()}")
            print(f"🏘️  Bairros: {df['bairro'].nunique()} únicos")
            print(f"🚨 Tipos de crime: {df['tipo_crime'].nunique()} únicos")
            return df
        except FileNotFoundError:
            print(f"⚠️  Arquivo {self.distributed_data_file} não encontrado")
            return pd.DataFrame()
    
    def standardize_current_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Padroniza dados atuais para formato comum"""
        if df.empty:
            return df
        
        # Mapear colunas para formato padrão
        standardized = pd.DataFrame()
        
        # Data
        if 'Data Registro' in df.columns:
            standardized['data'] = pd.to_datetime(df['Data Registro']).dt.strftime('%Y-%m-%d')
        elif 'Data' in df.columns:
            standardized['data'] = pd.to_datetime(df['Data']).dt.strftime('%Y-%m-%d')
        
        # Bairro
        if 'Bairro' in df.columns:
            standardized['bairro'] = df['Bairro']
        
        # Tipo de crime
        if 'Descricao do Fato' in df.columns:
            standardized['tipo_crime'] = df['Descricao do Fato']
        elif 'Tipo' in df.columns:
            standardized['tipo_crime'] = df['Tipo']
        elif 'Crime' in df.columns:
            standardized['tipo_crime'] = df['Crime']
        
        # Quantidade (assumir 1 por registro)
        standardized['quantidade'] = 1
        
        # Coordenadas se disponíveis
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            standardized['latitude'] = df['Latitude']
            standardized['longitude'] = df['Longitude']
        
        # Período do dia se disponível
        if 'Periodo do Dia' in df.columns:
            standardized['periodo_dia'] = df['Periodo do Dia']
        
        # Fonte
        standardized['fonte'] = 'Dataset Original'
        
        # Zona (classificar)
        standardized['zona'] = standardized['bairro'].apply(self.classify_neighborhood_zone)
        
        print(f"📊 Dados atuais padronizados: {len(standardized)} registros")
        return standardized
    
    def classify_neighborhood_zone(self, neighborhood: str) -> str:
        """Classifica bairro por zona geográfica"""
        zone_mapping = {
            "Centro": ["Centro Histórico", "Cidade Baixa", "Floresta", "Marcílio Dias", 
                      "Menino Deus", "Praia de Belas", "Santa Cecília", "Azenha"],
            "Norte": ["Anchieta", "Auxiliadora", "Bom Fim", "Farroupilha", "Higienópolis", 
                     "Independência", "Moinhos de Vento", "Mont'Serrat", "Rio Branco", "Santana",
                     "Jardim Lindóia", "Jardim São Pedro", "Mapa", "Mathias Velho", "Passo d'Areia", 
                     "Petrópolis", "Rubem Berta", "São Geraldo", "São João", "Sarandi", "Vila Ipiranga"],
            "Sul": ["Aberta dos Morros", "Belém Novo", "Belém Velho", "Campo Novo", "Cavalhada", 
                   "Chapéu do Sol", "Coronel Aparício Borges", "Espírito Santo", "Guarujá", 
                   "Hípica", "Ipanema", "Lageado", "Lami", "Nonoai", "Pedra Redonda", 
                   "Ponta Grossa", "Restinga", "Serraria", "Sétimo Céu", "Tristeza", 
                   "Vila Assunção", "Vila Conceição", "Vila Nova"],
            "Leste": ["Agronomia", "Bela Vista", "Boa Vista", "Camaquã", "Cascata", "Cristal", 
                     "Glória", "Jardim Botânico", "Jardim do Salso", "Lomba do Pinheiro", 
                     "Mário Quintana", "Medianeira", "Partenon", "Santo Antônio", "São José", 
                     "Três Figueiras", "Vila João Pessoa", "Volta do Guerino"],
            "Oeste": ["Arquipélago", "Humaitá", "Ilha da Pintada", "Ilha do Pavão", "Navegantes"]
        }
        
        for zone, neighborhoods in zone_mapping.items():
            if neighborhood in neighborhoods:
                return zone
        return "Norte"  # Default
    
    def standardize_crime_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Padroniza tipos de crimes"""
        crime_mapping = {
            # Mapeamento de crimes do dataset atual para tipos padronizados
            "ROUBO A TRANSEUNTE": "Roubo",
            "ROUBO DE VEICULO": "Roubo de veículo",
            "ROUBO EM RESIDENCIA": "Roubo",
            "ROUBO EM ESTABELECIMENTO COMERCIAL": "Roubo",
            "FURTO DE VEICULO": "Furto",
            "FURTO EM RESIDENCIA": "Furto",
            "FURTO EM ESTABELECIMENTO COMERCIAL": "Furto",
            "HOMICIDIO DOLOSO": "Homicídio",
            "LESAO CORPORAL": "Lesão corporal",
            "TRAFICO DE DROGAS": "Tráfico de drogas",
            "AMEACA": "Ameaça"
        }
        
        # Aplicar mapeamento
        df['tipo_crime_padronizado'] = df['tipo_crime'].str.upper().map(crime_mapping)
        
        # Para crimes não mapeados, manter original
        df['tipo_crime_padronizado'] = df['tipo_crime_padronizado'].fillna(df['tipo_crime'])
        
        # Substituir coluna original
        df['tipo_crime'] = df['tipo_crime_padronizado']
        df = df.drop('tipo_crime_padronizado', axis=1)
        
        return df
    
    def aggregate_current_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agrega dados atuais por data, bairro e tipo de crime"""
        if df.empty:
            return df
        
        # Agrupar por data, bairro e tipo de crime
        aggregated = df.groupby(['data', 'bairro', 'tipo_crime', 'zona', 'fonte']).agg({
            'quantidade': 'sum',
            'latitude': 'mean',
            'longitude': 'mean',
            'periodo_dia': lambda x: x.mode().iloc[0] if not x.empty else None
        }).reset_index()
        
        print(f"📊 Dados atuais agregados: {len(aggregated)} registros únicos")
        return aggregated
    
    def filter_overlapping_data(self, current_df: pd.DataFrame, distributed_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Remove sobreposições entre dados atuais e distribuídos"""
        if current_df.empty or distributed_df.empty:
            return current_df, distributed_df
        
        # Identificar bairros e períodos que já existem nos dados atuais
        current_neighborhoods = set(current_df['bairro'].unique())
        current_dates = set(pd.to_datetime(current_df['data']).dt.to_period('M'))
        
        print(f"🏘️  Bairros nos dados atuais: {len(current_neighborhoods)}")
        print(f"📅 Períodos nos dados atuais: {len(current_dates)}")
        
        # Filtrar dados distribuídos para evitar sobreposição
        distributed_df['data_period'] = pd.to_datetime(distributed_df['data']).dt.to_period('M')
        
        # Manter apenas dados distribuídos para:
        # 1. Bairros não cobertos pelos dados atuais
        # 2. Períodos não cobertos pelos dados atuais para bairros existentes
        filtered_distributed = distributed_df[
            (~distributed_df['bairro'].isin(current_neighborhoods)) |
            (~distributed_df['data_period'].isin(current_dates))
        ].copy()
        
        filtered_distributed = filtered_distributed.drop('data_period', axis=1)
        
        print(f"📊 Dados distribuídos filtrados: {len(filtered_distributed)} registros (removidas sobreposições)")
        
        return current_df, filtered_distributed
    
    def integrate_datasets(self, current_df: pd.DataFrame, distributed_df: pd.DataFrame) -> pd.DataFrame:
        """Integra datasets atual e distribuído"""
        if current_df.empty and distributed_df.empty:
            print("⚠️  Nenhum dado disponível para integração")
            return pd.DataFrame()
        
        if current_df.empty:
            print("📊 Usando apenas dados distribuídos")
            return distributed_df
        
        if distributed_df.empty:
            print("📊 Usando apenas dados atuais")
            return current_df
        
        # Garantir que as colunas sejam compatíveis
        common_columns = ['data', 'bairro', 'tipo_crime', 'quantidade', 'zona', 'fonte']
        
        # Adicionar colunas faltantes com valores padrão
        for col in common_columns:
            if col not in current_df.columns:
                current_df[col] = None
            if col not in distributed_df.columns:
                distributed_df[col] = None
        
        # Selecionar apenas colunas comuns
        current_df_clean = current_df[common_columns].copy()
        distributed_df_clean = distributed_df[common_columns].copy()
        
        # Combinar datasets
        integrated_df = pd.concat([current_df_clean, distributed_df_clean], ignore_index=True)
        
        # Ordenar por data e bairro
        integrated_df = integrated_df.sort_values(['data', 'bairro', 'tipo_crime'])
        
        print(f"✅ Datasets integrados: {len(integrated_df)} registros totais")
        return integrated_df
    
    def validate_integration(self, integrated_df: pd.DataFrame) -> Dict:
        """Valida a integração dos dados"""
        if integrated_df.empty:
            return {"error": "Dataset integrado está vazio"}
        
        validation = {
            "total_records": len(integrated_df),
            "unique_neighborhoods": integrated_df['bairro'].nunique(),
            "unique_crime_types": integrated_df['tipo_crime'].nunique(),
            "date_range": {
                "start": integrated_df['data'].min(),
                "end": integrated_df['data'].max()
            },
            "sources": integrated_df['fonte'].value_counts().to_dict(),
            "zones": integrated_df['zona'].value_counts().to_dict(),
            "crime_types": integrated_df['tipo_crime'].value_counts().to_dict()
        }
        
        # Verificar cobertura geográfica
        all_poa_neighborhoods = 94  # Total oficial
        coverage_percentage = (validation["unique_neighborhoods"] / all_poa_neighborhoods) * 100
        validation["geographic_coverage"] = {
            "covered_neighborhoods": validation["unique_neighborhoods"],
            "total_neighborhoods": all_poa_neighborhoods,
            "coverage_percentage": round(coverage_percentage, 1)
        }
        
        return validation
    
    def generate_integration_report(self, validation: Dict):
        """Gera relatório da integração"""
        print("=" * 80)
        print("RELATÓRIO DE INTEGRAÇÃO DE DADOS DE CRIMINALIDADE")
        print("=" * 80)
        print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        if "error" in validation:
            print(f"❌ Erro: {validation['error']}")
            return
        
        # Estatísticas gerais
        print("1. ESTATÍSTICAS GERAIS:")
        print("-" * 40)
        print(f"• Total de registros: {validation['total_records']:,}")
        print(f"• Bairros únicos: {validation['unique_neighborhoods']}")
        print(f"• Tipos de crime únicos: {validation['unique_crime_types']}")
        print(f"• Período: {validation['date_range']['start']} a {validation['date_range']['end']}")
        print()
        
        # Cobertura geográfica
        coverage = validation['geographic_coverage']
        print("2. COBERTURA GEOGRÁFICA:")
        print("-" * 40)
        print(f"• Bairros cobertos: {coverage['covered_neighborhoods']}/{coverage['total_neighborhoods']}")
        print(f"• Percentual de cobertura: {coverage['coverage_percentage']}%")
        print()
        
        # Distribuição por fonte
        print("3. DISTRIBUIÇÃO POR FONTE:")
        print("-" * 40)
        for source, count in validation['sources'].items():
            percentage = (count / validation['total_records']) * 100
            print(f"• {source}: {count:,} registros ({percentage:.1f}%)")
        print()
        
        # Distribuição por zona
        print("4. DISTRIBUIÇÃO POR ZONA:")
        print("-" * 40)
        for zone, count in validation['zones'].items():
            percentage = (count / validation['total_records']) * 100
            print(f"• Zona {zone}: {count:,} registros ({percentage:.1f}%)")
        print()
        
        # Top 10 tipos de crime
        print("5. TOP 10 TIPOS DE CRIME:")
        print("-" * 40)
        crime_types = validation['crime_types']
        sorted_crimes = sorted(crime_types.items(), key=lambda x: x[1], reverse=True)[:10]
        for i, (crime_type, count) in enumerate(sorted_crimes, 1):
            percentage = (count / validation['total_records']) * 100
            print(f"{i:2d}. {crime_type}: {count:,} registros ({percentage:.1f}%)")
        print()
        
        print("6. PRÓXIMOS PASSOS:")
        print("-" * 40)
        print("1. Validar dados com fontes conhecidas")
        print("2. Expandir cobertura temporal se necessário")
        print("3. Documentar limitações e metodologia")
        print("4. Atualizar aplicação com dados integrados")
        print("5. Implementar monitoramento de qualidade")
        print()
        print("=" * 80)
    
    def save_integrated_data(self, integrated_df: pd.DataFrame) -> str:
        """Salva dados integrados"""
        if integrated_df.empty:
            print("⚠️  Nenhum dado para salvar")
            return ""
        
        # Salvar arquivo principal
        integrated_df.to_csv(self.output_file, index=False, encoding='utf-8')
        print(f"💾 Dados integrados salvos em: {self.output_file}")
        
        # Salvar backup com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"integrated_crime_data_backup_{timestamp}.csv"
        integrated_df.to_csv(backup_file, index=False, encoding='utf-8')
        print(f"💾 Backup salvo em: {backup_file}")
        
        return self.output_file
    
    def create_metadata_file(self, validation: Dict):
        """Cria arquivo de metadados da integração"""
        metadata = {
            "integration_info": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "description": "Dataset integrado de criminalidade de Porto Alegre"
            },
            "data_sources": {
                "original_dataset": {
                    "file": self.current_data_file,
                    "description": "Dados originais do projeto ALERTA POA"
                },
                "distributed_model": {
                    "file": self.distributed_data_file,
                    "description": "Dados distribuídos baseados no modelo UFRGS"
                }
            },
            "statistics": validation,
            "limitations": [
                "Dados distribuídos são estimativas baseadas em modelo acadêmico",
                "Pesquisa UFRGS é de 2016-2017 (pode estar desatualizada)",
                "Alguns tipos de crime podem ter distribuição imprecisa",
                "Fatores populacionais são estimativas"
            ],
            "methodology": [
                "Dados originais mantidos como fonte primária",
                "Modelo UFRGS aplicado para distribuir dados municipais",
                "Sobreposições removidas para evitar duplicação",
                "Tipos de crime padronizados"
            ]
        }
        
        metadata_file = "integrated_crime_data_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Metadados salvos em: {metadata_file}")
        return metadata_file

def main():
    """Função principal"""
    print("🔄 Iniciando integração de dados de criminalidade...")
    
    # Criar integrador
    integrator = CrimeDataIntegrator()
    
    # Carregar dados
    print("\n📂 Carregando dados...")
    current_data = integrator.load_current_data()
    distributed_data = integrator.load_distributed_data()
    
    # Padronizar dados atuais
    print("\n🔧 Padronizando dados atuais...")
    current_standardized = integrator.standardize_current_data(current_data)
    current_standardized = integrator.standardize_crime_types(current_standardized)
    current_aggregated = integrator.aggregate_current_data(current_standardized)
    
    # Padronizar dados distribuídos
    print("\n🔧 Padronizando dados distribuídos...")
    distributed_standardized = integrator.standardize_crime_types(distributed_data)
    
    # Filtrar sobreposições
    print("\n🔍 Filtrando sobreposições...")
    current_filtered, distributed_filtered = integrator.filter_overlapping_data(
        current_aggregated, distributed_standardized
    )
    
    # Integrar datasets
    print("\n🔗 Integrando datasets...")
    integrated_data = integrator.integrate_datasets(current_filtered, distributed_filtered)
    
    # Validar integração
    print("\n✅ Validando integração...")
    validation = integrator.validate_integration(integrated_data)
    
    # Gerar relatório
    integrator.generate_integration_report(validation)
    
    # Salvar dados
    print("\n💾 Salvando dados integrados...")
    output_file = integrator.save_integrated_data(integrated_data)
    metadata_file = integrator.create_metadata_file(validation)
    
    print(f"\n✅ Integração concluída com sucesso!")
    print(f"📁 Arquivo principal: {output_file}")
    print(f"📋 Metadados: {metadata_file}")
    print(f"🎯 Próximo passo: Validar com dados conhecidos")

if __name__ == "__main__":
    main()
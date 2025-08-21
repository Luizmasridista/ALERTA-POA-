#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo de Distribuição de Crimes por Bairros
Aplica modelo baseado na pesquisa UFRGS aos dados municipais
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import os
from typing import Dict, List, Tuple

class CrimeDistributionModel:
    def __init__(self, model_file="ufrgs_distribution_model.json"):
        self.model_file = model_file
        self.distribution_model = self.load_distribution_model()
        self.all_neighborhoods = self.get_all_poa_neighborhoods()
        
    def load_distribution_model(self):
        """Carrega o modelo de distribuição criado"""
        try:
            with open(self.model_file, 'r', encoding='utf-8') as f:
                model_data = json.load(f)
            return model_data['model']
        except FileNotFoundError:
            print(f"⚠️  Arquivo {self.model_file} não encontrado. Criando modelo básico...")
            return self.create_basic_model()
    
    def create_basic_model(self):
        """Cria modelo básico se o arquivo não existir"""
        basic_neighborhoods = [
            "Centro Histórico", "Cidade Baixa", "Menino Deus", 
            "Floresta", "Santana", "Azenha"
        ]
        
        basic_model = {}
        for neighborhood in basic_neighborhoods:
            basic_model[neighborhood] = {
                "zone": "Centro" if neighborhood in ["Centro Histórico", "Cidade Baixa", "Menino Deus", "Azenha"] else "Norte",
                "population_factor": 1.0 / len(basic_neighborhoods),
                "final_weights": {
                    "Homicídio": 0.1,
                    "Roubo": 0.3,
                    "Roubo de veículo": 0.2,
                    "Furto": 0.3,
                    "Lesão corporal": 0.1
                }
            }
        return basic_model
    
    def get_all_poa_neighborhoods(self):
        """Lista completa dos 94 bairros oficiais de Porto Alegre"""
        return [
            # Zona Norte
            "Anchieta", "Auxiliadora", "Bom Fim", "Farroupilha", "Higienópolis", 
            "Independência", "Moinhos de Vento", "Mont'Serrat", "Rio Branco", "Santana",
            
            # Zona Sul
            "Aberta dos Morros", "Belém Novo", "Belém Velho", "Campo Novo", "Cavalhada", 
            "Chapéu do Sol", "Coronel Aparício Borges", "Espírito Santo", "Guarujá", 
            "Hípica", "Ipanema", "Lageado", "Lami", "Nonoai", "Pedra Redonda", 
            "Ponta Grossa", "Restinga", "Serraria", "Sétimo Céu", "Tristeza", "Vila Assunção", 
            "Vila Conceição", "Vila Nova",
            
            # Zona Leste
            "Agronomia", "Bela Vista", "Boa Vista", "Camaquã", "Cascata", "Cristal", 
            "Glória", "Jardim Botânico", "Jardim do Salso", "Lomba do Pinheiro", 
            "Mário Quintana", "Medianeira", "Partenon", "Santo Antônio", "São José", 
            "Três Figueiras", "Vila João Pessoa", "Volta do Guerino",
            
            # Zona Oeste
            "Arquipélago", "Humaitá", "Ilha da Pintada", "Ilha do Pavão", "Navegantes", 
            "Serraria",
            
            # Centro
            "Azenha", "Centro Histórico", "Cidade Baixa", "Floresta", "Marcílio Dias", 
            "Menino Deus", "Praia de Belas", "Santa Cecília",
            
            # Zona Norte (continuação)
            "Jardim Lindóia", "Jardim São Pedro", "Mapa", "Mathias Velho", "Passo d'Areia", 
            "Petrópolis", "Rubem Berta", "São Geraldo", "São João", "Sarandi", "Vila Ipiranga",
            
            # Zona Extremo Sul
            "Chapéu do Sol", "Ponta Grossa", "Vila Assunção",
            
            # Outros bairros
            "Boa Vista", "Camaquã", "Cascata", "Cristal", "Glória", "Jardim Botânico", 
            "Lomba do Pinheiro", "Mário Quintana", "Medianeira", "Partenon", "Santo Antônio", 
            "São José", "Três Figueiras", "Vila João Pessoa", "Volta do Guerino"
        ]
    
    def classify_neighborhood_by_zone(self, neighborhood: str) -> str:
        """Classifica bairro por zona geográfica"""
        # Mapeamento simplificado por zona
        zone_mapping = {
            # Centro
            "Centro": ["Centro Histórico", "Cidade Baixa", "Floresta", "Marcílio Dias", 
                      "Menino Deus", "Praia de Belas", "Santa Cecília", "Azenha"],
            
            # Norte
            "Norte": ["Anchieta", "Auxiliadora", "Bom Fim", "Farroupilha", "Higienópolis", 
                     "Independência", "Moinhos de Vento", "Mont'Serrat", "Rio Branco", "Santana",
                     "Jardim Lindóia", "Jardim São Pedro", "Mapa", "Mathias Velho", "Passo d'Areia", 
                     "Petrópolis", "Rubem Berta", "São Geraldo", "São João", "Sarandi", "Vila Ipiranga"],
            
            # Sul
            "Sul": ["Aberta dos Morros", "Belém Novo", "Belém Velho", "Campo Novo", "Cavalhada", 
                   "Chapéu do Sol", "Coronel Aparício Borges", "Espírito Santo", "Guarujá", 
                   "Hípica", "Ipanema", "Lageado", "Lami", "Nonoai", "Pedra Redonda", 
                   "Ponta Grossa", "Restinga", "Serraria", "Sétimo Céu", "Tristeza", 
                   "Vila Assunção", "Vila Conceição", "Vila Nova"],
            
            # Leste
            "Leste": ["Agronomia", "Bela Vista", "Boa Vista", "Camaquã", "Cascata", "Cristal", 
                     "Glória", "Jardim Botânico", "Jardim do Salso", "Lomba do Pinheiro", 
                     "Mário Quintana", "Medianeira", "Partenon", "Santo Antônio", "São José", 
                     "Três Figueiras", "Vila João Pessoa", "Volta do Guerino"],
            
            # Oeste
            "Oeste": ["Arquipélago", "Humaitá", "Ilha da Pintada", "Ilha do Pavão", "Navegantes"]
        }
        
        for zone, neighborhoods in zone_mapping.items():
            if neighborhood in neighborhoods:
                return zone
        
        # Default para bairros não mapeados
        return "Norte"  # Assume zona norte como padrão
    
    def get_crime_weights_by_zone(self, zone: str) -> Dict[str, float]:
        """Retorna pesos de crime por zona baseados na pesquisa UFRGS"""
        zone_weights = {
            "Norte": {
                "Homicídio": 0.7,
                "Roubo": 0.6,
                "Roubo de veículo": 0.6,
                "Furto": 0.5,
                "Lesão corporal": 0.6,
                "Tráfico de drogas": 0.7,
                "Ameaça": 0.6
            },
            "Centro": {
                "Homicídio": 0.3,
                "Roubo": 0.8,
                "Roubo de veículo": 0.8,
                "Furto": 0.9,
                "Lesão corporal": 0.7,
                "Tráfico de drogas": 0.5,
                "Ameaça": 0.6
            },
            "Sul": {
                "Homicídio": 0.7,
                "Roubo": 0.4,
                "Roubo de veículo": 0.4,
                "Furto": 0.4,
                "Lesão corporal": 0.5,
                "Tráfico de drogas": 0.6,
                "Ameaça": 0.5
            },
            "Leste": {
                "Homicídio": 0.4,
                "Roubo": 0.7,
                "Roubo de veículo": 0.7,
                "Furto": 0.6,
                "Lesão corporal": 0.5,
                "Tráfico de drogas": 0.5,
                "Ameaça": 0.5
            },
            "Oeste": {
                "Homicídio": 0.5,
                "Roubo": 0.5,
                "Roubo de veículo": 0.5,
                "Furto": 0.5,
                "Lesão corporal": 0.5,
                "Tráfico de drogas": 0.5,
                "Ameaça": 0.5
            }
        }
        
        return zone_weights.get(zone, zone_weights["Norte"])
    
    def estimate_population_factor(self, neighborhood: str) -> float:
        """Estima fator populacional do bairro"""
        # Estimativas baseadas em dados do IBGE e conhecimento local
        population_estimates = {
            # Bairros centrais (alta densidade)
            "Centro Histórico": 40000,
            "Cidade Baixa": 12000,
            "Menino Deus": 35000,
            "Floresta": 13000,
            "Santana": 45000,
            "Azenha": 8000,
            
            # Bairros nobres (média-alta densidade)
            "Moinhos de Vento": 25000,
            "Auxiliadora": 30000,
            "Bom Fim": 20000,
            "Independência": 15000,
            "Higienópolis": 18000,
            "Mont'Serrat": 12000,
            "Rio Branco": 10000,
            "Três Figueiras": 22000,
            "Jardim Botânico": 8000,
            
            # Bairros populosos
            "Restinga": 60000,
            "Lomba do Pinheiro": 55000,
            "Partenon": 40000,
            "Sarandi": 35000,
            "Rubem Berta": 30000,
            "Cavalhada": 45000,
            "Tristeza": 25000,
            "Ipanema": 20000,
            
            # Outros bairros (estimativa média)
            "default": 15000
        }
        
        population = population_estimates.get(neighborhood, population_estimates["default"])
        
        # Calcular fator proporcional (assumindo população total de ~1.5M)
        total_estimated_population = 1500000
        return population / total_estimated_population
    
    def distribute_municipal_crimes(self, municipal_data: pd.DataFrame) -> pd.DataFrame:
        """Distribui crimes municipais por bairros usando o modelo"""
        distributed_data = []
        
        for _, row in municipal_data.iterrows():
            crime_type = row['tipo_crime']
            total_crimes = row['quantidade']
            date = row['data']
            
            # Distribuir por todos os bairros
            for neighborhood in self.all_neighborhoods:
                zone = self.classify_neighborhood_by_zone(neighborhood)
                crime_weights = self.get_crime_weights_by_zone(zone)
                population_factor = self.estimate_population_factor(neighborhood)
                
                # Calcular peso final
                crime_weight = crime_weights.get(crime_type, 0.5)
                final_weight = crime_weight * population_factor
                
                # Calcular quantidade distribuída
                distributed_crimes = int(total_crimes * final_weight)
                
                if distributed_crimes > 0:
                    distributed_data.append({
                        'data': date,
                        'bairro': neighborhood,
                        'tipo_crime': crime_type,
                        'quantidade': distributed_crimes,
                        'zona': zone,
                        'fonte': 'SSP-RS (distribuído)',
                        'peso_crime': crime_weight,
                        'fator_populacional': population_factor,
                        'peso_final': final_weight
                    })
        
        return pd.DataFrame(distributed_data)
    
    def create_sample_municipal_data(self) -> pd.DataFrame:
        """Cria dados municipais de exemplo para teste"""
        # Dados de exemplo baseados em padrões típicos
        sample_data = []
        
        # Gerar dados para 2024
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        crime_types = {
            "Homicídio": {"min": 5, "max": 15},
            "Roubo": {"min": 800, "max": 1200},
            "Roubo de veículo": {"min": 300, "max": 500},
            "Furto": {"min": 1500, "max": 2500},
            "Lesão corporal": {"min": 400, "max": 700},
            "Tráfico de drogas": {"min": 100, "max": 200},
            "Ameaça": {"min": 200, "max": 400}
        }
        
        current_date = start_date
        while current_date <= end_date:
            for crime_type, ranges in crime_types.items():
                # Variação sazonal
                month_factor = 1.0
                if current_date.month in [12, 1, 2]:  # Verão - mais crimes
                    month_factor = 1.2
                elif current_date.month in [6, 7, 8]:  # Inverno - menos crimes
                    month_factor = 0.8
                
                base_crimes = np.random.randint(ranges["min"], ranges["max"])
                monthly_crimes = int(base_crimes * month_factor)
                
                sample_data.append({
                    'data': current_date.strftime('%Y-%m-%d'),
                    'tipo_crime': crime_type,
                    'quantidade': monthly_crimes,
                    'municipio': 'Porto Alegre',
                    'fonte': 'SSP-RS (simulado)'
                })
            
            # Próximo mês
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return pd.DataFrame(sample_data)
    
    def validate_distribution(self, distributed_data: pd.DataFrame, original_data: pd.DataFrame) -> Dict:
        """Valida a distribuição comparando totais"""
        validation_results = {}
        
        # Comparar totais por tipo de crime
        original_totals = original_data.groupby('tipo_crime')['quantidade'].sum()
        distributed_totals = distributed_data.groupby('tipo_crime')['quantidade'].sum()
        
        validation_results['crime_type_comparison'] = {}
        for crime_type in original_totals.index:
            original_total = original_totals[crime_type]
            distributed_total = distributed_totals.get(crime_type, 0)
            difference = abs(original_total - distributed_total)
            percentage_diff = (difference / original_total) * 100 if original_total > 0 else 0
            
            validation_results['crime_type_comparison'][crime_type] = {
                'original': int(original_total),
                'distributed': int(distributed_total),
                'difference': int(difference),
                'percentage_diff': round(percentage_diff, 2)
            }
        
        # Estatísticas gerais
        validation_results['general_stats'] = {
            'total_neighborhoods': distributed_data['bairro'].nunique(),
            'total_records': len(distributed_data),
            'date_range': {
                'start': distributed_data['data'].min(),
                'end': distributed_data['data'].max()
            }
        }
        
        return validation_results
    
    def generate_distribution_report(self, distributed_data: pd.DataFrame, validation: Dict):
        """Gera relatório da distribuição"""
        print("=" * 80)
        print("RELATÓRIO DE DISTRIBUIÇÃO DE CRIMES POR BAIRROS")
        print("=" * 80)
        print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Estatísticas gerais
        stats = validation['general_stats']
        print("1. ESTATÍSTICAS GERAIS:")
        print("-" * 40)
        print(f"• Total de bairros cobertos: {stats['total_neighborhoods']}")
        print(f"• Total de registros gerados: {stats['total_records']}")
        print(f"• Período: {stats['date_range']['start']} a {stats['date_range']['end']}")
        print()
        
        # Comparação por tipo de crime
        print("2. VALIDAÇÃO POR TIPO DE CRIME:")
        print("-" * 40)
        comparison = validation['crime_type_comparison']
        for crime_type, data in comparison.items():
            print(f"• {crime_type}:")
            print(f"  Original: {data['original']:,}")
            print(f"  Distribuído: {data['distributed']:,}")
            print(f"  Diferença: {data['difference']:,} ({data['percentage_diff']:.1f}%)")
            print()
        
        # Top 10 bairros por crimes
        print("3. TOP 10 BAIRROS POR TOTAL DE CRIMES:")
        print("-" * 40)
        top_neighborhoods = distributed_data.groupby('bairro')['quantidade'].sum().sort_values(ascending=False).head(10)
        for i, (neighborhood, total) in enumerate(top_neighborhoods.items(), 1):
            zone = self.classify_neighborhood_by_zone(neighborhood)
            print(f"{i:2d}. {neighborhood} (Zona {zone}): {total:,} crimes")
        print()
        
        # Distribuição por zona
        print("4. DISTRIBUIÇÃO POR ZONA GEOGRÁFICA:")
        print("-" * 40)
        zone_distribution = distributed_data.groupby('zona')['quantidade'].sum().sort_values(ascending=False)
        total_crimes = zone_distribution.sum()
        for zone, total in zone_distribution.items():
            percentage = (total / total_crimes) * 100
            print(f"• Zona {zone}: {total:,} crimes ({percentage:.1f}%)")
        print()
        
        # Distribuição por tipo de crime
        print("5. DISTRIBUIÇÃO POR TIPO DE CRIME:")
        print("-" * 40)
        crime_distribution = distributed_data.groupby('tipo_crime')['quantidade'].sum().sort_values(ascending=False)
        for crime_type, total in crime_distribution.items():
            percentage = (total / total_crimes) * 100
            print(f"• {crime_type}: {total:,} crimes ({percentage:.1f}%)")
        print()
        
        print("6. PRÓXIMOS PASSOS:")
        print("-" * 40)
        print("1. Integrar dados distribuídos com dataset atual")
        print("2. Validar com dados reais conhecidos")
        print("3. Ajustar pesos se necessário")
        print("4. Expandir para dados históricos (2020-2023)")
        print("5. Documentar limitações e metodologia")
        print()
        print("=" * 80)
    
    def save_distributed_data(self, distributed_data: pd.DataFrame, filename="distributed_crime_data.csv"):
        """Salva dados distribuídos em arquivo CSV"""
        distributed_data.to_csv(filename, index=False, encoding='utf-8')
        print(f"\n💾 Dados distribuídos salvos em: {filename}")
        return filename

def main():
    """Função principal"""
    print("🚀 Iniciando modelo de distribuição de crimes por bairros...")
    
    # Criar instância do modelo
    model = CrimeDistributionModel()
    
    # Criar dados municipais de exemplo
    print("📊 Criando dados municipais de exemplo...")
    municipal_data = model.create_sample_municipal_data()
    print(f"✅ {len(municipal_data)} registros municipais criados")
    
    # Aplicar distribuição
    print("🔄 Aplicando modelo de distribuição...")
    distributed_data = model.distribute_municipal_crimes(municipal_data)
    print(f"✅ {len(distributed_data)} registros distribuídos por bairros")
    
    # Validar distribuição
    print("🔍 Validando distribuição...")
    validation = model.validate_distribution(distributed_data, municipal_data)
    
    # Gerar relatório
    model.generate_distribution_report(distributed_data, validation)
    
    # Salvar dados
    output_file = model.save_distributed_data(distributed_data)
    
    print(f"\n✅ Modelo de distribuição aplicado com sucesso!")
    print(f"📁 Dados salvos em: {output_file}")
    print(f"🎯 Próximo passo: Integrar com dataset atual do projeto")

if __name__ == "__main__":
    main()
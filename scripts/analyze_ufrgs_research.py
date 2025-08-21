#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise da Pesquisa UFRGS sobre Crimes Violentos por Bairros
Extrai informações da pesquisa para criar modelo de distribuição
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json

class UFRGSResearchAnalyzer:
    def __init__(self):
        self.research_data = self.load_research_findings()
        self.target_neighborhoods = [
            "Centro Histórico", "Cidade Baixa", "Menino Deus", 
            "Floresta", "Santana", "Azenha"
        ]
        
    def load_research_findings(self):
        """Carrega os principais achados da pesquisa UFRGS"""
        return {
            "title": "A prevalência de crimes violentos e a desigualdade social nos bairros do município de Porto Alegre",
            "institution": "UFRGS - Instituto de Filosofia e Ciências Humanas",
            "period": "2016-2017",
            "total_neighborhoods": 94,
            "crime_types_analyzed": [
                "Homicídios dolosos",
                "Roubos de veículos", 
                "Roubos"
            ],
            "key_findings": {
                "homicides": {
                    "pattern": "Concentrados nas zonas periféricas (norte e sul)",
                    "correlation": "Forte correlação com condições socioeconômicas",
                    "zones": ["Norte", "Sul"]
                },
                "vehicle_theft": {
                    "pattern": "Zonas norte, centrais e leste",
                    "correlation": "Pouca correlação com condições socioeconômicas",
                    "zones": ["Norte", "Centro", "Leste"]
                },
                "robberies": {
                    "pattern": "Zonas norte, centrais e leste",
                    "correlation": "Ambivalência da variável renda",
                    "zones": ["Norte", "Centro", "Leste"]
                }
            },
            "socioeconomic_factors": [
                "População",
                "Infraestrutura", 
                "Renda",
                "Trabalho",
                "Educação"
            ]
        }
    
    def classify_project_neighborhoods(self):
        """Classifica os bairros do projeto por zona geográfica"""
        neighborhood_zones = {
            "Centro Histórico": "Centro",
            "Cidade Baixa": "Centro", 
            "Menino Deus": "Centro",
            "Floresta": "Norte",
            "Santana": "Norte",
            "Azenha": "Centro"
        }
        return neighborhood_zones
    
    def estimate_crime_distribution_weights(self):
        """Estima pesos de distribuição baseados nos achados da UFRGS"""
        zones = self.classify_project_neighborhoods()
        
        # Pesos baseados nos padrões identificados na pesquisa
        crime_weights = {
            "Homicídio": {
                "Norte": 0.7,  # Alta concentração em zonas periféricas
                "Centro": 0.3,  # Menor concentração no centro
                "Sul": 0.7,
                "Leste": 0.4
            },
            "Roubo": {
                "Norte": 0.6,  # Distribuição entre norte, centro e leste
                "Centro": 0.8,  # Alta concentração no centro
                "Sul": 0.4,
                "Leste": 0.7
            },
            "Roubo de veículo": {
                "Norte": 0.6,  # Distribuição entre norte, centro e leste
                "Centro": 0.8,  # Alta concentração no centro
                "Sul": 0.4,
                "Leste": 0.7
            },
            "Furto": {
                "Norte": 0.5,  # Assumindo padrão similar aos roubos
                "Centro": 0.9,  # Maior concentração no centro (áreas comerciais)
                "Sul": 0.4,
                "Leste": 0.6
            },
            "Lesão corporal": {
                "Norte": 0.6,  # Assumindo padrão misto
                "Centro": 0.7,
                "Sul": 0.5,
                "Leste": 0.5
            }
        }
        
        # Aplicar pesos aos bairros do projeto
        neighborhood_weights = {}
        for neighborhood, zone in zones.items():
            neighborhood_weights[neighborhood] = {}
            for crime_type, zone_weights in crime_weights.items():
                neighborhood_weights[neighborhood][crime_type] = zone_weights.get(zone, 0.5)
        
        return neighborhood_weights
    
    def create_population_adjustment_factors(self):
        """Cria fatores de ajuste baseados na população dos bairros"""
        # Dados aproximados de população (baseados em estimativas)
        population_estimates = {
            "Centro Histórico": 40000,
            "Cidade Baixa": 12000,
            "Menino Deus": 35000,
            "Floresta": 13000,
            "Santana": 45000,
            "Azenha": 8000
        }
        
        total_population = sum(population_estimates.values())
        
        # Calcular fatores proporcionais
        population_factors = {}
        for neighborhood, pop in population_estimates.items():
            population_factors[neighborhood] = pop / total_population
        
        return population_factors
    
    def generate_distribution_model(self):
        """Gera modelo completo de distribuição de crimes por bairros"""
        crime_weights = self.estimate_crime_distribution_weights()
        population_factors = self.create_population_adjustment_factors()
        
        distribution_model = {}
        
        for neighborhood in self.target_neighborhoods:
            distribution_model[neighborhood] = {
                "zone": self.classify_project_neighborhoods()[neighborhood],
                "population_factor": population_factors[neighborhood],
                "crime_weights": crime_weights[neighborhood],
                "final_weights": {}
            }
            
            # Combinar peso de crime com fator populacional
            for crime_type, crime_weight in crime_weights[neighborhood].items():
                combined_weight = crime_weight * population_factors[neighborhood]
                distribution_model[neighborhood]["final_weights"][crime_type] = combined_weight
        
        return distribution_model
    
    def validate_model_with_current_data(self):
        """Valida o modelo com dados atuais do projeto"""
        try:
            # Tentar carregar dados atuais
            current_data = pd.read_csv("data/crime_data_poa.csv")
            
            validation_results = {
                "total_records": len(current_data),
                "neighborhoods_covered": current_data['bairro'].nunique(),
                "crime_types_covered": current_data['tipo_crime'].nunique(),
                "date_range": {
                    "start": current_data['data'].min(),
                    "end": current_data['data'].max()
                }
            }
            
            # Analisar distribuição atual por bairro
            current_distribution = current_data.groupby(['bairro', 'tipo_crime']).size().unstack(fill_value=0)
            
            validation_results["current_distribution"] = current_distribution.to_dict()
            
            return validation_results
            
        except FileNotFoundError:
            return {"error": "Arquivo de dados atual não encontrado"}
    
    def create_implementation_strategy(self):
        """Cria estratégia de implementação do modelo"""
        strategy = {
            "phase_1_data_collection": {
                "description": "Coletar dados municipais da SSP-RS",
                "tasks": [
                    "Download das planilhas SSP-RS (2020-2025)",
                    "Extração de dados de Porto Alegre",
                    "Limpeza e padronização dos dados"
                ]
            },
            "phase_2_model_application": {
                "description": "Aplicar modelo de distribuição",
                "tasks": [
                    "Aplicar pesos por zona geográfica",
                    "Ajustar por fatores populacionais",
                    "Distribuir crimes por bairros do projeto"
                ]
            },
            "phase_3_validation": {
                "description": "Validar resultados",
                "tasks": [
                    "Comparar com dados atuais do projeto",
                    "Validar com notícias e relatórios",
                    "Ajustar modelo se necessário"
                ]
            },
            "phase_4_integration": {
                "description": "Integrar com dataset atual",
                "tasks": [
                    "Merge com dados existentes",
                    "Expandir cobertura temporal",
                    "Documentar limitações"
                ]
            }
        }
        return strategy
    
    def generate_comprehensive_report(self):
        """Gera relatório completo da análise"""
        print("=" * 80)
        print("ANÁLISE DA PESQUISA UFRGS - CRIMES VIOLENTOS POR BAIRROS")
        print("=" * 80)
        print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Informações da pesquisa
        research = self.research_data
        print("1. INFORMAÇÕES DA PESQUISA:")
        print("-" * 40)
        print(f"Título: {research['title']}")
        print(f"Instituição: {research['institution']}")
        print(f"Período analisado: {research['period']}")
        print(f"Total de bairros: {research['total_neighborhoods']}")
        print(f"Tipos de crime analisados: {', '.join(research['crime_types_analyzed'])}")
        print()
        
        # Principais achados
        print("2. PRINCIPAIS ACHADOS:")
        print("-" * 40)
        findings = research['key_findings']
        for crime_type, data in findings.items():
            print(f"• {crime_type.replace('_', ' ').title()}:")
            print(f"  Padrão: {data['pattern']}")
            print(f"  Correlação: {data['correlation']}")
            print(f"  Zonas: {', '.join(data['zones'])}")
            print()
        
        # Classificação dos bairros do projeto
        print("3. CLASSIFICAÇÃO DOS BAIRROS DO PROJETO:")
        print("-" * 40)
        zones = self.classify_project_neighborhoods()
        for neighborhood, zone in zones.items():
            print(f"• {neighborhood}: Zona {zone}")
        print()
        
        # Modelo de distribuição
        print("4. MODELO DE DISTRIBUIÇÃO GERADO:")
        print("-" * 40)
        model = self.generate_distribution_model()
        for neighborhood, data in model.items():
            print(f"• {neighborhood} (Zona {data['zone']}):")
            print(f"  Fator populacional: {data['population_factor']:.3f}")
            print(f"  Pesos finais por crime:")
            for crime, weight in data['final_weights'].items():
                print(f"    - {crime}: {weight:.3f}")
            print()
        
        # Validação com dados atuais
        print("5. VALIDAÇÃO COM DADOS ATUAIS:")
        print("-" * 40)
        validation = self.validate_model_with_current_data()
        if "error" in validation:
            print(f"⚠️  {validation['error']}")
        else:
            print(f"• Total de registros atuais: {validation['total_records']}")
            print(f"• Bairros cobertos: {validation['neighborhoods_covered']}")
            print(f"• Tipos de crime: {validation['crime_types_covered']}")
            print(f"• Período: {validation['date_range']['start']} a {validation['date_range']['end']}")
        print()
        
        # Estratégia de implementação
        print("6. ESTRATÉGIA DE IMPLEMENTAÇÃO:")
        print("-" * 40)
        strategy = self.create_implementation_strategy()
        for phase_key, phase in strategy.items():
            print(f"• {phase['description']}:")
            for task in phase['tasks']:
                print(f"  - {task}")
            print()
        
        # Limitações e considerações
        print("7. LIMITAÇÕES E CONSIDERAÇÕES:")
        print("-" * 40)
        print("• Dados da pesquisa são de 2016-2017 (podem estar desatualizados)")
        print("• Modelo baseado em padrões gerais, não dados específicos")
        print("• Fatores populacionais são estimativas")
        print("• Necessária validação com dados reais")
        print("• Alguns tipos de crime não foram analisados na pesquisa original")
        print()
        
        print("8. PRÓXIMOS PASSOS:")
        print("-" * 40)
        print("1. Implementar modelo de distribuição")
        print("2. Aplicar aos dados municipais da SSP-RS")
        print("3. Validar resultados com dados conhecidos")
        print("4. Ajustar pesos se necessário")
        print("5. Integrar com dataset atual")
        print("6. Expandir para todos os 94 bairros")
        print()
        print("=" * 80)
    
    def save_distribution_model(self, filename="ufrgs_distribution_model.json"):
        """Salva o modelo de distribuição em arquivo JSON"""
        model = self.generate_distribution_model()
        
        # Adicionar metadados
        model_with_metadata = {
            "metadata": {
                "source": "Pesquisa UFRGS 2016-2017",
                "created_at": datetime.now().isoformat(),
                "description": "Modelo de distribuição de crimes por bairros baseado em pesquisa acadêmica",
                "neighborhoods_count": len(self.target_neighborhoods),
                "crime_types": list(model[self.target_neighborhoods[0]]['final_weights'].keys())
            },
            "model": model
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(model_with_metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Modelo salvo em: {filename}")
        return filename

def main():
    """Função principal"""
    analyzer = UFRGSResearchAnalyzer()
    
    # Gerar relatório completo
    analyzer.generate_comprehensive_report()
    
    # Salvar modelo
    model_file = analyzer.save_distribution_model()
    
    print(f"\n✅ Análise da pesquisa UFRGS concluída!")
    print(f"📊 Modelo de distribuição criado e salvo em: {model_file}")
    print(f"🎯 Próximo passo: Aplicar modelo aos dados municipais da SSP-RS")

if __name__ == "__main__":
    main()
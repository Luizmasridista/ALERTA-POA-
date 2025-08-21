#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para download de dados da SSP-RS
Automatiza o download das planilhas de indicadores criminais de Porto Alegre
"""

import requests
import os
from datetime import datetime
import pandas as pd

class SSPDataDownloader:
    def __init__(self):
        self.base_url = "https://www.ssp.rs.gov.br"
        self.download_dir = "data/ssp_rs"
        self.ensure_directory()
        
    def ensure_directory(self):
        """Cria diretório para downloads se não existir"""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            print(f"Diretório criado: {self.download_dir}")
    
    def get_available_data_sources(self):
        """Lista as fontes de dados identificadas na SSP-RS"""
        sources = {
            "indicadores_criminais": {
                "url": "https://www.ssp.rs.gov.br/indicadores-criminais",
                "description": "Indicadores criminais gerais e por municípios",
                "period": "Dados mensais desde 2002",
                "coverage": "20 principais tipos criminais",
                "format": "Excel (.xlsx)"
            },
            "violencia_mulher": {
                "url": "https://www.ssp.rs.gov.br/indicadores-da-violencia-contra-a-mulher",
                "description": "Indicadores de violência contra a mulher",
                "period": "Dados mensais desde 2012",
                "coverage": "5 principais crimes contra mulheres",
                "format": "Excel (.xlsx)"
            },
            "indicadores_eficiencia": {
                "url": "https://www.ssp.rs.gov.br/indicadores-de-eficiencia",
                "description": "Indicadores de eficiência policial",
                "period": "Dados mensais desde 2007",
                "coverage": "Ações da BM e PC",
                "format": "Excel (.xlsx)"
            }
        }
        return sources
    
    def analyze_porto_alegre_data_needs(self):
        """Analisa as necessidades específicas de dados para Porto Alegre"""
        needs = {
            "municipality_code": "Porto Alegre",
            "target_years": [2020, 2021, 2022, 2023, 2024, 2025],
            "crime_types_needed": [
                "Homicídio",
                "Latrocínio", 
                "Roubo",
                "Roubo de veículo",
                "Furto",
                "Furto de veículo",
                "Lesão corporal",
                "Ameaça",
                "Estupro",
                "Feminicídio",
                "Tentativa de feminicídio"
            ],
            "data_granularity": "Municipal (não disponível por bairro)",
            "update_frequency": "Mensal"
        }
        return needs
    
    def get_manual_download_instructions(self):
        """Fornece instruções para download manual das planilhas"""
        instructions = {
            "step_1": {
                "action": "Acessar página de Indicadores Criminais",
                "url": "https://www.ssp.rs.gov.br/indicadores-criminais",
                "files_to_download": [
                    "Indicadores criminais geral e por municípios 2025.xlsx",
                    "Indicadores criminais geral e por municípios 2024.xlsx",
                    "Indicadores criminais geral e por municípios 2023.xlsx",
                    "Indicadores criminais geral e por municípios 2022.xlsx",
                    "Indicadores criminais geral e por municípios 2021.xlsx",
                    "Indicadores criminais geral e por municípios 2020.xlsx"
                ]
            },
            "step_2": {
                "action": "Acessar página de Violência Contra a Mulher",
                "url": "https://www.ssp.rs.gov.br/indicadores-da-violencia-contra-a-mulher",
                "files_to_download": [
                    "Indicadores de violência contra a mulher geral e por município 2024.xlsx",
                    "Indicadores de violência contra a mulher geral e por município 2023.xlsx",
                    "Indicadores de violência contra a mulher geral e por município 2022.xlsx",
                    "Indicadores de violência contra a mulher geral e por município 2021.xlsx",
                    "Indicadores de violência contra a mulher geral e por município 2020.xlsx"
                ]
            },
            "step_3": {
                "action": "Salvar arquivos no diretório",
                "target_directory": self.download_dir,
                "naming_convention": "ssp_rs_[tipo]_[ano].xlsx"
            }
        }
        return instructions
    
    def analyze_data_limitations(self):
        """Analisa as limitações dos dados da SSP-RS"""
        limitations = {
            "geographic_granularity": {
                "available": "Dados por município",
                "needed": "Dados por bairro",
                "impact": "Não é possível obter dados específicos por bairro diretamente"
            },
            "data_distribution": {
                "challenge": "Como distribuir dados municipais por bairros",
                "solutions": [
                    "Usar proporções da pesquisa UFRGS (2016-2017)",
                    "Aplicar fatores demográficos por bairro",
                    "Usar dados de notícias para validação",
                    "Criar modelo estatístico de distribuição"
                ]
            },
            "temporal_coverage": {
                "available": "2002-2025 (mensal)",
                "project_needs": "2020-2025",
                "status": "Cobertura adequada"
            },
            "crime_types": {
                "available": "20 principais tipos criminais",
                "project_coverage": "Boa cobertura dos tipos necessários",
                "gaps": "Alguns crimes específicos podem não estar incluídos"
            }
        }
        return limitations
    
    def create_integration_strategy(self):
        """Cria estratégia para integração com dataset atual"""
        strategy = {
            "phase_1_download": {
                "description": "Download manual das planilhas SSP-RS",
                "files_needed": 11,  # 6 anos de indicadores + 5 anos de violência contra mulher
                "estimated_time": "30 minutos"
            },
            "phase_2_processing": {
                "description": "Processamento e limpeza dos dados",
                "tasks": [
                    "Extrair dados específicos de Porto Alegre",
                    "Padronizar nomes de crimes",
                    "Converter para formato do projeto",
                    "Agregar dados mensais"
                ]
            },
            "phase_3_distribution": {
                "description": "Distribuição por bairros usando modelo",
                "approach": "Aplicar proporções da pesquisa UFRGS",
                "validation": "Comparar com dados de notícias"
            },
            "phase_4_integration": {
                "description": "Integração com dataset atual",
                "method": "Merge baseado em bairro, data e tipo de crime",
                "output": "Dataset expandido com cobertura histórica"
            }
        }
        return strategy
    
    def generate_report(self):
        """Gera relatório completo sobre dados da SSP-RS"""
        print("=" * 80)
        print("RELATÓRIO: DADOS SSP-RS PARA PORTO ALEGRE")
        print("=" * 80)
        print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Fontes disponíveis
        print("1. FONTES DE DADOS IDENTIFICADAS:")
        print("-" * 40)
        sources = self.get_available_data_sources()
        for key, source in sources.items():
            print(f"• {source['description']}")
            print(f"  URL: {source['url']}")
            print(f"  Período: {source['period']}")
            print(f"  Cobertura: {source['coverage']}")
            print(f"  Formato: {source['format']}")
            print()
        
        # Necessidades do projeto
        print("2. NECESSIDADES DO PROJETO:")
        print("-" * 40)
        needs = self.analyze_porto_alegre_data_needs()
        print(f"• Município: {needs['municipality_code']}")
        print(f"• Anos necessários: {', '.join(map(str, needs['target_years']))}")
        print(f"• Granularidade: {needs['data_granularity']}")
        print(f"• Frequência: {needs['update_frequency']}")
        print(f"• Tipos de crime ({len(needs['crime_types_needed'])}):")
        for crime in needs['crime_types_needed']:
            print(f"  - {crime}")
        print()
        
        # Limitações
        print("3. LIMITAÇÕES IDENTIFICADAS:")
        print("-" * 40)
        limitations = self.analyze_data_limitations()
        for category, details in limitations.items():
            print(f"• {category.replace('_', ' ').title()}:")
            if isinstance(details, dict):
                for key, value in details.items():
                    if isinstance(value, list):
                        print(f"  {key}: {', '.join(value)}")
                    else:
                        print(f"  {key}: {value}")
            print()
        
        # Instruções de download
        print("4. INSTRUÇÕES PARA DOWNLOAD MANUAL:")
        print("-" * 40)
        instructions = self.get_manual_download_instructions()
        for step_key, step in instructions.items():
            print(f"• {step['action']}:")
            if 'url' in step:
                print(f"  URL: {step['url']}")
            if 'files_to_download' in step:
                print(f"  Arquivos ({len(step['files_to_download'])}):")
                for file in step['files_to_download']:
                    print(f"    - {file}")
            if 'target_directory' in step:
                print(f"  Diretório: {step['target_directory']}")
            if 'naming_convention' in step:
                print(f"  Convenção: {step['naming_convention']}")
            print()
        
        # Estratégia de integração
        print("5. ESTRATÉGIA DE INTEGRAÇÃO:")
        print("-" * 40)
        strategy = self.create_integration_strategy()
        for phase_key, phase in strategy.items():
            print(f"• {phase['description']}:")
            if 'files_needed' in phase:
                print(f"  Arquivos necessários: {phase['files_needed']}")
            if 'estimated_time' in phase:
                print(f"  Tempo estimado: {phase['estimated_time']}")
            if 'tasks' in phase:
                print(f"  Tarefas:")
                for task in phase['tasks']:
                    print(f"    - {task}")
            if 'approach' in phase:
                print(f"  Abordagem: {phase['approach']}")
            if 'validation' in phase:
                print(f"  Validação: {phase['validation']}")
            if 'method' in phase:
                print(f"  Método: {phase['method']}")
            if 'output' in phase:
                print(f"  Resultado: {phase['output']}")
            print()
        
        print("6. PRÓXIMOS PASSOS:")
        print("-" * 40)
        print("1. Realizar download manual das planilhas SSP-RS")
        print("2. Processar dados de Porto Alegre")
        print("3. Analisar pesquisa UFRGS para proporções por bairro")
        print("4. Criar modelo de distribuição")
        print("5. Integrar com dataset atual")
        print("6. Validar resultados")
        print("7. Documentar limitações")
        print()
        print("=" * 80)

def main():
    """Função principal"""
    downloader = SSPDataDownloader()
    downloader.generate_report()
    
    print("\n📁 Diretório de download criado:", downloader.download_dir)
    print("\n⚠️  IMPORTANTE: Os dados da SSP-RS precisam ser baixados manualmente")
    print("   devido às políticas de segurança do site.")
    print("\n🔗 Links principais:")
    print("   • Indicadores Criminais: https://www.ssp.rs.gov.br/indicadores-criminais")
    print("   • Violência Contra Mulher: https://www.ssp.rs.gov.br/indicadores-da-violencia-contra-a-mulher")
    
if __name__ == "__main__":
    main()
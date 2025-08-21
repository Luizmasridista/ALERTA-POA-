import pandas as pd
import requests
from datetime import datetime
import json

# Lista dos bairros que temos no projeto atual
current_neighborhoods = [
    'Centro Histórico', 'Cidade Baixa', 'Menino Deus', 'Floresta', 
    'Santana', 'Azenha', 'Bom Fim', 'Independência', 'Moinhos de Vento',
    'Auxiliadora', 'Rio Branco', 'Montserrat', 'Bela Vista', 'Farroupilha',
    'Petrópolis', 'Santa Cecília'
]

print("=== BUSCA POR DADOS REAIS DE CRIMINALIDADE ===")
print(f"Bairros no projeto atual: {len(current_neighborhoods)}")
print("\nBairros:")
for i, bairro in enumerate(current_neighborhoods, 1):
    print(f"{i:2d}. {bairro}")

print("\n=== FONTES OFICIAIS IDENTIFICADAS ===")
print("1. SSP-RS - Secretaria da Segurança Pública do RS")
print("   - Observatório Estadual da Segurança Pública")
print("   - Dados mensais desde 2002")
print("   - URL: https://www.ssp.rs.gov.br/indicadores-criminais")

print("\n2. DataPOA - Portal de Dados Abertos de Porto Alegre")
print("   - Dados municipais em formato aberto")
print("   - URL: http://datapoa.com.br")

print("\n3. ObservaPOA - Observatório da Cidade de Porto Alegre")
print("   - Seção de Violência e Criminalidade (em desenvolvimento)")
print("   - URL: https://prefeitura.poa.br/smpg/observapoa")

print("\n4. Ministério da Justiça e Segurança Pública")
print("   - Sistema Nacional de Informações de Segurança Pública (Sinesp)")
print("   - 28 indicadores nacionais")

print("\n=== PRÓXIMOS PASSOS ===")
print("1. Acessar dados da SSP-RS por município (Porto Alegre)")
print("2. Verificar disponibilidade de dados por bairro")
print("3. Coletar dados históricos 2020-2025")
print("4. Expandir tipos de crimes além de assaltos")
print("5. Validar e integrar dados reais no sistema")

print("\n=== TIPOS DE CRIMES A INCLUIR ===")
crimes_types = [
    'Homicídio doloso', 'Roubo de veículos', 'Roubo a instituição financeira',
    'Roubo de carga', 'Furto de veículos', 'Estupro', 'Tráfico de drogas',
    'Lesão corporal', 'Ameaça', 'Extorsão', 'Sequestro'
]

for i, crime in enumerate(crimes_types, 1):
    print(f"{i:2d}. {crime}")

print("\n=== ANÁLISE DO DATASET ATUAL ===")
try:
    df = pd.read_csv('../data/distributed_crime_data.csv')
    # Renomear colunas para compatibilidade
    df = df.rename(columns={
        'data': 'Data Registro',
        'bairro': 'Bairro'
    })
    print(f"Registros atuais: {len(df)}")
    print(f"Período: {df['Data Registro'].min()} a {df['Data Registro'].max()}")
    print(f"Tipos de crime atual: {df['Descricao do Fato'].unique()}")
    print(f"Bairros com dados: {len(df['Bairro'].unique())}")
except Exception as e:
    print(f"Erro ao ler dataset atual: {e}")

print("\n=== RECOMENDAÇÕES ===")
print("• Priorizar dados oficiais da SSP-RS")
print("• Buscar dados por delegacia/região para mapear bairros")
print("• Incluir coordenadas geográficas precisas")
print("• Expandir período histórico (2020-2025)")
print("• Diversificar tipos de crimes")
print("• Validar qualidade e consistência dos dados")
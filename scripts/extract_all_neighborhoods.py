import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

# Lista dos 94 bairros oficiais de Porto Alegre baseada na Lei 12.112/2016
# Extraída da Wikipedia e outras fontes oficiais
bairros_oficiais = [
    'Aberta dos Morros', 'Agronomia', 'Anchieta', 'Arquipélago', 'Auxiliadora',
    'Azenha', 'Bela Vista', 'Belém Novo', 'Belém Velho', 'Boa Vista',
    'Boa Vista do Sul', 'Bom Fim', 'Bom Jesus', 'Camaquã', 'Campo Novo',
    'Cascata', 'Cavalhada', 'Centro Histórico', 'Chácara das Pedras', 'Chapéu do Sol',
    'Cidade Baixa', 'Coronel Aparício Borges', 'Costa e Silva', 'Cristal', 'Cristo Redentor',
    'Espírito Santo', 'Extrema', 'Farrapos', 'Farroupilha', 'Floresta',
    'Glória', 'Guarujá', 'Higienópolis', 'Hípica', 'Humaitá',
    'Independência', 'Ipanema', 'Jardim Botânico', 'Jardim Carvalho', 'Jardim do Salso',
    'Jardim Europa', 'Jardim Floresta', 'Jardim Isabel', 'Jardim Itu', 'Jardim Leopoldina',
    'Jardim Lindóia', 'Jardim Planalto', 'Jardim Sabará', 'Jardim São Pedro', 'Lageado',
    'Lami', 'Lomba do Pinheiro', 'Mário Quintana', 'Marcílio Dias', 'Medianeira',
    'Menino Deus', 'Moinhos de Vento', 'Mont Serrat', 'Morro Santana', 'Navegantes',
    'Nonoai', 'Parque Santa Fé', 'Partenon', 'Passo da Areia', 'Passo das Pedras',
    'Pedra Redonda', 'Petrópolis', 'Pitinga', 'Praia de Belas', 'Protásio Alves',
    'Restinga', 'Rio Branco', 'Rubem Berta', 'Santa Cecília', 'Santa Maria Goretti',
    'Santa Rosa de Lima', 'Santa Tereza', 'Santana', 'Santo Antônio', 'São Caetano',
    'São Geraldo', 'São João', 'São José', 'São Sebastião', 'Sarandi',
    'Serraria', 'Sétimo Céu', 'Teresópolis', 'Três Figueiras', 'Tristeza',
    'Umbu', 'Vila Assunção', 'Vila Conceição', 'Vila Ipiranga', 'Vila João Pessoa',
    'Vila Nova', 'Vilas do Almirante Tamandaré'
]

print(f'Total de bairros oficiais de Porto Alegre: {len(bairros_oficiais)}')
print('\nLista completa dos 94 bairros oficiais:')
for i, bairro in enumerate(sorted(bairros_oficiais), 1):
    print(f'{i:2d}. {bairro}')

# Carregar dataset atual
df_atual = pd.read_csv('../data/distributed_crime_data.csv')
# Renomear colunas para compatibilidade
df_atual = df_atual.rename(columns={'bairro': 'Bairro'})
bairros_atuais = set(df_atual['Bairro'].unique())

print(f'\n\nBairros no dataset atual ({len(bairros_atuais)}):')
for bairro in sorted(bairros_atuais):
    print(f'- {bairro}')

# Identificar bairros faltantes
bairros_faltantes = set(bairros_oficiais) - bairros_atuais
print(f'\n\nBairros FALTANTES no dataset ({len(bairros_faltantes)}):')
for bairro in sorted(bairros_faltantes):
    print(f'- {bairro}')

# Verificar se há bairros no dataset que não estão na lista oficial
bairros_extras = bairros_atuais - set(bairros_oficiais)
if bairros_extras:
    print(f'\n\nBairros no dataset que NÃO estão na lista oficial ({len(bairros_extras)}):')
    for bairro in sorted(bairros_extras):
        print(f'- {bairro}')

print(f'\n\nResumo:')
print(f'- Total de bairros oficiais: {len(bairros_oficiais)}')
print(f'- Bairros no dataset atual: {len(bairros_atuais)}')
print(f'- Bairros faltantes: {len(bairros_faltantes)}')
print(f'- Cobertura atual: {len(bairros_atuais)/len(bairros_oficiais)*100:.1f}%')
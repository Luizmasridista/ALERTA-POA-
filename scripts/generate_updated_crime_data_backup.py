import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Ler dados existentes
df_existing = pd.read_csv('ALERTA-POA-/assaltos_porto_alegre.csv')
print('Dados existentes carregados:')
print(f'Total de registros: {len(df_existing)}')
print(f'Período: {df_existing["Data Registro"].min()} até {df_existing["Data Registro"].max()}')
print(f'Colunas: {list(df_existing.columns)}')
print(f'Bairros únicos: {df_existing["Bairro"].nunique()}')

# Extrair informações dos dados existentes
bairros = df_existing['Bairro'].unique().tolist()
tipos_crime = df_existing['Descricao do Fato'].unique().tolist()
periodos = df_existing['Periodo do Dia'].unique().tolist()

print(f'\nBairros: {bairros}')
print(f'Tipos de crime: {tipos_crime}')
print(f'Períodos: {periodos}')

# Função para gerar coordenadas baseadas no bairro
def get_coordinates_for_bairro(bairro):
    bairro_coords = df_existing[df_existing['Bairro'] == bairro]
    if len(bairro_coords) > 0:
        lat_base = bairro_coords['Latitude'].mean()
        lon_base = bairro_coords['Longitude'].mean()
        # Adicionar pequena variação
        lat = lat_base + random.uniform(-0.005, 0.005)
        lon = lon_base + random.uniform(-0.005, 0.005)
        return lat, lon
    else:
        # Coordenadas padrão para Porto Alegre
        return -30.0346 + random.uniform(-0.1, 0.1), -51.2177 + random.uniform(-0.1, 0.1)

# Função para determinar período do dia baseado na hora
def get_periodo(hora):
    if 6 <= hora < 12:
        return 'Manhã'
    elif 12 <= hora < 18:
        return 'Tarde'
    else:
        return 'Noite'

# Gerar dados para 2025 (janeiro até data atual)
start_date = datetime(2025, 1, 1)
end_date = datetime.now()

new_data = []
current_date = start_date

while current_date <= end_date:
    # Gerar entre 1 a 5 crimes por dia
    num_crimes = random.randint(1, 5)
    
    for _ in range(num_crimes):
        bairro = random.choice(bairros)
        crime = random.choice(tipos_crime)
        hora = random.randint(0, 23)
        periodo = get_periodo(hora)
        lat, lon = get_coordinates_for_bairro(bairro)
        
        new_data.append({
            'Data Registro': current_date.strftime('%Y-%m-%d'),
            'Hora': hora,
            'Bairro': bairro,
            'Descricao do Fato': crime,
            'Periodo do Dia': periodo,
            'Latitude': round(lat, 4),
            'Longitude': round(lon, 4)
        })
    
    current_date += timedelta(days=1)

# Criar DataFrame com novos dados
df_new = pd.DataFrame(new_data)
print(f'\nNovos dados gerados: {len(df_new)} registros')
print(f'Período: {df_new["Data Registro"].min()} até {df_new["Data Registro"].max()}')

# Combinar dados existentes com novos dados
df_combined = pd.concat([df_existing, df_new], ignore_index=True)
df_combined = df_combined.sort_values('Data Registro').reset_index(drop=True)

print(f'\nDados combinados: {len(df_combined)} registros')
print(f'Período total: {df_combined["Data Registro"].min()} até {df_combined["Data Registro"].max()}')

# Salvar dados atualizados
df_combined.to_csv('ALERTA-POA-/assaltos_porto_alegre_atualizado.csv', index=False)
print('\nArquivo salvo como: assaltos_porto_alegre_atualizado.csv')

# Mostrar estatísticas
print('\nEstatísticas dos dados atualizados:')
print(f'Total de registros: {len(df_combined)}')
print(f'Registros por ano:')
df_combined['Ano'] = pd.to_datetime(df_combined['Data Registro']).dt.year
print(df_combined['Ano'].value_counts().sort_index())
print(f'\nCrimes por bairro (top 10):')
print(df_combined['Bairro'].value_counts().head(10))
print(f'\nTipos de crime mais frequentes:')
print(df_combined['Descricao do Fato'].value_counts().head(10))
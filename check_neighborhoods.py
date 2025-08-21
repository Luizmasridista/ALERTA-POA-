import pandas as pd

# Carregar dados
df = pd.read_csv('data/distributed_crime_data.csv')

# Verificar bairros únicos
print(f'Total de bairros únicos nos dados: {df["bairro"].nunique()}')
print('\nTodos os bairros únicos:')
for i, bairro in enumerate(sorted(df['bairro'].unique()), 1):
    print(f'{i:2d}. {bairro}')

# Verificar se há dados para cada bairro
print('\nContagem de registros por bairro (top 20):')
bairro_counts = df['bairro'].value_counts().head(20)
for bairro, count in bairro_counts.items():
    print(f'{bairro}: {count} registros')
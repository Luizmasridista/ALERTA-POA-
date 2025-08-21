import pandas as pd

# Carregar o dataset atual
df = pd.read_csv('../data/distributed_crime_data.csv')
# Renomear colunas para compatibilidade
df = df.rename(columns={
    'data': 'Data Registro',
    'bairro': 'Bairro',
    'tipo_crime': 'Descricao do Fato'
})

# Analisar bairros únicos
bairros_unicos = df['Bairro'].unique()
print(f'Total de bairros únicos no dataset: {len(bairros_unicos)}')
print('\nBairros incluídos:')
for bairro in sorted(bairros_unicos):
    print(f'- {bairro}')

print(f'\nTotal de registros: {len(df)}')

# Analisar distribuição por bairro
print('\nDistribuição de crimes por bairro:')
distribuicao = df['Bairro'].value_counts()
for bairro, count in distribuicao.head(10).items():
    print(f'{bairro}: {count} registros')

# Verificar colunas disponíveis
print('\nColunas disponíveis no dataset:')
for col in df.columns:
    print(f'- {col}')

# Verificar tipos de crime se a coluna existir
if 'Tipo' in df.columns:
    print('\nTipos de crime incluídos:')
    tipos = df['Tipo'].unique()
    for tipo in sorted(tipos):
        print(f'- {tipo}')
elif 'Crime' in df.columns:
    print('\nTipos de crime incluídos:')
    tipos = df['Crime'].unique()
    for tipo in sorted(tipos):
        print(f'- {tipo}')
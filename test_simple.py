import streamlit as st
import pandas as pd
from modules import data_loader

# Configuração da página
st.set_page_config(
    page_title="Teste Simples - Alerta POA",
    page_icon="🚨",
    layout="wide"
)

def main():
    st.title("🚨 Teste Simples - Alerta POA")
    
    try:
        # Carregar dados
        st.write("Carregando dados...")
        df = data_loader.load_data()
        
        st.write(f"✅ Dados carregados com sucesso: {len(df)} registros")
        
        if not df.empty:
            st.write("📊 Primeiras 5 linhas dos dados:")
            st.dataframe(df.head())
            
            st.write("📈 Informações básicas:")
            st.write(f"- Total de registros: {len(df)}")
            st.write(f"- Colunas: {list(df.columns)}")
        else:
            st.error("❌ Nenhum dado foi carregado")
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
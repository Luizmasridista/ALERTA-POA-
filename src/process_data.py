
import pandas as pd

def load_and_preprocess_data(file_path):
    df = pd.read_csv(file_path, sep=\";\
    df.columns = [\"Data Registro\", \"Descricao do Fato\", \"Municipio do Fato\", \"Tipo de Ocorrencia\"]
    
    # Filtrar por Porto Alegre
    df_poa = df[df[\"Municipio do Fato\"] == \"Porto Alegre\"]
    
    # Converter \"Data Registro\" para datetime
    df_poa[\"Data Registro\"] = pd.to_datetime(df_poa[\"Data Registro\"])
    
    # Filtrar por assaltos (roubos)
    assault_keywords = [\"ROUBO\", \"ASSALTO\"]
    df_assaltos = df_poa[df_poa[\"Descricao do Fato\"]
    
    # Extrair hora e categorizar
    df_assaltos[\"Hora\"] = df_assaltos[\"Data Registro\"]
    def categorize_time(hour):
        if 0 <= hour < 6:
            return \"Madrugada\"
        elif 6 <= hour < 12:
            return \"Manhã\"
        elif 12 <= hour < 18:
            return \"Tarde\"
        else:
            return \"Noite\"
    df_assaltos[\"Periodo do Dia\"] = df_assaltos[\"Hora\"]
    
    # Mapeamento de meses e dias da semana para português
    month_mapping = {
        1: \"Janeiro\", 2: \"Fevereiro\", 3: \"Março\", 4: \"Abril\",
        5: \"Maio\", 6: \"Junho\", 7: \"Julho\", 8: \"Agosto\",
        9: \"Setembro\", 10: \"Outubro\", 11: \"Novembro\", 12: \"Dezembro\"
    }
    day_mapping = {
        0: \"Segunda-feira\", 1: \"Terça-feira\", 2: \"Quarta-feira\",
        3: \"Quinta-feira\", 4: \"Sexta-feira\", 5: \"Sábado\", 6: \"Domingo\"
    }
    
    df_assaltos[\"Mes\"] = df_assaltos[\"Data Registro\"]
    df_assaltos[\"Dia da Semana\"] = df_assaltos[\"Data Registro\"]
    
    return df_assaltos

if __name__ == \"__main__\":


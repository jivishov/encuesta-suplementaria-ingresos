import streamlit as st
from mitosheet.streamlit.v1 import spreadsheet
import mitosheet
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")

st.title("Ingresos en Chile")

st.markdown("A continuación se presentan los datos de la Encuesta Suplementaria de Ingresos que puedes descargar desde [este enlace]('https://www.ine.gob.cl/estadisticas/sociales/ingresos-y-gastos/encuesta-suplementaria-de-ingresos'). Hemos seleccionado sólo las columnas relevantes para esta aplicación pero puedes descargar aquí la encuesta completa seleccionando 'Import' y luego 'Import Files'.")

st.markdown("Sigue las instrucciones para obtener el ingreso medio de las personas ocupadas en Chile.")

CSV_URL = "https://raw.githubusercontent.com/alonsosilvaallende/encuesta-suplementaria-ingresos/main/data/esi-2022---personas.csv"
#CSV_URL = 'https://raw.githubusercontent.com/plotly/datasets/master/tesla-stock-price.csv'
#df, code = spreadsheet(CSV_URL, encoding="ISO-8859-1", low_memory=False, index_col=0)
@st.cache_data
def get_data(url):
    data = pd.read_csv(CSV_URL, encoding="ISO-8859-1", low_memory=False, index_col=0)
    data = data[["ing_t_p", "fact_cal_esi", "ocup_ref", "sexo", "region"]]
    return data

data = get_data(CSV_URL)

df, code = spreadsheet(data, import_folder="./data")
#df, code = spreadsheet(import_folder="./data")

data['ingreso_ponderado'] = data['ing_t_p'] * data['fact_cal_esi']

CHECKS_AND_ERRORS = [
    (
        lambda df: (df["ocup_ref"].isnull().sum() > 0),
        '(1/9) Por favor selecciona sólo las personas ocupadas con más de 1 mes en el empleo actual.',
        "Para hacerlo selecciona el ícono de filtro de la columna 'ocup_ref', y luego agrega el filtro '=' a 1."
    ),
    (
        lambda df: len(df.columns) < 6,
        "(2/9) Por favor agrega una nueva columna.",
        "Para hacerlo selecciona la columna 'region' y haz click en 'Add Col' en el menú."
    ),
    (
        lambda df: "ingreso_ponderado" not in list(df.columns),
        "(3/9) Cambia el nombre de la nueva columna a 'ingreso_ponderado'.",
        "Para hacerlo haz doble click en el nombre de la columna."
    ),
    (
        lambda df: df.iloc[0,5] != data.iloc[0,0]*data.iloc[0,1],
        "(4/9) Agrega el ingreso ponderado por el factor de expansión.",
        "Para hacerlo agrega la ecuación '=ing_t_p1*fact_cal_esi1' en la célula 1 de la nueva columna ingreso_ponderado."
    ),
    (
        lambda df: len(df.columns) < 7,
        "(5/9) Por favor agrega una nueva columna.",
        "Para hacerlo selecciona la columna 'ingreso_ponderado' y haz click en 'Add Col' en el menú."
    ),
    (
        lambda df: "resultados" not in list(df.columns),
        "(6/9) Cambia el nombre de la nueva columna a 'resultados'.",
        "Para hacerlo haz doble click en el nombre de la columna."
    ),
    (
        lambda df: np.round(df.iloc[0,6]) != np.round(data['ingreso_ponderado'].sum()),
        "(7/9) Calcula el total de ingresos ponderados por el factor de expansión.",
        "Para hacerlo agrega la ecuación '=sum(ingreso_ponderado1\:ingreso_ponderado93103)' y **deselecciona 'Edit entire column'** en la celda 1 de la columna 'resultados'."
    ),
    (
        lambda df: np.round(df.iloc[1,6]) != np.round(data[data["ocup_ref"] == 1]["fact_cal_esi"].sum()),
        "(8/9) Calcula el número estimado de personas ocupadas.",
        "Para hacerlo agrega la ecuación '=sum(fact_cal_esi1\:fact_cal_esi93103)' y **deselecciona 'Edit entire column'** en la celda 3 de la columna 'resultados'."
    ),
    (
        lambda df: np.round(df.iloc[2,6]) != np.round(data['ingreso_ponderado'].sum()/(data[data["ocup_ref"] == 1]["fact_cal_esi"].sum())),
        "(9/9) Calcula el ingreso promedio mensual en Chile.",
        "Para hacerlo agrega la ecuación '=resultados1/resultados3' y **deselecciona 'Edit entire column'** en la celda 5 de la columna 'resultados'."
    ),
]

def run_data_checks_and_display_prompts(df):
    """
    Runs the data checks and displays prompts for the user to fix the data.
    """
    for check, error_message, help in CHECKS_AND_ERRORS:
        if check(df):
            st.error(error_message + " " + help)
            return False
    return True

df = list(df.values())[0]
checks_passed = run_data_checks_and_display_prompts(df)

def ingreso_promedio(data):
    n_ocupados = data['fact_cal_esi'].sum()
    promedio = (data['ing_t_p']*data['fact_cal_esi']).sum()/n_ocupados
    return int(np.round(promedio))

if checks_passed:
    n_ocupados = df["fact_cal_esi"].sum()
    st.success('Felicitaciones! Lo lograste!', icon="✅")
    st.write(f"El número de personas ocupadas en Chile es: {n_ocupados:,.0f}".replace(',','.'))
    st.write(f"El ingreso medio mensual de los ocupados en Chile es: ${ingreso_promedio(df):,.0f}".replace(',','.'))
    st.write(f"El código Python que generaste para obtener esos resultados es el siguiente:")

#st.write(df)
st.code(code)

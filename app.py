
from ast import operator
from operator import index
import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

# Přidání stylu pro zvětšení šířky datového rámce
st.markdown(
    """
    <style>
    .css-1ex1afd {  /* Identifikátor může být jiný, záleží na verzi Streamlit */
        width: 1200px !important;  /* Nastavení šířky dle potřeby */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load the data
def load_data():
    df = pd.read_csv("scraped.csv")
    return df

table = load_data().copy()

import calendar
from datetime import datetime

# Vytvoreni slovniku pro prevod zkratky mesice na cislo mesice
month_to_num = {month: index for index, month in enumerate(calendar.month_abbr) if month}

def transform_date_corrected(date_str):
    try:
        # Rozdeleni retezce na mesic a rozmezi dni
        parts = date_str.split()
        month_str = parts[0][:-1]  # Odstraneni tecky z nazvu mesice
        days_range = parts[1]

        # Převedení názvu měsíce na číslo
        month_number = month_to_num[month_str[:3].capitalize()]

        # Vyber posledniho dne z rozmezi
        last_day = int(days_range.split('-')[1])

        # Vytvoreni noveho datumoveho retezce
        new_date = f"{last_day}. {month_number}."
        return new_date
    except Exception as e:
        # Pokud format neni spravny, vrat puvodni retezec
        return date_str


# Aplikace opravene transformace na sloupec 'Date'
table['Date'] = table['Date'].apply(transform_date_corrected)
table.rename(columns={"Date":"Datum"},inplace=True)

table = table[["Datum","Candidate 1","Percentage 1","Percentage 3","Candidate 3","Pollster","Sample","Sample Type"]]

# Přidání mezery mezi číslo a symbol procenta
table['Percentage 1'] = table['Percentage 1'].apply(lambda x: x[:-1])
table['Percentage 3'] = table['Percentage 3'].apply(lambda x: x[:-1])

# Převod hodnot na řetězce a přidání " %"
table["Percentage 1"] = table["Percentage 1"].astype(str) + " %"
table["Percentage 3"] = table["Percentage 3"].astype(str) + " %"

# Změna formátu sloupce "Sample" z "1,906" na "1 906"
table["Sample"] = table["Sample"].str.replace(',', ' ')

table.rename(columns={"Percentage 1":"Harris","Percentage 3":"Trump"},inplace=True)
table = table[["Datum","Harris","Trump","Pollster","Sample","Sample Type"]]

table['Sample Type'] = table['Sample Type'].replace({'LV': 'pravděpodobní voliči', 'RV': 'registrovaní voliči', 'A': 'dospělá populace'})
table["Agentura"] = table["Pollster"] + " (" + table["Sample"] + " resp., " + table["Sample Type"] + " )"

table = table[["Datum","Harris","Trump","Agentura"]]

# Funkce pro modrou barvu
def color_percentage_blue(val, max_intensity=255):
    percentage = int(val.strip(' %'))
    intensity = max_intensity - int((percentage / 100) ** 2 * max_intensity)
    color = f'rgb({intensity}, {intensity}, 255)'  # Světlejší modrá pro vyšší procenta
    return f'background-color: {color}; color: white; text-align: center;'

# Funkce pro červenou barvu
def color_percentage_red(val, max_intensity=255):
    percentage = int(val.strip(' %'))
    intensity = max_intensity - int((percentage / 100) ** 2 * max_intensity)
    color = f'rgb(255, {intensity}, {intensity})'  # Světlejší červená pro vyšší procenta
    return f'background-color: {color}; color: white; text-align: center;'

# Nastavení maximální intenzity pro modrou a červenou
max_blue_intensity = 140
max_red_intensity = 140


# Použití stylování na DataFrame
styled_table = table.style.applymap(lambda x: color_percentage_blue(x, max_intensity=max_blue_intensity), subset=['Harris'])\
                          .applymap(lambda x: color_percentage_red(x, max_intensity=max_red_intensity), subset=['Trump'])



st.title("Předvolební průzkumy v USA")
st.text("")
harris_column = st.column_config.TextColumn(label="Harris", width="small")
trump_column = st.column_config.TextColumn(label="Trump", width="small")
pollster_column = st.column_config.TextColumn(label="Agentura",width="large")

st.dataframe(styled_table,hide_index=True,column_config={"Harris": harris_column,
                                                  "Trump": trump_column,"Agentura":pollster_column},height=500)

import datetime
# Získání aktuálního data
dnesni_datum = datetime.date.today().strftime("%d.%m.%Y")  # Formátování data na formát DD.MM.YYYY

st.markdown(f'<span style="font-size: 14px">**Zdroj:** fivethirtyeight.com | **Data:** k {dnesni_datum} | **Autor:** lig </span>', unsafe_allow_html=True)



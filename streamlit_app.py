import streamlit as st
import folium
from streamlit_folium import st_folium
import gzip
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import plotly.express as px


APP_TITLE = "Statistiques immobilières"
APP_SUB_TITLE = "Source : DVF (etat francais)"

#chargement données cadastrales
with gzip.open('./cadastre/cadastre-95-communes.json.gz', 'rb') as f:
    geo_cadastre_commune = json.loads(f.read().decode("utf-8"))

# Chargement données Valeurs Foncieres
df95_2022 = pd.read_csv("./cleaned_datasets/2022_95_DVF_cleaned.csv", low_memory=False)
df95_2021 = pd.read_csv("./cleaned_datasets/2021_95_DVF_cleaned.csv", low_memory=False)
df95_2020 = pd.read_csv("./cleaned_datasets/2020_95_DVF_cleaned.csv", low_memory=False)
df95_2019 = pd.read_csv("./cleaned_datasets/2019_95_DVF_cleaned.csv", low_memory=False)
df95_2018 = pd.read_csv("./cleaned_datasets/2018_95_DVF_cleaned.csv", low_memory=False)

df95_2022['Date mutation'] = pd.to_datetime(df95_2022['Date mutation'], format="%Y-%m-%d", dayfirst=True)
df95_2021['Date mutation'] = pd.to_datetime(df95_2021['Date mutation'], format="%Y-%m-%d", dayfirst=True)
df95_2020['Date mutation'] = pd.to_datetime(df95_2020['Date mutation'], format="%Y-%m-%d", dayfirst=True)
df95_2019['Date mutation'] = pd.to_datetime(df95_2019['Date mutation'], format="%Y-%m-%d", dayfirst=True)
df95_2018['Date mutation'] = pd.to_datetime(df95_2018['Date mutation'], format="%Y-%m-%d", dayfirst=True)

df95_2022['code_insee'] = df95_2022["Code departement"].astype(str) + df95_2022["Code commune"].astype(str).str.zfill(3)
df95_2021['code_insee'] = df95_2021["Code departement"].astype(str) + df95_2021["Code commune"].astype(str).str.zfill(3)
df95_2020['code_insee'] = df95_2020["Code departement"].astype(str) + df95_2020["Code commune"].astype(str).str.zfill(3)
df95_2019['code_insee'] = df95_2019["Code departement"].astype(str) + df95_2019["Code commune"].astype(str).str.zfill(3)
df95_2018['code_insee'] = df95_2018["Code departement"].astype(str) + df95_2018["Code commune"].astype(str).str.zfill(3)

df95_2022["surface_totale"] = df95_2022.groupby('id_vente')['Surface reelle bati'].transform('sum')
df95_2021["surface_totale"] = df95_2021.groupby('id_vente')['Surface reelle bati'].transform('sum')
df95_2020["surface_totale"] = df95_2020.groupby('id_vente')['Surface reelle bati'].transform('sum')
df95_2019["surface_totale"] = df95_2019.groupby('id_vente')['Surface reelle bati'].transform('sum')
df95_2018["surface_totale"] = df95_2018.groupby('id_vente')['Surface reelle bati'].transform('sum')

df95_2022["prix_m2"] = df95_2022["Valeur fonciere"]/df95_2022["surface_totale"]
df95_2021["prix_m2"] = df95_2021["Valeur fonciere"]/df95_2021["surface_totale"]
df95_2020["prix_m2"] = df95_2020["Valeur fonciere"]/df95_2020["surface_totale"]
df95_2019["prix_m2"] = df95_2019["Valeur fonciere"]/df95_2019["surface_totale"]
df95_2018["prix_m2"] = df95_2018["Valeur fonciere"]/df95_2018["surface_totale"]

# Valeur foncière moyenne pour chaque commune
df_95_2022_meanVF = df95_2022.groupby("id_vente").first().groupby("code_insee")["Valeur fonciere"].median()
df_95_2022_dept_meanVF = df95_2022.groupby("id_vente").first().groupby("Code departement")["Valeur fonciere"].median()




def get_nom_ville(code_insee):
    ville = ""
    for feature in geo_cadastre_commune["features"]:
        if feature["properties"]["id"] == code_insee:
            ville = feature["properties"]["nom"]
            break
    return ville

def get_plot_trade_monthly_commune(code_insee):
    
    st.subheader("Évolution du nombre de transactions par mois")

    # Group transactions by month and count the number of transactions for each month
    transactions_par_mois_2019 = df95_2019[df95_2019["code_insee"] == code_insee].groupby(df95_2019['Date mutation'].dt.month).size()
    transactions_par_mois_2022 = df95_2022[df95_2022["code_insee"] == code_insee].groupby(df95_2022['Date mutation'].dt.month).size()

    # Create a Plotly Express line plot
    fig = px.line()
    
    # Add lines for each year
    fig.add_scatter(x=transactions_par_mois_2019.index, y=transactions_par_mois_2019, name='Transactions en 2019')
    fig.add_scatter(x=transactions_par_mois_2022.index, y=transactions_par_mois_2022, name='Transactions en 2022')

    # Set labels and title
    fig.update_layout(xaxis_title='Mois', yaxis_title='Nombre de transactions')

    # Show the plot
    st.plotly_chart(fig)

def get_plot_trade_monthly_dept(code_dept):

    st.subheader("Évolution du nombre de transactions par mois")

    # Group transactions by month and count the number of transactions for each month
    transactions_par_mois_2019 = df95_2019[df95_2019["Code departement"] == code_dept].groupby(df95_2019['Date mutation'].dt.month).size()
    transactions_par_mois_2022 = df95_2022[df95_2022["Code departement"] == code_dept].groupby(df95_2022['Date mutation'].dt.month).size()

    # Create a Plotly Express line plot
    fig = px.line()
    
    # Add lines for each year
    fig.add_scatter(x=transactions_par_mois_2019.index, y=transactions_par_mois_2019, name='Transactions en 2019')
    fig.add_scatter(x=transactions_par_mois_2022.index, y=transactions_par_mois_2022, name='Transactions en 2022')

    # Set labels and title
    fig.update_layout(xaxis_title='Mois', yaxis_title='Nombre de transactions')

    # Show the plot
    st.plotly_chart(fig)
   
def get_plot_type_distribution_commune(code_insee):

    st.subheader("Répartition des ventes selon le type")

    # Crée une liste des types de biens uniques dans le dataframe
    types = df95_2022["type_global"].unique()

    # Initialise le dictionnaire avec des valeurs nulles pour chaque type de bien
    nb_per_type_2019 = {t: 0 for t in types}
    nb_per_type_2022 = {t: 0 for t in types}

    # Compte le nombre de ventes pour chaque type de bien (inclus aussi vente avec plusieurs parcelles)
    for t in types:
        nb_per_type_2022[t] = len(df95_2022[(df95_2022["type_global"]==t) & (df95_2022["code_insee"]==code_insee)].groupby("id_vente").first())
        nb_per_type_2019[t] = len(df95_2019[(df95_2019["type_global"]==t) & (df95_2019["code_insee"]==code_insee)].groupby("id_vente").first())

    # Trie les clés du dictionnaire en fonction de leurs valeurs
    sorted_keys_2019 = sorted(nb_per_type_2019, key=nb_per_type_2019.get)
    sorted_keys_2022 = sorted(nb_per_type_2022, key=nb_per_type_2022.get)

    # Crée le graphique avec Plotly
    fig = px.bar()
    fig.add_bar(x=sorted_keys_2019, y=[nb_per_type_2019[k] for k in sorted_keys_2019], name='Transactions en 2019')
    fig.add_bar(x=sorted_keys_2022, y=[nb_per_type_2022[k] for k in sorted_keys_2022], name='Transactions en 2022')
    fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':sorted_keys_2019}, 
                      xaxis_tickangle=-45,
                      yaxis_title='Nombre de transactions par type')
    
    # Affiche le graphique dans Streamlit
    st.plotly_chart(fig)

def get_plot_type_distribution_dept(code_dept):
    
    st.subheader("Répartition des ventes selon le type")

    # Crée une liste des types de biens uniques dans le dataframe
    types = df95_2022["type_global"].unique()

    # Initialise le dictionnaire avec des valeurs nulles pour chaque type de bien
    nb_per_type_2019 = {t: 0 for t in types}
    nb_per_type_2022 = {t: 0 for t in types}

    # Compte le nombre de ventes pour chaque type de bien (inclus aussi vente avec plusieurs parcelles)
    for t in types:
        nb_per_type_2022[t] = len(df95_2022[(df95_2022["type_global"]==t) & (df95_2022["Code departement"]==code_dept)].groupby("id_vente").first())
        nb_per_type_2019[t] = len(df95_2019[(df95_2019["type_global"]==t) & (df95_2019["Code departement"]==code_dept)].groupby("id_vente").first())

    # Trie les clés du dictionnaire en fonction de leurs valeurs
    sorted_keys_2019 = sorted(nb_per_type_2019, key=nb_per_type_2019.get)
    sorted_keys_2022 = sorted(nb_per_type_2022, key=nb_per_type_2022.get)

    # Crée le graphique avec Plotly
    fig = px.bar()
    fig.add_bar(x=sorted_keys_2019, y=[nb_per_type_2019[k] for k in sorted_keys_2019], name='Transactions en 2019')
    fig.add_bar(x=sorted_keys_2022, y=[nb_per_type_2022[k] for k in sorted_keys_2022], name='Transactions en 2022')
    fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':sorted_keys_2019}, 
                      xaxis_tickangle=-45,
                      yaxis_title='Nombre de transactions par type')
    
    # Affiche le graphique dans Streamlit
    st.plotly_chart(fig)

def get_plot_price_distribution_commune(code_insee, type="Maison"):

    st.subheader("Distribution des prix de vente de maisons")

    transactions_maison_2019 = df95_2019[(df95_2019["Type local"]==type) & (df95_2019["code_insee"]==code_insee)].groupby("id_vente").first()["Valeur fonciere"]
    transactions_maison_2022 = df95_2022[(df95_2022["Type local"]==type) & (df95_2022["code_insee"]==code_insee)].groupby("id_vente").first()["Valeur fonciere"]

    # Concaténer les deux séries de données avec l'année correspondante
    df_combined = pd.concat([
        pd.DataFrame({'Prix de vente': transactions_maison_2019, 'Année': '2019'}),
        pd.DataFrame({'Prix de vente': transactions_maison_2022, 'Année': '2022'})
    ])

    # Créer l'histogramme avec Plotly Express
    fig = px.histogram(
        df_combined,
        x='Prix de vente',
        color='Année',
        nbins=15,
        opacity=0.5,
        labels={'x': 'Prix de vente', 'y': 'Nombre de transactions'}
    )
    fig.update_layout(showlegend=True)

    # Afficher le graphique dans Streamlit
    st.plotly_chart(fig)

def get_plot_price_distribution_dept(code_dept, type="Maison"):

    st.subheader(f'Distribution des prix de vente selon le type')
    st.caption("Veuillez sélectionner un type de produit")

    types = ["Maison", "Appartement", "Local industriel. commercial ou assimilé", "Terrain à bâtir ou en état futur d'achèvement"]
    type = st.selectbox('Type de bien', types, key='type_distribution')

    transactions_maison_2019 = df95_2019[(df95_2019["type_global"]==type) & (df95_2019["Code departement"]==code_dept)].groupby("id_vente").first()["Valeur fonciere"]
    transactions_maison_2022 = df95_2022[(df95_2022["type_global"]==type) & (df95_2022["Code departement"]==code_dept)].groupby("id_vente").first()["Valeur fonciere"]

    # Concaténer les deux séries de données avec l'année correspondante
    df_combined = pd.concat([
        pd.DataFrame({'Prix de vente': transactions_maison_2019, 'Année': '2019'}),
        pd.DataFrame({'Prix de vente': transactions_maison_2022, 'Année': '2022'})
    ])

    # Créer l'histogramme avec Plotly Express
    fig = px.histogram(
        df_combined,
        x='Prix de vente',
        color='Année',
        nbins=60,
        opacity=0.5,
        labels={'x': 'Prix de vente', 'y': 'Nombre de transactions'}
    )
    fig.update_xaxes(range=[0, 1500000])  # Plage des valeurs pour ne pas avoir les grandes valeurs
    fig.update_layout(showlegend=True)

    # Afficher le graphique dans Streamlit
    st.plotly_chart(fig)

def get_plot_type_average_price_commune(code_insee):

    st.subheader(f'Comparaison des prix de ventes moyen pour chaque type par année')

    # Computation of the mean
    years = [2018, 2019, 2020, 2021, 2022]
    types = ["Maison", "Appartement", "Local industriel. commercial ou assimilé", "Terrain à bâtir ou en état futur d'achèvement"]

    average_price_type = {}
    for t in types:
        average_price_type[t] = []
        for year in years:
            df_year = globals()[f"df95_{year}"]
            values = df_year[(df_year["type_global"] == t) & (df_year["code_insee"] == code_insee)].groupby("id_vente").first()["Valeur fonciere"].values
            average_price_type[t].append(np.mean(values))

    # Create a DataFrame for the plot
    data = {"Year": years}
    data.update(average_price_type)
    df = pd.DataFrame(data)

    # Plot using Plotly Express
    fig = px.line(df, x="Year", y=types)
    fig.update_layout(yaxis_tickformat="%d")

    # Add dropdown buttons for type selection
    for t in types:
        fig.update_traces(visible=False, selector=dict(name=t))

    buttons = []
    for i, t in enumerate(types):
        visible = [False] * len(types)
        visible[i] = True
        button = dict(label=t, method="update", args=[{"visible": visible}, {"title": f"Comparaison des prix de ventes moyen pour {t} par année"}])
        buttons.append(button)

    fig.update_layout(updatemenus=[dict(active=0, buttons=buttons)])

    # Afficher le graphique dans Streamlit
    st.plotly_chart(fig)

def get_plot_type_median_price_dept(code_dept):

    st.subheader("Comparaison des prix de ventes médian pour chaque type par année")

    # Computation of the mean
    years = [2018, 2019, 2020, 2021, 2022]
    types = ["Maison", "Appartement", "Local industriel. commercial ou assimilé", "Terrain à bâtir ou en état futur d'achèvement"]

    average_price_type = {}
    for t in types:
        average_price_type[t] = []
        for year in years:
            df_year = globals()[f"df95_{year}"]
            values = df_year[(df_year["type_global"] == t) & (df_year["Code departement"] == code_dept)].groupby("id_vente").first()["Valeur fonciere"].values
            average_price_type[t].append(np.median(values))

    # Create a DataFrame for the plot
    data = {"Year": years}
    data.update(average_price_type)
    df = pd.DataFrame(data)

    # Plot using Plotly Express
    fig = px.line(df, x="Year", y=types)
    fig.update_layout(yaxis_tickformat="%d")

    # Afficher le graphique dans Streamlit
    st.plotly_chart(fig)

def display_map_m2(type="Maison"):

    st.subheader("Carte des prix m2 par type et par ville")

    types = ["Maison", "Appartement", "Local industriel. commercial ou assimilé", "Terrain à bâtir ou en état futur d'achèvement"]
    type = st.selectbox('Type de bien', types, key='type_price_m2')

    #valeur prix/m2 pour chaque commune
    df_95_2022_m2VF = df95_2022[df95_2022["type_global"]==type].groupby("id_vente").first().groupby("code_insee")["prix_m2"].median()

    map_m2 = folium.Map(location=[	49.08, 	2.20], zoom_start=10, tiles='CartoDB positron', scrollWheelZoom=False)

    choropleth_m2 = folium.Choropleth(
        geo_data =  geo_cadastre_commune,
        data = df_95_2022_m2VF,
        columns = (df_95_2022_m2VF.index.name, df_95_2022_m2VF.name),
        key_on = 'feature.properties.id',
        highlight=True
    )
    choropleth_m2.geojson.add_to(map_m2)

    # Ajout de la donnée financieres au fichier geoJson Data cadastre commune
    # Parcourir les éléments de data_cadastre["features"]
    for feature in choropleth_m2.geojson.data["features"]:
        ## Obtenir la commune du feature
        commune = feature["properties"]["id"]

        feature["properties"]["valm2_commune_DVF"] = df_95_2022_m2VF[commune] if commune in df_95_2022_m2VF else 0

    choropleth_m2.geojson.add_child(
        folium.features.GeoJsonTooltip(fields=['id', 'nom', "valm2_commune_DVF"],
                                       aliases=['Code insee', 'Nom', "Prix de vente médian m2"],
                                       localize=True)
    )

    st_map = st_folium(map_m2, width=700, height=450)

def display_map():
    map = folium.Map(location=[	49.08, 	2.20], zoom_start=10, tiles='CartoDB positron')

    choropleth = folium.Choropleth(
        geo_data =  geo_cadastre_commune,
        data = df_95_2022_meanVF,
        columns = (df_95_2022_meanVF.index.name, df_95_2022_meanVF.name),
        key_on = 'feature.properties.id',
        highlight=True
    )
    choropleth.geojson.add_to(map)

    # Ajout de la donnée financieres au fichier geoJson Data cadastre commune
    # Parcourir les éléments de data_cadastre["features"]
    for feature in choropleth.geojson.data["features"]:
        ## Obtenir la commune du feature
        commune = feature["properties"]["id"]

        feature["properties"]["val_commune_DVF"] = df_95_2022_meanVF[commune] if commune in df_95_2022_meanVF else 0

    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(fields=['id', 'nom', "val_commune_DVF"],
                                       aliases=['Code insee', 'Nom', "Prix de vente médian"],
                                       localize=True)
    )

    st_map = st_folium(map, width=700, height=450)

    code_insee=""
    if st_map['last_active_drawing']:
        code_insee = st_map['last_active_drawing']['properties']['id']
    return code_insee


def main():
    st.set_page_config(page_title=APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)


    #DISPLAY FILTERS AND MAP
    #avec la carte
    code_insee = display_map()

    ##Avec la side bar
    #code_insee_list = list(df95_2022['code_insee'].unique())
    #code_insee_list.insert(0, "Null")  # Ajouter l'option "Null" car sinon probleme sur la sidebar
    #code_insee_list.sort()
    #selected_code_insee = st.sidebar.selectbox('Code INSEE', code_insee_list)
    #if selected_code_insee:
    #    code_insee = selected_code_insee

    #if not code_insee:
    #    code_insee_list = list(df95_2022['code_insee'].unique())
    #    code_insee_list.sort()
    #    code_insee = st.sidebar.selectbox('Code insee', code_insee_list)


    #DISPLAY METRICS

    #si pas de selection sur la carte   ffiche les stats du 95
    if not code_insee:
        st.subheader(f"STATISTIQUES DVF 95")

        get_plot_trade_monthly_dept(95)
        get_plot_type_distribution_dept(95)
        get_plot_price_distribution_dept(95, type="Maison")
        get_plot_type_median_price_dept(95)
        display_map_m2()

    else:

        st.subheader(f"{get_nom_ville(code_insee)}")

        get_plot_trade_monthly_commune(code_insee)
        get_plot_type_distribution_commune(code_insee)
        get_plot_price_distribution_commune(code_insee, type="Maison")
        get_plot_type_average_price_commune(code_insee)




if __name__ == "__main__":
    main()

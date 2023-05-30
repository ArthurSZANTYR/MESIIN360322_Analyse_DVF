import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)

######PARAMETERS#######
file = "https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20230405-160733/valeursfoncieres-2022.txt"
year = 2022
#######################

def cleaning(code_dpt, file, year):
  df = pd.read_csv(file, sep="|")
  
  # Convertir la colonne 'Date' en format de date
  df['Date mutation'] = pd.to_datetime(df['Date mutation'], dayfirst=True)

  ## Sélectionner les lignes ayant un code département égal à code_dpt
  #df = df.loc[df['Code departement'] == code_dpt]

  #on a besoin de regrouper les ventes qui contiennent plusieurs parcelle -> on crée une column id_vente
  #-> on les trie par ordre croissant puis les regrpupe sous le meme index si meme date/prix/code commune

  # Supprimer les lignes contenant des NaN dans la colonne 'date''prix et 'code commune
  df = df.dropna(subset=['Date mutation', 'Valeur fonciere', 'Code commune'])

  # Tri du dataframe par ordre chronologique croissant
  df = df.sort_values('Date mutation', ascending=True)

  # Création de la nouvelle colonne "id_vente" qui prend des valeurs uniques pour chaque transaction
  prev_commune = None
  prev_mutation = None
  prev_price = None
  sequence = 1
  sequences = []
  for index, row in df.iterrows():
      if (row['Date mutation'] == prev_mutation) and (row['Valeur fonciere'] == prev_price) and (row['Code commune'] == prev_commune):
          sequence=sequence
      else:
        sequence+=1

      sequences.append(sequence)
      prev_mutation = row['Date mutation']
      prev_price = row['Valeur fonciere']
      prev_commune = row['Code commune']
  df['id_vente'] = sequences

  # Création de la nouvelle colonne "type_global" qui donne pour valeur "appartement/maison/local comercial/ensemble immobilier"
  df['type_global'] = 'ensemble immobilier'
  for id_vente, vente in df.groupby('id_vente'):
      nb_maison = vente[vente['Type local']=='Maison']['Type local'].count()
      nb_appartement = vente[vente['Type local']=='Appartement']['Type local'].count()
      nb_commercial = vente[vente['Type local']=='Local industriel. commercial ou assimilé']['Type local'].count()
      nb_bien_principal = nb_maison + nb_appartement + nb_commercial

      if nb_bien_principal == 0:
        df.loc[vente.index, 'type_global'] = 'Autre'
      elif nb_bien_principal >1:
        df.loc[vente.index, 'type_global'] = 'Ensemble immobilier'
      elif nb_maison == 1:
        df.loc[vente.index, 'type_global'] = 'Maison'
      elif nb_appartement == 1:
        df.loc[vente.index, 'type_global'] = 'Appartement'
      elif nb_commercial == 1:
        df.loc[vente.index, 'type_global'] = 'Local industriel. commercial ou assimilé'

  #classement de terrain a a batir et Vente en l'état futur d'achèvement dans le type global Terrain
  mask = df['Nature mutation'].isin(["Vente terrain à bâtir", "Vente en l'état futur d'achèvement"])
  df.loc[mask, 'type_global'] = "Terrain à bâtir ou en état futur d'achèvement"

  df = df.drop(df[df["type_global"]=="Autre"].index)

  # Convertir la colonne "Valeur fonciere" en nombre flottant en remplaçant la virgule par un point
  df["Valeur fonciere"] = df["Valeur fonciere"].str.replace(",", ".").astype(float)

  #Créer la colonne code insee
  df['code_insee'] = (df["Code departement"].astype(str) + df["Code commune"].astype(str).str.zfill(3)).astype(int)

  ##supprimer les outliers

  # Calculez le premier quartile (Q1) et le troisième quartile (Q3)
  Q1 = df95_2022["Valeur fonciere"].quantile(0.10)
  Q3 = df95_2022["Valeur fonciere"].quantile(0.90)

  # Calculez la plage interquartile (IQR)
  IQR = Q3 - Q1

  # Calculez les limites inférieure et supérieure pour détecter les outliers
  lower_bound = Q1 - 1.5 * IQR
  upper_bound = Q3 + 1.5 * IQR

  # Filtrez le DataFrame pour exclure les outliers
  df95_2022 = df95_2022[(df95_2022["Valeur fonciere"] >= lower_bound) & (df95_2022["Valeur fonciere"] <= upper_bound)]


  # save to csv
  csv_path = '/cleaned_dataset/' + f'{year}_DVF_cleaned.csv'
  df.to_csv(csv_path, index=True)



#####RUN######
cleaning(code_dpt=None, file = file, year = year)

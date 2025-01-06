import base64
import requests
import csv
import datetime
import os
import pandas as pd

# Configurations
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URL = "https://digital.iservices.rte-france.com/token/oauth"
DATA_URL = "https://digital.iservices.rte-france.com/open_api/wholesale_market/v2/france_power_exchanges"
CSV_FILE = "marche_spot.csv"

def get_token(client_id, client_secret):
    """Génère un token via l'API de RTE en utilisant l'authentification Basic."""
    # Encoder le client_id et client_secret en Base64
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    # Headers de la requête
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Corps de la requête
    payload = {
        "grant_type": "client_credentials"
    }

    # Effectuer la requête POST
    response = requests.post(TOKEN_URL, headers=headers, data=payload)

    # Vérifier la réponse
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Erreur lors de la génération du token : {response.status_code} - {response.text}")

    
def fetch_data(token):
    """Récupère les données du marché spot via l'API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    params = {"start_date": f"{today}T00:00:00+02:00", "end_date": f"{today}T23:59:59+02:00"}
    response = requests.get(DATA_URL, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if "france_power_exchanges" in data and len(data["france_power_exchanges"]) > 0:
            # Accéder aux valeurs dans le premier élément de "france_power_exchanges"
            values = data["france_power_exchanges"][0]["values"]
            if len(values) > 0:
                return values
            else:
                print("Aucune donnée disponible pour aujourd'hui.")
                return []
        else:
            print("Aucune donnée disponible dans la réponse JSON.")
            return []
    else:
        raise Exception(f"Erreur lors de la récupération des données : {response.status_code} - {response.text}")


def save_to_csv(data, file_path):
    """Sauvegarde les données dans un fichier CSV en évitant les doublons."""
    file_exists = os.path.isfile(file_path)

    # Charger les données existantes si le fichier existe
    existing_data = []
    if file_exists:
        existing_data = pd.read_csv(file_path).to_dict('records')

    # Convertir les données actuelles en un format comparable
    existing_set = {(row["start_date"], row["end_date"]) for row in existing_data}

    # Ajouter uniquement les nouvelles lignes
    new_rows = [
        [entry["start_date"], entry["end_date"], entry["value"], entry["price"]]
        for entry in data
        if (entry["start_date"], entry["end_date"]) not in existing_set
    ]

    if new_rows:
        with open(file_path, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(["start_date", "end_date", "value", "price"])  # Écrire l'en-tête
            writer.writerows(new_rows)  # Écrire les nouvelles lignes
        print(f"{len(new_rows)} nouvelles lignes ajoutées au fichier {file_path}.")
    else:
        print("Aucune nouvelle donnée à ajouter.")


def main():
    try:
        # Génération du token
        token = get_token(CLIENT_ID, CLIENT_SECRET)
        print("Token généré avec succès.")

        # Récupération des données
        data = fetch_data(token)
        print("Données récupérées avec succès.")

        # Sauvegarde dans un fichier CSV
        save_to_csv(data, CSV_FILE)
        print(f"Données enregistrées dans le fichier {CSV_FILE}.")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    main()

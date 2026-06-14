import streamlit as st
import requests

# 1. Configuration de la page
st.set_page_config(page_title="OKIABRI", page_icon="💼", layout="wide")

st.title("💼 Okiabri Portefeuille Crypto ")
st.write("Bienvenue sur votre portefeuille.")
st.divider()

# --- FONCTIONS DE DONNÉES ---
def lire_donnees():
    donnees = {}
    try:
        with open("allocations.txt", "r") as fichier:
            for ligne in fichier:
                morceaux = ligne.strip().split(":")
                if len(morceaux) == 2:
                    donnees[morceaux[0]] = float(morceaux[1])
    except FileNotFoundError:
        pass
    return donnees

def sauvegarder_donnees(dico):
    with open("allocations.txt", "w") as fichier:
        for projet, pourcentage in dico.items():
            fichier.write(f"{projet}:{pourcentage}\n")

# --- NOUVELLE FONCTION : L'API COINGECKO ---
def obtenir_prix_marche(dico_projets):
    if len(dico_projets) == 0:
        return {}
    
    # On met tous les noms en minuscules pour le serveur
    noms_min = []
    for nom in dico_projets.keys():
        noms_min.append(nom.lower())
        
    noms_colles = ",".join(noms_min)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={noms_colles}&vs_currencies=usd"
    
    try:
        reponse = requests.get(url)
        return reponse.json()
    except:
        return None # En cas de panne d'Internet

# On charge le portefeuille
portefeuille = lire_donnees()

# --- BARRE LATÉRALE ---
st.sidebar.header("🛠️ Gérer mon portefeuille")

with st.sidebar.form("formulaire_ajout"):
    st.subheader("Ajouter ou Modifier")
    nouveau_nom = st.text_input("Nom du projet :").capitalize()
    nouveau_pourcentage = st.number_input("Pourcentage (%) :", min_value=0.0, max_value=100.0, step=0.1)
    bouton_ajouter = st.form_submit_button("Enregistrer le projet")
    
    if bouton_ajouter:
        if nouveau_nom != "":
            portefeuille[nouveau_nom] = nouveau_pourcentage
            sauvegarder_donnees(portefeuille)
            st.rerun()
        else:
            st.error("Erreur : Le nom ne peut pas être vide.")

# --- SECTION SUPPRESSION (À placer dans la barre latérale) ---
st.sidebar.divider() # On ajoute une ligne visuelle pour séparer l'ajout de la suppression
st.sidebar.subheader("🗑️ Supprimer un projet")

# On vérifie d'abord que le portefeuille n'est pas vide (on ne peut pas supprimer le vide !)
if len(portefeuille) > 0:
    
    # On crée un nouveau formulaire dédié à la suppression
    with st.sidebar.form("formulaire_suppression"):
        
        # st.selectbox crée un menu déroulant. Ses 'options' sont les clés (noms) de notre dictionnaire
        projet_a_supprimer = st.selectbox("Choisissez le projet à retirer :", options=list(portefeuille.keys()))
        
        # Le bouton pour valider l'action
        bouton_supprimer = st.form_submit_button("Supprimer définitivement")
        
        # Si on clique sur le bouton...
        if bouton_supprimer:
            # 1. On utilise le mot-clé 'del' pour l'effacer de la mémoire
            del portefeuille[projet_a_supprimer]
            
            # 2. On écrase l'ancien fichier texte par le nouveau dictionnaire sans ce projet
            sauvegarder_donnees(portefeuille)
            
            # 3. On rafraîchit la page instantanément
            st.rerun()
            

# --- AFFICHAGE PRINCIPAL (AVEC API LIVE) ---
st.subheader("📊 Valorisation en Temps Réel")
capital = st.number_input("Entrez votre capital total ($) :", min_value=0.0, value=1000.0)

if len(portefeuille) == 0:
    st.warning("Votre portefeuille est vide. Utilisez le menu de gauche pour ajouter des projets.")
else:
    # L'effet magique de chargement pendant qu'on interroge CoinGecko !
    with st.spinner("Connexion au marché mondial en cours..."):
        prix_live = obtenir_prix_marche(portefeuille)

    if prix_live is None:
        st.error("Erreur réseau : Impossible de joindre CoinGecko. Revenez plus tard.")
    
    # Création des colonnes pour les cartes
    colonnes = st.columns(3)
    index = 0
    
    for projet, pourcentage in portefeuille.items():
        montant_dollars = capital * (pourcentage / 100)
        projet_min = projet.lower()
        
        # Si on a bien reçu les prix et que notre crypto a été trouvée
        if prix_live and projet_min in prix_live:
            prix_actuel = prix_live[projet_min]["usd"]
            
            # Calcul du nombre de jetons !
            nombre_jetons = montant_dollars / prix_actuel
            
            # On prépare le texte de notre carte Streamlit
            titre_carte = f"{projet} ({prix_actuel} $)"
            texte_principal = f"{nombre_jetons:.4f} jetons"
        else:
            # Si le projet est introuvable sur CoinGecko (ex: Hyperlyquid)
            titre_carte = f"{projet} (Introuvable)"
            texte_principal = "Prix inconnu"
            
        with colonnes[index]:
            # delta_color="off" permet que le texte en bas de la carte soit gris (neutre) et pas vert fluo
            st.metric(label=titre_carte, value=texte_principal, delta=f"{montant_dollars:.2f} $ ({pourcentage}%)", delta_color="off")
            
        index = (index + 1) % 3

st.divider()

# Vérification des 100%
total = sum(portefeuille.values())
if total == 100.0:
    st.success(f"Allocation parfaite : {total}%")
elif total > 100.0:
    st.error(f"Erreur : Vous dépassez les 100% (Total: {total}%)")
else:
    st.info(f"Attention : Vous n'avez alloué que {total:.2f}% pour le moment.")

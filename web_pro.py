import streamlit as st # type: ignore

# 1. Configuration de la page (Pour qu'elle prenne toute la largeur de l'écran)
st.set_page_config(page_title="Mon Portefeuille Pro", page_icon="💼", layout="wide")

st.title("💼 Mon Portefeuille Crypto Pro")
st.write("Bienvenue sur votre tableau de bord financier personnel.")
st.divider()

# --- MES BOÎTES À OUTILS (Adaptées pour le Web) ---
def lire_donnees():
    donnees = {}
    try:
        with open("allocations.txt", "r") as fichier:
            for ligne in fichier:
                morceaux = ligne.strip().split(":")
                if len(morceaux) == 2:
                    donnees[morceaux[0]] = float(morceaux[1])
    except FileNotFoundError:
        pass # Si le fichier n'existe pas, on renvoie le dictionnaire vide
    return donnees

def sauvegarder_donnees(dico):
    with open("allocations.txt", "w") as fichier:
        for projet, pourcentage in dico.items():
            fichier.write(f"{projet}:{pourcentage}\n")

# On charge le portefeuille en mémoire
portefeuille = lire_donnees()


# --- LA BARRE LATÉRALE (LE MENU DE GAUCHE) ---
st.sidebar.header("🛠️ Gérer mon portefeuille")

# Création du formulaire d'ajout/modification
with st.sidebar.form("formulaire_ajout"):
    st.subheader("Ajouter ou Modifier")
    
    nouveau_nom = st.text_input("Nom du projet :").capitalize()
    nouveau_pourcentage = st.number_input("Pourcentage (%) :", min_value=0.0, max_value=100.0, step=0.1)
    
    bouton_ajouter = st.form_submit_button("Enregistrer le projet")
    
    if bouton_ajouter:
        if nouveau_nom != "":
            portefeuille[nouveau_nom] = nouveau_pourcentage
            sauvegarder_donnees(portefeuille)
            st.rerun() # On rafraîchit la page web instantanément
        else:
            st.error("Erreur : Le nom ne peut pas être vide.")


# --- AFFICHAGE PRINCIPAL (CENTRE DE LA PAGE) ---
st.subheader("📊 Calculateur d'Allocations")
capital = st.number_input("Entrez votre capital total ($) :", min_value=0.0, value=1000.0)

if len(portefeuille) == 0:
    st.warning("Votre portefeuille est vide. Utilisez le menu de gauche pour ajouter des projets.")
else:
    colonnes = st.columns(3)
    index = 0
    for projet, pourcentage in portefeuille.items():
        montant = capital * (pourcentage / 100)
        with colonnes[index]:
            st.metric(label=projet, value=f"{pourcentage}%", delta=f"{montant:.2f} $")
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
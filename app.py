import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt
import io

# CONFIGURATION
st.set_page_config(
    page_title="Système de suivi et étiquettes pour un contrôle efficace de cheminement des modules",
    layout="wide"
)

# MASQUER LES ERREURS ROUGES
st.markdown("""
    <style>
    .element-container:has(.stException) {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# CONSTANTES
HISTORIQUE_FILE = "historique.csv"

# CHARGEMENT DE L'HISTORIQUE
if "historique" not in st.session_state:
    if os.path.exists(HISTORIQUE_FILE):
        st.session_state.historique = pd.read_csv(HISTORIQUE_FILE).to_dict(orient="records")
    else:
        st.session_state.historique = []

if "page" not in st.session_state:
    st.session_state.page = "home"

if "show_chart_page" not in st.session_state:
    st.session_state.show_chart_page = False

# CHARGER DONNEES MODULES
@st.cache_data
def load_data():
    return pd.read_excel("data.xlsx")

df = load_data()

# FOND PERSONNALISÉ
def set_background(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
    """, unsafe_allow_html=True)

# GÉNÉRER PDF
def generate_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Historique des modules scannés", ln=1, align="C")
    pdf.ln(10)
    for i, row in dataframe.iterrows():
        pdf.cell(200, 10, txt=f"{row['datetime']} - {row['code']}", ln=1)
    return pdf.output(dest='S').encode('latin-1')

# AFFICHER GRAPHIQUE
def afficher_graphiques():
    st.markdown("### 📊 Répartition des scans par jour")
    historique_df = pd.DataFrame(st.session_state.historique)
    historique_df['date'] = historique_df['datetime'].str[:10]
    daily_counts = historique_df['date'].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(2, 1))  # taille très réduite
    ax.bar(daily_counts.index, daily_counts.values)
    ax.set_xlabel("Date", fontsize=8)
    ax.set_ylabel("Nombre de scans", fontsize=8)
    ax.set_title("Scans par jour", fontsize=10)
    ax.tick_params(axis='x', labelsize=6)
    ax.tick_params(axis='y', labelsize=6)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# PAGE ACCUEIL
if st.session_state.page == "home":
    set_background("BACK/pic.png")

    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.image("BACK/IAV_Logo.png", width=100)
    with col3:
        st.image("BACK/ESTP_Logo.png", width=100)

    st.markdown("""
        <style>
        .title-home {
            font-size: 50px;
            text-align: center;
            color: white;
            font-weight: bold;
            padding: 2rem;
            text-shadow: 2px 2px 4px #000;
        }
        .center-wrap {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 60vh;
            flex-direction: column;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="center-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="title-home">Bienvenue dans la gestion des modules RFID </div>', unsafe_allow_html=True)

    if st.button("Commencer le check 🔍"):
        st.session_state.page = "scan"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# PAGE GRAPHIQUE SÉPARÉE
elif st.session_state.page == "chart":
    if st.button("🔙 Retour à l'historique"):
        st.session_state.page = "scan"
        st.rerun()
    afficher_graphiques()

# PAGE SCAN
elif st.session_state.page == "scan":
    st.markdown("""
        <style>
        .stApp { background-color: #f5f5f5; }
        .info-box {
            background-color: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0px 4px 8px rgba(0,0,0,0.1);
        }
        .title-style {
            font-size: 35px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        st.image("BACK/IAV_Logo.png", width=80)
    with col3:
        st.image("BACK/ESTP_Logo.png", width=80)
    with col2:
        st.markdown("<div class='title-style'> Gestion des modules RFID </div>", unsafe_allow_html=True)

    with st.form("scan_form", clear_on_submit=True):
        barcode = st.text_input("🔍 Scannez un code-barres :", "")
        submitted = st.form_submit_button("📤 Scanner")

    if submitted and barcode:
        barcode = barcode.upper()
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y à %H:%M:%S")

        result = df[df["Barcode"] == barcode]

        nouveau_scan = {"code": barcode, "datetime": timestamp}
        st.session_state.historique.append(nouveau_scan)
        pd.DataFrame(st.session_state.historique).to_csv(HISTORIQUE_FILE, index=False)

        previous = [h for h in st.session_state.historique if h["code"] == barcode]
        if len(previous) > 1:
            st.warning(f"⚠️ Le module {barcode} a déjà été scanné le {previous[-2]['datetime']}")

        if not result.empty:
            st.success(f"✅ Module {barcode} détecté")
            image_path = os.path.join("images", f"{barcode}.jpeg")

            col_img, col_infos = st.columns([1, 2])
            with col_img:
                if os.path.exists(image_path):
                    st.image(image_path, caption=barcode, use_container_width=True)
                else:
                    st.warning("📸 Image non trouvée.")

            with col_infos:
                item = result.iloc[0]
                st.markdown(f"""
                    <div class='info-box'>
                        <p><b>🆔 ID :</b> {item['Id']}</p>
                        <p><b>🎫 Dimensions(mètre) :</b> {item['Dimensions']}</p>
                        <p><b>🎨 Couleur :</b> {item['Color']}</p>
                        <p><b>🧵 Besoin en filament :</b> {item['Filament']}</p>
                        <p><b>💶 Coût(€) :</b> {item['Coût']}</p>
                        <p><b>🧱 Matériau :</b> {item['Material']}</p>
                        <p><b>🕒 Temps d'impression :</b> {item['Printing time']}</p>
                        <p><b>🧵🖨️ Imprimante :</b> {item['Imprimante']}</p>
                        <p><b>📍 Destination :</b> {item['Destination']}</p>
                        

                    </div>
                """, unsafe_allow_html=True)
        else:
            st.error("❌ Aucun module trouvé.")

    if st.button("🔙 Retour à l'accueil"):
        st.session_state.page = "home"
        st.rerun()

    if st.session_state.historique:
        st.markdown("## 📂 Historique des modules scannés")
        historique_df = pd.DataFrame(st.session_state.historique)

        st.markdown("### 🔢 Filtres")
        codes = historique_df['code'].unique()
        selected_code = st.selectbox("🔍 Filtrer par code :", ["Tous"] + list(codes))
        dates = historique_df['datetime'].str[:10].unique()
        selected_date = st.selectbox("🗓️ Filtrer par date :", ["Toutes"] + sorted(dates))

        filtered_df = historique_df.copy()
        if selected_code != "Tous":
            filtered_df = filtered_df[filtered_df["code"] == selected_code]
        if selected_date != "Toutes":
            filtered_df = filtered_df[filtered_df["datetime"].str.startswith(selected_date)]

        st.dataframe(filtered_df, use_container_width=True)

        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("Télécharger l'historique filtré", csv, "historique_modules.csv", "text/csv")

        pdf_bytes = generate_pdf(filtered_df)
        st.download_button("📄 Exporter en PDF", data=pdf_bytes, file_name="historique_modules.pdf", mime="application/pdf")

        if st.button("♻️ Réinitialiser l'historique"):
            st.session_state.historique = []
            if os.path.exists(HISTORIQUE_FILE):
                os.remove(HISTORIQUE_FILE)
            st.success("✅ Historique vidé.")
            st.rerun()

        if st.button("📊 Voir le graphique des scans"):
            st.session_state.page = "chart"
            st.rerun()

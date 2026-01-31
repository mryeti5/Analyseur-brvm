import streamlit as st

# Configuration de la page
st.set_page_config(page_title="BRVM Fondamental V8", layout="wide", page_icon="📈")

st.title("📊 Analyseur Fondamental BRVM - Expert V8")
st.markdown("---")

# --- 1. BARRE LATÉRALE : COLLECTE DES DONNÉES ---
st.sidebar.header("📥 Saisie des données")

with st.sidebar:
    nom = st.text_input("Nom de l'entreprise", "SOCIETE GENERALE CI")
    pays = st.selectbox("Pays de l'entreprise", 
                        ["Cote d'ivoire", "Senegal", "Mali", "Burkina Faso", "Benin", "Niger", "Togo"])
    secteur = st.selectbox("Secteur d'activité", 
                           ["Services financiers", "Telecommunications", "Energie", "Publics", "Industriels", "Consommation de base", "Consommation discretionnaire"])
    
    st.subheader("Marché & Bilan")
    cours_actuel = st.number_input("Cours Actuel (FCFA)", value=29350)
    capitaux_propres = st.number_input("Capitaux Propres", value=451721000000)
    nombre_titres = st.number_input("Nombre de titres", value=31111110)

# --- 2. ZONE PRINCIPALE : DONNÉES HISTORIQUES ---
st.subheader("📋 Saisie de l'Historique (5 ans)")
col_p, col_r = st.columns(2)

with col_p:
    pnb_input = st.text_area("PNB (ex: 100, 120...)", "164062000000, 185000000000, 210000000000, 240000000000, 263207000000")
    bnpa_input = st.text_area("BNPA (Bénéfice par action)", "1556, 2121, 2346, 2957, 3254")

with col_r:
    rn_input = st.text_area("Résultat Net", "48435000000, 66000000000, 73000000000, 92000000000, 101228000000")
    div_input = st.text_area("Dividendes Brut", "368.30, 800, 1200, 1400, 1639.00")

# --- 3. LOGIQUE DE CALCUL ---
if st.button("🚀 GÉNÉRER LE RAPPORT D'ANALYSE"):
    try:
        # Conversion des données
        list_pnb = [float(x.strip()) for x in pnb_input.split(",")]
        list_rn = [float(x.strip()) for x in rn_input.split(",")]
        list_bnpa = [float(x.strip()) for x in bnpa_input.split(",")]
        list_div = [float(x.strip()) for x in div_input.split(",")]
        annees = [2020, 2021, 2022, 2023, 2024]

        # Calculs Croissance
        pnb_tot = ((list_pnb[-1] - list_pnb[0]) / list_pnb[0]) * 100
        rn_tot = ((list_rn[-1] - list_rn[0]) / list_rn[0]) * 100
        pnb_moy = pnb_tot / 4
        rn_moy = rn_tot / 4
        
        # Marges et Rentabilité
        marges = [(rn * 100) / pnb for rn, pnb in zip(list_rn, list_pnb)]
        marge_moyenne = sum(marges) / len(marges)

        def diag_rentabilite(sect, moy):
            s = sect.lower()
            if "telecom" in s: limites = [5, 15]
            elif "financier" in s: limites = [20, 30]
            elif "consommation" in s: limites = [5, 12]
            else: limites = [5, 10]
            if moy < limites[0]: return "FAIBLEMENT RENTABLE"
            if limites[0] <= moy <= limites[1]: return "RENTABLE"
            return "TRÈS RENTABLE"

        # Fiscalité et TD
        def get_coeff(p, a):
            p = p.lower()
            if "ivoire" in p: return 0.88 if a >= 2024 else 0.90
            if "senegal" in p: return 0.90
            if "burkina" in p: return 0.875
            if "niger" in p: return 0.93
            return 0.95

        tds = [(d*100)/(b*get_coeff(pays, a)) for d, b, a in zip(list_div, list_bnpa, annees)]

        # Ratios
        per = cours_actuel / list_bnpa[-1]
        vmc = capitaux_propres / nombre_titres
        pbr = (cours_actuel * nombre_titres) / capitaux_propres
        rvc = per * pbr

        # --- 4. AFFICHAGE DU RAPPORT ---
        st.header(f"📈 Rapport : {nom}")

        # Section Croissance
        st.subheader("1. Dynamique de Croissance")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Progression PNB", f"+{pnb_tot:.1f}%")
        c2.metric("Moyenne Annuelle PNB", f"+{pnb_moy:.1f}%")
        c3.metric("Progression RN", f"+{rn_tot:.1f}%")
        c4.metric("Moyenne Annuelle RN", f"+{rn_moy:.1f}%")

        # Section Rentabilité
        st.markdown("---")
        st.subheader("2. Rentabilité Opérationnelle")
        rm1, rm2 = st.columns(2)
        rm1.metric("Marge Nette Moyenne", f"{marge_moyenne:.2f}%")
        rm2.info(f"💡 **Diagnostic Secteur ({secteur})** : {diag_rentabilite(secteur, marge_moyenne)}")

        # Tableau des flux
        st.subheader("3. Historique Dividendes & Taux de Distribution")
        rows = []
        for i in range(len(annees)):
            note = "⚠️ ALERTE : TD > 100%" if tds[i] > 100 else ("💎 STRATÉGIE RENTE" if tds[i] > 50 else "📈 CROISSANCE")
            rows.append({
                "Année": annees[i],
                "Marge Nette (%)": f"{marges[i]:.2f} %",
                "TD (Fiscalité incluse)": f"{tds[i]:.2f} %",
                "Type d'Action": note
            })
        st.table(rows)

        # Section Valorisation
        st.markdown("---")
        st.subheader("4. Analyse de la Valorisation")
        v1, v2, v3, v4 = st.columns(4)
        
        def evaluer(val, seuils):
            if val < seuils[0]: return "SOUS-ÉVALUÉE"
            if seuils[0] <= val <= seuils[1]: return "JUSTE VALEUR"
            return "SURÉVALUÉE"

        v1.metric("PER", f"{per:.2f}", evaluer(per, [9, 11]), delta_color="inverse")
        v2.metric("VMC (Valeur Comptable)", f"{vmc:.0f} FCFA")
        v3.metric("PBR", f"{pbr:.2f}", evaluer(pbr, [0.7, 1]), delta_color="inverse")
        v4.metric("RVC (PER x PBR)", f"{rvc:.2f}", evaluer(rvc, [7, 10]), delta_color="inverse")

        # Conclusion Finale
        st.markdown("---")
        if per < 9:
            st.success(f"### 🎯 CONCLUSION : {nom} est une opportunité SOUS-ÉVALUÉE")
            st.balloons()
        elif 9 <= per <= 11:
            st.warning(f"### ⚖️ CONCLUSION : {nom} est à sa JUSTE VALEUR")
        else:
            st.error(f"### 🚩 CONCLUSION : {nom} est SURÉVALUÉE")

    except Exception as e:
        st.error(f"Erreur de saisie : {e}")
"""
Interface de validation des emails hebdomadaires Algo-Draw
Streamlit app pour preview et envoi des emails
"""

import streamlit as st
import json
import os
from datetime import datetime
from email_generator import generate_email_data
from email_templates import generate_email_basic, generate_email_premium
import resend
from supabase import create_client

# Configuration
st.set_page_config(page_title="Validation Email Hebdo", layout="wide", page_icon="📧")

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

resend.api_key = RESEND_API_KEY
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- SESSION STATE ---
if 'email_data' not in st.session_state:
    st.session_state.email_data = None
if 'alertes_cashout' not in st.session_state:
    st.session_state.alertes_cashout = ""
if 'note_analyste' not in st.session_state:
    st.session_state.note_analyste = ""

# --- HEADER ---
st.markdown("# 📧 Validation Email Hebdomadaire")
st.markdown("---")

# --- ÉTAPE 1 : GÉNÉRATION DES DONNÉES ---
col_gen1, col_gen2 = st.columns([3, 1])

with col_gen1:
    st.markdown("### Étape 1 : Génération des données")
    st.markdown("Analyse Google Sheets et génère les statistiques de la semaine.")

with col_gen2:
    if st.button("🔄 Générer les données", type="primary", use_container_width=True):
        with st.spinner("📊 Analyse en cours..."):
            try:
                data = generate_email_data()
                st.session_state.email_data = data
                st.success("✅ Données générées !")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur : {e}")

# Si données chargées, afficher le reste
if st.session_state.email_data:
    data = st.session_state.email_data
    
    st.markdown("---")
    
    # --- STATS AUTO-GÉNÉRÉES ---
    st.markdown("### 📊 Statistiques Auto-Générées")
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    
    with col_s1:
        st.metric("Nouvelles équipes", len(data['nouvelles_equipes']))
    with col_s2:
        st.metric("Closes", len(data['closes']))
    with col_s3:
        st.metric("Actives (Premium/VIP)", data['stats_globales']['nb_actives'])
    with col_s4:
        st.metric("Top 3 (Basic)", len(data['top_3']))
    
    # Détails closes
    if data['closes']:
        total_net = sum([c['net_u'] for c in data['closes']])
        st.info(f"**Bénéfice total closes cette semaine :** {total_net:+.1f}U")
    
    st.markdown("---")
    
    # --- SECTIONS À COMPLÉTER ---
    st.markdown("### 📝 Sections à Compléter")
    
    # Alertes cash-out
    st.markdown("#### ⚠️ Alertes Cash-Out (Premium/VIP uniquement)")
    st.caption("Zone libre pour rédiger les recommandations de sécurisation")
    
    # Pré-remplissage avec paliers critiques détectés
    placeholder_cashout = ""
    if data['paliers_critiques']:
        for pc in data['paliers_critiques']:
            placeholder_cashout += f"🔔 {pc['equipe']} ({pc['palier']}) — {pc['championnat']}\n"
            placeholder_cashout += f"Prochain match : {pc['proch_match']}\n"
            placeholder_cashout += "Contexte : [À compléter]\n"
            placeholder_cashout += "Recommandation : [À compléter]\n\n"
    else:
        placeholder_cashout = "Aucun palier critique (≥P3) détecté cette semaine."
    
    alertes_cashout = st.text_area(
        "Rédigez vos alertes cash-out",
        value=st.session_state.alertes_cashout or placeholder_cashout,
        height=200,
        key="textarea_cashout"
    )
    st.session_state.alertes_cashout = alertes_cashout
    
    st.markdown("---")
    
    # Note de l'analyste
    st.markdown("#### 💬 Note de l'Analyste (tous forfaits)")
    st.caption("Votre insight hebdomadaire personnel")
    
    # Suggestion auto
    suggestion_note = f"""Cette semaine, {len(data['nouvelles_equipes'])} nouvelle{'s' if len(data['nouvelles_equipes']) > 1 else ''} équipe{'s' if len(data['nouvelles_equipes']) > 1 else ''} identifiée{'s' if len(data['nouvelles_equipes']) > 1 else ''}. """
    
    if data['closes']:
        suggestion_note += f"{len(data['closes'])} martingale{'s' if len(data['closes']) > 1 else ''} close{'s' if len(data['closes']) > 1 else ''} avec un ROI moyen satisfaisant. "
    
    suggestion_note += "\n\n[Ajoutez votre analyse personnelle ici]"
    
    note_analyste = st.text_area(
        "Rédigez votre note",
        value=st.session_state.note_analyste or suggestion_note,
        height=150,
        key="textarea_note"
    )
    st.session_state.note_analyste = note_analyste
    
    st.markdown("---")
    
    # --- PREVIEW EMAIL ---
    st.markdown("### 🔍 Preview Email")
    
    tab_basic, tab_premium = st.tabs(["📧 Basic", "📧 Premium/VIP"])
    
    with tab_basic:
        st.markdown("#### Aperçu Email Basic")
        html_basic = generate_email_basic(data, "", note_analyste)
        st.components.v1.html(html_basic, height=800, scrolling=True)
    
    with tab_premium:
        st.markdown("#### Aperçu Email Premium/VIP")
        html_premium = generate_email_premium(data, alertes_cashout, note_analyste)
        st.components.v1.html(html_premium, height=1000, scrolling=True)
    
    st.markdown("---")
    
    # --- DESTINATAIRES ---
    st.markdown("### 👥 Destinataires")
    
    try:
        # Récupérer tous les utilisateurs avec email + plan
        users_result = supabase.table("profiles").select("email, plan").execute()
        users = users_result.data
        
        basic_users = [u['email'] for u in users if u['plan'] == 'basic']
        premium_vip_users = [u['email'] for u in users if u['plan'] in ['premium', 'vip']]
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.info(f"**Basic :** {len(basic_users)} destinataires")
            with st.expander("Voir la liste"):
                for email in basic_users:
                    st.text(f"• {email}")
        
        with col_d2:
            st.info(f"**Premium/VIP :** {len(premium_vip_users)} destinataires")
            with st.expander("Voir la liste"):
                for email in premium_vip_users:
                    st.text(f"• {email}")
        
        total_destinataires = len(basic_users) + len(premium_vip_users)
        
    except Exception as e:
        st.error(f"Erreur chargement destinataires : {e}")
        total_destinataires = 0
        basic_users = []
        premium_vip_users = []
    
    st.markdown("---")
    
    # --- ENVOI ---
    st.markdown("### 📤 Envoi des Emails")
    
    col_e1, col_e2, col_e3 = st.columns([2, 2, 2])
    
    with col_e1:
        if st.button("📤 Envoyer MAINTENANT", type="primary", use_container_width=True, disabled=(total_destinataires == 0)):
            if not alertes_cashout.strip() or "[À compléter]" in alertes_cashout:
                st.warning("⚠️ Les alertes cash-out contiennent encore des sections à compléter.")
            elif not note_analyste.strip() or "[Ajoutez votre analyse" in note_analyste:
                st.warning("⚠️ La note de l'analyste n'est pas finalisée.")
            else:
                with st.spinner("📧 Envoi en cours..."):
                    try:
                        # Envoyer aux Basic
                        for email in basic_users:
                            resend.Emails.send({
                                "from": "L'équipe Algo-Draw <onboarding@resend.dev>",
                                "to": email,
                                "subject": f"📊 Votre résumé hebdomadaire Algo-Draw — {data['semaine']}",
                                "html": html_basic
                            })
                        
                        # Envoyer aux Premium/VIP
                        for email in premium_vip_users:
                            resend.Emails.send({
                                "from": "L'équipe Algo-Draw <onboarding@resend.dev>",
                                "to": email,
                                "subject": f"📊 Bilan hebdomadaire — {len(data['nouvelles_equipes'])} nouvelles opportunités",
                                "html": html_premium
                            })
                        
                        st.success(f"✅ {total_destinataires} emails envoyés avec succès !")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Erreur envoi : {e}")
    
    with col_e2:
        if st.button("⏰ Programmer Jeudi 8h", use_container_width=True, disabled=True):
            st.info("⚙️ Fonctionnalité de programmation à venir (GitHub Actions)")
    
    with col_e3:
        if st.button("💾 Sauvegarder brouillon", use_container_width=True):
            # Sauvegarder dans un fichier JSON
            draft = {
                'data': data,
                'alertes_cashout': alertes_cashout,
                'note_analyste': note_analyste,
                'saved_at': datetime.now().isoformat()
            }
            with open('/tmp/email_draft.json', 'w', encoding='utf-8') as f:
                json.dump(draft, f, ensure_ascii=False, indent=2)
            st.success("✅ Brouillon sauvegardé !")

else:
    st.info("👆 Cliquez sur 'Générer les données' pour commencer.")
    
    # Afficher les stats hardcodées en attendant
    st.markdown("### 📊 Performances Algo-Draw")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.metric("ROI Saison en cours", "+141%", help="9 mois (juil-mars)")
    with col_p2:
        st.metric("Taux de réussite", "92%", help="Saison 2025-2026")
    with col_p3:
        st.metric("Taux de réussite", "90%", help="Saison 2023-2024")

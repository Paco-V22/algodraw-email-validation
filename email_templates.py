"""
Templates HTML pour les emails Algo-Draw
"""

def format_proba(proba):
    """Formate la probabilité en pourcentage"""
    return f"{int(proba * 100)}%"

def format_net_u(net_u):
    """Formate le net en unités avec signe"""
    return f"{net_u:+.1f}U".replace('.', ',')

def format_roi(roi):
    """Formate le ROI en pourcentage avec signe"""
    return f"{roi:+.0f}%"

# === TEMPLATE BASIC ===

def generate_email_basic(data, alertes_cashout="", note_analyste=""):
    """Génère l'email HTML pour forfait Basic"""
    
    # Construction liste Top 3
    top_3_html = ""
    for m in data['top_3']:
        top_3_html += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #333;">
                <strong>{m['equipe']}</strong><br>
                <span style="color: #888; font-size: 0.9em;">{m['championnat']}</span>
            </td>
            <td style="padding: 12px; border-bottom: 1px solid #333; text-align: center;">
                <span style="color: #4CAF50; font-weight: bold;">{format_proba(m['proba'])}</span>
            </td>
            <td style="padding: 12px; border-bottom: 1px solid #333; text-align: center;">
                {m['palier']}
            </td>
        </tr>
        """
    
    # Construction liste closes
    closes_html = ""
    total_net = 0
    for c in data['closes']:
        total_net += c['net_u']
        closes_html += f"""
        <li style="margin: 10px 0; padding: 10px; background: #2d2d2d; border-radius: 5px;">
            <strong>{c['equipe']}</strong> — {c['score']} ✅ ({c['palier']})<br>
            <span style="color: #4CAF50;">{format_net_u(c['net_u'])} • ROI {format_roi(c['roi'])}</span>
        </li>
        """
    
    if not closes_html:
        closes_html = "<li>Aucune martingale close cette semaine</li>"
    
    perf_semaine = format_net_u(total_net) if data['closes'] else "+0,0U"
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #1a1a1a; font-family: Arial, sans-serif; color: #ffffff;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        
        <!-- En-tête -->
        <div style="text-align: center; padding: 30px 0; border-bottom: 2px solid #e63946;">
            <h1 style="margin: 0; font-size: 28px; color: #e63946;">📊 Algo-Draw</h1>
            <p style="margin: 10px 0 0 0; color: #888;">Votre bilan hebdomadaire</p>
        </div>
        
        <!-- Top 3 Martingales -->
        <div style="margin-top: 30px;">
            <h2 style="color: #e63946; border-left: 4px solid #e63946; padding-left: 15px;">
                📈 VOS TOP 3 MARTINGALES ACTIVES
            </h2>
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; background: #2d2d2d; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background: #3d3d3d;">
                        <th style="padding: 12px; text-align: left;">Équipe</th>
                        <th style="padding: 12px; text-align: center;">Proba</th>
                        <th style="padding: 12px; text-align: center;">Statut</th>
                    </tr>
                </thead>
                <tbody>
                    {top_3_html}
                </tbody>
            </table>
        </div>
        
        <!-- Martingales closes -->
        <div style="margin-top: 30px;">
            <h2 style="color: #e63946; border-left: 4px solid #e63946; padding-left: 15px;">
                ✅ MARTINGALES CLOSES CETTE SEMAINE
            </h2>
            <ul style="list-style: none; padding: 0; margin-top: 15px;">
                {closes_html}
            </ul>
            <p style="margin-top: 15px; padding: 15px; background: #2d2d2d; border-radius: 5px; text-align: center;">
                <strong>🎯 Performance semaine : {perf_semaine}</strong>
            </p>
        </div>
        
        <!-- Upgrade Premium -->
        <div style="margin-top: 30px; padding: 25px; background: linear-gradient(135deg, #e63946 0%, #c41e2a 100%); border-radius: 10px; text-align: center;">
            <h3 style="margin: 0 0 15px 0; color: #ffffff;">🔒 PASSEZ À PREMIUM</h3>
            <p style="margin: 0 0 20px 0; color: #ffffff; font-size: 0.95em;">
                Les membres Premium/VIP suivent actuellement <strong>{data['stats_globales']['nb_actives']}</strong> martingales actives.<br>
                Multipliez vos opportunités dès aujourd'hui.
            </p>
            <a href="https://algodraw-jhscbhc4gcec3npaxbrafd.streamlit.app/?page=pricing" 
               style="display: inline-block; padding: 12px 30px; background: #ffffff; color: #e63946; text-decoration: none; border-radius: 5px; font-weight: bold;">
                Upgrader mon forfait
            </a>
        </div>
        
        <!-- Footer -->
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #333; text-align: center; color: #888; font-size: 0.85em;">
            <p>À la semaine prochaine,<br>L'équipe Algo-Draw</p>
            <p style="margin-top: 15px;">
                <a href="https://algodraw-jhscbhc4gcec3npaxbrafd.streamlit.app" style="color: #e63946; text-decoration: none;">
                    Connectez-vous sur algodraw.com
                </a>
            </p>
            <p style="margin-top: 20px; font-size: 0.75em; color: #666;">
                Vous recevez cet email car vous êtes abonné au forfait Basic Algo-Draw.<br>
                <a href="#" style="color: #666;">Se désabonner</a>
            </p>
        </div>
        
    </div>
</body>
</html>
    """
    
    return html

# === TEMPLATE PREMIUM/VIP ===

def generate_email_premium(data, alertes_cashout="", note_analyste=""):
    """Génère l'email HTML pour forfaits Premium/VIP"""
    
    # Nouvelles équipes
    nouvelles_html = ""
    if data['nouvelles_equipes']:
        for n in data['nouvelles_equipes']:
            nouvelles_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #333;">
                    <strong>{n['equipe']}</strong><br>
                    <span style="color: #888; font-size: 0.9em;">{n['championnat']}</span>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #333; text-align: center;">
                    SSN {n['ssn']}
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #333; text-align: center;">
                    <span style="color: #4CAF50; font-weight: bold;">{format_proba(n['proba'])}</span>
                </td>
            </tr>
            """
    else:
        nouvelles_html = """
        <tr>
            <td colspan="3" style="padding: 20px; text-align: center; color: #888;">
                Aucune nouvelle équipe cette semaine
            </td>
        </tr>
        """
    
    # Toutes les martingales actives (top 8)
    actives_html = ""
    for m in data['all_actives'][:8]:
        actives_html += f"• {m['equipe']} — Proba {format_proba(m['proba'])} — {m['palier']}<br>"
    
    if len(data['all_actives']) > 8:
        actives_html += f"<em style='color: #888;'>... et {len(data['all_actives']) - 8} autres</em>"
    
    # Alertes cash-out
    cashout_section = ""
    if alertes_cashout and alertes_cashout.strip():
        cashout_section = f"""
        <div style="margin-top: 30px; padding: 20px; background: #3d2a00; border-left: 4px solid #ff9800; border-radius: 5px;">
            <h2 style="color: #ff9800; margin: 0 0 15px 0;">
                ⚠️ ALERTES CASH-OUT (PALIERS CRITIQUES)
            </h2>
            <div style="color: #ffffff; line-height: 1.6;">
                {alertes_cashout}
            </div>
        </div>
        """
    
    # Martingales closes avec ROI détaillé
    closes_html = ""
    total_net = 0
    total_roi_sum = 0
    nb_closes = len(data['closes'])
    
    for c in data['closes']:
        total_net += c['net_u']
        total_roi_sum += c['roi']
        closes_html += f"""
        <li style="margin: 10px 0; padding: 15px; background: #2d2d2d; border-radius: 5px;">
            <strong>{c['equipe']}</strong> — {c['score']} ✅ ({c['palier']})<br>
            <span style="color: #4CAF50; font-size: 1.1em;">{format_net_u(c['net_u'])} • ROI {format_roi(c['roi'])}</span>
        </li>
        """
    
    if not closes_html:
        closes_html = "<li>Aucune martingale close cette semaine</li>"
        avg_roi = 0
    else:
        avg_roi = total_roi_sum / nb_closes if nb_closes > 0 else 0
    
    bilan_closes = f"{format_net_u(total_net)} | ROI moyen : {format_roi(avg_roi)}" if nb_closes > 0 else "Aucune close"
    
    # Note de l'analyste
    note_section = ""
    if note_analyste and note_analyste.strip():
        note_section = f"""
        <div style="margin-top: 30px; padding: 20px; background: #1e3a5f; border-left: 4px solid #2196F3; border-radius: 5px;">
            <h2 style="color: #2196F3; margin: 0 0 15px 0;">
                💬 NOTE DE L'ANALYSTE
            </h2>
            <div style="color: #ffffff; line-height: 1.6; font-style: italic;">
                {note_analyste}
            </div>
        </div>
        """
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #1a1a1a; font-family: Arial, sans-serif; color: #ffffff;">
    <div style="max-width: 650px; margin: 0 auto; padding: 20px;">
        
        <!-- En-tête -->
        <div style="text-align: center; padding: 30px 0; border-bottom: 2px solid #e63946;">
            <h1 style="margin: 0; font-size: 28px; color: #e63946;">📊 Algo-Draw Premium</h1>
            <p style="margin: 10px 0 0 0; color: #888;">Votre bilan hebdomadaire complet</p>
        </div>
        
        <!-- Nouvelles équipes -->
        <div style="margin-top: 30px;">
            <h2 style="color: #e63946; border-left: 4px solid #e63946; padding-left: 15px;">
                🆕 NOUVELLES ÉQUIPES IDENTIFIÉES ({len(data['nouvelles_equipes'])})
            </h2>
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; background: #2d2d2d; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background: #3d3d3d;">
                        <th style="padding: 12px; text-align: left;">Équipe</th>
                        <th style="padding: 12px; text-align: center;">SSN</th>
                        <th style="padding: 12px; text-align: center;">Proba</th>
                    </tr>
                </thead>
                <tbody>
                    {nouvelles_html}
                </tbody>
            </table>
        </div>
        
        <!-- Toutes les martingales actives -->
        <div style="margin-top: 30px;">
            <h2 style="color: #e63946; border-left: 4px solid #e63946; padding-left: 15px;">
                📊 TOUTES LES MARTINGALES ACTIVES ({data['stats_globales']['nb_actives']})
            </h2>
            <div style="margin-top: 15px; padding: 20px; background: #2d2d2d; border-radius: 8px; line-height: 1.8;">
                {actives_html}
            </div>
        </div>
        
        <!-- Alertes cash-out -->
        {cashout_section}
        
        <!-- Martingales closes -->
        <div style="margin-top: 30px;">
            <h2 style="color: #e63946; border-left: 4px solid #e63946; padding-left: 15px;">
                ✅ MARTINGALES CLOSES CETTE SEMAINE ({nb_closes})
            </h2>
            <ul style="list-style: none; padding: 0; margin-top: 15px;">
                {closes_html}
            </ul>
            <p style="margin-top: 15px; padding: 15px; background: #2d2d2d; border-radius: 5px; text-align: center;">
                <strong>Bilan closes : {bilan_closes}</strong>
            </p>
        </div>
        
        <!-- Performance globale -->
        <div style="margin-top: 30px; padding: 20px; background: #2d2d2d; border-radius: 8px;">
            <h2 style="color: #e63946; margin: 0 0 15px 0;">📈 PERFORMANCE GLOBALE</h2>
            <table style="width: 100%; color: #ffffff;">
                <tr>
                    <td style="padding: 8px 0;">ROI Portefeuille :</td>
                    <td style="padding: 8px 0; text-align: right; font-weight: bold; color: #4CAF50;">+141%</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0;">Taux réussite saison :</td>
                    <td style="padding: 8px 0; text-align: right; font-weight: bold;">92%</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0;">Capital engagé :</td>
                    <td style="padding: 8px 0; text-align: right; font-weight: bold;">{data['stats_globales']['capital_engage_u']:.0f}U</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0;">Bénéfice net cumulé :</td>
                    <td style="padding: 8px 0; text-align: right; font-weight: bold; color: #4CAF50;">{format_net_u(data['stats_globales']['benefice_total_u'])}</td>
                </tr>
            </table>
        </div>
        
        <!-- Note analyste -->
        {note_section}
        
        <!-- Footer -->
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #333; text-align: center; color: #888; font-size: 0.85em;">
            <p>Connectez-vous sur algodraw.com pour voir tous les détails.</p>
            <p style="margin-top: 15px; font-weight: bold; color: #ffffff;">
                Bonne semaine,<br>L'équipe Algo-Draw
            </p>
            <p style="margin-top: 20px; font-size: 0.75em; color: #666;">
                Vous recevez cet email car vous êtes abonné au forfait Premium/VIP Algo-Draw.<br>
                <a href="#" style="color: #666;">Gérer mes préférences</a>
            </p>
        </div>
        
    </div>
</body>
</html>
    """
    
    return html

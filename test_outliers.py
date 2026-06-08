"""
Script complet pour lancer une analyse et générer le rapport PDF
"""

import requests
import json
import time
import os
import sys

print("=" * 70)
print("🚀 AUTOEDA - ANALYSE COMPLÈTE AVEC RAPPORT PDF")
print("=" * 70)

BASE_URL = "http://localhost:8000/api/v1"

# 1. Vérifier que le serveur est en ligne
print("\n🔍 1. VÉRIFICATION DU SERVEUR...")
try:
    response = requests.get(f"{BASE_URL}/public/health", timeout=5)
    if response.status_code == 200:
        print("   ✅ Serveur en ligne")
    else:
        print(f"   ❌ Serveur répond mais status: {response.status_code}")
        sys.exit(1)
except requests.exceptions.ConnectionError:
    print("   ❌ Serveur non accessible !")
    print("   Lance d'abord: uvicorn app.main:app --reload")
    sys.exit(1)

# 2. Upload du fichier Titanic
print("\n📤 2. UPLOAD DU FICHIER TITANIC...")
file_path = "D:/AutoEDA_Backend/titanic.csv"

if not os.path.exists(file_path):
    print(f"   ❌ Fichier non trouvé: {file_path}")
    sys.exit(1)

with open(file_path, 'rb') as f:
    files = {'file': ('titanic.csv', f, 'text/csv')}
    response = requests.post(f"{BASE_URL}/upload", files=files)

if response.status_code == 200:
    upload_data = response.json()
    file_id = upload_data['file_id']
    print(f"   ✅ Upload réussi!")
    print(f"   📁 File ID: {file_id}")
    print(f"   📊 Lignes: {upload_data['rows']}")
    print(f"   📋 Colonnes: {upload_data['columns']}")
else:
    print(f"   ❌ Erreur upload: {response.text}")
    sys.exit(1)

# 3. Lancer l'analyse complète
print("\n🔬 3. LANCEMENT DE L'ANALYSE COMPLÈTE...")
print("   ⏳ Calcul en cours (cela peut prendre quelques secondes)...")
start_time = time.time()

response = requests.post(f"{BASE_URL}/analysis/run/{file_id}?quick=false", timeout=120)

elapsed_time = time.time() - start_time

if response.status_code == 200:
    analysis_result = response.json()
    print(f"   ✅ Analyse terminée en {elapsed_time:.2f} secondes")
    
    quality = analysis_result.get('quality', {}).get('score', {})
    print(f"   📈 Score qualité: {quality.get('total_score', 'N/A')}/100")
    print(f"   🎯 Grade: {quality.get('grade', 'N/A')}")
    print(f"   💾 From cache: {analysis_result.get('from_cache', False)}")
    
    # Sauvegarder le résultat
    with open("last_analysis_result.json", "w", encoding='utf-8') as f:
        json.dump(analysis_result, f, indent=2, ensure_ascii=False)
    print("   💾 Résultat sauvegardé dans last_analysis_result.json")
else:
    print(f"   ❌ Erreur analyse: {response.text}")
    sys.exit(1)

# 4. Générer le rapport PDF
print("\n📄 4. GÉNÉRATION DU RAPPORT PDF...")
print("   ⏳ Génération en cours...")

response = requests.get(f"{BASE_URL}/reports/pdf/{file_id}?download=false", timeout=120)

if response.status_code == 200:
    pdf_data = response.json()
    pdf_path = pdf_data.get('report_path')
    print(f"   ✅ PDF généré avec succès!")
    print(f"   📁 Chemin: {pdf_path}")
    
    # Vérifier la taille du fichier
    if os.path.exists(pdf_path):
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f"   📏 Taille: {size_kb:.1f} KB")
else:
    print(f"   ❌ Erreur PDF: {response.text}")

# 5. Télécharger le PDF
print("\n📥 5. TÉLÉCHARGEMENT DU PDF...")
response = requests.get(f"{BASE_URL}/reports/pdf/{file_id}/download")

if response.status_code == 200:
    with open("rapport_complet.pdf", "wb") as f:
        f.write(response.content)
    print(f"   ✅ PDF téléchargé: rapport_complet.pdf ({len(response.content)/1024:.1f} KB)")
else:
    print(f"   ❌ Erreur téléchargement: {response.text}")

# 6. Résumé final
print("\n" + "=" * 70)
print("📊 RÉSUMÉ FINAL")
print("=" * 70)
print(f"""
   ✅ Upload réussi
   📁 File ID: {file_id}
   🔬 Analyse: {elapsed_time:.2f}s
   ⭐ Score qualité: {quality.get('total_score', 'N/A')}/100
   📄 Rapport PDF: rapport_complet.pdf
   
   🔗 Liens utiles:
   - Swagger UI: http://localhost:8000/docs
   - Health check: http://localhost:8000/api/v1/public/health
""")

print("✅ Analyse terminée ! Ouvre 'rapport_complet.pdf' pour voir le résultat.")
# Debug-Anleitung: "Bewertung veröffentlichen funktioniert nicht"

## Schritt-für-Schritt Diagnose

### 1. Anmeldung überprüfen
- **Benutzer**: sarah.klein@demo.com
- **Passwort**: password123
- **Oder**: max.mustermann@test.de / password123

**Test**: Nach Login sollten Sie oben rechts Ihren Namen sehen

### 2. Shop auswählen
- Gehen Sie zu "Shops" im Menü
- Wählen Sie einen Shop, den Sie **noch NICHT bewertet haben**
- **Wichtig**: Jeder Benutzer kann einen Shop nur einmal bewerten!

### 3. Bewertungsformular öffnen
- Klicken Sie auf "Bewertung schreiben"
- **Falls Button grau/inaktiv**: Sie müssen angemeldet sein
- **Falls "Sie haben diesen Shop bereits bewertet"**: Wählen Sie einen anderen Shop

### 4. Formular ausfüllen - TEST 1 (Ohne Nachweise)
**Für 4-5 Sterne (einfach):**
1. Wählen Sie 5 Sterne
2. Schreiben Sie einen Kommentar (mind. 10 Zeichen)
3. **Keine** Bestellnummer oder Bilder nötig
4. Klicken Sie "Bewertung veröffentlichen"
5. **Erwartet**: Toast "Ihre Bewertung wurde erfolgreich veröffentlicht."

### 5. Formular ausfüllen - TEST 2 (Mit Nachweisen)
**Für 1-3 Sterne (komplex):**
1. Wählen Sie 3 Sterne
2. **Gelber Bereich erscheint**: "Nachweis erforderlich"
3. Schreiben Sie einen Kommentar
4. **Bestellnummer eingeben**: z.B. "ORD-2024-12345" (mind. 3 Zeichen)
5. **Bild hochladen**: Klicken Sie auf Upload-Bereich, wählen Sie JPG/PNG
6. **Warten Sie**: Bis Bild-Vorschau erscheint (zeigt hochgeladenes Bild)
7. Klicken Sie "Bewertung veröffentlichen"
8. **Erwartet**: Toast "Ihre Bewertung wurde zur Prüfung eingereicht..."

## Häufige Probleme & Lösungen

### Problem 1: "Sie haben diesen Shop bereits bewertet"
**Lösung**: Wählen Sie einen anderen Shop aus der Liste

### Problem 2: Button tut nichts (bei 1-3 Sternen)
**Diagnose**:
- Öffnen Sie Browser-Konsole (F12 → Console Tab)
- Suchen Sie nach Fehlern (rot)
- **Fehler "invalid form control"**: Bild nicht hochgeladen oder Bestellnummer fehlt

**Lösung**:
- Stellen Sie sicher, dass:
  - ✅ Bestellnummer mindestens 3 Zeichen hat
  - ✅ Mindestens 1 Bild hochgeladen wurde
  - ✅ Bild-Vorschau sichtbar ist

### Problem 3: Keine Toast-Nachricht
**Mögliche Ursachen**:
- API-Fehler (401, 400)
- Netzwerk-Problem
- Browser-Cache

**Lösung**:
1. Browser-Konsole öffnen (F12)
2. Network Tab öffnen
3. Nach "/api/reviews" POST-Request suchen
4. Status Code prüfen:
   - ✅ 201: Erfolg
   - ❌ 400: Validierungsfehler (Response lesen)
   - ❌ 401: Nicht angemeldet

## Quick-Test Script

### Browser-Konsole (F12) ausführen:
```javascript
// Test 1: Ist Benutzer angemeldet?
console.log('Token:', localStorage.getItem('token') ? 'Ja' : 'Nein');

// Test 2: User-Daten
const user = JSON.parse(localStorage.getItem('user') || '{}');
console.log('User:', user.email, 'Role:', user.role);

// Test 3: API Test
fetch('/api/auth/me', {
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
})
.then(r => r.json())
.then(d => console.log('Auth Check:', d))
.catch(e => console.error('Auth Failed:', e));
```

## Backend-Test (ohne Frontend)

```bash
# Login
TOKEN=$(curl -s -X POST https://trust-ratings-app.preview.emergentagent.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"sarah.klein@demo.com","password":"password123"}' | jq -r '.token.access_token')

# Shop-ID holen
SHOP_ID=$(curl -s https://trust-ratings-app.preview.emergentagent.com/api/shops | jq -r '.data[0].id')

# 5-Sterne-Review erstellen
curl -X POST https://trust-ratings-app.preview.emergentagent.com/api/reviews \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"shop_id\": \"$SHOP_ID\",
    \"rating\": 5,
    \"comment\": \"Backend-Test erfolgreich!\"
  }"
```

**Falls dieser Test funktioniert, liegt das Problem im Frontend!**

## Support-Informationen sammeln

Wenn das Problem weiterhin besteht, sammeln Sie diese Informationen:

1. **Browser & Version** (Chrome, Firefox, Safari)
2. **Screenshot** vom Bewertungsformular (mit geöffneter Browser-Konsole)
3. **Fehlermeldungen** aus Browser-Konsole (F12 → Console)
4. **Network-Logs** (F12 → Network → Filter "reviews")
5. **Welcher Benutzer** (Email)
6. **Welcher Shop** (Name oder ID)
7. **Welche Sternzahl** (1-3 oder 4-5)

Mit diesen Informationen kann ich das Problem genau identifizieren!

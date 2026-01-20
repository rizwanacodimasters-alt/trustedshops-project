# 🔐 TESTBENUTZER - ZUGANGSDATEN

## System-URL
**Frontend**: https://trust-ratings-app.preview.emergentagent.com

---

## 👨‍💼 ADMINISTRATOR-ACCOUNTS

### Admin 1 (Haupt-Administrator)
- **Email**: `admin@trustedshops.de`
- **Passwort**: `admin123`
- **Name**: Admin Hauptmann
- **Rolle**: Administrator
- **Status**: ✅ Verifiziert & Aktiv
- **Login getestet**: ✅ Funktioniert (24.11.2024)
- **E-Mail-Verifizierung**: ❌ Nicht erforderlich (Auto-Verifizierung)

**Berechtigungen:**
- ✅ Alle Bewertungen ansehen und freigeben/ablehnen
- ✅ Benutzer verwalten
- ✅ Shops verwalten und verifizieren
- ✅ Sicherheits-Monitoring
- ✅ Statistiken ansehen

**Zugriff auf:**
- Dashboard: `/admin`
- Review-Verwaltung: Bewertungen freigeben (1-3 Sterne)
- User-Verwaltung: Benutzer sperren/aktivieren
- Shop-Verifikation: Shops verifizieren

---

## 🏪 SHOP-BESITZER-ACCOUNTS

### Shop-Besitzer 1
- **Email**: `hans.mueller@shop.de`
- **Passwort**: `shop123`
- **Name**: Hans Müller
- **Rolle**: Shop Owner
- **Status**: ✅ Verifiziert & Aktiv
- **Login getestet**: ✅ Funktioniert (24.11.2024)

**Berechtigungen:**
- ✅ Eigene Shops erstellen und verwalten
- ✅ Bewertungen für eigene Shops einsehen
- ✅ Auf Bewertungen antworten
- ✅ Shop-Verifizierung beantragen
- ✅ Abonnements verwalten (Stripe)

**Zugriff auf:**
- Dashboard: `/shop-dashboard`
- Shop erstellen: "Neuer Shop" Button
- Bewertungen verwalten: Reviews Tab
- Rechnungen: Billing Tab

---

### Shop-Besitzer 2
- **Email**: `maria.schmidt@shop.de`
- **Passwort**: `shop123`
- **Name**: Maria Schmidt
- **Rolle**: Shop Owner
- **Status**: ✅ Verifiziert & Aktiv
- **Login getestet**: ✅ Funktioniert (24.11.2024)

**Berechtigungen:**
- Gleiche wie Shop-Besitzer 1

---

## 👤 KUNDEN-ACCOUNTS (Shopper)

### Kunde 1
- **Email**: `sarah.klein@demo.com`
- **Passwort**: `password123`
- **Name**: Sarah Klein
- **Rolle**: Shopper (Kunde)
- **Status**: ✅ Verifiziert & Aktiv
- **Login getestet**: ✅ Funktioniert (24.11.2024)

**Berechtigungen:**
- ✅ Shops suchen und ansehen
- ✅ Bewertungen schreiben (mit Nachweisen für 1-3 Sterne)
- ✅ Eigene Bewertungen bearbeiten/löschen
- ✅ Shops als Favoriten markieren
- ✅ Benachrichtigungen empfangen

**Zugriff auf:**
- Dashboard: `/my-dashboard`
- Bewertungen schreiben: Auf jedem Shop
- Eigene Bewertungen verwalten: Dashboard → Bewertungen Tab

---

### Kunde 2
- **Email**: `max.mustermann@test.de`
- **Passwort**: `password123`
- **Name**: Max Mustermann
- **Rolle**: Shopper (Kunde)
- **Status**: ✅ Verifiziert & Aktiv

**Berechtigungen:**
- Gleiche wie Kunde 1

---

### Kunde 3 (Test-Account)
- **Email**: `test@review.de`
- **Passwort**: `test123`
- **Name**: Test Reviewer
- **Rolle**: Shopper (Kunde)
- **Status**: ✅ Verifiziert & Aktiv

**Hinweis**: Dieser Account wurde für Backend-Tests erstellt

---

## 📋 TEST-SZENARIEN

### Szenario 1: Review mit hoher Bewertung (Kunde)
1. Login als: `sarah.klein@demo.com` / `password123`
2. Zu `/shops` navigieren
3. Einen Shop auswählen (noch nicht bewertet)
4. "Bewertung schreiben" klicken
5. **5 Sterne** auswählen
6. Kommentar schreiben (z.B. "Exzellenter Service!")
7. "Bewertung veröffentlichen" klicken
8. **Erwartet**: Sofortige Veröffentlichung, Toast-Nachricht

### Szenario 2: Review mit niedriger Bewertung (Kunde)
1. Login als: `max.mustermann@test.de` / `password123`
2. Zu `/shops` navigieren
3. Einen Shop auswählen
4. "Bewertung schreiben" klicken
5. **2 Sterne** auswählen
6. **Gelber Bereich erscheint**: "Nachweis erforderlich"
7. Kommentar schreiben
8. **Bestellnummer eingeben**: z.B. "ORD-2024-12345"
9. **Bild hochladen**: PNG/JPG auswählen
10. "Bewertung veröffentlichen" klicken
11. **Erwartet**: Status "Pending", Toast "Wartet auf Admin-Freigabe"

### Szenario 3: Bewertung bearbeiten (Kunde)
1. Login als: `sarah.klein@demo.com` / `password123`
2. Zu `/my-dashboard` navigieren
3. Tab "Bewertungen" öffnen
4. Bei einer Bewertung auf **Stift-Icon** klicken
5. **Alle Felder sind vorausgefüllt** (Text, Sterne, ggf. Bilder)
6. Änderungen vornehmen
7. "Speichern" klicken
8. **Erwartet**: Aktualisierung erfolgreich

### Szenario 4: Bewertung freigeben (Admin)
1. Login als: `admin@trustedshops.de` / `admin123`
2. Zu `/admin` navigieren
3. Tab "Bewertungen" oder "Reviews" öffnen
4. Filter auf "Pending" setzen
5. Bewertung mit 1-3 Sternen ansehen
6. **Nachweise prüfen**: Bestellnummer + Fotos
7. "Freigeben" oder "Ablehnen" klicken
8. Bei Ablehnung: Grund angeben
9. **Erwartet**: Status ändert sich, Benutzer sieht Update

### Szenario 5: Shop erstellen (Shop-Besitzer)
1. Login als: `hans.mueller@shop.de` / `shop123`
2. Zu `/shop-dashboard` navigieren
3. "Neuer Shop" oder "Shop erstellen" klicken
4. Formular ausfüllen:
   - Name, Website, Kategorie (Pflichtfelder)
   - Optional: Logo, Bild, Beschreibung, E-Mail, Telefon, Adresse
5. "Shop erstellen" klicken
6. **Erwartet**: Shop erscheint in der Liste

### Szenario 6: Auf Bewertung antworten (Shop-Besitzer)
1. Login als: `maria.schmidt@shop.de` / `shop123`
2. Zu `/shop-dashboard` navigieren
3. Tab "Bewertungen" öffnen
4. Bei einer Bewertung "Antworten" klicken
5. Antwort schreiben
6. "Antwort senden" klicken
7. **Erwartet**: Antwort erscheint unter der Bewertung

---

## 🚨 WICHTIGE HINWEISE

### Bekannte Einschränkungen:
1. **Ein Shop = Eine Bewertung**: Jeder Benutzer kann einen Shop nur einmal bewerten
2. **Passwort-Hashing**: Neue Benutzer über Registrierung erstellen (funktioniert)
3. **E-Mail-Verifizierung**: Muss aktiviert sein für Dashboard-Zugang

### Fehlerbehebung:
- **"Sie haben diesen Shop bereits bewertet"**: Anderen Shop wählen
- **Login funktioniert nicht**: Stellen Sie sicher, dass Sie die richtigen Passwörter verwenden
- **Dashboard nicht erreichbar**: E-Mail-Verifizierung prüfen

### Browser-Konsole Debug (F12):
```javascript
// Prüfen ob angemeldet
console.log('Token:', localStorage.getItem('token') ? 'Ja' : 'Nein');

// User-Info anzeigen
console.log('User:', JSON.parse(localStorage.getItem('user') || '{}'));
```

---

## 📊 STATISTIK

**Gesamt-Benutzer im System**: 6
- 👨‍💼 Administratoren: 1
- 🏪 Shop-Besitzer: 2
- 👤 Kunden: 3

**Alle Accounts sind:**
- ✅ E-Mail verifiziert
- ✅ Aktiv
- ✅ Sofort einsatzbereit

---

## 🔄 WEITERE TESTBENUTZER ERSTELLEN

Falls Sie weitere Testbenutzer benötigen, können Sie:

1. **Über die Registrierung** (empfohlen):
   - Zu `/signup` navigieren
   - Formular ausfüllen
   - Nach Registrierung E-Mail in der Datenbank auf `email_verified: true` setzen

2. **Über die Datenbank** (für Entwickler):
   ```python
   # Siehe /app/DEBUG_GUIDE.md für Skripte
   ```

---

**Letzte Aktualisierung**: 24. November 2024
**System-Version**: 1.0
**Status**: ✅ Alle Accounts funktionsfähig

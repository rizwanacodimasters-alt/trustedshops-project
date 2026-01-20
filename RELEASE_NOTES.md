# Release Notes - Review System Update

## Datum: 24.11.2024

### ✅ Behobene Probleme

#### 1. Review-Abgabe funktioniert jetzt korrekt
- **Problem**: Der "Bewertung veröffentlichen" Button hat nicht funktioniert
- **Ursache**: HTML5 `required`-Attribut auf verstecktem File-Input blockierte das Submit
- **Lösung**: `required`-Attribut entfernt, Validierung erfolgt jetzt in JavaScript

#### 2. Customer Dashboard - Verbesserte Review-Anzeige
- **NEU**: Status-Badges für Bewertungen:
  - 🟠 "Wartet auf Freigabe" (pending)
  - 🟢 "Freigegeben" (approved)
  - 🔴 "Abgelehnt" (rejected)
- **NEU**: Anzeige der eingereichten Nachweise:
  - Bestellnummer wird angezeigt
  - Hochgeladene Produktfotos in Galerie-Ansicht
  - Fotos können durch Klick vergrößert werden
- **NEU**: Ablehnungsgründe werden angezeigt (admin_notes)

#### 3. Success-Toast-Nachrichten
- **4-5 Sterne**: "Ihre Bewertung wurde erfolgreich veröffentlicht."
- **1-3 Sterne**: "Ihre Bewertung wurde zur Prüfung eingereicht und wird nach der Genehmigung veröffentlicht."

### 📝 Technische Details

#### Geänderte Dateien:
- `/app/frontend/src/components/ui/image-upload.jsx`
  - Entfernung des `required`-Attributs
  - Verbessertes State-Management für Bild-Vorschauen
  - Memory-Optimierung mit `URL.revokeObjectURL()`

- `/app/frontend/src/pages/CustomerDashboard.jsx`
  - Status-Badge-Anzeige hinzugefügt
  - Proof-Anzeige-Sektion implementiert
  - Admin-Notes-Anzeige bei Ablehnung

### 🧪 Getestete Benutzer

- **sarah.klein@demo.com** / password123 (verifiziert)
- **max.mustermann@test.de** / password123 (verifiziert)

### 📋 Nächste Schritte (noch offen)

1. **Admin Dashboard**: Sicherstellen, dass Admin nur ansehen und freigeben kann (nicht bearbeiten)
2. **Benutzernamen**: "Anonymous User" Problem beheben (Backend-Lookup)
3. **Edit-Funktion**: Benutzer sollen Nachweise nachträglich bearbeiten können

### ⚠️ Bekannte Einschränkungen

- Benutzer können einen Shop nur einmal bewerten
- Bei Ablehnung durch Admin kann der Benutzer die Bewertung löschen und neu einreichen
- Bilder werden als Base64 gespeichert (kann bei vielen Bildern Speicherplatz beanspruchen)

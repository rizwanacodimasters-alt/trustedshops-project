# Dashboard Features - Implementierungsplan

## Fehlende & Zu verbessernde Features

### 🔴 PRIORITÄT 1 (Kritisch - Sofort implementieren)

1. **Profilbild-Upload**
   - Benutzer sollen Profilbilder hochladen können
   - Backend: File Upload Route erstellen
   - Frontend: Upload-Komponente im MyAccount/Profile
   - Speicherung: Base64 oder File-Upload mit persistentem Storage

2. **Review-Bearbeitung**
   - Kunden sollen ihre eigenen Reviews bearbeiten können
   - Backend: PUT /api/reviews/{review_id} Route
   - Frontend: Edit-Button in Reviews-Liste
   - Validierung: Nur eigene Reviews bearbeitbar

3. **Shop-Namen korrekt anzeigen**
   - Bug: Reviews zeigen "Unknown Shop" statt echten Namen
   - Backend: Aggregation-Pipeline prüfen/fixen
   - Frontend: Shop-Name korrekt aus API-Response anzeigen

### 🟡 PRIORITÄT 2 (Wichtig - Nach P1)

4. **Account-Deaktivierung/Löschung**
   - Benutzer sollen Account deaktivieren können
   - Backend: PATCH /api/users/me/deactivate, DELETE /api/users/me
   - Frontend: Einstellungen-Seite mit Bestätigung
   - Daten: Soft-Delete vs Hard-Delete

5. **Passwort-Änderung verbessern**
   - Aktuell: Timeout-Probleme
   - Backend: POST /api/auth/change-password
   - Frontend: Formular im MyAccount verbessern
   - Validierung: Altes Passwort verifizieren

6. **Pagination/Load More**
   - Reviews-Liste: Load More Button
   - Favorites-Liste: Load More
   - Notifications-Liste: Load More
   - Backend: Pagination bereits vorhanden
   - Frontend: Load More UI implementieren

### ✅ BEREITS IMPLEMENTIERT

- ✅ E-Mail-Verifizierung (Customer & Shop Owner)
- ✅ ProtectedRoute (Zugriffsschutz)
- ✅ Dashboard Overview (Statistiken)
- ✅ Reviews anzeigen & sortieren
- ✅ Notifications anzeigen & als gelesen markieren
- ✅ Profil bearbeiten (Name, Email, Phone)
- ✅ Favorites-Tab (leer anzeigen funktioniert)

## Implementierungsreihenfolge

1. Shop-Namen Fix (Quick Win)
2. Profilbild-Upload
3. Review-Bearbeitung
4. Load More Pagination
5. Account-Deaktivierung
6. Passwort-Änderung verbessern

## Testing-Strategie

Nach jeder Feature-Implementierung:
1. Backend-Tests mit curl/testing-agent
2. Frontend-Tests mit screenshot-tool
3. E2E-Tests mit auto_frontend_testing_agent

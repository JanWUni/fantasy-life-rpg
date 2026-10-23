# Unreal-Ansicht der Studien A und B

Status: **review_ready**, keine Abnahme. Worktree `E:/Business/fantasy-rpg-refiner`, Branch `assets/refiner`.
Der Nutzer hat die Unreal-Ansicht beider zuvor in Blender geprüften Glasstudien beauftragt.

## Ergebnis und Herkunft

- A: `EC.HighCultureCity / StreetStudy01`, 21 Meshes, 470 HISM-Instanzen, 24 Scheiben.
- B: `ER.RootRetreat / CourtyardStudy01`, 27 Meshes, 318 HISM-Instanzen, 14 Scheiben.
- Geometrie aus Refiner-Lieferung `17828dce95c0d68fd5300bc9d8cba1db1178b83f`; Glasstände und SHA256 in `manifest.json` und `plan.json`. Alle 48 verwendeten FBX-Hashes erneut geprüft. Die beiden Blender-Maßfiguren sind nicht exportiert; der vorhandene Spieler dient dem Größenvergleich.
- Zwei neue wiederverwendbare Blueprints, elf eigene Materialien und 48 Meshes, ausschließlich unter den eigenen StudyA/StudyB/StudyAB-Content-Pfaden. Lab ausdrücklich gespeichert. Keine Änderung an gemeinsamen Materialien, Generatoren, Konfiguration oder Gameplay-Code; kein Commit/Push.
- Lab-Offsets in cm: A `(4300,-900,31)`, B `(4300,2500,31)`, Rotation null und Skalierung eins. Bestehende 399 Actors mit Transform, Ordner, Mesh und Materialbelegung erhalten.

## Tatsächliche Prüfungen

Legacy-FbxFactory verwendet, keine Interchange-Abnahme. Importierte Bounds, Dreieckzahlen, Slot-Reihenfolge und alle Instanztransformationen mit Manifest verglichen. Blender-Zuordnung `UE_cm=(100*B.x,-100*B.y,100*B.z)`, UE-Yaw negativ zum Blender-Yaw. Ein zunächst fehlerhaft positional konstruierter Python-Rotator wurde mit benannten Feldern korrigiert; Abschlussprüfung danach bestanden (`rotation_correction.json`, `lab_verification.json`).

57/158 UCX-Hüllen aus den Quellen erhalten. Je Studie eine einfache Box für Glas und Pflaster ergänzt, insgesamt vier Boxen. Sechs Kapselabfragen mit tatsächlichen Spielermaßen Radius 35/Halbhöhe 90 cm prüfen die drei A-Eingänge sowie B-Eingang und zwei Innenverbindungen. Bodenauflagen und alle 38 Scheiben physisch geprüft. Diese Abfragen sind kein manueller Rundgang.

Das eigene Glasmaterial dupliziert den zuvor geprüften Substrate-SimpleVolume-Ansatz, Roughness .025 und hohe Transmission. Glasschatten sind deaktiviert, Rahmenschatten erhalten: Tageslicht kann eintreten; dies ist eine praktische Näherung ohne validierte refraktive Kaustik. Farben/Rauheiten der festen Materialien sind angenähert; Blender-Prozeduraldetails wurden nicht automatisch übertragen. Keine Beleuchtungsänderung am Lab.

`Previews/` enthält tatsächliche Unreal-Bilder beider Übersichten und Fenster innen/außen. `PIE_B.png` zeigt den laufenden Spielmodus. `pie_live.json` belegt den vorhandenen BP_PrototypeCharacter und beide vollständigen Assemblies in der PIE-Welt. Start vor B; A liegt südlich dahinter. Zum Erkunden in die Spielansicht klicken, WASD/Maus; F6 öffnet die vorhandene Entwickler-Toolbox mit Flug/Freikamera.

## Erhaltung und Sitzungseinschränkungen

`file_preservation.json` vergleicht sämtliche zuvor erfassten Dateien byteweise. Nur die ausdrücklich beauftragte Lab-Karte darf gegenüber diesem Arbeitsbaseline abweichen. Der bereits zuvor extern gespeicherte A-Blend-Stand und alle anderen vorhandenen Änderungen bleiben erhalten. Die Vorabkopie der Lab-Karte liegt ignoriert unter `Saved/StudyABIntegration/Before/`.

Ein erster Editorprozess stürzte beim automatischen Speichern von Engine-Hilfsmeshes ab. Recovery-Dateien wurden gesichert; in der aktuellen Sitzung ist Autosave nur im Speicher pausiert, ohne SaveConfig. Ein weiterer Realtime-API-Aufruf erzeugte einen nichtfatalen Engine-Ensure und wurde aus dem Prüfskript entfernt. Kein fehlerfreier Engine-Lauf wird behauptet.

Die automatische Freigabeprüfung lehnte einen Neustart wegen zahlreicher ungespeicherter Game-Pakete und möglichem Änderungsverlust ab. Es erfolgte kein Umgehen dieser Sperre und kein Verwerfen dieser Pakete. Stattdessen bleibt die laufende Sitzung offen. Importer-Vorgaben, Interchange-CVar und Hintergrund-/Slate-Throttling wurden wiederhergestellt; Autosave bleibt wegen des beobachteten Absturzes für diese Sitzung pausiert (`session_preserved.json`). Keine globale Save-All-Aktion.

## Offen

- Nutzerbewertung von Maßstab, Silhouette, Glas und Innenraum; manueller Rundgang.
- Sicherer Neustart mit Prüfung der gespeicherten Pakete, sobald die übrigen ungespeicherten Änderungen geklärt sind; bislang keine Reload-Abnahme.
- Materialdetails, Licht-/Belichtungsabstimmung, Zielplattform/Performance und kontrollierter Reimport vor Produktionsfreigabe.
- Keine neue Lore-/Architekturkanon-Festlegung und keine Abnahme als fertiges Endprodukt.

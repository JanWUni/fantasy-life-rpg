# Kleinere Fenster für den separaten Wandkatalog

Status **review_ready**, nicht accepted. Nutzerfeedback: Fenster zu groß; Farbwirkung passt noch nicht zu den Elfenhäusern. Beauftragt ist vorerst die Verkleinerung. Die drei Wandvarianten bleiben Auswahlmuster; ihre Farb-/Stileignung ist ausdrücklich offen.

## Änderung

Nur die drei Fensterwände des Katalogs, deren separater Rahmen und die Glasscheibe wurden geometrisch aktualisiert. Öffnung zuvor120×152cm, jetzt65×90cm; Brüstung100→135cm, Kopf maximal252→225cm. Orientierung an den vorhandenen Hausstudien mit65×80cm-Scheiben. Rahmen und Glas sind in der Geometrie verkleinert, die sechs eingesetzten Instanzen aufZ137cm im Lab angehoben (WandbasisZ2 + Brüstung135). Keine Actor-Skalierung zur Größenkorrektur.

Wandaußenmaße300×24×320cm, Startpivot, Endanschlüsse, Holz-/Steindekor, Materialslots sowie alle Farben und Texturen bleiben erhalten. Glas weiterhin durchsichtig und physisch blockierend. Unberührt: geschlossene Katalogwände, Möbel, Lampen und sämtliche Häuser.

Neue editierbare Quelle `WindowResize02.blend`; der bisherige Katalog bleibt unverändert als Vorrevision erhalten. Fünf neue FBX in `Exports/`. Dieselben fünf eigenen Unreal-Assetpfade wurden ausdrücklich mit Legacy-FbxFactory aktualisiert, Referenzen und Materialien erhalten. Nominale Assetnamen bleiben zur Referenzerhaltung bestehen; maßgeblich sind die gemessenen Bounds im Manifest. Fenstervertrag ist nun `draft_2_window`; der bestehende äußere Wandanschluss bleibt unverändert.

## Prüfbelege

- Neue Quelle erneut geöffnet, verwendete externe Texturen aufgelöst und alle fünf FBX zurückimportiert: Bounds, Dreiecke, Slots und UCX erhalten; keine degenerierten UV-Dreiecke oder nichtmannigfaltigen Kanten. Alle sechs anderen Module in der Quelle in Größe, Dreiecken und Slots erhalten. Ein beim ersten Speichern fehlerhafter relativer Texturpfad wurde vor Abschluss korrigiert und erneut geprüft.
- Tatsächlicher Unreal-Legacy-Reimport: fünf Meshes, unveränderte Slots/Materialreferenzen und Kollisionsanzahlen. Keine Interchange-Abnahme.
- Für jede Variante reale einfache Sichtbarkeitsabfragen: neue Scheibe blockiert; ohne sie ist die neue Öffnung frei. Neue seitliche Wandfüllung, höhere Brüstung und tieferer Sturz blockieren. Eine zusätzliche Abfrage mit ignorierter Wand belegt, dass außerhalb der kleineren Scheibe keine alte übergroße Glaskollision übrig ist.
- Sämtliche vorab erfassten Lab-Actors geprüft; ausschließlich die sechs bezeichneten Fenstereinsätze dürfen ihre Höhe ändern. Häuser, sonstige Transformationen, Meshreferenzen, Ordner und Material-Overrides erhalten.
- Dateihashes über den gesamten Eingangsbestand geprüft: ausschließlich fünf bezeichnete eigene Unreal-Meshpakete und die Lab-Karte dürfen abweichen. Bisherige Blender-Quellen, gemeinsame Materialien, Texturen, Config, Tools und Gameplay bleiben unverändert.
- Blender- und Unreal-Bilder unter `Previews/` tatsächlich angesehen. Lab-Spielmodus nach der Bearbeitung vor dem kleineren B-Fenstermuster wieder gestartet; kein vollständiger manueller Rundgang behauptet.

## Übergabe

Maßauswahl und visuelle Abnahme stehen aus. Die vorläufigen Farben sind keine bestätigte elfische Stilvorgabe. Kein Neustart oder Verwerfen fremder ungespeicherter Pakete; sitzungsweise Importdefaults wiederhergestellt. Autosave bleibt im vorher pausierten Zustand. Saubere Paket-Reload-Prüfung weiterhin offen. Kein Commit/Push und keine neue Kultur-/Architekturfestlegung.

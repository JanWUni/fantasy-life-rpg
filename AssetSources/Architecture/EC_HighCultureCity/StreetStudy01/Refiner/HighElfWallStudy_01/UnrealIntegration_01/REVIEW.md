# Hochelfen-Wände – Unreal-Vergleich 01

Status **review_ready**, keine Produktionsabnahme. Nutzerauftrag: beide gezeigten Wandvarianten so ins Refiner-Lab übernehmen. Geschlossene Wand, Türöffnung und separate Tür sind die nächsten geplanten Module, in diesem Import noch nicht erstellt.

## Quelle und Umfang

Worktree `E:/Business/fantasy-rpg-refiner`, Branch `assets/refiner`. Geprüfte Eingangsquelle `../HighElf_WallVariants_01.blend`, SHA256 `a7661b62ce555d4aac13b85d4cb16aa18471f3e5f428b720abdfa92871864e6a`. Eigene Exportkopie `HighElf_Export_01.blend`, 9 FBXs und 15 gebackene Texturen. Eingangsgeometrie, Häuser, ältere Wände und gemeinsame Materialien unverändert.

Unreal: 9 neue Meshes, 6 private Materialien, 15 Texturen und 2 statische Baugruppen-Blueprints unter `/Game/Art/{Architecture,Materials,Textures}/HighElfWallStudy01`. Gleicher Kern, Rahmen und Glas werden von beiden Varianten gemeinsam verwendet. Blueprint enthält 6 Mesh-Komponenten, keine hinzugefügte Gameplay-Logik. Glas bleibt separat und wirft keinen Schatten; kein verstecktes Innenlicht ergänzt.

Die allein stehenden Vergleichswände liegen im Lab bei A `(1600,3100,2)` und B `(2200,3100,2)` cm. Eine zweite A/B-Kombination bei `(1600,2350,2)` / `(1900,2350,2)` prüft den 300-cm-Stoß. Outliner: `Lab/Architecture/HighElfWallStudy01`.

## Übertragung und tatsächliche Prüfungen

- Blender 5.2.2: Quelle erneut geöffnet, neun FBX-Rückimporte hinsichtlich Dreiecken, Bounds, Slots und Hüllenzahl bestanden.
- Kalibriertes FBX_SCALE_NONE, Forward -Y / Up Z, UE_cm=(100*x,-100*y,100*z). Keine zusätzliche Spiegelung oder negative Skalierung. Unreal 5.8 via MCP `StaticMeshTools.import_file` mit explizitem Legacy-FbxFactory-Import; tatsächlich gespeicherte Importdaten an allen 9 Meshes `FbxStaticMeshImportData`.
- Tatsächliche Unreal-Bounds mit Blender abgeglichen, Fehler unter 0,002 cm. Dreiecke und Slots erhalten. Kern 15 konvexe Hüllen, separate Scheibe 1 Hülle; Zierwerk und Rahmen ohne blockierende Hülle.
- Vier unskalierte Baugruppen geprüft. Einfacher Kollisionstrace von beiden Seiten trifft am Fenster zuerst die Scheibe; seitlicher Wandkern, Brüstung und Sturz blockieren. Beidseitige Kapseltests (Radius 35 / Halbhöhe 90 cm) blockieren an beiden Wänden und lassen den Zwischenraum frei. Zwei Traces am Modulstoß bestehen.
- 434 vorhandene Actors inklusive Haus-Transforms, Meshreferenzen und Material-Overrides unverändert. Von 1959 vorhandenen Dateien nur die ausdrücklich beauftragte Lab-Karte geändert; alte Assetdateien bytegleich. Neue Assets und die Lab-Karte einzeln gespeichert, kein Save All.
- Importdefaults und Sitzungs-CVar wiederhergestellt. Keine Projektkonfiguration geändert. Editor nicht neu gestartet, keine fremden dirty Packages verworfen.

## Materialien und Grenzen

Blender-BaseColor, Rauheit und Mikro-Normalen als 1024²-PNG je fünf opaken Materialfamilien gebacken. 1-m-Materialausschnitt auf einer Fläche, UV0-Kachelung: eine Näherung der ursprünglichen räumlichen Noise-Verteilung, keine pixelidentische 3D-Shaderübertragung. Grundpalette und Rauheitsbereiche stammen aus der gewählten Quelle. Normalkarten in Unreal mit invertiertem Grünkanal. Klares Glas verwendet eine eigene Kopie des bereits geprüften Substrate-Glasmaterials.

A: 3.912 Dreiecke pro kompletter Wand, B: 9.860; sechs Materialfamilien pro Baugruppe. Diese Detailstudien überschreiten die Prototyp-Reviewschwelle für einfache Wände. Optimierung, LODs und Siedlungsperformance bleiben offen. Nanite aus. Keine Packaging-/Multiplayer-Abnahme.

Sauberes Editor-/Karten-Neuladen bleibt offen, da die laufende Sitzung bereits andere ungespeicherte Pakete enthält, die erhalten bleiben. Vorhandene Datei-Hashes beweisen nicht die Erhaltung ungespeicherter Editorzustände; deswegen kein erzwungener Neustart. Reimportfestigkeit dieser neuen Baugruppen ist noch separat zu prüfen. Status bleibt review_ready.

Keine Commits oder Pushes in diesem Auftrag. Blender-Ausgangsdatei und deren vorherige Dokumentation bleiben als eigener historischer Stand erhalten.

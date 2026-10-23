# Architekturstudie A – kultivierte Stein-/Holzstraße nach Bild 33

Stand: 23. Oktober 2026. Status **creator_ready**, ausschließlich auf Creator-/Blender-Ebene; Sichtentscheidung steht aus.

## Auftrag und Identität

- KitId `EC.HighCultureCity`, ModuleId `StreetStudy01`, InterfaceVersion **0.1**, Studienrevision **1**.
- Tatsächliche Ausgangsrevision `e66d5beed7bb85313501659d646f25778515134b` auf `assets/creator`, Worktree `E:\Business\fantasy-rpg-creator`. Zu Beginn sauber; kein Zurücksetzen, Merge oder Branchwechsel.
- Einziger Schreibbereich: `AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Creator/`. Neue, eigenständige Studie; das alte Blatthof-/Innenwand-Modul bleibt eingefroren.
- Die beiden tatsächlichen Referenz-PNGs wurden vor Modellierung angesehen. Diese Studie nutzt Bild 33; lokale Kopie unter `References/`, Hash `195a27381b9088b2f095ddfc4ab4d6c29add66e7626060700fe29c94c1af678f`. Bildreferenz ist kein maßhaltiger Bauplan.
- Aktuelle Hauptrepo-Grundlagen ergänzend nur gelesen. Einzelne Dokumenthashes und Herkunft stehen im Manifest; keine Dokumente angleichen oder Kanon ergänzen.

## Gestaltung und Prototypmaße

Drei 7 × 8 m große eingeschossige Hausprototypen mit 3,9 m Wandkrone. Haus A hat ein flach gewalmtes Dach bis 5,4 m, Haus B ein niedrigeres Dach bis 5,0 m, Haus C einen kleinen steinernen Eingangsvorbau. Gemeinsame Fassaden-, Seitenwand-, Boden-, Fenster-, Tür- und Ziereinheiten; wiederholte Teile teilen Mesh-Daten. Helle langlebig wirkende Steinflächen, dunkles Schnitzholz, begrenzte Baumreliefs und kleine tiefe Fenster. Zwei geplante Straßenbäume, geordnetes Pflaster; kein Blattdach oder Wurzelhaus. Fassadenabstand 9 m, freie mittlere Straßenbreite etwa 6 m. Alle drei Innenräume bleiben leer und haben Böden und Dachabschluss. Diese Maße sind technische Studienannahmen, keine allgemeinen Baustandards.

Die Studie ist bewusst vereinfachte 3D-Geometrie, keine AI-Illustration. Struktur, Dekor, Türen/Fenster, Boden, Natur und 180-cm-Maßfigur sind in getrennten Collections. Die ausgeblendeten Source-/UCX-Collections liefern editierbare, einzeln exportierbare Bibliotheksobjekte. Szenenobjekte sind Instanzen dieser Mesh-Daten. Keine Gameplay-Tür oder Interaktion.

## Dateien und reproduzierbare Prüfung

- `StreetStudy01.blend`: editierbare Szene und Assetbibliothek; erneut in einem separaten Blender-Prozess geöffnet.
- `Exports/`: **21** FBX-Dateien, jeweils genau ein Render-Mesh plus zugehörige UCX, falls vorhanden. Jede Datei in Blender rückimportiert, Körperzahl, Bounds, Dreiecke und Materialslotnamen geprüft.
- `manifest.json`: vollständige Teileliste, Einzelbounds, Pivots, Instanztransforms, Referenz-/Dokumenthashes, Materialien, Exporthashes, Einschränkungen.
- `verification.json`: tatsächliche Source-/Roundtrip-Messwerte und stichprobenartige Tür-/Boden-/Dachabfragen; kein Unreal- oder Kapselnachweis.
- `preservation.json`: tatsächlicher Vorher-/Nachherabgleich aller 1.072 vorher versionierten Worktree-Dateien; byteidentisch einschließlich des eingefrorenen Innenwand-Moduls. Branch und Ausgangs-HEAD unverändert. Keine Aussage über parallel bearbeitete andere Worktrees.
- `Previews/01_eye_overview.png`, `02_house.png`, `03_plan.png`, `04_interior.png`: echte Blender-Cycles-Render mit neutraler gemeinsamer Tagesbeleuchtung und Maßfigur. Die Innenansicht nutzt zusätzlich eine neutrale, nur im Renderprozess gesetzte Aufhellfläche zur Geometriebeurteilung; sie ist keine geplante Gebäudeleuchte. Aufsicht ist perspektivisch. Keine Render-only-Architektur; Bilder zeigen die gelieferte Szene.
- `build_study.py`: eigenständiger lokaler Blender-Erzeuger/Prüfer/Renderer, ohne gemeinsame Tool-Änderungen. `finalize_delivery.py`: lokale Herkunfts-/Berichtserstellung. `.gitattributes` bewahrt die Lieferbytes.
- `SHA256SUMS`: Hash sämtlicher Lieferdateien außer der Liste selbst. Nicht committed; Commit-/Integrationsfreigabe ist kein Teil dieses Auftrags.

Blender 5.2.2 LTS, Metric / Unit Scale 1.0 / Meter. Zum Prüfen aus einem neuen Blender-Prozess: `--background --factory-startup --python-exit-code 1 --python <absoluter Pfad>/build_study.py -- --mode verify`. Zum Rendern `--mode render`. `build` schützt vorhandene Quellen; `revise` ist nur für ausdrücklich beauftragte Iteration im eigenen Studienordner vorgesehen. Nach jeder Änderung Prüfungen und Hashliste neu erzeugen.

## Neuer technischer Anschlussvertrag

Keine R255-/Blatthof-Kompatibilität. Version **0.1** beschreibt eine Studienzusammenstellung, keinen freigegebenen Baukasten. Exportobjekte haben Translation/Rotation Null und Skalierung Eins; Geometrie und Pivot liegen im eigenen lokalen Bezug. Pivots und lokale Bounds jeder Einheit sowie exakte Instanztranslation/-drehung sind im Manifest. Haus-/Flügelursprung liegt auf Bodenhöhe; Wandfelder werden über ihre im Skript/Manifest dokumentierten End-/Ebenenmaße gefügt. Vollständige Anschlussprofile erst nach Sichtauswahl als Produktionsvertrag festlegen.

Unreal-Ziel: Zentimeter, `UE_cm=(100*B.x,-100*B.y,100*B.z)`. Blender -Y entspricht Unreal +Y. Keine zusätzliche Spiegelung oder negative Objektskalierung. Kalibriertes Exportprofil: **FBX_SCALE_NONE**, global_scale 1, apply_unit_scale true, Forward -Y, Up Z, use_space_transform true, bake_space_transform false. Auswahl ausschließlich MESH; Modifier/kontrollierte Triangulierung, FACE-Smoothing, Tangenten. Keine Kamera, Lichter, Animation oder eingebetteten Texturen im FBX. Kamera/Licht bleiben nur in der Blender-Review-Szene.

## Geometrie, Materialien und Kollision

**3034 Dreiecke** über die einzigartigen exportierten Render-Einheiten; **57 UCX-Körper** über die einzigartige Bibliothek. Diese Summen sind keine Instanz-/Draw-Call- oder Laufzeitmessung. Die vollständige Szene enthält zusätzliche Instanzen und die Maßfigur. Je ein UV0-Kanal mit metrischen Flächenprojektionen; absichtliche Überlappungen für einfache Kachelflächen. Keine Produktions-UVs oder finale Lightmap-UVs. Source-Normalen und geschlossene Meshkomponenten geprüft. Mehrteilige Dekor-/Baumgeometrie darf sich als zusammengefasste Studiengruppe absichtlich überschneiden; kein boolesch vereinigtes Produktionsmodell behauptet.

| Einheit | Dreiecke | UCX | Materialslots |
| --- | ---: | ---: | --- |
| `SM_EC_Facade_700x390` | 164 | 23 | Stone |
| `SM_EC_SideWall_800x390` | 100 | 13 | Stone |
| `SM_EC_RearWall_700x390` | 100 | 13 | Stone |
| `SM_EC_Floor_700x800` | 12 | 1 | StoneFloor |
| `SM_EC_HipRoof_790x890` | 12 | 1 | Slate |
| `SM_EC_HipRoof_LowVariant_790x890` | 12 | 1 | Slate |
| `SM_EC_PorchPosts_220x270` | 24 | 2 | StoneLight |
| `SM_EC_PorchRoof_240x150` | 12 | 1 | Slate |
| `SM_EC_StoneDressings` | 344 | 0 | StoneLight |
| `SM_EC_EntryWoodArch` | 236 | 0 | Wood |
| `SM_EC_TreeRelief` | 268 | 0 | StoneLight |
| `SM_EC_DoorLeaf_140x235` | 12 | 1 | Wood |
| `SM_EC_CityWindowFrame_65x80` | 124 | 0 | Wood |
| `SM_EC_CityWindowGlass_65x80` | 12 | 0 | Glass |
| `SM_EC_CityShutter_32x84` | 12 | 0 | Wood |
| `SM_EC_Paving_120x80` | 12 | 0 | StoneFloor |
| `SM_EC_GroundBase_3200x3000` | 12 | 1 | Soil |
| `SM_EC_Curb_100x20` | 12 | 0 | StoneLight |
| `SM_EC_PlanterRim` | 12 | 0 | Stone |
| `SM_EC_StreetTreeTrunk` | 342 | 0 | Wood |
| `SM_EC_StreetTreeCrown` | 1200 | 0 | Leaves |

Strukturkollision besteht aus einzelnen geschlossenen konvexen Teilkörpern. Öffnungen werden ausgespart; keine komplette Haus-/Hofhülle als UCX. Die vielen Teilkörper der Wandraster sind bewusst einfach prüfbar, aber noch nicht für Laufzeit optimiert. Dekor, Natur, Glas und Detailteile ohne UCX sind im Manifest ausgewiesen. Aufteilung in weitere semantische Produktionsmodule oder Reduktion der Kollisionskörper später gesondert prüfen. Ein LOD, Nanite vorgesehen aus; weitere LODs nur nach Auftrag.

Roughness und Grundfarben stehen je Blender-Material im Manifest. Prozedurales Bump dient nur der Blender-Sichtprüfung, ohne externe Texturen. Blender-Shader werden nicht als vollständig nach Unreal übertragbar behandelt. Keine bestehenden Unreal-Materialien geändert.

## Tatsächlich geprüft und noch offen

Erneutes Source-Öffnen; Einheiten und externe Bibliotheken; nicht entartete, geschlossene Source-Einheiten; alle FBX-Rückimporte mit Materialslots, Dreiecken, Bounds und konvexen UCX. Durchgangsproben: neun horizontale Render-Rays pro bezeichnetem Eingang im zentralen 1,2 × 2,2-m-Freiraum; Boden und Dach an mehreren Innenpunkten getroffen. Die tatsächlichen Einzelresultate stehen in `verification.json`. Kein versteckter geschlossener Wandkörper hinter diesen Eingängen. Statische Türblätter sind geöffnet angeordnet.

Nicht geprüft: kontinuierliches Kapselvolumen, alle Fenster-/Nahtkontakte, Innenkamera-Clipping, Unreal-Import/-Reimport/Materialzuordnung/Lightmap-Erzeugung, PIE, Packaging, Multiplayer, Performance, fertige Vegetation oder Produktionsqualität. Kleine Fenster sind opake/transmissive Glasplatzhalter; keine besondere Glas- oder Beleuchtungstechnologie. Review-Schwellen gelten je Produktionsteil; zusammengesetzte Studiengruppen sind gegebenenfalls später aufzuteilen.

Blender meldete lediglich DeprecationWarnings zu use_nodes. Korrigierte explorative Skript-/Prüfversuche sind keine bestandenen Abnahmen; maßgeblich ist der abschließende Prüfbericht. Keine Meldungen unterdrückt.

Nächster Schritt: gemeinsame Sichtprüfung und ausdrückliche Auswahl/Änderungswünsche. Nur danach Refiner-Übernahme als eigene Kopie; vorhandene Creator-Übergaben nicht überschreiben. **Kein Unreal-Import/Reimport, keine Editor-/Level-/Blueprint-/Material-/Config-Änderungen, keine Commits oder Pushes.** Eine spätere Integration benötigt einen benannten Verantwortlichen und den kalibrierten Legacy-Pfad FbxFactory/FbxStaticMeshImportData. Interchange ist nicht validiert; bestehende Kollision niemals pauschal löschen.

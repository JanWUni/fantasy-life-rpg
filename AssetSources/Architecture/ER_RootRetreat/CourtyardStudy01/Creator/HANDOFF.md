# Architekturstudie B – älterer Baumkörper und Wurzelhof nach Bild 23

Stand: 23. Oktober 2026. Status **creator_ready**, ausschließlich auf Creator-/Blender-Ebene; Sichtentscheidung steht aus.

## Auftrag und Identität

- KitId `ER.RootRetreat`, ModuleId `CourtyardStudy01`, InterfaceVersion **0.2**, Studienrevision **2**.
- Tatsächliche Ausgangsrevision `e66d5beed7bb85313501659d646f25778515134b` auf `assets/creator`, Worktree `E:\Business\fantasy-rpg-creator`. Der versionierte Bestand blieb unverändert; die Studien A/B lagen vor dieser Iteration bereits unversioniert vor. Kein Zurücksetzen, Merge oder Branchwechsel.
- Einziger Schreibbereich: `AssetSources/Architecture/ER_RootRetreat/CourtyardStudy01/Creator/`. Neue, eigenständige Studie; das alte Blatthof-/Innenwand-Modul bleibt eingefroren.
- Die beiden tatsächlichen Referenz-PNGs wurden vor Modellierung angesehen. Diese Studie nutzt Bild 23; lokale Kopie unter `References/`, Hash `28dd234d36960c91154452c84d3eb225701985067dd9e93b28e40a06176f6afe`. Bildreferenz ist kein maßhaltiger Bauplan.
- Aktuelle Hauptrepo-Grundlagen ergänzend nur gelesen. Einzelne Dokumenthashes und Herkunft stehen im Manifest; keine Dokumente angleichen oder Kanon ergänzen.

## Gestaltung und Prototypmaße

Vom Nutzer bestätigte Szenenänderung in Revision 2: nur ein Haupteingang am älteren Baumkörper. Die beiden früheren Außentüren der Wohnflügel sind durch kleine Fenster (65 × 80 cm) über geschlossenen Brüstungen ersetzt; die äußeren Türrahmen und Türblätter dort entfallen. Beide Flügel sind nun innen direkt mit dem Baumkörper verbunden. Dafür rücken ihre Mittelpunkte von Y0,4 auf Y3,70 m; die Drehungen −12°/+12° bleiben erhalten. Die inneren Seitenwände erhalten je eine Öffnung von 1,6 × 2,4 m, der Baumkörper zwei korrespondierende seitliche Bogenöffnungen. Ein boolesch vereinigter, geschlossener Renderboden verbindet alle drei Räume auf Z0 ohne doppelte Deckflächen. Drei konvexe Boden-Proxys überlappen auf demselben Niveau absichtlich an den Übergängen. Die gewohnten Rinden-/Wurzelkörper, Baumalter, niedrigen gebogenen Dächer, Kräuterbeete und Sitzplätze bleiben als Stilrichtung erhalten. Die zwei Flügel sind je 6,4 × 5,5 m groß, der alte Körper 5,2 m im Durchmesser und 4,3 m hoch; der alte Baum reicht bis etwa 12,3 m. Dies ist eine bestätigte Zusammenstellungsentscheidung für diese Studie, keine allgemeine Kultur-/Architekturregel. Heilkundige Elfen bleibt eine vorläufige mögliche Nutzungszuordnung.

Die Studie ist bewusst vereinfachte 3D-Geometrie, keine AI-Illustration. Struktur, Dekor, Türen/Fenster, Boden, Natur und 180-cm-Maßfigur sind in getrennten Collections. Die ausgeblendeten Source-/UCX-Collections liefern editierbare, einzeln exportierbare Bibliotheksobjekte. Szenenobjekte sind Instanzen dieser Mesh-Daten. Keine Gameplay-Tür oder Interaktion.

## Dateien und reproduzierbare Prüfung

- `CourtyardStudy01.blend`: editierbare Szene und Assetbibliothek; erneut in einem separaten Blender-Prozess geöffnet.
- `Exports/`: **27** FBX-Dateien, jeweils genau ein Render-Mesh plus zugehörige UCX, falls vorhanden. Jede Datei in Blender rückimportiert, Körperzahl, Bounds, Dreiecke und Materialslotnamen geprüft.
- `manifest.json`: vollständige Teileliste, Einzelbounds, Pivots, Instanztransforms, Referenz-/Dokumenthashes, Materialien, Exporthashes, Einschränkungen.
- `verification.json`: tatsächliche Source-/Roundtrip-Messwerte und stichprobenartige Tür-/Boden-/Dachabfragen; kein Unreal- oder Kapselnachweis.
- `preservation.json`: tatsächlicher Vorher-/Nachherabgleich aller 1.072 vorher versionierten Worktree-Dateien; byteidentisch einschließlich des eingefrorenen Innenwand-Moduls. Branch und Ausgangs-HEAD unverändert. Keine Aussage über parallel bearbeitete andere Worktrees.
- `Previews/01_eye_overview.png`, `02_house.png`, `03_plan.png`, `04_interior.png`: echte Blender-Cycles-Render; die Innenansicht zeigt nun den Übergang vom zentralen Raum zum Westflügel. Zusätzlich `05_connected_plan.png`: orthografische Schnittaufsicht mit ausgeblendeten Dach-/Baummassen und Dekor; ein temporärer Boolean-Schnitt bei Z1,80 m legt Wandöffnungen und den gemeinsamen Boden frei. Diese reine Render-Prüfdarstellung wird nicht in die Quelle gespeichert. Gemeinsame neutrale Tagesbeleuchtung und Maßfigur. Die Innenansicht nutzt eine temporäre neutrale Prüfaufhellung.
- `build_study.py`: eigenständiger lokaler Blender-Erzeuger/Prüfer/Renderer, ohne gemeinsame Tool-Änderungen. `finalize_delivery.py`: lokale Herkunfts-/Berichtserstellung. `.gitattributes` bewahrt die Lieferbytes.
- `SHA256SUMS`: Hash sämtlicher Lieferdateien außer der Liste selbst. Nicht committed; Commit-/Integrationsfreigabe ist kein Teil dieses Auftrags.

Blender 5.2.2 LTS, Metric / Unit Scale 1.0 / Meter. Zum Prüfen aus einem neuen Blender-Prozess: `--background --factory-startup --python-exit-code 1 --python <absoluter Pfad>/build_study.py -- --mode verify`. Zum Rendern `--mode render`. `build` schützt vorhandene Quellen; `revise` ist nur für ausdrücklich beauftragte Iteration im eigenen Studienordner vorgesehen. Nach jeder Änderung Prüfungen und Hashliste neu erzeugen.

## Neuer technischer Anschlussvertrag

Keine R255-/Blatthof-Kompatibilität. Version **0.2** ändert Fassaden-, Innenwand- und Kern-Anschlüsse gegenüber 0.1; die betroffenen Teile tragen neue Assetnamen, kein stiller Unreal-Reimport. Unveränderte Studienbauteile bleiben wiederverwendet. Exportobjekte haben Translation/Rotation Null und Skalierung Eins; Pivots, Bounds und Instanztransforms stehen im Manifest. Der gemeinsame Boden verwendet den Szenenursprung und bereits in seine Meshkoordinaten übernommene Raumlagen. Diese Studienzusammenstellung ist kein freigegebener Produktionsbaukasten.

Unreal-Ziel: Zentimeter, `UE_cm=(100*B.x,-100*B.y,100*B.z)`. Blender -Y entspricht Unreal +Y. Keine zusätzliche Spiegelung oder negative Objektskalierung. Kalibriertes Exportprofil: **FBX_SCALE_NONE**, global_scale 1, apply_unit_scale true, Forward -Y, Up Z, use_space_transform true, bake_space_transform false. Auswahl ausschließlich MESH; Modifier/kontrollierte Triangulierung, FACE-Smoothing, Tangenten. Keine Kamera, Lichter, Animation oder eingebetteten Texturen im FBX. Kamera/Licht bleiben nur in der Blender-Review-Szene.

## Geometrie, Materialien und Kollision

**7348 Dreiecke** über die einzigartigen exportierten Render-Einheiten; **158 UCX-Körper** über die einzigartige Bibliothek. Diese Summen sind keine Instanz-/Draw-Call- oder Laufzeitmessung. Die vollständige Szene enthält zusätzliche Instanzen und die Maßfigur. Je ein UV0-Kanal mit metrischen Flächenprojektionen; absichtliche Überlappungen für einfache Kachelflächen. Keine Produktions-UVs oder finale Lightmap-UVs. Source-Normalen und geschlossene Meshkomponenten geprüft. Mehrteilige Dekor-/Baumgeometrie darf sich als zusammengefasste Studiengruppe absichtlich überschneiden; kein boolesch vereinigtes Produktionsmodell behauptet.

| Einheit | Dreiecke | UCX | Materialslots |
| --- | ---: | ---: | --- |
| `SM_ER_WingWindowFacade_640x280_v02` | 200 | 29 | BarkYoung |
| `SM_ER_WingRear_640x280` | 100 | 13 | BarkYoung |
| `SM_ER_WingSide_550x311` | 100 | 13 | BarkYoung |
| `SM_ER_WingInternalLink_550x311_v02` | 44 | 5 | BarkYoung |
| `SM_ER_WingRootVault_720x620` | 100 | 12 | BarkYoung |
| `SM_ER_WingCrownFill` | 100 | 12 | BarkYoung |
| `SM_ER_DoorLeaf_140x230` | 12 | 1 | Wood |
| `SM_ER_RootDoorArch` | 296 | 0 | BarkOld |
| `SM_ER_RetreatWindowFrame_65x80` | 124 | 0 | Wood |
| `SM_ER_RetreatWindowGlass_65x80` | 12 | 0 | Glass |
| `SM_ER_RetreatShutter_32x84` | 12 | 0 | Wood |
| `SM_ER_WingRootRibs` | 900 | 0 | BarkOld |
| `SM_ER_WingClosedStoneSill_v02` | 12 | 0 | StoneFloor |
| `SM_ER_OldCoreLinkedShell_R260_H430_v02` | 444 | 68 | BarkOld |
| `SM_ER_OldCoreCrown_640x620` | 336 | 1 | BarkOld |
| `SM_ER_LivingOldTrunk` | 332 | 0 | BarkOld |
| `SM_ER_OldButtressRoots` | 576 | 0 | BarkOld |
| `SM_ER_OldTreeCanopy` | 2080 | 0 | Leaves |
| `SM_ER_YoungLivingTrunk` | 144 | 0 | BarkYoung |
| `SM_ER_YoungTreeCrown` | 400 | 0 | Leaves |
| `SM_ER_LinkingRootArches` | 152 | 0 | BarkOld |
| `SM_ER_Ground_2600x2300` | 12 | 1 | Soil |
| `SM_ER_CourtStone_100x70` | 12 | 0 | StoneFloor |
| `SM_ER_Bench_210x56` | 36 | 0 | Wood |
| `SM_ER_HerbBed_250x140` | 32 | 0 | StoneFloor |
| `SM_ER_HerbClusters` | 576 | 0 | Herbs |
| `SM_ER_ConnectedFloor_v02` | 204 | 3 | Wood |

Strukturkollision besteht aus einzelnen geschlossenen konvexen Teilkörpern. Öffnungen werden ausgespart; keine komplette Haus-/Hofhülle als UCX. Die vielen Teilkörper der Wandraster sind bewusst einfach prüfbar, aber noch nicht für Laufzeit optimiert. Dekor, Natur, Glas und Detailteile ohne UCX sind im Manifest ausgewiesen. Aufteilung in weitere semantische Produktionsmodule oder Reduktion der Kollisionskörper später gesondert prüfen. Ein LOD, Nanite vorgesehen aus; weitere LODs nur nach Auftrag.

Roughness und Grundfarben stehen je Blender-Material im Manifest. Prozedurales Bump dient nur der Blender-Sichtprüfung, ohne externe Texturen. Blender-Shader werden nicht als vollständig nach Unreal übertragbar behandelt. Keine bestehenden Unreal-Materialien geändert.

## Tatsächlich geprüft und noch offen

Erneutes Source-Öffnen; Einheiten, geschlossene Source-Einheiten und alle FBX-Rückimporte mit Materialslots, Dreiecken, Bounds und konvexen UCX. Genau ein äußeres Türblatt. Je neun freie Render-/UCX-Strahlen für Haupteingang und beide inneren Wege durch beide beteiligten Wandlagen; mindestens 1,2 × 2,2 m stichprobenartig frei. Pro Innenverbindung 96 Bodenproben je Darstellung (Render/UCX) entlang und beiderseits der Strecke, Sollhöhe Z0. Der Renderboden ist eine zusammenhängende, geschlossene Komponente. Die alten Außentürstellen blockieren unten und oberhalb der neuen Fenster. Die tatsächlichen Messwerte stehen in `verification.json`. Keine funktionierende Türlogik oder vollständige Kapselbewegungsprüfung behauptet.

Nicht geprüft: kontinuierliches Kapselvolumen, alle Fenster-/Nahtkontakte, Innenkamera-Clipping, Unreal-Import/-Reimport/Materialzuordnung/Lightmap-Erzeugung, PIE, Packaging, Multiplayer, Performance, fertige Vegetation oder Produktionsqualität. Kleine Fenster sind opake/transmissive Glasplatzhalter; keine besondere Glas- oder Beleuchtungstechnologie. Review-Schwellen gelten je Produktionsteil; zusammengesetzte Studiengruppen sind gegebenenfalls später aufzuteilen.

Blender meldete lediglich DeprecationWarnings zu use_nodes. Korrigierte explorative Skript-/Prüfversuche sind keine bestandenen Abnahmen; maßgeblich ist der abschließende Prüfbericht. Keine Meldungen unterdrückt.

Nächster Schritt: gemeinsame Sichtprüfung und ausdrückliche Auswahl/Änderungswünsche. Nur danach Refiner-Übernahme als eigene Kopie; vorhandene Creator-Übergaben nicht überschreiben. **Kein Unreal-Import/Reimport, keine Editor-/Level-/Blueprint-/Material-/Config-Änderungen, keine Commits oder Pushes.** Eine spätere Integration benötigt einen benannten Verantwortlichen und den kalibrierten Legacy-Pfad FbxFactory/FbxStaticMeshImportData. Interchange ist nicht validiert; bestehende Kollision niemals pauschal löschen.

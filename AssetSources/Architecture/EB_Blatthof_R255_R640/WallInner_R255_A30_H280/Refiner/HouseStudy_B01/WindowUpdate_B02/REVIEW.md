# B02 – separate klare Fenster und Refiner-Lab

Stand: **23. Oktober 2026**. Status **review_ready**, keine Produktionsfreigabe. Der Nutzer bewertet die Hausstudie positiv, wünscht austauschbare durchsichtige Fenster mit Lichteinfall und hat ausdrücklich das **Refiner-Lab** als Integrationsziel ausgewählt. Das Hauptprojekt wurde nicht verändert.

## Ergebnis

Beide Häuser stehen jetzt im bestehenden `/Game/Prototype/Maps/Lvl_AssetLab`, Outliner `Lab/Architecture/ElvenHouseB02/`. Das kleinere Haus beginnt bei `(-2400,-1900,31)` cm und misst 10 × 12 m, das längere bei `(0,-1900,31)` cm und misst 10 × 16 m. Die bestehenden Lab-Muster, Spielerstart und Beleuchtung bleiben erhalten. Keine neuen Innenraum-Fülllichter. Die Größen und Profile bleiben vorläufige Prüfwerte der bestehenden Hausstudie.

Wiederverwendbares einzelnes Fenster-Asset: **`/Game/Art/Architecture/ElvenHouseB01/Windows/BP_EH_Window_Arch_100x173`**. Es enthält einen Rahmen und eine klare Scheibe als getrennte Meshkomponenten. Ein solches Blueprint-Asset lässt sich als Ganzes platzieren und später gezielt variieren. Die dazu passende Wand mit Aussparung ist `Windows/Meshes/SM_EH_Wall_WindowOpening_200x24x320`.

Die 10 beziehungsweise 12 Fenster der beiden Häuser sind tatsächliche Instanzen dieses Assets. Für Varianten muss die Öffnung kompatibel bleiben; alternative Formen werden hier nicht festgelegt. Die 60 vor der Aufstellung erfassten vorhandenen Lab-Actors sind nach Speichern/Wiederöffnen hinsichtlich Lage, Drehung, Skalierung, Ordnern, Mesh- und Materialreferenzen unverändert. 198 neue Haus-/Fenster-/Sockel-/Treppenactors wurden hinzugefügt; neue und alte Muster überlappen nicht.

## Quelle und Anschluss

Ausgangspunkt: Commit **`21a7ef17dd5cfd6f058b4c0f7440d2727b98c18d`** auf `assets/refiner`. Die neue editierbare Quelle [EH_HouseB02_Windows.blend](EH_HouseB02_Windows.blend) ist eine eigene Kopie. B01, die alte R255-Lieferung und Creator-Dateien bleiben unverändert. Die Quelle enthält beide Hausaufstellungen und die ursprünglichen übrigen Module; nur die bisher integrierte Fensterwand wird in drei wiederverwendbare Geometrien aufgeteilt.

| Neues Mesh | Dreiecke | Slots | UCX |
| --- | ---: | --- | ---: |
| Wand mit Fensteröffnung, 200 × 24 × 320 cm | 744 | Plaster, Timber, Stone | 7 |
| Rahmen einschließlich Maßwerk und Fensterbank | 456 | Timber, Stone | 0 |
| Glas, nominal 100 × 173 cm, 2 cm Geometriedicke | 72 | Glass | 1 |

Die Summe bleibt **1.272 Dreiecke**, sämtliche bisherigen Renderflächen und UVs werden ohne zusätzliche Ornamente aufgeteilt. Die Wand behält unteren Startpivot, Maße und Anschlüsse `(0,0,0)` / `(200,0,0)` cm. Der Fensterpivot liegt mittig am unteren Rand der Öffnung auf der äußeren Rahmenmittellinie. Montage relativ zur Wand: **Blender `(1,-0.055,0.95)` m**, Unreal **`(100,5.5,95)` cm**, gleiche Drehung, Skalierung Eins. Die nominelle Öffnung ist 100 × 173 cm; Rahmen und Fensterbank stehen darüber hinaus. Ihre tatsächlichen Bounds stehen im [Manifest](manifest.json).

Die neue Fensterwand und das Fenster haben eigene Assetnamen und einen dokumentierten Vertrag `draft_1_window_2`; kein stiller Slotwechsel des alten B01-Meshes. Die übrigen B01-Module werden unverändert referenziert. Das R255/A30-Kit ist weiterhin eine andere Profilfamilie.

## Durchsicht und Licht

Das neue eigene Material **`M_EH_Glass_Clear`** verwendet explizites Substrate: **Slab BSDF, Simple Volume**, Transmittance-To-MFP, Surface Forward Shading, Roughness 0,06 und F0 0,04. Zieltransmittanz am senkrechten Einfall: RGB `(0.97,0.985,1)` für die optisch dünne Slab-Schicht. Keine Bildschirmverzerrung durch Refraction. Die reale Meshdicke von 2 cm ist von der optischen Slab-Schicht zu unterscheiden; es wird keine vollständige physikalische Fenstersimulation behauptet.

Der Rahmen wirft Schatten. Die klare Scheibe wirft bewusst **keinen opaken Schatten** und beeinflusst die Distance-Field-Beleuchtung nicht. Dadurch gelangt bestehendes dynamisches Lab-Tageslicht durch die echte Wandöffnung. Das Glas bleibt physikalisch geschlossen und blockiert die Figur; Durchsicht bedeutet keine begehbare Öffnung. Keine farbigen Buntglasschatten, Kaustiken, Bruch- oder Öffnungsmechanik ergänzt. Die Beleuchtung ist weiterhin ein Prototyp.

Die technische Shadergrundlage ist [Epics Substrate-Dokumentation für UE 5.8](https://dev.epicgames.com/documentation/unreal-engine/overview-of-substrate-materials-in-unreal-engine?application_version=5.8). Der zuerst versuchte Legacy-ThinTranslucent-Pfad und anschließend der ungeeignete Diffusionsmodus wirkten im lokalen Renderer dunkel. Erst der ausdrücklich eingestellte **Simple-Volume-Modus** lieferte die geprüfte Durchsicht. Keine Projekt-/Renderer-Konfiguration geändert.

## Tatsächliche Belege

- [Blender-Quelle erneut geöffnet und alle drei FBX-Dateien zurückimportiert](Evidence/blender_verification.json): geschlossene Komponenten, konsistente Flächenorientierung, positive Volumen, nicht degenerierte UVs, Slot-/Boundsvergleich und UCX-Anzahlen bestanden. Relative Verweise auf die unveränderten B01-Texturen funktionieren.
- [Unreal-Lab-Prüfung](Evidence/lab_verification.json): alle drei Meshes über `FbxFactory`/`FbxStaticMeshImportData`, Einheitsskalierung, erwartete Dreiecke/Slots, zwei UV-Kanäle, UCX 7/0/1 und Boundsabweichung unter 0,001 cm. An allen 22 Fenstern trifft die einfache Abfrage die Scheibe; beim Ignorieren nur des jeweiligen Fensteractors bleibt die Wandöffnung frei. Alle Scheiben sichtbar, alle Rahmen mit Schatten und alle Glasscheiben ohne opaken Schatten.
- [Expliziter Legacy-Reimport](Evidence/reimport_windows.json): dieselben drei Quellen erneut importiert; Geometriezahlen, Kollisionshüllen, Slotfolge und Materialzuordnung erhalten. Anschließend Lab über die unveränderte B01-Prüfkarte verlassen und erneut geladen; alle statischen Prüfungen erneut bestanden.
- [Durchblick von innen](Previews/window_inside.png) und [von außen](Previews/window_outside.png) bei sichtbarer Scheibe. [Kontrollaufnahme ohne Scheibe](Previews/window_inside_pane_hidden.png) ist ausdrücklich als Diagnose gekennzeichnet; die endgültigen Fenster enthalten sichtbares Glas.
- [Tageslicht mit klarer Scheibe](Previews/sunlit_floor_clear.png), [Kontrollbild mit vorübergehendem opaken Verschluss](Previews/sunlit_floor_blocked.png): derselbe Lab-Sonnenstand, gleiche Kamera und festes EV1. Der entsprechende Lichtfleck verschwindet beim Verschluss. Im festgelegten Bodenbildausschnitt ist die mittlere sRGB-Helligkeit mit klarer Scheibe etwa **2,09-mal** so hoch. [Messbeleg](Evidence/sunlight_comparison.json). Dies ist ein Bildvergleich, keine photometrische Energiebilanz. Verschluss und temporäres Belichtungsvolumen sind entfernt und wurden nicht mitgespeichert.
- [PIE im tatsächlichen Lab](Evidence/pie_result.json): E öffnet, schließt und öffnet die neue Haustür; vier W-Eingaben führen von `(-1900,-1800,123.15)` bis ungefähr `(-1900,-2432,123.06)` cm ins Haus. Bodenhöhe stabil. Screenshots: [Tür](Previews/pie_door_open.png), [innen](Previews/pie_inside.png). Die vorhandene Türlogik blieb unverändert.
- [Lab-Übersicht](Previews/lab_overview.png). Die ursprüngliche gesonderte B01-Prüfkarte bleibt als eingefrorener Vergleich erhalten und wird nicht auf transparente Fenster umgebaut.

## Grenzen und Übergabe

Ein Fenster ist nun separat wiederverwendbar; weitere Fensterformen/-größen wurden nicht hergestellt. Die Auslagerung erhöht die Zahl der Komponenten und Materialabschnitte trotz unveränderter Dreieckssumme. Transparenzsortierung, Reflexionen, Lumen-/Belichtungsqualität und Kosten vieler Fenster sind vor Serienproduktion gesondert zu prüfen. Innenausbau und die zuvor offenen oberen Kollisionen an Giebel, Dachfüllungen und Vordach bleiben offen. Kein Performance-, Packaging- oder Multiplayer-Nachweis.

Die Arbeiten wurden ausschließlich im ausgewählten Refiner-Worktree ausgeführt. Unter bestehendem `Content/` wird nur `Lvl_AssetLab.umap` ergänzt; dazu kommen fünf neue Assets: drei Meshes, ein Material, ein Fenster-Blueprint. Gemeinsame Materialien, bestehende Blueprints, weitere Karten, Generatoren und Projektkonfiguration bleiben unverändert. Der zeitweilige Legacy-Importer-Sitzungswert wird auf seinen Ausgangswert zurückgesetzt. Keine automatische Übernahme ins Hauptprojekt, kein Commit oder Push dieses Updates.

# Elfenhaus – Fenstermodul 01

Stand: **22. Oktober 2026**, Unreal Engine 5.8. Ergänzung zum [geschlossenen Hausprototyp 01](ELVEN_CLOSED_HOUSE_01.md), auf Nutzerauftrag im bestehenden Asset-Lab getestet. Eine neue Fensterwand ersetzt das erste geschlossene Außenwandfeld; die Stilstudie bleibt erhalten. Dies ist ein Architekturprototyp, keine neue Stil- oder Lorefestlegung.

## Finden und wiederverwenden

- Karte `/Game/Prototype/Maps/Lvl_AssetLab`, Ordner `Lab/Architecture/ElvenClosedHouse01`, Actor `Lab_EBHouse_Closed01` bei `(−4400,1000,12)`.
- Vorhandenes Prefab `BP_EB_House_A60_Prototype01`, Komponente **`A_OuterWall`**. Das zweite Außenwandfeld bleibt geschlossen. Vorlage und gespeicherte Hausinstanz referenzieren das neue Mesh bei unverändertem Transform und Einheitsskalierung.
- Neues Mesh: `/Game/Art/Architecture/ElvenBlatthof/Modular/Window01/Meshes/SM_EB_WallOuter_Window_R640_A30_H280_LeafFrame`.
- Unveränderte Alternative: `JoinSample01/Meshes/SM_EB_WallOuter_R640_A30_H280`. Beim manuellen Austausch nur das Mesh der jeweiligen Außenwandkomponente wechseln; keine zusätzliche geschlossene Wand hinter dem Fenster platzieren.

Wand, Rahmen, Fensterfüllung und äußeres Blattmaßwerk bilden **ein gemeinsames Modul**. Es entstehen keine einzelnen Zier-Actors, kein Tick und keine Fensterbedienung. Die vorhandene Eingangstür bleibt unabhängig davon nutzbar.

## Anschlussvertrag und Materialien

| Merkmal | Implementierter Stand |
| --- | --- |
| Kit / Interface / Modul | `EB.Blatthof.R255_R640` / `1` / `EB.Wall.Outer.Window.A30.v1` |
| Wandfeld | 30°, R630…650 cm, Höhe 280 cm, Dicke 20 cm |
| Fensterzone | Winkel 6…24°, Brüstung Z75, Oberkante Z240; 165 cm hoch, etwa 201 cm Bogenbreite auf R640 |
| Füllung | R637…643 cm, **fest und undurchsichtig**, entsprechend dem vorhandenen Glasprototyp |
| Rahmen / Schmuck | Timber-Rahmen mit Mittelpfosten und Querleisten; Bronze-Blattmaßwerk außen, vom vorhandenen Motiv abgeleitet |
| Pivot / Achsen | R255-Startpunkt auf Boden Z0; X tangential, Y nach innen, Z nach oben |
| Join_A | `(0,0,0)`, Anschlussrichtung Yaw 180° |
| Join_B | `(127,5; 34,16352203496813; 0)`, Yaw 30° |
| Tatsächliche Slotreihenfolge | `Ivory`, `Glass`, `Timber`, `Bronze` |

Alle vier Slots verwenden direkt die vorhandenen `MI_Blatthof_*` unter `/Game/Art/Materials/ElvenBlatthof/`. Keine neuen Materialien oder Texturen; der bestehende Master `M_FlatCol` bleibt unverändert. Das Fenster besitzt eine echte Aussparung in der Ivory-Wand, die durch die bestehende dunkle Glass-Füllung geschlossen wird. Es bietet **keinen transparenten Durchblick und keinen Lichteinfall** durch die Scheibe. Innen ist der Rahmen sichtbar, das äußere Maßwerk liegt hinter der undurchsichtigen Füllung.

Kit, Interface, ModuleId, Lage, Winkel, Quellpfad, Pivot, Anschlüsse und Fensterparameter sind als Editor-Metadaten am neuen Mesh gespeichert. Das Exportmanifest enthält dieselben Daten. Keine nativen Sockets, kein Laufzeitkatalog und kein PCG-Graph; die bisherigen berechneten Anschlüsse gelten weiter.

## Quelle und Aufwand

Neue reproduzierbare Quelle: [generate_elven_window.py](../../Tools/Prototype/generate_elven_window.py).

```powershell
python -B Tools/Prototype/generate_elven_window.py
```

Der Aufruf schreibt nur OBJ, MTL und Manifest unter `Saved/ElvenWindowSources/`. Bestehende Geometriehelfer werden als Bibliothek genutzt; deren `build()` wird nicht ausgeführt und ihre Quellen werden nicht geändert. Import, Materialzuordnung, einfache Kollision und Hausintegration erfolgten über Unreal MCP. Der Exporter baut kein Unreal-Gebäude automatisch auf. Seine Ausgabe muss separat importiert und die Manifest-Kollision separat angewandt werden.

Ausgelesener Endstand: **808 Dreiecke, 1.332 Render-Vertices, vier Materialslots, ein LOD, Nanite aus**. Bounds im gemeinsamen Modulkoordinatensystem ungefähr `(0;−399,395;0)` bis `(325;−290,596;280)` cm. Ein UV-Kanal aus dem einfachen Projektionsmapping ist Quellbestandteil; finale UV-/Lightmap-Qualität ist nicht abgenommen.

Kollision: **elf Boxen**, davon acht für Seiten/Brüstung/Sturz und drei dünne Körper für die fest geschlossene Fensterfüllung; `UseSimpleAsComplex`. Maßwerk und Rahmen besitzen keine zusätzlichen feinen Kollisionskörper. Die Näherung über 6°-Bänder weicht radial um ungefähr 0,9 cm ab; überstehender Schmuck darf daher optisch vor der Kollisionsfläche liegen. Keine durchgehende Vollwand-Kollision hinter der Fensterzone.

Das Gesamt-Prefab behält neun StaticMeshComponents und zwei ChildActorComponents. Ohne vorhandenes Türblatt/Rahmen steigt die Hausgeometrie von 4.452 auf **5.176 Dreiecke**, die einfache Körperzahl von 73 auf **79**. Vier Materialabschnitte der Fensterwand verursachen mehr Renderaufwand als die vorherige einfarbige Wand. Die Prototyp-Reviewschwellen werden eingehalten; keine Messung für Siedlungen oder Produktionsfreigabe. Zusätzliche LODs erst anhand der benötigten Kameradistanzen und Szenendichte festlegen.

## Tatsächlich geprüft

| Prüfung | Ergebnis |
| --- | --- |
| Geometriequelle | Vier passende Grenzpunkte und sichtbare Grenznormalen am 30°-Stoß; Wandendpunkte entsprechen dem bisherigen Außenwandvertrag |
| Import | Dreiecke, Vertices, Bounds, Slotreihenfolge, zugewiesene vorhandene Materialien, LOD/Nanite und elf Kollisionsboxen ausgelesen |
| Prefab | Mit Warnungen als Fehler kompiliert; nur `A_OuterWall.StaticMesh` ausgetauscht, neun statische Komponenten erhalten |
| Speichern/Wiederöffnen | Mesh, Haus und Lab gespeichert, über Sandbox gewechselt und erneut geprüft |
| Fensterfüllung | 21 Positionen jeweils von innen und außen abgefragt; Treffer auf der dünnen Füllung statt auf R630-Vollwand |
| Hülle | 14 Wand-/Brüstungs-/Sturzabfragen, 14 Bodenabfragen auf Welt-Z12, zehn Dachabfragen und sechs Endabschlussabfragen bestanden; freier Innengang |
| Wiederverwendung | Zweite temporäre Hausinstanz mit 30° Rotation und Einheitsskalierung übernimmt das Fenster aus dem Prefab; Material-Override verändert die erste Instanz nicht; Hilfsinstanz entfernt |
| Tatsächliche PIE-Spielerkapsel | Radius 35 cm, Halbhöhe 90 cm; Annäherung von innen und außen wird im Gehmodus gestoppt, ohne Durchtritt |
| Nahtbegehung | Feldstoß vorwärts und rückwärts im Gehmodus überquert; Höhenvariation 0,0 cm |
| Sichtprüfung | Gerenderte Außen-, Innen- und Übersicht kontrolliert; nach Korrektur des äußeren Maßwerks erneut aufgenommen |

Die Bewegungsprüfung verwendet kurzzeitige Geschwindigkeitsimpulse auf der bestehenden transienten CharacterMovement-Komponente. Keine Teleportation durch das Fenster und kein NoClip. Das ist **kein physischer WASD-/E-Test**. Die Spielerkapsel wird im Stand bereits von Brüstung bzw. Rahmenbereich aufgehalten; die separaten Linienprüfungen weisen zusätzlich die dünne Füllung nach.

Die endgültige Änderung nach dieser Bewegungsprüfung betrifft ausschließlich die Orientierung der Querschnittsringe des äußeren Maßwerks. Die erste Variante zeigte Knicke am vertikalen Tangentenwechsel des übernommenen Röhrenhelfers. Der neue lokale Helfer verwendet stabile radiale Querschnitte; ursprüngliche Quelle und Stilstudie bleiben unverändert. Die neue Fassung besitzt dieselbe strukturelle Geometrie und dieselben Kollisionsboxen; statische Anschluss-/Kollisionsprüfung, erneutes Laden und Sichtprüfung wurden mit ihr wiederholt. Nur der eigene verworfene Meshzwischenstand wurde entfernt.

**Zusätzliche Regressionstests bleiben offen:** Im ersten gemeinsamen Lauf besteht `AssetWorkspace.AssetLabPIE`; `DeveloperToolbox.MapsPIE.Lvl_AssetLab` scheitert an F6-Schließen/Eingaberückgabe und `Interaction.DoorPIE` an Fokus/Feedback/E-Öffnen im ursprünglichen Testlevel. Der Türtest scheitert auch einzeln. Ein Kontrolllauf ohne Hintergrund-CPU-Drosselung liefert ebenfalls Eingabefehler im Lab-Test und wurde anschließend beendet; er ist kein bestandener Gesamtlauf. Die Sitzungseinstellung wurde zurückgestellt, PIE beendet. Die Ursache ist nicht abschließend eingegrenzt; ein Zusammenhang mit Editor-/Eingabetiming ist eine Hypothese. Keine Testaussagen, Eingabe-/Gameplay-Implementierung oder Logunterdrückung geändert, um diese Ergebnisse zu umgehen. Keine vollständige Suite oder neuer C++-Build ausgeführt.

## Erhaltung und nächste Kontrolle

Neu sind ausschließlich das Fenster-Mesh, dessen Exporter und diese Dokumentation. Autorisierte bestehende Änderungen: Haus-Prefab, Lab-Karte einschließlich Schild, technische Statusdatei und Verweis im Hausbericht. Der SHA-256-Abgleich gegen 1.063 vor Arbeitsbeginn erfasste versionierte Dateien bestätigt diese Eingrenzung: Stilstudienassets, ursprünglicher Generator, vorhandene Materialien, Tür-/Rahmenassets, alle bisherigen Modulmeshes, übrige Karten, C++, Projektkonfiguration und Worldbuilding sind identisch. Alle 68 verglichenen bestehenden Actor-Transforms und die vier Komponenten der Stilstudie bleiben gleich; am Haus ist ausschließlich `A_OuterWall.StaticMesh` geändert. Temporäre native Editor-Manager sind vom Actor-Erhaltungsabgleich ausgenommen. Mesh, Haus und Lab abschließend `dirty=false`, PIE beendet, temporäre Prüf-Actors entfernt. Keine Commit-/Push-/Staging-Aktion dieses Schritts.

Ein früher Hüllentest begann versehentlich innerhalb der vorhandenen Endkappen-Kollision und wurde mit einem Punkt außerhalb der Endkappe wiederholt. Ein erster Erhaltungsabgleich enthielt kurzlebige native Editor-Manager und kollidierte mit einem Kartenwechsel; die abschließende Prüfung erfolgte separat mit stabilen Actors. Diese Werkzeug-/Prüffehler sind keine bestandenen Testläufe und werden nicht durch die erfolgreichen Fensterprüfungen verdeckt.

Vor einer weiteren Freigabe die offenen Eingabe-Regressionen klären sowie manuell E von beiden Seiten, WASD an Fenster/Brüstung und die Third-Person-Kamera unter dem Dach prüfen. Öffnen des Fensters, transparente Verglasung, Innenmaßwerk, zusätzliche Varianten, Möblierung, Produktions-UVs, Packaging und Szenenperformance bleiben Folgeaufträge.

Lokale ignorierte Belege: `Saved/InteractionDev/window_{inspect,import,place,finish,verify,runtime,preserve}_result.json`, `window_smoke_result.json`, `window_door_isolated_result.json`, `window_input_control_result.json`, `window_final_audit.json` sowie `window_outside.png`, `window_inside.png` und `window_overview.png`. Zwischenquellen und Sicherungen bleiben unter `Saved/`.

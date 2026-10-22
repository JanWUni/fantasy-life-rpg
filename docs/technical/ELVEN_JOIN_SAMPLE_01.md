# Elfenhaus – Anschlussmuster 01

Stand: **22. Oktober 2026 · implementierter Anschlussversuch**, Unreal Engine 5.8. Grundlage: [Modularisierungsplan](ELVEN_MODULAR_BUILDING_PLAN.md). Dieser Versuch umfasst ausschließlich Boden, Innenwand, Außenwand und Mitteldach, jeweils zweimal instanziert. Kein Gebäude- oder PCG-Generator, keine vollständige Wohnhausvariante.

**Folgestand:** Das Muster wurde anschließend auf Nutzerauftrag mit Eingang, Funktionstür und Endabschlüssen zum [geschlossenen Hausprototyp 01](ELVEN_CLOSED_HOUSE_01.md) ergänzt. Die folgende Beschreibung dokumentiert den ursprünglichen offenen Anschlussversuch; dessen Modulassets bleiben erhalten.

## Im Asset-Lab finden

- Karte: `/Game/Prototype/Maps/Lvl_AssetLab`.
- Outliner: `Lab/Architecture/ElvenJoinSample01`, Unterordner `A` und `B`.
- Acht StaticMeshActors `Lab_EBJoin_A_*` / `Lab_EBJoin_B_*`, zusätzlich das Schild `Lab_EBJoin_Label`.
- Westlich der bestehenden Stilstudie: Feld A bei **(−4400, 1000, 12)**, Yaw 0°; Feld B bei **(−4272,5; 1034,163522…; 12)**, Yaw 30°.
- Vom Start links zur bisherigen Architekturzone gehen und weiter nach Westen zum neuen Schild. Die beiden radialen Enden des Musters sind offen; von dort lässt es sich betreten. Lokale Bodenoberkante ist Z=0, die Prüfaufstellung liegt bewusst 12 cm über dem Lab-Boden. So lässt sich fehlende Bodenkollision durch eine Messung unterscheiden.

Die bestehende Stilstudie bleibt als separates Original erhalten. Ihre Meshes, Materialien, ihr Blueprint und der ursprüngliche Geometriegenerator wurden nicht überschrieben. Die Karte erhält nur die neue Aufstellung und das Schild; vorhandene Actors werden nicht umgestellt.

## Neue Assets und wiederverwendete Quellen

Alle vier neuen Meshes liegen unter `/Game/Art/Architecture/ElvenBlatthof/Modular/JoinSample01/Meshes/`:

| Mesh | Maße / Funktion | Dreiecke LOD0 | Materialslots |
| --- | --- | ---: | --- |
| `SM_EB_Floor_R240_650_A30` | 30°-Bogen, R240…650 cm, Boden Z−12…0 | 84 | Stone |
| `SM_EB_WallInner_R255_A30_H280` | 30°, R245…265, Höhe 280 cm | 84 | Ivory |
| `SM_EB_WallOuter_R640_A30_H280` | 30°, R630…650, Höhe 280 cm | 84 | Ivory |
| `SM_EB_LeafRoof_R215_695_A30` | 30°, R215…695, Blattdicke 12; Dachoberseite Z300…455; Wandfüllungen ab Z280 | 1.784 | Jade, JadeLight, Timber, Ivory |

Das sind **2.036 Dreiecke pro Feld, 4.072 für die beiden Instanzen zusammen**. Alle vier Meshes wurden mit einem LOD und deaktiviertem Nanite ausgelesen; keine weiteren LODs erstellt. Dies ist keine gemessene Performanceaussage für viele Häuser.

Die vorhandenen Materialinstanzen `MI_Blatthof_Stone`, `Ivory`, `Jade`, `JadeLight` und `Timber` werden direkt weiterverwendet. Es gibt keine neuen Materialien, Texturen, Funktionstüren, Fenster, Verzierungsassets oder Gebäude-Blueprints.

Versionierte Geometriequelle: [generate_elven_join_sample.py](../../Tools/Prototype/generate_elven_join_sample.py). Sie importiert die vorhandenen `Mesh`-/`polar`-Funktionen aus `generate_elven_blatthof.py`, führt dessen `build()` jedoch nicht aus. Aufruf aus dem Projektverzeichnis:

```powershell
python -B Tools/Prototype/generate_elven_join_sample.py
```

Ausgabe ausschließlich nach `Saved/ElvenJoinSources/`: vier OBJ, eine MTL und `manifest.json`. Import, Zuordnung der vorhandenen Materialien, Kollision und Platzierung erfolgten über Unreal MCP. Der Exporter erzeugt keine Unreal-Assets oder Gebäudezusammenstellungen selbst. Die Kollisionsboxen sind ebenfalls im Manifest beschrieben; sie müssen beim erneuten Import gesondert angewandt werden, OBJ übernimmt diese Daten nicht automatisch.

## Anschlussvertrag und Dachanpassung

Alle vier Module teilen denselben Pivot: Startpunkt auf R255 cm, Bodenhöhe Z0. X zeigt tangential in zunehmende Bogenrichtung, Y zum Kreismittelpunkt, Z nach oben. Zusammengehörige Lagen eines Felds erhalten denselben Transform und Einheitsskalierung.

```text
Join_A: Position (0, 0, 0), Anschlussrichtung Yaw 180°
Join_B: Position (127,5; 34,16352203496813; 0), Anschlussrichtung Yaw 30°
```

Die zweite Modulinstanz hat gegenüber der ersten genau diese Position und 30° Drehung. Die Anschlussrichtungen zeigen beim Fügen gegeneinander. Keine manuelle Rundung auf ein kartesisches 10-cm-Raster.

Kit-ID, Lage, Winkel, Interface-Version, Pivot, Quellenpfad und die beiden Anschluss-Transforms wurden als **Editor-Metadaten** auf den vier neuen Meshassets gespeichert. Das Manifest enthält dieselbe geometrische Grundlage. Es wurden **keine nativen Mesh-Sockets, kein Laufzeitkatalog und kein automatisches Snap-Werkzeug** implementiert. Für diesen Versuch erfolgte die Aufstellung anhand der berechneten Transforms; die Metadaten sind noch keine Runtime-PCG-Schnittstelle.

Das neue Dach verwendet die vorhandene Querwölbung und Farbaufteilung. Die winkelabhängige Spitzenanhebung des vollständigen Referenzhauses entfällt beim wiederholbaren Mittelfeld. Ober-/Unterseiten, radiale Ränder und beide Stirnseiten sind geschlossen. Füllvolumen über beiden Wandkronen schließen bis an die stückweise lineare Dachunterseite an. Deshalb besitzt das Dach zusätzlich den vorhandenen Ivory-Materialslot.

Explizite Normalen erhalten die glatte Dach- und Wandwirkung über die Modulnaht; Stirnflächen behalten harte Normalen. Der Exporter prüft die transformierten Stoßpunkte und die sichtbaren Grenznormalen beider Instanzen gegeneinander. Dachadern, Stützen, Endspitzen und Ornamente wurden für diesen Anschlussversuch nicht ergänzt.

## Kollision und tatsächlich durchgeführte Prüfungen

| Prüfung | Ergebnis |
| --- | --- |
| Quellenprüfung: zwei identische Module mit 30° Anschluss-Transform | Passende Grenzpunkte und sichtbare Normalen; vier Grenzpunkte je Boden-/Wandmodul und 74 am Dach |
| Importdaten | Maße/Bounds, Dreiecke, Materialslots, LOD-Anzahl und Nanite-Zustand ausgelesen |
| Erneutes Laden | Lab über Sandbox gewechselt und wieder geöffnet; neue Assets und Lab gespeichert, `dirty=false` |
| Bodenmessungen | Zehn Abfragen bei R350/R500 und 15°, 29,9°, 30°, 30,1°, 45°: jeweils Welt-Z=12 |
| Innen-/Außenwände | Zehn radiale Abfragen einschließlich genau am Feldstoß blockieren; einfache Wandkörper liegen innerhalb etwa 0,9 cm der radialen Sollkontur |
| Dach | Fünf Abfragen einschließlich Feldstoß blockieren; zusätzliche Abfragen treffen beide Wand-Dach-Füllbereiche |
| Freier Gang | Horizontale Linien zwischen 20° und 40° in beiden Richtungen frei |
| Tatsächliche PIE-Spielerkapsel | Radius 35 cm, Halbhöhe 90 cm, Einheitsskalierung ausgelesen; `MOVE_Walking` während des beidseitigen Nahtübertritts bestätigt |
| Bewegung über die Naht | Über bestehende CharacterMovement-Geschwindigkeitsimpulse von −130 auf etwa +110 cm relativ zur Naht und zurück auf −110 cm; gemessene Höhenvariation **0,0 cm** |
| Vorhandener `FantasyLifeRPG.AssetWorkspace.AssetLabPIE` | Erfolgreich, 3,88 s |
| Vorhandener `FantasyLifeRPG.DeveloperToolbox.MapsPIE.Lvl_AssetLab` | Erfolgreich, 1,23 s |
| Gemeinsamer abschließender Testlauf | **2/2 erfolgreich in 5,11 s**, keine Testwarnungen/-fehler; PIE beendet |
| Sichtprüfung | Gerenderte Übersicht, Innenansicht und Dachnahansicht kontrolliert; keine sichtbare offene Modulnaht in diesen Ansichten |

Die Kollision verwendet bei allen vier neuen Meshes `UseSimpleAsComplex`, damit auch komplex angeforderte Abfragen dieselben einfachen Körper verwenden. Boden: zehn flache Boxen; Innen-/Außenwand: jeweils fünf gedrehte Boxen; Dach: acht automatisch erzeugte konvexe Hüllen. Insgesamt 28 einfache Körper je Feld. Alle acht Meshkomponenten sind statisch und verwenden `BlockAll`.

**Grenzen der Kollisionsnäherung:** Die Bodenboxen halten die Oberkante exakt eben, überdecken an den offenen inneren Endecken aber bis ungefähr 11 cm über den sichtbaren Winkelschnitt hinaus. Das wurde für dieses offene Lab-Anschlussmuster akzeptiert und ist keine finale Randlösung. Die Dachhüllen sind ebenfalls angenähert: an den gemessenen mittleren Stellen liegen ihre oberen Treffer etwa 2–3 cm über der sichtbaren Oberfläche. Für spätere Randabschlüsse bzw. präzise Dachkontakte kontrollierte konvexe Kollisionsquellen vorsehen. Die Wandboxen sind deutlich näher an der dünnen Wandkontur als die erste automatische Zerlegung.

Ein erster W-Tastentest über Slate erreichte die Zielposition nicht. Die Slate-Schnittstelle lieferte keine sichtbaren Fenster; auch eine Aufnahme der gesamten Editor-Anwendung war nicht verfügbar. Deshalb wird **kein erfolgreicher Slate-/physischer Tastaturtest am neuen Muster behauptet**. Die erfolgreiche Bewegungsprüfung setzt ausschließlich die Geschwindigkeit der transienten vorhandenen CharacterMovement-Komponente; ihre Kollisionsbewegung und der Gehmodus laufen weiter regulär. Es gibt keine Teleportation über die Naht und keinen NoClip für diese Prüfung. Beim Beenden von PIE verschwinden sämtliche temporären Laufzeitänderungen.

Die erste automatische Kollisionszerlegung lieferte zudem ungenaue Hüllen für dünne Wände und Boden; eine erste Wandabfrage verfehlte einen Treffer am Dreiecksrand. Die abschließende Prüfung verwendet die oben beschriebene korrigierte Kollision. Explorative Werkzeugabfragen erzeugten Fehlerprotokolle; die abschließenden beiden Automatisierungstests sind davon getrennt und meldungsfrei. Kein insgesamt fehlerfreier Entwicklungslauf behauptet. Keine Unterdrückung von Logmeldungen geändert.

## Erhaltungsprüfung und nächste manuelle Kontrolle

Vorhandene Projektdateien wurden vor Beginn mit SHA-256 erfasst, die Lab-Datei zusätzlich lokal gesichert. Der Editorabgleich prüft die ursprünglichen 66 Actor-Transforms und die Meshkomponenten der Stilstudie; der Dateiabgleich grenzt die Änderungen an bestehenden Projektdateien auf Lab und technische Dokumentation ein. Haus-/Türassets, ursprüngliche Geometriequelle, Materialien, übrige Karten, C++, Konfiguration und Worldbuilding bleiben unverändert. Keine Commits, Pushes oder Staging-Aktionen.

Manuell noch prüfen: mit WASD durch beide offenen Enden laufen, an Innen-/Außenwand entlanggehen, Schritt auf die 12-cm-Platte und Kamerakontakte unter dem Dach beurteilen. Besonders die offenen Bodenendecken und die vereinfachte Dachkollision sind noch keine Produktionslösung. Der Versuch ist ein Nachweis für zwei verbundene strukturelle Felder; ein vollständig geschlossenes Haus mit Tür, Fenstern und Endabschlüssen bleibt der nächste gemeinsame Auswahlschritt.

Lokale, ignorierte Belege unter `Saved/InteractionDev/`: `module_join_geometry.json`, `module_join_import_result.json`, `module_join_place_result.json`, `module_join_wall_boxes_result.json`, `module_join_floor_boxes_result.json`, `module_join_verify_result.json`, `module_join_velocity_walk_result.json`, `module_join_smoke_result.json`, `module_join_preserve_result.json`, `module_join_final_audit.json` sowie `module_join_overview.png`, `module_join_inside.png`, `module_join_roof_seam.png` und `module_join_velocity_walk.png`. Der frühere fehlgeschlagene Slate-Versuch bleibt als `module_join_walk_first_attempt.json` erhalten.

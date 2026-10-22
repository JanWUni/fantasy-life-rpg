# Creator-Übergabe: Innenwand R255 / A30 / H280

Stand: 22. Oktober 2026. **Status: `creator_ready`**, ausschließlich Blender-seitig geprüft. Keine Unreal-Abnahme oder Produktionsfreigabe.

## Identität und Zuständigkeit

| Feld | Wert |
| --- | --- |
| AssetName | `SM_EB_WallInner_R255_A30_H280` |
| KitId / ModuleId | `EB.Blatthof.R255_R640` / `WallInner_R255_A30_H280` |
| InterfaceVersion / Creator-Revision | `1` / `1` |
| Schreibverantwortlicher | Asset Creator, Branch `assets/creator` |
| Erlaubter Bereich | `AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Creator/` |
| Ausgangsrevision | `b1b2f051a2ead8d95c72e1253131eb9934d59b49` |
| Übergabestand | Geprüfte Creator-Revision 1; Dateiliste und SHA-256 in `SHA256SUMS`. Übergabe-Commit wird nach dem Committen separat genannt. |

Der Kit-Ordner verwendet Unterstriche gemäß ASCII-Dateinamenregel; die bestehende logische KitId mit Punkten bleibt unverändert. Der gesamte Lieferstand bleibt ab dieser Übergabe eingefroren. Refiner übernimmt eine eigene Kopie nach `../Refiner/`; Änderungen an Maßen, Pivot, Profil, Anschlüssen oder Slotvertrag vorher zurückmelden.

## Lieferumfang

- `SM_EB_WallInner_R255_A30_H280.blend`: editierbare Quelle, Collections `Render` und `Collision_UCX`.
- `Exports/SM_EB_WallInner_R255_A30_H280.fbx`: ein Render-Mesh und zehn benannte UCX-Meshes, kontrolliert trianguliert.
- `manifest.json`: technische Lieferbeschreibung, Quell-/Exporthashes und Verweis auf Prüfbericht.
- `verification.json`: tatsächliche Ergebnisse aus separatem Blender-Prozess: Quelle erneut geöffnet, FBX in leere Szene zurückimportiert und geprüft.
- `create_wall.py`: lokaler, eigenständiger Erzeuger und Prüfer; keine Änderung oder Ausführung von Bestands-`build()`-Funktionen.
- `Previews/two_modules.png`: Blender-Prüfansicht zweier passend gefügter Instanzen. Der grünliche Objektfarbwechsel verdeutlicht die Teilung; er ist kein zusätzlicher Materialslot oder Unreal-Material-Override. Kamera und zweite Instanz sind nur im transienten Vorschauprozess vorhanden.
- `HANDOFF.md` und `SHA256SUMS`: diese Übergabe und Prüfsummen sämtlicher Lieferdateien außer der Prüfsummenliste selbst.
- `.gitattributes`: ausschließlich in diesem Creator-Ordner wirksame LF-Regeln für Skript, Markdown und Prüfsummenliste. Blender-generierte JSON-Dateien bleiben bytegenau einschließlich ihrer ursprünglichen CRLF-Zeilenenden erhalten. So stimmen die Byte-Prüfsummen auch nach Windows-Checkouts. Bestehende LFS-Regeln für binäre Quellen/Exporte bleiben gültig.

Die ursprüngliche Geometrie ist mathematisch neu als geschweißtes Blender-Mesh aufgebaut; kein verlustbehafteter OBJ-Import. Vergleich mit `Tools/Prototype/generate_elven_join_sample.py` und dessen `Mesh.arc`-/Normalenfunktionen im Speicher, ohne ihre Ausgabedateien zu erzeugen. Referenzstand ist der oben genannte Commit. Inhaltliche Grundlage: `docs/technical/ELVEN_JOIN_SAMPLE_01.md`, gemeinsame Asset-Pipeline und kalibriertes Blender-/Unreal-Profil. Das vorhandene Elfenhaus ist nur visuelle Referenz; keine neue Architektur-, Kultur- oder Materialsymbolikentscheidung.

## Eingefrorener Maß- und Anschlussvertrag

- Blender **5.2.2 LTS**, Build `d13f752e3b9c`; Metric, Unit Scale **1.0**, Koordinaten in Metern. Nur FBX-Add-on `io_scene_fbx` benötigt, keine externen Bibliotheken oder Texturen.
- Ringsektor **30°**, Innen-/Außenradius **245 / 265 cm**, Referenzradius **255 cm**, radiale Dicke **20 cm**, Höhe **280 cm**, Unterkante/Bodenanschluss **Z0**. Zehn Segmente zu je 3°, passend zur bestehenden Kontur. Geschlossene Vollwand ohne Fenster, Türöffnung oder Dekor. Kein Boden- oder Dachteil mitgeliefert; Dachfüllung gehört zum bestehenden Dachmodul.
- Gemeinsamer Pivot am Feldanfang auf R255/Z0. Unreal X tangential in zunehmende Bogenrichtung, Y zum Kreismittelpunkt, Z oben. Kreismittelpunkt lokal UE `(0,255,0)` cm, Blender `(0,-2.55,0)` m. Pivot bleibt am Szenenursprung; alle Render-/UCX-Objekte haben Position/Rotation Null und Skalierung `(1,1,1)`.
- Unreal-Abbildung: `UE_cm = (100*B.x, -100*B.y, 100*B.z)`. Die Quelle ist bereits entsprechend ausgerichtet. Keine zusätzliche Spiegelung, negative Skalierung oder Skalierungskorrektur am Actor.
- Gemessene lokale UE-Bounds aus der Quelle: Min **`(0,-10,0)`**, Max **`(132.5,42.82377624511719,280)` cm**. R255 ist nicht die rechteckige Wandbreite; gekrümmte Kontur und Endprofile erhalten.

| Anschluss | Lokale Position UE, cm | Auswärtsrichtung Yaw |
| --- | --- | --- |
| `Join_A` | `(0,0,0)` | `180°` |
| `Join_B` | `(127.49999999999999,34.16352203496813,0)` | `30°` |

Die Formel `Join_B=(255*sin(30°),255*(1-cos(30°)),0)` ist maßgeblich; Werte aus dem Manifest mit voller Genauigkeit übernehmen. Die nächste Instanz erhält diese Position und Yaw 30°. Anschlusspositionen und Z-Achsen fallen zusammen, auswärts gerichtete X-Achsen stehen gegeneinander. Blender-Instanztranslation in Metern `(1.275,-0.3416352203496813,0)`, Z-Rotation **−30°**. Die Daten sind Übergabemetadaten, kein implementiertes Unreal-Socket-/Snap-System. Toleranzen: höchstens **0,1 cm / 0,1°**; nicht auf kartesisches Raster runden.

Einzelmodule sind einschließlich Stirnflächen geschlossen. Beim Aneinanderfügen treffen die vorgesehenen verdeckten Stirnflächen aufeinander; keine zusätzlich verdoppelten Seitenflächen, Zierbänder oder Innenflächen innerhalb eines Moduls. Varianten und Verfeinerungen müssen das gesamte Endprofil einschließlich Materialkante und Kollisionsende bewahren.

## Oberfläche, UV und Kollision

- Genau ein stabiler Slot: **Index 0 `Ivory`**, vorgesehen für das bestehende `/Game/Art/Materials/ElvenBlatthof/MI_Blatthof_Ivory`. Der Blender-Farbplatzhalter definiert kein neues Unreal-Material und ersetzt keine visuelle Materialabnahme.
- Ein Kanal **UV0**, sechs gepolsterte Inseln im Bereich 0…1 für Innen-/Außenseite, Ober-/Unterkante und Stirnseiten. Seiten innerhalb ihrer Insel kontinuierlich abgewickelt, kein absichtliches UV-Overlap. Keine Texturen. Das kalibrierte Profil erzeugt später einen zusätzlichen Lightmap-Kanal; dessen Qualität und UE-UV-Anzahl sind hier noch nicht geprüft.
- Explizite radiale Split-Normalen auf beiden gekrümmten Seiten; Ober-/Unterseite und Stirnflächen hart. Export-Triangulate-Modifier `FIXED` erhält die editierbaren Quads; FBX enthält Dreiecke. Tangentenexport gemäß Kalibrierung, spätere UE-Einstellung `ImportNormals` / `MikkTSpace`.
- **Zehn geschlossene konvexe 3°-Prismen**, `UCX_SM_EB_WallInner_R255_A30_H280_00` bis `_09`. Jede Hülle entspricht exakt einem linearen Rendersegment. Gemeinsame Trennebenen, keine volumetrische Überdeckung. Alle Ursprünge und Objekttransformationen identisch mit dem Render-Mesh.
- Diese quellseitigen Prismen ersetzen für die neue Lieferung die fünf angenäherten Editorboxen des alten Anschlussmusters. Sie ändern den strukturellen Anschlussvertrag nicht. Vorgesehener Unreal-Modus **`UseSimpleAsComplex`**; Zuordnung, Körperzahl, Kapsel und Kamera erst bei Integration prüfen.

| Kennzahl | Creator-Stand |
| --- | ---: |
| Render-Vertices in Blender | 44 |
| Editierbare Quads | 42 |
| Render-Dreiecke nach Modifier / im FBX | 84 |
| Materialslots / Texturen | 1 / 0 |
| UCX-Körper / UCX-Dreiecke insgesamt | 10 / 120 |
| Gelieferte LODs / beabsichtigtes Nanite | 1 / aus |

Die tatsächliche Render-Vertexzahl in Unreal steht noch nicht fest. Für die einfache 84-Dreiecke-Wand zunächst LOD0 beibehalten; weitere LOD-Geometrie nur nach eigenem Auftrag. Kein Performancebudget oder Produktionsstatus aus diesen Zahlen ableiten.

## Export und spätere Integration

Verwendet wurde das geprüfte Profil `Blender522_UE58_LegacyFBX_Calibration01` aus `AssetSources/Calibration/BlenderUE01/unreal_import_profile.json`: **`global_scale=1`, `apply_unit_scale=True`, `apply_scale_options='FBX_SCALE_NONE'`**, Forward `-Y`, Up `Z`, `use_space_transform=True`, `bake_space_transform=False`. Nur ausgewählte `MESH`-Objekte, Modifier, `FACE`-Smoothing, Triangulierung und Tangenten; keine Animation, Kamera, Lichter oder eingebetteten Texturen. FBX-Binärversion 7400, wie beim Kalibrierungsexport. `FBX_SCALE_UNITS` bleibt verworfen.

**Kein Unreal-Import ausgeführt.** Für eine spätere, ausdrücklich beauftragte Integration nur den kalibrierten **`FbxFactory` / `FbxStaticMeshImportData`-Pfad** verwenden und tatsächliche gespeicherte Werte sowie Ergebnisgeometrie prüfen. Die im Manifest referenzierten Importoptionen sind Kalibrierungsbefunde, keine an dieser Wand gemessenen Werte. Interchange ist nicht validiert und hat im Kalibrierungsversuch alte Simple Collision behalten. Der CVar wurde dort auf den ursprünglichen Wert 1 zurückgesetzt; Backend vor Integration bewusst wählen, keine dauerhafte Projektkonfiguration aus diesem Auftrag ableiten.

Die Kalibrierung beobachtete `AutoGenerateCollision=true`, erkannte jedoch die mitgelieferten UCX ohne zusätzliche Körper. Deshalb bei dieser Wand explizit zehn passende Hüllen und keine Zusatzkörper nachweisen. Keine pauschale Kollisionslöschung aus dem Test ableiten. Das Bestandsmesh unter `JoinSample01` hat denselben Assetnamen; diese Lieferung erlaubt **keinen** Reimport oder Austausch dieses Assets. Zielpfad und Integrationsverantwortlichen gesondert festlegen.

## Tatsächliche Prüfungen und Grenzen

Separater Blender-Prozess, Quelle wieder geöffnet und anschließend FBX in leere Szene importiert; **beide Prüfungen bestanden**. Keine Quelle beim Prüfen gespeichert.

| Prüfung | Quelle | FBX → Blender |
| --- | ---: | ---: |
| Maximaler Abstand zur Bestandsgeometrie | `0.00000763 cm` | `0.00001222 cm` |
| Maximale Fuge zweier aufeinanderfolgender Module | `0.00000191 cm` | `0.00001145 cm` |
| Radiale Normalen / Nahtnormalen | bestanden | bestanden |
| Geschlossene, zusammenhängend orientierte Mannigfaltigkeit; positive Volumina | bestanden | bestanden |
| Keine degenerierten Flächen / UV-Dreiecke; UV-Koordinaten in 0…1 | bestanden | bestanden |
| Zehn geschlossene konvexe UCX, korrekte Segmentpunkte, Summe der Volumina gleich Render-Volumen | bestanden | bestanden |
| Identitätstransformationen, ein `Ivory`-Slot, ein UV-Kanal | bestanden | bestanden |

`verification.json` enthält volle Messwerte, Körperlisten und Eingangsdatei-Hashes. Zweimodul-Vorschau visuell geprüft: Wandkörper, geschlossene Kanten und durchgehende Kontur an der farblich markierten Teilung. Dies ist eine Blender-Prüfansicht, kein Unreal-Rendering.

Noch **nicht durchgeführt**: Unreal-Import/Reimport, gespeicherte UE-Bounds/Normalen/UV-/Material-/Kollisionswerte, Material-Override im Editor, Kapsel-/PIE-/Kameratest, Montage mit Boden und Dach, Performance, Packaging oder Multiplayer. Aus der Quellenprüfung folgt keine automatische Unreal-Abnahme.

Der erste Blender-Start innerhalb der Sandbox scheiterte ohne Blender-Ausgabe. Die anschließenden freigegebenen Hintergrundläufe für Erzeugung, Prüfung und Vorschau waren erfolgreich. Beim Erzeugen meldete Blender eine DeprecationWarning zu `Material.use_nodes`; Export und Prüfungen waren erfolgreich. Keine Warnungsunterdrückung oder Projektkonfiguration geändert.

Erhaltungskontrolle: SHA-256 über Pfade und Inhalte aller **1.063 bereits versionierten Dateien** vor und nach der Arbeit identisch (`2C0E00D38E559B750F66A16A9FA7AD9DD8697CA065B676694ED376292FA2D526`). Der Git-Diff des Bestands ist leer. Neue Dateien liegen ausschließlich im erlaubten Creator-Bereich. Bestehende LFS-Regeln für `.blend` und `.fbx` sind bestätigt.

Nächste Zuständigkeit: Refiner prüft Hashes und Vertrag und bearbeitet ausschließlich seine eigene Kopie. Integration und `accepted` folgen erst nach gesondertem Auftrag und tatsächlicher Unreal-Abnahme. Keine Änderungen an Refiner-Dateien, Bestandsassets, Materialien, Blueprints, Levels, gemeinsamen Generatoren oder Worldbuilding. Bis zur Quellenprüfung wurden keine Commits oder Staging-Aktionen vorgenommen; der spätere ausdrückliche Commit-Auftrag umfasst ausschließlich dieses Creator-Modul. Kein Branchwechsel oder zusätzlicher Worktree.

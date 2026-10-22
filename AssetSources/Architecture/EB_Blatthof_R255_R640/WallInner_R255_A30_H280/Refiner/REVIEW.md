# Refiner-Review: Innenwand R255 / A30 / H280

Stand: 22. Oktober 2026. **Status: `review_ready`**, Refiner-Revision 1. Keine Integrationsfreigabe (`accepted`).

## Auftrag, Herkunft und Schreibzuständigkeit

- Asset: `SM_EB_WallInner_R255_A30_H280`; KitId `EB.Blatthof.R255_R640`; ModuleId `WallInner_R255_A30_H280`; InterfaceVersion **1**.
- Eingangsrevision: **`e66d5beed7bb85313501659d646f25778515134b`**, Creator-Revision 1.
- Creator-Pfad im Commit: `AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Creator/`.
- Creator-Basis: `b1b2f051a2ead8d95c72e1253131eb9934d59b49`. Refiner-Worktree: `E:/Business/fantasy-rpg-refiner`, Branch `assets/refiner`, HEAD unverändert `b1b2f051a2ead8d95c72e1253131eb9934d59b49`.
- Ausschließlicher Schreibbereich: `AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Refiner/`.

Die Lieferung wurde direkt aus dem bezeichneten Git-Commit gelesen; LFS-Payloads wurden anhand ihrer OIDs und Größen aus der lokalen Objektablage verifiziert. Kein Checkout, Cherry-Pick oder Branchwechsel. Alle **acht** Einträge aus Creator-`SHA256SUMS` stimmen, ebenso die Querverweise in Manifest und Prüfbericht. Eine bytegleiche Eingangskopie liegt isoliert unter `Evidence/Input/`; sie ist ein Prüfbeleg, kein alternativer Creator-Arbeitsbereich. Das archivierte `create_wall.py` wurde nicht ausgeführt.

| Eingangsdatei | SHA-256 |
| --- | --- |
| Blender-Quelle | `12e0de915a47fa7b9da25b8e777032a337e0079f977d79910d6c3a72c275c1be` |
| FBX | `0617e7534a0e272d504f966c7c14a293e1204126df7d7d4a60004defb40c072f` |
| manifest.json | `7423ac40ce138bac35eee86bb87ff5df8d597cbfbd65659926e409da52ce8988` |
| verification.json | `d65e99e53d198ae75650be6c05d745ad7334bf5da7077c3b5c5f22729bcf767c` |

Vollständige Dateiliste einschließlich HANDOFF und SHA256SUMS: [input_verification.json](Evidence/input_verification.json). Die eigene Quelldatei wurde zunächst als bytegleiche Kopie übernommen und anschließend ausschließlich im Refiner-Ordner gespeichert.

## Befund und gezielte Verbesserung

Topologie, Split-Normalen und zehn konvexe Kollisionskörper bestanden die unabhängige Prüfung bereits im Eingang. Deshalb wurden keine Vertices, Flächen, Profile, Normalen oder Kollisionskörper verändert und keine Rundungen/Ornamente ergänzt. Der direkte Vergleich sämtlicher Vertexpositionen, Polygonindizes, Ecknormalen, Glättungsflags und Objektmatrizen vor/nach der Bearbeitung ist exakt gleich.

Die bisher gleich groß belegten sechs UV-Kacheln skalierten unterschiedlich große reale Flächen verschieden stark und verzerrten besonders Ober-/Unterkante. UV0 wurde deshalb metrisch neu abgewickelt: Seiten nach tatsächlicher summierter Segmentsehnenlänge und Höhe, Ober-/Unterseite durch verzerrungsfreie XY-Projektion, Stirnseiten in ihrer radialen Ebene. Alle sechs Charts werden gemeinsam gleichmäßig skaliert und mit Abstand gepackt. 48 vorhandene Kanten tragen jetzt passende UV-Nahtmarkierungen. Hinzu kommen Herkunftsmetadaten am Renderobjekt; die Schnittstellenmetadaten bleiben erhalten.

| Kennzahl | Creator-Eingang → Refiner |
| --- | --- |
| Render-Vertices / editierbare Quads | 44 / 42 → 44 / 42 |
| Dreiecke nach Triangulierung / im FBX | 84 → 84 |
| Materialslots / Texturen | 1 / 0 → 1 / 0 |
| UV-Kanäle / Inseln | 1 / 6 → 1 / 6 |
| Verhältnis höchste/niedrigste lineare UV-Dichte | 3.89205446 → 1.00000110 |
| Maximale Dreiecks-Anisotropie (1 = unverzerrt) | 10.40898063 → 1.00000130 |
| Belegte UV-Fläche | 81.000% → 76.785% |
| Kleinster Abstand der Insel-Boundingboxen | 0.03333333 → 0.01160011 UV |
| UCX-Körper / UCX-Dreiecke | 10 / 120 → 10 / 120 |
| Gelieferte LODs / beabsichtigtes Nanite | 1 / aus → 1 / aus |

Die geringere UV-Belegung ist die bewusste Folge der einheitlichen Dichte und verzerrungsfreien Charts. Der Abstand entspricht bei einer lediglich beispielhaften 1024²-Textur ungefähr 11.88 Pixeln; es wurde keine Texturgröße oder spätere Mip-/Produktionsvorgabe festgelegt. UV0 ist kein geprüfter Lightmap-Kanal. Render-Vertexzahl und UV1 in Unreal bleiben unbekannt.

## Unveränderter Maß-, Pivot- und Anschlussvertrag

- Radien **245–265 cm**, Referenzradius **255 cm**, 30°, Höhe **280 cm**, Unterkante Z0, zehn 3°-Segmente; geschlossene Vollwand ohne Öffnungen.
- R255-Startpivot am Ursprung, X tangential, Unreal Y zum Kreismittelpunkt, Z oben. Kreismittelpunkt lokal UE `(0,255,0)` cm. Alle Render-/UCX-Objekte Position/Rotation Null, Skalierung Eins, positive Determinante.
- `Join_A`: Position `(0,0,0)`, auswärts Yaw 180°.
- `Join_B`: Position `(127.49999999999999,34.16352203496813,0)` cm, auswärts Yaw 30°. Diese Werte sind aus dem Eingangsmanifest übernommen, nicht neu gerundet.
- Zweite Blender-Instanz: `(1.275,-0.3416352203496813,0)` m, Z-Rotation −30°. Grenzwerte 0,1 cm / 0,1°. Endprofile einschließlich der vorhandenen geschlossenen Stirnflächen erhalten.
- Slot 0 **Ivory** → `/Game/Art/Materials/ElvenBlatthof/MI_Blatthof_Ivory`; ein UV-Kanal UV0; zehn unveränderte `UCX_SM_EB_WallInner_R255_A30_H280_00` bis `_09`, beabsichtigter UE-Modus `UseSimpleAsComplex`.
- Lokale UE-Bounds aus der erneut geöffneten Quelle: Min `[0.0, -10.0, 0.0]`, Max `[132.5, 42.82377624511719, 280.0]` cm.

Kein Schnittstellenänderungsbedarf festgestellt. Kein Boden-/Dachteil mitgeliefert; die bestehenden Dachfüllungen wurden weder bearbeitet noch gemeinsam geprüft.

## Tatsächlich ausgeführte Prüfungen und Ansichten

Blender **5.2.2 LTS**, Build `d13f752e3b9c`; eingebautes FBX-Add-on `io_scene_fbx`, keine externen Texturen/Bibliotheken. Der Prüfcode verwendet analytische Profilpunkte und eigene Topologie-/UV-Prüfungen, ohne den Creator- oder Bestandsgenerator auszuführen.

| Prüfung | Ergebnis / Beleg |
| --- | --- |
| Eingangsdateien und eigene Kopie | Alle Hashes bestanden; `Evidence/input_verification.json` |
| Topologie und Volumen | Quelle und Rückimport geschlossen, konsistent nach außen orientiert, keine degenerierten Flächen/ko­inzidenten Vertices; `verification.json` |
| Profil, Endpunkte und Naht | Maximale analytische Profilabweichung Quelle 0.0000000000 cm; Rückimport 0.0000000000 cm |
| Zwei passende Instanzen | Nahtabweichung Quelle 0.0000019073 cm; Rückimport 0.0000019073 cm |
| Normalen | Jede radiale Ecknormale, jede harte Planfläche und transformierte Nahtnormale geprüft; keine Änderung am Eingang |
| UV0 | Sechs Inseln, endlich/nicht degeneriert, Bereich 0…1; alle Dreieckspaare auf Überdeckungsfläche > 1e-9 UV² geprüft: keine; Dichte/Verzerrung gemessen |
| Einfache Kollision | Zehn geschlossene konvexe 3°-Prismen, Segmentpunkte analytisch passend, positive Volumina; Volumensumme entspricht Renderkörper; unverändert |
| Gespeicherte eigene Quelle | In separatem Blender-Prozess neu geöffnet; sämtliche Nachherwerte stimmen exakt mit dem Bearbeitungslauf überein |
| Eigenes FBX | In leere Blender-Szene zurückimportiert: 84 Renderdreiecke, zehn UCX, Ivory/UV0/Profil/Normalen erhalten; maximaler UV-Eckfehler 0.0000000000; Binärversion 7400 |
| Erhaltungsnachweis | 1063 vorher versionierte Dateien SHA-256-identisch; alle neuen Dateien ausschließlich im erlaubten Refiner-Bereich; `Evidence/preservation_after.json` |

Sichtprüfung der finalen Blender-Ansichten: [zwei Module innen](Previews/two_modules.png), [außen und Endprofil](Previews/two_modules_outer.png), [UV0 vorher](Previews/uv_before.png), [UV0 nachher](Previews/uv_after.png). Die Wandansichten zeigen durchgehende Kontur ohne sichtbare offene Naht in diesen Blickwinkeln. Die zweite Instanz hat nur für die Sichtbarkeit der Teilung eine andere Objektfarbe; Slotvertrag und Quelldatei enthalten keine zusätzliche Variante. Die UV-Ansichten zeigen die tatsächlichen Charts unter gleichem Maßstab. Kameras und zweite Instanz wurden nur transient erzeugt und nie in die editierbare Quelle gespeichert.

Ausführungsbelege: `Evidence/refine.log`, `verify.log`, `previews.log`; Messdaten: `Evidence/refinement.json` und [verification.json](verification.json). Der erste Sandbox-Start von Blender lieferte keine Ausgabe; die erfolgreichen Läufe erfolgten nach automatischer Freigabe außerhalb der Sandbox. Ein erster Bearbeitungsprüflauf brach vor dem Speichern an einem zu strikten Metadatenvergleich ab (`refine_attempt_01.log`). Die Prüfung verwendet jetzt gemessene numerische Abweichung statt Container-/Float-Gleichheit; volle Manifestpräzision bleibt erhalten. Erste Vorschau-Ränder wurden nach Sichtkontrolle erweitert; `previews_attempt_01.log` dokumentiert den vorigen Lauf. Diese Fehlversuche sind keine ungelösten Assetfehler. Keine Warnungsunterdrückung oder Blender-Benutzerkonfiguration gespeichert.

## Exportprofil und offene nächste Zuständigkeit

Eigenes Ergebnis: [SM_EB_WallInner_R255_A30_H280.blend](SM_EB_WallInner_R255_A30_H280.blend), [FBX](Exports/SM_EB_WallInner_R255_A30_H280.fbx), [manifest.json](manifest.json). Der Export stammt aus der eigenen Kopie; das Creator-FBX wurde nicht als Ergebnis wiederverwendet.

Metric, Unit Scale 1, Meter; `global_scale=1`, `apply_unit_scale=True`, **`FBX_SCALE_NONE`**, Forward −Y, Up Z, `use_space_transform=True`, `bake_space_transform=False`. Abbildung **`UE_cm=(100*B.x,-100*B.y,100*B.z)`**, keine zusätzliche Spiegelung oder negative Objektskalierung. Nur ausgewählte MESH-Objekte: ein Render-Mesh plus zehn UCX, kontrollierte FIXED-Triangulierung, FACE-Smoothing und Tangenten; keine Kameras/Lichter/Animation/Texturen exportiert.

**Nicht durchgeführt:** Unreal-Import/Reimport, Prüfung gespeicherter UE-Einstellungen, UE-Kollision/UV1/Material-Override, Kapsel/PIE/Kamera, Montage mit Boden/Dach, Performance, Packaging, Multiplayer. Der Blender-Rückimport ersetzt keine Unreal-Abnahme. Integration ist ein gesonderter Auftrag mit Zielpfad und benannter Zuständigkeit; ausschließlich der kalibrierte **FbxFactory/FbxStaticMeshImportData-Legacy-Pfad** ist vorgesehen. Interchange bleibt nicht validiert. Die tatsächlich gespeicherten Importwerte und zehn UCX ohne Zusatzkörper später nachweisen; keine pauschale Löschung bestehender Kollision. Kein Austausch des gleichnamigen Bestandsassets freigegeben.

Creator-Dateien, Content, Materialien, Blueprints, Levels, gemeinsame Generatoren und Projektkonfiguration blieben unberührt. Keine Unreal-Karte geöffnet/gespeichert, keine Commits oder Staging-Aktionen. Die Rolle Integration hat keine Freigabe erteilt; Status bleibt höchstens **review_ready**.

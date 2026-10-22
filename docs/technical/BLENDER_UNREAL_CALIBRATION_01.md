# Blender → Unreal: Kalibrierung 01

Stand: **22. Oktober 2026**, Blender **5.2.2 LTS** (`d13f752e3b9c`), Unreal Engine **5.8**. Ergebnis: Ein technisches Static-Mesh-Testasset wurde exportiert, importiert, gezielt reimportiert und nach Kartenwechsel erneut geprüft. Die unten beschriebene Kombination ist für diesen Test bestätigt. Interchange und andere Importerprofile sind damit nicht freigegeben.

## Isolierter Umfang

| Pfad | Inhalt |
| --- | --- |
| `AssetSources/Calibration/BlenderUE01/` | Editierbare `.blend`, FBX, `manifest.json`, ausgelesenes `unreal_import_profile.json`, `calibration_result.json` |
| `Tools/AssetPipeline/blender_ue_calibration.py` | Reproduzierbarer Blender-Generator ausschließlich für das Testmodell |
| `/Game/Art/Calibration/BlenderUE01/SM_Calibration_Axes_100x60x40` | Neues Testmesh, 36 Dreiecke, 72 Render-Vertices, drei Materialslots |
| `/Game/Art/Calibration/BlenderUE01/MI_Calibration_X`, `_Y`, `_Z` | Drei neue Farbinstanzen des unveränderten vorhandenen `M_FlatCol` |
| `/Game/Art/Calibration/BlenderUE01/Lvl_BlenderUECalibration01` | Neue eigene Prüfkarte aus einer Kopie der Engine-Standardvorlage |

`Calibration` ist eine technische Ausnahme von den Produktionskategorien Architecture/Furniture/Nature. Die Testgeometrie legt keine Architektur- oder Stilmerkmale fest. Originalhaus, bestehendes Lab und Sandbox wurden nicht als Arbeitsfläche benutzt oder gespeichert. Der Editor steht abschließend wieder im ursprünglichen `Lvl_AssetLab`; es ist unverändert und nicht dirty.

Das Testobjekt besteht aus drei Quadern: eine 100-cm-X-Achse, eine bis 60 cm reichende Y-Achse und eine bis 40 cm reichende Z-Achse. Der Ursprung liegt an der unteren Ecke `(0,0,0)`, alle Actor-Skalierungen sind `(1,1,1)`. Rot/Grün/Blau markieren die drei Slots `Cal_X`, `Cal_Y`, `Cal_Z`. Diese Farben sind reine Messhilfen. Drei passende geschlossene `UCX_<RenderMeshName>_00…02`-Körper sind in der Quelle enthalten.

## Bestätigtes Exportprofil

- Blender Metric, Unit Scale **1.0**, Geometrie in **Metern**. Unreal-Zielgröße: **100 × 60 × 40 cm**.
- Achsenabbildung: **Blender +X → Unreal +X**, **Blender −Y → Unreal +Y**, **Blender +Z → Unreal +Z**. Numerisch `UE_cm = (100*B_x, -100*B_y, 100*B_z)`. Die Quelle ist entsprechend in negativer Blender-Y-Richtung modelliert. Bereits richtig ausgerichtete Blender-Quellen nicht nochmals spiegeln.
- Alte Generator-/OBJ-Koordinaten in Unreal-Zentimetern deshalb vor Blender-Bearbeitung bewusst umrechnen: `B_m = (UE_x/100, -UE_y/100, UE_z/100)`. Bei einer geometrischen Spiegelung Flächenreihenfolge/Normalen korrigieren; keine negative Objektskalierung exportieren.
- Pivot am Szenenursprung, Objektposition/Rotation Null, Skalierung Eins. Forward **−Y**, Up **Z**, `global_scale=1`, `apply_unit_scale=True`, **`apply_scale_options='FBX_SCALE_NONE'`**, `use_space_transform=True`, `bake_space_transform=False`.
- Nur ausgewählte Meshes einschließlich UCX; keine Animation, Kamera, Lichter oder eingebetteten Texturen. Modifier anwenden, kontrolliert triangulieren, `mesh_smooth_type='FACE'`, `use_tspace=True`. Ein Render-Mesh pro FBX ist hier geprüft.
- Blender-Quelle: ein UV-Kanal und drei stabile Materialslots. Die Quelle wurde erneut in Blender geöffnet: keine externen Bibliotheken, UVs/Slots, Einheiten, Einheitsskalierung und drei UCX-Objekte bestätigt.

**Der zuerst vorgeschlagene Kandidat `FBX_SCALE_UNITS` ist für diesen Importpfad verworfen:** Er ergab nur `1 × 0,6 × 0,4 cm` statt `100 × 60 × 40 cm`. Mit positiver Blender-Y-Geometrie lag die importierte Form außerdem auf Unreal −Y. Erst die explizite Achsenabbildung und `FBX_SCALE_NONE` liefern das geprüfte Ergebnis. Keine Faktor-100-Korrektur am Unreal-Actor verwenden.

Erzeugung aus dem Projektstamm (schreibt ausschließlich die angegebenen Kalibrierungsquellen):

```powershell
$taskBlender = [Environment]::GetEnvironmentVariable('BLENDER_EXE', 'User')
& $taskBlender --background --factory-startup --python-exit-code 1 `
  --python "$PWD/Tools/AssetPipeline/blender_ue_calibration.py" -- `
  --root "$PWD/AssetSources/Calibration/BlenderUE01" --revision 2
```

Revision 1 besitzt einen 10 cm breiten X-Arm; Revision 2 verbreitert ihn auf 12 cm. Gesamtbounds, Pivot und Slots bleiben gleich. Diese absichtliche Profiländerung dient nur dem Reimportnachweis; bei Produktionsmodulen wären Anschlussänderungen getrennt abzustimmen.

## Import und Reimport: Importer ausdrücklich beibehalten

Der Erstimport erfolgte über Unreal MCP `StaticMeshTools.import_file`; dessen geprüfter lokaler Quellcode erstellt ausdrücklich eine **`FbxFactory`**. Die abschließend gespeicherten Importdaten sind **`FbxStaticMeshImportData`**. Die tatsächlichen Werte stehen maschinenlesbar im mitgelieferten Profil:

| Importeigenschaft | Abschließend ausgelesener Wert |
| --- | --- |
| Import Uniform Scale / Translation / Rotation | `1` / `(0,0,0)` / `(0,0,0)` |
| Convert Scene / Convert Scene Unit / Force Front XAxis | `true` / `false` / `false` |
| Coordinate System Policy / Using LUF UI | `MatchUpForwardAxes` / `false` |
| Transform Vertex to Absolute / Bake Pivot in Vertex | `true` / `false` |
| Normalen / Tangenten | `ImportNormals`; Tangenten über `MikkTSpace` |
| Combine Meshes | Im finalen gespeicherten Importdatensatz `false`; genau ein Render-Mesh pro FBX geprüft |
| One Convex Hull per UCX | `true`; genau drei importierte konvexe Körper |
| Auto Generate Collision | Im finalen gespeicherten Datensatz `true`; vorhandene UCX wurden erkannt, keine zusätzlichen automatischen Körper beobachtet |
| Generate Lightmap UVs | `true`; Unreal besitzt zwei UV-Kanäle, Blender liefert UV0 |
| Nanite / LODs | Aus / ein LOD |

Importierte Blender-Materialien und Texturen wurden nicht angelegt; die drei neuen Unreal-Materialinstanzen wurden den stabilen Slots zugeordnet. Es wurde keine Qualität gebackener Lightmaps beurteilt. Das bestehende Projekt verwendet weiterhin dynamische Beleuchtung.

**Wichtiger Befund:** Der erste Klick auf den normalen Mesh-Reimport wechselte automatisch zu **Interchange** (`InterchangeAssetImportData`). Die sichtbare Änderung wurde übernommen, die bisherigen einfachen Kollisionshüllen blieben jedoch auf dem alten Quellstand. Ein erfolgreicher Reimporthinweis allein genügt daher nicht zur Abnahme.

Für den klassischen Pfad wurde `Interchange.FeatureFlags.Import.FBX` **nur in der laufenden Sitzung** auf `0` gesetzt. Nach Wiederherstellung eines klassischen `FbxFactory`-Imports wurden eine klassische Rückübernahme auf Revision 1 und der abschließende gezielte Import der Revision 2 mit `AssetImportTask.replace_existing=True`, `replace_existing_settings=True` und expliziter `FbxFactory` geprüft. Referenzen und Materialzuordnungen blieben erhalten. Die vollständige Rückübernahme von Interchange wurde ausschließlich am eigenen neuen Testasset durchgeführt; das ist keine automatische Migrationsanleitung für Bestandsassets.

Bei der Bereinigung dieses experimentellen Wechsels wurden nur die eigenen Test-Kollisionskörper entfernt und der eigene Customized-Collision-Zustand zurückgesetzt. Ein normaler klassischer Rückimport auf Revision 1 übernahm anschließend wieder drei passende 10-cm-Hüllen. Der finale gezielte klassische Import liefert drei 12-cm-Hüllen. Daraus folgt **keine allgemeine Pflicht, vor jedem Reimport Kollision zu löschen**. Künstlerisch im Editor erstellte Kollision darf nicht ohne gesonderten Auftrag entfernt werden.

Angeforderte Importoptionen wurden bei der Arbeit nicht blind als wirksam behandelt: Die finale Mesh-Metadatenabfrage zeigte teilweise andere gespeicherte Werte als die an `AssetImportTask` übergebenen Optionen. Maßgeblich für dieses Profil sind die Tabelle und der gemessene Ergebniszustand. Bei einem anderen Importweg oder neuer Engine-/Blender-Version erneut prüfen.

Der Sitzungswert wurde abschließend auf den ursprünglichen Wert **`1`** zurückgesetzt und ausgelesen. Keine dauerhafte CVar-/Plugin-/Projektkonfiguration geändert. Für spätere Integration den Importer deshalb erneut bewusst wählen; die kalibrierte Legacy-Kombination ist nicht gleichbedeutend mit einem automatisch passenden Standard-Reimport. Hintergrund für die Optionen: [Epic FBX-Importreferenz](https://dev.epicgames.com/documentation/unreal-engine/fbx-import-options-reference-in-unreal-engine?lang=en-US).

## Tatsächliche Abnahme

| Prüfung | Ergebnis |
| --- | --- |
| Lokale Meshbounds und Pivot | Min ungefähr `(0,0,0)`, Max `(100,60,40)` cm; größte gemessene Rundungsabweichung unter `0,00001 cm` |
| Achsen/Händigkeit | Unterschiedlich lange Arme, getrennte Farben und Abfragen in positiven/negativen Richtungen bestätigen die dokumentierte Abbildung |
| Instanzen | Drei Instanzen, alle Einheitsskalierung; zusätzliche 90°-Rotation geprüft |
| Modulstoß | A bei `(0,0,20)`, B bei `(200,12,20)`, Yaw 180°; vier Abfragen knapp beiderseits von X100 bei Y1/Y11 treffen dieselbe Höhe Z30 |
| Material-Override | B besitzt einen zusätzlichen blauen Override für Slot 0; A behält seine unveränderte Slotzuordnung; beide referenzieren dasselbe Mesh |
| Geänderter Quellstand | Testpunkt `(80,11)` war bei Revision 1 frei, nach Revision 2 liegt dort die Meshoberseite auf Z30 |
| Einfache Kollision | Drei UCX-Körper mit korrekten Bounds einschließlich 12-cm-X-Arm; sieben zusätzliche echte `trace_complex=False`-Abfragen bestätigen Arme, Freiraum, Stoß und gedrehte Instanz |
| Reimport-Erhalt | Gesamtbounds, Pivot, drei Slots, Unreal-Materialzuordnung, Actor-Referenzen und instanzbezogener Override bleiben erhalten |
| Speichern/Wiederöffnen | Prüfkarte über das unveränderte Lab gewechselt und erneut geladen; Referenzen und Override erhalten, neue Karte/Mesh nicht dirty |
| Sichtprüfung | Gerenderte Übersicht kontrolliert: passende Farbflächen, sichtbare Außenseiten, drei unterschiedlich ausgerichtete Instanzen |
| Bestandsdateien | Vor Dokumentationsänderungen 1.051 bereits versionierte Dateien per SHA-256 identisch zur Ausgangslage; später nur die beauftragte technische Dokumentation geändert |

Die Rendergeometrie wurde über `SceneTools.trace_world` mit komplexen Sichtbarkeitsabfragen geprüft; die zusätzlichen einfachen Abfragen wurden separat über Unreals Python-API ausgeführt. Kein Kapsel-/Charakterlauf, PIE-, Gameplay-, Performance-, Packaging- oder Multiplayernachweis behauptet. Der Testkörper ist kein begehbares Gebäudemodul.

Lokale, ignorierte Belege: `Saved/BlenderUECalibration01/` mit `import_initial.json`, `import_calibrated.json`, `verify_initial.json`, `check_classic_revision1.json`, `native_legacy_import.json`, `verify_reimport.json`, `simple_collision.json`, `reopen_final.json`, `preservation.json`, Exportlogs und `overview_final.png`. Die gespeicherten Kalibrierungsergebnisse im Quellordner bleiben auch ohne diese lokalen Logs verfügbar.

Explorative Fehlversuche und abgewiesene Werkzeugabfragen sind in den Logs erkennbar: falscher Startmaßstab, erste falsche Stoßaufstellung, Importerwechsel, nicht ausgelöste Slate-Aktionen, nicht exponierte Eigenschaften und eine korrigierte Python-Pfadabfrage. Die finale Abnahme ist davon getrennt; kein insgesamt fehlerfreier Entwicklungslauf behauptet. Die Mesh-Vorschau ergänzte automatisch `AdvancedPreviewScene.SharedProfiles` in `Config/DefaultEditor.ini`; ausschließlich dieser neu erzeugte Vorschauabschnitt wurde auf den byteidentischen Ausgangsstand zurückgesetzt. Originalassets, vorhandene Level, Gameplay-Quellen und Worldbuilding bleiben erhalten.

# Glasprüfung – Studie B

Status **review_ready**, nicht accepted. Eigenständige Blender-Glasfassung aus Refiner-Commit `17828dce95c0d68fd5300bc9d8cba1db1178b83f`.
Quelle: `CourtyardStudy01_ClearGlass.blend`, SHA-256 `cdad5f660ed74f3c7ec729ce32d7e54fa00ad6330d3713931ca073448f621c5d`. Eingangsquelle `../CourtyardStudy01_Refined.blend`, SHA-256 `e7316e954df13af81b423d5e81680d08c84dd86ec08a299f31cc09a45433f3c1`.

Nur das vorhandene Material **Glass** wurde geändert: Transmission 1, Roughness 0,025, IOR 1,45, fast neutraler heller Farbton. Geschlossene 3-cm-Scheibe und bestehende leichte Brechung/Reflexion bleiben. Schattenstrahlen verwenden einen weißen Transparent-BSDF, damit direktes Tageslicht die Scheibe passiert. Das ist eine ausdrücklich dokumentierte Architektur-Näherung; keine berechneten Brechungskaustiken oder reale Transmissionsmessung.

Alle Meshkoordinaten, Flächen, UVs, Materialslotnamen/-reihenfolgen, Instanztransforms und übrigen Materialien sind nach erneutem Öffnen der Glasfassung exakt identisch zum übernommenen Stand. Die ursprünglichen Refiner-Dateien wurden durch diesen Auftrag nicht beschrieben. Während des Renderns wurde die geöffnete ursprüngliche A-Quelle außerhalb dieses Auftrags gespeichert; ihr neuer Hash und der lesende Vergleich von Geometrie, UVs, Slots, Instanztransforms und Materialien stehen im gesonderten A-Beleg `Evidence/external_parent_save.json` sowie im [Erhaltungsbericht](Evidence/preservation_after.json). Diese Speicherung bleibt erhalten und wird nicht zurückgesetzt. Alle anderen **1626** geprüften Bestandsdateien bleiben byteidentisch, einschließlich FBX, Creator, alter Musterhäuser, Content, Blueprints, Maps, Konfiguration und gemeinsamer Tools. Keine offenen Blender-Fenster neu geladen oder deren ungespeicherte Arbeit überschrieben.

Die neue Quelle startet mit einer Innenansicht in **Rendered** (Cycles), damit die Glasdurchsicht sichtbar wird; Solid zeigt keine echte Transparenz. Die ursprünglichen Szeneleuchten bleiben in der gespeicherten Quelle erhalten. Neue Review-Ansichten stehen in `glass_review_views_json`.

## Reale Ansichten und Tageslichtprüfung

- [Außen](Previews/01_window_outside.png): echter eingebauter Fensterrahmen und Durchsicht ins Haus.
- [Innen](Previews/02_window_inside.png): Durchsicht nach draußen.
- [Raum mit Tageslicht](Previews/03_daylight_room.png).
- [Opake Kontrollscheibe](Previews/04_daylight_opaque_control.png): dieselbe Szene/Kamera/Beleuchtung, nur die ausgewählte Scheibe temporär opak.

Cycles, 48 Samples, AgX. Für diese vier Prüfaufnahmen wird die vorhandene Sonne gezielt zum gewählten Fenster ausgerichtet. Himmel bleibt bei Stärke 0,45; keine Innenraum-Aufhellleuchte. Die Wände, Dachflächen, übrigen Fenster und Türen bleiben vorhanden. Die temporären Render-/Kontrolleinstellungen werden nicht in die Quelle gespeichert. Der Tageslichtvergleich misst an 81 projizierten Punkten der tatsächlichen Innenbodenfläche die displaylineare PNG-Helligkeit nach AgX: klar **0.204580**, opak **0.000408**, Verhältnis **501.542**. Das belegt den Lichteinfall dieser Scheibe, ist keine Messung von Szenenradiance/Lux oder vollständige Lichtplanung.

## Übergabe

Eigene Quelle und Manifest unter diesem Glas-Unterstand; die ältere Elternlieferung bleibt als eingefrorener vorheriger Stand erhalten. Keine neuen FBX notwendig für diesen reinen Blender-Materialauftrag. Der Blender-Shader ist nicht vollständig per FBX nach Unreal übertragbar; ein Unreal-Glasmaterial und tatsächliche Durchsicht, Schatten, Tageslicht und Performance sind später separat zu prüfen. Kein Unreal-Import, kein Commit und kein Push in diesem Auftrag. Frühere Geometrieprüfungen gelten für die exakt unveränderten Meshes; in diesem Schritt wurde kein erneuter FBX-Rückimport behauptet.

Reproduktion: `glass_update.py -- --mode prepare` nur in einem noch nicht erzeugten Unterstand; danach `--mode verify`, `--mode render --view NAME` für alle vier Ansichten, Sichtprüfung und `--mode seal`. Prüfsummenliste umfasst alle Lieferdateien außer sich selbst.

# Elfenhaus B01 – Unreal-Prüfstand

Stand: 22. Oktober 2026. **Status: review_ready, nicht accepted.** Der Nutzer hat die getrennte Unreal-Prüfkarte und zwei getrennte Commits ausdrücklich freigegeben. Dieser Arbeitschat übernimmt für diesen Vorgang die Integrationszuständigkeit.

## Ausgangspunkt und Umfang

Blender-Checkpoint: **`1dfb743f85e08c9e5a826f641398c63d8e135153`**, Branch `assets/refiner`, Worktree `E:\Business\fantasy-rpg-refiner`. Quelle: `../EH_HouseB01_Study.blend`, SHA-256 **`3f035ddc7293918d456d0c8b3f26ec3658f35e5f1797c43a81b9c5035f4a9e0c`**. Die Quelle, ihre Exporte und sämtliche 50 Prüfsummen des Blender-Checkpoints sind unverändert. Der frühere R255-Wandstand `4702ccf44e88d06e97d8e3975ec34b3982673a7f` bleibt erhalten.

Die Studie verwendet das vorläufige Kit **EH.HouseB.Prototype01 / draft_1**, nicht den R255/A30-Anschlussvertrag. 10 × 12 m und 10 × 16 m sind aufgebaute Vergleichsgrößen, keine allgemeinen elfischen Baustandards. Beide Häuser besitzen genau einen vorderen Eingang. Weitere Kultur-, Status- oder Architekturregeln werden nicht festgelegt.

Neu angelegt wurden ausschließlich 34 Unreal-Assets:

- 13 Meshes unter `/Game/Art/Architecture/ElvenHouseB01/Meshes`.
- 7 eigene Materialien unter `/Game/Art/Materials/ElvenHouseB01`.
- 12 Texturen unter `/Game/Art/Textures/ElvenHouseB01`.
- Eigene Kopie `Blueprints/BP_EH_ReviewDoor` des unveränderten `BP_PrototypeDoor`.
- Eigene Karte **`/Game/Art/Architecture/ElvenHouseB01/Maps/Lvl_ElvenHouseB01_Review`**.

168 Modulinstanzen teilen die 13 Mesh-Assets. Die zwei statischen Blender-Türinstanzen sind durch zwei Instanzen der eigenen Funktionstür ersetzt. Modul- und Komponentenmaßstab sind Eins. Boden und Beleuchtung sowie Sockel/Treppen aus Engine-Würfeln dienen ausschließlich der Prüfung. Die Treppenoberseiten liegen für den tatsächlichen Lauf bei 11/22/31 cm; die dekorativen Blender-Treppen wurden nicht verändert. Vier unverkörperte Prüfleuchten und EV6…13 dienen der Innenraumbegutachtung, nicht als finale Beleuchtung oder Einrichtung.

## In Unreal ansehen

Den Editor für **diesen Worktree** verwenden, nicht den parallel geöffneten Editor des Hauptprojekts. Im Content Browser zu `Art/Architecture/ElvenHouseB01/Maps` wechseln und `Lvl_ElvenHouseB01_Review` öffnen. Die Karte ist abschließend geladen, PIE beendet und gespeichert. Der Viewport steht auf der Vorderansicht; Echtzeit wurde zur Entlastung abgeschaltet und kann bei Bedarf mit Strg+R aktiviert werden.

„Spielen“ startet vor dem kleineren Haus. Mit WASD bewegen, mit der Maus schauen und in Türnähe **E** zum Öffnen/Schließen drücken. Das größere Vergleichshaus steht 18 m daneben. Die Tür übernimmt die bestehende unmittelbare 90°-Zustandsumschaltung; es gibt keine neue Schwenkanimation oder Hindernisprüfung.

Echte Unreal-Aufnahmen: [Vorne](Previews/front.png), [Längenvergleich](Previews/comparison.png), [Rückseite](Previews/rear.png), [Innenraum](Previews/inside.png), [PIE-Tür geöffnet](Previews/pie_door_open.png), [Figur innen](Previews/pie_inside.png). Die Aufnahmen sind keine Imagegen-Bilder. Innenraum und Rückansicht machen die noch einfache Ausarbeitung sichtbar. Die finalen Editoraufnahmen verwenden eine Belichtungskorrektur von −1,25 EV gegen ausgewaschene Außenflächen; die PIE-Prüfaufnahmen stammen unmittelbar vor dieser reinen Darstellungsanpassung. Geometrie und Physik blieben dabei unverändert.

## Tatsächliche Prüfungen

| Prüfung | Ergebnis und Beleg |
| --- | --- |
| Importweg | Alle 13 Meshes besitzen `FbxStaticMeshImportData`. MCP `StaticMeshTools.import_file` verwendet ausdrücklich `FbxFactory`. [Ausgelesene Daten](Evidence/mesh_initial.json). |
| Profil | Skalierung 1; Translation/Rotation Null; ConvertScene true, ConvertSceneUnit false, ForceFrontXAxis false; TransformVertexToAbsolute true; BakePivot false; ImportNormals/MikkTSpace; CombineMeshes false; OneHullPerUCX true; AutoGenerateCollision false; GenerateLightmapUVs true; Nanite false. |
| Größe und Achsen | `UE_cm=(100*B.x,-100*B.y,100*B.z)`, keine zusätzliche Spiegelung. Alle 13 lokalen Bounds gegen echte Blender-Vertexbounds geprüft; maximal **0,0000972748 cm** Abweichung. [Vergleich](Evidence/bounds_comparison.json). |
| Rendergeometrie/UV/Slots | Dreieckszahlen und Materialslotreihenfolgen stimmen mit dem Quellmanifest überein; zwei UV-Kanäle nach Lightmap-UV-Erzeugung. Alle Slots referenzieren die neuen passenden Materialien. [Native Prüfung](Evidence/native_verification.json). Kein Nachweis finaler Lightmapqualität. |
| Materialien | BaseColor, Roughness und Normalmaps in vier eigenen PBR-Graphen; OpenGL-Normalmaps mit Grünkanalumkehr, lineare Normal-/Roughnessdaten. Alle sieben Materialgraphen erfolgreich kompiliert. Normalstärke XY 0,32 bei Holz, sonst 0,20. Fenster bleiben opak reflektierend. [Materialien](Evidence/materials.json). |
| Quellkollision | Beim Erstimport stimmen alle 13 UCX-Anzahlen mit dem Manifest überein: Wände 1/1/1/6, Dächer je 16, Boden 1, übrige Module 0. |
| Türblattkollision | Ausschließlich am neuen Unreal-Türmesh konvexe Zerlegung angefordert, maximal vier Hüllen; **tatsächlich eine Hülle**. Die Blender-Quelle hat weiterhin null UCX für das Blatt. Bei dessen Reimport muss die eigene Unreal-Kollision gezielt erneut erzeugt und geprüft werden. |
| Einfache Physik | 14 Linien- und vier Kapselabfragen bestanden: Böden und Bodenstöße, untersuchte Dachstöße, Vorder-/Rückwände und geschlossene/offene Türen an beiden Häusern. Spielerkapsel tatsächlich Radius **35**, Halbhöhe **90 cm**. Temporäre Editor-Türdrehungen wiederhergestellt. [Messwerte](Evidence/native_verification.json). |
| Reimport | Wand SolidA und Dachmittelteil ausdrücklich klassisch aus derselben FBX-Quelle erneut importiert: Bounds, Dreiecke, Slots, Materialreferenzen, Hüllen und sämtliche betroffenen Actor-Meshreferenzen unverändert. Das prüft Wiederholbarkeit; keine geänderte Geometrierevision behauptet. [Vorher/nachher](Evidence/reimport.json). |
| Speichern/Wiederöffnen | Über die Engine-Standardvorlage auf die gespeicherte eigene Karte zurückgewechselt; Karte nicht dirty, native Prüfungen anschließend erneut bestanden. [Beleg](Evidence/reopen.json). |
| Tatsächliches Gameplay | Nach dem Wiederöffnen im separaten PIE-Fenster E: öffnen → schließen → öffnen. Vier tatsächliche W-Eingaben bewegen die Figur von Y100 bis ungefähr Y−533; Z bleibt auf dem Hausboden ungefähr 123 cm. Keine weitere Teleportation während des Laufes. [Beleg](Evidence/pie_result.json). |
| Erhalt des Bestands | **Alle 1.149** zu Beginn bereits versionierten Dateien byteidentisch zum Blender-Checkpoint, einschließlich aller bestehenden `Content/`-Assets, Karten, Konfiguration und Generatoren. [Hashprüfung](Evidence/preservation.json). |

Der lokale Development-Editor wurde für den eigenen Worktree gebaut; Build erfolgreich. Weder C++-Quellen noch Projektkonfiguration wurden geändert. Die Blender-Quellöffnung und die 13 Blender-FBX-Rückimporte sind im unveränderten vorherigen Checkpoint geprüft; diese Unreal-Integration erzeugte keine neuen Blender-Exporte.

## Grenzen und offene Punkte

- Menschliche Freigabe von Stil, Größe, Dachform und Materialwirkung steht aus. Dies ist eine erste begehbare Hausstudie, kein fertiges Endprodukt. Innenflächen, Einrichtung, transparente Fenster und anspruchsvollere Varianten sind offen.
- Giebel, seitliche Dachfüllungen und Vordach haben weiterhin keine eigene einfache Kollision. Dachhüllen sind Näherungen. Der erfolgreiche mittlere Türlauf ersetzt keine vollständige Kapsel-/Kameraprüfung aller Kanten, Sprünge und Winkel.
- Die Innenaufnahmen zeigen weiterhin einfache Flächen, unruhige Lumen-Beleuchtung und stellenweise helle Fugen. Diese Material-/Beleuchtungswirkung ist nicht abgenommen.
- PIE meldete bei zwei parallel laufenden Editoren VRAM-Überbelegung; außerdem erschien eine Warnung zur gecachten Lumen-/Sky-Beleuchtung und `r.EyeAdaptation.CachedLightingPreExposure`. Keine Warnungen unterdrückt und keine gemeinsame Renderer-Konfiguration angepasst. Beleuchtungsprofil und Ressourcenbedarf gesondert prüfen; kein Performance-Nachweis.
- Nur zwei Hauslängen und vorhandene Wand-/Fensterbelegungen sind aufgebaut. Weitere Dachsilhouetten, Breiten, Geschosse und prachtvollere Häuser benötigen eigene Arbeit und Designentscheidungen.
- Keine LOD-/Nanite-Optimierung, keine Serienhaus-Performance, kein Cooking/Packaging, kein Multiplayer-Nachweis. Die Fensterwand bleibt mit 1.272 Dreiecken eine dokumentierte Prototypausnahme.

## Arbeitsbelege und Reproduktion

Die Skripte in diesem Ordner verwenden MCP auf **Port 8001**, mit eigenem Editor und Pfad-/Kartenschutz. Der laufende Hauptprojekt-Editor auf Port 8000 wurde ausschließlich lesend untersucht. `bootstrap.py` wird manuell über die beobachtete Editor-Konsole ausgeführt; `-ExecutePythonScript` beendet den Editor nach Skriptabschluss und ist für den dauerhaften Review-Editor ungeeignet.

Reihenfolge für eine neue isolierte Lieferung: `extract_assembly.py` in Blender, `bootstrap.py`, `import_modules.py`, `materials.py`, `configure_door.py`, `assemble.py`, `review_lighting.py`. Die MCP-Batches laufen über `ue_rpc.py batch <Datei>`. Native Daten-/Kapselprüfungen und der ausdrücklich gesetzte Legacy-Reimport laufen über `ue_console.py verify_native.py` bzw. `reimport_native.py`, weil entsprechende Funktionen im MCP-Werkzeugsatz fehlen oder der Importer vorhandene Assets ablehnt. `pie_review.py` prüft eine bereits gestartete eigene PIE-Sitzung. Nicht blind erneut importieren oder fremde Pfade ersetzen.

Explorative Probleme sind von bestandenen Abschlussprüfungen getrennt: automatisch beendeter erster Startmodus, korrigierter Roughness-Sampler, beobachtete Blender-Suffixe bei Treppennamen, nicht exponierte Python-Eigenschaften, Fokusprobleme im eingebetteten PIE und zunächst veraltete temporale Viewport-Sichtbarkeit. Das separate Spielfenster und aufgewärmte Viewport-Aufnahmen lieferten die dokumentierten Abschlussbelege. Kein insgesamt fehler- oder warnungsfreier Entwicklungslauf behauptet.

Der vorübergehende Sitzungswert `Interchange.FeatureFlags.Import.FBX=0` wurde auf den ursprünglichen Wert **1** zurückgesetzt. Keine `/Game/`-Pakete und keine Karte bleiben dirty. Automatisch dirty markierte Engine-/Plugin-Hilfspakete wurden ausdrücklich nicht gespeichert; es gab kein „Save All“. [Abschlusszustand](Evidence/session_final.json).

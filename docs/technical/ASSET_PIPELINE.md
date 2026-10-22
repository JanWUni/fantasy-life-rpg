# Asset-Lab und World-Sandbox

Stand: 22. Oktober 2026, Unreal Engine 5.8. Diese Arbeitskonventionen gelten für den technischen Prototyp. Sie legen weder den endgültigen Grafikstil noch Architektur, Kulturen, Geografie oder das spätere modulare Gebäudesystem fest. Der jeweils geprüfte Stand steht in [TECHNICAL_STATUS.md](../TECHNICAL_STATUS.md).

## Ablage und Benennung

Neue wiederverwendbare Inhalte liegen in `Content/Art/` (im Editor `/Game/Art/`):

| Ordner | Inhalt |
| --- | --- |
| `Architecture` | Wände, Dächer, Fenster und sonstige Gebäudeteile |
| `Furniture` | Möbel und Einrichtungsobjekte |
| `Nature` | Pflanzen, Bäume und Felsen |
| `Materials` | Wiederverwendbare Materialien und Materialinstanzen |

Präfixe: `SM_` für Static Meshes, `BP_` für Blueprints, `M_` für Materialien, `MI_` für Materialinstanzen, `T_` für Texturen und `Lvl_` für Karten. Namen sollen Funktion und bei modularen Testteilen die Maße erkennen lassen. Assets über den Content Browser referenzieren; zum Platzieren derselben Geometrie weitere Actor-Instanzen verwenden, keine unabhängigen Mesh-Kopien.

Bestehende Inhalte bleiben an ihren bisherigen Pfaden. Insbesondere Tür, Rahmen, Spieler und Naturmeshes werden direkt aus `/Game/Prototype/` referenziert. Die Ordner `Art/Nature` und `Art/Furniture` bleiben zunächst leer; `.gitkeep` erhält sie im Dateisystem. Die Möbel im Lab sind einfache Levelinstanzen vorhandener Geometrie, keine zweite Möbelbibliothek.

## Vom Lab in die Sandbox

1. `/Game/Prototype/Maps/Lvl_AssetLab` öffnen. Es bietet eine **120 × 80 m** große Fläche mit 100-cm-Hauptraster, getrennte Bereiche für Architektur, Möbel und Natur, Podeste sowie 100-cm- und 180-cm-Referenzen. Die ursprünglichen Vergleichsgruppen stehen im mittleren Bereich; die freie Umgebung bietet Platz für weitere Gebäudemuster. Outliner-Ordner beginnen mit `Lab/` oder `Workspace/`.
2. Ein neues Asset im passenden `Art`-Ordner anlegen. Auf realistische Maße, verständlichen Pivot, Rotation und einfache Kollision prüfen. Am Boden und neben den Referenzkörpern beurteilen; Podeste sind 30 cm hoch.
3. Mindestens zwei Instanzen am Raster platzieren. Übergänge, Kollision, Kamera und Materialien in PIE testen. Einen Material-Override an nur einer Instanz setzen und kontrollieren, dass die andere unverändert bleibt. Änderungen am gemeinsamen Mesh oder am gemeinsamen Material wirken dagegen auf alle Referenzen.
4. Asset und Lab ausdrücklich speichern. Im Content Browser dasselbe Asset in `/Game/Prototype/Maps/Lvl_WorldSandbox` ziehen. Diese Karte bietet eine 120 × 120 m große, ebene Fläche mit Tagesbeleuchtung. Sie ist zunächst eine freie Baufläche mit einem Wandsegment.
5. Beide Karten erneut öffnen und in PIE testen; die bisherige Startkarte bleibt `Lvl_EnvironmentTest_01`. Steuerung: WASD, Maus, Leertaste und E an der Tür. Neue Karten besitzen eigene GameMode-Overrides auf den vorhandenen `BP_PrototypeGameMode`.

Die Lab-Beleuchtung nutzt Tageslicht bei 6500 K ohne Nebel oder Wolken. Das unterstützt einen neutralen Vergleich, ersetzt jedoch keine kalibrierte Materialprüfung. Die Sandbox nutzt 5700 K, Himmel, Wolken und Nebel. Künstlerische Materialqualität und finale Lichtstimmung sind offen.

## Technischer Wandnachweis

`/Game/Art/Architecture/SM_Wall_Test_400x20x300` ist ein eigenständiges Mesh mit **400 cm Breite (X), 20 cm Tiefe (Y), 300 cm Höhe (Z)**. Der Pivot liegt an der unteren Ecke `(0,0,0)`; die lokalen Bounds reichen bis `(400,20,300)`. Die Form wurde im Unreal Editor über MCP aus einer vorhandenen Würfelinstanz zusammengeführt: 12 Dreiecke, ein Materialslot (`lambert1` vom Ausgangsmesh), ein einfacher konvexer Kollisionskörper. Keine externe Modellierungspipeline wurde dafür eingeführt.

Zwei Instanzen im Architektur-Bereich stehen nebeneinander bei Einheitsskalierung. Die zweite zeigt einen blauen Material-Override. Die Sandbox referenziert dasselbe Mesh mit 90 Grad Drehung. Das Standardmaterial `MI_WorkspaceWall` ist austauschbar; alle sechs neuen Materialinstanzen verwenden den vorhandenen Master `/Game/LevelPrototyping/Materials/M_FlatCol` mit `Base Color`, `Roughness` und `Metallic`.

Als Funktionsdemo stehen die vorhandenen Blueprints `BP_PrototypeDoor` und `BP_PrototypeDoorFrame` im Lab. Ihre Implementierungen bleiben unverändert: bestehende E-Interaktion, Aktionstext und goldene Hervorhebung. Die Tür behält ihre bisherigen Grenzen, insbesondere unmittelbares Umschalten statt Schwenkanimation oder Hindernisprüfung.

## Maße, Pivot und Kollision

- 1 Unreal Unit entspricht 1 cm. Neue modulare Geometrie auf einen 10-cm-Arbeitsraster und bei großen Modulen auf 100-cm-Schritte ausrichten; Sondermaße ausdrücklich benennen.
- Wiederverwendbare Meshes in endgültigen Maßen speichern und in den Karten möglichst mit Skalierung `(1,1,1)` verwenden. X/Y bilden die Grundfläche, Z zeigt nach oben. Rotation und Skalierung vor dem Export anwenden; negative Skalierungen vermeiden.
- Bei Wandmodulen den Pivot an einer unteren Rasterecke verwenden. Andere Assettypen dürfen einen passenden Bodenmittelpunkt oder Gelenkpunkt besitzen; ihre Konvention dokumentieren und beim Austausch erhalten.
- Solide Teile müssen Spieler und Kamera passend blockieren. Möglichst einfache Boxen oder konvexe Körper verwenden und mit einer Spielerkapsel testen. Dekorative Bereichslinien und Text sollen nicht blockieren. Nach Änderungen am Mesh Kollision und Durchgänge erneut prüfen.
- Materialslots verständlich und stabil halten. Overrides an Mesh-Komponenten isolieren Varianten; Materialinstanzen isolieren Farb- und Oberflächenparameter vom Master. Kollisions-, UV- und Größenprüfung bleibt unabhängig vom Grafikstil erforderlich.

## Spätere Blender-Modelle

### Von der Stilstudie zum ausgearbeiteten Modell

Im Lab zuerst mehrere einfache Muster derselben Formsprache nebeneinander beurteilen. Große Formen, Dach-/Fensterproportionen, Farbflächen und Wiedererkennung sollen aus normaler Spielkamera überzeugen. Begehbarkeit, Durchgangshöhen, Kollision und Pivot bereits in dieser Phase prüfen. Feine Ornamente, einzelne Dachschuppen, aufwendige Texturen und vollständige Möblierung können warten. Ein Prototyp braucht nur so viele Details, dass seine gestalterische Absicht verständlich wird; der aktuelle Blatthof ist dafür ein erster Vergleichspunkt.

Wenn einige Muster zusammenpassen, ein repräsentatives Haus oder Bauteil in Blender ausarbeiten: saubere Geometrie, kontrollierte Rundungen und Normalen, UVs, stabile Materialslots, einfache Kollision und anschließend gezielte Oberflächendetails. Blender dient dabei auch zur Vereinfachung und Strukturierung; ein fertiges Spielasset benötigt nicht automatisch mehr Polygone. Referenzmaße und Pivot des Platzhalters übernehmen und den Austausch im Lab prüfen. Erst nach diesem kleinen Importversuch weitere Varianten systematisch ausarbeiten und in der World-Sandbox im räumlichen Zusammenhang beurteilen. Dieser Ablauf ist eine technische Arbeitskonvention, keine endgültige Kultur- oder Stilentscheidung.

### Import- und Austauschprüfung

Ein späteres Blender-Modell ersetzt oder ergänzt das Testasset erst nach einem kleinen Importversuch. Keine neue Importautomatisierung ist Bestandteil dieses Auftrags.

1. In realen Maßen modellieren: 1 m in Blender soll nach dem Import 100 UU ergeben. Mit einem bekannten 1-m-Referenzkörper verifizieren; Export-/Import-Skalierung nicht nach Gefühl korrigieren.
2. Objektursprung am vereinbarten Pivot setzen, Transformationen anwenden, Materialslots und UVs vorbereiten. Quelldateien gesammelt beim zuständigen Asset ablegen; `.blend` und binäre Austauschformate entsprechend den bestehenden LFS-Regeln verwalten.
3. Zunächst ein einzelnes FBX über den Unreal-Importdialog importieren. Ausrichtung, Bounds, Skalierung und Slotzuordnung im Editor prüfen. Einfache Kollision im Editor erzeugen oder passende `UCX_`-Körper importieren und danach prüfen.
4. Im Lab zwei Instanzen, Materialwechsel und Kollision testen. Erst anschließend dasselbe Asset in der Sandbox verwenden. Beim Reimport vorhandene Referenzen, Pivot und Slots erhalten; vor einem Austausch bestehender Gameplay-Assets dessen Auswirkungen gesondert prüfen.

## In diesem Auftrag angelegte Dateien

| Pfad | Zweck |
| --- | --- |
| `Content/Prototype/Maps/Lvl_AssetLab.umap` | Begehbare Testwerkstatt, drei Kategorien und Türdemo |
| `Content/Prototype/Maps/Lvl_WorldSandbox.umap` | Separate freie Baufläche |
| `Content/Art/Architecture/SM_Wall_Test_400x20x300.uasset` | Gemeinsames Wandmesh |
| `Content/Art/Materials/MI_WorkspaceWall.uasset` | Wandstandard |
| `Content/Art/Materials/MI_LabArchitecture.uasset` | Architekturmarkierung und Wandvariante |
| `Content/Art/Materials/MI_LabFurniture.uasset` | Möbelmarkierung und Platzhalter |
| `Content/Art/Materials/MI_LabNature.uasset` | Naturmarkierung |
| `Content/Art/Materials/MI_LabPedestal.uasset` | Podeste und Lab-Rand |
| `Content/Art/Materials/MI_SandboxGround.uasset` | Sandbox-Boden |
| `Content/Art/Furniture/.gitkeep`, `Content/Art/Nature/.gitkeep` | Erhalt der leeren Bibliotheksordner |
| `Source/FantasyLifeRPG/Prototype/Tests/AssetWorkspaceTests.cpp` | Zwei editorseitige PIE-Prüfungen |
| `docs/technical/ASSET_PIPELINE.md` | Dieser Arbeitsablauf |

Zusätzlich wird `docs/TECHNICAL_STATUS.md` fortgeschrieben. Lokale MCP-Skripte, Build-/Testprotokolle und Bildschirmaufnahmen liegen ignoriert unter `Saved/InteractionDev/asset_workspace*`, `workspace_*`, `run_workspace_phase.py` und `verify_asset_workspace.py`; sie gehören nicht zu den zu versionierenden Projektquellen.

## Grenzen und nächste Prüfungen

Die Sandbox hat offene Außenkanten; außerhalb der Fläche fällt die Figur bis zur Kill-Z. Das Lab besitzt niedrige Randbegrenzungen, die übersprungen werden können. Ein Rücksetz-/Respawnsystem, Sandbox-Navigation, NPCs, Landschaft, Gebäudeeditor und neue Gameplay-Systeme wurden nicht ergänzt.

Vor weiteren Assets beide Karten manuell ablaufen: Lesbarkeit der Schilder aus verschiedenen Entfernungen, Kameragefühl an Podesten und Wand, Kanten und Materialwahrnehmung prüfen. Lab-Tür mit E öffnen/schließen und Anzeige sowie Hervorhebung beurteilen. Spätere Blender-Importe, finale UVs/Materialien, Packaging, Multiplayer und größere Szenen benötigen eigene Prüfungen. Als nächster kleiner Schritt bietet sich ein weiteres Rastermodul oder ein einzelnes importiertes Modell mit demselben Lab→Sandbox-Ablauf an; eine größere Weltgestaltung bleibt eine spätere Entscheidung.

## Paralleler Creator-/Refiner-Workflow

Stand: **22. Oktober 2026 · Dokumentationsgrundlage, keine Asset-Produktion**. Die folgenden technischen Arbeitsregeln ergänzen den Lab-Ablauf für beide Rollen. Bei Bestandsmodulen gilt ihr dokumentierter Anschlussvertrag; ein allgemeines Raster ersetzt ihn nicht. Neue Kultur-, Materialsymbolik-, Sozialstatus- oder Architekturregeln werden hier nicht festgelegt. Bestätigte Entscheidungen in [DECISIONS.md](../DECISIONS.md) bleiben maßgeblich.

### Geprüfter Bestand und visuelle Referenz

| Befund | Grundlage und Grenze |
| --- | --- |
| Aktives Repository | `E:\Business\fantasy-rpg\Unreal Engine Project\FantasyLifeRPG`, C++-Projekt, `.uproject` mit EngineAssociation `5.8`. Der Chat-Ordner auf C: ist kein Git-Repository; `UE-Backup-2026-10-21` ist eine ältere Sicherung. Neue Arbeitsaufträge am E:-Projekt beginnen. |
| Vorhandene Konventionen | `Content/Art/{Architecture,Furniture,Nature,Materials}`, Präfixe `SM_`, `BP_`, `M_`, `MI_`, `T_`, `Lvl_`; 1 UU = 1 cm, 10-/100-cm-Raster, Einheitsskalierung und stabile Materialslots. |
| Elfenhaus | `Content/Art/Architecture/ElvenBlatthof/BP_ElvenBlatthof_Study.uasset`, vier Meshes unter `Meshes/`, neun Materialinstanzen unter `Content/Art/Materials/ElvenBlatthof/`. Laut bestehender Studie 39.616 Dreiecke ohne Tür/Rahmen, davon 29.040 in der Detail-/Rippengruppe. Kein neues Auslesen der Editor-Renderdaten in dieser Untersuchung. |
| Modulare Folgestände | Vier Meshes unter `ElvenBlatthof/Modular/JoinSample01/Meshes/`; zusätzlich `Modular/ClosedHouse01/BP_EB_House_A60_Prototype01.uasset`. Anfangs drei `_Sealed`-Meshes für Eingang und Enden; während der Untersuchung wurden die Enden außerhalb dieses Auftrags durch `SM_EB_EndCap_R245_650_A3_{Start,End}_Full` ersetzt. ClosedHouse01 wird im bisherigen Anschlussdokument noch nicht vollständig beschrieben; seinen aktuellen Gesamtzustand vor Bearbeitung gesondert erfassen. |
| Geometriequellen | `Tools/Prototype/generate_elven_blatthof.py`, `generate_elven_join_sample.py`, `generate_elven_closed_house.py`; vorhandene OBJ/MTL/Manifeste unter `Saved/ElvenBlatthofSources`, `Saved/ElvenJoinSources`, `Saved/ElvenClosedSources`. Keine `.blend`-/`.fbx`-Quelle im untersuchten Projektbestand gefunden. Generatoren wurden hier nicht ausgeführt. |
| Sichtprüfung | Gespeicherte `Saved/InteractionDev/elf_house_final_overview.png`, `closed_house_overview.png` und `closed_house_inside_pie.png` angesehen. Außenansichten zeigen geschwungene helle Wandmassen, breite grünblaue Dächer und am Original verzweigte Holz-/Rippenformen. Das geschlossene Muster ist deutlich einfacher. Die dunkle Innenaufnahme erlaubt keine zuverlässige Detailbeurteilung. Keine neue Live-Editorprüfung. |
| Renderer | Vorhandene `Config/DefaultEngine.ini`: Lumen-Konfiguration, virtuelle Schatten, DX12/SM6; `r.AllowStaticLighting=False`. Keine neue Konfiguration und keine gemessene Laufzeitperformance. |

Die Beobachtungen dienen dem Vergleich von Silhouette, Proportionen und Detailverteilung. Sie machen Blattdächer, Farben oder Materialien nicht zum verpflichtenden Standard aller elfischen Gebäude. Das Originalhaus einschließlich Tür-/Rahmenreferenzen bleibt erhalten. Vergleichsdokumente: [Stilstudie](ELVEN_BLATTHOF_STUDY.md), [Modularisierungsplan](ELVEN_MODULAR_BUILDING_PLAN.md), [implementierter Anschlussversuch](ELVEN_JOIN_SAMPLE_01.md). Dessen frühere Prüfungen sind keine in diesem Auftrag wiederholten Tests.

### Rollen und eindeutige Dateizuständigkeit

| Bereich | Asset Creator | Asset Refiner |
| --- | --- | --- |
| Aufgabe | Neue einfache, modulare Grundmodelle gemäß konkretem Auftrag; Maße, Pivot, Anschlüsse und Grundkollision zuerst | Übernommene Grundmodelle in Blender bereinigen und gezielt verbessern; Silhouette und technischen Anschlussvertrag erhalten |
| Schreibbereich je Modul | `AssetSources/<Kategorie>/<KitId>/<ModuleId>/Creator/` | `AssetSources/<Kategorie>/<KitId>/<ModuleId>/Refiner/` |
| Eigene Dateien | `.blend`, eigener Export, `manifest.json`, `HANDOFF.md`, bei Bedarf Erzeugungsskript und Vorschauen im eigenen Bereich | Eigene `.blend`-Kopie, eigener Export, `manifest.json`, `REVIEW.md`, bei Bedarf Bearbeitungsskript und Vorschauen im eigenen Bereich |
| Fremder Bereich | Refiner-Dateien und andere Module nur lesen | Creator-Dateien und andere Module nur lesen; Übernahme durch Kopie statt Überschreiben |
| Gemeinsame Dateien | Kein paralleles Schreiben an `Content/`, `Tools/Prototype/`, Pipeline-Dokumentation, Projektkonfiguration oder gemeinsamen Materialien | Dieselbe Einschränkung |

Ein Auftrag benennt Rolle, KitId, ModuleId, Ausgangsrevision und erlaubte Pfade. Ein Agent darf mehrere Module übernehmen; zwei Agenten bearbeiten dieselbe Datei niemals gleichzeitig. Creator kann Modul B beginnen, während Refiner den eingefrorenen Stand von Modul A bearbeitet. Gemeinsame Generatorfunktionen nur in einem getrennten, koordinierten Auftrag ändern; bestehende Prototype-Generatoren nicht nebenbei umbauen.

**Integration ist eine Zuständigkeit, kein zusätzlicher spezialisierter Agent:** Pro Importvorgang genau eine benannte Person oder einer der beiden Agenten. Nur diese Zuständigkeit darf im ausdrücklich erlaubten Umfang nach `Content/` importieren/reimportieren und Lab, Blueprint-Zusammenstellungen oder gemeinsame Materialreferenzen speichern. Eine Rollenbeschreibung allein erlaubt keine Änderung vorhandener Assets oder Levels.

### Namen und Quellordner

Neue technische IDs und Dateinamen verwenden ASCII, Buchstaben/Ziffern und Unterstriche, keine Leerzeichen/Umlaute. Schreibweise und Groß-/Kleinschreibung bleiben stabil. Schema für neue Meshes: `SM_<KitKurzname>_<Funktion>_<MaßeOderProfil>[_<Variante>]`. Maße im Namen sind Zentimeter; `R` Radius, `A` Winkel in Grad, `H` Höhe. Bestehende Namen nicht rückwirkend umbenennen.

Beispiele aus dem Bestand: `SM_Wall_Test_400x20x300`, `SM_EB_WallInner_R255_A30_H280`, `SM_EB_LeafRoof_R215_695_A30`. Ein Variantenkürzel ändert die Gestaltung innerhalb desselben Anschlussvertrags. Eine inkompatible Geometrie benötigt eine neue Interface-Version und eigene Identität; kein stiller Reimport. Revisionsstände stehen in Git und im Manifest, nicht als fortlaufende `_final_final`-Dateinamen.

Neue Quelldateien liegen künftig **außerhalb von `Content/` und `Saved/`**:

```text
AssetSources/<Kategorie>/<KitId>/<ModuleId>/
  Creator/<AssetName>.blend
  Creator/Exports/<AssetName>.fbx
  Creator/manifest.json
  Creator/HANDOFF.md
  Refiner/<AssetName>.blend
  Refiner/Exports/<AssetName>.fbx
  Refiner/manifest.json
  Refiner/REVIEW.md
```

`<Kategorie>` entspricht `Architecture`, `Furniture` oder `Nature`; `<AssetName>` enthält das Unreal-Präfix. Beispiel für technische IDs: KitId `EB.Blatthof.R255_R640`, ModuleId `WallInner_R255_A30_H280`. Die Struktur wird erst mit einem beauftragten Asset angelegt. Kein neues Modell oder leeres Quellgerüst ist Bestandteil dieser Einrichtung.

Das freigegebene Ergebnis wird unter dem passenden bestehenden `Content/Art/`-Pfad importiert; Creator-/Refiner-Namen werden nicht Bestandteil der endgültigen Unreal-Assetnamen. Neue Kits erhalten einen eigenen Unterordner. Bestandsassets werden nur bei ausdrücklichem Austauschauftrag ersetzt. Materialien bleiben unter `Content/Art/Materials/`; vorhandene Master/Instanzen referenzieren, keine Kopie je Modul.

`.blend`, `.fbx`, `.uasset`, `.umap` und übliche Bildquellen sind bereits in `.gitattributes` für LFS erfasst. Keine Änderung dieser Regeln erforderlich. Verbindliche Blender-Quellen und freigegebene FBX-Exporte versionieren; nur wiederherstellbare Zwischenprodukte, Recovery-Dateien und lokale Logs ignorieren. `.blend1` usw. und Python-Bytecode werden durch `.gitignore` ausgeschlossen. Textmanifeste, Skripte und Übergaben bleiben normale Git-Dateien. Ignorierte `Saved/`-Quellen sind keine dauerhafte Blender-Übergabe; benötigte Referenzdaten später gezielt übernehmen oder aus der passenden Generatorrevision rekonstruieren.

### Einheiten, Pivot und Snap-Vertrag

- Unreal: 1 UU = 1 cm. Blender-Arbeitsbasis für neue Dateien: Metric, Unit Scale 1.0, Koordinaten in Metern; 1 m muss in Unreal 100 cm ergeben. Ein in Zentimetern numerisch vorliegendes OBJ ist beim Einlesen entsprechend umzurechnen, nicht ungeprüft als Meter zu behandeln. Andere Bestandsdateieinheiten nur mit dokumentierter Umrechnung übernehmen.
- Unreal-Zielachsen: X entlang der vereinbarten Modulrichtung, Y gemäß Profil, Z oben. Blender-/FBX-Achsenumrechnung ausdrücklich protokollieren; Vorwärtsrichtung und Händigkeit an asymmetrischen Merkmalen prüfen. Nicht allein auf einen symmetrischen Würfel vertrauen.
- Endgültige Größe im Mesh, Rotation angewandt, Skalierung `(1,1,1)` in Blender und Unreal. Keine negative/nichtuniforme Skalierung zum Erzeugen kompatibler Varianten. Lage relativ zum vereinbarten Pivot beibehalten; Exportobjekt mit diesem Pivot am Szenenursprung, keine beiläufige Neuzentrierung nach Bounds.
- Gerade Wandmodule: Pivot an unterer Rasterecke, X entlang der Wand, Y zur Innenseite, Z oben. Bodenoberkante und Anschluss-Z im Manifest angeben; bestehender Testwandvertrag bleibt 400 × 20 × 300 cm. 10-cm-Arbeitsraster, 100-cm-Hauptraster für große Module; Sondermaße erhalten und dokumentieren. Bei Props Bodenmittelpunkt, bei Türen Gelenkpunkt nur nach dem jeweiligen Assetvertrag.
- Blatthof-Bogenkit: Boden R240…650, Innenwand R245…265, Außenwand R630…650 cm; H280, Boden Z−12…0; Dach R215…695. Gemeinsamer Pivot auf R255 am Feldanfang und Z0, X tangential, Y zum Kreismittelpunkt. Zusammengehörige Lagen teilen denselben Transform. Der Mittelpunkt liegt lokal bei `(0,255,0)` cm.
- Für Winkel θ: `Join_A.position=(0,0,0)`, Yaw 180°; `Join_B.position=(255*sin(θ),255*(1-cos(θ)),0)`, Yaw θ. Für 30° also `(127.5,34.16352203496813,0)` cm. Daten mit voller Rechengenauigkeit übernehmen; nicht aufs kartesische Raster runden. Anschlusspositionen und Z-Achsen fallen zusammen, ihre auswärts zeigenden X-Achsen stehen gegeneinander.
- Technische Abnahme neuer Verbindungen: Positionsversatz höchstens 0,1 cm und Winkelabweichung höchstens 0,1°, zusätzlich sichtbare Fuge, Normalen und Kollision prüfen. Das sind Arbeitsgrenzen für neue Lieferungen, kein nachträglicher Qualitätsnachweis des Bestands.

### Modulare Gebäude

Struktur (Boden/Wand/Dach/Abschluss), Dekor und Gebäudezusammenstellung getrennt behandeln. Große funktionsfähige Module bevorzugen; keine eigenen Actors für jeden Ast, Stein oder jede Dachader. Eine Funktionstür bleibt ein gesondertes Gameplay-Element. Grundriss, Wandkrone, Dachunterseite, Aussparungen und Kollisionsende sind gemeinsam zu prüfen.

Kompatibilität verlangt gleiche Kit-/Profilfamilie, Lage und Interface-Version; ähnliche Bounds oder gleicher Stil genügen nicht. Unterschiedliche Radien erhalten eigene Profile. Gerade und gebogene Module brauchen einen ausdrücklichen Übergang. Dekor darf Durchgänge und Kamerafreiraum nicht blockieren. Doppelbelegung an Nähten vermeiden; Stütze, Überfalz oder Zierabschluss gehört einer definierten Seite.

Beim Blatthof ersetzt ein 60°-Eingang genau zwei 30°-Innenwandfelder; kein geschlossenes Wandfeld hinter der Tür. Türblatt 120 × 12 × 220 cm und Rahmenöffnung 144 × 232 cm sind Bestandsmaße, kein allgemeiner Baustandard. Die eingebetteten Bestands-Türkomponenten behalten Einheitsskalierung. Aktuelle Spielerkapsel laut vorhandenen Prüfbelegen: Radius 35, Halbhöhe 90 cm; beim späteren Test erneut auslesen.

Mitteldächer müssen mit identischem Querschnitt wiederholbar sein. Die vom absoluten Hauswinkel abhängige Spitzenanhebung des Originalgenerators darf nicht auf jeden Feldstoß kopiert werden. Dach-/Wandfüllungen und radiale Endabschlüsse müssen die Hülle schließen. Erforderliche offene Flächen ausdrücklich benennen. Ein begehbarer Boden braucht eigene Kollision; den Lab-Boden nicht als verdeckte Voraussetzung übernehmen.

Die bestehenden Anschlussdaten sind Manifest-/Editor-Metadaten, kein implementiertes Socket-/PCG-System. Der Vertrag wird für die Übergabe dokumentiert; hier werden weder Runtime-Katalog noch Gebäudegenerator eingeführt.

### Blender-Quelle und Unreal-Export

Die `.blend` ist die editierbare Quelle. Renderobjekte eindeutig nach Asset benennen; Hilfsgeometrie/Referenzen in getrennten Collections halten und vom Export ausschließen. Externe Texturen relativ zur Quelldatei referenzieren und mitliefern oder bewusst packen; keine ausschließlich absoluten Rechnerpfade. Blender-Version, verwendete Add-ons und notwendige Modifier im Manifest nennen. Vor Export eine reproduzierbare Kopie/evaluierte Exportgeometrie verwenden, damit die bearbeitbare Quelle erhalten bleibt.

**Ziel für neue statische Meshes ist FBX**, zunächst ein Render-Mesh je Datei plus zugehörige Kollisionskörper. Nur ausgewählte Exportobjekte, keine Kamera/Lichter/Animation, kontrollierte Modifier, stabile Triangulierung, korrekte Normalen und UVs. Materialslots inklusive Reihenfolge nicht stillschweigend ändern. Unreal-Materialien werden dort zugeordnet; Blender-Shader nicht als vollständig übertragbar voraussetzen.

Als **ungeprüfter Startkandidat**, nicht als freigegebenes Preset: Blender `global_scale=1`, `apply_unit_scale=True`, `apply_scale_options='FBX_SCALE_UNITS'`, Forward `-Y`, Up `Z`; Unreal Import Uniform Scale 1. Der konkrete Blender-Exporter, Achsenumrechnung und gewählte UE-5.8-Importer müssen zusammen kalibriert werden. Ergebnis muss den obigen Maß-/Achsenvertrag erfüllen. Kein mehrfaches Faktor-100-Korrigieren an Export, Import und Actor. Das später tatsächlich erfolgreiche Profil mit Blender-/UE-Version und Importerbezeichnung im Manifest festhalten.

Vor Serienarbeit einen ausdrücklich beauftragten Kalibrierungsimport durchführen: 100-cm-Referenzlänge plus asymmetrische X-/Y-/Z-Markierung, Ursprung und mindestens zwei passende Modulinstanzen kontrollieren. Maßstab, Orientierung, Pivot, Bounds, Materialslots und Reimport prüfen. **Dieser Test wurde hier nicht ausgeführt; es wurden keine Testmeshes erzeugt.** UE dokumentiert FBX 2020.2 als Pipelinebasis; daraus folgt keine Zusicherung derselben Dateiversion durch Blender.

Einfache Kollision bevorzugen: Boxen bzw. getrennte geschlossene konvexe Körper `UCX_<vollständigerRenderMeshName>_00`, `_01` usw., beispielsweise `UCX_SM_EB_WallInner_R255_A30_H280_00`. Tür-/Fensteröffnungen nicht mit einer Gesamthülle verschließen. Bei mitgelieferter Kollision automatische zusätzliche Erzeugung vermeiden und Zuordnung im Importdialog/Static Mesh Editor prüfen. Bewusste Kollisionsmodi im Manifest nennen; das komplexe Kollisionsmodell der Stilstudie nicht ungeprüft zum Standard machen.

UV0 für Texturen brauchbar anlegen; Überlappungen/Spiegelung nur absichtlich und dokumentiert. Für späteres gebackenes Licht ist ein nicht überlappender Lightmap-Kanal mit geeignetem Padding nötig; aktuell ist statische Beleuchtung deaktiviert. Normalen erhalten, Tangenten nur mit passender UV-/Exportbasis übernehmen oder in Unreal konsistent erzeugen. Importoptionen für Materialien/Texturen, Normals/Tangents, Lightmaps, Kollision und Nanite pro Lieferung festhalten. Beim Reimport vorhandene Referenzen/Slots/Pivots bewahren; Änderung dieser Schnittstellen ist ein eigener Auftrag.

### Qualitäts- und Performance-Abnahme

| Stufe | Erforderlicher Nachweis |
| --- | --- |
| Creator bereit | Quelle öffnet; Maße/Einheiten, Transform, Pivot, Profil und Anschlüsse dokumentiert; Grundformen und Öffnungen erkennbar; keine degenerierten Flächen oder unbeabsichtigten Doppel-/Innenflächen; einfache Kollision vorbereitet; Übergabe vollständig |
| Refiner bereit | Saubere Normalen/Topologie, gezielte Rundungen ohne Anschlussverschiebung; geschlossene Volumen dort, wo vorgesehen; keine sichtbare Naht/Z-Fighting; UV-/Materialslotprüfung; Dekorfreiraum; dokumentierter Vorher-/Nachhervergleich |
| Unreal-Abnahme durch Integration | Kalibrierung bestanden; mindestens zwei Instanzen mit Einheitsskalierung; Anschluss-/Kollisions- und Kapseltest in beide Richtungen, Durchgang und Kamera; Material-Override isoliert; Reimport und erneutes Laden bestehen; tatsächliche Testbelege abgelegt |

Jede Lieferung nennt Dreiecke nach Modifiern/Triangulierung, Vertices, Materialslots, Texturgrößen, Kollisionskörper, LODs und Nanite-Zustand. Refiner vergleicht diese Werte mit dem Creator-Stand; zusätzliche Details müssen aus Spielkamera erkennbaren Nutzen haben. Instanzen gleicher Meshes und bestehende Materialinstanzen verwenden; kein Tick an rein statischer Dekoration. Materialslots und einzelne Komponenten verursachen zusätzliche Renderkosten und sind gemeinsam mit Geometrie zu betrachten.

Vorläufige **Review-Schwellen für neue Prototypmodule**: einfache Wand/Boden höchstens 1.000 Dreiecke, Mitteldach 3.000, zusammenhängende Dekorgruppe 5.000, möglichst 1–2 und höchstens 4 Materialslots. Überschreitung im Bericht begründen und vor Serienproduktion prüfen; keine stillschweigende Produktionsfreigabe. Diese Schwellen ändern bestehende Assets nicht. Das Anschlussmuster hat dokumentiert 2.036 Dreiecke und 28 einfache Kollisionskörper pro Feld; der Rippensatz des Originalhauses ist ein Optimierungskandidat, keine Zielvorgabe für jedes Modul.

LODs oder Nanite je Asset begründet festlegen; beides ersetzt keine Kollisions-/Materialoptimierung. Der vorhandene Anschlussversuch hat laut früherer Messung einen LOD und Nanite aus. Für neue einfache Grundmodelle zunächst ohne Nanite beginnen und einen dokumentierten LOD-Plan liefern; zusätzliche LOD-Geometrie erst im passenden Auftrag. Spätere Szene mit repräsentativer Hauszahl auf Zielhardware profilieren: GPU-/CPU-Framezeit, Draw Calls, Speicher und Kollision, einschließlich Cook/Packaging. Zielhardware, FPS, Kameradistanzen, Szenendichte und finale Textur-/LOD-Budgets sind **offen**; heute keine belastbare Performancefreigabe für eine Siedlung.

### Übergabe Creator → Refiner

1. Auftrag/Modul zuweisen und Schreibbereiche festhalten. Vor Bearbeitung `git status --short` prüfen; vorhandene Änderungen anderer Arbeiten erhalten. Benötigte Referenzen und ihren genauen Stand erfassen.
2. Creator liefert Grundmodell, Export soweit technisch prüfbar, Manifest und `Creator/HANDOFF.md`. Maße, Profil, Pivot, Slots und Anschluss-Transforms als eingefrorenen Vertrag festhalten. Noch nicht geprüfte Exporte ausdrücklich als ungeprüft kennzeichnen.
3. Für getrennte Worktrees einen gezielt geprüften gemeinsamen Basisstand und anschließend die Creator-Übergabe committen bzw. gezielt in den Refiner-Branch übernehmen. Vorher vorhandene Nutzeränderungen nicht pauschal stagen/committen. Ohne Commit im gemeinsamen Checkout ersatzweise explizite Dateiliste plus SHA-256 jeder Eingangsdatei festhalten; dieser Stand ist nicht automatisch in anderen Worktrees verfügbar.
4. Refiner prüft Revision/Hashes und Vertrag und meldet Annahme in `Refiner/REVIEW.md`. Quelle in eigenen Bereich kopieren; ursprüngliche Creator-Dateien bleiben unverändert. Falls eine `.blend` fehlt, die bezeichnete OBJ-/Generatorquelle als **nicht verlustfreie DCC-Übernahme** behandeln: Einheiten, Vertextrennung, Normalen, UVs, Materialgruppen und fehlende semantische Bauteilgruppen prüfen. Nicht automatisch per „lose Teile trennen“ zerlegen.
5. Refiner bearbeitet nur seine Kopie. Anschluss-/Maß-/Slotänderung als Änderungsbedarf zurückmelden; bei einer inkompatiblen Änderung neue Interface-Version und erneute Creator-Abnahme. Creator darf währenddessen andere Module bearbeiten. Änderungen am bereits übergebenen Modul erst nach Abschluss oder ausdrücklicher Neuübergabe.
6. Refiner liefert eigenen Export, Manifest, Vorher-/Nachherwerte, Ansichten und offene Prüfungen. Integration wählt genau einen freigegebenen Quellstand, importiert serialisiert und führt die Unreal-Abnahme durch. Status erst danach `accepted`; bei Problemen `needs_changes` mit konkretem Befund. Kein automatisches Überschreiben des Originalhauses.

Kleine gemeinsame Vorlage für `HANDOFF.md` und `REVIEW.md` (durch die jeweilige Rolle im eigenen Ordner ausfüllen):

```text
AssetName / KitId / ModuleId / InterfaceVersion:
Status: draft | creator_ready | refiner_active | review_ready | needs_changes | accepted
Schreibverantwortlicher und erlaubte Pfade:
Eingangsrevision (Commit + Pfad, alternativ Dateiliste + SHA-256):
Quelle/Generatorrevision und visuelle Referenz:
Blender-Version / Add-ons / editierbare Quelle / Exportpfad:
Einheiten / Bounds cm / Pivot / Achsen / Transform:
Profil / Join_A / Join_B / Öffnungen / Freiräume:
Materialslots in Reihenfolge und Unreal-Materialpfade:
Export- und Importprofil einschließlich Importer/Version:
UV-Kanäle / Normalen / Kollisionsmodus und Körper:
Dreiecke / Vertices / Slots / Texturen / LODs / Nanite, vorher → nachher:
Prüfung: Ergebnis + Beleg + Version; nicht durchgeführt ausdrücklich nennen:
Bekannte Einschränkungen / Änderungsbedarf / nächste Zuständigkeit:
Freigabe durch Integration und gewählter Quellstand:
```

Das Manifest enthält dieselben technischen Werte maschinenlesbar, mit Einheiten pro Koordinatensystem: Blender-Meter und Unreal-Zentimeter nicht vermischen. Es ist eine Lieferbeschreibung, kein neuer Laufzeitkatalog. Tests nie allein aus dem Statusfeld ableiten.

### Startaufträge für die beiden Rollen

**Asset Creator:** „Arbeite als Asset Creator. Lies AGENTS.md und docs/technical/ASSET_PIPELINE.md. Bearbeite ausschließlich das im Auftrag benannte neue Modul mit KitId/ModuleId und den dort erlaubten Pfaden. Erstelle ein einfaches Grundmodell nach dem vereinbarten Maß-/Pivot-/Anschlussvertrag; nutze das vorhandene Elfenhaus nur als visuelle Referenz. Liefere Quelle, prüfbaren Export, Manifest und Creator/HANDOFF.md. Bestehende Assets/Level und gemeinsame Dateien nur bei ausdrücklich benannter Zuständigkeit ändern. Keine offenen Stil-/Lorefragen selbst festlegen.“

**Asset Refiner:** „Arbeite als Asset Refiner. Lies AGENTS.md, docs/technical/ASSET_PIPELINE.md und die benannte Creator-Übergabe. Prüfe Eingangsrevision und Anschlussvertrag. Verbessere eine eigene Kopie unter dem erlaubten Refiner-Pfad in Blender; bewahre Maße, Pivot, Profile und Materialslotvertrag. Liefere Quelle, Export, Manifest und Refiner/REVIEW.md mit Vorher-/Nachherwerten und echten Prüfbelegen. Änderungen an Schnittstellen vorher als Änderungsbedarf melden. Bestehende Unreal-Assets/Level nur im ausdrücklich beauftragten Integrationsschritt ändern.“

Diese Starttexte richten Rollen im Projekt ein; sie starten keine Chats oder autonomen Produktionsaufträge. Konkretes Modul und Schreibbereich werden beim späteren Auftrag ergänzt. Der Einstieg über AGENTS.md folgt der [offiziellen OpenAI-Dokumentation](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex).

### Lokale Blender-Prüfung

**Ergebnis: nicht ausführbar nachgewiesen.** `Get-Command blender` findet keinen Befehl; der tatsächliche Headless-/Python-Aufruf endet vor Programmstart mit `BLENDER_CLI_UNAVAILABLE`, Exitcode 127. Daher weder Blender-Version noch eingebettetes Python oder FBX-Exporter bestätigt. Das vorhandene System-Python 3.12 ersetzt `bpy` nicht.

Gesucht wurde über PATH, die üblichen Blender-Foundation-/lokalen Programme-Verzeichnisse, installierte Programme in den HKLM-/HKCU-Uninstall-Einträgen, laufende Blender-Prozesse, WindowsApps-Blender-Einträge sowie `blender.exe` rekursiv unter `C:\Program Files`, `C:\Program Files (x86)`, `C:\Users\janwi`, `C:\SteamLibrary`, `D:\`, `E:\Programme` und `E:\Business`; kein Treffer. Steam-Bibliothekspfade wurden ebenfalls geprüft. Das beweist nicht die Abwesenheit jeder möglichen portablen Installation, etwa außerhalb der geprüften E:-Verzeichnisse. Es wurde nichts installiert und kein globaler PATH geändert.

Nach Installation oder Angabe eines vorhandenen absoluten Pfads im Projektterminal prüfen:

```powershell
$taskBlender = $env:BLENDER_EXE  # lokal auf einen geprüften absoluten blender.exe-Pfad setzen
if (-not $taskBlender -or -not (Test-Path -LiteralPath $taskBlender -PathType Leaf)) {
    throw 'BLENDER_EXE muss auf die vorhandene blender.exe zeigen.'
}
& $taskBlender --version
& $taskBlender --background --factory-startup --python-exit-code 1 --python-expr "import bpy, sys; print('BLENDER_PYTHON_OK', bpy.app.version_string, sys.version); assert bpy.app.background"
if ($LASTEXITCODE -ne 0) { throw 'Blender-Python-Smoke-Test fehlgeschlagen.' }
# Später ein geprüftes Skript aus dem zugewiesenen Modulordner ausführen:
# & $taskBlender --background --factory-startup --python-exit-code 1 --python '<absoluter Skriptpfad>'
```

Beide Aufrufformen (`--python-expr`, `--python`) werden von der [Blender-Kommandozeile](https://docs.blender.org/manual/en/3.6/advanced/command_line/arguments.html) unterstützt. Der erste Test speichert keine Datei und rendert nichts. Für den Nachweis von `--python` anschließend ein kleines Skript mit demselben Testinhalt ausführen und Exitcode prüfen; Exporter-Verfügbarkeit danach separat kontrollieren. Diese späteren Schritte sind offen, keine bereits bestandenen Tests. FBX-Einstellungen anhand der tatsächlich installierten Version prüfen; [Blender-FBX-API](https://docs.blender.org/api/3.6/bpy.ops.export_scene.html) und [Epic Static-Mesh-Pipeline](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-static-mesh-pipeline-in-unreal-engine) sind Ausgangsreferenzen, kein Beleg eines getesteten lokalen Presets.

### Git und Worktrees: Befund und sicherer Start

- Git 2.54.0.windows.1 und Git LFS 3.7.1 verfügbar; `origin` zeigt auf `https://github.com/JanWUni/fantasy-life-rpg.git`. Lokaler Branch `main`, HEAD `e049c497aefceb37102c1f77fb36becdc4eb5ae6` (`Add Unreal Engine 5.8 prototype project`). Genau ein Worktree vorhanden. Kein Netzwerk-Push-/LFS-Uploadtest erfolgt.
- `.gitattributes` und `.gitignore` sind versioniert; LFS-Filter und Pre-Push-Hook vorhanden. Für `.blend`, `.fbx` und ein vorhandenes Elfenhaus-`.uasset` wurde `filter/diff/merge=lfs`, `-text` über `git check-attr` bestätigt. Keine `lockable`-Attribute konfiguriert; LFS-Speicherung ist keine automatische Schreibsperre oder binäre Merge-Lösung.
- Bei der Abschlussprüfung scheiterten unbeschränkte `git diff --check`/`git diff --stat` am gestarteten LFS-Filterprozess: MSYS `NtCreateDirectoryObject`, Status `0xC0000022` (Zugriff verweigert), danach `remote end hung up unexpectedly`. `git lfs version/env` und Attributabfragen funktionieren. Die gezielte Textprüfung `git diff --check -- AGENTS.md .gitignore` besteht; ein lesender Status war mit nur für diesen Aufruf deaktivierten LFS-Filtern möglich. Keine permanente Filteränderung vorgenommen. Vor Worktree-Checkout, Commit oder Push LFS-Verarbeitung in einem normalen Projektterminal prüfen; Ursache bzw. Beschränkung dieser Ausführungsumgebung ist nicht abschließend geklärt. Kein Remote-Ausfall nachgewiesen.
- **Aktueller Arbeitsstand ist keine vollständige Worktree-Basis:** `Content/Art/`, `Tools/`, `docs/technical/`, die zusätzlichen Lab-/Sandbox-Karten und zahlreiche Prototype-Dateien sind unversioniert; außerdem existieren Änderungen an Konfiguration, C++, Karte und Statusdokumentation. Neue Worktrees aus HEAD enthalten diese Dateien/Änderungen nicht. Keine davon wurde in dieser Einrichtung gestaged oder committed.
- Vor paralleler Produktion gezielt einen gemeinsamen vollständigen Basis-Commit aus den benötigten Projekt-/Quell-/Dokumentationsdateien vorbereiten und prüfen. Keine pauschale Übernahme sämtlicher Nutzeränderungen. Erst danach getrennte Branches und kurze Worktree-Pfade verwenden, z. B. je einen für Creator und Refiner. Derselbe Branch kann nicht regulär in zwei Worktrees ausgecheckt sein. Eine Creator-Übergabe gelangt erst durch gezielte Commit-Übernahme in den Refiner-Stand.
- Keine Junctions/Symlinks auf gemeinsame schreibbare `Content/`, `AssetSources/`, `Saved/`, `Intermediate/` oder `Binaries/` verwenden. Worktrees brauchen ihre eigenen Arbeitsdateien, Builds und Editorzustände. LFS-Arbeitskopien können zusätzlich Plattenplatz belegen; lokale Objektablage/Referenzen nicht mit gemeinsam bearbeitbaren Quellen verwechseln. `core.longpaths=true` ist gesetzt, beseitigt aber nicht jedes Windows-/DCC-Pfadproblem.
- Ignorierte lokale Quellen/Bilder unter `Saved/` und `.codex/config.toml` wandern nicht automatisch mit. Referenzen gezielt bereitstellen, Blender-Pfad je Rechner setzen und UE-/MCP-Verbindung je Worktree prüfen. Ein lokaler MCP-Endpunkt darf nicht versehentlich in das andere Projekt schreiben. Vor jeder Editorintegration tatsächlichen Projektpfad und aktive Karte kontrollieren.
- Binärkonflikte durch Eigentümerschaft vermeiden; nie eine automatische Textzusammenführung von `.blend`, `.fbx`, `.uasset` oder `.umap` erwarten. Bei Kollision einen gewählten Stand übernehmen und andere Änderungen aus der Quelle neu anwenden. Keine gleichzeitigen Reimports derselben Paketpfade oder Saves derselben Karte.

**Erhaltungskontrolle:** Vor den Textänderungen und danach wurden SHA-256-Sammelwerte über Dateipfade und Inhalte erfasst. `Config` (5 Dateien), `Source` (121) und `Tools` (4) sind identisch. `Content` umfasst in beiden Stichproben 886 Dateien, sein Sammelwert hat sich jedoch geändert: parallele Schreibvorgänge an Lab-Karte, Haus-Blueprint und den ersetzten Endkappen sind anhand der Dateiliste und Änderungszeiten erkennbar. Deshalb wird kein unveränderter Gesamtprojektstand behauptet. Dieser Auftrag hat keine Schreiboperation auf Assets, Levels, C++, Generatoren oder Unreal-Konfiguration ausgeführt und keine fremden Änderungen zurückgesetzt. Bearbeitet wurden ausschließlich diese Pipeline-Datei, Root-`AGENTS.md` und `.gitignore`.

**Offene nächste Schritte:** Blender-Pfad/Installation und CLI-/Skriptfähigkeit bestätigen; Kalibrierungsimport freigeben und durchführen; vollständigen gemeinsamen Git-Basisstand herstellen und LFS-Verarbeitung prüfen; konkretes erstes Creator-/Refiner-Modul zuweisen. Zielhardware und Performancebudgets sowie gegebenenfalls gewünschte Stilvarianten bleiben separate Entscheidungen. Hier wurden keine Worktrees, 3D-Assets oder Exportskripte angelegt.

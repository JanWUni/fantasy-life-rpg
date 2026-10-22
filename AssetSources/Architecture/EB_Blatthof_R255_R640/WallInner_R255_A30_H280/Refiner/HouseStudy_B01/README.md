# Geschlossenes Elfenhaus B01 – erste modulare Blender-Studie

Stand: 22. Oktober 2026. **Status: draft, zur visuellen Beurteilung.** Dies ist ein tatsächlich modelliertes Blender-Haus; die PNG-Ansichten sind Renderings dieser Quelle und keine Imagegen-Bilder. Noch keine Produktionsfreigabe oder Unreal-Integration.

## Auftrag und Arbeitsgrenze

Der Nutzer hat die geschlossene holzbetonte Bildstudie B01 als Startpunkt bestätigt und ein etwas größeres Haus gewünscht. Technische Prüfanordnung: **10 × 12 m Außen-Grundfläche**, eingeschossig, 3,20 m Wandhöhe, ein Eingang vorne. Dazu ist eine **10 × 16 m** lange Zusammenstellung aus denselben Bauteilen aufgebaut. Die Größen, Öffnungsprofile und Kit-ID sind vorläufige Arbeitswerte für diese Studie, kein allgemeiner elfischer Baustandard.

Eigene vorläufige Kit-ID: `EH.HouseB.Prototype01`, Interface `draft_1`. Sie ist **nicht** mit dem früheren R255/A30-Bogenkit austauschbar. Kein Verbiegen oder Skalieren des alten Profils. Die alte Wandlieferung und alle Unreal-Bestandsassets bleiben erhalten.

## Öffnen und ansehen

- [Editierbare Blender-Quelle](EH_HouseB01_Study.blend).
- Szene **House_10x12**: erster Hausaufbau. Szene **House_10x16_Variation**: längere Variante. Szene **Module_Library**: einzeln benannte Quellen und ihre UCX-Körper, am eigenen Ursprung überlagert; ein einzelnes Bauteil zur Bearbeitung isolieren.
- Im 3D-Viewport die Materialvorschau aktivieren und das Haus rahmen. Die Präsentationskameras, Lichter und der große Bildhintergrund werden vom Skript nur transient zum Rendern erzeugt und sind kein Teil der Modulexporte.
- [Vorne](Previews/house_front.png), [hinten](Previews/house_rear.png), [längere Variante](Previews/house_long_variant.png).

Die Hülle besitzt umlaufende Wände, Böden, zwei Giebelfüllungen und passende seitliche Dach-Wand-Füllteile. Der Eingang ist ein echtes Loch im Wandfeld; davor sitzt ein getrenntes statisches Türblatt. Rückseite und Seiten haben keinen zweiten Eingang. Fenster sind tatsächlich ausgespart und enthalten separate Geometrieflächen für die geschlossene Verglasung. Das Glasmaterial ist ein opaker Reflexionsplatzhalter, keine fertige transparente Glaslösung.

## Bauteile und Variation

Jeder FBX-Export enthält genau ein Render-Mesh sowie die in der Tabelle genannten zugehörigen UCX-Meshes. [Exports](Exports/) und [Manifest](manifest.json).

| Modul | Render-Dreiecke | UCX-Körper | Slots |
| --- | ---: | ---: | --- |
| `SM_EH_Wall_SolidA_200x24x320` | 528 | 1 | Plaster, Timber, Stone |
| `SM_EH_Wall_SolidB_200x24x320` | 560 | 1 | Plaster, Timber, Stone |
| `SM_EH_Wall_Window_200x24x320` | 1272 | 1 | Plaster, Timber, Stone, Glass |
| `SM_EH_Wall_Entry_200x24x320` | 904 | 6 | Plaster, Timber, Stone |
| `SM_EH_Roof_Mid_W1000` | 1080 | 16 | Jade, Timber |
| `SM_EH_Roof_End_W1000` | 2400 | 16 | Jade, Timber |
| `SM_EH_Gable_W1000` | 1328 | 0 | Plaster, Timber |
| `SM_EH_EaveFill_Mid_200` | 44 | 0 | Plaster, Timber |
| `SM_EH_EaveFill_EndA_200` | 188 | 0 | Plaster, Timber |
| `SM_EH_EaveFill_EndB_200` | 188 | 0 | Plaster, Timber |
| `SM_EH_Floor_200x200x20` | 44 | 1 | Stone |
| `SM_EH_DoorLeaf_132_Study` | 332 | 0 | Timber, Bronze |
| `SM_EH_EntryCanopy_224` | 1044 | 0 | Jade, Timber |

Die beiden Wandvarianten behalten dieselbe Struktur und unterscheiden sich in kleinen Holzdetails. Fenster-/Eingangsfelder belegen dieselben 2-m-Felder. Dachmittelteile sind wiederholbar; Dachenden besitzen angehobene Abschlüsse. Die drei seitlichen Dachfüllungen schließen Mittelfeld sowie beide Längsenden ab. Der zweite Hausaufbau verwendet dieselben Mesh-Datenblöcke ohne negative oder nichtuniforme Skalierung. Damit ist eine Längenvariation tatsächlich aufgebaut. Andere Hausbreiten, Geschosse, umfangreichere Silhouetten- oder Dachvarianten sind noch nicht hergestellt.

Die Fensterwand liegt mit 1.272 Dreiecken über der 1.000-Dreiecke-Reviewschwelle für einfache Wände: darin sind Bogenrahmen, Maßwerk, Glas und Sockel enthalten. Das ist eine zu prüfende Prototypausnahme, keine Freigabe zur Serienproduktion. Dachmodule bleiben unter 3.000 Dreiecken. Finale LOD-/Nanite- und Szenenbudgets sind offen.

## Vorläufige technische Konvention

- Blender Metric, Unit Scale 1, Koordinaten in Metern. Exportabbildung **UE_cm=(100*B.x,-100*B.y,100*B.z)**. Deshalb zeigt die Hausfront in Blender nach −Y und in Unreal nach +Y.
- Gerade Wandfelder: lokale Breite X0…2 m, tragende Hülle Y0…0,24 m nach innen, Z0…3,20 m. Unterer A-Startpivot `(0,0,0)`. Anschluss B bei `(2,0,0)`; bei einer geraden Fortsetzung fällt der A-Pivot der nächsten Instanz dort zusammen. Kleine Holzdetails stehen vor die strukturelle Hülle; Struktur- und Dekorgrenzen sind deshalb zu unterscheiden. Der Hauptpfosten gehört zur A-Seite, Holzverbindungen dürfen sich konstruktiv überdecken.
- Alle Module werden bei lokalen Identitätstransformationen exportiert. Hausinstanzen verwenden nur Translation und 0/90/180/270° Drehung bei Skalierung Eins. Ecken entstehen vorläufig aus rechtwinklig aufgestellten Wandlagen; es gibt noch kein eigenständiges finales Eckmodul.
- Dächer: feste vorläufige Wandspannweite 10 m, seitlich etwa 65 cm Überstand. Mittelfeld 2 m Länge, Endstück 2,8 m einschließlich Überstand. Keine freie Breitenskalierung vorgesehen. Geometrische Naht- und Dachfüllprüfung bestanden; finale Normalen-/Materialwirkung im Unreal-Reimport ist offen.
- Eingang: nominell 136 cm Breite, seitliche Bogenansätze bei 222 cm, Bogenspitze etwa 285 cm. Statisches Türblatt separat mit Gelenkbezug. Das ist **keine** neue Implementierung der vorhandenen Gameplay-Tür und kein beschlossener universeller Türstandard.

## Materiallieferung

Vier Materialgruppen **Plaster, Timber, Stone, Jade** liefern je drei tatsächliche 1024²-PNG-Dateien: BaseColor, Tangent-Normal und Roughness. Zusammen **12 Texturen**, relativ unter [Textures](Textures/), ohne externe Bibliotheken oder Rechnerpfade. Materialshader und Texturen wurden prozedural im eigenen Blender-Skript erzeugt; kein Imagegen-Ersatzbild und kein bloßes Debug-Farbschema. Bronze und die opake Glasfläche verwenden einfache eigene Vorschauparameter.

UV0 verwendet absichtliche Wiederholung/Kachelung; überlappungsfreie eindeutige Lightmap-UVs wurden nicht geliefert. Diese PBR-Materialien ersetzen keine bestehenden Unreal-Materialien. Blender-Normaltexturen verwenden die OpenGL/+Y-Konvention; Grünkanal-/Tangentenkonvention und Materialzuordnung müssen bei späterer Unreal-Integration gesondert geprüft werden. Ein FBX allein überträgt die Blender-Nodes nicht vollständig.

## Tatsächlich geprüft

Blender 5.2.2 LTS, Quelle in neuem Prozess erneut geöffnet, alle **13 FBX-Dateien** jeweils in eine leere Blender-Szene importiert. Geschlossene orientierte Komponenten, positive Volumina, endliche Koordinaten/UVs, keine degenerierten Render-/UV-Dreiecke, erwartete Dreiecke/Slots/Körperzahlen, korrekte lokale Transformationen und verfügbare relative Texturen geprüft. Die Bauteile bestehen aus mehreren geschlossenen Bauteilvolumen; Holz-/Sockelverbindungen sind nicht zu einer einzigen Booleschen Hülle verschmolzen.

- Größte Bounds-Abweichung im FBX-Rückimport: 0.0000000000 m.
- Größter Positionsversatz der eigentlichen Dachschale an den geprüften Modulnähten beider Hauslängen: 0.0000019983 m.
- Größte Abweichung der Giebel-/Seitenfüllpunkte von der tatsächlich abgetasteten Dachunterseite: 0.0000002995 m.
- Beide Aufbauten: je ein Eingang, gemeinsame Modul-Meshdaten, Einheitsskalierung; `verification.json` enthält tatsächliche Werte.
- Erhaltung: 1095 von 1098 vorab erfassten Dateien bytegleich; geändert wurden nur die drei passenden Designdokumente zur Nutzerauswahl. Die vorherige Refiner-Lieferung besteht weiter mit allen 31 unveränderten Prüfsummen.

Prüfbelege: [verification.json](verification.json), `Evidence/verify.log`, `Evidence/render.log`, [Erhaltung](Evidence/preservation.json). Die erfolgreiche Prüfung wird von korrigierten Entwicklungsversuchen getrennt: Rundungsfehler am Türbogen, nicht ausgewertete Matrizen der inaktiven Vergleichsszene, eine beinahe doppelte Sampling-Endposition und ein abgewiesenes Ersetzen der eigenen Zwischenquelle. Frühere Logs bleiben als Belege erhalten. Die eigene Zwischenquelle wurde lokal als ignorierte `.blend1`-Sicherung bewahrt. Keine Warnungen unterdrückt; Blender meldet DeprecationWarnings zu Material-/World-Node-Eigenschaften.

## Grenzen und nächster Schritt

Noch **kein gebrauchsfertiges Gameplay-Haus**: Türinteraktion und vollständige geprüfte Kollision fehlen. Giebel, obere Seitenfüllungen, Türblatt und Eingangsvordach besitzen noch keine eigene freigegebene Kollision. Geschlossene Fenster verwenden bewusst einen einfachen vollen Blockkörper. Die vereinfachten oberen Eingangshüllen vereinfachen den Bogen; der freie Mindestquerschnitt muss mit der tatsächlichen Kapsel geprüft werden. Dachkollision ist eine konservative konvexe Annäherung mit 16 Streifen je Teil und ersetzt keinen Kapsel-/Kameratest. Das begehbare Hauptgeschoss liegt unter den Dachfüllungen; Dachbegehung ist nicht geprüft.

Offen: Beurteilung der tatsächlichen Hausproportionen durch den Nutzer, weitere Detail-/Materialqualität, finales Eck-/Anschlusskonzept, genaue Kollisionsabnahme, funktionierende Gameplay-Tür, Unreal-Import/Reimport/Normalen/UVs/Materialien, PIE/Kamera, Performance, LODs/Nanite, Packaging und Multiplayer. Der spätere Importweg bleibt der kalibrierte **Legacy FbxFactory/FbxStaticMeshImportData-Pfad mit FBX_SCALE_NONE**; Interchange ist nicht validiert.

Nächster sinnvoller Schritt: das hier sichtbare echte Modell beurteilen und die konkreten Korrekturen festlegen, danach den kleinsten kompletten Hausstand gezielt in Unreal integrieren. Bestehende Karten, Content, Materialien, Blueprints, gemeinsame Generatoren und Projektkonfiguration wurden nicht geändert. Keine Commits, Pushes oder neuen Worktrees.

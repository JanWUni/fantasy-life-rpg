# Refiner-Übergabe B – Baumkörper und Wurzelhof

Status **review_ready**, nicht accepted. Kit `ER.RootRetreat`, Modul `CourtyardStudy01`, Creator-Revision **2**, Interface **0.2** unverändert; eigene Refiner-Revision 2.

Eingangscommit **`7cf7bf322725559b4b3f5ccd220eb0544c589195`**, gezielte Übernahme nach vollständigem Abschluss von A: **`95020dd1693250747aee24a05c6ff7cd944dc6dc`**. Eingangsquelle SHA-256 **`e90d818ff70e2ac521541c71662e9da561719ad3ccab65527155276628cb8fad`**. 41 Lieferhashes und 34 vollständige LFS-Objekte gegen den Commit geprüft. Die abgeschlossene A-Lieferung ist einschließlich aller 43 versiegelten Dateien und ihrer Prüfsummenliste unverändert.

## Erhaltene Zusammenstellung

Die eigene editierbare [CourtyardStudy01_Refined.blend](CourtyardStudy01_Refined.blend) begann als byteidentische Eingangskopie. Älterer Baumkörper, zwei Wohnflügel, sämtliche **319 Instanztransforms**, Pivots, lokale Maße und Slots sind erhalten. Keine neue Lore-, Kultur-, Architektur- oder Nutzungsfestlegung. Die Bildreferenz ist visuelle Richtung, kein maßhaltiger Bauplan.

- **Genau ein äußerer Haupteingang** am zentralen Baumkörper; genau ein äußeres Türblatt in der Szene.
- Kleine Fenster an beiden Wohnflügeln, geschlossene Brüstungen an den ehemaligen Außentürstellen.
- **Zwei offene Innenverbindungen** durch die jeweils zwei beteiligten Wandlagen.
- **Ein zusammenhängender Renderboden auf Z0**, drei unveränderte einfache Boden-UCX mit absichtlicher Überdeckung am gleichen Niveau.
- Flügelzentren weiterhin `(-5.5,3.70,0)` / `(5.5,3.70,0)` m, Drehungen −12° / +12°; zentraler Ursprung `(0,3,0)` m.

## Technische Verfeinerung

Topologie, geschlossene Komponenten, positive Volumen und Normalen geprüft. Koplanare Bereinigung reduziert den gemeinsamen Renderboden **204 → 164 Dreiecke**, ohne seinen zusammenhängenden Aufbau oder das Z0-Niveau zu ändern. Strukturöffnungen und Kollisionsgeometrie bleiben erhalten. Normale fester Teile sind gewichtet gebacken; organische Rinden-/Wurzelkörper verwenden gleichmäßige Glättung mit harten Kappen und Kanten ab 45°. Laub/Kräuter bleiben weich geglättet, ohne störende Flächengewichtung.

Vier kleine zweistufige Rundungen: Türblatt 3 mm, vorhandener Wurzel-Türbogen 2 mm, Fensterladen 3 mm und Bank 4 mm. Zwei andere Versuche wurden durch die Vertrags-/Topologieprüfung zurückgenommen. Keine zusätzlichen Ornamente. Struktur-Bounds bleiben innerhalb 0,000001 m zum Eingang; die ausdrücklich beauftragte Innenkorrektur zweier Dekorgruppen ist unten getrennt ausgewiesen.

### Innenkorrektur in Refiner-Revision 2

Die in Revision 1 sichtbaren abgeschnittenen Enden von `OldButtressRoots` und `LinkingRootArches` im zentralen Raum wurden geometrisch entfernt. Jeder vorhandene geschlossene Wurzelkörper wurde einzeln gegen eine 40-seitige Freihaltezone geschnitten: Radius 2,24 m, Z −0,10 bis 4,30 m, konzentrisch zur bestehenden Innenwand mit Radius 2,20 m. Die neuen Abschlussflächen liegen innerhalb der bestehenden Wandstärke. Keine zusätzliche Blende und keine versteckte Render-Ersatzgeometrie.

Alle unveränderten Instanzmatrizen, Pivots, Strukturteile, Slots und 158 UCX bleiben exakt erhalten. Die entfernte Spitze von `LinkingRootArches` verkleinert ausschließlich dessen dekorative lokale Bounds: **Z-Min +0,0199177265 m**, **Y-Max −0,0365405083 m**. Das ist keine Änderung eines Anschlusses oder der äußeren Haussilhouette. Andere Bounds dieser Gruppe sowie sämtliche Bounds von `OldButtressRoots` bleiben erhalten. [Prüfbeleg](Evidence/interior_root_cleanup.json) dokumentiert Vorher/Nachher, positive geschlossene Volumen, nicht entartete UVs und echte Oberflächenproben außerhalb Radius 2,60 m. Die beiden betroffenen FBXs wurden aus der gespeicherten Quelle erneuert. Strukturöffnungen werden nicht mit einem Dekorteil geschlossen.

UV0 ist nicht entartet. Innen-/Außenwand des runden Baumkörpers erhalten eine metrische zylindrische Abwicklung mit je einer periodischen Naht; Kappen und radiale Laibungen bleiben planar. Die übrigen Teile nutzen konsistente metrische Projektionen mit dem bestehenden 2-m-Kachelmaß. Absichtliche Kachelüberschneidungen sind dokumentiert; kein Produktionsatlas oder finaler Lightmap-Kanal.

**Einzigartige Render-Dreiecke: 7348 → 8012**. Einfache UCX-Körper: **158 → 158**, Geometriefingerprints exakt erhalten. Bibliothekswerte, keine Siedlungs-/Draw-Call-/Laufzeitmessung.

| Asset | Dreiecke vorher → nachher | UCX | Rundung |
| --- | ---: | ---: | ---: |
| `SM_ER_WingWindowFacade_640x280_v02` | 200 → 200 | 29 | – |
| `SM_ER_WingRear_640x280` | 100 → 100 | 13 | – |
| `SM_ER_WingSide_550x311` | 100 → 100 | 13 | – |
| `SM_ER_WingInternalLink_550x311_v02` | 44 → 44 | 5 | – |
| `SM_ER_WingRootVault_720x620` | 100 → 100 | 12 | – |
| `SM_ER_WingCrownFill` | 100 → 100 | 12 | – |
| `SM_ER_DoorLeaf_140x230` | 12 → 60 | 1 | 3.0 mm |
| `SM_ER_RootDoorArch` | 296 → 376 | 0 | 2.0 mm |
| `SM_ER_RetreatWindowFrame_65x80` | 124 → 124 | 0 | – |
| `SM_ER_RetreatWindowGlass_65x80` | 12 → 12 | 0 | – |
| `SM_ER_RetreatShutter_32x84` | 12 → 60 | 0 | 3.0 mm |
| `SM_ER_WingRootRibs` | 900 → 900 | 0 | – |
| `SM_ER_WingClosedStoneSill_v02` | 12 → 12 | 0 | – |
| `SM_ER_OldCoreLinkedShell_R260_H430_v02` | 444 → 444 | 68 | – |
| `SM_ER_OldCoreCrown_640x620` | 336 → 336 | 1 | – |
| `SM_ER_LivingOldTrunk` | 332 → 332 | 0 | – |
| `SM_ER_OldButtressRoots` | 576 → 904 | 0 | – |
| `SM_ER_OldTreeCanopy` | 2080 → 2080 | 0 | – |
| `SM_ER_YoungLivingTrunk` | 144 → 144 | 0 | – |
| `SM_ER_YoungTreeCrown` | 400 → 400 | 0 | – |
| `SM_ER_LinkingRootArches` | 152 → 208 | 0 | – |
| `SM_ER_Ground_2600x2300` | 12 → 12 | 1 | – |
| `SM_ER_CourtStone_100x70` | 12 → 12 | 0 | – |
| `SM_ER_Bench_210x56` | 36 → 180 | 0 | 4.0 mm |
| `SM_ER_HerbBed_250x140` | 32 → 32 | 0 | – |
| `SM_ER_HerbClusters` | 576 → 576 | 0 | – |
| `SM_ER_ConnectedFloor_v02` | 204 → 164 | 3 | – |

## Tatsächliche Prüfbelege

- [Eingangsprüfung](Evidence/intake_verification.json): SHA256SUMS, LFS-OIDs/Dateigrößen und Creator-Bytes gegen Eingangscommit.
- [Vorher/Nachher](Evidence/refinement.json): Maße, UVs, geschlossene Komponenten und Volumen; exakte Instanzmatrizen und UCX-Fingerprints erhalten.
- [Quell-/FBX-Prüfung](verification.json) und [unabhängige Messung](Evidence/independent_verification.json): eigene gespeicherte Quelle in frischem Prozess erneut geöffnet; alle **27 FBX** zurückimportiert, Einheiten, Bounds, Identitätstransforms/Pivots, Slotfolge, UVs, endliche Einheitsnormalen und konvexe UCX geprüft. Alle Prüfungen bestanden.
- [Erneute Prüfung von A](Evidence/study_a_revalidation.json): versiegelte A-Quelle erneut geöffnet, alle 21 FBX samt UCX rückimportiert; keine A-Datei verändert. Quelle, Pivots, Instanzen, Slots, Topologie, Normalen, UVs, Bounds und konvexe Kollision bestanden.
- Der ursprüngliche Prüfer bestätigt genau ein äußeres Türblatt, eine verbundene Bodenkomponente, neun freie Render-/UCX-Strahlen je Zugang, 96 Bodenproben je Innenweg und Darstellung sowie geschlossene ehemalige Außentüren. Zusätzlich **1288 radiale Renderstrahlen** auf 1,0/2,2 m Höhe schließen unbeabsichtigte zentrale Außenöffnungen außerhalb des Haupteingangs aus.
- [Dichtere Innenweg-/Fenster-/Bodenprüfung](Evidence/openings_and_floor.json): je Verbindung **144 freie Strahlen pro Darstellung** im 1,2 m breiten Prüfbereich bis 2,2 m Höhe durch reale Rendergeometrie einschließlich Dekor und durch UCX; **704 Bodenproben pro Verbindung und Darstellung** entlang/beiderseits des Übergangs. Maximale Z0-Abweichung etwa **0,000000060 m**. Sieben kleine Öffnungen an den drei eindeutigen Flügelwandtypen geprüft; Brüstungen und Stürze geschlossen.
- [Erhaltung](Evidence/preservation_after.json): **1530 bereits vorhandene Dateien byteidentisch**, einschließlich vollständiger Studie A, altem Musterhaus, Content, Konfiguration und gemeinsamen Tools. Creator B ebenfalls unverändert.

Dies sind reale DCC- und stichprobenartige Geometrieprüfungen, **keine kontinuierliche Spielerkapsel- oder Unreal-Abnahme**. Die nominellen Öffnungsmaße sind keine Aussage über jede Kamera-/Kapseltrajektorie.

## Echte Ansichten

[Außenübersicht](Previews/01_eye_overview.png) · [Flügelansicht](Previews/02_house.png) · [Aufsicht](Previews/03_plan.png) · [Innenverbindung](Previews/04_interior.png) · **[Schnittaufsicht](Previews/05_connected_plan.png)**.

Echte Cycles-Render, 24 Samples, AgX, dieselbe neutrale Tagesbeleuchtung wie im Eingang. Innen nutzt eine temporäre neutrale Prüfaufhellung; das ist kein geplantes Gebäudelicht. Die Schnittaufsicht blendet Dach-/Baum-/Dekormassen aus und schneidet die tatsächlichen Wände temporär bei Z1,80 m. Diese Prüfdarstellung wird **nicht in der Quelle gespeichert**; das editierbare Modell bleibt vollständig. Keine AI-Abbildung oder abweichende Render-only-Architektur.

## Übergabe und Grenzen

27 eigene FBX unter [Exports/](Exports/). Kalibriertes Profil unverändert: **FBX_SCALE_NONE**, global_scale 1, Metric Unit Scale 1, Forward -Y / Up Z, `UE_cm=(100*B.x,-100*B.y,100*B.z)`. Keine zusätzliche Spiegelung oder negative Objektskalierung. Materialslots bleiben in identischer Reihenfolge. Blender 5.2.2 LTS.

Die Blender-Prüfmaterialien und ihr prozedurales Bump sind keine fertigen Unreal-Materialien. Kleine Glasflächen, Vegetation, überlappende Dekorkomponenten, fehlende Dekorkollision, finale Texturen/Lightmaps und LODs bleiben Prototypgrenzen. Die 158 kleinen Strukturhüllen wurden bewusst nicht eigenständig umgebaut; Optimierung und vollständige Kapsel-/Kameraprüfung sind spätere Aufgaben.

Die bisher deutlich in den zentralen Raum ragenden Endkappen der beiden Wurzelgruppen sind in der neuen Innenansicht entfernt. Die einfache strukturelle Wand-/Bogenverbindung und die übrigen überlappenden Studiengruppen bleiben gestalterisch vorläufig; keine fertige Innenausstattung oder ausmodellierte Produktionsarchitektur behauptet.

**Nicht durchgeführt:** Unreal-Import/Reimport, Interchange, Karten-/Blueprint-/Materialänderungen, PIE, Packaging/Cooking, Multiplayer, Siedlungsperformance und finale Art-/Produktionsabnahme. Keine Schnittstellenänderung erforderlich. Der anschließende Nutzerauftrag erlaubt einen gezielten Commit beider geprüfter Refiner-Lieferungen; fremde Änderungen und Unreal-Dateien sind davon ausgeschlossen. Kein Push beauftragt.

Reproduktion: `refine_study.py -- --mode prepare` (bei existierender, hashgeprüfter Lieferung nur nach ausdrücklichem Auftrag mit `--revise`), danach `resolve_interior_roots.py`, `refine_study.py -- --mode verify`, `check_clearances.py` und `refine_study.py -- --mode render` in frischem Blender. `reexport_roots.py` erneuert bei Bedarf ausschließlich die beiden Dekorexporte aus der gespeicherten Quelle. Fehlgeschlagene explorative Schnitte, UV-Projektionen und eine leere FBX-Auswahl wurden korrigiert; maßgeblich sind die anschließend vollständig bestandenen Prüfungen. Der Creator-Prüfer wird nur gelesen und auf diesen eigenen Refiner-Pfad gebunden. [Manifest](manifest.json) und [SHA256SUMS](SHA256SUMS) enthalten Herkunft, Werte und Dateihashes.

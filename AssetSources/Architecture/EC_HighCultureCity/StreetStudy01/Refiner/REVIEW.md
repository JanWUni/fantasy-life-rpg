# Refiner-Übergabe A – Hochkultur-Wohnstraße

Status **review_ready**, nicht accepted. Kit `EC.HighCultureCity`, Modul `StreetStudy01`, Creator-Revision 1, Interface **0.1** unverändert. Refiner-Revision 1.

Eingangscommit **`08e7d7eea4a161a5e5025d656ca5b199ed0130da`**, gezielte Übernahme auf `assets/refiner`: **`fe7b9a5239015dd1091dc20ebb0ca32cc420f62c`**. Eingangsquelle SHA-256 **`6f147895db5668b77083984a5553af15cfe4f3d338a1bbc60a86a81e076b7b25`**. Alle 34 Creator-Lieferhashes und 27 LFS-Objekte sind gegen den Commit geprüft; Creator-Dateien bleiben eingefroren. Das frühere Warten auf Sichtauswahl wird durch den ausdrücklichen aktuellen Refiner-Auftrag ersetzt.

## Bearbeitung

Die editierbare [StreetStudy01_Refined.blend](StreetStudy01_Refined.blend) begann als byteidentische eigene Kopie. Straßenanordnung, drei Haussilhouetten, kleine Fenster, Proportionen, Stein-/Holzmaterialien, Pivots und sämtliche **471 Instanztransforms** sind erhalten. Keine neue Architektur-, Kultur- oder Lore-Festlegung.

Vorhandene Topologie wurde auf Doppel-/Innenflächen, geschlossene Komponenten und entartete Flächen geprüft. Der konservative Versuch, koplanare Kanten unter Erhalt der UV-Grenzen aufzulösen, führte an den Strukturteilen zu keiner Reduktion; es wird keine Laufzeitoptimierung behauptet. Normalen fester Teile sind neu berechnet und als gewichtete Split-Normalen gebacken. Vorhandene Bögen und Baumkörper sind geglättet, während Kappen und scharfe Übergänge ab 45° getrennt bleiben. Laub behält gleichmäßige, ungewichtete Glättung, nachdem die Sichtprüfung dort Bänder durch gewichtete Normalen zeigte. Dachflächen bleiben plan statt pauschal weichgezeichnet.

Kleine zweistufige Rundungen an 4 Teilen betragen 3–4 mm. An 3 weiteren Teilen wurden Rundungen verworfen, sobald sie die exakten Bounds verändert hätten. Keine Änderung der Strukturöffnungen oder der UCX-Geometrie. UV0 verwendet eine konsistente Dominantachsenprojektion mit dem vorhandenen 2-m-Kachelmaß; absichtliche Überlappungen bleiben erhalten. Keine entarteten UV-Dreiecke, kein Produktionsatlas oder finaler Lightmap-Kanal.

**Einzigartige Render-Dreiecke: 3034 → 3274**; einfache Kollisionskörper **57 → 57**. Dies sind Bibliothekswerte, keine Instanz-/Draw-Call-/Performancewerte.

| Asset | Dreiecke vorher → nachher | UCX | Rundung |
| --- | ---: | ---: | ---: |
| `SM_EC_Facade_700x390` | 164 → 164 | 23 | – |
| `SM_EC_SideWall_800x390` | 100 → 100 | 13 | – |
| `SM_EC_RearWall_700x390` | 100 → 100 | 13 | – |
| `SM_EC_Floor_700x800` | 12 → 12 | 1 | – |
| `SM_EC_HipRoof_790x890` | 12 → 12 | 1 | – |
| `SM_EC_HipRoof_LowVariant_790x890` | 12 → 12 | 1 | – |
| `SM_EC_PorchPosts_220x270` | 24 → 120 | 2 | 4.0 mm |
| `SM_EC_PorchRoof_240x150` | 12 → 12 | 1 | – |
| `SM_EC_StoneDressings` | 344 → 344 | 0 | – |
| `SM_EC_EntryWoodArch` | 236 → 236 | 0 | – |
| `SM_EC_TreeRelief` | 268 → 268 | 0 | – |
| `SM_EC_DoorLeaf_140x235` | 12 → 60 | 1 | 3.0 mm |
| `SM_EC_CityWindowFrame_65x80` | 124 → 124 | 0 | – |
| `SM_EC_CityWindowGlass_65x80` | 12 → 12 | 0 | – |
| `SM_EC_CityShutter_32x84` | 12 → 60 | 0 | 3.0 mm |
| `SM_EC_Paving_120x80` | 12 → 12 | 0 | – |
| `SM_EC_GroundBase_3200x3000` | 12 → 12 | 1 | – |
| `SM_EC_Curb_100x20` | 12 → 12 | 0 | – |
| `SM_EC_PlanterRim` | 12 → 60 | 0 | 4.0 mm |
| `SM_EC_StreetTreeTrunk` | 342 → 342 | 0 | – |
| `SM_EC_StreetTreeCrown` | 1200 → 1200 | 0 | – |

## Tatsächliche Prüfungen

- [Eingang](Evidence/intake_verification.json): SHA256SUMS, vollständige LFS-OIDs/Größen und Creator-Textdateien gegen Eingangscommit.
- [Vorher/Nachher](Evidence/refinement.json): je Mesh Maße, Topologie, UVs, Volumen, Normalen und verworfene Rundungen. Boundsabweichung kleiner 0,000001 m; Materialslotnamen und Reihenfolge erhalten. Alle 57 UCX-Geometriefingerprints sowie Instanzmatrizen exakt erhalten.
- [Quell-/FBX-Prüfung](verification.json) und [zusätzliche unabhängige Messung](Evidence/independent_verification.json): gespeicherte Quelle in frischem Blender-Prozess erneut geöffnet, alle 21 FBX zurückimportiert. Einheiten, Bounds, Pivot/Identitätstransforms, Slotfolge, geschlossene positive Volumen, UVs und konvexe UCX geprüft. Alle Prüfungen bestanden.
- Eingänge: ursprüngliche neun Render-/UCX-Strahlen je Haus im zentralen **1,2 × 2,2-m-Prüfbereich** frei; mehrere Boden- und Dachproben getroffen. Dies ist kein kontinuierlicher Kapselnachweis.
- [Zusätzliche Fenster-/Bodenprüfung](Evidence/openings_and_floor.json): je zwei kleine Öffnungen in Fassade, Rück- und Seitenwand, zusammen 294 freie Strahlen je Darstellung; geschlossene Brüstungs-/Sturzproben. Fünf Innenbodenproben je Haus treffen in Render und UCX **Z0**.
- [Erhaltung](Evidence/preservation_after.json): **1451 vorher vorhandene Dateien byteidentisch**, einschließlich Content, Konfiguration, gemeinsamer Tools und der uncommittierten früheren Refiner-Arbeit. Keine Unreal-Operation ausgeführt.

## Echte Blender-Ansichten

[Straßenansicht](Previews/01_eye_overview.png) · [Hausansicht](Previews/02_house.png) · [Aufsicht](Previews/03_plan.png) · [Innen](Previews/04_interior.png).

Cycles, AgX, 24 Samples und unveränderte gemeinsame Tagesbeleuchtung. Die Innenansicht verwendet wie die Creator-Prüfdarstellung eine temporäre neutrale Aufhellfläche; diese ist kein geplantes Gebäudelicht und wird nicht in der Quelle gespeichert. Keine AI-Bilder oder Render-only-Architektur.

## Export und offene Punkte

21 eigene FBX unter [Exports/](Exports/); exakt ein Render-Mesh und die bezeichneten UCX je Datei. Kalibriertes Profil unverändert: **FBX_SCALE_NONE**, global_scale 1, Metric Unit Scale 1, Forward -Y / Up Z; `UE_cm=(100*B.x,-100*B.y,100*B.z)`. Keine zusätzliche Spiegelung, keine negative Skalierung. Geprüft in Blender 5.2.2 LTS.

Materialgraphen und prozedurales Bump bleiben Blender-Prüfmaterialien; ein vollständiger Shadertransfer nach Unreal wird nicht behauptet. Glas, Vegetation, UV-Atlas/Lightmaps und LODs bleiben Prototypgrenzen. Dekor/Natur ohne UCX erhalten weiterhin keine eigene Kollision. Viele kleine Strukturhüllen sind unverändert und vor Produktion gesondert zu optimieren.

**Nicht durchgeführt:** Unreal-Import/Reimport, Interchange, PIE, physische Spieler-/Kamera-/Kapselbegehung, Packaging/Cooking, Multiplayer, Siedlungsperformance und finale Art-Abnahme. Noch keine Freigabe zur Integration. Keine Schnittstellenänderung erforderlich; kein neuer Refiner-Commit und kein Push. Einziger Git-Schreibvorgang war die ausdrücklich erlaubte Eingangsübernahme.

Reproduktion: `refine_study.py -- --mode verify` beziehungsweise `--mode render` in einem neuen Blender-Prozess; der eingefrorene Creator-Prüfer wird ausschließlich lesend geladen und auf den Refiner-Pfad gebunden. Der Erzeugungsmodus überschreibt keine unbekannte Refiner-Arbeit. [SHA256SUMS](SHA256SUMS) deckt alle Lieferdateien außer sich selbst ab.

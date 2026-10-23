# Musterhaus B03 – Außenmaterialien, Innenräume und Asset-Ausstellung

Stand: 23. Oktober 2026. Arbeitsstand zur Sichtprüfung; keine finale Art- oder Produktionsabnahme.

## Auftrag und Bestand

Der Nutzer hat die Ausarbeitung eines Musterhauses im **Refiner-Lab** einschließlich Creator- und Integrationsaufgaben beauftragt. Verwendet wird das kleinere Haus **10 × 12 m**. Das lange Vergleichshaus, die Creator-Lieferung, die ursprünglichen B01/B02-Quellen und vorhandene gemeinsame Unreal-Assets bleiben erhalten. Ausgangs-HEAD ist `21a7ef17dd5cfd6f058b4c0f7440d2727b98c18d`; die bereits uncommittierte B02-Fensterintegration ist Teil der Eingangsgrundlage. Ihre Dateien werden nicht als neue B03-Arbeit ausgegeben.

Die visuelle Grundlage bleibt ART-ELF-01 und `docs/ART_DIRECTION_REFERENCES.md`: warmes Holz, helle Wände, geschwungene Fantasy-Dachform und eine realistischere, immersive Materialwirkung. Diese einzelne Einrichtung legt weder elfische Haushalte noch Brennstoffe, gesellschaftliche Zuordnung oder allgemeine Produktionsmaße fest.

## Ergebnis im Lab

- Karte: `/Game/Prototype/Maps/Lvl_AssetLab`.
- Musterhaus unverändert am Ursprung **(-2400,-1900,31) cm**; Eingang vor **(-1900,-1900)**.
- Außenhülle weiterhin `Lab/Architecture/ElvenHouseB02/House_10x12`; ausschließlich Material-Overrides an ihren Komponenten.
- Neue Innenbauteile und Einrichtung: `Lab/Architecture/ElvenHouseB03/House`.
- Einzelne Bauteile links/westlich daneben: `Lab/Architecture/ElvenHouseB03/Catalogue`. **34 unterschiedliche Render-Meshes**, beschriftet und bei Einheitsskalierung, umfassen bestehende Hüllenteile und alle 19 neuen Assets. Die dünnen Ausstellungspodeste sind nicht blockierende Lab-Hilfen.
- Das Haus 10 × 16 m dient weiterhin als unveränderter Vergleich.

## Materialien

Neue wiederverwendbare Materialfamilien liegen unter `/Game/Art/Materials/ElvenHouseB03`, ihre 29 eigenen 1024²-Quelltexturen unter `Textures/` und `/Game/Art/Textures/ElvenHouseB03`. Base Color, Roughness und höhenabgeleitete Tangent-Normalen unterscheiden Holz, Putz, Stein, Dach und Textilien. Holz hat gerichtete Maserung, der Boden Bretterfugen; Dachflächen zeigen versetzte kleine Reihen. Matte Putzflächen und zurückhaltende Kantenrundungen sollen die bisher gleichmäßige, weiche Wirkung reduzieren. Die Texturen sind eigene prozedurale Quellen, keine übernommenen Fotos oder fremden Spielassets.

Warme/kühlere Putz- und Holzvarianten sind Materialinstanzen desselben jeweiligen Masters. Das klare B02-Fenstermaterial wird weiter referenziert. Weder die bisherigen Materialgraphen noch die gemeinsam verwendeten alten Meshes wurden dafür geändert. Die neue Blender-Datei ist eine eigene editierbare Kopie; die zusätzlichen Unreal-Materialinstanzen bleiben im Integrationsstand dokumentiert.

## Räume und Einrichtung

Vorne liegt der offene Wohn-/Essbereich. Hinten schließen zwei Räume mit eigener Decke an: Schlafraum und Lager. Die lichte Grundfläche beträgt näherungsweise **9,52 × 6,96 m** vorne, **4,88 × 4,44 m** im Schlafraum und **4,52 × 4,44 m** im Lager. Zwei neue Durchgänge sind **120 × 235 cm** frei; vorerst ohne zusätzliche Türblätter. Die Raumaufteilung ist ein überprüfbarer Vorschlag.

Neue, separat exportierte Assets: Esstisch, Stuhl, Bett, Kleiderschrank, Anrichte, Bücherregal, Bank, Beistelltisch, Arbeitstisch, Truhe, Teppich, drei Laternenformen, drei geschlossene Wandbreiten, ein Durchgangsmodul und eine Deckenkachel. Insgesamt **19 neue Meshes** und **37 Innenrauminstanzen**. Möbel sind statische Modelle ohne Sitz-, Inventar-, Schlaf- oder Craftingfunktion. Es gibt noch keine Feuerstelle oder Kochmechanik.

Quelle: [EH_Musterhaus_B03.blend](EH_Musterhaus_B03.blend). Einzelne kalibrierte FBX unter [Exports/](Exports/); Geometriedaten, Slots, Kollisionshüllen, Maße und Platzierungen stehen im [Manifest](manifest.json). Neue Slots verwenden das Präfix `B03_`; die semantischen Rollen sind im Manifest aufgeführt. Kein bestehender Slotvertrag wurde verändert.

## Nachvollziehbare Beleuchtung

Das vorhandene Lab-Tageslicht bleibt erhalten und fällt weiterhin durch die tatsächlichen Fensteröffnungen mit sichtbaren klaren Scheiben. Neu sind **vier** sichtbare Leuchten mit zugehörigen Point Lights:

| Ort | Leuchte | Lichtstrom | Farbtemperatur |
| --- | --- | ---: | ---: |
| Essplatz | Hängelaterne, Aufhängung bis zur Dachunterseite | 90 lm | 3000 K |
| Schlafzimmer | Laterne auf dem Beistelltisch | 24 lm | 3000 K |
| Wohnbereich an der Trennwand | Wandleuchte mit befestigtem Arm | 40 lm | 3000 K |
| Lager | Laterne auf der Anrichte | 24 lm | 3000 K |

Die drei eigenen `BP_EH03_*` unter `/Game/Art/Furniture/ElvenHouseB03/Blueprints` bündeln sichtbare Geometrie und passende Lichtkomponente. Inverse quadratischer Abfall, begrenzte Radien und Schatten durch Raumgeometrie; keine zusätzlichen unsichtbaren Aufhelllichter. Das Leuchtengehäuse selbst wirft keinen Schatten auf seine eingeschlossene Punktquelle. Das ist eine bewusste Prototypvereinfachung, keine optische Simulation eines realen Brenners. Der kleine sichtbare Leuchtkern besitzt ein Emissionsmaterial. Brennstoff, Schalt-/Tageszeitlogik und Feuerpartikel sind nicht festgelegt oder implementiert.

Die erste gerenderte Fassung zeigte zu dominante gelbe Lampen und irrtümlich Stein auf dem Innenboden. Nach dieser Sichtprüfung wurden die vier Lichtströme reduziert, die Farbtemperatur auf 3000 K vereinheitlicht, die Grundfarbtexturen zurückgenommen und der Boden auf Bretter umgestellt. Materialinstanzen und Lampen-Blueprints wurden ebenfalls korrigiert. Die endgültigen Bilder zeigen den danach geprüften Zustand.

## Prüfbelege

- [Blender-Prüfung](Evidence/blender_verification.json): Quelle erneut geöffnet, Bildverweise aufgelöst, sämtliche 19 FBX zurückimportiert; Geometrie, Flächenorientierung, UVs, Maße und UCX-Anzahlen geprüft.
- [Legacy-Reimport](Evidence/reimport_assets.json): alle 19 eigenen Meshes explizit mit `FbxFactory` erneut importiert; Dreiecke, Slots, Materialreferenzen und Kollisionsanzahlen erhalten.
- [Gespeicherter Lab-Zustand](Evidence/lab_verification.json): tatsächliche Importbounds, Slots, Kollision, Durchgangs-/Kapselabfragen, Leuchten und Erhalt der Bestands-Actors.
- [Begehung](Evidence/pie_room_walk.json): tatsächliche CharacterMovement-Eingaben durch Wohnbereich, beide hinteren Räume und zurück; keine Teleports oder NoClip innerhalb der Route. Eine automatisierte Prüfroute ersetzt keinen vollständigen manuellen Kameratest.
- [Erhaltungskontrolle](Evidence/preservation.json): Vergleich gegen den gesamten vor B03 erfassten Bestand einschließlich uncommittierter B02-Dateien.

## Ansichten

[Außen](Previews/exterior.png) · [Wohnbereich](Previews/living.png) · [Raumaufteilung](Previews/rooms.png) · [Schlafzimmer](Previews/bedroom.png) · [Lager](Previews/storage.png) · [Haus und Ausstellung](Previews/overview.png) · [Einzelteile](Previews/gallery.png)

## Grenzen und Übergabe

Status höchstens **review_ready**, nicht accepted. Manuell zu beurteilen sind Materialwirkung aus Spielentfernung, ausreichende Variation, Möblierungsdichte, Raumgrößen, Third-Person-Kamera und Lichtstimmung. Diese Lieferung ist ein eingerichtetes Muster, keine freigegebene Hausserie. Weitere Haus-/Fensterformen, vollständige Küchenausstattung, Türblätter innen, Interaktionen, LODs, Siedlungsperformance, Cooking/Packaging und Multiplayer bleiben offen. Bereits zuvor dokumentierte Grenzen der unveränderten oberen Hüllenkollisionen bestehen weiter.

Nur das Refiner-Projekt wird verändert. Bestehende Dateien beschränken sich auf Lab und technischen Status; dazu kommen eigene B03-Quellen und Unreal-Assets. Kein Hauptprojekt-Import, keine Gameplay-/Projektkonfigurationsänderung, kein Commit und kein Push. Importe verwenden **FBX_SCALE_NONE**, `UE_cm=(100*B.x,-100*B.y,100*B.z)`, den geprüften Legacy-Pfad und Einheitsskalierung. Der sitzungsweise geänderte Importerwert wird abschließend wiederhergestellt.

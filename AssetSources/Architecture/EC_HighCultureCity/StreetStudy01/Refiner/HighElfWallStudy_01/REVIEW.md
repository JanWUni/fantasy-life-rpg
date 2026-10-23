# Hochelfen-Wandvergleich 01

Status: **review_ready**, nicht accepted. Blender-Stilstudie, kein fertiges Produktionsasset.

## Auftrag und Referenz

Zwei getrennte Wandvarianten nach der vom Nutzer gezeigten hellen Turm-/Palastreferenz: elfenbeinfarbener Stein, feine Goldlinien, kleine eisblaue Einlagen, schlanke Spitzbogenreliefs. A ist zurückhaltend, B besitzt zusätzliche seitliche Blindbögen, aufsteigende Rippen und plastische Steinprofile. Keine Gebäudeart, Magiefunktion, soziale Zuordnung oder allgemeine Architekturregel festgelegt. Bestehende Häuser und ältere Wandstudien unverändert.

Eigener Schreibbereich: `AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner/HighElfWallStudy_01/`.

## Quelle und Maße

Eingang: eigene geprüfte `WallCatalogue_01/WindowResize_02/WindowResize02.blend`, SHA256 `4dc9c257cc00392ae334415d51b9d64c10d2deeab345c27b3588f555dd98bbe3` auf Worktree `assets/refiner`, HEAD beim Start `17828dce95c0d68fd5300bc9d8cba1db1178b83f`. Der bisherige A-Wandkern wurde ausschließlich gelesen und in neue Geometrie-/Materialdaten übernommen. Quelle ist uncommitted; der Hash bezeichnet den genauen Eingang.

Neue Quelle: `HighElf_WallVariants_01.blend`, Blender 5.2.2 LTS. Kit `HE.WallStudy01`, neue visuelle Schnittstelle `new_visual_draft_1`; kein Ersatz unter altem Assetnamen oder Materialslotvertrag.

- Wandkern 300 × 24 × 320 cm, Fensteröffnung 65 × 90 cm, Brüstung 135 cm. Kern inklusive vorhandener parabolischer Öffnung geometrisch unverändert. Der spitze äußere Bogen ist zusätzlicher Schmuck; er vergrößert nicht die Öffnung.
- Lokales Mesh: Ursprung unten am Wandanfang; X entlang der Wand, +Y innen, Z oben. A wird bei X0, B bei X4,2 m präsentiert. Objekte haben Einheitsskalierung und keine Rotation. Dekor bleibt innerhalb X0–3 / Z0–3,2 m; tatsächliche Tiefen je Komponente stehen im Manifest. Neue Reliefs sind keine bereits abgenommenen Gebäudeanschlüsse.
- Wandkern, Steinrelief, Gold, blaue Einlagen, Rahmen und Glas sind je Variante separat auswählbar. Die kleinen blauen Steine besitzen Goldfassungen und sind baulich angebunden, nicht schwebend und keine Lichtquelle.
- Frontdekoration ist ausgearbeitet; Rückseite bewusst schlicht mit Rahmen, Sockel und Gesims.

## Tatsächliche Prüfungen

`Evidence/verification.json`: Datei in einem separaten Blender-Prozess erneut geöffnet; alle 12 Komponenten geprüft. Keine nichtmanifold Kanten, degenerierten Dreiecke oder degenerierten UV-Dreiecke. Einheitsskalierung und Modulgrenzen bestätigt. Beide Wandkern-Dreiecksmengen stimmen mit der Eingangsquelle überein. Raycasts zeigen echte freie Fensteröffnungen; seitlicher Stein, Brüstung und Sturz bleiben geschlossen. Glas ist eine separate geschlossene Scheibe mit Transmission 1. Die Blender-Schattenstrahlen passieren das Glas als Näherung für Tageslicht.

`Evidence/preservation.json`: 1946 bereits vorhandene Dateien unter AssetSources, Content, Config, Source, Tools und docs byteweise verglichen, keine Änderung. Kein Unreal-Aufruf, Import, Reimport, Karten-Save, Commit oder Push.

## Umfang und technische Grenzen

| Variante | Dreiecke | Vertices | getrennte Komponenten |
| --- | ---: | ---: | ---: |
| A – Schlicht | 3912 | 2076 | 6 |
| B – Prachtvoll | 9860 | 5118 | 6 |

Gegenüber dem bisherigen A-Wandmesh (792 Dreiecke, ohne separaten Rahmen/Glas) liegt hier deutlich mehr Detailgeometrie vor. Die 1.000-Dreiecke-Reviewschwelle für einfache Prototypwände wird überschritten: absichtlich zur Beurteilung von Silhouette, Rahmen und Relief. Vor Serienproduktion Geometrie vereinfachen bzw. Reliefanteile backen. Keine Performancefreigabe. Sechs Materialfamilien pro Ensemble, höchstens zwei Slots je einzelner Komponente; spätere Zusammenfassung/Slotbudget offen. Ein Detailstand, keine LODs, kein Nanite.

UV0 ist eine absichtlich überlappende Projektion für wiederholbare Oberflächen. Eigene Blender-Prozeduralmaterialien verwenden Objektkoordinaten; subtile Korn-, Farb- und Rauheitsvariation. Keine externen Bildtexturen erforderlich. Diese Shader sind nicht automatisch Unreal-kompatibel: Backen oder gezielt in Unreal nachbauen, sobald eine Richtung gewählt ist.

In diesem Blender-Auftrag keine FBX-Exporte, UCX-Hüllen, Unreal-Licht-/Kollisions-/Reload-Prüfung. Nach Stilentscheidung: Kollisionshüllen mit freier Öffnung, Export/Rückimport, Materialübertragung, Anschluss- und Laufzeitprüfung. Eine Integration ist hier nicht erfolgt.

## Ansehen

Blender startet im Material-Vorschaumodus mit beiden Varianten im Blick. Mittlere Maustaste dreht, Mausrad zoomt, Umschalt + mittlere Maustaste verschiebt. Collections `A_Schlicht` / `B_Prachtvoll`; Kameras `01_Aussen_Vergleich`, `02_Innen_Vergleich`, `03_Detail_Prachtvoll`, `04_Front_Orthogonal`. Renderbelege unter `Previews/` stammen aus der tatsächlichen Blender-Geometrie. Podeste, Schrift und Studiolicht gehören nur zur Präsentation.

Offen: visuelle Nutzerbewertung, Auswahl/Weiterentwicklung und technische Optimierung. Nicht als finaler Hochelfen-Kanon oder fertiges modulares Produktionskit übernehmen.

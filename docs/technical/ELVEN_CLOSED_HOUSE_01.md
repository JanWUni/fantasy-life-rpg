# Modulares Elfenhaus – geschlossener Prototyp 01

Stand: **22. Oktober 2026**, Unreal Engine 5.8. Das [zweifeldrige Anschlussmuster](ELVEN_JOIN_SAMPLE_01.md) wurde auf Nutzerauftrag zu einem geschlossenen, begehbaren Haus mit Funktionstür ergänzt. Es bleibt ein einfacher Architekturprototyp; Fenster, Möblierung, Stützen und weitere Verzierungen wurden nicht ergänzt.

**Folgestand:** Auf weiteren Nutzerauftrag ersetzt jetzt ein [Fenstermodul](ELVEN_WINDOW_01.md) das erste Außenwandfeld des Prefabs und seiner Lab-Instanz. Der folgende Bericht beschreibt den vorherigen Stand mit zwei geschlossenen Außenwandfeldern; die damaligen Modulassets bleiben erhalten. Aktuelle Fensterdaten und Testergebnisse einschließlich offener Eingabe-Regressionen stehen im Fensterbericht.

## Finden und wiederverwenden

- Karte: `/Game/Prototype/Maps/Lvl_AssetLab`.
- Outliner: `Lab/Architecture/ElvenClosedHouse01`, Actor `Lab_EBHouse_Closed01`.
- Position **(−4400, 1000, 12)**, Einheitsskalierung, westlich der ursprünglichen Stilstudie. Eingang auf der Hofseite in der Mitte des 60°-Bogens. Der Lab-Boden liegt 12 cm unter dem Innenboden; die Schwelle ist begehbar.
- Platzierbares Gesamt-Prefab: `/Game/Art/Architecture/ElvenBlatthof/Modular/ClosedHouse01/BP_EB_House_A60_Prototype01`.
- Vorhandene Bedienung: am Eingang **E** zum Öffnen/Schließen. Die vorhandene Tür schaltet unmittelbar um; keine neue Schwenkanimation, Schloss- oder Hindernislogik.

Die acht einzelnen Actors des früheren Anschlussmusters wurden durch eine Hausinstanz ersetzt, das zugehörige Schild aktualisiert. Die vier bisherigen Modulassets bleiben erhalten. Die ursprüngliche Blatthof-Stilstudie samt Hausasset, Generator, Materialien und Platzierung bleibt unverändert.

## Aufbau und neue Assets

Das Prefab enthält neun statische Meshkomponenten: je zwei vorhandene Böden, Außenwände und Dächer, ein neues Eingangsfeld und zwei neue Endabschlüsse. Hinzu kommen zwei ChildActorComponents für die **unveränderten** `BP_PrototypeDoor` und `BP_PrototypeDoorFrame`. Kein neues Gameplay-C++, kein neues Eingabesystem und keine prozedurale Generierung.

Die drei neuen Meshes liegen unter `/Game/Art/Architecture/ElvenBlatthof/Modular/ClosedHouse01/Meshes/`:

| Asset | Aufbau | Dreiecke |
| --- | --- | ---: |
| `SM_EB_WallInner_Entry_A60_H280_Sealed` | 60°-Innenwand mit geradem Portal und Übergangsschultern; nominale Rahmenöffnung 144 × 232 cm | 108 |
| `SM_EB_EndCap_R245_650_A3_Start_Full` | Anfangsabschluss mit vollständigem Wand-/Dachquerschnitt R245…650 | 220 |
| `SM_EB_EndCap_R245_650_A3_End_Full` | Entsprechender Endabschluss mit umgekehrter Belegungsrichtung | 220 |

Gesamtgeometrie ohne vorhandenes Türblatt/Rahmen: **4.452 Dreiecke**. Alle neuen Wandteile referenzieren das bestehende `MI_Blatthof_Ivory`. Boden-, Außenwand- und Dachassets werden aus `JoinSample01` referenziert; keine unabhängigen Kopien dieser Geometrie. Tür und Rahmen behalten ihre bisherigen grauen Prototypmaterialien.

Quelle: [generate_elven_closed_house.py](../../Tools/Prototype/generate_elven_closed_house.py). Aufruf im Projektverzeichnis:

```powershell
python -B Tools/Prototype/generate_elven_closed_house.py
```

Ausgabe ausschließlich nach `Saved/ElvenClosedSources/`: drei OBJ, MTL und Manifest mit Kollisionsboxen und Anschlussdaten. Bestehende Exporter werden als Bibliothek verwendet, ihre `build()`-Funktionen nicht ausgeführt und ihre Dateien nicht geändert. Unreal-Import, Prefab-Aufbau und Platzierung erfolgten über MCP. Das Skript ist eine Geometriequelle; es erzeugt kein Unreal-Haus automatisch.

## Maße, Anschluss und Kollision

Das Eingangsfeld ersetzt genau die beiden früheren hofseitigen 30°-Wandfelder. Seine äußeren Anschlüsse behalten Radien R245/R265, Boden Z0 und Wandkrone Z280. Um einen flachen Rahmen sauber anzuschließen, geht die Rundung im mittleren Bereich über zwei kurze Schultern in ein gerades Portal über. Die neue Wandöffnung und ihre Kollision enthalten keine Wandfläche hinter der Tür.

Das vorhandene Türblatt bleibt **120 × 12 × 220 cm**. Im gemeinsamen R255-Startkoordinatensystem liegen die beiden ChildActorComponents bei ungefähr `(77,538476; 0,699420; 0)` mit Yaw 30° und **Einheitsskalierung**. Der Blueprint der Funktionstür enthält seine Blattgröße bereits am Root-Mesh; keine zweite Skalierung wird aufgebracht. Die Tür öffnet relativ zu ihrer Ausgangsdrehung um −90° in Richtung Innenraum.

Die Endabschlüsse folgen jeweils einem 3°-Dachfeld. Ihre tangentiale Dicke wächst mit dem Radius ungefähr von 13 bis 34 cm; sie sind keine geraden 20-cm-Wandplatten. Der gesamte Wandquerschnitt einschließlich der Wand-Dach-Füllbereiche wird abgedeckt. Eine äußere Überdeckung von 0,01° – maximal ungefähr 1,2 mm – verhindert koplanare Endflächen und verdeckt die bisherigen Stirnflächen der weiterverwendeten Module. Der Endabschluss besitzt eine eigene Form für Anfang und Ende; keine negative Skalierung.

Kollision: vorhandene Boden-/Außenwand-/Dachkörper bleiben erhalten; das Eingangsfeld ergänzt sieben Boxen mit freier Türöffnung, jeder Endabschluss zehn Boxen entlang des Dachprofils. Insgesamt **73 einfache Körper für die neun statischen Hauskomponenten**, ohne die vorhandene Tür/Rahmen-Kollision. `UseSimpleAsComplex` bleibt die Prüfkonvention. Die oberen Endprofile sind durch Boxen angenähert; die bereits dokumentierte Dachnäherung und Bodenüberdeckung bleiben Prototypgrenzen. Keine Produktions- oder Siedlungsperformance gemessen.

## Tatsächlich geprüft

| Prüfung | Ergebnis |
| --- | --- |
| Geometriequelle | Eingangsendpunkte passen zum R255-Kit; äußere Endflächen auf korrekte Normalenrichtung geprüft |
| Prefab-Kompilierung | Mit Warnungen als Fehler erfolgreich |
| Statische Hülle | 14 Bodenabfragen einschließlich Naht auf Welt-Z12, zwölf Endwandabfragen auf zwei Höhen, Seitenwand-/Dach-/Sturzabfragen erfolgreich; Innenachse frei |
| Geschlossene Tür | Linienabfrage trifft das Blatt; tatsächliche Spielerkapsel wird vor dem Eingang gestoppt |
| Öffnen von außen | Vorhandene Spielerkomponente ruft `TryInteract` auf; Rückgabe erfolgreich, Haus-Türzustand offen, Drehung von etwa 30° auf −60°, mittiger Durchgang frei |
| Eingang | Tatsächlicher Spieler passiert die Schwelle ohne Teleport/NoClip; `MOVE_Walking`, vollständiger Eintritt bestätigt |
| Bedienung innen | Über denselben Interaktionspfad schließen und erneut öffnen erfolgreich; geschlossene Drehung innerhalb numerischer Toleranz wiederhergestellt |
| Ausgang | Spieler geht wieder hinaus und landet auf dem Lab-Boden; anschließendes Schließen von außen erfolgreich |
| Rahmen / Hervorhebung | Rahmentransform unverändert; vorhandenes `M_InteractionHighlight` am Türmesh nachgewiesen |
| Vorhandene Regressionstests | `Interaction.DoorPIE`, `AssetWorkspace.AssetLabPIE` und `DeveloperToolbox.MapsPIE.Lvl_AssetLab`: **3/3 erfolgreich, 10,39 s**, keine Testwarnungen/-fehler |
| Speicherung | Lab und vier neue Spielassets ausdrücklich gespeichert; erneutes Laden über die Sandbox und abschließende Hüllenabfragen |
| Sichtprüfung | Gerenderte Vorder-, End- und Außenansicht kontrolliert |

Die neue Tür wurde über eine **temporäre Prüf-Hilfe** mit der vorhandenen `UInteractionComponent::TryInteract()` des Spielers bedient. Damit laufen Zielsuche, Distanz-/Sicht-/Autoritätsprüfung und die unveränderte Türlogik regulär. Der Test setzt weder `bIsOpen` direkt noch teleportiert er den Spieler durch den Durchgang. Die Fortbewegung erfolgt über kurzzeitige Geschwindigkeitsimpulse der bestehenden CharacterMovement-Komponente. Dies ist **kein physischer E-/WASD-Bedienungstest am neuen Haus**. Der vorhandene `DoorPIE` prüft zusätzlich die bisherige Tür über den simulierten E-/Enhanced-Input-Pfad im ursprünglichen Testlevel.

Die Prüf-Hilfe und eigene verworfene Meshzwischenstände wurden anschließend entfernt; sie sind weder Bestandteil des gespeicherten Levels noch des Haus-Prefabs. Die finale Endflächenabdeckung wurde nach der Bewegungsprüfung ergänzt und anschließend statisch sowie visuell erneut geprüft; der Interaktions-/Schwellenbereich bleibt dabei unverändert.

Während der Entwicklung wurden Werkzeuggrenzen und Prüfskriptfehler korrigiert: strikte Floatgleichheit, eine zu kurze Bewegungsstrecke, nicht exponierte Eigenschaften und nicht unterstützter Reimport. Erfolgreiche Endprüfungen werden von diesen Fehlversuchen getrennt. Keine Logunterdrückung geändert. Kein C++-Build und keine vollständige Gesamtsuite erforderlich bzw. ausgeführt.

## Umfang und offene Folgeprüfungen

Geändert wurden die autorisierte Lab-Aufstellung und technische Dokumentation. Neu sind die drei Meshes, das Haus-Prefab und die zusätzliche Geometriequelle. Bestehende Stilstudien-/Tür-/Materialassets, die vier bisherigen Modulassets, übrige Karten, C++, Konfiguration und Worldbuilding bleiben erhalten; Dateihashes und die ursprünglichen Stilstudienkomponenten werden abschließend verglichen. Keine Commits, Pushes oder Staging-Aktionen.

Manuell noch prüfen: E von beiden Seiten, WASD über die Schwelle, Third-Person-Kamera an Tür und Dach, alle Innenecken sowie das unmittelbare Schließen bei einem Spieler im Schwenkbereich. Das Türsystem besitzt weiterhin keine Hindernisprüfung. Fenster, Möblierung, architektonische Verzierungen, weitere Hausgrößen, finale UVs/Texturen, Packaging und größere Szenen sind nicht Teil dieses Schritts. Das geschlossene Haus ist geometrisch vollständig, aber noch kein fertig ausgearbeitetes Wohnhausasset.

Lokale Belege unter `Saved/InteractionDev/`: `closed_house_geometry.json`, `closed_house_place_result.json`, `closed_house_runtime_result.json`, `closed_house_verify_result.json`, `closed_house_full_caps_result.json`, `closed_house_smoke_result.json`, `closed_house_preserve_result.json`, `closed_house_final_audit.json` sowie `closed_house_front.png`, `closed_house_end.png`, `closed_house_overview.png`, `closed_house_inside_pie.png`. Zwischenquellen unter `Saved/ElvenClosedSources/` bleiben ignoriert.

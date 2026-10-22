# Elfisches Wohnhaus – Blatthof-Stilstudie 01

Stand: 22. Oktober 2026, Unreal Engine 5.8.

Der Nutzer hat den unteren der drei Fantasy-Entwürfe (C, Blatthof) als Grundlage für ein erstes Muster im Asset-Lab gewählt. Die Studie untersucht die Formensprache im Spielmaßstab: geschwungener Grundriss, helle Wände, grünblaue Blattdächer mit Mittelrippen, verzweigte Holzstützen, Fenstermaßwerk und ein Hof mit angedeutetem Wasserlauf. Der Stand ist ein begehbarer Geometrie-/Farbprototyp. Gesellschaftliche Zuordnungen, regionale Bautypen und endgültige Architekturregeln werden hier nicht festgelegt. Worldbuilding bleibt unverändert.

## Im Editor finden und verwenden

- Karte: `/Game/Prototype/Maps/Lvl_AssetLab`.
- Outliner: `Lab/Architecture/ElvenBlatthof`, Actor `Lab_ElvenBlatthof_StyleStudy`.
- Position: `(-1900,1200,0)`, im hinteren linken Architektur-Bereich, Skalierung `(1,1,1)`.
- Vom Start aus links gehen, an den bestehenden Wand-/Türmustern vorbeigehen und den Hof von der Seite betreten. Die bisherigen Wandmuster bleiben vor dem Haus stehen; der Hof ist seitlich erreichbar.
- Wiederverwendbares Gesamtasset: `/Game/Art/Architecture/ElvenBlatthof/BP_ElvenBlatthof_Study`. Eine weitere Instanz lässt sich aus dem Content Browser platzieren.
- Im Hof die Eingangstür mit **E** öffnen/schließen; die vorhandenen Aktionstexte und die goldene Hervorhebung werden weiterverwendet. Mit **F6** kann die vorhandene freie Kamera für die Außenansicht aktiviert werden.

## Aufbau und Maße

Der Blueprint enthält vier getrennte StaticMeshComponents und zwei ChildActorComponents für die unveränderten `BP_PrototypeDoor` und `BP_PrototypeDoorFrame`. Keine neuen C++-Klassen, Inputassets oder Gameplay-Systeme. Der Blatt-/Hofgrundriss ist eine zusammenhängende bogenförmige Wohnfläche; eine Raumaufteilung und Möblierung fehlen noch.

| Asset unter `Art/Architecture/ElvenBlatthof/Meshes` | Zweck | Dreiecke |
| --- | --- | ---: |
| `SM_ElvenBlatthof_Shell` | Boden, gebogene Wände, ausgesparte Türöffnung, geschlossene Fensterflächen | 3.836 |
| `SM_ElvenBlatthof_LeafRoof_Smooth` | Dreiteiliges gebogenes Dach, geglättete Normalen | 6.528 |
| `SM_ElvenBlatthof_Ribs_Smooth` | Holzstützen, Dachadern, Fenstermaßwerk, Beeteinfassung | 29.040 |
| `SM_ElvenBlatthof_Courtyard` | Weg, angedeutete Brücke, Wasserstreifen, Pflanzenplatzhalter | 212 |

Gesamtgeometrie ohne die bestehenden Tür-/Rahmenmeshes: **39.616 Dreiecke**. Außenmaße einschließlich Dachrippen und Hofweg ungefähr **14 × 14,25 × 5,65 m**. Wandhöhe mindestens 2,8 m, Bodenoberkante Z=0, Türblatt 120 × 12 × 220 cm, vorgesehene Rahmenöffnung 144 × 232 cm. Der gemeinsame Pivot liegt auf Bodenhöhe im Mittelpunkt des bogenförmigen Grundrisses; Hoföffnung zeigt lokal nach -Y. Dach und Wandkörper besitzen für diesen statischen Einzelprototyp `UseComplexAsSimple`, doppelseitige Kollisionsgeometrie. Rippen und Hofdekoration kollidieren nicht; im Hof trägt der vorhandene Lab-Boden den Spieler. Es gibt keine Wassersimulation, Flüssigkeitskollision oder Brückenphysik.

Neun eigene Materialinstanzen unter `/Game/Art/Materials/ElvenBlatthof/MI_Blatthof_*` verwenden den bestehenden Master `M_FlatCol`: Ivory, Jade, JadeLight, Timber, Bronze, Glass, Stone, Garden und Water. Glas und Wasser sind bewusst opake Farbplatzhalter. UVs sind einfache generierte Projektionskoordinaten; finale Texturierung, Lightmap-UVs und Materialqualität stehen aus. Die vorhandene Tür behält zunächst ihre bisherige graue Testdarstellung.

Reproduzierbare Geometriequelle: `Tools/Prototype/generate_elven_blatthof.py`. Aufruf im Projektverzeichnis: `python Tools/Prototype/generate_elven_blatthof.py`. Der Generator schreibt OBJ/MTL und ein Manifest nach `Saved/ElvenBlatthofSources` (ignoriert). Die dortigen Dateien `..._LeafRoof.obj` und `..._Ribs.obj` sind die Quellen der abschließend importierten `_Smooth`-Assets. Import, Materialzuordnung, Blueprint-Komponenten, Platzierung und Speicherung erfolgten über Unreal MCP. Zwei früh erzeugte facettierte Zwischenmeshes wurden nach Prüfung fehlender Referenzen entfernt; nur die vier finalen Meshes verbleiben.

## Tatsächlich geprüft

| Prüfung | Ergebnis |
| --- | --- |
| Haus-Blueprint mit Warnungen als Fehler kompilieren | Erfolgreich |
| MCP-Linienabfragen im gespeicherten Lab | Außenwand und geschlossene Tür blockieren; Hofweg und Innenraumachse frei; Innenboden und Hofboden auf Z=0; Dach blockiert |
| Tür im neuen Haus über tatsächliche Slate-E-Eingabe in PIE | Öffnen und Schließen erfolgreich, `bIsOpen` jeweils ausgelesen; geschlossener Durchgang blockiert, offener Durchgang frei |
| Vorhandenes Feedback an der neuen Haustür | Beide Texte „E – Tür öffnen“ / „E – Tür schließen“ im Slate-Baum bestätigt; offene, gold hervorgehobene Tür im gerenderten Spielfenster geprüft |
| Tatsächliche W-Eingaben bei offener Tür | Spieler von Y=1300 durch den Eingang bis Y≈1794,99 gelaufen; Bodenhöhe stabil, äußere Wand beendet Vorwärtsbewegung |
| Bestehender `FantasyLifeRPG.AssetWorkspace.AssetLabPIE` | Erfolgreich, 3,79 s |
| Bestehender `FantasyLifeRPG.DeveloperToolbox.MapsPIE.Lvl_AssetLab` | Erfolgreich, 1,22 s |
| Speichern und erneutes Laden über eine andere Karte | Haus und ChildActors bleiben vorhanden; 14 neue Assets und Lab jeweils `dirty=false` |

Die beiden vorhandenen automatisierten Tests liefen gemeinsam **2/2 erfolgreich in 5,02 s**, ohne Testwarnungen und ohne Testfehler. Anschließend war PIE beendet. Diese beiden Tests prüfen die bisherige Lab-/Toolbox-Funktion; die neue Haustür wurde zusätzlich wie oben beschrieben separat in PIE geprüft. Die frühere vollständige 14er-Suite wurde in diesem Auftrag nicht erneut ausgeführt. Kein neuer C++-Build, da C++ unverändert blieb.

Eine erste Sichtprüfung fand eine doppelt angewandte Skalierung des eingebetteten Türblatts. Die ChildActorComponent verwendet jetzt Einheitsskalierung, weil die bestehende Tür ihren Maßstab bereits am Root-Mesh definiert. Nach Neuerzeugung der Hausinstanz und erneutem Laden sind 220 cm Türhöhe und die erfolgreiche PIE-Interaktion bestätigt. Während explorativer MCP-Abfragen wurden Editor-only-Levelabfragen während PIE sowie Zugriffe auf nicht exponierte Eigenschaften abgewiesen. Diese Werkzeugabfragen erzeugten Logfehler/-warnungen, sind kein meldungsfreier Gesamtlauf; die abschließenden beiden Tests meldeten keine Fehler oder Warnungen. Keine Einstellungen zur Unterdrückung von Meldungen geändert.

Lokale, ignorierte Belege: `Saved/InteractionDev/elf_verify_result.json`, `elf_pie_checks.json`, `elf_house_tests.json`, `elf_house_game.png`, `elf_house_final_overview.png` und `elf_house_final_audit.json`. Lokale MCP-Phasenskripte liegen ebenfalls in `Saved/InteractionDev/`.

## Grenzen und manuelle Folgeprüfung

Längere Begehung beider Gebäudeflügel, Rückweg und Türbedienung von innen, Kamera an allen Bögen/Dachkanten und Kontakte an seitlichen Fenstern sind noch manuell zu beurteilen. Die Linienabfragen sind kein vollständiger Kapseltest aller Oberflächen; der tatsächliche Lauf bestätigt die mittlere Eingangsroute. Der Hofweg, Wasserstreifen und Pflanzen sind visuelle Platzhalter auf dem Lab-Boden. Der Innenraum ist unmöbliert. Die geschwungenen Dächer sind eine erste räumliche Interpretation des ausgewählten Bildes, kein maßgetreuer Nachbau.

Nicht geprüft: finale Beleuchtung/Materialien, Performance bei vielen Häusern, LODs, optimierte modulare Kollision, Cooking/Packaging, Multiplayer oder Hausinstanzen in der World-Sandbox. Die vorhandene Tür schaltet ihren Zustand weiterhin unmittelbar um; eine Schwenkanimation und Hindernisprüfung wurden nicht ergänzt.

Mögliche spätere Varianten können dieselbe Formsprache mit anderem Maßstab, Hofumfang, Material und Detailgrad verwenden. Ob diese Varianten Adel, Bürgern, anderen Gruppen oder Regionen zugeordnet werden, bleibt eine ausdrückliche spätere Designentscheidung.

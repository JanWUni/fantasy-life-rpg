# Elfisches Wohnhaus – Bestandsaufnahme und Modularisierungsplan

Stand: **22. Oktober 2026 · Phase 1 · Analyse und Vorschlag**. Bezugsprojekt: `FantasyLifeRPG`, Unreal Engine 5.8.

**Folgestand:** Das erste Anschlussmuster aus vier Modul-Typen und zwei verbundenen Feldern wurde anschließend auf Nutzerauftrag umgesetzt. Tatsächlicher Umfang, Kollisionsnäherungen und Prüfbelege stehen in [ELVEN_JOIN_SAMPLE_01.md](ELVEN_JOIN_SAMPLE_01.md). Die übrigen Module dieser Phase-1-Planung bleiben Vorschläge.

## 1. Ergebnis und Geltungsbereich

Das vorhandene Elfenhaus ist **kein einzelnes Mesh**, aber auch **noch kein modularer Gebäudebaukasten**. Ein platzierbarer Haus-Blueprint bündelt vier eigenständige, jeweils hausgroße Meshes sowie die bestehenden Tür-/Rahmenblueprints. Böden, einzelne Wände, Fenster, Stützen und Dachblätter existieren darin überwiegend als gemeinsam exportierte Geometrie, nicht als einzeln austauschbare Assets.

**Empfehlung:** Die Stilstudie vollständig als Referenz und Gesamt-Prefab erhalten. Einen kleinen Baukasten aus ihrer vorhandenen Geometriequelle ableiten: zunächst eine feste Bogenfamilie mit kompatiblen Boden-, Wand-, Dach- und Abschlussmodulen. Damit bleibt die geschwungene Formensprache erhalten. Gerade Ergänzungen folgen erst nach einem erfolgreichen Bogenversuch. Keine Einzelsteine, Dachschuppen oder separat platzierten Dachadern als Standardmodule.

Die Tabellen unterscheiden **VORHANDEN**, **ABLEITUNG** und **NEU**. ABLEITUNG bedeutet ein künftig separat herzustellendes Asset aus vorhandenen Formen oder Quellfunktionen; es ist heute nicht als Modul vorhanden. Alle Maße, Namen und Regeln für neue Module sind technische **Vorschläge**, keine bestätigten Architektur- oder Lore-Entscheidungen. Untersucht wird ausschließlich das elfische Wohnhaus. Siedlungsgenerierung, andere Bautypen und neue Gameplay-Systeme sind nicht Teil dieser Phase.

## 2. Prüfgrundlage und Belastbarkeit

| Grundlage | In dieser Phase geprüft | Aussagegrenze |
| --- | --- | --- |
| Aktives Projekt auf `E:\Business\fantasy-rpg\Unreal Engine Project\FantasyLifeRPG` | Ordner, vorhandene `.uasset`-/`.umap`-Dateien, `.uproject`, Quellcode, Dokumentation | Der ältere Ordner `UE-Backup-2026-10-21` im Chat-Arbeitsverzeichnis ist nicht das untersuchte Hauptprojekt |
| Gespeicherte Unreal-Pakete | Lesbare Paketpfade in Haus-, Mesh-, Material-, Tür- und Lab-Dateien abgeglichen | Stringprüfung belegt enthaltene Referenznamen, ersetzt keinen vollständigen Reference-Viewer-/Asset-Registry-Audit |
| `Tools/Prototype/generate_elven_blatthof.py` | Vollständige Geometrie- und Exportlogik gelesen | In dieser Phase nicht ausgeführt oder geändert |
| `Saved/ElvenBlatthofSources/*.obj`, `manifest.json` | Vorhandene Geometriequellen, Materialgruppen, Dreieckszahlen und Bounds geprüft | Quellen und frühere Importbelege sind keine neue Messung der aktuellen Editor-Renderdaten |
| Frühere lokale Prüfbelege und Stilstudien-Dokumentation | Import, Platzierung, spätere `_Smooth`-Referenzen, Türkorrektur und gespeicherte Tests nachvollzogen | Frühere Tests werden ausdrücklich nicht als heute erneut ausgeführt dargestellt |
| `Saved/InteractionDev/elf_house_final_overview.png` | Gespeicherte Außenansicht angesehen | Keine neue Live-Aufnahme oder vollständige Innenraum-Sichtprüfung |
| Unreal-MCP-Leseversuch | Lokaler Endpunkt erreichbar, `get_current_level` jedoch leer; Hausasset dort nicht auffindbar | Kein aktuell nutzbarer Editor-Projektkontext. LOD-Abfrage lieferte ungültige Daten und wird nicht ausgewertet. Keine Karte geladen, keine Assets gespeichert oder bearbeitet |

**Offen bleiben:** aktuelle LOD-/Nanite-Einstellungen, UV-Kanalqualität, vollständige harte/weiche Referenzketten, Blueprint-Graphdetails, eventuelle Editor-Overrides sowie gemessene Laufzeitkosten. Hierzu keine Vermutungen als Befund ausgeben. Beim nächsten freigegebenen Assetversuch zuerst den korrekten Editor-Projektkontext prüfen.

Lesend erzeugte lokale Belege liegen ignoriert unter `Saved/InteractionDev/elven_modular_static_inventory.json` und `elven_modular_baseline.json`. Die neue versionierbare Arbeit dieser Phase ist dieses Markdown-Dokument; keine neuen Spielassets, Systeme oder Änderungen an Worldbuilding.

## 3. Technische Bestandsaufnahme

### 3.1 Ablage und konkrete Identifikation

| Status | Pfad | Funktion |
| --- | --- | --- |
| VORHANDEN | `/Game/Prototype/Maps/Lvl_AssetLab` | Testwerkstatt, laut letzter Dokumentation 120 × 80 m |
| VORHANDEN | Outliner `Lab/Architecture/ElvenBlatthof`, Actor `Lab_ElvenBlatthof_StyleStudy` | Hausinstanz, dokumentiert bei `(-1900,1200,0)`, Einheitsskalierung |
| VORHANDEN | `/Game/Art/Architecture/ElvenBlatthof/BP_ElvenBlatthof_Study` | Wiederverwendbares Gesamt-Prefab; vier StaticMeshComponents, zwei ChildActorComponents laut Aufbau-/Platzierungsbelegen |
| VORHANDEN | `/Game/Art/Architecture/ElvenBlatthof/Meshes/` | Vier Hausmeshes; vollständige Namen in der folgenden Tabelle |
| VORHANDEN | `/Game/Art/Materials/ElvenBlatthof/MI_Blatthof_*` | Neun Materialinstanzen |
| VORHANDEN | `/Game/Prototype/Blueprints/BP_PrototypeDoor`, `BP_PrototypeDoorFrame` | Funktionstür und Rahmen, direkt vom Haus referenziert |
| VORHANDEN | `/Game/LevelPrototyping/Materials/M_FlatCol` | Gemeinsamer Materialmaster |
| VORHANDEN | `Tools/Prototype/generate_elven_blatthof.py` | Offline-Geometriegenerator für die Stilstudie |
| VORHANDEN, lokal/ignoriert | `Saved/ElvenBlatthofSources/` | OBJ, MTL und Manifest; aus versioniertem Skript reproduzierbare Zwischenquellen |
| VORHANDEN | `/Game/Art/Architecture/SM_Wall_Test_400x20x300` | Gerades Vergleichsmodul, 400 × 20 × 300 cm, unterer Eckpivot; kein Bestandteil des Elfenhauses |

`Content/Prototype/Environment/Meshes/SM_PrototypeTimberHouse` ist ein anderer Hausprototyp und wird nicht mit dem Elfenhaus verwechselt. Weitere Template-Türmeshes existieren unter `LevelPrototyping/Interactable/Door`, sind aber nicht die direkt im Elfenhaus eingebundenen Tür-Blueprints.

Die gespeicherten Paketpfade ergeben folgende nachvollziehbare Abhängigkeiten:

```text
Lvl_AssetLab
└─ BP_ElvenBlatthof_Study
   ├─ SM_ElvenBlatthof_Shell
   ├─ SM_ElvenBlatthof_LeafRoof_Smooth
   ├─ SM_ElvenBlatthof_Ribs_Smooth
   ├─ SM_ElvenBlatthof_Courtyard
   │  └─ jeweilige MI_Blatthof_* → M_FlatCol
   ├─ BP_PrototypeDoor → SM_Cube, Engine-Sphere für Griff
   └─ BP_PrototypeDoorFrame → SM_Cube
```

Die Materialzeile gilt für alle vier Hausmeshes. Die `.obj`-Dateien heißen weiterhin `..._LeafRoof.obj` und `..._Ribs.obj`; die final verwendeten Unreal-Assets tragen `_Smooth`. Die frühen Unreal-Zwischenassets ohne diesen Zusatz sind im untersuchten Meshordner nicht vorhanden.

### 3.2 Meshes und tatsächliche Wiederverwendbarkeit

Alle folgenden Meshnamen liegen unter `/Game/Art/Architecture/ElvenBlatthof/Meshes/`.

| VORHANDENES Asset | Gebündelte Bestandteile | Dreiecke¹ | Materialzuordnung aus Quellen/Paketen | Wiederverwendung heute |
| --- | --- | ---: | --- | --- |
| `SM_ElvenBlatthof_Shell` | Bogenboden, Innen-/Außenwände, Türöffnung, Fensterbrüstungen/-stürze, geschlossene Glasflächen, Wand-Dach-Füllflächen | 3.836 | Stone, Ivory, Glass | Gesamte Hülle wieder platzierbar; kein separater Boden, keine einzelnen Wand-/Fenstermodule |
| `SM_ElvenBlatthof_LeafRoof_Smooth` | Drei überlappende breite Dachblätter einschließlich Unterseiten und Randflächen | 6.528 | Jade, JadeLight, Timber | Ganzes Hausdach separat nutzbar, einzelne Blätter nicht als Assets vorhanden |
| `SM_ElvenBlatthof_Ribs_Smooth` | Sockel-/Kronenbänder, verzweigte Stützen, Dachadern/-ränder, Fenstermaßwerk, Portalbogen, Brückengeländer, Beeteinfassungen | 29.040 | Stone, Timber, Bronze, JadeLight | Gesamter Detailsatz separat; einzelne Funktionen nicht unabhängig austauschbar |
| `SM_ElvenBlatthof_Courtyard` | Weg, Brückenplatte, Wasserstreifen, Beet-/Pflanzenplatzhalter | 212 | Stone, Water, Garden | Hof als Gesamtgruppe; kein selbsttragendes, geprüftes Bodenmodul |

¹ Vorhandene OBJ-Dreiecke stimmen mit dem Manifest und den früheren Importmessungen überein. Summe **39.616**, ohne Tür und Rahmen. Kein heutiger LOD-/Renderdaten-Audit.

Die Rippen-/Detailgruppe umfasst rund **73,3 %** dieser Dreiecke. Das macht sie zum ersten Kandidaten für spätere Detailvereinfachung und eine sinnvolle Aufteilung, belegt aber allein noch keinen Performanceengpass. Die Materialgruppen ergeben 13 Gruppen über die vier Quellen; dies ist **keine gemessene Draw-Call-Zahl**.

### 3.3 Maße und Formensprache des Bestands

Die folgenden Zentimetermaße stammen aus dem Generator, dem Manifest und den dokumentierten Import-/Türprüfungen:

| Eigenschaft | Bestand |
| --- | --- |
| Gesamtausdehnung inklusive Rippen und Hofweg | ungefähr 1.400 × 1.425 × 565 cm; Unterkante teilweise Z = −12 |
| Grundriss | Bogen von −35° bis 215°, insgesamt 250°, Hoföffnung lokal nach −Y |
| Boden | Ringsektor R = 240…650, Z = −12…0; radiale Bruttobreite 410 |
| Hofseitige Wand | R = 245…265, Dicke 20, regulär Z = 0…280 |
| Außenseitige Wand | R = 630…650, Dicke 20, regulär Z = 0…280 |
| Freie radiale Wohnbreite | 630 − 265 = **365** vor Zier-/Kollisionsdetails |
| Wandhöhe | Reguläre Wandkrone 280; zusätzliche Füllflächen folgen dem Dach und reichen höher |
| Dach | R = 215…695, Blattoberseite 300 plus Querwölbung bis 155 und winkelabhängige Spitzenanhebung; Unterseite um 12 abgesenkt |
| Drei Dachbereiche | −41…45°, 39…141°, 135…221°; Überlappungen von jeweils 6° |
| Fenster | Vier Bereiche von je 18°; Brüstung Z = 75, Oberkante 240, Höhe 165; Breite am Außenradius ungefähr 203 cm als Sehne |
| Eingang | Im hinteren Hofzentrum; nominell 144 × 232 Öffnung, Türblatt 120 × 12 × 220 |
| Hauspivot | Gemeinsamer Ursprung aller Hausgruppen auf Bodenhöhe im Mittelpunkt des Bogenkreises; kein Wand-Eckpivot |

Die nominelle Türöffnung wird durch einen Winkel aus `asin(72/260)` definiert. Ihre Sehnenbreite hängt deshalb vom betrachteten Wandradius ab; **144 cm sind nicht pauschal überall lichte Durchgangsbreite**. Beim Ableiten des Eingangs ist die reale engste Kollision zu prüfen. Das bestehende Türblatt ist als eigener interaktiver Actor wiederverwendbar. Seine Skalierung steckt bereits am Root-Mesh; die zuletzt korrigierte ChildActorComponent hat Einheitsskalierung. Diese Besonderheit beim Einbau erhalten und keine zweite Skalierung aufbringen.

Zu bewahren sind vor allem die helle geschwungene Wandmasse, die breiten grünblauen Blattdächer, warme verzweigte Holzstützen, bronzene Akzente und das Blattmaßwerk. Der Hof bleibt ein separates Ausstattungsangebot. Glas und Wasser sind derzeit opake Farbplatzhalter, keine fertigen Glas-/Wassermaterialien. Die neun Materialinstanzen lassen sich unmittelbar für neue Testmodule weiterverwenden; neue Mastermaterialien sind für den ersten Versuch nicht erforderlich.

### 3.4 Geometrie, Kollision und Generatoren

- Die Hülle enthält reale Aussparungen für Fenster; darin sitzen jedoch dunkle Glasflächen **im selben Mesh**. Die Glasflächen schließen im bisherigen komplexen Kollisionsmodell auch die Fensteröffnung. Fenstermaßwerk liegt wiederum in `Ribs_Smooth`. Ein sichtbares Fenster ist daher noch kein vollständiges separates Fensterasset.
- Die früheren Import-/Komponentenbelege setzen Hülle und Dach auf `UseComplexAsSimple` mit doppelseitiger Kollisionsgeometrie. Rippen und Hofkomponente haben keine Kollision. Der Lab-Boden trägt den Hof. Ein später frei platzierter Hof darf nicht ohne diese Voraussetzung als begehbar gelten.
- Die Quelldatei enthält einfache Projektions-UVs und für Dach/Rippen erzeugte geglättete Normalen. Finale UVs, Lightmap-UVs und hochwertige Oberflächen sind nicht nachgewiesen.
- `generate_elven_blatthof.py` erzeugt offline vier OBJ-Dateien und ein MTL/Manifest. Es importiert selbst keine Unreal-Assets und ist **kein Hausbau- oder Siedlungsgenerator**. Lokale, ignorierte MCP-Skripte erledigten Import, Materialzuordnung, Blueprint-Aufbau und Platzierung.
- Keine elfischen PCG-Graphen oder allgemeine Baukastenlogik in den untersuchten Quellen/Referenzen nachgewiesen. `FantasyLifeRPG.uproject` deklariert PCG nicht ausdrücklich. Das beweist nicht, dass PCG engineweit oder indirekt deaktiviert ist; Aktivierungszustand später im korrekten Editor prüfen. In dieser Phase nichts aktivieren.

## 4. Modularisieren, ohne die Stilstudie zu verlieren

### 4.1 Drei getrennte Ebenen

| Ebene | Inhalt | Bestandsbezug und Ziel |
| --- | --- | --- |
| **Strukturelle Bauteile** | Bodenfelder, Wandfelder mit echten Öffnungen, Dachabschnitte, Endabschlüsse; Stützen als konstruktiv aussehende Architektur | Definieren geschlossene Hülle und begehbare Räume. Keine neue physikalische Gebäudestatik vorausgesetzt |
| **Dekorative Elemente** | Fenstermaßwerk, Portalzier, Zierbänder, Dachadern, Beete/Hofausstattung | Nur getrennt, wenn Austausch, Sichtbarkeit oder Wiederholung davon profitieren; feine Adern als Gruppe am Dach behalten |
| **Gebäude-Prefabs** | Vollständige geprüfte Hauszusammenstellungen einschließlich Eingang und optionalem Hof | Bestehendes `BP_ElvenBlatthof_Study` bleibt erhalten. Spätere modulare Haus-Prefabs speichern eine Zusammenstellung derselben Module |

Eine Funktionstür bleibt ein Gameplay-Actor; ein statisches Fenstermaßwerk wird kein eigener tickender Blueprint. Modulare Herkunft und Laufzeitdarstellung dürfen sich unterscheiden: dieselben Module können später einzeln im Lab, instanziert in einer Siedlung oder gebündelt als Fernansicht verwendet werden.

### 4.2 Bevorzugte Ableitung aus der Quelle

1. Bestehenden Generator und vorhandene Hausassets unverändert als Referenz belassen. Bei späterer Freigabe einen gesonderten Modul-Exportpfad vorsehen.
2. Die vorhandenen Funktionen für Ringsektoren, Dachwölbung, Röhren/Stützen und Maßwerk weiterverwenden. Künftig gezielt nach Funktion sammeln: Boden, Innenwand, Außenwand, Dach, Stützen und Ausstattung. Neue Exporte mit eigenem Pivot, eindeutiger Kategorie und definierten Endprofilen erzeugen.
3. Zuerst **eine feste Radiusfamilie** testen. Unterschiedliche Winkel und Fenster-/Türvarianten verwenden dieselben Anschlüsse. Eine Änderung des Radius verlangt eine eigene Geometriefamilie; nicht durch nichtuniforme Actor-Skalierung erzwingen.
4. Neue Module unter einem ergänzenden Pfad wie `/Game/Art/Architecture/ElvenBlatthof/Modular/` ablegen. Alte Pfade nicht verschieben oder überschreiben. Bestehende Materialinstanzen direkt referenzieren.
5. Erst nach einem bestandenen Anschlussversuch Details und weitere Typen ergänzen. Nicht sofort das ganze Haus neu modellieren.

**Kritische Dachbesonderheit:** Die aktuelle Dachhöhe enthält `85 * abs((a-90)/125)**3`. Sie hängt vom absoluten Hauswinkel ab. Ein beliebiger ausgeschnittener 30°-Abschnitt lässt sich deshalb nicht einfach wiederholen: Höhen, Endprofile, Rippen und Dach-Wand-Füllflächen würden nicht durchgehend passen. Für ein wiederholbares Mitteldach muss dieser Längsverlauf vereinheitlicht und eine separate angehobene Endform geplant werden. Querwölbung, Farben und breite Blattwirkung können aus der Quelle übernommen werden. Die veränderte Silhouette ist vor einer Serienproduktion im Lab zu beurteilen. Bestehende 6°-Blattüberlappungen nicht ungeprüft auf jeden Modulstoß übertragen.

### 4.3 Alternative: vorhandene Meshes in einem DCC-Werkzeug bearbeiten

Ein gezielter Blender-Versuch an einer Kopie ist möglich, aber nicht als verlustfreie oder automatisch einfachere Zerlegung zugesichert. Die OBJs enthalten keine semantischen `o`-/`g`-Bauteilgruppen; der Export schreibt je Fläche eigene Vertexeinträge. „Nach losen Teilen trennen“ kann daher viele einzelne Flächen statt brauchbarer Bauteile erzeugen. Vor einem solchen Weg wären kontrolliertes Verschweißen, Auswahl nach Lage/Material und die Prüfung von Normalen und UVs erforderlich.

Materialtrennung hilft nur teilweise: Stone isoliert im Shell-Quellmesh den Boden, aber Ivory enthält viele Wände und Dachfüllflächen; Timber/Bronze im Rippenmesh verbinden mehrere Funktionen. Schnitte benötigen häufig neue Abschlussflächen, Kollisionskörper, UV-Ränder und Pivots. Gerade die Dachenden und gebogenen Fenster sind keine kostenfreien Ausschnitte. Empfehlung: zunächst ein repräsentatives Wandfeld und ein Dachprofil aus der Quelle ableiten; DCC-Nachbearbeitung dort einsetzen, wo das Ergebnis tatsächlich davon profitiert.

## 5. Vorgeschlagenes Maß-, Pivot- und Anschlusssystem

### 5.1 Gemeinsame Regeln

| Regel | Vorschlag für den ersten Baukasten |
| --- | --- |
| Einheit | 1 UU = 1 cm; Export-/Importmaßstab mit 100-cm-Referenzkörper prüfen |
| Welt-/Gebäuderaster | Gebäudeursprung und gerade Bauteile in 100-cm-Schritten, Modellier-Arbeitsraster 10 cm; bestehende Sondermaße ausdrücklich erhalten |
| Bodenbezug | Begehbare Oberkante Z = 0, erste Bodenplatte 12 cm nach unten; Anschlussflächen ohne Höhenversatz |
| Wandkrone | 280 cm passend zum Haus; Dach-Wand-Abschluss zusätzlich erforderlich. Das vorhandene 300-cm-Testwandmesh ist damit kein austauschbares Wandfeld |
| Transformation | Neue Module bei Skalierung `(1,1,1)`; keine negative oder nichtuniforme Skalierung. Links-/Rechtsformen bei Bedarf explizit exportieren |
| Gerade Teile, später | Wandbreiten 400 cm, Ergänzung 200 cm; Wanddicke 20 cm; Boden 400 × 400 bzw. 400 × 200 cm. Eckpivot unten, X entlang der Wand, Y zur Innenseite, Z oben |
| Bogenfamilie v1 | Boden R240…650, Innenwand R245…265, Außenwand R630…650; regulärer Winkel 30°, Eingangsfeld 60° |
| Bogenrotation | Reguläre Anschlussänderung 30°; genaue Translation über Anschluss-Transforms. Gebäude als Ganzes frei ausrichtbar |

**Ein einheitlicher Vertrag bedeutet nicht, alle organischen Punkte auf ein kartesisches Raster zu zwingen.** Bogenanschlüsse liegen rechnerisch außerhalb des 10-/100-cm-Rasters. Nur den Gebäudeursprung auf das Weltraster setzen; anschließend die Bogenanschlüsse exakt verwenden. Gerades Raster und Bogenfamilie sind ohne eigens modelliertes Übergangsmodul nicht austauschbar.

### 5.2 Bogenpivot und exakte Anschlüsse

Alle zusammengehörigen Bogenlagen verwenden denselben Referenzpunkt: **Startpunkt auf R = 255 cm, Z = 0**, also auf der Mittellinie der hofseitigen Wand. Dadurch lassen sich Boden, Innen-/Außenwand und Dach mit demselben Transform stapeln, obwohl ihre sichtbaren Bounds verschieden sind. X zeigt dort tangential in zunehmende Bogenrichtung, Y radial zum Kreismittelpunkt, Z nach oben. Der Kreismittelpunkt liegt lokal bei `(0,255,0)`.

Für einen Winkel θ liegt der Endreferenzpunkt lokal bei:

```text
A_Position = (0, 0, 0)
B_Position = (255 * sin(θ), 255 * (1 - cos(θ)), 0)
B_Tangente = um θ gegen die Starttangente gedreht
```

Für 30° ergibt das B ≈ `(127,500; 34,164; 0)` cm, für 60° B ≈ `(220,836; 127,500; 0)` cm. Diese gerundeten Zahlen dienen der Erklärung; die späteren Anschlussdaten müssen die berechneten Werte ohne fortlaufendes manuelles Runden speichern. Der 30°-Sektor hat außen ungefähr 336 cm Sehnenbreite und innen am Bezugsradius 132 cm Bogenlänge. Das ist ein Wand-/Raumfeld, kein winziger Zierstreifen.

Benannte Anschlussrahmen `Join_A` und `Join_B`: lokale X-Achse zeigt **aus dem Modul heraus**, Z bleibt oben. A zeigt entgegen der Starttangente, B entlang der Endtangente. Beim Fügen fallen Positionen und Z-Achsen zusammen, die X-Achsen zeigen gegeneinander. Der Einbau ergibt sich aus Gegenanschluss plus 180° Drehung um Z und inverser Transform des eigenen Anschlusses. Das gilt auch bei gedrehtem Gebäude; keine Addition gerundeter Weltkoordinaten.

Die Anschlussebene umfasst ein **Profil**, nicht nur einen Punkt: Bodenhöhe, Wandradien/-dicke, Dachquerschnitt, Materialkante und Kollisionsende müssen zusammenpassen. Ein Anschlussdatensatz kann im Mesh über Sockets und später zusätzlich in einem Modulkatalog beschrieben werden. [Unreal-Sockets unterstützen benannte Anheftpunkte](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-sockets-with-static-meshes-in-unreal-engine); die Gebäuderegeln und Kompatibilitätsprüfung bleiben eigene Planungslogik.

### 5.3 Übergänge, Abschlüsse und Toleranzen

- Reguläre Wände enden auf der vereinbarten radialen Schnittebene, ohne versehentliche Winkelüberlappung. Endflächen dürfen für eigenständige geschlossene Meshes vorhanden sein; koplanare Außenflächen und doppelte Zierbänder vermeiden.
- Die Dachmodule benötigen ein wiederholbares Querprofil und eigene Wandanschluss-Schürzen/Füllflächen bis Z = 280. Eine plane Wandkrone allein dichtet das vorhandene Blattdach nicht ab.
- Radiale Hausabschlüsse schließen den freien Bereich zwischen Innen- und Außenwand, ungefähr 365 cm, mit 20 cm Dicke. Ein Giebel-/Füllprofil schließt bis zur Dachunterseite. Derselbe geometrisch beidseitige Abschluss kann an beiden Enden stehen; Anschlussrichtung/Belegung je Instanz dokumentieren.
- Ein 30°-Feld erzeugt bereits eine Richtungsänderung. Ein zusätzlicher 90°-Eckstein gehört nicht an jeden Bogenstoß. Echte Innen-/Außenecken werden erst mit der geraden Ergänzungsfamilie benötigt.
- Für eine spätere Annäherung an den ursprünglichen 250°-Grundriss sind Sonderenden erforderlich: z. B. sechs 30°-Felder + ein 60°-Eingangsfeld + zwei 5°-Endbereiche. Diese 5°-Bereiche vorzugsweise in größeren Endbaugruppen bündeln. Der erste Versuch benötigt sie nicht.
- Vorschlag zur Abnahme: rechnerischer Anschlussversatz höchstens 0,1 cm, Winkelabweichung höchstens 0,1°; sichtbare Fuge/Z-Fighting zusätzlich aus Spielkamera prüfen. Dachüberdeckung nur als definierte Profilgeometrie, beispielsweise ein kurzer Überfalz, mit eindeutiger Eigentümerschaft. Keine pauschale Überlappung aller Wände als Fehlerkaschierung.

## 6. Priorisierte Asset-Liste

**P0:** kleinster brauchbarer, stilnaher Bogenbaukasten. **P1:** Varianten und stärkere Nähe zum Referenzhaus. **P2:** Erweiterung erst nach bestandenem P0/P1-Versuch. Alle Größen in cm; neue Namen sind Arbeitsnamen. Kein Eintrag mit ABLEITUNG/NEU existiert bereits als fertiges Modul.

| Prio | Kategorie / vorgeschlagener Name | Maß / Anschluss | Status und Wiederverwendungsweg |
| --- | --- | --- | --- |
| P0 | Boden `SM_EB_Floor_R240_650_A30` | Ringsektor 30°, R240…650, Dicke 12; Oberkante 0 | **ABLEITUNG** aus `shell.arc`, separat mit einfacher Bodenkollision |
| P0 | Innenwand geschlossen `SM_EB_WallInner_R255_A30_H280` | R245…265, 30°, Dicke 20, Höhe 280 | **ABLEITUNG** aus heller Bestandswand; Ivory weiterverwenden |
| P0 | Außenwand geschlossen `SM_EB_WallOuter_R640_A30_H280` | R630…650, 30°, Dicke 20, Höhe 280 | **ABLEITUNG**; keine erzwungene Wiederverwendung der anders gekrümmten Innenwand |
| P0 | Eingangsfeld `SM_EB_WallInner_Entry_A60_H280` | Gleiche Innenradien, 60°; mittige Türöffnung passend zum vorhandenen Rahmen, Blatt 120 × 220 | **ABLEITUNG** aus Eingang samt Portalzier; ersetzt genau zwei innere 30°-Wandfelder. Boden/Dach bleiben im 30°-Takt |
| P0 | Außenwand mit Fenster `SM_EB_WallOuter_Window_A30_H280` | Außenradien wie oben; mittig 18° Fensterzone, Brüstung 75, Fensterhöhe 165 | **ABLEITUNG** aus Bestandsfenster; Rahmen/Glas/Maßwerk für den ersten Test als gemeinsame Fensterwand, echte Wandöffnung |
| P0 | Mitteldach `SM_EB_LeafRoof_R215_695_A30` | 30°, R215…695, Blattdicke 12; Querwölbung ungefähr 155 über 300 | **ABLEITUNG mit Profilanpassung**: wiederholbarer Längsverlauf, geschlossene Ränder und Wandanschluss-Füllflächen; breite Mittelrippe/feine Adern zunächst als Gruppe integriert |
| P0 | Radialabschluss `SM_EB_EndWall_Radial_D365` | Freie radiale Breite etwa 365, Dicke 20, Wandzone 280 plus passendes Dachfüllprofil | **ABLEITUNG/NEUE Anschlussgeometrie**; schließt beide Hausenden ohne Loch im Dachanschluss |
| P0 | Verzweigtes Stützenpaar `SM_EB_SupportPair_R247_644_H285` | Paar an den beiden Wandzonen, etwa Z8…293, mit vereinbartem Astfreiraum | **ABLEITUNG** aus bestehenden Röhrenformen; ein zusammenhängender Satz je Feldanschluss, nicht ein Actor je Ast |
| P0 | Funktionstür und Rahmen | Blatt 120 × 12 × 220, dokumentierter Rahmenaußenumfang 144 × 232 | **VORHANDEN**: `BP_PrototypeDoor` und `BP_PrototypeDoorFrame` direkt einsetzen, Einheitsskalierung der Einbettung beachten |
| P0 | Farb-/Oberflächenpalette | Neun bestehende `MI_Blatthof_*` | **VORHANDEN**, keine neue Materialbibliothek für den Versuch |
| P1 | Eigenständiger Fenstereinsatz | 18°-Profil R637…654, Höhe 165; passend zum Außenwandanschluss | **ABLEITUNG** aus Glas/Maßwerk, nur bei gewünschtem Austausch herauslösen; keine generische flache Scheibe für alle Radien |
| P1 | Separater Portalbogen | Bestand etwa 170 breit einschließlich Röhrendicke, Spitze etwa Z278 | **ABLEITUNG** aus Portalrohr; vom Eingang unabhängig nur wenn Varianten dies benötigen |
| P1 | Dach-Endbaugruppe links/rechts | Zunächst 30°-Endfeld; später mit integrierter 5°-Ergänzung | **ABLEITUNG/NEU**: angehobene Blattspitzen und sauberer Abschluss statt Skalieren des Mitteldachs |
| P1 | Sockel-/Kronenband | Je 30° zur passenden Innen-/Außenradiusfamilie; Bestand Z4…19 bzw. Z266…282 | **ABLEITUNG** aus `Ribs`; für P0 optional am Wand-/Dachmodul belassen |
| P1 | Hofweg und Brückenplatte | Wegbreite 150; Brücke etwa 170 × 140 | **ABLEITUNG** aus `Courtyard`; eigene tragende Kollision erforderlich, Wasser/Garten separat optional |
| P1 | Zweite sichtbare Wand-/Dachvariante | Identisches Profil, gleiche Maße/Slots, alternative Zierverteilung | **NEU auf vorhandener Formbasis**, erst nach geschlossenen Anschlüssen; keine Radiusänderung als Zufallsvariante |
| P1 | Modulares Haus-Prefab A/B | Geprüfte 120°- und 150°-Zusammenstellung desselben Radiuskits | **NEU**, nur gespeicherte Anordnung bestehender Module plus Funktionstür; kein universeller Generator |
| P2 | Gerade Wand-/Bodenfelder | Wand 400/200 × 20 × 280; Boden 400 × 400/200 × 12 | **NEU/ABLEITUNG** derselben Gestaltung; vorhandene 400 × 20 × 300 Testwand nur als Maß-/Importreferenz |
| P2 | Innen-/Außenecke, gerader Anschluss | 90°-Anschluss mit 20-cm-Wandprofil, H280; Verkleidung innerhalb eines definierten z. B. 40 × 40 Felds | **NEU**; erst mit gerader Familie, inklusive eigener Dach-/Bodenecke |
| P2 | Bogen–Gerade-Übergang | Gleiche Bodenhöhe und Wandkrone, expliziter Wechsel von Radius- zu geradem Profil | **NEU**; Anschlussform erst nach praktischer Erprobung festlegen |
| P2 | Weitere Radiusfamilie / Innenwände / Geschosse | Eigene Profile; Geschosshöhe und Treppen noch zu bestimmen | **NEU**, nicht Voraussetzung für den ersten Wohnhaustest |

P0 umfasst **acht neue Mesh-Typen** einschließlich Fensterwand und Stützenpaar, plus vorhandene Tür/Rahmen und Materialien. Das ist der vorgeschlagene erste Entscheidungsumfang, keine bereits begonnene Produktion. Für einen reinen Anschlussnachweis kann das Stützenpaar zuletzt kommen; für einen Stilvergleich ist es wertvoll.

## 7. Anschlussregeln, Varianten und Metadaten für spätere Generierung

### 7.1 Verbindlichkeit der Profile im vorgeschlagenen System

Ein Generator darf erst nach geometrischer Kompatibilität gewichten. Gleicher Stil oder ähnliche Bounds reichen nicht. Vorgeschlagene Regeln:

1. `KitId`, `InterfaceVersion`, Lage und Radius-/Profilfamilie müssen zusammenpassen. Innenwand R255 und Außenwand R640 sind verschiedene Lagen desselben Felds.
2. Winkelbilanz pro Lage: ein 60°-Eingang belegt zwei 30°-Zellen und verdrängt dort beide Innenwandfelder. Kein zusätzlicher geschlossener Wandabschnitt hinter der Tür. Außenwände, Boden und Dach werden unabhängig passend belegt.
3. Alle seitlichen Anschlüsse müssen durch ein Nachbarmodul oder einen passenden Endabschluss belegt sein. Dachanschlüsse brauchen Nachbardach oder Endprofil. Keine offenen Enden als zufälliger Varianteneffekt.
4. Dach-/Stützenvarianten müssen denselben Freiraumvertrag erfüllen. Dekor darf eine Türöffnung, ein Fenster oder einen Laufweg nicht verdecken. Ein Stützen-/Zierstoß gehört genau einem Feld, etwa dessen A-Seite; die freie B-Seite des letzten Felds erhält einen Abschluss. Keine doppelten Stützen an jedem Stoß.
5. Strukturelle Form nicht zufällig skalieren oder verbiegen. Für das erste Kit ein Radius und ein Dachquerprofil. Farben/Zierdetails dürfen nur innerhalb kompatibler Varianten wechseln.
6. Eingang besitzt getrennte Daten für Durchgang, Türanschlag, Interaktionsposition und notwendigen Bewegungs-/Kamerafreiraum. Die aktuelle Tür schaltet sofort; eine spätere Schwenktür würde zusätzliche Freiraumprüfung benötigen.

### 7.2 Kleiner, versionierbarer Modulkatalog – zunächst nur planen

Später genügt zunächst eine DataTable oder ein DataAsset-Katalog; kein neues Framework erforderlich. Laufzeitrelevante Daten nicht ausschließlich in Editor-Metadaten-Tags ablegen. Mesh-Sockets und Katalog dürfen nicht unterschiedliche Anschlusskoordinaten pflegen: eine Quelle definieren und daraus exportieren/validieren.

| Metadaten | Zweck |
| --- | --- |
| `ModuleId`, `KitId`, `InterfaceVersion`, `SourceRevision` | Stabile Identität, Anschlussversion und nachvollziehbare Herkunft |
| `Category`, `Layer`, `Mesh` oder `ActorClass` | Struktur/Dekor/Prefab, Boden/Wand/Dach/Gameplay; Soft-Referenz auf Asset |
| `FootprintType`, `RadiiCm`, `AngleDeg`, `HeightCm`, `FloorZCm` | Tatsächliche Belegung; Bogenwerte statt vorgetäuschter rechteckiger Rastermaße |
| `Connections[]` | Name, lokale Transform, Profil-ID, Anschlussrolle, erlaubte Gegenprofile und Belegungszustand |
| `OccupiedCells`, `PlacementBounds`, `ClearanceVolumes` | Winkelzellen, Platzierungsprüfung, Dachüberstand und freie Tür-/Laufbereiche getrennt |
| `VariantSet`, `Weight`, `AllowedRotations`, `MirrorPolicy` | Austauschbare Formen, Auswahlgewicht, erlaubte Ausrichtung; standardmäßig keine Spiegelung |
| `MaterialSet`, `StableSlotNames`, `CollisionPolicy`, `RenderPolicy` | Zusammenpassende Materialien, Kollision sowie statische Instanz oder Gameplay-Actor |
| `BuildingId`, `ModuleInstanceId`, `Seed`, `CatalogVersion` | Reproduzierbare Zusammenstellung und spätere Zuordnung interaktiver Elemente |

Beispiel **vorgeschlagener** Katalogeintrag, keine angelegte Unreal-Struktur:

```yaml
ModuleId: EB.Wall.Inner.Solid.A30.v1
KitId: EB.Blatthof.R255_R640
InterfaceVersion: 1
Category: Structure
Layer: InnerWall
AngleDeg: 30
RadiiCm: [245, 265]
HeightCm: 280
FloorZCm: 0
OccupiedCells: 1
ProfileId: EB.InnerWall.R255.T20.H280.v1
Connections:
  - {Name: Join_A, Socket: Join_A, Role: Start}
  - {Name: Join_B, Socket: Join_B, Role: End}
MirrorPolicy: Forbidden
RenderPolicy: StaticInstance
```

Für vollständige Gebäude-Prefabs zusätzlich Eingangstransform, Gesamtbelegungsfläche einschließlich Dach/Hof, Gebäudebounds, Bodenauflage und freie Annäherungsroute vorsehen. Damit kann später eine Siedlungsplanung Häuser platzieren, ohne die einzelnen Wandregeln erneut zu lösen.

### 7.3 Unreal-PCG als spätere Ausgabestufe

Geplante Trennung: **gültiger Gebäudeplan → Modul-/Transformliste → Darstellung**. PCG kann später solche Punkte/Attribute übernehmen und statische Meshes auswählen/platzieren. Der [Static Mesh Spawner und die Attributoperationen](https://dev.epicgames.com/documentation/en-us/unreal-engine/procedural-content-generation-framework-node-reference-in-unreal-engine) bieten dafür vorhandene Unreal-Bausteine. Aus ihrer Existenz folgt kein automatisches Verständnis von Wänden, Radien oder Raumabschlüssen; diese Regeln müssen vorher erfüllt sein.

Statische Felder nach Mesh, Material und Kollisionskonfiguration gruppieren; Tür-Actors gesondert mit stabiler ID erzeugen. PCG erhält beispielsweise `ModuleId`, Meshreferenz, Transform, Materialvariante, `BuildingId` und Seed. Assetpfade/Datentypen und Actor-Ausgabe erst am tatsächlichen UE-5.8-Graphen verifizieren. Keine Forderung nach Geometry-Script-Interop allein für das Platzieren bekannter Module; Mesh-Sampling wäre ein eigener Anwendungsfall. Für die erste Baukastenprüfung ist PCG überhaupt nicht erforderlich.

## 8. Performance und Erweiterbarkeit

| Thema | Konsequenz für die Planung |
| --- | --- |
| Modulgröße | Wandfelder und ganze Blatt-/Stützengruppen statt einzelner Äste/Adern; Dekor nur separat, wenn Austausch oder Sichtbarkeit dies rechtfertigt |
| Instanzen | Wiederholte statische Module eignen sich für ISM; HISM abhängig von Sichtweiten-/LOD-Verhalten prüfen. Gleiches Mesh in vielen Blueprint-Komponenten garantiert noch kein gewünschtes Instancing. [Epic beschreibt ISM als Gruppierung identischer Meshes](https://dev.epicgames.com/documentation/en-us/unreal-engine/instanced-static-mesh-component-in-unreal-engine) |
| Materialslots | Bestehende Palette zunächst übernehmen, Slots stabil halten; unnötige Slots vermeiden. Erst bei größerer Szene Textur-/Trim-/Atlasstrategie beurteilen |
| Kollision | Neue Böden/Wände mit einfachen Boxen bzw. mehreren konvexen Segmentkörpern; Fenster-/Türöffnungen freihalten. Ein einzelner konvexer Körper über dem ganzen konkaven Haus würde Hof/Durchgänge schließen |
| Dach/Schmuck | Lauf- und Kamerabereiche sinnvoll blockieren; feine Adern/Blätter ohne Kollision. Bestehendes `UseComplexAsSimple` als Prototypzustand erhalten, nicht zum Standard aller neuen Module machen. [Unreal unterstützt einfache Kollisionskörper für Static Meshes](https://dev.epicgames.com/documentation/unreal-engine/setting-up-collisions-with-static-meshes-in-unreal-engine?lang=en-US) |
| LOD/Nanite | Gegenwärtig nicht neu geprüft. Zuerst detailreiche Rippen vereinfachen und aus Distanz vergleichen; Nanite ersetzt keine Actor-, Material- oder Kollisionsplanung |
| Sichtbarkeit/Fernansicht | Modulgrenzen nicht unnötig fein. Später HLOD oder vereinfachte Gebäudeansichten prüfen; Originalmodule als bearbeitbare Quellen erhalten |
| Interaktion | Nur Türen und spätere tatsächlich interaktive Teile als Gameplay-Actors. Keine Actor-/Tick-Kosten pro Zierobjekt |
| Persistenz | Seed, Katalogversion und stabile Gebäude-/Modul-IDs vorbereiten; noch keine Persistenz-/Netzwerkarchitektur festlegen |

Für P0 kein unbelegtes FPS-, Dreiecks- oder Draw-Call-Budget festschreiben. Nach dem einzelnen Haus einen begrenzten Vergleich mit beispielsweise 10 und 50 Wiederholungen bei identischer Kamera/Lichtumgebung vorsehen: CPU-/GPU-Zeit, Actor-/Komponentenzahl, Material-/Renderaufwand und Kollisionskosten vergleichen. Das ist eine spätere Messung, keine in dieser Phase erledigte Prüfung und kein Freibrief für Siedlungsmaßstab.

## 9. Kleinster sinnvoller Folgeversuch nach gemeinsamer Auswahl

**Ziel:** Mit den acht P0-Mesh-Typen zwei geschlossene, begehbare kleine Bogenhäuser bauen, ohne Generatorimplementierung. Die bestehende Stilstudie steht daneben als visueller Maßstab.

1. **Ein Anschlussmuster zuerst:** Boden30 + Innenwand30 + Außenwand30 + Mitteldach30 zweimal fügen. Wand-Dach-Füllung, Normalen, Materialkanten und Kollision prüfen. Erst wenn dieser Stoß passt, Eingang, Fenster und Endabschluss ableiten. Das teure Dachrisiko wird so früh geklärt.
2. **Haus A mit 120°:** vier Boden30, vier Außenwandfelder (z. B. drei geschlossen, eins mit Fenster), hofseitig ein Eingang60 plus zwei geschlossene Innenwand30, vier Dach30, zwei Radialabschlüsse, passend verteilte Stützenpaare und die vorhandene Funktionstür mit Rahmen. Eingangsfeld ersetzt zwei innere Wandfelder. End-/Dachfüllungen müssen vollständig schließen; Hofdekoration ist nicht erforderlich.
3. **Haus B mit 150°:** je ein zusätzliches Boden30-, Außenwand30-, Innenwand30- und Dach30-Feld sowie passender Stützstoß. Dieselben Meshassets verwenden. So belegt der Versuch echte Kombinierbarkeit und nicht nur die Rekonstruktion einer einzigen Zusammenstellung.
4. **Einbau zunächst manuell:** Anschlusstransforms bzw. Sockets verwenden, zusammengehörige Lagen auf demselben Feldtransform platzieren. Eine einfache geprüfte Hauszusammenstellung kann anschließend als neues Prefab gespeichert werden; noch kein parametrisierter Hausgenerator nötig.
5. **Labprüfung nach Freigabe:** separate markierte Testfläche neben der unveränderten Studie verwenden. Einfache Materialien direkt wiederverwenden; Tür und Rahmen beibehalten. Das vorhandene Lab muss erst für diesen Folgeauftrag ausdrücklich geändert werden, nicht in Phase 1.

Abnahme für den Versuch:

- Maße, Pivot und Einheitsskalierung stimmen nach Import; beide Hausgrößen verwenden dieselben Module. Verschieben und Drehen des Gesamthauses erzeugt keine Anschlussfehler.
- Alle Boden-, Wand- und Dachstöße sind geschlossen; kein sichtbares Z-Fighting, keine doppelten Stützen und keine helle Spalte zwischen Wandkrone und Dach.
- Begehung mit dem tatsächlichen Spieler in beide Richtungen, Tür offen/geschlossen, Kamera an Bogenwänden, Fenstern und Enden. Der C++-Standard setzt Kapselradius 42 und Halbhöhe 96 cm; die tatsächlich im Spieler-Blueprint wirksame Kapsel vor der Prüfung auslesen. Linienabfragen allein reichen nicht.
- Kollision trägt den Boden auch über einem freien Prüfbereich oder mit entsprechenden Bodenabfragen; der Lab-Untergrund darf fehlende Modulkollision nicht verdecken. Innenwand, Fenster und Dach verhalten sich wie vorgesehen, Türöffnung wird nicht von automatischer konvexer Kollision verschlossen.
- Vorhandene E-Interaktion, Öffnen/Schließen, Aktionstext und Hervorhebung funktionieren. Rahmenblatt nicht doppelt skalieren; Türbedienung auch von innen prüfen.
- Materialvariante an einer Instanz beeinflusst keine andere unbeabsichtigt. Farben, Dachblattwirkung und verzweigte Stützen aus Spielkamera mit der alten Studie vergleichen.
- Neue Assets/Prüfzusammenstellung ausdrücklich speichern und erneut laden; vorhandene Lab-/Toolbox-Tests ergänzend ausführen. Diese Tests allein beweisen noch keine Modulnahtqualität.

Dieser Versuch umfasst bewusst noch keinen kompletten 250°-Blatthof, keine Möblierung, keinen Wasserlauf, keine weiteren Geschosse und keine Siedlung. Nach bestandener Abnahme entscheiden wir über Dach-Endformen, austauschbare Fenster und eine zweite kompatible Variante. Das begrenzt die Zusatzarbeit, ohne den eigentlichen Anschluss- und Wiederverwendungsnachweis zu überspringen.

## 10. Risiken, offene Entscheidungen und durchgeführter Umfang

| Punkt | Vor einer Umsetzung zu klären / vorgeschlagener Umgang |
| --- | --- |
| Mitteldach verändert Längssilhouette | Erst zwei Dachfelder im Lab beurteilen. Quelle/Formensprache übernehmen, alte Studie als Vergleich bewahren |
| Feste Radien begrenzen Hausformen | Bewusste Grenze für v1; andere Radien und gerade Übergänge erst nach dem Basistest |
| Viele eng gebündelte Details | Zuerst Stützen-/Fenster-/Dachgruppen ableiten; keine automatische Einzelteilzerlegung versprechen |
| Rahmenöffnung und Fensterkollision | Reale lichte Maße messen; Geometrieöffnung und Kollisionsöffnung getrennt prüfen |
| Ungeprüfte Editor-/Renderdaten | Korrekten Editor-Kontext wiederherstellen und vor Import Reference Viewer, Slots, UVs, LOD/Nanite und Kollision lesen |
| Produktionsqualität | Finale Texturen, UVs, Lightmaps, LOD-/Nanitewahl, Packaging, Mehrspieler und große Szenen bleiben eigene spätere Prüfungen |

**Vorgeschlagene nächste Entscheidung:** Freigabe eines ersten Anschlussmusters und danach der acht P0-Mesh-Typen mit festen Bestandsradien. Es wurde noch nichts davon implementiert. Keine Änderungen an `.uasset`, `.umap`, Blueprints, Generatoren, Gameplay, Konfiguration oder Worldbuilding; keine Commits, Staging- oder Push-Aktionen.

### Projektquellen

- [Stilstudie und bisherige Prüfgrenzen](ELVEN_BLATTHOF_STUDY.md)
- [Bestehende Asset-Pipeline, Maße und Lab→Sandbox-Ablauf](ASSET_PIPELINE.md)
- [Technischer Ist-Zustand](../TECHNICAL_STATUS.md)
- [Entscheidungsregister](../DECISIONS.md) und [elfische Kultur/Architektur](../worldbuilding/voelker/elfen/kultur.md)
- [Versionierte Geometriequelle](../../Tools/Prototype/generate_elven_blatthof.py)

Lokale historische Belege: `Saved/ElvenBlatthofSources/manifest.json`, `Saved/InteractionDev/elf_import_result.json`, `elf_refine.py`, `elf_refresh_result.json`, `elf_verify_result.json`, `elf_house_final_audit.json`, `elf_pie_checks.json`, `elf_house_tests.json`, `elf_house_final_overview.png`. Frühere `elf_inspect_result.json` enthält noch die später korrigierte doppelte Türskalierung und ist kein abschließender Zustand; maßgeblich sind die anschließenden Korrektur-/Prüfbelege. Externe Unreal-Referenzen wurden am 22. Oktober 2026 geprüft und sind bei den jeweiligen technischen Aussagen verlinkt.

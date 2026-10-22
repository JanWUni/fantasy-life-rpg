# Developer Toolbox V1

Unreal Engine 5.8, Entwicklungsprototyp. Die Toolbox wird am vorhandenen `BP_PrototypePlayerController` aktiviert. Dadurch steht sie in `Lvl_Prototype_01`, `Lvl_EnvironmentTest_01`, `Lvl_AssetLab` und `Lvl_WorldSandbox` bereit, ohne diese Karten zu verändern. Sie ist kein spielbares Admin-/Berechtigungssystem.

## Bedienung

**F6** öffnet und schließt das UMG-Panel. **ESC** schließt ein geöffnetes Panel ebenfalls. F7 wurde geprüft: Der Engine-Blueprint-Editor belegt die Taste mit `CompileBlueprint`; der Behavior-Tree-Vergleich verwendet sie ebenfalls. Deshalb wird die erlaubte Alternative F6 eingesetzt. Bare F6 ist in den geprüften Projekt-/Editorbelegungen frei; vorhandenes Ctrl+F6 bleibt unberührt. F1 und bestehende Kontexte/Belegungen wurden nicht geändert.

Die Welt läuft bei geöffnetem Panel weiter. Der Mauszeiger ist frei; Charakterbewegung, Springen, Interaktion und Kameraeingaben werden während der Bedienung unterdrückt. Beim Schließen werden die vom Panel gesetzten Eingabesperren aufgehoben, der bisherige Cursorzustand und der Spielfokus wiederhergestellt. Bereits von anderen Funktionen gesetzte Bewegungs-/Blicksperren bleiben erhalten.

Gewählte Werkzeuge bleiben beim Schließen aktiv, damit man tatsächlich fliegen oder die freie Kamera bedienen kann. Sie werden über ihre Schaltfläche oder **Werkzeuge zurücksetzen** beendet. Bei PIE-Ende, Komponentenabbau und Weltwechsel werden temporäre Eingaben, Kamera, Effekte und Charakteränderungen aufgeräumt.

| Bereich | Bedienung |
| --- | --- |
| Flug | WASD horizontal, Maus zum Blicken, Leertaste aufwärts, linke Strg abwärts |
| NoClip | Unabhängiger Schalter; deaktiviert Actor-Kollision. Ohne Flug horizontal bei konstanter Höhe; mit Flug auch vertikal. Intern nutzt beides den vorhandenen CharacterMovement-Flugmodus. |
| Tempo | Flug und Kamera getrennt zwischen 100 und 5000 cm/s; linke oder rechte Shift halten: dreifaches Tempo in Flug/NoClip/Kamera, doppeltes ursprüngliches Lauftempo am Charakter |
| Freie Kamera | Eigener temporärer Kamera-Actor, WASD horizontal, Maus, Leertaste/Strg vertikal. Der Charakter bleibt besessen; seine Steuerung wird abgefangen. |
| Effekte | Bestehendes Niagara-Asset auswählen und am Spieler oder an einer per Sicht-/Bodenabfrage ermittelten Testposition auslösen. Stoppen entfernt nur durch diese Toolbox erzeugte Systeme. |
| Simulationen | Vorhandene NPC-Routen stoppen oder an Wegpunkt 1 neu starten. Ohne passende Route bleiben die Schaltflächen deaktiviert. |

Flug und NoClip stoppen beim Loslassen aller wirksamen Bewegungstasten sofort, statt durch die Standard-Flugbremsung nachzugleiten. Die erhöhte Beschleunigung während dieser Modi macht Richtungswechsel und Shift-Tempo unmittelbar spürbar. Beim Loslassen von Shift wird die Fluggeschwindigkeit direkt auf das eingestellte Normaltempo begrenzt. Die freie Kamera bewegt sich ebenfalls nur bei Bewegungseingabe und blickt mit Maus nach unten auch nach unten (keine invertierte Y-Achse).

Beim Abschalten von NoClip wird die volle Spielerkapsel gegen die Umgebung geprüft. Falls die aktuelle Position blockiert ist, wird ein zuvor gespeicherter freier Punkt verwendet. Gibt es keinen freien geprüften Punkt, bleibt NoClip aktiv und eine Meldung fordert zum Herausbewegen auf. Es wird kein neues Respawn-System eingeführt. Beim Abschalten von Flug werden ursprünglicher Bewegungsmodus, benutzerdefinierter Untermodus, Beschleunigung, Fluggeschwindigkeit und Actor-Kollision wiederhergestellt; Geschwindigkeit/Impulse werden bewusst angehalten. In der Luft setzt danach die normale CharacterMovement-Physik ein. Bodensprint verwendet die bestehende Charakterbewegung und verändert vorübergehend ausschließlich deren ursprüngliches Lauftempo; Loslassen, Menü, Werkzeugwechsel und Aufräumen stellen diesen Wert wieder her.

Die freie Kamera beginnt an der aktuellen Spielansicht. Beim Beenden werden vorheriges ViewTarget und ControlRotation wiederhergestellt. Die Charakterkamera folgt dann dem aktuellen Charakter; eine inzwischen physisch veränderte Charakterposition wird nicht zurückteleportiert. Am SpringArm und an den Gameplay-Kamera-Komponenten werden keine dauerhaften Werte geändert.

## Aufbau und Erweiterung

- `Development/DeveloperToolboxComponent.*`: Zustände, Laufzeitfreigabe, temporärer Enhanced-Input-Kontext, Eingabefokus, Bewegungs-/Kameraänderungen und Aufräumen. Die Standardkomponente ist deaktiviert; das Prototyp-Controller-Blueprint schaltet sie gezielt ein. Der Basiscontroller erhält nur dieses Subobjekt.
- `Development/DeveloperToolboxWidget.*`: UMG-WidgetTree mit drei Karten, Scrollbereich, Schaltflächen und Geschwindigkeitsfeldern. Es ruft die APIs der Komponente und Dienste auf; die eigentliche Steuerungslogik liegt nicht in der Oberfläche. `WidgetClass` ist für spätere eigene Widget-Unterklassen konfigurierbar.
- `Development/DeveloperEffectTester.*`: vorhandene `UNiagaraSystem`-Referenzen aus dem Blueprint-Katalog. Maximal acht aktive Testsysteme, getrennt von Gameplay-Effekten. Neue Beispiele als Eintrag mit Label und Soft-Referenz ergänzen; keine neuen Effektassets nötig. `Niagara` ergänzt die private Modulabhängigkeit.
- `Development/DeveloperScenario.*`: kleine Szenarioadapter. `ScenarioClasses` ergänzen; `CanRun`, `OnStart` und `OnStop` in einer C++-/Blueprint-Unterklasse implementieren. Die öffentliche Start-/Stop-Schnittstelle prüft zuvor die Freigabe. `Cleanup` muss eigene temporäre Änderungen zurücknehmen.
- `UDeveloperNPCRouteScenario`: verwendet ausschließlich `UWaypointMovementComponent::StartRoute/StopRoute`. Bei Reset wird der zuvor laufende/gestoppte Zustand der beeinflussten Routen wiederhergestellt. Ein Neustart setzt die Route wie die bestehende API auf Wegpunkt 1 zurück; exakte Timer-/Wegpunktfortsetzung wird nicht versprochen.

Die temporären Toolbox-Aktionen übernehmen WASD, Maus, Leertaste, Strg und Shift nur bei aktiven Werkzeugen oder geöffnetem Panel. Im Normalbetrieb bleiben die vorhandenen Enhanced-Input-Aktionen wirksam. Der Kontext wird nicht als neues Asset gespeichert und beim Abbau entfernt. Weitere Werkzeuge sollen bestehende Mechanik-Schnittstellen verwenden und Eingaben, Effekte sowie gespeicherte Zustände ausdrücklich aufräumen.

Konfigurierte Beispiele sind die unveränderten Assets `/Game/Variant_Combat/VFX/NS_Damage` und `/Game/LevelPrototyping/Interactable/JumpPad/Assets/NS_JumpPad`. Der Niagara-Dienst lädt ein ausgewähltes Soft-Asset bei Bedarf synchron. Ein erster Aufruf kann deshalb Lade-/Niagara-Kompilierungszeit benötigen; es wird keine latenzfreie oder vorgewärmte Effektbibliothek versprochen.

## Freigabegrenze

Bodensprint ist ebenfalls an die aktivierte Toolbox im Prototyp-Controller gebunden. Er legt keine neue globale Sprintbelegung in den Input-Assets an. Linke und rechte Shift teilen sich die temporäre Enhanced-Input-Aktion. Flug/NoClip erhöhen vorübergehend die vorhandene CharacterMovement-Beschleunigung und lesen Eingaben vor dessen Bewegungstick; beim Beenden wird auch diese Änderung zurückgenommen. Ohne wirksame Bewegungseingabe werden ausstehende Bewegung und Geschwindigkeit direkt gelöscht. Die normale Bodenbewegung behält ihre bisherige Beschleunigung und Bremsung.

`CanUse()` liefert in **Shipping stets false**. In anderen Konfigurationen werden zusätzlich explizite Blueprint-Aktivierung, eine gültige Spielwelt, ein lokaler PlayerController, Autorität und **NM_Standalone** verlangt. Flug, NoClip, Kamera, Effektauslösung und Szenariostart/-stopp prüfen diese Grenze auch ohne UI-Aufruf. In Netzwerksitzungen bleiben die Werkzeuge gesperrt, einschließlich Listen-Server. Es existieren keine Admin-RPCs oder clientseitig auslösbaren Serveraktionen.

Eine spätere Multiplayer-Freigabe erfordert ein serverseitiges Berechtigungskonzept und erneute Validierung je Aktion. Es genügt nicht, die Oberfläche einzublenden oder den NetMode-Check zu entfernen. Shipping enthält die Typen noch für stabile Blueprint-Referenzen, führt aber keine Toolbox-Eingabeeinrichtung oder freigegebenen Steuerungsaktionen aus.

## Nicht verfügbar in V1

NPC-Spawning, Tageszeit, Wetter, Zeitraffer und neue Simulationsereignisse sind als nicht verfügbar beschriftet. Es gibt keine neue NPC-KI, keine neue Effektbibliothek, keine Änderungen an Lore, Weltgestaltung, bisherigen Levels oder Startkarten.

## Manuelle Prüfung

1. In jeder der vier Karten PIE starten, Spielfenster fokussieren, F6 mehrfach öffnen/schließen. ESC auch bei fokussiertem Geschwindigkeitsfeld und geöffneter Auswahlliste testen. Ohne geöffnetes Panel behält ESC sein normales Editorverhalten.
2. Im Panel WASD, Leertaste, E und Maus bewegen: Charakter/Kamera sollen still bleiben, NPCs weiterlaufen. Danach normales Laufen, Springen, Kamera und E-Interaktionen prüfen.
3. Flug und NoClip einzeln und gemeinsam schalten, Tempo ändern, auf-/absteigen und Shift verwenden. NoClip in einer Wand abschalten und die Rückkehrposition beurteilen. Außenkanten der Sandbox bleiben offen.
4. Freie Kamera bewegen, Tempo ändern, mehrfach zur Figur zurückkehren. Wechsel mit aktivem Flug/NoClip und geöffnetem Panel prüfen.
5. Beide Effektpositionen und Stoppen aus verschiedenen Kamerawinkeln beurteilen. NPC-Routen im Environment-Level stoppen/neustarten; in Karten ohne NPC muss der Bereich als nicht verfügbar erscheinen.
6. Mit aktiver Kamera, Flug, NoClip, Effekten und Menü PIE beenden und erneut starten. Keine Zustände dürfen in die nächste Sitzung übernommen werden.

Automatisierte Ergebnisse und verbleibende Einschränkungen werden im [technischen Status](../TECHNICAL_STATUS.md) festgehalten. Packaging/Cooking, tatsächliche Shipping-Ausführung, Split-Screen, Controller-/Touchbedienung und spätere Multiplayer-Administration benötigen gesonderte Prüfungen.

## Geprüfter Stand vom 22. Oktober 2026

**Nachfolgende Steuerungsanpassung:** Die freie Kamera verwendet nun eine nicht invertierte Y-Achse. Flug/NoClip stoppen ohne Nachgleiten; beide Shift-Tasten erhöhen das Tempo, einschließlich Bodensprint. `FantasyLifeRPG.DeveloperToolbox.HandlingPIE` prüft beide Maus-Y-Richtungen, tatsächliche Geschwindigkeiten, Stillstand von Position und Velocity nach Loslassen, Shift-Rücknahme, Originalwerte nach Modusende sowie Sprint-Rücksetzung beim Menü/Abbau. Einzeltest nach Editorneustart **1/1 erfolgreich in 5,04 s**, anschließend die erweiterte vollständige Suite **14/14 erfolgreich in 78,10 s**. Editor-Build erfolgreich in 53,71 s ohne Compilerwarnungen. Bekannte Crowd-/Recast-Warnungen bleiben bestehen; keine Testfehler. Die Bedienhinweise wurden im gerenderten Panel kontrolliert. Das subjektive Maus-/Bewegungsgefühl bei längerer physischer Bedienung bleibt manuell zu beurteilen. Belege: `Saved/InteractionDev/toolbox_handling_build.log`, `toolbox_handling_tests_handling.json` und `toolbox_handling_tests_all.json`.

- Abschließender Editor-Build erfolgreich, ohne Compilerwarnungen.
- Gemeinsame Suite: **13/13 erfolgreich** in 73,03 s. Sie enthält alle acht bisherigen Projekttests und fünf neue Toolbox-Prüfungen.
- Anschließend ausschließlich die fünf neuen Tests um zweite Effektauslösung, genauen NoClip-Rückkehrpunkt und NPC-Rücksetzung ergänzt: **5/5 erfolgreich** in 10,54 s nach erneutem Editorneustart. Toolbox-Implementierung dabei unverändert.
- Ein vorheriger separater Kontrolltest direkt nach Editorneustart besteht in 18,98 s. Die Fixture wartet vor dem ersten Tastendruck auf die anfänglichen Spiel-/Eingabeframes (mindestens 0,35 s Weltzeit) und sendet dann genau einen F6-Druck; keine Wiederholung bei Fehlschlag.
- F6 über den PlayerController-/Enhanced-Input-Pfad, ESC über das tatsächlich fokussierte Slate-/UMG-Widget, UMG-Schaltflächen-Callbacks und SpinBox-Signale geprüft. Die Oberfläche wurde zusätzlich als gerendertes PIE-Fenster kontrolliert. Diese Automationen ersetzen keine vollständige physische Maus-/Tastaturprüfung aller Fokuszustände.
- Flug mit W/Leertaste/Strg, Shift-Limit, Geschwindigkeit, NoClip-Unabhängigkeit und Rückkehr aus dem Wandmesh, freie Kamerabewegung bei stillstehender Figur, Wiederherstellung von ViewTarget/ControlRotation, Effektauslösung an beiden Positionen, Instanzlimit/Stoppen, Backend-Sperre bei deaktivierter Toolbox und Aufräumen bestätigt.
- In allen vier Prototypkarten öffnen/schließen, passender Szenario-Verfügbarkeitsstatus und PIE-Ende mit aktivem Panel, Kamera, Flug, NoClip und Testeffekt geprüft. In der Umgebung Start/Stop der vorhandenen Route und Rücksetzen ursprünglich laufender sowie gestoppter Routen bestätigt.

Während der Entwicklung verursachte `DeactivateImmediate()` im Effekt-Aufräumcode einen Absturz: Niagara konnte dabei die autozerstörende Komponente synchron ungültig machen. Die Bereinigung hält jetzt eine lokale Referenz, schaltet AutoDestroy für den kontrollierten Abbau aus und prüft vor dem abschließenden Zerstören erneut. Die erfolgreichen Stresstests stammen aus dem korrigierten Stand. Ein früher F6-Kaltstarttest begann außerdem vor abgeschlossenen Eingabe-/Fokusframes; die Bereitschaftsprüfung wurde ergänzt und der temporäre Kontext erhält eine ausdrückliche Initialisierungs-/Rebuild-Konfiguration. Diese Zwischenstände werden nicht als erfolgreiche Tests gezählt.

Die bekannten Crowd-/Recast-Weltwechselwarnungen bleiben bestehen. Der normale deutsche Editorstart meldet weiterhin die zuvor zugeordneten 17 Engine-Selbsttestfehler; während der abschließenden Toolbox-Tests wurden keine Error-Logeinträge festgestellt. Es wird kein vollständig meldungsfreier Editorstart behauptet.

Neue Dateien: vier C++-Klassenpaare unter `Source/FantasyLifeRPG/Development/`, `Development/Tests/DeveloperToolboxTests.cpp` und dieses Dokument. Bestehende Änderungen dieses Auftrags: `FantasyLifeRPGPlayerController.h/.cpp`, `FantasyLifeRPG.Build.cs`, `BP_PrototypePlayerController.uasset` und `docs/TECHNICAL_STATUS.md`. Keine neuen Maps, Niagara-Assets, Input-Assets oder globalen Konfigurationseinträge. Lokale ignorierte Belege: `Saved/InteractionDev/toolbox_build_final.log`, `toolbox_tests_all.json`, `toolbox_tests_new.json`, `toolbox_tests_controls.json`, `toolbox_configuration.json`, `toolbox_saved_audit.json` und `toolbox_panel.png`.

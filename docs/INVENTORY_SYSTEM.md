# Aufsammeln und Inventar V1

Unreal Engine 5.8, Sitzungsprototyp. Bestätigte Startregeln stehen in [GAME_SYSTEMS.md](GAME_SYSTEMS.md) und unter INV-01/02 in [DECISIONS.md](DECISIONS.md).

## Ausprobieren

1. `/Game/Prototype/Maps/Lvl_InventoryTest_01` öffnen und Play starten.
2. Den beschrifteten Testgegenständen nähern. Die bestehende Hervorhebung und E-Anzeige zeigen das nächste erreichbare Ziel. **E** nimmt den vollständigen Weltstapel auf.
3. **I** öffnet das Inventar mit Name, Anzahl und Platzbelegung. Gleiche Arten füllen vorhandene Stapel bis zum jeweiligen Maximum; weitere Mengen belegen weitere Plätze.
4. Einen belegten Eintrag auswählen und **1 Stück ablegen** anklicken. Bei freiem Boden vor der Figur entsteht ein aufnehmbarer Weltgegenstand. Fehlen Boden oder Platz, bleibt das Inventar unverändert und eine Meldung erscheint.
5. **I**, **Escape** oder **Schließen** schließen das Fenster. Danach lässt sich der abgelegte Gegenstand wieder mit E aufnehmen.

Bei geöffnetem Fenster läuft die Welt weiter. Bewegung, Kamera, Sprung, E und F6 werden für die Bedienung gesperrt. Die vom Inventar gesetzten Bewegungs-/Blicksperren werden beim Schließen und Weltabbau zurückgenommen; bereits bestehende Sperren werden nicht zurückgesetzt. Eine andere geöffnete Oberfläche muss zunächst geschlossen werden. Die Entwickler-Toolbox bleibt separat.

Die Toolbox respektiert jetzt auch Eingabesperren anderer Oberflächen: Während das Inventar offen ist, werden temporäre Flug-/Kameraachsen und gehaltene Sprintzustände zurückgenommen. Beim Schließen bewegen sich Flug oder freie Kamera erst nach erneuter Eingabe. Das Toolbox-Panel kann dem Inventar den Fokus nicht entziehen.

Bei vollem Inventar bleibt der aufzunehmende Gegenstand liegen. Der Prototyp zeigt die Meldung über die vorhandene lokale Nachrichtenkomponente des Prototyp-Spielers. Das Inventarfenster zeigt Meldungen in seiner Statuszeile. Ein eigener Spieler-Blueprint benötigt für Meldungen außerhalb des Fensters ebenfalls `PrototypeMessageComponent` oder einen eigenen Empfänger für `OnNotice`.

## Bausteine

- `InventoryItemDefinition`: gemeinsames DataAsset pro Gegenstandsart mit Anzeigename, maximaler Stapelgröße, vorhandenem Weltmesh und Weltmaßstab. Die Asset-Referenz ist die Typidentität; gleichnamige verschiedene Definitionen werden nicht vermischt.
- `InventoryComponent`: sitzungsgebundene Mengen am Spielercharakter. Standardkapazität 20, kein Tick. `CanAdd` prüft den Platz, `TryAdd` überträgt atomar die gesamte Menge, `DropOne` prüft Boden, Weg und freien Raum vor dem Spawn. Erst nach erfolgreichem Spawn wird genau ein Stück entfernt. `OnChanged` und `OnNotice` trennen Modell und Darstellung.
- `InventoryPickup`: verwendet das vorhandene Interaktionsinterface und dessen Autoritäts-, Reichweiten- und Sichtprüfung. Erfolg zerstört den aufgenommenen Weltactor; Ablehnung erhält ihn. Ein Transferguard schützt vor erneuter Aufnahme während synchroner Ereignisse. Der Actor blockiert Sichtabfragen, aber weder Pawn noch Kamera; es gibt keine Gegenstandsphysik.
- `InventoryUIComponent`: lokale Eingabe und Fokus am Basis-PlayerController. I wird über einen temporären Enhanced-Input-Kontext eingebunden; vorhandene Input-Assets werden nicht verändert. Besessenwechsel und EndPlay lösen Bindungen und räumen den Fokus auf.
- `InventoryWidget`: scrollbare Platzliste, Auswahl, Name/Anzahl, Ablegen und Status. Änderungen aktualisieren die Ansicht über Ereignisse.

`FantasyLifeRPGCharacter` und `FantasyLifeRPGPlayerController` erhalten jeweils eine native Standardkomponente. Bestehende abgeleitete Prototyp-Blueprints erben sie ohne Bearbeitung ihrer Assets. Neue Testinhalte liegen separat unter `/Game/Prototype/Inventory/` und in der neuen Testkarte. Bestehende Karten, Elfenassets und Startkarten werden für diesen Ausbau nicht geändert.

## Weitere Testgegenstände anlegen

1. `DA_TestWood` oder `DA_TestStone` unter einem neuen Namen duplizieren. Anzeigename, maximale Stapelgröße, Weltmesh und Maßstab in der neuen Definition einstellen. Für nicht stapelbare Arten `MaxStack` auf 1 setzen.
2. Einen Actor der nativen Klasse `InventoryPickup` in einer dafür vorgesehenen Testkarte platzieren. `Item` auf die neue Definition setzen und `Quantity` einstellen. Das Mesh wird aus der Definition übernommen.
3. Mit dem Prototyp-Spieler aufnehmen, die Menge im Inventar prüfen und ein Stück wieder ablegen. Alle Instanzen derselben Art müssen dieselbe Definition verwenden.

## Grenzen

Kein SaveGame, kein Transfer zwischen Karten/Charakteren, keine automatische Inventarübernahme beim Respawn. Neue PIE-Sitzungen beginnen mit leerem Inventar und den gespeicherten Testgegenständen. Keine neuen Regeln für Tod oder Gegenstandsbesitz. Keine Ausrüstung, Verwendung, Sortierung, Mengenwahl oder Gewichtsberechnung.

Gameplay-Mutationen verlangen Autorität. Server-RPCs, Replikation und Multiplayer-Synchronisierung sind noch nicht implementiert; V1 wird im Standalone-Modus geprüft. Tastatur/Maus sind der erste Bedienumfang. Controller, Touch, Split-Screen und Packaging benötigen eigene Prüfungen.

## Prüfung

Die automatisierten Tests stehen unter `FantasyLifeRPG.Inventory`:

- `Rules`: Stapelgrenzen, 20 Plätze, Auffüllen bei vollem Inventar, vollständige Ablehnung statt Teilverlust, ungültige Mengen/Definitionen, getrennte Typidentität, Sicht/Reichweite, erfolgreicher Welttransfer, freier/blockierter Ablegeort, Mengenrundlauf und Freigabe belegter Plätze.
- `PlayablePIE`: gespeicherte Testgegenstände, frische leere Sitzung, echte E-/I-Eingaben durch den PlayerController, Halten von E, sichtbares Inventar, Eingabesperren, UMG-Ablegeschaltfläche, erneute Aufnahme, volle Inventarmeldung, I/Escape über den fokussierten Slate-Widgetpfad und Wiederherstellung der Bewegung. Zusätzlich Sprint/Flug beim Menüwechsel, gegenseitiger Fokusschutz mit der Toolbox und Erhalt externer Eingabesperren. Der Test beendet PIE auch mit zuletzt geöffnetem Inventar.

Build, ausgeführte Testergebnisse und visuelle Prüfung werden nach Abschluss im [technischen Status](TECHNICAL_STATUS.md) festgehalten. Das subjektive Bediengefühl mit echter Tastatur/Maus sowie längere Spielsitzungen bleiben manuell zu beurteilen.

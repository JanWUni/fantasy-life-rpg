# Begehbare Testumgebung und NPC

Stand: 21. Oktober 2026, Unreal Engine 5.8. Neutrale technische Testwelt ohne verbindliche Orts-, Kultur- oder Lore-Festlegung.

## Starten und ausprobieren

`/Game/Prototype/Maps/Lvl_EnvironmentTest_01` ist jetzt Editor-Startkarte und Spielstartkarte. Projekt öffnen, **Play** starten und dem Weg zur Lichtung folgen. Das ursprüngliche Third-Person-Level und `Lvl_Prototype_01` sind weiterhin vorhanden und wurden bei dieser Erweiterung nicht bearbeitet.

- Der Third-Person-Spieler startet auf dem südlichen Weg. WASD, Kamera und Sprung stammen aus dem vorhandenen Projekt.
- Das Holzhaus steht bei ungefähr `(900, 1350, 80)` cm. Seine Tür benutzt den unveränderten `BP_PrototypeDoor` samt separatem Rahmen. Bei gültigem Ziel erscheinen „E – Interagieren“ und die goldene Hervorhebung. E öffnet, erneutes E schließt.
- Der Mannequin startet rechts vor dem Haus bei ungefähr `(1400, 1030, 176)` cm und läuft inzwischen eine Route über drei Wegpunkte. Innerhalb von 230 cm zum Interaktionspunkt erscheint „E – Sprechen“. E pausiert die Route für drei Sekunden, richtet ihn zum Spieler aus und zeigt für sechs Sekunden: **„Hallo, Reisender! Willkommen in unserer Testwelt.“** Wiederholtes Ansprechen ersetzt die vorhandene Antwortanzeige und verlängert die Bewegungspause. Routen-Konfiguration und aktueller Testbericht: [NPC_MOVEMENT.md](NPC_MOVEMENT.md).

## Umgebung und Assets

Das neue Level wurde über Unreal MCP aus der Engine-Vorlage `Template_Default` kopiert, separat gespeichert und erst danach bearbeitet. Der Boden der neuen Kopie wurde durch ein eigenes Höhenmesh ersetzt. Die bereitgestellte MCP-Anbindung besitzt keine Landscape-Erstellung; der unterstützte Static-Mesh-Import wurde deshalb als Alternative verwendet. Es handelt sich um ein statisches Prototyp-Gelände, nicht um ein nativ modellierbares Unreal-Landscape.

- Gelände: 80 × 80 Meter, 12.800 Dreiecke, sanfte Höhenunterschiede von insgesamt ungefähr vier Metern, flache Lichtung vor dem Haus.
- Geschwungener Weg mit eigener begehbarer Oberfläche, leicht über dem Gelände, damit sich die Flächen nicht gegenseitig überlagern.
- 64 einfache Tannen, 30 Felsen, ein Holzhaus mit Planken, Balken, Giebeldach, Fenster-Platzhaltern und zugänglichem Innenraum. Bank und Holzstapel ergänzen die Lichtung.
- Warme Tagesbeleuchtung, Sky Atmosphere, Wolken, Himmelslicht und weichere Sonnenschatten aus der kopierten Engine-Umgebung.
- Neue Assets liegen unter `/Game/Prototype/Environment/`. Die Tür erhält ausschließlich Materialüberschreibungen an ihrer neuen Levelinstanz. Die bisherigen Tür- und Spieler-Blueprints bleiben unverändert.
- Im Projekt und den untersuchten Engine-Inhalten waren keine geeigneten fertigen Vegetations- oder Gebäudeassets verfügbar. Tannen, Felsen und Haus sind deshalb einfache selbst erzeugte Platzhaltermeshes. Der NPC nutzt `SKM_Manny_Simple` und die vorhandene `MM_Idle`-Animation. Keine heruntergeladenen Assets und keine zusätzlichen Plugins.

Die neuen statischen Meshes verwenden für das unbewegte Testgelände und die zusammengesetzten Hausöffnungen Dreieckskollision (`UseComplexAsSimple`). Sie sind nicht für simulierte bewegliche Physikobjekte vorgesehen. Die wiederverwendete bewegliche Tür behält ihre vorhandene einfache Kollision.

`Tools/Prototype/generate_environment_sources.py` erzeugt die deterministischen Importquellen und die Streuverteilung unter `Saved/EnvironmentSources/`. Es benötigt nur Python-Standardmodule. Die OBJ-Dateien wurden über Unreal MCP importiert. Zehn Farbvarianten teilen sich ein einfaches, raues Material mit prozeduraler Farbvariation. Für den Prototyp gibt es keine aufwendigen Texturen, Gras-Foliage, Windanimation oder Produktions-LOD-Pipeline.

Beim OBJ-Import gab es Hinweise zu fehlenden Smoothing-Groups und bei Teilen des Hauses zu degenerierten Tangenten/fehlenden passenden UVs. Die Platzhalter verwenden flache Schattierung und keine Normalmap; die gerenderte Szene wurde geprüft. Diese Importwarnungen sind von den fehler- und warnungsfreien abschließenden C++-/PIE-Tests zu unterscheiden. Für spätere Produktionsassets sind geeignete Normalen, UVs und LODs erforderlich.

## Modulare NPC-Grundlage

- `NPC/PrototypeNPC.*`: `ACharacter`, implementiert das vorhandene `IInteractable` direkt. Benutzt dessen gemeinsame Reichweiten-/Sichtvalidierung und prüft Autorität vor der Ausführung. Reichweite, Aktivierung, Interaktionspunkt, Begrüßung und Drehung zum Interaktor sind einstellbar. Der aktuelle Ausbau ergänzt separate Wegpunkt- und Animationskomponenten am Blueprint, ohne Behavior Tree oder Actor-Tick.
- `BP_EnvironmentNPC`: weist Mesh und Idle-Animation zu. Das validierte Ereignis `OnSpokenTo` ruft `ShowMessageTo(Interactor, Greeting)` auf. Die C++-NPC-Klasse kennt weder Widgets noch Spieler-UI-Klassen.
- `Prototype/PrototypeMessageComponent.*`: austauschbare lokale Darstellung am Spieler. Zeigt genau eine passive Antwortanzeige, ersetzt sie bei neuer Nachricht und entfernt sie per Timer bzw. beim Beenden. Sie erzeugt keine UI für einen nicht lokal kontrollierten Pawn.
- `Prototype/UI/PrototypeMessageWidget.*`: Anzeige ohne Eingabefokus oder Dialogzustand, oberhalb des bestehenden E-Hinweises.
- `BP_EnvironmentCharacter`: Kind des vorhandenen `BP_PrototypeCharacter`; ergänzt nur die Antwortkomponente. Der eigene `BP_EnvironmentGameMode` wählt diesen Spieler im neuen Level. Enhanced Input, Interaktionskomponente und Hervorhebung werden geerbt.

Es gibt keine neue Interaktionssuche oder zweite E-Belegung. Die spätere Netzwerk-Erweiterung benötigt weiterhin eine serverseitig geprüfte Interaktionsanfrage und replizierte Zustände bzw. eine gezielte Antwort an den auslösenden Client. Der NPC-Zustand und seine Drehung sind aktuell nicht repliziert. Die lokale Begrüßung ist ein Test der Darstellung, kein vollständiges Dialogsystem.

## Tatsächlich erfolgreich geprüft

Die folgenden Ergebnisse beschreiben den ursprünglichen Umgebungs-Ausbau. Der aktuelle Stand mit NPC-Bewegung, Kamera-Prüfung, Aktionstexten und sechs erfolgreichen Tests steht in [NPC_MOVEMENT.md](NPC_MOVEMENT.md). Der ursprüngliche Umgebungstest stoppt die Route inzwischen absichtlich für seine kontrollierte Interaktionsfixture; der neue Navigationstest prüft die laufende Route separat.

- `FantasyLifeRPGEditor Win64 Development` einschließlich UHT, Kompilierung und Link: erfolgreich. Der abschließende Build hatte keine Compilerwarnungen. Alle drei neuen Gameplay-Blueprints wurden über MCP kompiliert und gespeichert.
- Neustart des Editors und Laden des gespeicherten Levels: erfolgreich; Haus, Tür, Vegetation und NPC sind vorhanden.
- `FantasyLifeRPG.Environment.PlayablePIE`: **Success**, keine Fehler oder Warnungen, ungefähr 15 Sekunden. Prüft Geländegröße, vorhandene Bäume/Felsen und 45 Bodenabfragen entlang des Weges. Der echte CharacterMovement-Pfad bewegt den Spieler vom Start bis zur Lichtung, ohne ihn während dieses Wegabschnitts zu teleportieren.
- Derselbe Integrationstest prüft Öffnen und Schließen der übernommenen Haustür durch simulierte E-Ereignisse im vorhandenen Enhanced-Input-Pfad. Eine spielergroße Kapsel wird geschlossen blockiert und kann bei geöffneter Tür den Hausdurchgang passieren.
- NPC-Prüfungen: Idle-Animation läuft, feste Position bleibt erhalten, bestehende Zielanzeige und Mesh-Hervorhebung, E erzeugt genau eine sichtbare Antwort mit dem eingestellten Text, horizontale Ausrichtung zum Spieler, kein wiederholtes Ansprechen beim Halten von E, automatisches Ausblenden und erneutes Ansprechen. Außerhalb der Reichweite, hinter einem temporären Sichtblocker oder bei deaktiviertem NPC verschwinden Zielhinweis und Hervorhebung; unerlaubtes Ansprechen erzeugt keine Antwort.
- Gemeinsamer abschließender Lauf: **5 erfolgreich, 0 fehlgeschlagen, 0 übersprungen**, keine Fehler oder Warnungen. Enthält zusätzlich alle bisherigen Tests `Interaction.Rules`, `Interaction.PrototypePIE`, `Interaction.FeedbackPIE` und `Interaction.DoorPIE`.
- Gerenderte PIE-Sichtprüfung: Landschaft mit Weg, Bäumen, Felsen und Haus am Startpunkt; NPC mit goldener Hervorhebung und vollständiger, umgebrochener Begrüßung nach über MCP ausgelöstem E. Bestehender E-Hinweis bleibt sichtbar. Lokale Screenshots: `Saved/InteractionDev/environment_spawn_final.png` und `npc_greeting_final.png`.

Testcode: `Source/FantasyLifeRPG/Prototype/Tests/EnvironmentTests.cpp`. Die Tests laden gespeicherte Maps; eigene Editoränderungen vorher speichern. Prüfprotokoll und Screenshots unter `Saved/InteractionDev/` bleiben ignorierte lokale Artefakte.

## Manuell prüfen und Prototyp-Grenzen

- Mit eigener Tastatur und Kamera vom Start zum Haus laufen; Umgebung abseits des automatisch geprüften Weges, Hänge, Felsen, Bäume, Hausinnenraum und Kartenrand erkunden. Nicht jeder Quadratmeter wurde automatisiert durchlaufen. Die begrenzte Testfläche besitzt noch keine ausgearbeitete Weltgrenze.
- Haustür öffnen, hindurchgehen und von innen schließen. Das direkte Umschalten besitzt weiterhin keine Animation und prüft keinen belegten Tür-/Schwenkbereich.
- NPC von verschiedenen Richtungen ansprechen; Lesbarkeit und Dauer der Nachricht sowie Kamera und Hervorhebung bei eigener Auflösung beurteilen. Der Input wurde durch Editor-/Engine-Ereignisse geprüft, nicht durch menschliche Tastaturbedienung.
- Kein Performance-Benchmark, paketierter Build, Multiplayer, Split-Screen, Controller oder Touch-Test. Keine Dialogauswahl, Persistenz, Tagesabläufe, Berufe oder NPC-Simulation implementiert.

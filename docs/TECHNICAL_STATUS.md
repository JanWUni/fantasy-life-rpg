# Technischer Ist-Zustand

**Stand:** 22. Oktober 2026

Diese Datei beschreibt ausschließlich den überprüften technischen Arbeitsstand. Technische Zielrichtungen und offene Architekturentscheidungen stehen in [IMPLEMENTATION_APPROACH.md](IMPLEMENTATION_APPROACH.md); verbindliche Spiel- und Weltentscheidungen stehen in [DECISIONS.md](DECISIONS.md).

Der neueste Pipeline-Prüfstand steht im Abschnitt „Blender→Unreal-Kalibrierung 01“. „Untersuchung der verbleibenden Unreal-Meldungen“ und die übrigen Ausbauabschnitte dokumentieren ihre jeweiligen früheren Prüfungen.

## Repository und Projekt

- Das bestehende Repository `JanWUni/fantasy-life-rpg` ist im lokalen Unreal-Projektverzeichnis eingerichtet.
- Der lokale Branch `main` verfolgt `origin/main` und übernimmt die bestehende GitHub-Historie.
- Das Unreal-Projekt liegt im Repository-Stamm als `FantasyLifeRPG.uproject`.
- Unreal-Konfiguration, C++-Quellen und Projektinhalte liegen in `Config/`, `Source/` und `Content/`.
- Worldbuilding und Game Design bleiben in der bestehenden Struktur unter `docs/`.

## Unreal Engine

- Die Projektdatei ist derzeit mit **Unreal Engine 5.8** verknüpft.
- Das Runtime-Modul heißt `FantasyLifeRPG`.
- In der Projektdatei sind unter anderem `AIModule` und `UMG` als zusätzliche Modulabhängigkeiten eingetragen.
- Das Projekt enthält C++-Quellen sowie vorhandene Template- und Prototypinhalte für Third Person, Combat, Platforming und Side Scrolling.
- Die aktuellen Standard- und Editor-Startkarten verweisen auf den separaten Prototyp-Level `/Game/Prototype/Maps/Lvl_EnvironmentTest_01`. Der ursprüngliche Third-Person-Template-Level bleibt erhalten.
- Vorhandene Assets und Levels wurden bei der Repository-Einrichtung nicht verändert.

## Unreal MCP

- Das Plugin `ModelContextProtocol` ist in der Projektdatei aktiviert.
- Die lokale Codex-Konfiguration bindet den Unreal-MCP-Dienst derzeit über `http://127.0.0.1:8000/mcp` ein.
- `.codex/config.toml` ist eine rechnerbezogene Konfiguration und wird durch `.gitignore` von der Versionsverwaltung ausgeschlossen.
- Die tatsächliche Editorverbindung und die verfügbaren MCP-Operationen müssen bei einer laufenden Unreal-Editor-Sitzung geprüft werden.

## Versionsverwaltung

- Generierte Unreal-Verzeichnisse, Build-Ausgaben, Shader-Caches, Visual-Studio-Zustände und Projektlösungen werden ignoriert.
- `.uasset`, `.umap` und weitere binäre Asset- und Quelldateiformate sind in `.gitattributes` für Git LFS registriert.
- Git LFS ist lokal für dieses Repository initialisiert.
- Zum Zeitpunkt dieser Bestandsaufnahme wurde kein Einrichtungs-Commit erstellt und nichts gepusht.

## Interaktionsprototyp

- Das erste Interaktionssystem ist in C++ unter `Source/FantasyLifeRPG/Interaction/` umgesetzt: Spielerkomponente, Blueprint-fähiges Interface und optionale Actor-Basisklasse.
- `/Game/Prototype/Maps/Lvl_Prototype_01` verwendet eigene Prototyp-Blueprints und enthält `BP_InteractionTest` mit 200 cm Reichweite und sichtbarem Zustandswechsel über Enhanced Input / Taste E.
- Die ursprünglichen Template-Levels und Worldbuilding-Dokumente wurden dafür nicht verändert. Die spätere Umgebungserweiterung setzt ihre eigene Karte als Standard- und Editor-Startkarte.
- Eine separate lokale Feedback-Komponente am Prototyp-Spieler zeigt bei einem gültigen, erreichbaren Ziel „E – Interagieren“ unten mittig an und hebt dessen Mesh gold hervor. Bei Sicht- oder Reichweitenverlust verschwinden beide. Die Darstellung verwendet ein transparentes Overlay mit vorübergehendem Fallback-Rendering der ausgewählten Nanite-Static-Mesh-Komponente.
- Der Interaktionspunkt des Testobjekts wurde von der Bodenfläche ins Mesh versetzt, damit der Boden die Sichtprüfung nicht am Endpunkt blockiert.
- `BP_PrototypeDoor` und der separate feste `BP_PrototypeDoorFrame` stehen bei ungefähr `(650, -350, 0)` cm in `Lvl_Prototype_01`. Die Tür nutzt die vorhandene Interaktionsbasis, Anzeige und Hervorhebung. E schaltet unmittelbar zwischen der geschlossenen Ausgangsdrehung und einem lokalen Versatz von -90 Grad um. Blatt und Griff verwenden vorhandene Platzhaltermeshes. Animation, Schwenkbereichsprüfung und Zustandsreplikation sind noch nicht umgesetzt.
- Editor-Build und alle vier automatisierten Tests `FantasyLifeRPG.Interaction.Rules`, `FantasyLifeRPG.Interaction.PrototypePIE`, `FantasyLifeRPG.Interaction.FeedbackPIE` und `FantasyLifeRPG.Interaction.DoorPIE` sind erfolgreich abgeschlossen; der letzte gemeinsame Lauf hatte keine Fehler oder Warnungen. Der Feedbacktest prüft die tatsächlich gerenderte Widget-Position und das Wiederherstellen der Overlay-/Nanite-Fallback-Werte. Der Türtest prüft E von beiden Seiten, Reichweite/Sicht, Feedback, feste Rahmenposition, relativen Schwenk einer gedrehten Instanz sowie den blockierten bzw. freien Durchgang mittels Kapselabfrage. Geschlossener und offener Zustand wurden zusätzlich im gerenderten PIE-Spielfenster visuell geprüft.
- Multiplayer wird durch getrennte Anfrage/Validierung/Ausführung und Autoritätsprüfungen vorbereitet. RPCs und Replikation sind noch nicht implementiert.
- Bedienung, Grenzen, genaue Testabdeckung und offene manuelle Prüfungen: [INTERACTION_SYSTEM.md](INTERACTION_SYSTEM.md).

## Begehbare Testumgebung und NPC

- `/Game/Prototype/Maps/Lvl_EnvironmentTest_01` ist ein separates, gespeichertes Level auf Basis einer Kopie der Engine-Basic-Vorlage. Es umfasst ungefähr 80 × 80 Meter hügeliges Mesh-Gelände, einen gewundenen Weg, 64 Tannen, 30 Felsen, eine Lichtung mit begehbarem Holzhaus sowie kleine Platzhalterdetails. Es wurde kein natives Landscape angelegt; die verfügbare MCP-Anbindung unterstützt stattdessen den verwendeten Mesh-Import.
- Die neue Karte ist in `Config/DefaultEngine.ini` als Spiel- und Editor-Startkarte eingetragen. Die bisherigen Third-Person- und Prototyp-Level sowie die bisherigen Tür- und Spieler-Blueprints wurden bei dieser Erweiterung nicht geändert.
- Das Haus nutzt die fertige Blueprint-Tür und den vorhandenen Rahmen als neue Levelinstanzen. Eingabe, Reichweitenprüfung, Anzeige und Hervorhebung werden übernommen.
- `NPC/PrototypeNPC.*` implementiert das vorhandene Interaktionsinterface mit Autoritäts-/Sicht-/Reichweitenprüfung. Der stationäre NPC verwendet im eigenen Blueprint den vorhandenen Mannequin und `MM_Idle`, richtet sich beim Ansprechen zum Spieler aus und löst eine austauschbare lokale Nachrichtendarstellung aus. Keine AI-Steuerung oder NPC-Simulation.
- Der neue Spieler-Blueprint erbt vom bisherigen Prototyp-Spieler und ergänzt `PrototypeMessageComponent` und ein passives Antwortwidget. Der NPC-Code hängt nicht von diesen UI-Klassen ab; die Verbindung liegt im NPC-Blueprint. Die Begrüßung erscheint sechs Sekunden lang und ersetzt gegebenenfalls die vorherige Nachricht.
- Abschließender Editor-Build und alle fünf automatisierten Tests erfolgreich, ohne Fehler oder Warnungen. `FantasyLifeRPG.Environment.PlayablePIE` lässt den Spieler tatsächlich vom Spawn zur Lichtung laufen und prüft außerdem Wegoberfläche, Haustür, Idle, NPC-Antwort, Ausrichtung, lokale UI, Reichweite und Sichtblockierung. Alle vier bisherigen Interaktionstests bestehen weiterhin. Landschaft und NPC-Antwort wurden zusätzlich im gerenderten Spielfenster geprüft.
- Die Umgebung bleibt eine neutrale Testwelt mit einfacher Platzhalteroptik. Keine kostenpflichtigen Assets, zusätzlichen Plugins, Worldbuilding-Änderungen, Commits oder Pushes. Exakte Testabdeckung, OBJ-Importwarnungen und manuelle Restprüfungen: [ENVIRONMENT_TEST.md](ENVIRONMENT_TEST.md).

## NPC-Bewegung und Prüfstand vom 21. Oktober 2026

- Der NPC in `Lvl_EnvironmentTest_01` besitzt nun eine wiederverwendbare `WaypointMovementComponent`. Er läuft per nativem AIController und NavMesh zyklisch über drei im Editor verschiebbare TargetPoints, wartet standardmäßig 1,5 Sekunden und umgeht die Bank neben dem Haus. Die Komponente verwendet Pfadabschluss-Ereignisse und Timer ohne eigenen Tick. Fehlgeschlagene Ziele werden verzögert erneut angefragt.
- Eine separate `PrototypeLocomotionComponent` schaltet anhand der tatsächlichen Geschwindigkeit zwischen vorhandener Idle- und Laufanimation um. Das NPC-Blueprint pausiert die Bewegung beim Ansprechen drei Sekunden und zeigt weiterhin die lokale Begrüßung. Der native Interaktionscode kennt weder Bewegungskomponente noch UI.
- Das bestehende Interaktionsinterface liefert jetzt den Aktionstext. Das vorhandene Widget zeigt „E – Tür öffnen“, „E – Tür schließen“, „E – Sprechen“ oder den bisherigen Rückfall „E – Interagieren“. Der Text aktualisiert sich auch beim gleichbleibenden Ziel nach einer Zustandsänderung.
- Editor-Build erfolgreich ohne Compilerwarnungen. Alle sechs Tests erfolgreich: die bisherigen fünf in einem Lauf und `Environment.NavigationPIE` anschließend separat. Der Navigationstest prüft zwei Runden, Wartezeiten, Hindernisumgehung, Ansprechen beim Laufen, Pause/Fortsetzen, Animationen, unerreichbare Ziele und Timer-Abbruch. Der Umgebungstest prüft zusätzlich Aktionstexte und Kamera-Kollision im Haus.
- Navigationstest-Frame-Stichprobe: Mittelwert 13,04 ms, Maximum 147,85 ms, ein Frame über 100 ms bei 2.410 Samples. Kein Last-/GPU-Benchmark. Beim PIE-Start/-Ende bzw. Weltwechsel bleibt eine Engine-Warnung zur frühen Initialisierung des optionalen Crowd-Managers vor verfügbaren Recast-Daten; vollständige NavMesh-Pfade und Runden bestehen. Keine abschließenden Testfehler.
- Logprüfung: Die bereits in älteren Sitzungen vorhandenen Editor-Startfehler (`LogAutomationTest: Condition failed`, fehlende `GameFeatureData`-Asset-Manager-Regel) bestehen weiter und sind nicht vollständig bereinigt. Im letzten Navigationstest und der anschließenden Sichtprüfung gab es keine Error-Logeinträge. Die bekannten Startmeldungen und die Crowd-Warnung sind im aktuellen Prüfbericht getrennt von den erfolgreichen Gameplay-Tests dokumentiert.
- Änderungen sind auf den Prototyp-Ausbau beschränkt. Template-Levels und Worldbuilding-Dateien bleiben unverändert; keine Commits oder Pushes. Aktuelle Konfiguration, genaue Testergebnisse, bekannte Warnung und manuelle Restprüfungen: [NPC_MOVEMENT.md](NPC_MOVEMENT.md).

## Stabilisierung von Environment.PlayablePIE – 22. Oktober 2026

Bei der anschließenden Bestandsaufnahme scheiterte `Environment.PlayablePIE` einmal nach ungefähr 4,86 Sekunden mit `Environment PIE fixture disappeared`; die unveränderte Einzelwiederholung bestand. Die alte Fehlermeldung benannte weder die verlorene Referenz noch den Testschritt. Der genaue Auslöser dieses historischen Abbruchs ist deshalb nicht abschließend nachgewiesen. Auch vor der jetzigen Ablaufkorrektur bestanden drei Einzelwiederholungen mit ergänzter Diagnose und eine vollständige Suite; ein reproduzierbarer Fehler an Gelände, Tür oder NPC wurde dabei nicht gefunden.

Im Testcode waren zwei fehlende Absicherungen feststellbar: `FStartPIECommand` und `FEndPlayMapCommand` fordern den Sitzungswechsel an und kehren sofort zurück; der Test wartete nicht ausdrücklich auf dessen Abschluss. Zudem wählte er den ersten passenden PIE-Weltkontext ohne Prüfung auf aktive Sitzung, abgeschlossene Initialisierung oder laufenden Weltabbau. Diese Schwachstellen sind behoben, ohne sie als bewiesene alleinige Ursache des früheren Abbruchs auszugeben.

- `Prototype/Tests/EnvironmentTests.cpp` beendet vor dem Laden eine gegebenenfalls vorhandene PIE-/Simulationssitzung und wartet, bis auch deren Weltkontexte entfernt sind. Dasselbe gilt am Testende. Ein ausstehender, noch nicht gestarteter Play-Auftrag wird abgebrochen. Der Abbau besitzt eine Fehlergrenze von 20 Sekunden.
- Der Start verwendet den vorhandenen Engine-Automationshelfer mit Bereitschaftsprüfung statt einer bloßen Startanforderung. Sein Beobachter wird erst nach dem alten Sitzungsende angelegt; seine Zeitmessung funktioniert auch beim delegierten Aufruf. Eine temporäre Kopie der Editor-Play-Einstellungen legt einen Einzelspieler im Standalone-Modus fest, ohne die Benutzereinstellungen zu speichern.
- Der Test bindet sich an `GEditor->PlayWorld` und verlangt eine initialisierte, gestartete Welt ohne laufenden Abbau. Während des Tests prüft er weiterhin die Sitzungsidentität und seine Actor-/UI-Referenzen. Initiale Welt-/Actor-Pfade und Positionen sowie bei einem Verlust Testschritt, Gültigkeit der zentralen Referenzen und letzte Spieler-/NPC-Position werden protokolliert.
- Die Bereitschaftsfrist der Fixture beginnt bei deren erster Ausführung. Die Wegprüfung verwendet unverändert echte CharacterMovement-Eingaben und dieselbe 30-Sekunden-Grenze. Ein verlorener Testaufbau führt weiterhin zum Fehler; es gibt keine stillen Wiederholungen oder Wiederherstellung während des Testfalls.

Tatsächlich nach dieser Korrektur über Unreal MCP geprüft:

| Szenario | Ergebnis |
| --- | --- |
| Einzeltest direkt nach Editorneustart | 1/1 erfolgreich, 15,32 Sekunden |
| Direkte Einzelwiederholung | 1/1 erfolgreich, 15,24 Sekunden |
| Start aus laufendem PIE mit Spawn-Überschreibung am Haus | 1/1 erfolgreich, 15,27 Sekunden |
| Start aus laufender Simulation in `Lvl_Prototype_01` | 1/1 erfolgreich, 15,23 Sekunden |
| Vollständige Suite, erster Lauf | 6/6 erfolgreich, 57,55 Sekunden |
| Vollständige Suite, zweiter Lauf | 6/6 erfolgreich, 60,43 Sekunden |

Damit bestehen **16 Testausführungen ohne Testfehler**, darunter **sechs aufeinanderfolgende Ausführungen von PlayablePIE**. Beide vollständigen Läufe umfassen `Environment.NavigationPIE`, `Environment.PlayablePIE`, `Interaction.DoorPIE`, `Interaction.FeedbackPIE`, `Interaction.PrototypePIE` und `Interaction.Rules`. Jeder Lauf endete ohne aktive PIE-Sitzung; die sechs Umgebungsläufe starteten am gespeicherten PlayerStart. Kompilierung und Link von `FantasyLifeRPGEditor Win64 Development` waren erfolgreich, ohne Compilerwarnungen.

Die bekannte Crowd-/Recast-Warnung tritt weiterhin bei Sitzungs- und Weltwechseln auf. Sie wurde nicht unterdrückt; die bekannten Editor-Startmeldungen (`Condition failed`, fehlende `GameFeatureData`-Regel) wurden in diesem Auftrag nicht behoben. Nach Beginn der abschließenden Wiederholungstests wurden keine Error-Logeinträge erfasst. Die Wiederholungen bestätigen den geprüften Ablauf, beweisen aber nicht, dass jeder mögliche Editorzustand oder externe PIE-Abbruch ausgeschlossen ist. Bei einem erneuten Verlust liefert der Test nun genauere Diagnoseinformationen.

Die Änderung betrifft ausschließlich Testcode und diese technische Statusdokumentation. Spielsysteme, Karten, Blueprints, Template-Inhalte und Worldbuilding bleiben unverändert; keine Commits oder Pushes. Eine zusätzliche manuelle Spielprüfung wurde für diese Testablaufkorrektur nicht durchgeführt. Die bisherigen manuellen Gameplay- und Langzeitprüfungen bleiben offen. Lokale, ignorierte Belege: `Saved/InteractionDev/playable_fix_results.json`, `playable_fix_build.log` und der Wiederholungslauf `verify_playable_fix.py` im selben Verzeichnis.

## Untersuchung der verbleibenden Unreal-Meldungen – 22. Oktober 2026

Die drei untersuchten Meldungsgruppen sind jetzt zugeordnet. Es gibt daraus keinen nachgewiesenen kritischen Prototyp-Blocker. Eine projektseitige Integrationslücke und ein bei den Regressionstests aufgefallener Fehler der Testzeitmessung wurden gezielt korrigiert.

| Einstufung | Meldung / Befund | Herkunft und Auswirkung | Behandlung |
| --- | --- | --- | --- |
| Relevant, behoben | Fehlende Asset-Manager-Regel für `GameFeatureData` | GameFeatures-Plugin meldet eine fehlende Projektkonfiguration; notwendig für das Laden entsprechender Feature-Daten. Der Prototyp besitzt keine registrierten GameFeatureData-Assets. | Eine typbezogene Regel in `Config/DefaultGame.ini` ergänzt; Startprüfung in englischer und deutscher Sitzung ohne diese Fehler. |
| Unkritisch für den aktuellen Prototyp | Crowd-/Recast-Warnungen bei Weltwechsel und PIE-Ende | Engine-Navigations-/Crowd-Code sucht nach dem Abmelden seiner Recast-Daten erneut nach NavMesh. Die geprüfte NPC-Route verwendet normale AI-Pfadverfolgung. | Nicht unterdrückt; keine Engine-, Crowd- oder Navigationskonfiguration geändert. |
| Unkritisch für den aktuellen Prototyp, relevant für Engine-Testqualität | 17 `Condition failed` beim deutschen Editorstart | Drei interne Core-Selbsttests vergleichen englische Solltexte mit sprachabhängigen Ausgaben. Kein Tür-, NPC- oder Interaktionscode als Auslöser. | Deutsch/Englisch/Deutsch-Vergleich durchgeführt; keine Engine-Patches, globale Sprachänderung oder Abschaltung der Selbsttests. |
| Relevant, behoben | Erste NPC-Wartezeit im Navigationstest zu kurz gemessen | Eigener Test startete seine Messung erst einen Frame nach synchroner Ankunft. Gemeldet wurden 1,341 statt 1,5 Sekunden. | Anfangszustand direkt nach `StartRoute()` beobachten; dieselbe Wartezeit und Toleranz weiter prüfen. Gameplay-Code unverändert. |

**Crowd/Recast:** Die Rohwarnungen der untersuchten Läufe stehen unmittelbar bei `BeginTearingDown` beziehungsweise `UWorld::CleanupWorld`. Der Quellcode liefert die passende Kette: `UNavigationSystemV1::UnregisterNavData` → `UCrowdManager::OnNavDataUnregistered` → `SetNavData(nullptr, true)` → `OnNavMeshUpdate` → `CreateCrowdManager`. Letzteres protokolliert die Warnung, wenn keine geeigneten Recast-Daten mehr vorhanden sind. Die frühere Erklärung einer frühen Initialisierung wird damit für die tatsächlich beobachteten Meldungen präzisiert: Sie entstehen hier beim Abbau beziehungsweise Wechsel der Welt. Die Engine besitzt außerdem Registrierungs-/Initialisierungspfade; diese wurden nicht pauschal als fehlerhaft eingestuft.

MCP bestätigt am NPC-Blueprint `AIControllerClass=/Script/AIModule.AIController`. Dieser Engine-Controller erzeugt standardmäßig `UPathFollowingComponent`; die eigene Route fordert vollständige Pfade über `MoveTo` an. Der Navigationstest prüft NavMesh-Projektion, Hindernisumgehung und wiederholte Ankünfte. Es gibt daher keinen Beleg für fehlende nutzbare Navigation während der geprüften Route. Der Weltabbau des eigenen Levels löst den Engine-Codepfad aus; die Meldung ist kein nachgewiesener Fehler der Bewegungskomponente. Bei künftiger tatsächlicher Detour-Crowd-Nutzung muss deren Initialisierung separat geprüft werden. Eine während des laufenden Spiels auftretende Warnung mit fehlgeschlagenen Pfaden wäre neu zu bewerten.

**Die 17 Startmeldungen sind vollständig aufgeschlüsselt:**

| Engine-Test | Fehlerereignisse bei deutscher Sprache |
| --- | ---: |
| `System.Core.Experimental.UnifiedError.CreateErrorMessage` | 7 |
| `System.Core.Experimental.UnifiedError.CreateErrorMessageWithContext` | 4 |
| `Core.Logging.StructuredLogFormat` | 6 |
| Summe | 17 |

Die Start-Selbsttests laufen in `LaunchEngineLoop.cpp` vor der Engine-Initialisierung. `LowLevelTestAdapter.h` meldet bei einem fehlgeschlagenen `CHECK` nur „Condition failed“. Mit einer einmaligen, sitzungsbezogenen Erhöhung der Log-Ausführlichkeit wurden am deutschen Start genau die oben genannten drei Testklassen und 17 Fehler direkt zugeordnet. Die ursprüngliche Ausführlichkeit `Warning` wurde wiederhergestellt. Explizite MCP-Testläufe reproduzieren dieselben 7/4/6 Fehler. Ein vorübergehender Start mit `-culture=en` ergibt **0 dieser Startmeldungen und 3/3 erfolgreiche Kontrolltests**. Nach Rückkehr zur normalen OS-Sprache `de-DE` treten dieselben 17 Ereignisse und dieselben drei Testfehlschläge erneut auf. Der Zusammenhang mit den englischen Solltexten und lokalisierten Ausgaben ist damit bestätigt. Diese diagnostischen Engine-Testfehlschläge sind von den Projekttests zu unterscheiden. Der Editorstart bleibt mit deutscher Sprache deshalb weiterhin nicht vollständig fehlerfrei protokolliert.

**GameFeatureData:** Das Projekt aktiviert `AllToolsets`; dessen Abhängigkeit `GameFeaturesToolset` aktiviert `GameFeatures`. Die Fehlermeldungen stammen aus `UGameFeaturesSubsystem::OnAssetManagerCreated` und dem GameFeatures-Editor-Modul. Es handelt sich um eine projektseitige Konfigurationslücke bei einer vorhandenen Plugin-Abhängigkeit. Die ergänzte Regel entspricht der eingebauten Editoraktion `AddDefaultGameDataRule`: native Basisklasse `/Script/GameFeatures.GameFeatureData`, keine Blueprint-Klassen, `AlwaysCook`, keine Scan-Verzeichnisse oder konkreten Assets. Die bestehenden Regeln für Map und PrimaryAssetLabel bleiben erhalten. MCP bestätigt alle drei geladenen Typregeln und findet keine registrierten GameFeatureData-Assets. Es wurden keine Plugins deaktiviert, Feature-Plugins angelegt oder allgemeinen Content-Scanpfade hinzugefügt. Nach Neustart verschwinden sowohl der `LogGameFeatures`-Fehler als auch der entsprechende `LoadErrors`-Eintrag.

**Zusätzliche Testkorrektur:** Im ersten vollständigen Regressionslauf bestanden 5/6 Projekttests. Nur `NavigationPIE` meldete den oben genannten Messfehler. Die Fixture setzt den NPC auf Wegpunkt 1; `StartRoute` kann deshalb unmittelbar `Arrive` aufrufen und den 1,5-Sekunden-Timer starten. Die bisherige Beobachtung erst im nächsten Frame ließ dessen verstrichene Spielzeit aus der Messung fallen. Der Test beobachtet jetzt diesen synchronen Anfangszustand sofort und protokolliert die erste gemessene Wartezeit. Der NPC-Timer und die Testtoleranz wurden nicht verändert. Der erste korrigierte Test nach normalem Editorneustart besteht und misst 1,505 Sekunden. Der Editor-Build einschließlich Kompilierung und Link ist erfolgreich, ohne Compilerwarnungen.

Abschließende Regression nach der Konfigurations- und Testkorrektur, im normalen deutschen Editor ohne Sprach-/Log-Overrides:

| Prüfung | Ergebnis |
| --- | --- |
| Editor-Build `FantasyLifeRPGEditor Win64 Development` | Erfolgreich, 19,28 Sekunden, keine Compilerwarnungen |
| `Environment.NavigationPIE` direkt nach Editorneustart | 1/1 erfolgreich, 31,80 Sekunden |
| Vollständige Projektsuite, Lauf 1 | 6/6 erfolgreich, 57,95 Sekunden |
| Vollständige Projektsuite, Lauf 2 | 6/6 erfolgreich, 57,65 Sekunden |

Insgesamt **13 erfolgreiche Projekttest-Ausführungen nach der letzten Korrektur**. Beide Suiten umfassen Navigation, begehbare Umgebung, Tür, Feedback, Testobjekt und Interaktionsregeln. Die erste Wartezeit wird in den drei Navigationstests mit 1,505 / 1,514 / 1,505 Sekunden bei eingestellten 1,5 Sekunden gemessen. Während dieser abschließenden Gameplay-Tests gibt es keine Error-Logeinträge; enthaltene Warnungen betreffen ausschließlich den bekannten Crowd-/Recast-Weltabbau. Der normale Editorstart enthält weiterhin die 17 erklärten Engine-Selbsttestfehler, aber keine fehlende GameFeatureData-Regel mehr. Abschließend ist `Lvl_EnvironmentTest_01` geöffnet und PIE beendet. Die Engine-/Sprachdiagnose, der erste fehlgeschlagene Regressionslauf und die erfolgreichen abschließenden Läufe bleiben als getrennte Belege erhalten.

Quellcodebelege im eingesetzten Engine-5.8-Build: `Runtime/Core/Public/Misc/LowLevelTestAdapter.h:130`, `Runtime/Core/Tests/Experimental/UnifiedError/UnifiedErrorTests.cpp:479` und `:512`, `Runtime/Core/Tests/Logging/StructuredLogFormatTest.cpp:21`, `Runtime/Launch/Private/LaunchEngineLoop.cpp:4376`, `Runtime/AIModule/Private/Navigation/CrowdManager.cpp:897` und `:1377`, `Runtime/NavigationSystem/Private/NavigationSystem.cpp:2975` sowie `Plugins/Runtime/GameFeatures/Source/GameFeaturesEditor/Private/GameFeaturesEditorModule.cpp:358` und `GameFeatures/Private/GameFeaturesSubsystem.cpp:775`. Die Runtime-/Launch-Pfade beziehen sich auf `Engine/Source/`.

Keine ungeklärte Herkunft verbleibt bei den drei untersuchten Meldungsgruppen. Paketierter Build/Cooking, tatsächliche Game-Feature-Aktivierung und Crowd-Navigation unter Last wurden nicht getestet. Engine- und Plugin-Dateien, Gameplay-Code, Assets, Template-Levels und Worldbuilding bleiben unverändert; keine Commits oder Pushes. Lokale Diagnose- und Testbelege unter `Saved/InteractionDev/warnings_*` bleiben ignoriert.

## Asset-Lab und World-Sandbox – 22. Oktober 2026

Zwei zusätzliche, separat gespeicherte Karten bilden jetzt den Arbeitsbereich für wiederverwendbare Assets. Einrichtung, Platzierung, Materialinstanzen, Mesh-Erstellung, Speicherprüfung und PIE-Aufrufe erfolgten über Unreal MCP. Die bisherigen Startlevel-Einstellungen bleiben erhalten. Es wurden keine neuen Gameplay-Systeme, Plugins oder externen Modellierungswerkzeuge eingeführt.

- `/Game/Prototype/Maps/Lvl_AssetLab`: 60 × 40 m ebener Rasterboden, drei räumlich getrennte und beschriftete Bereiche für Architektur, Möbel und Natur, drei Podeste, Referenzkörper mit 100 cm beziehungsweise 180 cm und eine niedrige Randbegrenzung. 62 Actors mit `Lab/`- und `Workspace/`-Outliner-Ordnern. Vorhandene Würfel-/Zylindergeometrie, Tanne und Fels dienen als Referenzen. Eigener GameMode-Override verwendet den bestehenden Third-Person-Prototyp samt Enhanced Input.
- `/Game/Prototype/Maps/Lvl_WorldSandbox`: 120 × 120 m ebener Boden, Tageslicht mit Himmel/Wolken und eine gedrehte Referenz des Wandmoduls. 19 Actors, vorhandener Third-Person-Prototyp und PlayerStart. Noch keine Landschaft, Stadt oder NPC-Navigation.
- `/Game/Art/Architecture/SM_Wall_Test_400x20x300`: gemeinsames, eigenständiges technisches Wandmesh, 400 × 20 × 300 cm, unterer Eckpivot, 12 Dreiecke, ein Materialslot und ein einfacher konvexer Kollisionskörper. Aus vorhandener Geometrie mit dem Unreal-Merge-Werkzeug erzeugt. Zwei Lab-Instanzen und eine Sandbox-Instanz referenzieren exakt dasselbe Mesh bei Einheitsskalierung. Die zweite Lab-Instanz demonstriert einen separaten Material-Override.
- Sechs neue Materialinstanzen unter `/Game/Art/Materials` verwenden den vorhandenen Master `M_FlatCol`; der Rasterboden verwendet das bestehende Grid-Material. `Art/Architecture`, `Nature`, `Furniture` und `Materials` bilden die neue Bibliotheksstruktur. Die beiden zunächst leeren Ordner werden über `.gitkeep` erhalten; vorhandene Natur- und Gameplay-Assets wurden weder verschoben noch kopiert.
- Eine zusätzliche Instanz von `BP_PrototypeDoor` mit `BP_PrototypeDoorFrame` demonstriert im Lab unverändert das bestehende Interaktionssystem. E öffnet und schließt die Tür, das vorhandene Widget zeigt den passenden Aktionstext, das Blatt wird gold hervorgehoben.

Die neue Datei `Source/FantasyLifeRPG/Prototype/Tests/AssetWorkspaceTests.cpp` ergänzt ausschließlich editorseitige Prüfungen. Sie lädt die gespeicherten Karten, wartet auf initialisiertes PIE und prüft tatsächliche Enhanced-Input-Ereignisse für W, Maus, Leertaste sowie E an der Lab-Tür. Zusätzlich prüft sie Bodengröße und Bodentreffer, Wandmaße/Pivot, gemeinsame Mesh-Referenz, Einheitsskalierung, einfache Wandkollision mittels Spielerkapsel, drei sichtbare Bereichslabels, Podeste, 100-cm-Rasterparameter und unabhängige Materialänderungen. Materialänderungen erfolgen nur vorübergehend an PIE-Komponenten; gemeinsame Assets bleiben unverändert. Beide Tests warten auf vollständigen Sitzungsabbau.

Tatsächlich durchgeführte Prüfungen:

| Prüfung | Ergebnis |
| --- | --- |
| Editor-Build `FantasyLifeRPGEditor Win64 Development` | Erfolgreich, 12,88 s; abschließender Build ohne Compilerwarnungen |
| Neue Kartentests nach Editorneustart | 2/2 erfolgreich, 7,26 s; eine bekannte Crowd-/Recast-Warnung beim ersten Weltwechsel |
| Gemeinsame Suite einschließlich aller sechs bisherigen Tests | 8/8 erfolgreich, 65,21 s; keine Testfehler, vier bekannte Crowd-/Recast-Warnungen |
| Neue Kartentests nach abschließender Beschriftungskorrektur | 2/2 erfolgreich, 6,73 s; keine Testfehler oder Testwarnungen |
| Gerenderte Prüfung im schwebenden PIE-Spielfenster | Lab-Startansicht, sichtbare Türhervorhebung mit „E – Tür öffnen“ und Sandbox mit Figur/Boden/Tageshimmel geprüft |
| MCP-Speicherprüfung nach Wiederöffnen beider Karten | Alle neun neuen Unreal-Assets vorhanden und `dirty=false` |

Die gemeinsame Suite umfasst `AssetWorkspace.AssetLabPIE` (3,97 s), `AssetWorkspace.WorldSandboxPIE` (2,91 s), `Environment.NavigationPIE` (31,69 s), `Environment.PlayablePIE` (15,45 s), `Interaction.DoorPIE` (5,14 s), `Interaction.FeedbackPIE` (3,62 s), `Interaction.PrototypePIE` (2,39 s) und `Interaction.Rules` (0,03 s), jeweils mit Präfix `FantasyLifeRPG.`. Damit bestehen auch die bisherigen Prüfungen für NPC-Route, Umgebung, Tür, Anzeige, Hervorhebung und Interaktionsregeln weiterhin. Alle Testläufe endeten ohne aktive PIE-Sitzung.

Bei der zusätzlichen Sichtprüfung verdeckte ein Bedienhinweis nahe dem Spawn zunächst die Kamera. Die drei Begrüßungs-/Bedienungstexte stehen jetzt seitlich; die freie Startansicht wurde im Spielfenster erneut kontrolliert. Die abschließende Wiederholung betrifft beide neuen Karten. Die bestehenden sechs Tests wurden zuvor gemeinsam erfolgreich ausgeführt; die Textplatzierung verändert deren Karten oder Gameplay nicht.

Seit Beginn der gemeinsamen Suite wurden keine Error-Logeinträge gefunden. Beim normalen deutschen Editorstart bestehen weiterhin die bekannten 17 Engine-Selbsttestmeldungen `Condition failed`; die zuvor dokumentierten Crowd-/Recast-Warnungen treten bei Weltwechseln auf. Diese Meldungen wurden nicht unterdrückt und die zugehörigen Engine-/Plugin-Einstellungen nicht verändert. Die GameFeatureData-Startfehler kehrten nicht zurück. Es ist daher kein vollständig meldungsfreier Editorstart behauptet.

**Speicherzustand und Umfang:** Der Vergleich gegen SHA-256-Werte von 995 zuvor vorhandenen Projektdateien bestätigt, dass mit Ausnahme dieser fortgeschriebenen Statusdokumentation keine bestehende Datei verändert wurde. Das schließt beide bisherigen Prototypkarten, ursprüngliche Template-Levels, vorhandene Blueprints/Meshes, C++-Implementierungen, Konfiguration und Worldbuilding ein. Die neuen Dateien sind gespeichert, aber nicht committed; der bereits vor Auftrag vorhandene uncommittete Entwicklungsstand bleibt bestehen. Keine Commits, Pushes oder Staging-Aktionen.

**Offene manuelle Prüfungen und Grenzen:** Beide Karten längere Zeit mit Tastatur/Maus ablaufen, Kameragefühl und Kontakte an Podesten/Wänden prüfen sowie Beschriftungslesbarkeit und Materialwirkung aus verschiedenen Blickwinkeln beurteilen. Die automatisierten Prüfungen decken konkrete Kollisionen und Eingaben ab, keinen flächendeckenden Hindernisparcours oder Performancebenchmark. Die Sandbox besitzt offene Außenkanten und kein Rücksetzsystem; das Lab hat überspringbare niedrige Randbegrenzungen. Die Tür behält ihre bisherigen Einschränkungen. Blender-Import, finale UVs/Art-Qualität, Packaging/Cooking und Multiplayer sind nicht getestet. Vor Ausbau der Welt zunächst ein weiteres Rastermodul oder ein einzelnes importiertes Modell nach dem dokumentierten Lab→Sandbox-Ablauf prüfen.

Vollständige Dateiliste, Namens-/Maß-/Pivotregeln, Material- und Kollisionsworkflow sowie Vorbereitung späterer Blender-Modelle: [technical/ASSET_PIPELINE.md](technical/ASSET_PIPELINE.md). Ignorierte lokale Belege: `Saved/InteractionDev/asset_workspace_build.log`, `asset_workspace_tests_all.json`, `asset_workspace_tests_new.json`, `asset_workspace_saved_audit.json`, `asset_workspace_baseline.json` und `asset_workspace_*_game.png`. Der Editor bleibt abschließend im gespeicherten `Lvl_AssetLab`, ohne PIE; die konfigurierte Startkarte bleibt `Lvl_EnvironmentTest_01`.

## Developer Toolbox V1 – 22. Oktober 2026

Die Toolbox ist am bestehenden `BP_PrototypePlayerController` aktiviert und damit in allen vier Prototypkarten verfügbar. **F6** ersetzt das gewünschte F7, weil F7 im Engine-Blueprint-Editor bereits `CompileBlueprint` auslöst und im Behavior-Tree-Vergleich ebenfalls verwendet wird. Bare F6 besitzt in den geprüften Projekt-/Editorbelegungen keinen Konflikt. F1 und bestehende Input-Assets/-Konfigurationen bleiben unverändert.

Die UMG-Oberfläche trennt Spieler, Effekte und Simulationen. Die Welt wird nicht pausiert; das offene Panel gibt den Mauszeiger frei und unterdrückt Gameplay-Eingaben. F6, ESC oder die Schließen-Schaltfläche geben Spielfokus und die vom Panel gesetzten Eingabesperren frei. Externe Bewegungs-/Blicksperren bleiben erhalten. Aktiv gewählte Werkzeuge bleiben nach dem Schließen bedienbar und werden einzeln oder über Reset beendet; beim PIE-/Welt-/Komponentenabbau wird aufgeräumt.

- `Development/DeveloperToolboxComponent.*`: opt-in aktivierte Steuerungslogik mit temporärem Enhanced-Input-Kontext. Flug und NoClip getrennt schaltbar, WASD horizontal, Maus, Leertaste/Strg vertikal im Flug, einstellbare 100–5000 cm/s und optional dreifaches Tempo mit Shift. NoClip allein hält ohne Schwerkraft die Höhe; der bestehende CharacterMovement-Flugmodus wird intern wiederverwendet. Beim Abschalten werden ursprüngliche Bewegungs-/Kollisionseinstellungen wiederhergestellt. Eine Kapselprüfung verhindert im geprüften Wandfall das Einschließen; ohne freien Rückkehrpunkt bleibt NoClip mit Meldung aktiv.
- Die freie Kamera ist ein temporärer CameraActor mit separatem Tempo. Sie übernimmt weder Besitz noch Gameplay-Kamera-Komponenten. ViewTarget und ControlRotation werden beim Beenden wiederhergestellt. Auch Pawn-Wechsel und Verlust des eigenen Kameraziels werden behandelt.
- `Development/DeveloperToolboxWidget.*`: tatsächlicher UMG-WidgetTree, drei Karten mit Scrollbereich, Schaltflächen, Auswahllisten und Geschwindigkeitsfeldern. UI und Steuerungslogik sind getrennt.
- `Development/DeveloperEffectTester.*`: katalogisierte vorhandene Niagara-Systeme `NS_Damage` und `NS_JumpPad`, Auslösung am Spieler oder an einer Testposition über Sicht-/Bodenabfrage, maximal acht aktive Toolbox-Effekte und gezieltes Stoppen. Keine Effektassets verändert oder neu erstellt. Erster Aufruf kann synchrones Laden/Niagara-Kompilieren benötigen.
- `Development/DeveloperScenario.*`: erweiterbare Adapter mit Verfügbarkeitsprüfung und Start-/Stop-Grenze. V1 bindet ausschließlich vorhandene `WaypointMovementComponent`-Routen an. Reset stellt zuvor laufende beziehungsweise gestoppte Routen wieder her; ein Neustart beginnt an Wegpunkt 1. In Karten ohne Route sind die Aktionen deaktiviert. NPC-Spawn, Wetter, Tageszeit und Zeitraffer bleiben ausdrücklich nicht verfügbar.

**Freigabe:** Jeder öffentliche Steuerungseinstieg prüft zusätzlich zur UI die Laufzeitbedingungen. In Shipping ist `CanUse()` per Compile-Guard stets false. Außerhalb Shipping sind Blueprint-Opt-in, lokaler Controller, Spielwelt, Autorität und `NM_Standalone` erforderlich. Netzwerksitzungen einschließlich Listen-Server bleiben gesperrt. Keine Admin-RPCs oder rein clientseitig geschützten Serveraktionen. Eine spätere Multiplayer-Freigabe benötigt serverseitige Berechtigungen. Tatsächliche Shipping-Ausführung und Netzwerkprozesse wurden in diesem Auftrag nicht getestet.

| Tatsächlich durchgeführte Prüfung | Ergebnis |
| --- | --- |
| Abschließender Editor-Build einschließlich erweiterter Tests | Erfolgreich, 9,82 s; keine Compilerwarnungen |
| Separater Kontrolltest nach Editorneustart | 1/1 erfolgreich, 18,98 s, einschließlich gerendertem Panel und echter Slate-ESC-Eingabe |
| Gemeinsame Suite mit allen acht bisherigen Tests und fünf Toolbox-Tests | **13/13 erfolgreich**, 73,03 s; keine Testfehler, sechs bekannte Crowd-/Recast-Warnungen |
| Gezielte Wiederholung aller fünf um zusätzliche Aussagen erweiterten Toolbox-Tests nach weiterem Editorneustart | **5/5 erfolgreich**, 10,54 s; keine Testfehler, drei bekannte Crowd-/Recast-Warnungen |
| Speichern/Wiederöffnen über MCP | Prototyp-Controller, vier Karten und beide Effektassets vorhanden, jeweils `dirty=false`; PIE beendet |

Die fünf neuen Tests sind `FantasyLifeRPG.DeveloperToolbox.ControlsPIE` sowie `FantasyLifeRPG.DeveloperToolbox.MapsPIE.Lvl_AssetLab`, `.Lvl_WorldSandbox`, `.Lvl_Prototype_01` und `.Lvl_EnvironmentTest_01`. Sie prüfen F6 über PlayerController/Enhanced Input, F6-Schließen, unterdrückte Bewegung/Sprung im Menü, nicht pausierte Welt, Cursor-/Sperrrückgabe, UMG-Button-Callbacks und SpinBox-Signale. Der Kontrolltest schließt ESC über den tatsächlichen Slate-Eingabeweg des fokussierten Panels und prüft, dass PIE weiterläuft. Weiter geprüft: W/Leertaste/Strg im Flug, Tempo/Shift, NoClip unabhängig vom Flug, Rückkehr aus einer Wand an den zuvor freien Punkt, freie Kamerabewegung bei stillstehender Figur, ViewTarget-/Rotationsrückgabe, beide Effektauslösungen, Instanzlimit/Stoppen und Backend-Ablehnung bei deaktivierter Toolbox. Jeder Kartentest beendet PIE mit aktivem Menü, Flug, NoClip, freier Kamera und Testeffekt. Im Environment-Level werden außerdem NPC-Routen und Reset für ursprünglich laufende sowie gestoppte Routen geprüft. Die letzte Änderung erweiterte ausschließlich Testaussagen; die Toolbox-Implementierung blieb gegenüber der erfolgreichen 13er-Suite unverändert.

Während der Entwicklung wurde ein eigener Niagara-Aufräumfehler gefunden: `DeactivateImmediate()` konnte die automatisch zerstörende Komponente synchron ungültig machen; der folgende Zugriff über dieselbe schwache Referenz verursachte einen Editorabsturz. Der kontrollierte Abbau hält jetzt eine lokale Referenz, schaltet AutoDestroy ab und prüft vor dem Zerstören erneut. Die abschließenden Stress-/Wiederholungsläufe stammen aus dem korrigierten Stand. Frühe F6-Kaltstartproben begannen außerdem vor den anfänglichen Eingabe-/Fokusframes und schlugen fehl, während die Wiederholung bestand. Der temporäre Kontext erhält nun ausdrückliche Rebuild-Optionen; die Testfixture wartet vor einem einzelnen, nicht wiederholten Tastendruck mindestens 0,35 s Weltzeit. Die erfolgreichen Proben protokollieren eine aufgebaute, nicht ignorierte F6-Zuweisung. Die fehlgeschlagenen Zwischenstände werden nicht als erfolgreiche Tests ausgegeben.

Die gerenderte Oberfläche wurde kontrolliert; ein Beleg liegt unter `Saved/InteractionDev/toolbox_panel.png`. Während der abschließenden Tests gab es keine Error-Logeinträge. Die bekannten Crowd-/Recast-Weltwechselwarnungen und die 17 bereits zugeordneten Engine-Selbsttestfehler beim deutschen Editorstart bleiben bestehen. Es wurde keine globale Engine-, Plugin-, Sprach- oder Input-Konfiguration geändert.

**Umfang/Speicherung:** Neu sind vier C++-Klassenpaare unter `Development/`, eine Testdatei und [technical/DEVELOPER_TOOLBOX.md](technical/DEVELOPER_TOOLBOX.md). Bestehende Änderungen dieses Auftrags sind das native Controller-Subobjekt in `FantasyLifeRPGPlayerController.h/.cpp`, die private Niagara-Modulabhängigkeit, Aktivierung/Effektkatalog im `BP_PrototypePlayerController` und diese Statusdokumentation. Ein Hashvergleich gegen 1007 zuvor vorhandene Projektdateien grenzt die Änderungen ab; Karten, bisherige Gameplay-/NPC-/Interaktionsimplementierungen, ursprüngliche Templates, Effekt-/Inputassets, Konfiguration und Worldbuilding bleiben unverändert. Alle Änderungen sind gespeichert. Der vorhandene uncommittete Stand bleibt erhalten; keine Commits, Pushes oder Staging-Aktionen.

**Manuell offen:** Physische F6-/ESC-Bedienung bei unterschiedlichen Fenster-, Dropdown- und SpinBox-Fokuszuständen, vollständige Mausbedienung, längeres Fliegen und NoClip an komplexeren Kollisionen, Material-/Effektwirkung aus verschiedenen Blickwinkeln sowie freie Kamera über längere Sitzungen. Die Rückkehrprüfung ist an der vorhandenen Wand bestätigt, kein allgemeiner Suchalgorithmus für beliebig veränderte oder vollständig blockierte Welten. Packaging/Cooking, Shipping-Laufzeit, Split-Screen, Controller/Touch und Multiplayer bleiben ungetestet. Vollständige Bedienung und Erweiterungspunkte stehen im verlinkten Toolbox-Dokument. Lokale ignorierte Belege: `toolbox_build_final.log`, `toolbox_tests_all.json`, `toolbox_tests_new.json`, `toolbox_tests_controls.json`, `toolbox_configuration.json`, `toolbox_saved_audit.json` und das frühere Fehlerlog `toolbox_effect_cleanup_crash.log`, jeweils unter `Saved/InteractionDev/`. Abschließend ist `Lvl_AssetLab` ohne PIE geöffnet; die Startkarte bleibt `Lvl_EnvironmentTest_01`.

## Toolbox-Steuerung: Mausachse, Bremsung und Sprint – 22. Oktober 2026

Die freie Kamera blickt mit Mausbewegung nach unten jetzt nach unten. Die vorherige zusätzliche Invertierung wurde ausschließlich in der freien Kamera entfernt; die normalen Kamera-/Inputassets bleiben unverändert. Flug und NoClip stoppen beim Loslassen wirksamer Bewegungstasten direkt, statt mit der Standard-Flugbremsung nachzugleiten. Eine vorübergehend höhere CharacterMovement-Beschleunigung macht Anfahren, Richtungswechsel und Tempoerhöhung unmittelbar spürbar. Die Toolbox liest die Eingaben vor dem Bewegungstick; ohne Bewegungseingabe werden ausstehende Eingabe und Geschwindigkeit gelöscht. Ursprüngliche Beschleunigung, Flugtempo und Bewegungseinstellungen werden beim Modusende wiederhergestellt.

**Linke und rechte Shift halten:** doppeltes ursprüngliches Lauftempo im normalen Charaktermodus, dreifaches eingestelltes Tempo für Flug/NoClip/freie Kamera. Beim Loslassen wird das ursprüngliche Lauftempo wiederhergestellt; im Flug wird die tatsächliche Geschwindigkeit sofort auf das Normaltempo begrenzt. Menü, Werkzeugwechsel, Pawn-Wechsel und Aufräumen behandeln auch den temporären Bodensprint. Die normalen Boden-Beschleunigungs-/Bremswerte werden dafür nicht verändert. Die bisherigen Standalone-/Shipping-Grenzen gelten weiter.

| Tatsächlich durchgeführte Prüfung | Ergebnis |
| --- | --- |
| Editor-Build `FantasyLifeRPGEditor Win64 Development` | Erfolgreich, 53,71 s; keine Compilerwarnungen |
| Neuer `FantasyLifeRPG.DeveloperToolbox.HandlingPIE` direkt nach Editorneustart | 1/1 erfolgreich, 5,04 s |
| Vollständige erweiterte Suite | **14/14 erfolgreich**, 78,10 s; keine Testfehler, sechs bekannte Crowd-/Recast-Warnungen |

Der neue Test prüft die beiden Maus-Y-Richtungen über Enhanced Input, die tatsächliche Flug-/NoClip-Geschwindigkeit mit linker beziehungsweise rechter Shift, die Rückkehr zum Normaltempo nach Shift und den Stillstand nach Loslassen anhand von Position und Velocity. Der Test bremst den Charakter dabei nicht selbst. Zusätzlich geprüft: tatsächlicher Bodensprint, ursprüngliches Lauftempo nach Loslassen und Menüöffnung, Tempo/Stillstand der freien Kamera und ursprüngliche Beschleunigung/Fluggeschwindigkeit nach Modusende. Absichtlich vom Standard abweichende Ausgangswerte verhindern, dass ein hart codierter Rücksetzwert unbemerkt besteht. Alle bisherigen Toolbox-, Karten-, Tür-, Interaktions- und NPC-Tests bleiben erfolgreich. Die aktualisierten Bedienhinweise wurden im gerenderten UMG-Panel geprüft. Während der abschließenden Tests gab es keine Error-Logeinträge; die bekannten deutschen Engine-Startmeldungen bleiben separat bestehen.

Der Umfang beschränkt sich auf `DeveloperToolboxComponent.h/.cpp`, den UMG-Hilfetext, die zusätzliche Prüfung in `Development/Tests/DeveloperToolboxTests.cpp` und technische Dokumentation. Keine Karten-, Blueprint-, Inputasset-, Konfigurations- oder Worldbuilding-Änderungen. Änderungen gespeichert, keine Commits oder Pushes. Das subjektive Spielgefühl und längere Bedienung mit physischer Maus/Tastatur bleiben manuell zu beurteilen. Bedienung und Grenzen: [technical/DEVELOPER_TOOLBOX.md](technical/DEVELOPER_TOOLBOX.md). Lokale ignorierte Belege: `Saved/InteractionDev/toolbox_handling_build.log`, `toolbox_handling_tests_handling.json`, `toolbox_handling_tests_all.json` und `toolbox_handling_baseline.json`. Abschließend ist `Lvl_AssetLab` ohne PIE geöffnet.

## Elfisches Wohnhaus: Blatthof-Stilstudie 01 – 22. Oktober 2026

Auf Grundlage des vom Nutzer ausgewählten unteren Fantasy-Entwurfs C steht jetzt ein erstes begehbares Hausmuster im hinteren Architektur-Bereich von `Lvl_AssetLab`: Outliner `Lab/Architecture/ElvenBlatthof`, Actor `Lab_ElvenBlatthof_StyleStudy`, Position `(-1900,1200,0)`. Es verbindet gebogene helle Wände, ein grünblaues Blattdach, Holzrippen, Fenstermaßwerk und einen Hof mit Pflanzen- und Wasserplatzhaltern. Die Studie legt keine endgültigen elfischen Bautypen oder gesellschaftlichen Zuordnungen fest; Worldbuilding bleibt unverändert.

Wiederverwendbar ist `/Game/Art/Architecture/ElvenBlatthof/BP_ElvenBlatthof_Study` mit vier getrennten Meshes und den unveränderten Tür-/Rahmenblueprints als ChildActors. Neun neue Materialinstanzen verwenden den vorhandenen Master `M_FlatCol`. Tür-Eingabe, Aktionstext und Hervorhebung verwenden die bestehenden Systeme. Kein neues Gameplay, kein C++, keine neuen Input- oder Engine-Einstellungen. Die Geometrie lässt sich mit `Tools/Prototype/generate_elven_blatthof.py` erneut erzeugen; Editoroperationen erfolgten über Unreal MCP.

**Tatsächlich bestätigt:** Blueprint kompiliert mit Warnungen als Fehler. MCP-Linienabfragen bestätigen Wand-/Dach-/Bodenkollision, die freie Hof-/Innenraumachse und die Sperre der geschlossenen Tür. In PIE öffnet/schließt eine tatsächliche Slate-E-Eingabe die neue Haustür, beide Aktionstexte wurden aus dem Slate-Baum gelesen und die goldene Hervorhebung im gerenderten Spielfenster gesehen. Bei offener Tür lief die Figur mit W-Eingaben von Y=1300 durch den Eingang bis zur äußeren Innenwand bei Y≈1794,99. Die vorhandenen Tests `AssetWorkspace.AssetLabPIE` und `DeveloperToolbox.MapsPIE.Lvl_AssetLab` bestehen **2/2 in 5,02 s**, ohne Testfehler/-warnungen; PIE danach beendet. Die frühere 14er-Suite und ein C++-Build wurden nicht erneut ausgeführt. Explorative, nicht unterstützte MCP-Eigenschafts-/Editorabfragen während PIE erzeugten zuvor Werkzeug-Logmeldungen; daher kein meldungsfreier Gesamtlauf behauptet.

Eine während der Sichtprüfung erkannte doppelte Skalierung der eingebetteten Tür ist korrigiert; nach Neuerzeugung der Hausinstanz und Kartenwechsel ist das Blatt 220 cm hoch. Alle 14 neuen Assets und die Lab-Karte sind gespeichert und wurden nach Wiederöffnen mit `dirty=false` geprüft. Der Hashvergleich zum Auftragsbeginn begrenzt Änderungen an zuvor vorhandenen Projektdateien auf `Lvl_AssetLab.umap` und diese Statusdatei. Neue Dateien: Haus-Blueprint, vier Meshes, neun Materialien, Generator und technische Beschreibung. Bisherige Lab-Actors, Gameplay-Assets, Sandbox/Umgebung/Template-Levels, C++, Konfiguration und Worldbuilding bleiben erhalten. Keine Commits, Pushes oder Staging-Aktionen.

**Manuell offen:** alle Seiten und beide Wohnflügel ablaufen, Rückweg/Bedienung von innen und Kamerakontakte prüfen, Form- und Materialwirkung beurteilen. Glas und Wasser sind opake Farbplatzhalter, der Innenraum ist unmöbliert, Hofdekoration trägt keine eigene Kollision. Keine Performance-/LOD-/Packaging-/Multiplayerprüfung. Der Stilprototyp ist noch kein finales Hausasset oder allgemeiner modularer Gebäudebaukasten. Maße, Assetliste, Testgrenzen und Belege: [technical/ELVEN_BLATTHOF_STUDY.md](technical/ELVEN_BLATTHOF_STUDY.md).

## Asset-Lab vergrößert und Detail-Workflow – 22. Oktober 2026

`Lvl_AssetLab` ist auf Nutzerauftrag von **60 × 40 auf 120 × 80 m** vergrößert: **9.600 m²**, vierfache bisherige Fläche. Der Boden reicht von `(-6000,-4000,-20)` bis `(6000,4000,0)`; die vier vorhandenen niedrigen Randbegrenzungen stehen an den neuen Außenkanten. Nur Boden und Randbegrenzungen wurden transformiert. Die 61 übrigen Actors behalten ihre zuvor ausgelesenen Transformationen, einschließlich Haus, Türmuster, Vergleichswände, Beschriftungen, Podeste und PlayerStart. Die bisherigen markierten Vergleichsgruppen bleiben im mittleren Bereich; außen steht freie Bau- und Vergleichsfläche zur Verfügung. Die Sandbox bleibt 120 × 120 m groß.

Die Karte wurde über Unreal MCP bearbeitet, ausdrücklich gespeichert und über einen Kartenwechsel erneut geladen. Vier Kollisionsabfragen außerhalb der alten Fläche (West/Ost bei X=±5000, Nord/Süd bei Y=±3000) treffen den erweiterten Boden auf Z=0; die gespeicherten Bodenbounds sind 12000 × 8000 cm. Die ursprüngliche 100-cm-Rastergröße bleibt erhalten. Der bestehende Maßtest in `Prototype/Tests/AssetWorkspaceTests.cpp` erwartet jetzt diese neuen Lab-Abmessungen; die Sandbox-Erwartung bleibt 12000 × 12000 cm. Keine neuen Gameplay-Systeme oder Änderungen an Gameplay-Code.

| Tatsächlich durchgeführte Prüfung | Ergebnis |
| --- | --- |
| Editor-Build einschließlich angepasster Testdatei | Erfolgreich; abschließender Build 3,05 s. Der erste Linkversuch war durch die noch im Editor geladene DLL gesperrt; nach regulärem Schließen bestand die Wiederholung. |
| `FantasyLifeRPG.AssetWorkspace.AssetLabPIE` | Abschließend erfolgreich, 3,78 s |
| `FantasyLifeRPG.AssetWorkspace.WorldSandboxPIE` | Abschließend erfolgreich, 2,90 s |
| `FantasyLifeRPG.DeveloperToolbox.MapsPIE.Lvl_AssetLab` | Abschließend erfolgreich, 1,26 s |
| Gemeinsamer abschließender Testlauf | **3/3 erfolgreich, 7,93 s**, keine Testfehler/-warnungen, PIE beendet |
| MCP-Speichern/Wiederöffnen und Bodenprüfung | Neue Maße und vier Bodenstichproben bestätigt |

Beim ersten gemeinsamen Lauf bestand das Lab bereits, während der zusätzliche Sandbox-Test einmal an der W-Bewegungsaussage scheiterte. Die separate Sandbox-Wiederholung bestand in 2,89 s, anschließend auch der gemeinsame Dreierlauf. Es wurde keine Ursache für diesen einzelnen Eingabe-Testfehler nachgewiesen und kein unbelegter Gameplay-Fix vorgenommen. Die Sandbox-Datei und Eingabeimplementierung sind gegenüber Auftragsbeginn unverändert. Bei erneutem Auftreten den Start-/Eingabezeitpunkt dieses Tests gezielt untersuchen. Die vollständige frühere 14er-Suite wurde nicht erneut ausgeführt.

Der in [technical/ASSET_PIPELINE.md](technical/ASSET_PIPELINE.md) ergänzte Ablauf empfiehlt zunächst mehrere einfache Stilmuster im Lab: Silhouette, Maßstab, Grundriss, Farbflächen, Kollision und Begehbarkeit beurteilen. Nach Auswahl eines zusammenpassenden Satzes ein repräsentatives Modell in Blender mit sauberer Geometrie, Normalen, UVs, Materialslots und passender Kollision ausarbeiten. Details gezielt ergänzen; mehr Polygone sind kein Selbstzweck. Pivot, Maße und Referenzen beim Austausch erhalten. Blender-Modelle wurden in diesem Auftrag nicht erstellt oder importiert.

**Umfang/Speicherung:** Gespeicherte Änderungen an Lab-Karte, einer bestehenden Testaussage, Asset-Pipeline und dieser Statusdokumentation. Gebäude-/Türassets, Sandbox und übrige Levels, Gameplay-Implementierungen, Konfiguration und Worldbuilding bleiben unverändert. Kein Commit, Push oder Staging. Manuell offen: die gesamte zusätzliche Fläche und neue Randkanten ablaufen, Kameragefühl und Abstände beurteilen. Die bisherigen überspringbaren Randbegrenzungen bleiben bestehen; kein neues Rücksetzsystem. Lokale ignorierte Belege: `Saved/InteractionDev/elf_expand_lab_result.json`, `lab_expand_build.log` (gesperrter erster Linkversuch), `lab_expand_build_final.log`, `lab_expand_tests.json`, `lab_expand_sandbox_retry.json`, `lab_expand_tests_final.json` und `lab_expand_final_audit.json`. Abschließend bleibt das gespeicherte Lab ohne PIE geöffnet.

## Elfisches Anschlussmuster 01 – 22. Oktober 2026

Im Asset-Lab stehen westlich der unveränderten Blatthof-Stilstudie zwei verbundene 30°-Felder unter `Lab/Architecture/ElvenJoinSample01`. Vier neue Meshassets für Boden, Innenwand, Außenwand und wiederholbares Mitteldach werden jeweils zweimal instanziert. Einheitsskalierung, gemeinsame R255-Startpivots und berechnete Anschluss-Transforms; vorhandene Blatthof-Materialien direkt wiederverwendet. Keine neuen Gameplay-, Blueprint-, PCG- oder C++-Systeme. Neue reproduzierbare Geometriequelle: `Tools/Prototype/generate_elven_join_sample.py`; der ursprüngliche Generator bleibt unverändert.

**Bestätigt:** Grenzpunkte/Normalen in der Quelle geprüft; Importdaten ausgelesen; zehn Bodenabfragen einschließlich Naht auf Welt-Z12, Wand-/Dach-/Füllbereichsabfragen und freier Gang in beide Richtungen. Tatsächlicher Spieler mit Kapselradius 35/Halbhöhe 90 überquert die Naht im Gehmodus über transiente Geschwindigkeitsimpulse vorwärts und rückwärts, Höhenvariation 0,0 cm. Ein Slate-W-Tastentest konnte mangels sichtbarer Editorfenster nicht bestätigt werden und wird nicht als erfolgreich dargestellt. Die vorhandenen Tests `AssetWorkspace.AssetLabPIE` und `DeveloperToolbox.MapsPIE.Lvl_AssetLab` bestehen **2/2 in 5,11 s**, ohne Testwarnungen/-fehler. Gespeicherte Assets und Lab nach Kartenwechsel geprüft; PIE beendet. Kein C++-Build nötig, keine vollständige Suite ausgeführt.

**Grenzen:** Beide radialen Enden offen, kein vollständiges Haus. Boden-/Wandkollision aus definierten Boxen, Dach aus acht konvexen Hüllen; `UseSimpleAsComplex`. Bodenboxen überdecken offene innere Endecken um bis ungefähr 11 cm, Dachkontakte sind noch angenähert. Manuelle WASD-/Kameraprüfung bleibt offen. Die ursprünglichen Hausassets und vorhandenen Lab-Actors bleiben erhalten. Details, Pfade, Geometriezahlen, Erhaltungsprüfung und lokale Belege: [technical/ELVEN_JOIN_SAMPLE_01.md](technical/ELVEN_JOIN_SAMPLE_01.md).

## Geschlossenes modulares Elfenhaus 01 – 22. Oktober 2026

Das zweifeldrige Anschlussmuster ist jetzt als `BP_EB_House_A60_Prototype01` mit Eingang und beiden Endabschlüssen geschlossen. Lab: `Lab/Architecture/ElvenClosedHouse01`, Actor `Lab_EBHouse_Closed01` bei `(-4400,1000,12)`. Neun statische Meshkomponenten verwenden die bisherigen Böden/Außenwände/Dächer und drei neue Abschluss-/Eingangsmeshes; zwei ChildActors verwenden die unveränderten `BP_PrototypeDoor` und `BP_PrototypeDoorFrame`. Die vorherigen acht Muster-Actors wurden durch die Hausinstanz ersetzt. Stilstudie und bisherige Modulassets bleiben erhalten.

**Geprüft:** Geschlossene Hülle einschließlich Dachanschlüssen, freie Türöffnung nach Öffnen und Sperre durch das geschlossene Blatt. Tatsächlicher Spieler wird geschlossen blockiert, öffnet über den vorhandenen `TryInteract`-Pfad, geht hinein, schließt/öffnet innen, geht hinaus und schließt außen. Bewegung über transiente CharacterMovement-Impulse ohne Durchgangsteleport/NoClip; kein physischer Tastaturtest behauptet. Rahmen bleibt unverändert, goldene Türhervorhebung nachgewiesen. Drei bestehende Tests einschließlich `Interaction.DoorPIE` bestehen **3/3 in 10,39 s**, ohne Testwarnungen/-fehler. Abschließende Endflächenabdeckung statisch/visuell geprüft, Assets und Lab gespeichert und wieder geladen. Temporäre Prüf-Hilfe entfernt; kein neuer Gameplay-Code, PCG, C++-Build oder Änderung bestehender Türlogik.

Quelle und Grenzen: [technical/ELVEN_CLOSED_HOUSE_01.md](technical/ELVEN_CLOSED_HOUSE_01.md). Manuelle E-/WASD-/Kameraprüfung bleibt offen. Keine Fenster/Möblierung oder finale Material-/Kollisionsoptimierung. Ursprüngliche Stilstudien-, Tür- und Materialassets sowie übrige Karten bleiben unverändert.

## Blender→Unreal-Kalibrierung 01 – 22. Oktober 2026

Der isolierte Static-Mesh-Kalibrierungsimport mit Blender 5.2.2 LTS und Unreal 5.8 ist durchgeführt. Neues Testmesh, drei Materialinstanzen und eine eigene Prüfkarte liegen ausschließlich unter `/Game/Art/Calibration/BlenderUE01`; editierbare Quelle, FBX, Manifest, ausgelesenes Importprofil und Ergebnis unter `AssetSources/Calibration/BlenderUE01`. Generator: `Tools/AssetPipeline/blender_ue_calibration.py`.

Bestätigt: 100 × 60 × 40 cm, unterer Ursprung, Einheitsskalierung, dokumentierte Achsenabbildung, drei stabile Materialslots, isolierter Instanz-Override, drei UCX-Hüllen, gedrehte Instanz, vier Abfragen am Modulstoß, sieben zusätzliche einfache Kollisionsabfragen und Erhalt der Referenzen nach gezieltem klassischem Reimport und Kartenwechsel. 36 Dreiecke, 72 Render-Vertices, ein LOD, Nanite aus. Keine Gameplay-/PIE-/Performance- oder Packagingabnahme.

Wichtige Korrektur: Das frühere `FBX_SCALE_UNITS`-Startprofil lieferte um Faktor 100 zu kleine Geometrie. Geprüft ist `FBX_SCALE_NONE` mit `UE_cm=(100*B.x,-100*B.y,100*B.z)`. Der normale UI-Reimport wechselte zunächst vom klassischen FBX-Importer zu Interchange und behielt alte Kollisionshüllen. Der abschließende gezielte `FbxFactory`-Import aktualisiert auch diese korrekt. Importer deshalb ausdrücklich beibehalten; Interchange bleibt ungeprüft. Sitzungs-CVar zurückgesetzt, unbeabsichtigte Vorschaukonfiguration byteidentisch wiederhergestellt. Vor Dokumentationsänderungen waren alle 1.051 vorhandenen versionierten Dateien identisch zur Ausgangslage. Bestehende Assets und Level bleiben unverändert; ursprüngliches Asset-Lab wieder geöffnet und nicht dirty. Vollständige Werte, Grenzen und Belege: [BLENDER_UNREAL_CALIBRATION_01.md](technical/BLENDER_UNREAL_CALIBRATION_01.md).

## Noch offene technische Entscheidungen

Die Repository-Einrichtung bestätigt keine endgültige Gameplay-, Networking-, Persistenz-, Weltsimulations- oder Deployment-Architektur. Diese Punkte bleiben gemäß [IMPLEMENTATION_APPROACH.md](IMPLEMENTATION_APPROACH.md) offen, bis sie ausdrücklich entschieden und dokumentiert werden.


## Elfenhaus B02 im Refiner-Lab – 23. Oktober 2026

Der Nutzer hat die erste gerade Hausstudie positiv bewertet und ausdrücklich das Refiner-Lab als Ziel gewählt. Beide Hauslängen (10 × 12 m und 10 × 16 m) stehen jetzt im südlichen Bereich von `/Game/Prototype/Maps/Lvl_AssetLab`, Outliner `Lab/Architecture/ElvenHouseB02`. Bestehende Lab-Actors und Beleuchtung bleiben erhalten; das Hauptprojekt ist unverändert. Maße und Stil bleiben eine Prototyp-Arbeitsrichtung.

22 separat instanzierte `BP_EH_Window_Arch_100x173` ersetzen die integrierten opaken Fenster. Die eigene Blender-Kopie teilt jedes ursprüngliche Fensterfeld in Wandöffnung (744 Dreiecke), Rahmen/Fensterbank (456) und Scheibe (72); zusammen unverändert 1.272 Dreiecke. Eigenes klares Substrate-Simple-Volume-Material ermöglicht Durchsicht, die Scheibe blockiert weiterhin physikalisch. Rahmen werfen Schatten, die klare Scheibe keinen opaken Schatten. Bestehende Materialien und Blueprints wurden nicht geändert.

Quelle erneut geöffnet, drei FBX-Rückimporte, Legacy-Unreal-Import/Reimport, Größen/Slots/UCX 7/0/1, alle 22 Öffnungen, Speichern/Wiederöffnen und der tatsächliche E-/W-Türlauf im Lab bestanden. Ein kontrollierter Bildvergleich mit temporärem opakem Fensterverschluss bestätigt den Sonnenlichtfleck im Innenraum; Testobjekte sind entfernt. Kein Performance-/Produktionsnachweis. Status review_ready; Innenausbau, obere Zusatzkollisionen und weitere Fenster-/Hausvarianten bleiben offen.

Vollständige Pfade, Montagevertrag, Messwerte, Ansichten und Grenzen: [B02-Review](../AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Refiner/HouseStudy_B01/WindowUpdate_B02/REVIEW.md). Eigenständige ursprüngliche B01-Prüfkarte und sämtliche Quellen des Ausgangsstands bleiben erhalten. Dieses Update ist noch nicht committet oder gepusht.

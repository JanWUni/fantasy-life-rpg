# NPC-Route und Interaktionsverbesserungen

Stand: 21. Oktober 2026, Unreal Engine 5.8. Kleine Erweiterung der neutralen Prototypwelt; keine NPC-Simulation oder Lore-Festlegung.

## Ausprobieren und im Editor einstellen

`/Game/Prototype/Maps/Lvl_EnvironmentTest_01` öffnen und Play starten. Der NPC beginnt an der Lichtung, wartet und läuft anschließend eine wiederholte Route neben dem Haus. Der Spieler kann ihn auch während des Laufens mit E ansprechen. Die Route pausiert dann drei Sekunden, der NPC dreht sich zum Spieler und die bestehende Begrüßung erscheint. Danach setzt er seinen Weg fort.

Im Outliner unter `Environment/Navigation` liegen drei `TargetPoint`-Actors und `Environment_NavBounds`. Die Wegpunkte heißen `NPC_Route_01`, `NPC_Route_02` und `NPC_Route_03`, ungefähr bei `(1400,1030,80)`, `(1750,1700,80)` und `(1450,1750,80)` cm. Sie können im Editor verschoben werden. Am platzierten `Environment_GreetingNPC` enthält die Komponente `WaypointMovement` die geordnete Referenzliste `Waypoints`. Der Prototyp verwendet drei Punkte; die Komponente kann auch andere Listenlängen durchlaufen.

- `WaitSeconds`: Wartezeit pro Ankunft, gespeichert 1,5 Sekunden. Null wird auf mindestens einen kurzen Timerschritt begrenzt.
- `WalkSpeed`: 160 cm/s; `AcceptanceRadius`: 25 cm; `RetrySeconds`: eine Sekunde bei fehlgeschlagener Pfadanfrage.
- `bAutoStart`, `StartRoute`, `StopRoute`, `PauseFor`: Route automatisch starten, explizit steuern oder befristet pausieren. Eine erneute Pause verlängert die laufende Pause. Beim Pausieren während einer Wartephase wird deren Restzeit erhalten.
- `GetRouteState`, `GetWaypointIndex` und `GetCompletedVisits`: Blueprint-Abfragen für Diagnose und weitere Prototypen.
- Neue Ziele müssen auf erreichbarer NavMesh-Fläche liegen. Nach Änderungen an statischer Geometrie oder Navigationsgrenzen Navigation im Editor neu bauen/aktualisieren und speichern. Die aktuelle Route bleibt außerhalb des Hauses; das Passieren einer sich öffnenden Tür durch den NPC ist nicht Bestandteil dieses Prototyps.

## Technische Umsetzung

`NPC/WaypointMovementComponent.*` ist eine Actor-Komponente für einen `ACharacter` mit nativem `AAIController`. Sie arbeitet nur auf Autorität, fordert Pfade über `AAIController::MoveTo` an und reagiert auf `UPathFollowingComponent::OnRequestFinished`. Partielle Pfade gelten nicht als Ankunft. Native Timer steuern Warten, Wiederholung und Pausen; die Komponente hat keinen Tick. Fehlgeschlagene Ziele werden mit Abstand erneut versucht, zerstörte Ziele werden übersprungen und eine leere/ungültige Route wird gestoppt. `StopRoute`/EndPlay entfernen Timer und Delegate-Bindung und stoppen die Bewegung. Der Component-Code kennt weder die NPC-Interaktion noch ein Widget.

`NPC/PrototypeLocomotionComponent.*` ist eine separate, einfache Darstellungskomponente. Sie wählt anhand der tatsächlichen Geschwindigkeit zwischen den vorhandenen Assets `MM_Idle` und `MF_Unarmed_Walk_Fwd`. Der Wechsel wird alle 0,1 Sekunden geprüft; dieselbe Animation wird nicht ständig neu gestartet. Die Lauf-Abspielrate folgt ungefähr der Geschwindigkeit. Dies ist eine Platzhalter-Umschaltung mit harten Übergängen, kein neues Animations-/Motion-Matching-System.

`BP_EnvironmentNPC` verbindet die Module: `OnSpokenTo` ruft vor der bestehenden Nachricht `WaypointMovement.PauseFor(3)` auf. Die native NPC-Interaktion validiert weiterhin Sicht, Reichweite, Aktivierung und Autorität. Die Ausrichtung zum Sprecher folgt nach dem Blueprint-Ereignis, sodass ein gestoppter Lauf sie nicht sofort überschreibt. Die C++-NPC-Klasse besitzt keine Abhängigkeit von der Bewegungskomponente oder der UI.

Die Navigation wurde über Unreal MCP im Prototyp-Level angelegt und gespeichert: `NavMeshBoundsVolume`, Recast-Navigationsdaten und drei TargetPoints. Die Grenzen decken ungefähr 78 × 78 Meter ab; der Rand des 80-Meter-Geländes bleibt außerhalb. Der Recast-Agent ist auf Radius 42 cm und Höhe 192 cm eingestellt. Eine Teilstrecke wird durch die bestehende Bank blockiert und benötigt einen Umweg. Es wurden keine Template-Levels oder globalen Navigations-/Crowd-Einstellungen geändert. `NavigationSystem` ist als private Editor-Abhängigkeit für die Integrationstests eingebunden; die Bewegung nutzt das bereits vorhandene `AIModule`.

## Gemeinsame Interaktionstexte

`IInteractable.GetInteractionText` liefert ausschließlich die Aktion. Die vorhandene Feedback-Komponente fragt diese auch beim gleichbleibenden Ziel erneut ab. Das vorhandene `InteractionPromptWidget` formatiert „E – {Aktion}“ und aktualisiert seinen Text ohne zweites Widget oder zusätzliche Eingabebelegung.

- Tür: Der vorhandene `BP_PrototypeDoor` liefert abhängig von seinem bereits vorhandenen `bIsOpen` „Tür öffnen“ bzw. „Tür schließen“. Beide platzierten Türinstanzen nutzen diese Funktion.
- NPC: „Sprechen“, über `InteractionAction` einstellbar.
- Andere einfache Objekte: `InteractableActor.InteractionAction`, mit „Interagieren“ als Rückfall bei leerem Text. Der bisherige Testwürfel behält diesen Rückfall.

Der Hinweis ist 360 × 56 UI-Einheiten groß, damit auch die Türtexte Platz finden. Zielauswahl, Reichweite, Sichtlinie, goldene Hervorhebung und die bestehende Nachrichtendarstellung bleiben erhalten. Es gibt kein neues Dialog- oder Inventarsystem.

## Tatsächlich erfolgreiche Prüfungen

Vor Beginn bestanden die bisherigen fünf Tests erneut. Nach der Erweiterung sind **alle sechs Tests erfolgreich**, geprüft in einem Lauf der fünf bisherigen Tests und einem anschließenden Navigationstest. Es gab keine abschließenden Testfehler. Die Navigationswelt erzeugt allerdings die unten dokumentierten Engine-Warnungen beim Weltwechsel.

- Editor-Build `FantasyLifeRPGEditor Win64 Development`: erfolgreich, einschließlich UHT, Kompilierung und Link, ohne Compilerwarnungen. Tür- und NPC-Blueprint wurden über MCP kompiliert und gespeichert.
- `Environment.NavigationPIE`: erfolgreich, ungefähr 32 Sekunden. Lädt die gespeicherte Welt nach Editorneustart, prüft drei gespeicherte Wegpunktreferenzen und deren Projektion auf NavMesh. Prüft den vollständigen Umweg um die Bank sowie sieben Ankünfte in zyklischer Reihenfolge (zwei vollständige Runden), Akzeptanzabstand und Wartezeiten in Spielzeit einschließlich Frame-Toleranz. Der erste Aufenthalt prüft die gespeicherten 1,5 Sekunden, weitere Aufenthalte eine geänderte Einstellung.
- Derselbe Test spricht den laufenden NPC über simulierte E-Ereignisse im bestehenden Enhanced-Input-Pfad an. Er prüft Zieltext, Antwort, Stillstand, Drehung zum Spieler, dreisekündige Pause und anschließendes Weiterlaufen. Idle und Laufanimation müssen beide tatsächlich aktiv gewesen sein. Außerdem geprüft: verbleibende Wartezeit nach Pause, unerreichbares Ziel ohne falsche Ankunft, Neustart nach Korrektur sowie Abbruch ausstehender Bewegung/Timer.
- `Environment.PlayablePIE`: erfolgreich. Der bestehende Test stoppt die Route ausdrücklich für seine reproduzierbare Interaktionsfixture. Er prüft weiterhin den echten Spielerweg zur Lichtung, Bodenoberflächen, Tür-Kollision, NPC-Reichweite/Sicht, Antwort und Hervorhebung. Neu geprüft: Aktionstexte vor/nach Türöffnung, „Sprechen“ und Kamera-Rückzug im Haus an der geschlossenen Tür.
- `Interaction.DoorPIE`, `Interaction.FeedbackPIE`, `Interaction.PrototypePIE` und `Interaction.Rules`: weiterhin erfolgreich. Der Feedbacktest prüft zusätzlich den generischen Aktionstext. Eingeschlossene Reichweitengrenze, blockierte Sicht und nicht erlaubte Interaktionen bleiben Teil dieser Prüfungen.
- Gerenderte PIE-Sichtprüfung: laufender NPC neben dem Haus, angesprochener/pausierender NPC mit „E – Sprechen“ und Begrüßung sowie geschlossene/geöffnete Haustür mit passendem Aktionstext. E wurde dabei auch über Slate/MCP ausgelöst. Lokale Bilder: `Saved/InteractionDev/npc_walk_final.png`, `patrol_speak_final.png`, `door_action_closed_final.png` und `door_action_open_final.png`.
- Performance-Stichprobe im erfolgreichen Navigationstest: 2.410 Frame-Samples, im Mittel 13,04 ms, Maximum 147,85 ms, ein Frame über 100 ms. Das sind Editor-Spielzeitwerte ohne Hardware-/GPU-Profiling oder Benchmark-Zusage; ein einzelner Ausreißer bleibt sichtbar.

Testcode: `Prototype/Tests/NavigationTests.cpp`, `Prototype/Tests/EnvironmentTests.cpp` und die bisherigen Tests unter `Interaction/Tests/`. Der letzte Navigationstest ist lokal unter `Saved/InteractionDev/navigation_tests_final.json` protokolliert. Eigene Editoränderungen vor dem Start der Tests speichern.

## Bekannte Grenzen und manuelle Prüfungen

- Beim PIE-Start und bei Weltwechseln/PIE-Ende erscheint `LogCrowdFollowing: Unable to find RecastNavMesh instance while trying to create UCrowdManager instance`. Im erfolgreichen Navigationstest wurden zwei solche Warnungen erfasst; auch der Umgebungstest und der Übergang zum Türtest enthalten sie. Die Engine initialisiert den optionalen Crowd-Manager, bevor passende Recast-Daten registriert sind. Der Prototyp benutzt normale AI-Pfadverfolgung; fertige NavMesh-Projektion und zwei vollständige Runden bestehen. Die Warnung wird nicht unterdrückt. Es wurden keine Engine-Änderungen oder globalen Crowd-Abschaltungen vorgenommen.
- Der Editorstart ist ebenfalls nicht logfehlerfrei: 17 Meldungen `LogAutomationTest: Error: Condition failed` vor der Engine-Initialisierung und eine fehlende Asset-Manager-Regel für `GameFeatureData`. Beide sind bereits in `FantasyLifeRPG-backup-2026.10.21-17.53.54.log` mit Startzeit 17:40 UTC vorhanden, also vor dem Bewegungsausbau. Die genaue Ursache der Start-Assertions wurde nicht vollständig untersucht. Game-Feature-Plugins werden von diesem Prototyp nicht verwendet; eine globale Asset-Manager-/Plugin-Bereinigung wurde außerhalb des Auftragsumfangs nicht vorgenommen. Nach Beginn des letzten Navigationstests und während der anschließenden Sichtprüfung wurden keine Error-Logeinträge erfasst. Das bedeutet nicht, dass die gesamte Editor-Startkonfiguration bereinigt ist.
- Nicht abschließend geprüft: bewegliche Laufzeithindernisse, NPC-Wege durch die Haustür, beliebige weitere Routen, zerstörte Wegpunkte während jeder einzelnen Bewegungsphase, längere Dauerläufe und mehrere NPCs. Kein Multiplayer/RPC/Replikation, paketierter Build, Split-Screen oder Controller-/Touch-Test. Kein Performance-Profiling unter Last.
- Mit eigener Tastatur und Kamera zur Lichtung laufen, zwei Runden beobachten und den NPC sowohl beim Warten als auch im Laufen ansprechen. Wiederholt ansprechen, die Route körperlich mit dem Spieler blockieren und nach Freigabe das Weiterlaufen beobachten.
- Im Editor Wegpunkte und `WaitSeconds` ändern, Navigation aktualisieren und die neue Route prüfen. Bei unerreichbaren Zielen bleibt der NPC im Retry-Zustand, bis ein vollständiger Weg möglich ist oder die Route gestoppt wird.
- Haustür von beiden Seiten bedienen und Kamera/Lesbarkeit an Haus, Bäumen und bei eigener Auflösung beurteilen. Die Tür schaltet weiterhin sofort, ohne Animation oder belegten Schwenkbereich zu prüfen. Die begrenzte Testwelt besitzt noch keine ausgearbeitete Weltgrenze. Die früher dokumentierten Platzhalter-UV-/Smoothing-Importhinweise bleiben bestehen.

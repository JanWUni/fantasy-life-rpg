# Gameplay-Pipeline

Stand: **23. Oktober 2026**, technischer Entwicklungsablauf für den Unreal-5.8-Prototyp. Dieser Chat bleibt der Gameplay-Chat. Die [Asset-Pipeline](ASSET_PIPELINE.md) gilt weiterhin für Creator/Refiner; Worldbuilding bleibt in seiner vorhandenen Dokumentstruktur. Der Ablauf legt keine zusätzlichen Spielregeln oder endgültige Architektur fest.

## Arbeitsorte und Ausgangsstand

| Arbeitsort | Aufgabe |
| --- | --- |
| `E:/Business/fantasy-rpg/Unreal Engine Project/FantasyLifeRPG`, Branch `main` | Gemeinsamer Integrationsstand, vorhandener Unreal-Editor und dessen lokale MCP-Anbindung |
| `E:/Business/fantasy-rpg-gameplay`, Branch `gameplay/development` | Eigener Git-Worktree für Gameplay-Code und auftragsbezogene Dokumentation |
| Vorhandene Creator-/Refiner-Worktrees | Getrennte Asset-Arbeit gemäß Asset-Pipeline; kein automatischer Wechsel ihrer Branches oder Dateien |

Der Chat-Projektordner auf C: ist kein Git-Repository. Repositorybefehle und Dateiänderungen müssen ausdrücklich den zutreffenden E:-Arbeitsort verwenden. Der Gameplay-Worktree ist ein regulärer Git-Worktree; seine Erstellung verändert die App-Zuordnung oder das Standardarbeitsverzeichnis dieses Chats nicht automatisch.

Getrennte lokale Sicherungen vor Einrichtung des Gameplay-Worktrees:

- `472a787`: Elfenfenster, Haus-/Lab-Integration, Generator und zugehörige Dokumentation.
- `c008b03`: Aufsammeln und Inventar V1, Testgegenstände/-karte, Tests und bestätigte Regeln.

Beide bauen aufeinander auf. Die Elfen- und Inventarabschnitte der gemeinsamen Statusdatei wurden jeweils nur ihrem passenden Commit zugeordnet. Die Pipeline folgt in einem eigenen Dokumentationscommit. Der Gameplay-Worktree startet vom danach vollständig gesicherten `main` und enthält dadurch beide Funktionen samt Pipeline.

Builds, Caches, lokale MCP-Konfiguration und Prüfartefakte unter `Saved/` werden nicht aus dem Hauptprojekt übernommen und nicht versioniert. Git LFS stellt die versionierten binären Inhalte bereit. Ein frischer Worktree enthält den Quell-/Assetstand; er ist damit noch kein neu gebauter oder separat in PIE geprüfter Editorstand.

## Zuständigkeiten und Parallelität

| Zuständigkeit | Verantwortung |
| --- | --- |
| Gameplay | Kleine Mechaniken anhand bestätigter Regeln implementieren, relevante Tests und Bedienhinweise pflegen |
| Asset Creator / Refiner | Getrennte Quellen und Übergaben gemäß bestehender Asset-Pipeline |
| Integration | Pro Vorgang genau eine benannte Person oder ein benannter Agent: Code übernehmen, Editor bauen, ausdrücklich erlaubte Blueprint-/Map-/Importänderungen vornehmen und das Zusammenspiel prüfen |
| Nutzer | Offene Spielregeln entscheiden und den spielbaren Stand nach Spielgefühl beurteilen |

Integration ist eine Zuständigkeit und erfordert keinen zusätzlichen dauerhaften Agenten. Dieser Gameplay-Chat kann sie für einen konkreten Auftrag übernehmen. Weitere Chats/Agenten entstehen nur auf ausdrücklichen Auftrag.

Pro Datei gibt es genau einen Schreibverantwortlichen. Besonders Charakter-/Controller-Basisklassen, gemeinsame Interfaces, `Config/`, `AGENTS.md`, `DECISIONS.md`, `GAME_SYSTEMS.md` und `TECHNICAL_STATUS.md` sind gemeinsame Berührungspunkte. Änderungen dort vor paralleler Bearbeitung abstimmen. Assetarbeit beginnt nicht gleichzeitig eine Bearbeitung derselben Map oder desselben Blueprints.

## Ablauf je Mechanik

1. **Auftrag und Regeln lesen.** `AGENTS.md`, [Spielsysteme](../GAME_SYSTEMS.md), [Entscheidungen](../DECISIONS.md), [technischen Status](../TECHNICAL_STATUS.md) und die betroffene Systemdokumentation lesen. Bestätigte Regeln von Vorschlägen unterscheiden. Nur offene Fragen klären, die den aktuellen Umfang tatsächlich verändern.
2. **Arbeitsstand prüfen.** Repositorypfad, `git status --short`, Branch, HEAD und auftragsbezogene Dateizuständigkeit erfassen. Fremde Änderungen erhalten. Einen benannten Ausgangscommit verwenden; uncommittete Änderungen sind nicht automatisch in anderen Worktrees vorhanden.
3. **Kleinen prüfbaren Umfang festlegen.** Gewünschtes Spielerverhalten, betroffene Schnittstellen, erlaubte Dateien/Assets und konkrete Erfolgskriterien notieren. Beispiel: E nimmt einen Gegenstand auf, die Anzahl erscheint im Inventar, Ablegen und Wiederaufnahme erhalten die Gesamtmenge. Keine offenen Lore-, Todes-, Speicher- oder Multiplayerregeln nebenbei entscheiden.
4. **Im Gameplay-Worktree implementieren.** Vorhandene Schnittstellen nutzen und Modell, Darstellung und Eingabe trennen. Gemeinsame Klassen nur so weit ändern, wie der Auftrag erfordert. Placeholder-Assets und separate Testkarten bevorzugen; vorhandene Assets/Levels nur im ausdrücklich beauftragten Umfang bearbeiten.
5. **Quellstand prüfen.** Im Gameplay-Worktree `git diff --check` und den passenden Editor-Build ausführen. Für Regel-/PIE-Tests eine ausdrücklich zugeordnete Editorinstanz verwenden; beim gemeinsamen Haupteditor erfolgen diese erst nach der gezielten Übernahme in Schritten 6/7. Ein erfolgreicher Build allein ist keine Gameplay-Abnahme. Noch ausstehende Laufzeittests bei einem Quellstand-Commit ausdrücklich benennen.
6. **Nacheinander integrieren.** Den auf Quell-/Build-Ebene geprüften, committeten Gameplay-Stand gezielt in `main` übernehmen; Umfang und Konflikte vorher prüfen. Den Haupteditor passend zum neuen Quellstand bauen bzw. neu starten. Erst danach damit verbundene, ausdrücklich beauftragte Editor-/Assetänderungen durchführen. Ein alter geladener Editorstand ist kein Test des neuen Codes. Fehler im Integrationsstand gezielt korrigieren und als weitere Änderung sichern.
7. **Spielbaren Stand abnehmen.** Die relevanten Regel-/PIE-Tests und gerenderten Eingabepfade prüfen: Anzeige, Fokus-/Eingaberückgabe, Reichweite, Ablehnungsfälle, Aufräumen bei PIE-Ende. Bei Änderungen gemeinsamer Eingabe-, Charakter-, Controller- oder Interaktionspfade die Regression verbreitern. Fehler reparieren und betroffene Prüfungen wiederholen; unveränderte Prüfungen nach Erfolg nur bei neuem Anlass wiederholen. Relevante Assets speichern, erneut laden und erneut kontrollieren. Das subjektive Spielgefühl bleibt eine Nutzerprüfung; Automation nicht als physische Bedienung ausgeben.
8. **Dokumentieren und sichern.** Bestätigte neue Designentscheidungen konsistent in Sachdatei und Entscheidungsregister festhalten. Systemanleitung und technischen Status mit tatsächlichen Ergebnissen und Grenzen aktualisieren. Commits auftragsbezogen trennen; lokale Logs/Screenshots bleiben unter `Saved/`. Commit-/Übernahmeaktionen nach dem konkreten Auftrag ausführen; Push und Veröffentlichung benötigen einen entsprechenden Nutzerauftrag.

## Unreal-Editor und MCP

Ein Worktree trennt Dateien, aber keine bereits laufende Editorinstanz. Die vorhandene lokale Verbindung `http://127.0.0.1:8000/mcp` ist zunächst die des Hauptprojekts. Ein Skript aus dem Gameplay-Worktree würde über dieselbe Adresse weiterhin diesen Editor steuern.

Vor jeder Editorintegration den Projektpfad der angesprochenen Instanz nachweisen und ihn mit dem Integrationsauftrag abgleichen. Den ausgeführten Quellstand, die zugehörige Editor-Binärdatei und geladene Map zusammen prüfen. Kein Import, Speichern, Kartenwechsel oder PIE-Start in einer gleichzeitig anderweitig bearbeiteten Instanz. Keine unbeaufsichtigten globalen Save-All-Aufrufe; nur die beauftragten Assets speichern.

Für V1 wird ein gemeinsamer Integrationseditor verwendet. Ein eigener Gameplay-Editor müsste ausdrücklich mit der Gameplay-`.uproject` und getrenntem MCP-Port gestartet und diesem Chat eindeutig zugeordnet werden. Port/Editor nicht automatisch aus dem aktuellen Shell-Verzeichnis ableiten. Maschinenbezogene MCP-Konfiguration nicht committen.

## Prüfungen und Übergabe

- Inventar: `FantasyLifeRPG.Inventory` und die Anleitung [INVENTORY_SYSTEM.md](../INVENTORY_SYSTEM.md).
- Gemeinsame Interaktion: relevante `FantasyLifeRPG.Interaction`-Tests, bei Menü-/Eingabeänderungen zusätzlich Toolbox- und Umgebungsfälle.
- Aktueller Ausgangsbeleg: letzter Inventar-Editor-Build erfolgreich, vollständige Suite **16/16 in 83,03 s**, bekannte Crowd-/Recast-Weltwechselwarnungen. Das ist ein bereits ausgeführter Test des Hauptprojekts; kein neuer Worktree-Test.
- Neue Mechaniken nennen ihre eigenen Erfolgskriterien; Tests nicht durch bloße Code-Nachbildung oder abgeschwächte Aussagen ersetzen.

Eine Übergabe nennt Ausgangscommit, Ergebniscommit, genaue Dateien und binäre Assets, durchgeführte Prüfungen mit Ergebnis, manuelle Restprüfungen und bekannte Grenzen. `git diff --stat <Ausgangscommit>..<Ergebniscommit>` macht den Umfang sichtbar. Für binäre Assets LFS-Zuordnung und verfügbare Inhalte prüfen; `.umap`/`.uasset` nicht als Text zusammenführen.

Nach der Übernahme den Gameplay-Worktree nur bei sauberem eigenen Stand gezielt mit dem neuen Integrationsstand abgleichen. Keine fremden Branches zurücksetzen, bestehende Creator-/Refiner-Worktrees ungefragt aktualisieren oder bereits veröffentlichte Historie umschreiben. Ein unvollständiger Auftrag bleibt als solcher dokumentiert.

# Technischer Ist-Zustand

**Stand:** 21. Oktober 2026

Diese Datei beschreibt ausschließlich den überprüften technischen Arbeitsstand. Technische Zielrichtungen und offene Architekturentscheidungen stehen in [IMPLEMENTATION_APPROACH.md](IMPLEMENTATION_APPROACH.md); verbindliche Spiel- und Weltentscheidungen stehen in [DECISIONS.md](DECISIONS.md).

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
- Die aktuellen Standard- und Editor-Startkarten verweisen auf den vorhandenen Third-Person-Template-Level.
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

## Noch offene technische Entscheidungen

Die Repository-Einrichtung bestätigt keine endgültige Gameplay-, Networking-, Persistenz-, Weltsimulations- oder Deployment-Architektur. Diese Punkte bleiben gemäß [IMPLEMENTATION_APPROACH.md](IMPLEMENTATION_APPROACH.md) offen, bis sie ausdrücklich entschieden und dokumentiert werden.

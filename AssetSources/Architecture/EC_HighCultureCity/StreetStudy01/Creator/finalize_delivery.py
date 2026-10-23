"""Write local handoff, provenance, and checksums after Blender verification/rendering."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[4]
MAIN=Path(r"E:\Business\fantasy-rpg\Unreal Engine Project\FantasyLifeRPG")

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(name,text):
    with (ROOT/name).open("w",encoding="utf-8",newline="\n") as out:
        out.write(text)

m=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
assert m["status"]=="creator_ready"
if (ROOT/"preservation.json").exists():
    m["preservation"]=json.loads((ROOT/"preservation.json").read_text(encoding="utf-8"))
    assert m["preservation"]["passed"]
a=m["module_id"]=="StreetStudy01"
folder="2026-10-23-hochkultur-stein-und-schnitzholz" if a else "2026-10-23-kultur-und-wurzelarchitektur"
image="33-geordnete-wohnstrasse.png" if a else "23-gewachsener-familienhof.png"
ref=Path(r"C:\Users\janwi\Documents\ChatGPT\Fantasy Life RPG\output\stilfindung-elfische-wohnhaeuser")/folder/image
assert sha(ref)==m["reference_image_sha256"]
(ROOT/"References").mkdir(exist_ok=True)
target=ROOT/"References"/image
if not target.exists():
    shutil.copyfile(ref,target)
assert sha(target)==sha(ref)
m["reference_image"]={"original":str(ref),"local_copy":target.relative_to(ROOT).as_posix(),"sha256":sha(target),"visually_inspected":True}
m["documentation_inputs"]=[]
for name in ["AGENTS.md","docs/technical/ASSET_PIPELINE.md","docs/technical/BLENDER_UNREAL_CALIBRATION_01.md","docs/ART_DIRECTION_REFERENCES.md","docs/DECISIONS.md"]+["docs/worldbuilding/voelker/elfen/"+p+".md" for p in ["kultur","gesellschaft","geschichte","magie"]]:
    p=REPO/name
    q=MAIN/name
    m["documentation_inputs"].append({"path":name,"worktree_sha256":sha(p) if p.exists() else None,"main_repository_sha256":sha(q) if q.exists() else None,"main_repository_read_only":True})
m["generator"]={"file":"build_study.py","sha256":sha(ROOT/"build_study.py")}
m["previews"]=[{"file":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"renderer":"Blender Cycles; 24 samples; AgX; shared neutral daylight setup","visually_reviewed":True} for p in sorted((ROOT/"Previews").glob("*.png"))]
assert len(m["previews"])==4
m["status_note"]="Creator-side prototype ready for visual review; no production, gameplay, or engine acceptance"
write("manifest.json",json.dumps(m,indent=2,ensure_ascii=False)+"\n")
write(".gitattributes","# Stable delivery bytes across Windows checkouts.\n*.py text eol=lf\n*.md text eol=lf\n*.json -text\nSHA256SUMS text eol=lf\n.gitattributes text eol=lf\n")
total=sum(e["source_stats"]["triangles"] for e in m["exports"])
hulls=sum(len(e["collision_names"]) for e in m["exports"])
rows="\n".join("| `"+e["asset_name"]+"` | "+str(e["source_stats"]["triangles"])+" | "+str(len(e["collision_names"]))+" | "+", ".join(e["source_stats"]["material_slots"])+" |" for e in m["exports"])
title="A – kultivierte Stein-/Holzstraße nach Bild 33" if a else "B – älterer Baumkörper und Wurzelhof nach Bild 23"
design=("Drei 7 × 8 m große eingeschossige Hausprototypen mit 3,9 m Wandkrone. Haus A hat ein flach gewalmtes Dach bis 5,4 m, Haus B ein niedrigeres Dach bis 5,0 m, Haus C einen kleinen steinernen Eingangsvorbau. Gemeinsame Fassaden-, Seitenwand-, Boden-, Fenster-, Tür- und Ziereinheiten; wiederholte Teile teilen Mesh-Daten. Helle langlebig wirkende Steinflächen, dunkles Schnitzholz, begrenzte Baumreliefs und kleine tiefe Fenster. Zwei geplante Straßenbäume, geordnetes Pflaster; kein Blattdach oder Wurzelhaus. Fassadenabstand 9 m, freie mittlere Straßenbreite etwa 6 m. Alle drei Innenräume bleiben leer und haben Böden und Dachabschluss. Diese Maße sind technische Studienannahmen, keine allgemeinen Baustandards."
        if a else "Drei baulich zusammenhängende Prototypmassen: älterer zentraler Baum-/Rindenkörper und zwei niedrigere gewölbte Wohnflügel. Baum- und Wurzelformen sowie gedeckte Verbindungen fassen einen geschützten Hof. Alte graubraune und jüngere wärmere Rinden-/Holzflächen bleiben ruhig getrennt. Wenige Kräuterbeete und Sitzplätze deuten eine mögliche Nutzung an. Die Angabe heilkundige Elfen bleibt vorläufig; keine neue Unterart, Religion oder Kulturhierarchie. Größen sind technische Studienannahmen. Die Flügel besitzen leere Innenräume, begehbare Böden und echte Türdurchgänge; der zentrale alte Körper ist ebenfalls separat zugänglich. Keine interne Raumverbindung zwischen den Flügeln behauptet; Verbindung erfolgt über den Hof und äußere Wurzel-/Tragstrukturen.")
write("HANDOFF.md",f"""# Architekturstudie {title}

Stand: 23. Oktober 2026. Status **creator_ready**, ausschließlich auf Creator-/Blender-Ebene; Sichtentscheidung steht aus.

## Auftrag und Identität

- KitId `{m['kit_id']}`, ModuleId `{m['module_id']}`, InterfaceVersion **0.1**, Studienrevision **1**.
- Tatsächliche Ausgangsrevision `{m['base_commit']}` auf `assets/creator`, Worktree `E:\\Business\\fantasy-rpg-creator`. Zu Beginn sauber; kein Zurücksetzen, Merge oder Branchwechsel.
- Einziger Schreibbereich: `{m['creator_directory']}/`. Neue, eigenständige Studie; das alte Blatthof-/Innenwand-Modul bleibt eingefroren.
- Die beiden tatsächlichen Referenz-PNGs wurden vor Modellierung angesehen. Diese Studie nutzt Bild {'33' if a else '23'}; lokale Kopie unter `References/`, Hash `{m['reference_image_sha256']}`. Bildreferenz ist kein maßhaltiger Bauplan.
- Aktuelle Hauptrepo-Grundlagen ergänzend nur gelesen. Einzelne Dokumenthashes und Herkunft stehen im Manifest; keine Dokumente angleichen oder Kanon ergänzen.

## Gestaltung und Prototypmaße

{design}

Die Studie ist bewusst vereinfachte 3D-Geometrie, keine AI-Illustration. Struktur, Dekor, Türen/Fenster, Boden, Natur und 180-cm-Maßfigur sind in getrennten Collections. Die ausgeblendeten Source-/UCX-Collections liefern editierbare, einzeln exportierbare Bibliotheksobjekte. Szenenobjekte sind Instanzen dieser Mesh-Daten. Keine Gameplay-Tür oder Interaktion.

## Dateien und reproduzierbare Prüfung

- `{m['source_blend']}`: editierbare Szene und Assetbibliothek; erneut in einem separaten Blender-Prozess geöffnet.
- `Exports/`: **{len(m['exports'])}** FBX-Dateien, jeweils genau ein Render-Mesh plus zugehörige UCX, falls vorhanden. Jede Datei in Blender rückimportiert, Körperzahl, Bounds, Dreiecke und Materialslotnamen geprüft.
- `manifest.json`: vollständige Teileliste, Einzelbounds, Pivots, Instanztransforms, Referenz-/Dokumenthashes, Materialien, Exporthashes, Einschränkungen.
- `verification.json`: tatsächliche Source-/Roundtrip-Messwerte und stichprobenartige Tür-/Boden-/Dachabfragen; kein Unreal- oder Kapselnachweis.
- `preservation.json`: tatsächlicher Vorher-/Nachherabgleich aller 1.072 vorher versionierten Worktree-Dateien; byteidentisch einschließlich des eingefrorenen Innenwand-Moduls. Branch und Ausgangs-HEAD unverändert. Keine Aussage über parallel bearbeitete andere Worktrees.
- `Previews/01_eye_overview.png`, `02_house.png`, `03_plan.png`, `04_interior.png`: echte Blender-Cycles-Render mit neutraler gemeinsamer Tagesbeleuchtung und Maßfigur. Die Innenansicht nutzt zusätzlich eine neutrale, nur im Renderprozess gesetzte Aufhellfläche zur Geometriebeurteilung; sie ist keine geplante Gebäudeleuchte. Aufsicht ist perspektivisch. Keine Render-only-Architektur; Bilder zeigen die gelieferte Szene.
- `build_study.py`: eigenständiger lokaler Blender-Erzeuger/Prüfer/Renderer, ohne gemeinsame Tool-Änderungen. `finalize_delivery.py`: lokale Herkunfts-/Berichtserstellung. `.gitattributes` bewahrt die Lieferbytes.
- `SHA256SUMS`: Hash sämtlicher Lieferdateien außer der Liste selbst. Nicht committed; Commit-/Integrationsfreigabe ist kein Teil dieses Auftrags.

Blender 5.2.2 LTS, Metric / Unit Scale 1.0 / Meter. Zum Prüfen aus einem neuen Blender-Prozess: `--background --factory-startup --python-exit-code 1 --python <absoluter Pfad>/build_study.py -- --mode verify`. Zum Rendern `--mode render`. `build` schützt vorhandene Quellen; `revise` ist nur für ausdrücklich beauftragte Iteration im eigenen Studienordner vorgesehen. Nach jeder Änderung Prüfungen und Hashliste neu erzeugen.

## Neuer technischer Anschlussvertrag

Keine R255-/Blatthof-Kompatibilität. Version **0.1** beschreibt eine Studienzusammenstellung, keinen freigegebenen Baukasten. Exportobjekte haben Translation/Rotation Null und Skalierung Eins; Geometrie und Pivot liegen im eigenen lokalen Bezug. Pivots und lokale Bounds jeder Einheit sowie exakte Instanztranslation/-drehung sind im Manifest. Haus-/Flügelursprung liegt auf Bodenhöhe; Wandfelder werden über ihre im Skript/Manifest dokumentierten End-/Ebenenmaße gefügt. Vollständige Anschlussprofile erst nach Sichtauswahl als Produktionsvertrag festlegen.

Unreal-Ziel: Zentimeter, `UE_cm=(100*B.x,-100*B.y,100*B.z)`. Blender -Y entspricht Unreal +Y. Keine zusätzliche Spiegelung oder negative Objektskalierung. Kalibriertes Exportprofil: **FBX_SCALE_NONE**, global_scale 1, apply_unit_scale true, Forward -Y, Up Z, use_space_transform true, bake_space_transform false. Auswahl ausschließlich MESH; Modifier/kontrollierte Triangulierung, FACE-Smoothing, Tangenten. Keine Kamera, Lichter, Animation oder eingebetteten Texturen im FBX. Kamera/Licht bleiben nur in der Blender-Review-Szene.

## Geometrie, Materialien und Kollision

**{total} Dreiecke** über die einzigartigen exportierten Render-Einheiten; **{hulls} UCX-Körper** über die einzigartige Bibliothek. Diese Summen sind keine Instanz-/Draw-Call- oder Laufzeitmessung. Die vollständige Szene enthält zusätzliche Instanzen und die Maßfigur. Je ein UV0-Kanal mit metrischen Flächenprojektionen; absichtliche Überlappungen für einfache Kachelflächen. Keine Produktions-UVs oder finale Lightmap-UVs. Source-Normalen und geschlossene Meshkomponenten geprüft. Mehrteilige Dekor-/Baumgeometrie darf sich als zusammengefasste Studiengruppe absichtlich überschneiden; kein boolesch vereinigtes Produktionsmodell behauptet.

| Einheit | Dreiecke | UCX | Materialslots |
| --- | ---: | ---: | --- |
{rows}

Strukturkollision besteht aus einzelnen geschlossenen konvexen Teilkörpern. Öffnungen werden ausgespart; keine komplette Haus-/Hofhülle als UCX. Die vielen Teilkörper der Wandraster sind bewusst einfach prüfbar, aber noch nicht für Laufzeit optimiert. Dekor, Natur, Glas und Detailteile ohne UCX sind im Manifest ausgewiesen. Aufteilung in weitere semantische Produktionsmodule oder Reduktion der Kollisionskörper später gesondert prüfen. Ein LOD, Nanite vorgesehen aus; weitere LODs nur nach Auftrag.

Roughness und Grundfarben stehen je Blender-Material im Manifest. Prozedurales Bump dient nur der Blender-Sichtprüfung, ohne externe Texturen. Blender-Shader werden nicht als vollständig nach Unreal übertragbar behandelt. Keine bestehenden Unreal-Materialien geändert.

## Tatsächlich geprüft und noch offen

Erneutes Source-Öffnen; Einheiten und externe Bibliotheken; nicht entartete, geschlossene Source-Einheiten; alle FBX-Rückimporte mit Materialslots, Dreiecken, Bounds und konvexen UCX. Durchgangsproben: neun horizontale Render-Rays pro bezeichnetem Eingang im zentralen 1,2 × 2,2-m-Freiraum; Boden und Dach an mehreren Innenpunkten getroffen. Die tatsächlichen Einzelresultate stehen in `verification.json`. Kein versteckter geschlossener Wandkörper hinter diesen Eingängen. Statische Türblätter sind geöffnet angeordnet.

Nicht geprüft: kontinuierliches Kapselvolumen, alle Fenster-/Nahtkontakte, Innenkamera-Clipping, Unreal-Import/-Reimport/Materialzuordnung/Lightmap-Erzeugung, PIE, Packaging, Multiplayer, Performance, fertige Vegetation oder Produktionsqualität. Kleine Fenster sind opake/transmissive Glasplatzhalter; keine besondere Glas- oder Beleuchtungstechnologie. Review-Schwellen gelten je Produktionsteil; zusammengesetzte Studiengruppen sind gegebenenfalls später aufzuteilen.

Blender meldete lediglich DeprecationWarnings zu use_nodes. Korrigierte explorative Skript-/Prüfversuche sind keine bestandenen Abnahmen; maßgeblich ist der abschließende Prüfbericht. Keine Meldungen unterdrückt.

Nächster Schritt: gemeinsame Sichtprüfung und ausdrückliche Auswahl/Änderungswünsche. Nur danach Refiner-Übernahme als eigene Kopie; vorhandene Creator-Übergaben nicht überschreiben. **Kein Unreal-Import/Reimport, keine Editor-/Level-/Blueprint-/Material-/Config-Änderungen, keine Commits oder Pushes.** Eine spätere Integration benötigt einen benannten Verantwortlichen und den kalibrierten Legacy-Pfad FbxFactory/FbxStaticMeshImportData. Interchange ist nicht validiert; bestehende Kollision niemals pauschal löschen.
""")
files=sorted(p for p in ROOT.rglob("*") if p.is_file() and p.name!="SHA256SUMS")
write("SHA256SUMS","".join(sha(p)+"  "+p.relative_to(ROOT).as_posix()+"\n" for p in files))
print("DELIVERY_FINALIZED",m["module_id"],len(files)+1,"files",total,"unique triangles",hulls,"UCX")

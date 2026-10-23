from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[6]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()
def read(n):return json.loads((ROOT/n).read_text(encoding='utf-8-sig'))
def write(n,d):(ROOT/n).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
old=read('Evidence/files_before.json');changed=[p for p,h in old.items() if not (REPO/p).exists() or sha(REPO/p)!=h]
assert changed==['Content/Prototype/Maps/Lvl_AssetLab.umap'],changed
assert read('Evidence/unreal_verification.json')['status']=='passed'
assert read('Evidence/blender_verification.json')['status']=='passed'
assert read('Evidence/session_restored.json')['status']=='passed'
write('Evidence/preservation.json',dict(status='passed',checked=len(old),changed_existing=changed,existing_houses_unchanged=True))
data=read('manifest.json');saved=read('Evidence/import_assets.json')['saved'];verification=read('Evidence/unreal_verification.json')
data.update(status='review_ready',accepted=False,unreal_map='/Game/Prototype/Maps/Lvl_AssetLab',unreal_packages=saved,placement=read('Evidence/place_walls.json')['placed'],export_source_sha256=sha(ROOT/data['export_source']),
    package_sha256={p:sha(REPO/('Content/'+p.removeprefix('/Game/')+'.uasset')) for p in saved},map_sha256=sha(REPO/changed[0]),
    evidence=['Evidence/blender_verification.json','Evidence/unreal_verification.json','Evidence/preservation.json','Evidence/session_restored.json'],pending=['User assessment in Unreal','Performance/LOD optimisation for repeated use','Clean editor/map reload deferred while unrelated dirty packages remain preserved'],next_modules=['Matching solid wall','Matching door opening wall','Separate door leaf and frame; gameplay only when explicitly specified'])
write('manifest.json',data)
review=f'''# Hochelfen-Wände – Unreal-Vergleich 01

Status **review_ready**, keine Produktionsabnahme. Nutzerauftrag: beide gezeigten Wandvarianten so ins Refiner-Lab übernehmen. Geschlossene Wand, Türöffnung und separate Tür sind die nächsten geplanten Module, in diesem Import noch nicht erstellt.

## Quelle und Umfang

Worktree `E:/Business/fantasy-rpg-refiner`, Branch `assets/refiner`. Geprüfte Eingangsquelle `../HighElf_WallVariants_01.blend`, SHA256 `{data['source_sha256']}`. Eigene Exportkopie `HighElf_Export_01.blend`, 9 FBXs und 15 gebackene Texturen. Eingangsgeometrie, Häuser, ältere Wände und gemeinsame Materialien unverändert.

Unreal: 9 neue Meshes, 6 private Materialien, 15 Texturen und 2 statische Baugruppen-Blueprints unter `/Game/Art/{{Architecture,Materials,Textures}}/HighElfWallStudy01`. Gleicher Kern, Rahmen und Glas werden von beiden Varianten gemeinsam verwendet. Blueprint enthält 6 Mesh-Komponenten, keine hinzugefügte Gameplay-Logik. Glas bleibt separat und wirft keinen Schatten; kein verstecktes Innenlicht ergänzt.

Die allein stehenden Vergleichswände liegen im Lab bei A `(1600,3100,2)` und B `(2200,3100,2)` cm. Eine zweite A/B-Kombination bei `(1600,2350,2)` / `(1900,2350,2)` prüft den 300-cm-Stoß. Outliner: `Lab/Architecture/HighElfWallStudy01`.

## Übertragung und tatsächliche Prüfungen

- Blender 5.2.2: Quelle erneut geöffnet, neun FBX-Rückimporte hinsichtlich Dreiecken, Bounds, Slots und Hüllenzahl bestanden.
- Kalibriertes FBX_SCALE_NONE, Forward -Y / Up Z, UE_cm=(100*x,-100*y,100*z). Keine zusätzliche Spiegelung oder negative Skalierung. Unreal 5.8 via MCP `StaticMeshTools.import_file` mit explizitem Legacy-FbxFactory-Import; tatsächlich gespeicherte Importdaten an allen 9 Meshes `FbxStaticMeshImportData`.
- Tatsächliche Unreal-Bounds mit Blender abgeglichen, Fehler unter 0,002 cm. Dreiecke und Slots erhalten. Kern 15 konvexe Hüllen, separate Scheibe 1 Hülle; Zierwerk und Rahmen ohne blockierende Hülle.
- Vier unskalierte Baugruppen geprüft. Einfacher Kollisionstrace von beiden Seiten trifft am Fenster zuerst die Scheibe; seitlicher Wandkern, Brüstung und Sturz blockieren. Beidseitige Kapseltests (Radius 35 / Halbhöhe 90 cm) blockieren an beiden Wänden und lassen den Zwischenraum frei. Zwei Traces am Modulstoß bestehen.
- {verification['existing_actors_preserved']} vorhandene Actors inklusive Haus-Transforms, Meshreferenzen und Material-Overrides unverändert. Von {len(old)} vorhandenen Dateien nur die ausdrücklich beauftragte Lab-Karte geändert; alte Assetdateien bytegleich. Neue Assets und die Lab-Karte einzeln gespeichert, kein Save All.
- Importdefaults und Sitzungs-CVar wiederhergestellt. Keine Projektkonfiguration geändert. Editor nicht neu gestartet, keine fremden dirty Packages verworfen.

## Materialien und Grenzen

Blender-BaseColor, Rauheit und Mikro-Normalen als 1024²-PNG je fünf opaken Materialfamilien gebacken. 1-m-Materialausschnitt auf einer Fläche, UV0-Kachelung: eine Näherung der ursprünglichen räumlichen Noise-Verteilung, keine pixelidentische 3D-Shaderübertragung. Grundpalette und Rauheitsbereiche stammen aus der gewählten Quelle. Normalkarten in Unreal mit invertiertem Grünkanal. Klares Glas verwendet eine eigene Kopie des bereits geprüften Substrate-Glasmaterials.

A: 3.912 Dreiecke pro kompletter Wand, B: 9.860; sechs Materialfamilien pro Baugruppe. Diese Detailstudien überschreiten die Prototyp-Reviewschwelle für einfache Wände. Optimierung, LODs und Siedlungsperformance bleiben offen. Nanite aus. Keine Packaging-/Multiplayer-Abnahme.

Sauberes Editor-/Karten-Neuladen bleibt offen, da die laufende Sitzung bereits andere ungespeicherte Pakete enthält, die erhalten bleiben. Vorhandene Datei-Hashes beweisen nicht die Erhaltung ungespeicherter Editorzustände; deswegen kein erzwungener Neustart. Reimportfestigkeit dieser neuen Baugruppen ist noch separat zu prüfen. Status bleibt review_ready.

Keine Commits oder Pushes in diesem Auftrag. Blender-Ausgangsdatei und deren vorherige Dokumentation bleiben als eigener historischer Stand erhalten.
'''
(ROOT/'REVIEW.md').write_text(review,encoding='utf-8')
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and p.suffix not in ['.pyc','.blend1'])
(ROOT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in files),encoding='utf-8')
print(json.dumps(dict(status='passed',existing_checked=len(old),changed=changed,new_packages=len(saved),hashed=len(files))))

from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[6]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((ROOT/n).read_text(encoding='utf-8'))
def write(n,d):(ROOT/n).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
d=read('manifest.json');allowed={'Content/Prototype/Maps/Lvl_AssetLab.umap'}|{'Content/Art/Architecture/WallCatalogue01/Meshes/'+n+'.uasset' for n in d['assets']}
before=read('Evidence/files_before.json');changed=[];missing=[]
for n,h in before.items():
    p=REPO/n
    if not p.is_file():missing.append(n)
    elif sha(p)!=h:changed.append(n)
assert not missing and set(changed)<=allowed,(missing,changed)
assert read('Evidence/blender_verification.json')['status']==read('Evidence/unreal_verification.json')['status']==read('Evidence/session_restored.json')['status']=='passed'
for n,i in d['assets'].items():assert sha(ROOT/'Exports'/(n+'.fbx'))==i['fbx_sha256']
write('Evidence/file_preservation.json',dict(status='passed',existing_files_checked=len(before),changed=changed,missing=missing,allowed_changes=sorted(allowed),
    original_house_assets_and_all_materials_unchanged=True,previous_catalogue_sources_unchanged=True))
d.update(status='review_ready',accepted=False,map='/Game/Prototype/Maps/Lvl_AssetLab',source_sha256=sha(ROOT/d['source']),
    unreal_paths={n:'/Game/Art/Architecture/WallCatalogue01/Meshes/'+n for n in d['assets']},
    saved_package_sha256={n:sha(REPO/n) for n in sorted(allowed)},
    evidence=['Evidence/blender_verification.json','Evidence/reimport_windows.json','Evidence/unreal_verification.json','Evidence/file_preservation.json','Evidence/session_restored.json'],
    pending=['Visual approval of smaller window size','Elven color/style fit explicitly unaccepted; current colors temporarily retained','Safe editor package reload still pending because of previously unresolved dirty packages'],
    commit_created=False,pushed=False)
write('manifest.json',d)
(ROOT/'REVIEW.md').write_text('''# Kleinere Fenster für den separaten Wandkatalog

Status **review_ready**, nicht accepted. Nutzerfeedback: Fenster zu groß; Farbwirkung passt noch nicht zu den Elfenhäusern. Beauftragt ist vorerst die Verkleinerung. Die drei Wandvarianten bleiben Auswahlmuster; ihre Farb-/Stileignung ist ausdrücklich offen.

## Änderung

Nur die drei Fensterwände des Katalogs, deren separater Rahmen und die Glasscheibe wurden geometrisch aktualisiert. Öffnung zuvor120×152cm, jetzt65×90cm; Brüstung100→135cm, Kopf maximal252→225cm. Orientierung an den vorhandenen Hausstudien mit65×80cm-Scheiben. Rahmen und Glas sind in der Geometrie verkleinert, die sechs eingesetzten Instanzen aufZ137cm im Lab angehoben (WandbasisZ2 + Brüstung135). Keine Actor-Skalierung zur Größenkorrektur.

Wandaußenmaße300×24×320cm, Startpivot, Endanschlüsse, Holz-/Steindekor, Materialslots sowie alle Farben und Texturen bleiben erhalten. Glas weiterhin durchsichtig und physisch blockierend. Unberührt: geschlossene Katalogwände, Möbel, Lampen und sämtliche Häuser.

Neue editierbare Quelle `WindowResize02.blend`; der bisherige Katalog bleibt unverändert als Vorrevision erhalten. Fünf neue FBX in `Exports/`. Dieselben fünf eigenen Unreal-Assetpfade wurden ausdrücklich mit Legacy-FbxFactory aktualisiert, Referenzen und Materialien erhalten. Nominale Assetnamen bleiben zur Referenzerhaltung bestehen; maßgeblich sind die gemessenen Bounds im Manifest. Fenstervertrag ist nun `draft_2_window`; der bestehende äußere Wandanschluss bleibt unverändert.

## Prüfbelege

- Neue Quelle erneut geöffnet, verwendete externe Texturen aufgelöst und alle fünf FBX zurückimportiert: Bounds, Dreiecke, Slots und UCX erhalten; keine degenerierten UV-Dreiecke oder nichtmannigfaltigen Kanten. Alle sechs anderen Module in der Quelle in Größe, Dreiecken und Slots erhalten. Ein beim ersten Speichern fehlerhafter relativer Texturpfad wurde vor Abschluss korrigiert und erneut geprüft.
- Tatsächlicher Unreal-Legacy-Reimport: fünf Meshes, unveränderte Slots/Materialreferenzen und Kollisionsanzahlen. Keine Interchange-Abnahme.
- Für jede Variante reale einfache Sichtbarkeitsabfragen: neue Scheibe blockiert; ohne sie ist die neue Öffnung frei. Neue seitliche Wandfüllung, höhere Brüstung und tieferer Sturz blockieren. Eine zusätzliche Abfrage mit ignorierter Wand belegt, dass außerhalb der kleineren Scheibe keine alte übergroße Glaskollision übrig ist.
- Sämtliche vorab erfassten Lab-Actors geprüft; ausschließlich die sechs bezeichneten Fenstereinsätze dürfen ihre Höhe ändern. Häuser, sonstige Transformationen, Meshreferenzen, Ordner und Material-Overrides erhalten.
- Dateihashes über den gesamten Eingangsbestand geprüft: ausschließlich fünf bezeichnete eigene Unreal-Meshpakete und die Lab-Karte dürfen abweichen. Bisherige Blender-Quellen, gemeinsame Materialien, Texturen, Config, Tools und Gameplay bleiben unverändert.
- Blender- und Unreal-Bilder unter `Previews/` tatsächlich angesehen. Lab-Spielmodus nach der Bearbeitung vor dem kleineren B-Fenstermuster wieder gestartet; kein vollständiger manueller Rundgang behauptet.

## Übergabe

Maßauswahl und visuelle Abnahme stehen aus. Die vorläufigen Farben sind keine bestätigte elfische Stilvorgabe. Kein Neustart oder Verwerfen fremder ungespeicherter Pakete; sitzungsweise Importdefaults wiederhergestellt. Autosave bleibt im vorher pausierten Zustand. Saubere Paket-Reload-Prüfung weiterhin offen. Kein Commit/Push und keine neue Kultur-/Architekturfestlegung.
''',encoding='utf-8')
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and '__pycache__' not in p.parts)
(ROOT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in files),encoding='utf-8')
print('REVIEW_READY',len(changed),'authorized existing files changed;',len(before),'baseline files checked;',len(files),'hashes')

"""Seal evidence for the authorized A/B Unreal review, without saving editor packages."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[5]
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,data):
    (ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

before=read('Evidence/files_before.json')
allowed='Content/Prototype/Maps/Lvl_AssetLab.umap'
changed=[];missing=[]
for name,old in before.items():
    path=REPO/name
    if not path.is_file():missing.append(name)
    elif sha(path)!=old:changed.append(name)
write('Evidence/file_preservation.json',dict(checked_existing_files=len(before),changed=changed,missing=missing,
    allowed_modified_files=[allowed],status='passed' if not missing and set(changed)<={allowed} else 'failed'))
assert not missing and set(changed)<={allowed},(missing,changed)
plan=read('plan.json');lab=read('Evidence/lab_verification.json');pie=read('Evidence/pie_live.json')
assert lab['status']==pie['status']=='passed'
roots=['Content/Art/Architecture/StudyA_Street01','Content/Art/Architecture/StudyB_Root01','Content/Art/Materials/StudyAB_Review01']
assets={p.relative_to(REPO).as_posix():sha(p) for root in roots for p in (REPO/root).rglob('*.uasset')}
assert len(assets)==61,len(assets)
studies=[]
for s in plan['studies']:
    assert sha(Path(s['glass_source']))==s['glass_source_sha256']
    for e in s['mesh_manifest']['exports']:
        assert sha(Path(s['parent'])/e['path'])==e['sha256']
    a=lab['assemblies'][s['tag']]
    studies.append(dict(tag=s['tag'],source=s['glass_source'],source_sha256=s['glass_source_sha256'],
        source_geometry_delivery_commit='17828dce95c0d68fd5300bc9d8cba1db1178b83f',
        destination=s['dest'],blueprint=s['blueprint'],translation_cm=s['offset'],
        components=a['component_count'],instances=a['instances'],window_panes=a['glass_panes_physically_checked']))
write('manifest.json',dict(status='review_ready',accepted=False,map=plan['map'],studies=studies,
    saved_assets_sha256=assets,saved_lab_sha256=sha(REPO/allowed),
    importer='Legacy FbxFactory / FbxStaticMeshImportData; Interchange not used',
    geometry_mapping='UE_cm=(100*B.x,-100*B.y,100*B.z); yaw_UE=-yaw_Blender; unit actor scales',
    actual_evidence=['Evidence/import_modules.json','Evidence/populate_instances.json','Evidence/rotation_correction.json',
        'Evidence/lab_verification.json','Evidence/pie_live.json','Evidence/file_preservation.json','Evidence/session_preserved.json'],
    pending=['Independent visual acceptance and manual traversal','Clean editor restart and package reload verification',
        'Performance, target-platform rendering, lightmaps and production material detail','Controlled reimport regression'],
    live_session=dict(editor_left_open=True,pie_started=True,unsaved_packages_preserved=True,autosave_paused_in_memory=True,
        clean_restart='Automatic approval review rejected restarting with dirty Game packages; no discard or workaround performed'),
    commit_created=False,pushed=False))

(ROOT/'REVIEW.md').write_text('''# Unreal-Ansicht der Studien A und B

Status: **review_ready**, keine Abnahme. Worktree `E:/Business/fantasy-rpg-refiner`, Branch `assets/refiner`.
Der Nutzer hat die Unreal-Ansicht beider zuvor in Blender geprüften Glasstudien beauftragt.

## Ergebnis und Herkunft

- A: `EC.HighCultureCity / StreetStudy01`, 21 Meshes, 470 HISM-Instanzen, 24 Scheiben.
- B: `ER.RootRetreat / CourtyardStudy01`, 27 Meshes, 318 HISM-Instanzen, 14 Scheiben.
- Geometrie aus Refiner-Lieferung `17828dce95c0d68fd5300bc9d8cba1db1178b83f`; Glasstände und SHA256 in `manifest.json` und `plan.json`. Alle 48 verwendeten FBX-Hashes erneut geprüft. Die beiden Blender-Maßfiguren sind nicht exportiert; der vorhandene Spieler dient dem Größenvergleich.
- Zwei neue wiederverwendbare Blueprints, elf eigene Materialien und 48 Meshes, ausschließlich unter den eigenen StudyA/StudyB/StudyAB-Content-Pfaden. Lab ausdrücklich gespeichert. Keine Änderung an gemeinsamen Materialien, Generatoren, Konfiguration oder Gameplay-Code; kein Commit/Push.
- Lab-Offsets in cm: A `(4300,-900,31)`, B `(4300,2500,31)`, Rotation null und Skalierung eins. Bestehende 399 Actors mit Transform, Ordner, Mesh und Materialbelegung erhalten.

## Tatsächliche Prüfungen

Legacy-FbxFactory verwendet, keine Interchange-Abnahme. Importierte Bounds, Dreieckzahlen, Slot-Reihenfolge und alle Instanztransformationen mit Manifest verglichen. Blender-Zuordnung `UE_cm=(100*B.x,-100*B.y,100*B.z)`, UE-Yaw negativ zum Blender-Yaw. Ein zunächst fehlerhaft positional konstruierter Python-Rotator wurde mit benannten Feldern korrigiert; Abschlussprüfung danach bestanden (`rotation_correction.json`, `lab_verification.json`).

57/158 UCX-Hüllen aus den Quellen erhalten. Je Studie eine einfache Box für Glas und Pflaster ergänzt, insgesamt vier Boxen. Sechs Kapselabfragen mit tatsächlichen Spielermaßen Radius 35/Halbhöhe 90 cm prüfen die drei A-Eingänge sowie B-Eingang und zwei Innenverbindungen. Bodenauflagen und alle 38 Scheiben physisch geprüft. Diese Abfragen sind kein manueller Rundgang.

Das eigene Glasmaterial dupliziert den zuvor geprüften Substrate-SimpleVolume-Ansatz, Roughness .025 und hohe Transmission. Glasschatten sind deaktiviert, Rahmenschatten erhalten: Tageslicht kann eintreten; dies ist eine praktische Näherung ohne validierte refraktive Kaustik. Farben/Rauheiten der festen Materialien sind angenähert; Blender-Prozeduraldetails wurden nicht automatisch übertragen. Keine Beleuchtungsänderung am Lab.

`Previews/` enthält tatsächliche Unreal-Bilder beider Übersichten und Fenster innen/außen. `PIE_B.png` zeigt den laufenden Spielmodus. `pie_live.json` belegt den vorhandenen BP_PrototypeCharacter und beide vollständigen Assemblies in der PIE-Welt. Start vor B; A liegt südlich dahinter. Zum Erkunden in die Spielansicht klicken, WASD/Maus; F6 öffnet die vorhandene Entwickler-Toolbox mit Flug/Freikamera.

## Erhaltung und Sitzungseinschränkungen

`file_preservation.json` vergleicht sämtliche zuvor erfassten Dateien byteweise. Nur die ausdrücklich beauftragte Lab-Karte darf gegenüber diesem Arbeitsbaseline abweichen. Der bereits zuvor extern gespeicherte A-Blend-Stand und alle anderen vorhandenen Änderungen bleiben erhalten. Die Vorabkopie der Lab-Karte liegt ignoriert unter `Saved/StudyABIntegration/Before/`.

Ein erster Editorprozess stürzte beim automatischen Speichern von Engine-Hilfsmeshes ab. Recovery-Dateien wurden gesichert; in der aktuellen Sitzung ist Autosave nur im Speicher pausiert, ohne SaveConfig. Ein weiterer Realtime-API-Aufruf erzeugte einen nichtfatalen Engine-Ensure und wurde aus dem Prüfskript entfernt. Kein fehlerfreier Engine-Lauf wird behauptet.

Die automatische Freigabeprüfung lehnte einen Neustart wegen zahlreicher ungespeicherter Game-Pakete und möglichem Änderungsverlust ab. Es erfolgte kein Umgehen dieser Sperre und kein Verwerfen dieser Pakete. Stattdessen bleibt die laufende Sitzung offen. Importer-Vorgaben, Interchange-CVar und Hintergrund-/Slate-Throttling wurden wiederhergestellt; Autosave bleibt wegen des beobachteten Absturzes für diese Sitzung pausiert (`session_preserved.json`). Keine globale Save-All-Aktion.

## Offen

- Nutzerbewertung von Maßstab, Silhouette, Glas und Innenraum; manueller Rundgang.
- Sicherer Neustart mit Prüfung der gespeicherten Pakete, sobald die übrigen ungespeicherten Änderungen geklärt sind; bislang keine Reload-Abnahme.
- Materialdetails, Licht-/Belichtungsabstimmung, Zielplattform/Performance und kontrollierter Reimport vor Produktionsfreigabe.
- Keine neue Lore-/Architekturkanon-Festlegung und keine Abnahme als fertiges Endprodukt.
''',encoding='utf-8')

files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and '__pycache__' not in p.parts)
(ROOT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in files),encoding='utf-8')
print('REVIEW_READY',len(assets),'assets;',len(before),'existing files checked;',len(files),'review hashes')

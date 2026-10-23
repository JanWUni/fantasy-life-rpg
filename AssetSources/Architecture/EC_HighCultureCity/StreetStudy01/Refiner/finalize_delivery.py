"""Seal only the Refiner delivery after actual DCC tests and visual review."""
from pathlib import Path
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[4];CREATOR=ROOT.parent/'Creator'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,data):
    (ROOT/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
m=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
assert m['status'] in ['refiner_verified','review_ready']
for file in ['verification.json','Evidence/independent_verification.json','Evidence/openings_and_floor.json','Evidence/intake_verification.json']:
    assert json.loads((ROOT/file).read_text())['status']=='passed',file
assert sha(ROOT/m['source_blend'])==m['source_blend_sha256']
for entry in m['exports']:assert sha(ROOT/entry['path'])==entry['sha256']
for name in ['01_eye_overview','02_house','03_plan','04_interior']:assert (ROOT/'Previews'/(name+'.png')).is_file()
baseline=json.loads((ROOT/'Evidence/preservation_before.json').read_text());changed=[];missing=[]
for name,digest in baseline['files'].items():
    p=REPO/name
    if not p.is_file():missing.append(name)
    elif sha(p)!=digest:changed.append(name)
assert not missing and not changed,('Existing files changed outside Refiner scope',changed,missing)
incoming={}
for line in (CREATOR/'SHA256SUMS').read_text().splitlines():
    digest,name=line.split(maxsplit=1);name=name.lstrip('* ');assert sha(CREATOR/name)==digest;incoming[name]=digest
preservation=dict(status='passed',files_before=len(baseline['files']),files_unchanged=len(baseline['files']),changed_existing=[],deleted_existing=[],
    creator_files_unchanged=len(incoming),existing_refiner_work_preserved=True,no_unreal_operations=True)
write('Evidence/preservation_after.json',preservation)
changes=m['refiner_changes'];before=sum(v['before']['triangles'] for v in changes.values());after=sum(v['after']['triangles'] for v in changes.values())
hulls=sum(len(e['collision_names']) for e in m['exports']);bevels={n:v['controlled_bevel_m'] for n,v in changes.items() if v['controlled_bevel_m']}
rejected=[n for n,v in changes.items() if v['bevel_rejected_to_preserve_contract']]
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
m.update(status='review_ready',accepted=False,refiner_revision=1,refiner_intake_head=head,
    generator=dict(file='refine_study.py',sha256=sha(ROOT/'refine_study.py')),
    creator_verifier_dependency=dict(file='../Creator/build_study.py',sha256=sha(CREATOR/'build_study.py'),read_only=True),
    previews=[dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),renderer='Actual Blender Cycles / AgX / 24 samples',visually_reviewed=True) for p in sorted((ROOT/'Previews').glob('*.png'))],
    reference_image=dict(file='../Creator/'+m['reference_image']['local_copy'],sha256=m['reference_image_sha256'],visually_inspected=True,read_only=True),
    preservation=preservation,verification=dict(file='verification.json',sha256=sha(ROOT/'verification.json')),
    refiner_summary=dict(unique_triangles_before=before,unique_triangles_after=after,ucx_before=hulls,ucx_after=hulls,
        controlled_bevels_m=bevels,bevels_rejected_to_preserve_bounds=rejected,interface_changes_required=False))
write('manifest.json',m)
rows='\n'.join('| `'+n+'` | '+str(v['before']['triangles'])+' → '+str(v['after']['triangles'])+' | '+str(len(next(e for e in m['exports'] if e['asset_name']==n)['collision_names']))+' | '+('%.1f mm'%(1000*v['controlled_bevel_m']) if v['controlled_bevel_m'] else '–')+' |' for n,v in changes.items())
review=f'''# Refiner-Übergabe A – Hochkultur-Wohnstraße

Status **review_ready**, nicht accepted. Kit `{m['kit_id']}`, Modul `{m['module_id']}`, Creator-Revision {m['revision']}, Interface **{m['interface_version']}** unverändert. Refiner-Revision 1.

Eingangscommit **`{m['input_commit']}`**, gezielte Übernahme auf `assets/refiner`: **`{head}`**. Eingangsquelle SHA-256 **`{m['input_source_sha256']}`**. Alle 34 Creator-Lieferhashes und 27 LFS-Objekte sind gegen den Commit geprüft; Creator-Dateien bleiben eingefroren. Das frühere Warten auf Sichtauswahl wird durch den ausdrücklichen aktuellen Refiner-Auftrag ersetzt.

## Bearbeitung

Die editierbare [StreetStudy01_Refined.blend](StreetStudy01_Refined.blend) begann als byteidentische eigene Kopie. Straßenanordnung, drei Haussilhouetten, kleine Fenster, Proportionen, Stein-/Holzmaterialien, Pivots und sämtliche **{len(m['placement_instances'])} Instanztransforms** sind erhalten. Keine neue Architektur-, Kultur- oder Lore-Festlegung.

Vorhandene Topologie wurde auf Doppel-/Innenflächen, geschlossene Komponenten und entartete Flächen geprüft. Der konservative Versuch, koplanare Kanten unter Erhalt der UV-Grenzen aufzulösen, führte an den Strukturteilen zu keiner Reduktion; es wird keine Laufzeitoptimierung behauptet. Normalen fester Teile sind neu berechnet und als gewichtete Split-Normalen gebacken. Vorhandene Bögen und Baumkörper sind geglättet, während Kappen und scharfe Übergänge ab 45° getrennt bleiben. Laub behält gleichmäßige, ungewichtete Glättung, nachdem die Sichtprüfung dort Bänder durch gewichtete Normalen zeigte. Dachflächen bleiben plan statt pauschal weichgezeichnet.

Kleine zweistufige Rundungen an {len(bevels)} Teilen betragen 3–4 mm. An {len(rejected)} weiteren Teilen wurden Rundungen verworfen, sobald sie die exakten Bounds verändert hätten. Keine Änderung der Strukturöffnungen oder der UCX-Geometrie. UV0 verwendet eine konsistente Dominantachsenprojektion mit dem vorhandenen 2-m-Kachelmaß; absichtliche Überlappungen bleiben erhalten. Keine entarteten UV-Dreiecke, kein Produktionsatlas oder finaler Lightmap-Kanal.

**Einzigartige Render-Dreiecke: {before} → {after}**; einfache Kollisionskörper **{hulls} → {hulls}**. Dies sind Bibliothekswerte, keine Instanz-/Draw-Call-/Performancewerte.

| Asset | Dreiecke vorher → nachher | UCX | Rundung |
| --- | ---: | ---: | ---: |
{rows}

## Tatsächliche Prüfungen

- [Eingang](Evidence/intake_verification.json): SHA256SUMS, vollständige LFS-OIDs/Größen und Creator-Textdateien gegen Eingangscommit.
- [Vorher/Nachher](Evidence/refinement.json): je Mesh Maße, Topologie, UVs, Volumen, Normalen und verworfene Rundungen. Boundsabweichung kleiner 0,000001 m; Materialslotnamen und Reihenfolge erhalten. Alle 57 UCX-Geometriefingerprints sowie Instanzmatrizen exakt erhalten.
- [Quell-/FBX-Prüfung](verification.json) und [zusätzliche unabhängige Messung](Evidence/independent_verification.json): gespeicherte Quelle in frischem Blender-Prozess erneut geöffnet, alle 21 FBX zurückimportiert. Einheiten, Bounds, Pivot/Identitätstransforms, Slotfolge, geschlossene positive Volumen, UVs und konvexe UCX geprüft. Alle Prüfungen bestanden.
- Eingänge: ursprüngliche neun Render-/UCX-Strahlen je Haus im zentralen **1,2 × 2,2-m-Prüfbereich** frei; mehrere Boden- und Dachproben getroffen. Dies ist kein kontinuierlicher Kapselnachweis.
- [Zusätzliche Fenster-/Bodenprüfung](Evidence/openings_and_floor.json): je zwei kleine Öffnungen in Fassade, Rück- und Seitenwand, zusammen 294 freie Strahlen je Darstellung; geschlossene Brüstungs-/Sturzproben. Fünf Innenbodenproben je Haus treffen in Render und UCX **Z0**.
- [Erhaltung](Evidence/preservation_after.json): **{len(baseline['files'])} vorher vorhandene Dateien byteidentisch**, einschließlich Content, Konfiguration, gemeinsamer Tools und der uncommittierten früheren Refiner-Arbeit. Keine Unreal-Operation ausgeführt.

## Echte Blender-Ansichten

[Straßenansicht](Previews/01_eye_overview.png) · [Hausansicht](Previews/02_house.png) · [Aufsicht](Previews/03_plan.png) · [Innen](Previews/04_interior.png).

Cycles, AgX, 24 Samples und unveränderte gemeinsame Tagesbeleuchtung. Die Innenansicht verwendet wie die Creator-Prüfdarstellung eine temporäre neutrale Aufhellfläche; diese ist kein geplantes Gebäudelicht und wird nicht in der Quelle gespeichert. Keine AI-Bilder oder Render-only-Architektur.

## Export und offene Punkte

21 eigene FBX unter [Exports/](Exports/); exakt ein Render-Mesh und die bezeichneten UCX je Datei. Kalibriertes Profil unverändert: **FBX_SCALE_NONE**, global_scale 1, Metric Unit Scale 1, Forward -Y / Up Z; `UE_cm=(100*B.x,-100*B.y,100*B.z)`. Keine zusätzliche Spiegelung, keine negative Skalierung. Geprüft in Blender 5.2.2 LTS.

Materialgraphen und prozedurales Bump bleiben Blender-Prüfmaterialien; ein vollständiger Shadertransfer nach Unreal wird nicht behauptet. Glas, Vegetation, UV-Atlas/Lightmaps und LODs bleiben Prototypgrenzen. Dekor/Natur ohne UCX erhalten weiterhin keine eigene Kollision. Viele kleine Strukturhüllen sind unverändert und vor Produktion gesondert zu optimieren.

**Nicht durchgeführt:** Unreal-Import/Reimport, Interchange, PIE, physische Spieler-/Kamera-/Kapselbegehung, Packaging/Cooking, Multiplayer, Siedlungsperformance und finale Art-Abnahme. Noch keine Freigabe zur Integration. Keine Schnittstellenänderung erforderlich; kein neuer Refiner-Commit und kein Push. Einziger Git-Schreibvorgang war die ausdrücklich erlaubte Eingangsübernahme.

Reproduktion: `refine_study.py -- --mode verify` beziehungsweise `--mode render` in einem neuen Blender-Prozess; der eingefrorene Creator-Prüfer wird ausschließlich lesend geladen und auf den Refiner-Pfad gebunden. Der Erzeugungsmodus überschreibt keine unbekannte Refiner-Arbeit. [SHA256SUMS](SHA256SUMS) deckt alle Lieferdateien außer sich selbst ab.
'''
(ROOT/'REVIEW.md').write_text(review,encoding='utf-8',newline='\n')
(ROOT/'.gitattributes').write_text('# Stable delivery bytes.\n*.py text eol=lf\n*.md text eol=lf\n*.json -text\nSHA256SUMS text eol=lf\n.gitattributes text eol=lf\n',encoding='utf-8',newline='\n')
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and '__pycache__' not in p.parts and not p.name.endswith('.blend1'))
(ROOT/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files),encoding='utf-8',newline='\n')
print('REFINER_DELIVERY_SEALED',m['module_id'],len(files),before,after,hulls)

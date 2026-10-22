"""Describe and hash the own Blender study after its render/verification completed."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')

def main():
    m=read(ROOT/'manifest.json');v=read(ROOT/'verification.json');before=read(ROOT/'Evidence/before.json')
    assert v['status']=='passed' and len(v['source'])==13
    assert all(sha(ROOT/p)==h for p,h in m['sha256'].items())
    allowed={'docs/DECISIONS.md','docs/technical/ELVEN_BLATTHOF_STUDY.md','docs/worldbuilding/voelker/elfen/kultur.md'}
    changed=[p for p,h in before['files'].items() if not (REPO/p).exists() or sha(REPO/p)!=h]
    assert set(changed)<=allowed,changed
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO).decode().strip()==before['head']
    # Preserve the earlier committed Refiner wall delivery, including its archived Creator inputs.
    old=ROOT.parent
    for line in (old/'SHA256SUMS').read_text(encoding='utf-8').splitlines():
        h,p=line.split('  ',1);assert sha(old/p)==h,p
    previews=['Previews/house_front.png','Previews/house_rear.png','Previews/house_long_variant.png']
    for p in previews:assert (ROOT/p).is_file()
    m['status']='draft'
    m['validation_status']='Blender source/module FBX checks passed; visual study for user review; not production accepted'
    m['verification']={'path':'verification.json','sha256':sha(ROOT/'verification.json')}
    m['previews']=previews
    m['textures']={key:{'base_color':'Textures/T_EH_'+key+'_BaseColor.png',
        'normal':'Textures/T_EH_'+key+'_Normal.png','roughness':'Textures/T_EH_'+key+'_Roughness.png',
        'size_px':[1024,1024],'normal_convention':'Blender/OpenGL tangent +Y; Unreal conversion must be checked'}
        for key in ('Plaster','Timber','Stone','Jade')}
    m['uv_policy']='UV0 intentionally tiles/repeats; no unique lightmap unwrap supplied. Production texel density not fixed.'
    m['roof_collision_approximation']='16 convex strips per roof module; End uses straight longitudinal hull interpolation; source approximation only, untested in Unreal'
    m['geometry_review_exceptions']={'window_triangles':1272,'note':'The detailed arch/window includes frame, glass and tracery. Above 1000-triangle simple-wall review threshold; optimize/review before serial production.'}
    write(ROOT/'manifest.json',m)
    preservation={'status':'passed','baseline_files':len(before['files']),'unchanged_files':len(before['files'])-len(changed),
        'changed_design_documents_only':changed,'head_unchanged':before['head'],'previous_refiner_delivery_all_31_hashes_unchanged':True,
        'unreal_started':False,'existing_assets_modified':False}
    write(ROOT/'Evidence/preservation.json',preservation)
    table='\n'.join('| `'+a['name']+'` | '+str(a['triangles'])+' | '+str(a['ucx_hulls'])+' | '+', '.join(a['slots'])+' |' for a in m['assets'])
    fit=max(s.get('roof_underside_fit_max_error_m',0) for s in v['source'].values())
    seam=max(s['max_shell_position_error_m'] for a in v['assemblies'].values() for s in a['roof_seams'])
    error=max(s['bounds_roundtrip_max_error_m'] for s in v['roundtrip'].values())
    text=f'''# Geschlossenes Elfenhaus B01 – erste modulare Blender-Studie

Stand: 22. Oktober 2026. **Status: draft, zur visuellen Beurteilung.** Dies ist ein tatsächlich modelliertes Blender-Haus; die PNG-Ansichten sind Renderings dieser Quelle und keine Imagegen-Bilder. Noch keine Produktionsfreigabe oder Unreal-Integration.

## Auftrag und Arbeitsgrenze

Der Nutzer hat die geschlossene holzbetonte Bildstudie B01 als Startpunkt bestätigt und ein etwas größeres Haus gewünscht. Technische Prüfanordnung: **10 × 12 m Außen-Grundfläche**, eingeschossig, 3,20 m Wandhöhe, ein Eingang vorne. Dazu ist eine **10 × 16 m** lange Zusammenstellung aus denselben Bauteilen aufgebaut. Die Größen, Öffnungsprofile und Kit-ID sind vorläufige Arbeitswerte für diese Studie, kein allgemeiner elfischer Baustandard.

Eigene vorläufige Kit-ID: `EH.HouseB.Prototype01`, Interface `draft_1`. Sie ist **nicht** mit dem früheren R255/A30-Bogenkit austauschbar. Kein Verbiegen oder Skalieren des alten Profils. Die alte Wandlieferung und alle Unreal-Bestandsassets bleiben erhalten.

## Öffnen und ansehen

- [Editierbare Blender-Quelle](EH_HouseB01_Study.blend).
- Szene **House_10x12**: erster Hausaufbau. Szene **House_10x16_Variation**: längere Variante. Szene **Module_Library**: einzeln benannte Quellen und ihre UCX-Körper, am eigenen Ursprung überlagert; ein einzelnes Bauteil zur Bearbeitung isolieren.
- Im 3D-Viewport die Materialvorschau aktivieren und das Haus rahmen. Die Präsentationskameras, Lichter und der große Bildhintergrund werden vom Skript nur transient zum Rendern erzeugt und sind kein Teil der Modulexporte.
- [Vorne](Previews/house_front.png), [hinten](Previews/house_rear.png), [längere Variante](Previews/house_long_variant.png).

Die Hülle besitzt umlaufende Wände, Böden, zwei Giebelfüllungen und passende seitliche Dach-Wand-Füllteile. Der Eingang ist ein echtes Loch im Wandfeld; davor sitzt ein getrenntes statisches Türblatt. Rückseite und Seiten haben keinen zweiten Eingang. Fenster sind tatsächlich ausgespart und enthalten separate Geometrieflächen für die geschlossene Verglasung. Das Glasmaterial ist ein opaker Reflexionsplatzhalter, keine fertige transparente Glaslösung.

## Bauteile und Variation

Jeder FBX-Export enthält genau ein Render-Mesh sowie die in der Tabelle genannten zugehörigen UCX-Meshes. [Exports](Exports/) und [Manifest](manifest.json).

| Modul | Render-Dreiecke | UCX-Körper | Slots |
| --- | ---: | ---: | --- |
{table}

Die beiden Wandvarianten behalten dieselbe Struktur und unterscheiden sich in kleinen Holzdetails. Fenster-/Eingangsfelder belegen dieselben 2-m-Felder. Dachmittelteile sind wiederholbar; Dachenden besitzen angehobene Abschlüsse. Die drei seitlichen Dachfüllungen schließen Mittelfeld sowie beide Längsenden ab. Der zweite Hausaufbau verwendet dieselben Mesh-Datenblöcke ohne negative oder nichtuniforme Skalierung. Damit ist eine Längenvariation tatsächlich aufgebaut. Andere Hausbreiten, Geschosse, umfangreichere Silhouetten- oder Dachvarianten sind noch nicht hergestellt.

Die Fensterwand liegt mit 1.272 Dreiecken über der 1.000-Dreiecke-Reviewschwelle für einfache Wände: darin sind Bogenrahmen, Maßwerk, Glas und Sockel enthalten. Das ist eine zu prüfende Prototypausnahme, keine Freigabe zur Serienproduktion. Dachmodule bleiben unter 3.000 Dreiecken. Finale LOD-/Nanite- und Szenenbudgets sind offen.

## Vorläufige technische Konvention

- Blender Metric, Unit Scale 1, Koordinaten in Metern. Exportabbildung **UE_cm=(100*B.x,-100*B.y,100*B.z)**. Deshalb zeigt die Hausfront in Blender nach −Y und in Unreal nach +Y.
- Gerade Wandfelder: lokale Breite X0…2 m, tragende Hülle Y0…0,24 m nach innen, Z0…3,20 m. Unterer A-Startpivot `(0,0,0)`. Anschluss B bei `(2,0,0)`; bei einer geraden Fortsetzung fällt der A-Pivot der nächsten Instanz dort zusammen. Kleine Holzdetails stehen vor die strukturelle Hülle; Struktur- und Dekorgrenzen sind deshalb zu unterscheiden. Der Hauptpfosten gehört zur A-Seite, Holzverbindungen dürfen sich konstruktiv überdecken.
- Alle Module werden bei lokalen Identitätstransformationen exportiert. Hausinstanzen verwenden nur Translation und 0/90/180/270° Drehung bei Skalierung Eins. Ecken entstehen vorläufig aus rechtwinklig aufgestellten Wandlagen; es gibt noch kein eigenständiges finales Eckmodul.
- Dächer: feste vorläufige Wandspannweite 10 m, seitlich etwa 65 cm Überstand. Mittelfeld 2 m Länge, Endstück 2,8 m einschließlich Überstand. Keine freie Breitenskalierung vorgesehen. Geometrische Naht- und Dachfüllprüfung bestanden; finale Normalen-/Materialwirkung im Unreal-Reimport ist offen.
- Eingang: nominell 136 cm Breite, seitliche Bogenansätze bei 222 cm, Bogenspitze etwa 285 cm. Statisches Türblatt separat mit Gelenkbezug. Das ist **keine** neue Implementierung der vorhandenen Gameplay-Tür und kein beschlossener universeller Türstandard.

## Materiallieferung

Vier Materialgruppen **Plaster, Timber, Stone, Jade** liefern je drei tatsächliche 1024²-PNG-Dateien: BaseColor, Tangent-Normal und Roughness. Zusammen **12 Texturen**, relativ unter [Textures](Textures/), ohne externe Bibliotheken oder Rechnerpfade. Materialshader und Texturen wurden prozedural im eigenen Blender-Skript erzeugt; kein Imagegen-Ersatzbild und kein bloßes Debug-Farbschema. Bronze und die opake Glasfläche verwenden einfache eigene Vorschauparameter.

UV0 verwendet absichtliche Wiederholung/Kachelung; überlappungsfreie eindeutige Lightmap-UVs wurden nicht geliefert. Diese PBR-Materialien ersetzen keine bestehenden Unreal-Materialien. Blender-Normaltexturen verwenden die OpenGL/+Y-Konvention; Grünkanal-/Tangentenkonvention und Materialzuordnung müssen bei späterer Unreal-Integration gesondert geprüft werden. Ein FBX allein überträgt die Blender-Nodes nicht vollständig.

## Tatsächlich geprüft

Blender {v['blender']}, Quelle in neuem Prozess erneut geöffnet, alle **13 FBX-Dateien** jeweils in eine leere Blender-Szene importiert. Geschlossene orientierte Komponenten, positive Volumina, endliche Koordinaten/UVs, keine degenerierten Render-/UV-Dreiecke, erwartete Dreiecke/Slots/Körperzahlen, korrekte lokale Transformationen und verfügbare relative Texturen geprüft. Die Bauteile bestehen aus mehreren geschlossenen Bauteilvolumen; Holz-/Sockelverbindungen sind nicht zu einer einzigen Booleschen Hülle verschmolzen.

- Größte Bounds-Abweichung im FBX-Rückimport: {error:.10f} m.
- Größter Positionsversatz der eigentlichen Dachschale an den geprüften Modulnähten beider Hauslängen: {seam:.10f} m.
- Größte Abweichung der Giebel-/Seitenfüllpunkte von der tatsächlich abgetasteten Dachunterseite: {fit:.10f} m.
- Beide Aufbauten: je ein Eingang, gemeinsame Modul-Meshdaten, Einheitsskalierung; `verification.json` enthält tatsächliche Werte.
- Erhaltung: {preservation['unchanged_files']} von {preservation['baseline_files']} vorab erfassten Dateien bytegleich; geändert wurden nur die drei passenden Designdokumente zur Nutzerauswahl. Die vorherige Refiner-Lieferung besteht weiter mit allen 31 unveränderten Prüfsummen.

Prüfbelege: [verification.json](verification.json), `Evidence/verify.log`, `Evidence/render.log`, [Erhaltung](Evidence/preservation.json). Die erfolgreiche Prüfung wird von korrigierten Entwicklungsversuchen getrennt: Rundungsfehler am Türbogen, nicht ausgewertete Matrizen der inaktiven Vergleichsszene, eine beinahe doppelte Sampling-Endposition und ein abgewiesenes Ersetzen der eigenen Zwischenquelle. Frühere Logs bleiben als Belege erhalten. Die eigene Zwischenquelle wurde lokal als ignorierte `.blend1`-Sicherung bewahrt. Keine Warnungen unterdrückt; Blender meldet DeprecationWarnings zu Material-/World-Node-Eigenschaften.

## Grenzen und nächster Schritt

Noch **kein gebrauchsfertiges Gameplay-Haus**: Türinteraktion und vollständige geprüfte Kollision fehlen. Giebel, obere Seitenfüllungen, Türblatt und Eingangsvordach besitzen noch keine eigene freigegebene Kollision. Geschlossene Fenster verwenden bewusst einen einfachen vollen Blockkörper. Die sechs oberen Eingangshüllen vereinfachen den Bogen; der freie Mindestquerschnitt muss mit der tatsächlichen Kapsel geprüft werden. Dachkollision ist eine konservative konvexe Annäherung mit 16 Streifen je Teil und ersetzt keinen Kapsel-/Kameratest. Das begehbare Hauptgeschoss liegt unter den Dachfüllungen; Dachbegehung ist nicht geprüft.

Offen: Beurteilung der tatsächlichen Hausproportionen durch den Nutzer, weitere Detail-/Materialqualität, finales Eck-/Anschlusskonzept, genaue Kollisionsabnahme, funktionierende Gameplay-Tür, Unreal-Import/Reimport/Normalen/UVs/Materialien, PIE/Kamera, Performance, LODs/Nanite, Packaging und Multiplayer. Der spätere Importweg bleibt der kalibrierte **Legacy FbxFactory/FbxStaticMeshImportData-Pfad mit FBX_SCALE_NONE**; Interchange ist nicht validiert.

Nächster sinnvoller Schritt: das hier sichtbare echte Modell beurteilen und die konkreten Korrekturen festlegen, danach den kleinsten kompletten Hausstand gezielt in Unreal integrieren. Bestehende Karten, Content, Materialien, Blueprints, gemeinsame Generatoren und Projektkonfiguration wurden nicht geändert. Keine Commits, Pushes oder neuen Worktrees.
'''
    text=text.replace('Die sechs oberen Eingangshüllen','Die vereinfachten oberen Eingangshüllen')
    (ROOT/'README.md').write_text(text,encoding='utf-8',newline='\n')
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and p.suffix!='.blend1')
    (ROOT/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files),encoding='utf-8',newline='\n')
    print('HOUSE_DRAFT_DELIVERY_OK',len(m['assets']),'modules;',len(files),'files hashed; prior wall delivery unchanged')

if __name__=='__main__':main()

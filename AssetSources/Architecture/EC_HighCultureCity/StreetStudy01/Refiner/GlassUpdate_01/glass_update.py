"""Blender-only clear-glass revision. Frozen parent and open GUI files are untouched.

Modes: prepare, verify, render --view NAME, seal. No exports or Unreal operations.
"""
from pathlib import Path
import argparse,hashlib,json,math,subprocess,sys
sys.dont_write_bytecode=True
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent;PARENT=ROOT.parent;REPO=PARENT.parents[4]
PARENT_MANIFEST=json.loads((PARENT/'manifest.json').read_text(encoding='utf-8'))
STUDY='A' if PARENT_MANIFEST['module_id']=='StreetStudy01' else 'B'
BLEND=ROOT/(PARENT_MANIFEST['module_id']+'_ClearGlass.blend')
VIEW_NAMES=['01_window_outside','02_window_inside','03_daylight_room','04_daylight_opaque_control']
OTHER=REPO/('AssetSources/Architecture/ER_RootRetreat/CourtyardStudy01/Refiner/GlassUpdate_01' if STUDY=='A' else 'AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner/GlassUpdate_01')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,data):
    p=ROOT/name;assert p.resolve().is_relative_to(ROOT.resolve());p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def mesh_fingerprint(me):
    data=dict(vertices=[list(v.co) for v in me.vertices],faces=[list(p.vertices) for p in me.polygons],
        slots=[m.name if m else None for m in me.materials],material_indices=[p.material_index for p in me.polygons],
        uv=[dict(name=u.name,coords=[list(d.uv) for d in u.data]) for u in me.uv_layers])
    return hashlib.sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()
def material_state(mat):
    def value(v):
        if isinstance(v,(float,int,str,bool)):return v
        try:return list(v)
        except TypeError:return str(v)
    return dict(diffuse_color=list(mat.diffuse_color),nodes=[dict(name=n.name,type=n.bl_idname,
        inputs={i.identifier:value(i.default_value) for i in n.inputs if hasattr(i,'default_value')}) for n in mat.node_tree.nodes],
        links=[[l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier] for l in mat.node_tree.links])
def snapshot():
    return dict(meshes={me.name:mesh_fingerprint(me) for me in bpy.data.meshes},
        objects={o.name:dict(data=o.data.name if o.data else None,matrix=[list(row) for row in o.matrix_world]) for o in bpy.data.objects if o.type=='MESH'},
        other_materials={m.name:material_state(m) for m in bpy.data.materials if m.name!='Glass'})
def check_preservation():
    base=read('Evidence/preservation_before.json');changed=[];external=[]
    audit_path=(ROOT if STUDY=='A' else OTHER)/'Evidence/external_parent_save.json'
    audit=json.loads(audit_path.read_text()) if audit_path.exists() else None
    for name,h in base['files'].items():
        p=REPO/name
        if not p.is_file() or sha(p)!=h:
            if audit and name==audit['parent_file'] and p.is_file() and sha(p)==audit['current_sha256'] and h==audit['input_sha256']:
                assert audit['geometry_slots_uvs_transforms_and_other_materials_equal'] and audit['parent_glass_equal_to_input']
                external.append(dict(file=name,input_sha256=h,externally_saved_sha256=audit['current_sha256'],
                    preserved_without_overwrite=True,read_only_audit=audit_path.relative_to(ROOT,walk_up=True).as_posix()))
            else:changed.append(name)
    assert not changed,changed
    return dict(status='passed',files_checked=len(base['files']),files_byte_identical=len(base['files'])-len(external),
        externally_saved_parent_sources=external,unexpected_changes_outside_glass_updates=[],no_unreal_operations=True)
def pane():
    tag='House_A' if STUDY=='A' else 'WestWing'
    prefix='City' if STUDY=='A' else 'Retreat'
    candidates=[bpy.data.objects[e['object']] for e in PARENT_MANIFEST['placement_instances']
        if prefix+'WindowGlass' in e['asset'] and tag in e['object']]
    assert candidates
    # The first placed window is in the front facade of the selected house/wing.
    return candidates[0]
def view_geometry():
    obj=pane();center=obj.matrix_world@Vector((0,.115,.4))
    outward=(obj.matrix_world.to_3x3()@Vector((0,-1,0))).normalized()
    right=(obj.matrix_world.to_3x3()@Vector((1,0,0))).normalized();up=Vector((0,0,1))
    views={
      '01_window_outside':(center+outward*2.1+right*.35+up*.08,center-outward*.4,38),
      '02_window_inside':(center-outward*1.6+right*.28+up*.08,center+outward*2,30),
      '03_daylight_room':(center-outward*3.0+right*1.15+up*.1,center-outward*.25-up*.42,24)}
    if STUDY=='A':
        views['03_daylight_room']=(center-outward*3.0+right*1.15+up*.1,center-outward*.6-up*.95,20)
    views['04_daylight_opaque_control']=views['03_daylight_room']
    return obj,center,outward,views
def set_camera(view):
    _,_,_,views=view_geometry();pos,target,lens=views[view];cam=bpy.context.scene.camera
    cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=lens
    cam.data.clip_start=.02;cam.data.clip_end=1000
def prepare():
    assert REPO==Path('E:/Business/fantasy-rpg-refiner')
    assert subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip()=='assets/refiner'
    assert not BLEND.exists(),'Do not overwrite an existing glass revision'
    files={}
    for folder in ['Content','AssetSources','Config','Source','Tools','docs']:
        for p in (REPO/folder).rglob('*'):
            if p.is_file() and not any(p.is_relative_to(r) for r in [ROOT,OTHER]) and '__pycache__' not in p.parts and not p.name.endswith('.blend1'):
                files[p.relative_to(REPO).as_posix()]=sha(p)
    for n in ['AGENTS.md','.gitattributes','.gitignore','FantasyLifeRPG.uproject']:files[n]=sha(REPO/n)
    write('Evidence/preservation_before.json',dict(files=files,head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()))
    for line in (PARENT/'SHA256SUMS').read_text().splitlines():
        h,n=line.split(maxsplit=1);assert sha(PARENT/n)==h,n
    source=PARENT/PARENT_MANIFEST['source_blend'];assert sha(source)==PARENT_MANIFEST['source_blend_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source));before=snapshot();write('Evidence/geometry_before.json',before)
    glass=bpy.data.materials['Glass'];old=material_state(glass);nodes=glass.node_tree.nodes;nodes.clear()
    output=nodes.new('ShaderNodeOutputMaterial');output.location=(540,50)
    bsdf=nodes.new('ShaderNodeBsdfPrincipled');bsdf.name='ClearGlass_Principled';bsdf.location=(-120,100)
    bsdf.inputs['Base Color'].default_value=(.98,.995,1,1)
    bsdf.inputs['Transmission Weight'].default_value=1
    bsdf.inputs['Roughness'].default_value=.025
    bsdf.inputs['IOR'].default_value=1.45
    bsdf.inputs['Alpha'].default_value=1
    path=nodes.new('ShaderNodeLightPath');path.location=(-400,-220)
    transparent=nodes.new('ShaderNodeBsdfTransparent');transparent.location=(-100,-180)
    transparent.inputs['Color'].default_value=(1,1,1,1)
    mix=nodes.new('ShaderNodeMixShader');mix.name='ArchitecturalShadowTransmission';mix.location=(310,50)
    links=glass.node_tree.links;links.new(path.outputs['Is Shadow Ray'],mix.inputs[0]);links.new(bsdf.outputs['BSDF'],mix.inputs[1]);links.new(transparent.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],output.inputs['Surface'])
    glass.diffuse_color=(.98,.995,1,1)
    glass['review_note']='Clear refraction for camera rays; transparent shadow rays for direct daylight. Architectural approximation, no refractive caustic simulation.'
    assert snapshot()==before,'Only the Glass shader may change'
    scene=bpy.context.scene;scene.cycles.max_bounces=12;scene.cycles.transmission_bounces=8;scene.cycles.transparent_max_bounces=8
    scene.cycles.preview_samples=16
    _,_,_,views=view_geometry();pos,target,lens=views['02_window_inside']
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                space=area.spaces.active;space.clip_start=.02;space.clip_end=1000;space.lens=lens
                space.shading.type='RENDERED';space.overlay.show_overlays=False
                space.region_3d.view_perspective='PERSP';space.region_3d.view_distance=.5
                space.region_3d.view_rotation=(target-pos).to_track_quat('-Z','Y')
                space.region_3d.view_location=pos+(target-pos).normalized()*.5
    scene['glass_review_views_json']=json.dumps({n:[list(p),list(t),l] for n,(p,t,l) in views.items()})
    scene['status']='refiner_glass_review';set_camera('02_window_inside')
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    write('manifest.json',dict(kit_id=PARENT_MANIFEST['kit_id'],module_id=PARENT_MANIFEST['module_id'],interface_version=PARENT_MANIFEST['interface_version'],
      status='refiner_active',accepted=False,scope='Blender glass material only; no FBX or Unreal integration',
      parent_refiner_commit=read('Evidence/preservation_before.json')['head'],parent_manifest='../manifest.json',
      parent_source='../'+source.name,parent_source_sha256=sha(source),source_blend=BLEND.name,source_blend_sha256=sha(BLEND),
      parent_refiner_revision=PARENT_MANIFEST.get('refiner_revision'),refiner_revision=PARENT_MANIFEST.get('refiner_revision',0)+1,
      material_slot='Glass',geometry_unchanged=True,transmission_weight=1,roughness=.025,ior=1.45,base_color_linear=[.98,.995,1,1],
      shadow_policy='Is Shadow Ray -> white Transparent BSDF; camera/refraction rays -> Principled transmission. Direct-light approximation, no caustics.',
      parent_fbx_exports_unchanged=True,new_fbx_exports_performed=False,unreal_import_performed=False,
      views={n:[list(p),list(t),l] for n,(p,t,l) in views.items()}))
    write('Evidence/material_change.json',dict(status='passed',before=old,after=material_state(glass),geometry_slots_transforms_and_other_materials_unchanged=True))
    print('CLEAR_GLASS_PREPARED',STUDY,flush=True)
def verify():
    m=read('manifest.json');assert sha(BLEND)==m['source_blend_sha256'];bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    assert snapshot()==read('Evidence/geometry_before.json')
    glass=bpy.data.materials['Glass'];node=glass.node_tree.nodes['ClearGlass_Principled']
    assert node.inputs['Transmission Weight'].default_value==1 and abs(node.inputs['Roughness'].default_value-.025)<1e-6
    assert any(l.from_socket.name=='Is Shadow Ray' for l in glass.node_tree.links)
    obj=pane();scene=bpy.context.scene;hits=[]
    # Real saved glass volume: two ray intersections (outside and inside surfaces).
    for x,z in [(-.2,.15),(.2,.15),(-.2,.65),(.2,.65)]:
        origin=Vector((x,-.2,z));direction=Vector((0,1,0));a=obj.ray_cast(origin,direction,distance=1)
        assert a[0];b=obj.ray_cast(a[1]+direction*.0001,direction,distance=1);assert b[0]
        thickness=(b[1]-a[1]).length;assert abs(thickness-.03)<1e-5;hits.append(dict(local_x=x,local_z=z,thickness_m=thickness))
    write('Evidence/source_verification.json',dict(status='passed',source_reopened=True,all_mesh_geometry_uvs_slot_indices_and_instance_transforms_exact=True,
        other_materials_exact=True,glass_node_graph_verified=True,pane_object=obj.name,glass_volume_rays=hits,
        original_fbx_and_ucx_unchanged=True,unreal_import=False))
    write('Evidence/preservation_after.json',check_preservation());print('CLEAR_GLASS_SOURCE_VERIFIED',STUDY,flush=True)
def render(view):
    assert view in VIEW_NAMES;bpy.ops.wm.open_mainfile(filepath=str(BLEND));scene=bpy.context.scene
    obj,center,outward,views=view_geometry();set_camera(view)
    # Actual house, all walls/roofs/other windows remain. No interior fill lights.
    for light in [o for o in scene.objects if o.type=='LIGHT']:
        if light.data.type!='SUN':light.hide_render=True
        else:
            direction=-outward*.65+Vector((0,0,-.75));light.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();light.data.energy=2.7
    scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.45
    scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.cycles.seed=1234
    scene.render.resolution_x=1280;scene.render.resolution_y=960;scene.render.resolution_percentage=100
    if 'daylight' in view:scene.render.resolution_percentage=65
    if view=='04_daylight_opaque_control':
        opaque=bpy.data.materials.new('TemporaryOpaqueControl');opaque.use_nodes=True
        opaque.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.03,.03,.03,1)
        obj.material_slots[0].link='OBJECT';obj.material_slots[0].material=opaque
    scene.render.image_settings.file_format='PNG';(ROOT/'Previews').mkdir(exist_ok=True)
    scene.render.filepath=str(ROOT/'Previews'/(view+'.png'));bpy.ops.render.render(write_still=True)
    if 'daylight' in view:
        # Sample the actual floor patch projected through this pane under the sun.
        floor=center-outward*(center.z*.65/.75);floor.z=.001
        rendered=bpy.data.images.load(scene.render.filepath,check_existing=False);width,height=rendered.size;pixels=list(rendered.pixels[:]);values=[]
        for i in range(9):
            for j in range(9):
                p=floor+Vector((.02*(i-4),.02*(j-4),0));ndc=world_to_camera_view(scene,scene.camera,p)
                assert 0<ndc.x<1 and 0<ndc.y<1,(view,tuple(ndc))
                x=int(ndc.x*width);y=int(ndc.y*height);index=4*(y*width+x)
                values.append(.2126*pixels[index]+.7152*pixels[index+1]+.0722*pixels[index+2])
        write('Evidence/'+view+'.json',dict(view=view,mean_floor_patch_linear_luminance=sum(values)/len(values),floor_receiver_m=list(floor),
            luminance_space='Display-linear PNG values after AgX; relative comparison, not scene radiance or lux',
            samples=len(values),sun_direction=list(-outward*.65+Vector((0,0,-.75))),interior_lights=False,only_selected_pane_opaque=view=='04_daylight_opaque_control'))
    write('Evidence/render_'+view+'.json',dict(status='passed',file='Previews/'+view+'.png',sha256=sha(ROOT/'Previews'/(view+'.png')),
        source_sha256=sha(BLEND),cycles_samples=48,sun_aimed_at_selected_window=True,sky_strength=.45,no_interior_fill_lights=True,
        camera=dict(position=list(views[view][0]),target=list(views[view][1]),lens_mm=views[view][2]),
        temporary_control_only=view=='04_daylight_opaque_control',temporary_setup_not_saved=True))
    print('CLEAR_GLASS_RENDERED',STUDY,view,flush=True)
def seal():
    m=read('manifest.json');assert sha(BLEND)==m['source_blend_sha256']
    assert read('Evidence/source_verification.json')['status']=='passed'
    for name in VIEW_NAMES:assert read('Evidence/render_'+name+'.json')['source_sha256']==sha(BLEND)
    clear=read('Evidence/03_daylight_room.json')['mean_floor_patch_linear_luminance'];opaque=read('Evidence/04_daylight_opaque_control.json')['mean_floor_patch_linear_luminance']
    assert clear>opaque*1.10,(clear,opaque,'No measurable daylight through selected pane')
    proof=dict(status='passed',clear_floor_luminance=clear,opaque_floor_luminance=opaque,ratio=clear/max(opaque,1e-9),
        scope='Actual complete house, fixed sun/sky/camera, selected pane alone switched opaque for control; 81 projected floor samples from display-linear PNG after AgX, no interior fill',
        limitation='Architectural transparent-shadow approximation, not refractive caustic simulation or calibrated illuminance measurement')
    write('Evidence/daylight_comparison.json',proof);preservation=check_preservation();write('Evidence/preservation_after.json',preservation)
    m.update(status='review_ready',accepted=False,verification='Evidence/source_verification.json',daylight_verification=proof,
        preservation=preservation,
        previews=[dict(file='Previews/'+n+'.png',sha256=sha(ROOT/'Previews'/(n+'.png')),view=n) for n in VIEW_NAMES])
    write('manifest.json',m)
    review=f'''# Glasprüfung – Studie {STUDY}

Status **review_ready**, nicht accepted. Eigenständige Blender-Glasfassung aus Refiner-Commit `{m['parent_refiner_commit']}`.
Quelle: `{BLEND.name}`, SHA-256 `{sha(BLEND)}`. Eingangsquelle `{m['parent_source']}`, SHA-256 `{m['parent_source_sha256']}`.

Nur das vorhandene Material **Glass** wurde geändert: Transmission 1, Roughness 0,025, IOR 1,45, fast neutraler heller Farbton. Geschlossene 3-cm-Scheibe und bestehende leichte Brechung/Reflexion bleiben. Schattenstrahlen verwenden einen weißen Transparent-BSDF, damit direktes Tageslicht die Scheibe passiert. Das ist eine ausdrücklich dokumentierte Architektur-Näherung; keine berechneten Brechungskaustiken oder reale Transmissionsmessung.

Alle Meshkoordinaten, Flächen, UVs, Materialslotnamen/-reihenfolgen, Instanztransforms und übrigen Materialien sind nach erneutem Öffnen der Glasfassung exakt identisch zum übernommenen Stand. Die ursprünglichen Refiner-Dateien wurden durch diesen Auftrag nicht beschrieben. Während des Renderns wurde die geöffnete ursprüngliche A-Quelle außerhalb dieses Auftrags gespeichert; ihr neuer Hash und der lesende Vergleich von Geometrie, UVs, Slots, Instanztransforms und Materialien stehen im gesonderten A-Beleg `Evidence/external_parent_save.json` sowie im [Erhaltungsbericht](Evidence/preservation_after.json). Diese Speicherung bleibt erhalten und wird nicht zurückgesetzt. Alle anderen **{preservation['files_byte_identical']}** geprüften Bestandsdateien bleiben byteidentisch, einschließlich FBX, Creator, alter Musterhäuser, Content, Blueprints, Maps, Konfiguration und gemeinsamer Tools. Keine offenen Blender-Fenster neu geladen oder deren ungespeicherte Arbeit überschrieben.

Die neue Quelle startet mit einer Innenansicht in **Rendered** (Cycles), damit die Glasdurchsicht sichtbar wird; Solid zeigt keine echte Transparenz. Die ursprünglichen Szeneleuchten bleiben in der gespeicherten Quelle erhalten. Neue Review-Ansichten stehen in `glass_review_views_json`.

## Reale Ansichten und Tageslichtprüfung

- [Außen](Previews/01_window_outside.png): echter eingebauter Fensterrahmen und Durchsicht ins Haus.
- [Innen](Previews/02_window_inside.png): Durchsicht nach draußen.
- [Raum mit Tageslicht](Previews/03_daylight_room.png).
- [Opake Kontrollscheibe](Previews/04_daylight_opaque_control.png): dieselbe Szene/Kamera/Beleuchtung, nur die ausgewählte Scheibe temporär opak.

Cycles, 48 Samples, AgX. Für diese vier Prüfaufnahmen wird die vorhandene Sonne gezielt zum gewählten Fenster ausgerichtet. Himmel bleibt bei Stärke 0,45; keine Innenraum-Aufhellleuchte. Die Wände, Dachflächen, übrigen Fenster und Türen bleiben vorhanden. Die temporären Render-/Kontrolleinstellungen werden nicht in die Quelle gespeichert. Der Tageslichtvergleich misst an 81 projizierten Punkten der tatsächlichen Innenbodenfläche die displaylineare PNG-Helligkeit nach AgX: klar **{clear:.6f}**, opak **{opaque:.6f}**, Verhältnis **{proof['ratio']:.3f}**. Das belegt den Lichteinfall dieser Scheibe, ist keine Messung von Szenenradiance/Lux oder vollständige Lichtplanung.

## Übergabe

Eigene Quelle und Manifest unter diesem Glas-Unterstand; die ältere Elternlieferung bleibt als eingefrorener vorheriger Stand erhalten. Keine neuen FBX notwendig für diesen reinen Blender-Materialauftrag. Der Blender-Shader ist nicht vollständig per FBX nach Unreal übertragbar; ein Unreal-Glasmaterial und tatsächliche Durchsicht, Schatten, Tageslicht und Performance sind später separat zu prüfen. Kein Unreal-Import, kein Commit und kein Push in diesem Auftrag. Frühere Geometrieprüfungen gelten für die exakt unveränderten Meshes; in diesem Schritt wurde kein erneuter FBX-Rückimport behauptet.

Reproduktion: `glass_update.py -- --mode prepare` nur in einem noch nicht erzeugten Unterstand; danach `--mode verify`, `--mode render --view NAME` für alle vier Ansichten, Sichtprüfung und `--mode seal`. Prüfsummenliste umfasst alle Lieferdateien außer sich selbst.
'''
    (ROOT/'REVIEW.md').write_text(review,encoding='utf-8',newline='\n')
    (ROOT/'.gitattributes').write_text('*.py text eol=lf\n*.md text eol=lf\n*.json -text\nSHA256SUMS text eol=lf\n.gitattributes text eol=lf\n',encoding='utf-8',newline='\n')
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and '__pycache__' not in p.parts)
    (ROOT/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files),encoding='utf-8',newline='\n')
    print('CLEAR_GLASS_REVIEW_READY',STUDY,proof,flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['prepare','verify','render','seal'],required=True);parser.add_argument('--view',choices=VIEW_NAMES)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if args.mode=='render':render(args.view)
    else:{'prepare':prepare,'verify':verify,'seal':seal}[args.mode]()

"""Refine only the smaller house and place a walkable catalogue of every used mesh next to it."""
import json,math
AS='editor_toolset.toolsets.asset.AssetTools';SC='editor_toolset.toolsets.scene.SceneTools';AC='editor_toolset.toolsets.actor.ActorTools'
OB='editor_toolset.toolsets.object.ObjectTools';SM='editor_toolset.toolsets.static_mesh.StaticMeshTools'
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Refiner/HouseStudy_B01/Musterhaus_B03/'
MAP='/Game/Prototype/Maps/Lvl_AssetLab';MAT='/Game/Art/Materials/ElvenHouseB03';OLD='/Game/Art/Architecture/ElvenHouseB01'
ARCH='/Game/Art/Architecture/ElvenHouseB03';FURN='/Game/Art/Furniture/ElvenHouseB03'
PREFIX='Lab_EH_B03_'
def tool(g,op,**args):return execute_tool(g+'.'+op,json.dumps(args)).get('returnValue')
def ref(p):return dict(refPath=p+'.'+p.rsplit('/',1)[-1])
def vec(x,y,z):return dict(x=x,y=y,z=z)
def props(o,**v):
    tool(OB,'list_properties',instance=o);assert tool(OB,'set_properties',instance=o,values=json.dumps(v))
def get(o,fields):return json.loads(tool(OB,'get_properties',instance=o,properties=fields))
def asset_path(n):return (ARCH if any(s in n for s in ['Interior','Ceiling']) else FURN)+'/Meshes/'+n
def run():
    assert tool(SC,'get_current_level')==MAP and not tool('EditorToolset.EditorAppToolset','IsPIERunning')
    with open(ROOT+'manifest.json','r') as f:data=json.load(f)
    actors={tool(AC,'get_label',actor=a):a for a in tool(SC,'find_actors',name='',tag='',collision_channels=[])}
    # Idempotence only for this new delivery's own actors.
    for label,a in actors.items():
        if label.startswith(PREFIX):tool(SC,'remove_from_scene',actor=a)
    placed={};changed=[]
    def place(label,path,loc,yaw=0,scale=(1,1,1),folder='House'):
        a=tool(SC,'add_to_scene_from_asset',asset_path=path,name=PREFIX+label,
            xform=dict(location=vec(*loc),rotation=dict(pitch=0,yaw=yaw,roll=0),scale=vec(*scale)),snap_to_ground=False)
        tool(SC,'set_actor_folder',actor=a,folder_path='Lab/Architecture/ElvenHouseB03/'+folder);placed[PREFIX+label]=a;return a
    def override(actor,rolemap,variant=0):
        for comp in tool(AC,'get_components',actor=actor,component_type=dict(refPath='/Script/Engine.StaticMeshComponent')):
            value=get(comp,['staticMesh','overrideMaterials']);mesh=value['staticMesh']
            if not mesh:continue
            slots=tool(SM,'get_material_slots',mesh=mesh)
            overrides=[]
            for s in slots:
                role=s if isinstance(s,str) else s['slotName'] if 'slotName' in s else s['name'] if 'name' in s else s['materialSlotName']
                role=role.replace('B03_','')
                path=rolemap.get(role)
                if role=='Glass':path='/Game/Art/Materials/ElvenHouseB01/M_EH_Glass_Clear'
                if path:overrides.append(ref(path))
                else:overrides.append(None)
            if len(value['overrideMaterials'])!=len(overrides):props(comp,overrideMaterials=[])
            props(comp,overrideMaterials=overrides)
    # Component overrides leave shared old meshes/materials and the long house unchanged.
    for label,a in actors.items():
        if not label.startswith('Lab_EH_B02_House_10x12_'):continue
        mapping={k:MAT+'/M_EH03_'+k for k in data['material_families']}
        if 'Step' in label or 'Foundation' in label:mapping={'Material':MAT+'/M_EH03_Stone','WorldGridMaterial':MAT+'/M_EH03_Stone'}
        index=int(label.split('House_10x12_')[1].split('_')[0]) if 'Foundation' not in label else 0
        if index%4==1:mapping['Plaster']=MAT+'/MI_EH03_Plaster_Warm'
        elif index%4==3:mapping['Plaster']=MAT+'/MI_EH03_Plaster_Cool'
        # The floor gets board seams without imposing seams onto structural beams.
        components=tool(AC,'get_components',actor=a,component_type=dict(refPath='/Script/Engine.StaticMeshComponent'))
        for comp in components:
            value=get(comp,['staticMesh']);mesh=value['staticMesh']
            if mesh and 'Floor_' in mesh['refPath']:mapping['Stone']=MAT+'/M_EH03_Floor'
        override(a,mapping,index);changed.append(label)
    for i,item in enumerate(data['placements']):
        loc=[-2400+100*item['location_m'][0],-1900-100*item['location_m'][1],31+100*item['location_m'][2]]
        yaw=-item['yaw_blender'];name=item['module'];path=asset_path(name)
        if item['light']:
            kind=name.replace('SM_EH03_','').removesuffix('_24');path=FURN+'/Blueprints/BP_EH03_'+kind
        a=place('Interior_%02d_'%i+name,path,loc,yaw,folder='House/'+item['zone'])
        if item['light']:
            comp=tool(AC,'get_components',actor=a,component_type=dict(refPath='/Script/Engine.PointLightComponent'))[0]
            props(comp,intensity=item['light']['lumens'],attenuationRadius=item['light']['radius_cm'],temperature=item['light']['temperature'])
        elif 'Timber' in data['assets'][name]['slots'] and i%3==1:
            mapping={k:MAT+'/M_EH03_'+k for k in data['material_families']};mapping['Timber']=MAT+'/MI_EH03_Timber_Honey';override(a,mapping)
    def text(label,message,loc,size=16):
        a=tool(SC,'add_to_scene_from_class',actor_type=dict(refPath='/Script/Engine.TextRenderActor'),name=PREFIX+label,
            xform=dict(location=vec(*loc),rotation=dict(pitch=0,yaw=90,roll=0),scale=vec(1,1,1)),snap_to_ground=False)
        tool(SC,'set_actor_folder',actor=a,folder_path='Lab/Architecture/ElvenHouseB03/Catalogue/Labels')
        comp=tool(AC,'get_components',actor=a,component_type=dict(refPath='/Script/Engine.TextRenderComponent'))[0]
        props(comp,text=message,worldSize=size,horizontalAlignment='EHTA_Center',textRenderColor=dict(r=225,g=220,b=195,a=255))
        placed[PREFIX+label]=a
    # Catalogue contains exactly one instance of every render mesh used by the sample.
    catalogue={name:asset_path(name) for name in data['assets']}
    with open(ROOT+'../manifest.json','r') as f:old=json.load(f)
    for item in old['assets']:
        n=item['name']
        if n!='SM_EH_Wall_Window_200x24x320':catalogue[n]=OLD+'/Meshes/'+n
    for n in ['SM_EH_Wall_WindowOpening_200x24x320','SM_EH_WindowFrame_Arch_100x173','SM_EH_WindowGlass_Arch_100x173']:catalogue[n]=OLD+'/Windows/Meshes/'+n
    entries=[]
    for n,p in catalogue.items():
        b=tool(SM,'get_bounds',mesh=ref(p));lo=b['min'];hi=b['max']
        entries.append(dict(module=n,path=p,lo=lo,hi=hi,width=hi['x']-lo['x'],depth=hi['y']-lo['y']))
    entries.sort(key=lambda e:-e['width'])
    x=-5800;y=-850;row_depth=0;layout=[]
    for i,e in enumerate(entries):
        width=max(e['width'],140)+100;depth=max(e['depth'],130)+130
        if x+width>-2860:x=-5800;y-=row_depth;row_depth=0
        assert y-depth>-3950,('Catalogue outside Lab',e['module'],y,depth)
        loc=[x+50-e['lo']['x'],y-65-e['hi']['y'],2-e['lo']['z']]
        a=place('Catalogue_%02d_'%i+e['module'],e['path'],loc,folder='Catalogue/Meshes')
        mapping={k:MAT+'/M_EH03_'+k for k in data['material_families']}
        if 'Floor_' in e['module']:mapping['Stone']=MAT+'/M_EH03_Floor'
        override(a,mapping)
        label=e['module'].replace('SM_EH03_','').replace('SM_EH_','')
        text('Label_%02d'%i,label,[x+width/2,y+10,32],13)
        # Thin nonblocking visual bay with the old neutral review-ground material.
        tile=place('Bay_%02d'%i,'/Engine/BasicShapes/Cube',[x+width/2,y-depth/2,0],scale=((width-30)/100,(depth-35)/100,.02),folder='Catalogue/Bays')
        comp=tool(AC,'get_components',actor=tile,component_type=dict(refPath='/Script/Engine.StaticMeshComponent'))[0]
        props(comp,overrideMaterials=[ref('/Game/Art/Materials/ElvenHouseB01/M_EH_ReviewGround')],bodyInstance=dict(collisionProfileName='NoCollision',collisionEnabled='NoCollision'))
        layout.append(dict(module=e['module'],actor=a,position_cm=loc,bay=[x,y,width,depth],bounds=e))
        x+=width;row_depth=max(row_depth,depth)
    text('Catalogue_Title','BAUTEILE UND EINRICHTUNG / B03',[-4400,-690,130],30)
    text('Sample_Title','MUSTERHAUS B03 / Wohnen - Schlafen - Lager',[-1900,-1550,335],22)
    assert tool(AS,'save_assets',asset_paths=[MAP])
    return dict(map=MAP,modified_small_house_actors=changed,new_actors=placed,catalogue=layout,
        catalogue_mesh_count=len(catalogue),interior_instances=len(data['placements']),rooms=['Wohn-/Essbereich','Schlafraum','Lager'],
        no_hidden_fill_lights=True,comparison_house_unchanged=True)

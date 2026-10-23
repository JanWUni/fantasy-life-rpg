"""Add a labelled independent comparison area. Never touch existing house actors."""
import json
AS='editor_toolset.toolsets.asset.AssetTools';SC='editor_toolset.toolsets.scene.SceneTools'
AC='editor_toolset.toolsets.actor.ActorTools';OB='editor_toolset.toolsets.object.ObjectTools'
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner/WallCatalogue_01/'
ARCH='/Game/Art/Architecture/WallCatalogue01';FURN='/Game/Art/Furniture/WallCatalogue01'
PREFIX='Lab_WC01_'
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def props(o,**v):
    tool(OB,'list_properties',instance=o);assert tool(OB,'set_properties',instance=o,values=json.dumps(v))
def vec(x,y,z):return dict(x=x,y=y,z=z)
def xf(p,yaw=0,scale=(1,1,1)):return dict(location=vec(*p),rotation=dict(pitch=0,yaw=yaw,roll=0),scale=vec(*scale))
def run():
    MAP='/Game/Prototype/Maps/Lvl_AssetLab'
    assert tool(SC,'get_current_level')==MAP and not tool('EditorToolset.EditorAppToolset','IsPIERunning')
    with open(ROOT+'manifest.json','r') as f:data=json.load(f)
    assert not any(tool(AC,'get_label',actor=a).startswith(PREFIX) for a in tool(SC,'find_actors',name='',tag='',collision_channels=[]))
    placed=[]
    def put(label,path,loc,yaw=0,kind='Mesh',scale=(1,1,1)):
        a=tool(SC,'add_to_scene_from_asset',asset_path=path,name=PREFIX+label,xform=xf(loc,yaw,scale),snap_to_ground=False)
        tool(SC,'set_actor_folder',actor=a,folder_path='Lab/Architecture/WallCatalogue01/'+kind)
        placed.append(dict(label=PREFIX+label,actor=a,path=path,location_cm=loc,yaw=yaw,kind=kind));return a
    def mesh(label,n,loc,yaw=0):
        info=data['assets'][n];path=(FURN if info['kind'] in ['Lamp','Furniture'] else ARCH)+'/Meshes/'+n
        a=put(label,path,loc,yaw)
        c=tool(AC,'get_components',actor=a,component_type=dict(refPath='/Script/Engine.StaticMeshComponent'))[0]
        if info['kind'] in ['Window','Lamp']:props(c,bodyInstance=dict(collisionProfileName='NoCollision',collisionEnabled='NoCollision'))
        else:props(c,bodyInstance=dict(collisionProfileName='BlockAll',collisionEnabled='QueryAndPhysics'))
        if info['kind']=='Glass':props(c,castShadow=False)
        return a
    def text(label,message,loc,size=22):
        a=tool(SC,'add_to_scene_from_class',actor_type=dict(refPath='/Script/Engine.TextRenderActor'),name=PREFIX+label,xform=xf(loc,90),snap_to_ground=False)
        tool(SC,'set_actor_folder',actor=a,folder_path='Lab/Architecture/WallCatalogue01/Labels')
        c=tool(AC,'get_components',actor=a,component_type=dict(refPath='/Script/Engine.TextRenderComponent'))[0]
        props(c,text=message,worldSize=size,horizontalAlignment='EHTA_Center',textRenderColor=dict(r=240,g=235,b=215,a=255))
        placed.append(dict(label=PREFIX+label,actor=a,location_cm=loc,kind='Label'))
    for x,style,title in [(-2200,'A','A / PUTZ + HOLZ'),(-1200,'B','B / HOLZRAHMEN'),(-200,'C','C / STEINSOCKEL')]:
        for y,window in [(2000,False),(3000,True)]:
            n='SM_WC01_Wall_'+style+('_Window' if window else '_Solid')+'_300x24x320'
            mesh(style+('_Window' if window else '_Solid'),n,[x,y,2])
            text(style+('_WindowLabel' if window else '_SolidLabel'),title+(' / FENSTER' if window else ' / GESCHLOSSEN'),[x+150,y+95,30],19)
            if window:
                for p in ['WindowFrame_140x40x157','WindowGlass_Clear_112x2x145']:mesh(style+'_'+p,'SM_WC01_'+p,[x+150,y,102])
            else:put(style+'_Lamp',FURN+'/Blueprints/BP_WC01_WallLamp',[x+65,y+4,202],kind='Lamp')
    # Separate props and one contextual table/chair arrangement, without assembling a house.
    mesh('Table_Context','SM_WC01_Table_180x100x78',[-1050,2420,2])
    mesh('Chair_Context','SM_WC01_Chair_48x49x101',[-1050,2520,2],0)
    mesh('Table_Single','SM_WC01_Table_180x100x78',[650,2150,2])
    mesh('Chair_Single','SM_WC01_Chair_48x49x101',[1000,2150,2])
    text('FurnitureLabel','TISCH / STUHL - EINZELASSETS',[800,2380,30],23)
    for p,x in [('WindowFrame_140x40x157',650),('WindowGlass_Clear_112x2x145',1000)]:mesh('Single_'+p,'SM_WC01_'+p,[x,2900,12])
    text('InsertLabel','RAHMEN / KLARGLAS - SEPARAT',[800,3100,24],20)
    # Two unscaled instances demonstrate the exact common end interface at X=1000.
    mesh('Snap_A','SM_WC01_Wall_A_Solid_300x24x320',[700,3500,2])
    mesh('Snap_B','SM_WC01_Wall_B_Solid_300x24x320',[1000,3500,2])
    text('SnapLabel','ANSCHLUSSPROBE / 2 x 300 cm',[1000,3620,30],22)
    text('Title','WANDKATALOG 01 / AUSWAHLMUSTER - HAEUSER UNVERAENDERT',[-600,3800,370],29)
    assert tool(AS,'save_assets',asset_paths=[MAP])
    return dict(status='passed',map=MAP,placed=placed,existing_house_actors_modified=0,scope='Independent catalogue only; no house modifications')

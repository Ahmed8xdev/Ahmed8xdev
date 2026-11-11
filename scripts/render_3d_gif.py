#!/usr/bin/env python3
"""Procedurally render a looping 3D technology orbit GIF from actual 3D geometry."""
from __future__ import annotations
import math, random, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FRAMES = 760, 420, 28
SCALE = 1.0
OUT = "assets/technology-orbit.gif"
random.seed(38)
stars = [(random.randrange(W), random.randrange(H), random.choice((1,1,1,2)), random.uniform(.2,.7)) for _ in range(110)]
labels = [("PYTHON", "#ffd572"), ("PHP", "#b2abff"), ("LARAVEL", "#ff8d94"),
          ("MCP", "#86f4eb"), ("IDA PRO", "#ffb17f"), ("AI AGENTS", "#c8aaff")]
font_paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]
font_path = next((x for x in font_paths if os.path.exists(x)), None)
def font(sz):
    return ImageFont.truetype(font_path, sz) if font_path else ImageFont.load_default()
f_big, f_medium, f_small = font(49), font(16), font(13)

def lerp(a,b,t): return a+(b-a)*t
def mix(c1,c2,t):
    return tuple(int(lerp(a,b,t)) for a,b in zip(c1,c2))
def rgb(h):
    h=h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def project(p, angle):
    x,y,z=p
    c,s=math.cos(angle), math.sin(angle)
    x,z=x*c+z*s,-x*s+z*c
    k=math.cos(-.36); t=math.sin(-.36)
    y,z=y*k-z*t,y*t+z*k
    scale=340/(5.8-z)
    return (int(530+x*scale),int(228-y*scale),z)
def rgba(v,a=255): return (*v,a)
def face_normal(v):
    u=[v[1][i]-v[0][i] for i in range(3)]
    w=[v[2][i]-v[0][i] for i in range(3)]
    return (u[1]*w[2]-u[2]*w[1], u[2]*w[0]-u[0]*w[2], u[0]*w[1]-u[1]*w[0])
def add_box(faces,cx,cy,cz,sx,sy,sz,base):
    verts=[(cx+sx*x,cy+sy*y,cz+sz*z) for x in (-1,1) for y in (-1,1) for z in (-1,1)]
    for ids in [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]:
        faces.append(([verts[i] for i in ids],rgb(base)))
def outline(draw,xy,col,width=2): draw.line(xy+[xy[0]],fill=col,width=width,joint="curve")
def render(idx):
    theta=idx*2*math.pi/FRAMES
    bg=Image.new("RGB",(W,H))
    pix=bg.load()
    for y in range(H):
        for x in range(W):
            spread=math.exp(-(((x-530)/270)**2+((y-210)/220)**2))
            pix[x,y]=(int(6+9*spread+6*y/H),int(12+9*spread),int(30+21*spread+4*y/H))
    img=bg.convert("RGBA")
    board=ImageDraw.Draw(img,"RGBA")
    for x,y,r,a in stars:
        brightness=int(110*a+40)
        board.ellipse((x-r,y-r,x+r,y+r),fill=(156,190,255,brightness))
    # The native browser site supplies touch and mouse interaction; the GIF is a visual loop.
    board.rounded_rectangle((29,30,265,58),radius=11,fill=(47,52,108,190),outline=(87,109,170,180),width=1)
    board.text((43,37),"AHMED  /  3D SYSTEMS",font=f_small,fill=(196,239,247,255))
    board.text((33,104),"BUILD",font=f_big,fill=(230,242,255,255))
    board.text((33,158),"BEYOND",font=f_big,fill=(130,240,229,255))
    board.text((34,234),"ENGINEERING  •  INTEGRATIONS",font=f_medium,fill=(191,199,232,255))
    board.text((34,262),"Reverse Engineering | MCP | AI",font=f_small,fill=(131,153,209,255))
    board.text((34,283),"Python | PHP | Laravel",font=f_small,fill=(131,153,209,255))
    glow=Image.new("RGBA",(W,H)); gd=ImageDraw.Draw(glow,"RGBA")
    for radius,a in [(130,22),(98,30),(62,45)]:
        gd.ellipse((530-radius,228-radius,530+radius,228+radius),fill=(91,94,255,a))
    glow=glow.filter(ImageFilter.GaussianBlur(34))
    img=Image.alpha_composite(img,glow)
    geom=Image.new("RGBA",(W,H)); d=ImageDraw.Draw(geom,"RGBA")
    # A real 3D projection of two gimbals, a faceted core and rotating nodes.
    for tilt in (.2,1.25):
        path=[]
        for step in range(130):
            t=step*math.tau/129
            p=(2.1*math.cos(t),.18*math.sin(t+tilt)+.58*math.cos(t)*math.sin(tilt),1.25*math.sin(t))
            q=project(p,theta*.65)
            path.append((q[0],q[1]))
        d.line(path,fill=(81,204,255,175),width=3,joint="curve")
    faces=[]
    add_box(faces,0,0,0,1.1,1.1,1.1,"#5f79fb")
    add_box(faces,0,0,0,.79,.79,.79,"#1f77d9")
    # Polygon faces are depth sorted using actual rotated projected coordinates.
    projected=[]
    for poly,base in faces:
        p=[project(v,theta) for v in poly]
        z=sum(t[2] for t in p)/len(p)
        normal=face_normal(poly)
        illumination=.35+.65*abs(math.cos(theta)*normal[2]-math.sin(theta)*normal[0])
        shade=mix((21,25,62),base,illumination)
        projected.append((z,[(t[0],t[1]) for t in p],shade))
    for _,p,color in sorted(projected,key=lambda x:x[0]):
        d.polygon(p,fill=rgba(color,225))
        outline(d,p,rgba(mix(color,(165,246,255),.65),230),width=2)
    # A monogram constructed with solid projected 3D strokes.
    for a,b in [((-0.61,-0.43,1.12),(0,.65,1.12)),((0,.65,1.12),(.61,-.43,1.12)),
                ((-.38,-.04,1.12),(.38,-.04,1.12))]:
        pa,pb=project(a,theta),project(b,theta)
        d.line((pa[0],pa[1],pb[0],pb[1]),fill=(206,253,255,245),width=9)
    # Spherical node orbits revolve in 3D, never using dashed lines.
    for k,(word,color) in enumerate(labels):
        ang=theta+k*math.tau/len(labels)
        q=project((2.55*math.cos(ang),.65*math.sin(ang*1.7),1.9*math.sin(ang)),theta*.1)
        nx,ny=int(q[0]),int(q[1])
        if not (280<nx<735 and 25<ny<400): continue
        co=rgb(color)
        d.ellipse((nx-8,ny-8,nx+8,ny+8),fill=rgba(co,255),outline=(234,249,255,255),width=2)
        if k%2==0:
            tw=int(d.textbbox((0,0),word,font=f_small)[2])
            bx=max(284,min(745-tw-22,nx-tw/2-10))
            by=min(385,ny+13)
            d.rounded_rectangle((bx,by,bx+tw+20,by+25),radius=9,
                                fill=(18,27,59,235),outline=rgba(co,180),width=1)
            d.text((bx+10,by+5),word,font=f_small,fill=(240,249,255,255))
    img=Image.alpha_composite(img,geom)
    gloss=Image.new("RGBA",(W,H)); gl=ImageDraw.Draw(gloss)
    gl.ellipse((516,214,544,242),fill=(133,253,255,95))
    gloss=gloss.filter(ImageFilter.GaussianBlur(14))
    img=Image.alpha_composite(img,gloss)
    return img.convert("RGB")

frames=[render(i) for i in range(FRAMES)]
os.makedirs(os.path.dirname(OUT),exist_ok=True)
frames[0].save(OUT,save_all=True,append_images=frames[1:],duration=85,loop=0,
               optimize=True,disposal=2)
print(f"Saved animated 3D projection at {OUT}; frames={FRAMES}; size={os.path.getsize(OUT)} bytes")

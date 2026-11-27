#!/usr/bin/env python3
"""Deterministic, print-friendly activity-page generator for BOOK_001.

Uses only the Python standard library. Generated SVGs are vector pages sized
for an 8.5 x 11 inch trim box. Puzzle answer keys are generated from the same
data used to draw each page.
"""
from __future__ import annotations
import argparse, json, math, random, string, xml.sax.saxutils as xu
from collections import deque
from pathlib import Path

PAGE_W, PAGE_H = 850, 1100
ROOT_SEED = 20261127

MAZES = [
 (15,6,"Help the car find the gas station"),(16,6,"Help the cat find its suitcase"),
 (17,6,"Guide the airplane to the airport"),(18,6,"Help the camper reach the campsite"),
 (19,6,"Guide the boat to the harbor"),(20,8,"Find the road to the beach"),
 (21,8,"Help the family reach the picnic area"),(22,8,"Guide the train to the station"),
 (23,8,"Find the route to the mountain cabin"),(24,8,"Help the dog reach the travel bag"),
 (25,8,"Guide the bus through town to the hotel"),(26,10,"Navigate the road-trip junctions to the campsite"),
 (27,10,"Guide the plane through the airport paths"),(28,10,"Find the winding route to the lighthouse"),
 (29,10,"Help the family reach the ferry terminal"),(30,10,"Navigate the mountain road to the lookout"),
]
DOTS = [
 (31,"Car",30,[(8,68),(8,50),(17,50),(24,40),(31,31),(66,31),(74,38),(82,48),(94,51),(94,68),(88,68),(86,78),(80,84),(73,84),(67,78),(65,68),(35,68),(33,78),(27,84),(20,84),(14,78),(12,68)]),
 (32,"Airplane",30,[(50,5),(57,35),(91,49),(91,57),(58,54),(57,82),(70,91),(70,96),(50,91),(30,96),(30,91),(43,82),(42,54),(9,57),(9,49),(43,35)]),
 (33,"Palm tree",30,[(49,94),(53,72),(48,51),(35,38),(18,32),(28,20),(45,27),(39,8),(52,20),(62,5),(61,28),(82,15),(72,35),(91,39),(68,47),(56,56),(60,94)]),
 (34,"Suitcase",30,[(25,25),(38,25),(40,12),(62,12),(64,25),(78,25),(83,32),(83,83),(76,90),(24,90),(17,83),(17,32),(25,25)]),
 (35,"Boat",30,[(8,62),(92,62),(82,80),(68,91),(30,91),(17,80),(8,62),(30,60),(30,18),(50,8),(50,60),(54,60),(72,24),(72,60)]),
 (36,"Sun",30,[(50,5),(57,23),(73,10),(72,30),(94,28),(80,45),(98,56),(78,64),(88,84),(67,78),(58,98),(48,78),(27,90),(32,68),(7,61),(28,49),(12,31),(35,31)]),
 (37,"Compass",50,[(50,3),(59,38),(94,50),(59,59),(50,97),(41,59),(6,50),(41,41)]),
 (38,"Camper van",50,[(8,38),(18,38),(28,20),(70,20),(82,38),(92,38),(92,77),(83,82),(76,94),(62,94),(55,82),(32,82),(25,94),(11,94),(8,82)]),
 (39,"Train",50,[(13,25),(70,25),(70,15),(83,15),(83,25),(90,25),(90,76),(82,83),(72,83),(65,94),(52,94),(46,83),(29,83),(22,94),(10,94),(10,83),(5,76),(5,38),(13,25)]),
 (40,"Mountain",50,[(5,88),(27,40),(38,60),(60,12),(95,88),(5,88)]),
 (41,"Seashell",50,[(50,92),(25,85),(12,65),(15,42),(28,22),(50,8),(72,22),(85,42),(88,65),(75,85),(50,92)]),
 (42,"Road-trip map",50,[(12,18),(38,8),(62,18),(88,8),(88,82),(62,92),(38,82),(12,92),(12,18),(38,8),(38,82),(62,92),(62,18)]),
]
WORD_SEARCHES = [
 (43,"Road Trip Basics",["CAR","PLANE","ROAD","MAP","TRIP","BUS","VAN","GAS"],False),
 (44,"Beach Day",["SUN","SEA","SAND","BEACH","HAT","BAG","TOWEL","WAVE"],False),
 (45,"Train Travel",["TRAIN","RAIL","TRACK","TICKET","SEAT","STOP","CAB","TRIP"],False),
 (46,"Camping Trip",["CAMP","TENT","FIRE","LAKE","TREE","HILL","HIKE","MAP"],False),
 (47,"Boating",["BOAT","SHIP","SAIL","PORT","FISH","DOCK","WAVE","SEA"],False),
 (48,"At the Hotel",["HOTEL","ROOM","KEY","BED","POOL","LOBBY","BELL","BAG"],False),
 (49,"At the Airport",["AIRPORT","PILOT","FLIGHT","TICKET","LUGGAGE","GATE","CABIN","BOARDING","RUNWAY","TRAVEL"],True),
 (50,"On the Highway",["HIGHWAY","MOTORWAY","TRAFFIC","SIGNPOST","MILESTONE","JOURNEY","PETROL","DRIVER","SEATBELT","MAP"],True),
 (51,"Holiday Packing",["BACKPACK","PASSPORT","CAMERA","SUNSCREEN","SANDALS","HOLIDAY","POSTCARD","SOUVENIR","GUIDEBOOK","BEACH"],True),
 (52,"Nature Explorer",["MOUNTAIN","FOREST","RIVER","VALLEY","CAMPING","TRAILER","COMPASS","BINOCULARS","WILDLIFE","NATURE"],True),
 (53,"Railway Journey",["STATION","PLATFORM","RAILWAY","CONDUCTOR","CARRIAGE","TUNNEL","ENGINE","SCHEDULE","ARRIVAL","DEPARTURE"],True),
 (54,"At the Harbor",["FERRY","HARBOR","ANCHOR","SAILBOAT","CAPTAIN","OCEAN","ISLAND","COASTLINE","LIFEBUOY","VOYAGE"],True),
]
GAME_PAGES = [
 (73,"License Plate Alphabet","Find each letter on a license plate. Check it when you spot it.",list("ABCDEFGHIJKLM"),"letters"),
 (74,"License Plate Alphabet","Find each letter on a license plate. Check it when you spot it.",list("NOPQRSTUVWXYZ"),"letters"),
 (75,"I Spy: Road Trip","Look out the window and check each thing you spot.",["CAR","TRUCK","TRAFFIC LIGHT","ROAD SIGN","BRIDGE","TREE","CLOUD","BIRD","BICYCLE","GAS STATION"],"checklist"),
 (76,"I Spy: Places & Travel","Look out for these places and things on your journey.",["AIRPLANE","BUS","DOG","MOUNTAIN","RIVER","CAMPER","TRAIN","BOAT","TUNNEL","HOTEL"],"checklist"),
 (77,"Count the Objects","Count each group carefully. Write the total in the box.",["CARS","ROAD SIGNS","TRUCKS"],"count_a"),
 (78,"Count the Objects","Count each group carefully. Write the total in the box.",["CLOUDS","TREES","BIRDS"],"count_b"),
 (79,"Road Trip Bingo","Spot an item and mark its square. Get four in a row to win!",["CAR","TRUCK","BRIDGE","TREE","BUS","CLOUD","ROAD SIGN","BICYCLE","BIRD","TUNNEL","RIVER","CAMPER","AIRPLANE","GAS STATION","MOTORBIKE","TRAIN"],"bingo"),
 (80,"Road Trip Bingo","Spot an item and mark its square. Get four in a row to win!",["BOAT","FERRY","MOUNTAIN","DOG","HOTEL","CAMPFIRE","MAP","SUITCASE","BEACH","PALM TREE","TRAFFIC LIGHT","PICNIC","TRAIN","AIRPLANE","WATERFALL","TOLL BOOTH"],"bingo"),
]

def esc(v):
    return xu.escape(str(v), {'"':'&quot;'})

def page_svg(title,instruction,body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="8.5in" height="11in" viewBox="0 0 {PAGE_W} {PAGE_H}">
<rect width="{PAGE_W}" height="{PAGE_H}" fill="#fff"/>
<g fill="#000" font-family="Arial, Helvetica, sans-serif">
<text x="425" y="100" text-anchor="middle" font-size="36" font-weight="700">{esc(title)}</text>
<text x="425" y="148" text-anchor="middle" font-size="20">{esc(instruction)}</text></g>
{body}
<text x="425" y="1060" text-anchor="middle" font-family="Arial" font-size="15" fill="#555">ROAD TRIP ACTIVITY BOOK</text>
</svg>'''

def generate_maze(size,seed):
    rng=random.Random(seed)
    walls=[[True,True,True,True] for _ in range(size*size)]
    visited={0}; stack=[0]
    while stack:
        cell=stack[-1]; row,col=divmod(cell,size); options=[]
        for wi,(dr,dc) in enumerate([(-1,0),(0,1),(1,0),(0,-1)]):
            nr,nc=row+dr,col+dc
            if 0<=nr<size and 0<=nc<size:
                nxt=nr*size+nc
                if nxt not in visited: options.append((nxt,wi))
        if not options: stack.pop(); continue
        nxt,wi=rng.choice(options); opposite=(wi+2)%4
        walls[cell][wi]=False; walls[nxt][opposite]=False
        visited.add(nxt); stack.append(nxt)
    walls[0][0]=False; walls[-1][2]=False
    goal=size*size-1; q=deque([0]); prev={0:None}
    while q:
        cell=q.popleft()
        if cell==goal: break
        row,col=divmod(cell,size)
        for wi,(dr,dc) in enumerate([(-1,0),(0,1),(1,0),(0,-1)]):
            nr,nc=row+dr,col+dc
            if 0<=nr<size and 0<=nc<size and not walls[cell][wi]:
                nxt=nr*size+nc
                if nxt not in prev: prev[nxt]=cell; q.append(nxt)
    if goal not in prev: raise ValueError("Maze has no path")
    path=[]; cur=goal
    while cur is not None: path.append(cur); cur=prev[cur]
    return walls,list(reversed(path))

def maze_svg(size,prompt,walls,page):
    box=620; cell=box/size; x0,y0=115,260; lines=[]
    for r in range(size):
        for c in range(size):
            idx=r*size+c; x=x0+c*cell; y=y0+r*cell
            if walls[idx][0] and idx!=0: lines.append(f'<path d="M{x:.2f} {y:.2f}h{cell:.2f}"/>')
            if walls[idx][1]: lines.append(f'<path d="M{x+cell:.2f} {y:.2f}v{cell:.2f}"/>')
            if walls[idx][2] and idx!=size*size-1: lines.append(f'<path d="M{x:.2f} {y+cell:.2f}h{cell:.2f}"/>')
            if walls[idx][3] and c==0: lines.append(f'<path d="M{x:.2f} {y:.2f}v{cell:.2f}"/>')
    body=f'<g fill="none" stroke="#000" stroke-width="5" stroke-linecap="square">{ "".join(lines) }</g><g font-family="Arial" font-size="19" font-weight="700"><text x="{x0}" y="{y0-28}">START</text><text x="{x0+box}" y="{y0+box+42}" text-anchor="end">FINISH</text></g>'
    return page_svg(f"Maze {page-14}",prompt,body)

def polygon_samples(points,count):
    pts=[(float(x),float(y)) for x,y in points]
    if pts[0]!=pts[-1]: pts.append(pts[0])
    lengths=[math.dist(a,b) for a,b in zip(pts,pts[1:])]
    total=sum(lengths); result=[]
    for i in range(count):
        target=total*i/count; acc=0.0
        for j,length in enumerate(lengths):
            if acc+length>=target or j==len(lengths)-1:
                t=0.0 if length==0 else (target-acc)/length
                a,b=pts[j],pts[j+1]
                result.append((a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)); break
            acc+=length
    return result

def dot_svg(name,count,outline):
    points=polygon_samples(outline,count); left,top,width,height=140,250,570,570
    xs=[p[0] for p in points]; ys=[p[1] for p in points]
    minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
    scale=min(width/max(1,maxx-minx),height/max(1,maxy-miny))
    ox=left+(width-(maxx-minx)*scale)/2; oy=top+(height-(maxy-miny)*scale)/2
    mapped=[(ox+(x-minx)*scale,oy+(y-miny)*scale) for x,y in points]
    dots=[]
    for i,(x,y) in enumerate(mapped,1):
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="#fff" stroke="#000" stroke-width="2.2"/>')
        dx=8 if i%2 else -8; anchor="start" if dx>0 else "end"
        dots.append(f'<text x="{x+dx:.1f}" y="{y-7:.1f}" text-anchor="{anchor}" font-family="Arial" font-size="15">{i}</text>')
    return page_svg(f"Connect the Dots: {name}","Connect the dots in order. What will you discover?",''.join(dots)),mapped

def make_word_search(words,diagonal,seed):
    rng=random.Random(seed); n=10; dirs=[(0,1),(1,0)]
    if diagonal: dirs += [(1,1),(1,-1)]
    for _ in range(300):
        grid=[["" for _ in range(n)] for _ in range(n)]; placements=[]; ok=True
        for word in sorted(words,key=lambda w:(-len(w),w)):
            candidates=[]
            for dr,dc in dirs:
                for r in range(n):
                    for c in range(n):
                        er,ec=r+(len(word)-1)*dr,c+(len(word)-1)*dc
                        if not (0<=er<n and 0<=ec<n): continue
                        cells=[(r+i*dr,c+i*dc) for i in range(len(word))]
                        if all(grid[rr][cc] in ("",ch) for (rr,cc),ch in zip(cells,word)):
                            candidates.append((r,c,dr,dc,cells))
            rng.shuffle(candidates)
            if not candidates: ok=False; break
            r,c,dr,dc,cells=candidates[0]
            for (rr,cc),ch in zip(cells,word): grid[rr][cc]=ch
            placements.append({"word":word,"start":[r,c],"end":[r+(len(word)-1)*dr,c+(len(word)-1)*dc],"direction":[dr,dc]})
        if ok:
            for r in range(n):
                for c in range(n):
                    if not grid[r][c]: grid[r][c]=rng.choice(string.ascii_uppercase)
            return grid,placements
    raise RuntimeError("Unable to place all words")

def word_svg(title,words,grid):
    x0,y0,cell=155,235,54; lines=[]; letters=[]
    for i in range(11):
        p=x0+i*cell; lines += [f'<path d="M{p} {y0}v{10*cell}"/>',f'<path d="M{x0} {y0+i*cell}h{10*cell}"/>']
    for r in range(10):
        for c in range(10):
            letters.append(f'<text x="{x0+(c+.5)*cell}" y="{y0+(r+.68)*cell}" text-anchor="middle" font-family="Arial" font-size="27" font-weight="700">{grid[r][c]}</text>')
    listed=[]
    for i,w in enumerate(words):
        col,row=i//5,i%5; x=180+col*280; y=850+row*35
        listed.append(f'<rect x="{x}" y="{y-17}" width="15" height="15" fill="none" stroke="#000" stroke-width="1.7"/><text x="{x+25}" y="{y}" font-family="Arial" font-size="19">{w}</text>')
    body=f'<g fill="none" stroke="#000" stroke-width="2">{"".join(lines)}</g><g fill="#000">{"".join(letters)}{"".join(listed)}</g>'
    return page_svg(f"Word Search: {title}","Find and circle all the hidden words.",body)

def checkbox(x,y,label,font=21):
    return f'<rect x="{x}" y="{y-22}" width="22" height="22" fill="none" stroke="#000" stroke-width="2.5"/><text x="{x+38}" y="{y}" font-family="Arial" font-size="{font}">{esc(label)}</text>'

def game_svg(title,instruction,items,kind):
    out=[]
    if kind=="letters":
        for i,item in enumerate(items):
            col,row=i%4,i//4; x,y=120+col*155,290+row*175
            out += [f'<rect x="{x}" y="{y}" width="115" height="125" rx="10" fill="none" stroke="#000" stroke-width="3"/>',f'<text x="{x+57}" y="{y+78}" text-anchor="middle" font-family="Arial" font-size="55" font-weight="700">{item}</text>',f'<rect x="{x+82}" y="{y+95}" width="20" height="20" fill="none" stroke="#000" stroke-width="2"/>']
    elif kind=="checklist":
        for i,item in enumerate(items):
            col,row=i//5,i%5; out.append(checkbox(145+col*330,300+row*125,item,21))
    elif kind.startswith("count"):
        counts=[4,6,3] if kind=="count_a" else [5,7,4]
        for i,(item,count) in enumerate(zip(items,counts)):
            y=310+i*220; out.append(f'<text x="130" y="{y}" font-family="Arial" font-size="24" font-weight="700">{item}</text>')
            for j in range(count):
                x=150+j*72
                if item == "CARS":
                    out.append(f'<g transform="translate({x},{y+25})"><rect x="0" y="0" width="42" height="20" rx="5" fill="none" stroke="#000" stroke-width="2.5"/><path d="M8 0l7 -10h15l8 10" fill="none" stroke="#000" stroke-width="2.5"/><circle cx="10" cy="22" r="5" fill="#fff" stroke="#000" stroke-width="2"/><circle cx="34" cy="22" r="5" fill="#fff" stroke="#000" stroke-width="2"/></g>')
                elif item == "TRUCKS":
                    out.append(f'<g transform="translate({x},{y+25})"><rect x="0" y="0" width="27" height="23" fill="none" stroke="#000" stroke-width="2.5"/><path d="M27 7h11l9 9v7H27Z" fill="none" stroke="#000" stroke-width="2.5"/><circle cx="10" cy="25" r="5" fill="#fff" stroke="#000" stroke-width="2"/><circle cx="38" cy="25" r="5" fill="#fff" stroke="#000" stroke-width="2"/></g>')
                elif item=="ROAD SIGNS":
                    out.append(f'<g transform="translate({x+8},{y+10})"><path d="M15 0L30 15L15 30L0 15Z" fill="none" stroke="#000" stroke-width="2.5"/><path d="M15 30v22" stroke="#000" stroke-width="3"/></g>')
                elif item=="CLOUDS":
                    out.append(f'<path d="M{x} {y+35}q-8 -18 12 -22q10 -28 30 -8q25 -4 22 20q18 16 -5 24h-48q-20 -2 -11 -14Z" fill="none" stroke="#000" stroke-width="2.5"/>')
                elif item=="TREES":
                    out.append(f'<g transform="translate({x+8},{y+5})"><path d="M15 0L0 27h10L2 42h26l-8 -15h10Z" fill="none" stroke="#000" stroke-width="2.5"/><path d="M15 42v12" stroke="#000" stroke-width="3"/></g>')
                else:
                    out.append(f'<g transform="translate({x+5},{y+10})"><path d="M0 20q18 -24 35 0q-18 18 -35 0Z" fill="none" stroke="#000" stroke-width="2.5"/><path d="M35 20l12 -9v18Z" fill="none" stroke="#000" stroke-width="2.5"/></g>')
            out.append(f'<rect x="690" y="{y-35}" width="75" height="55" fill="none" stroke="#000" stroke-width="2.5"/>')
    elif kind=="bingo":
        x0,y0,cell=95,250,165
        for r in range(4):
            for c in range(4):
                x,y=x0+c*cell,y0+r*cell; label=items[r*4+c]
                out += [f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="none" stroke="#000" stroke-width="2.5"/>',f'<text x="{x+cell/2}" y="{y+cell/2+7}" text-anchor="middle" font-family="Arial" font-size="17" font-weight="700">{esc(label)}</text>']
    return page_svg(title,instruction,''.join(out))

def build(output:Path):
    output.mkdir(parents=True,exist_ok=True); answer=output/"answer_keys"; answer.mkdir(exist_ok=True)
    report={"project":"BOOK_001_ROAD_TRIP","seed":ROOT_SEED,"pages_generated":[],"checks":{}}
    maze_keys={}
    for page,size,prompt in MAZES:
        walls,path=generate_maze(size,ROOT_SEED+page)
        maze_keys[str(page)]={"grid_size":size,"start":[0,0],"finish":[size-1,size-1],"solution_path":[list(divmod(i,size)) for i in path],"solution_steps":len(path)-1}
        dest=output/"mazes"/f"page_{page:02d}_maze.svg"; dest.parent.mkdir(exist_ok=True)
        dest.write_text(maze_svg(size,prompt,walls,page),encoding="utf-8"); report["pages_generated"].append(page)
    (answer/"maze_solutions.json").write_text(json.dumps(maze_keys,indent=2),encoding="utf-8")
    dot_keys={}
    for page,name,count,outline in DOTS:
        svg,points=dot_svg(name,count,outline); dest=output/"dot_to_dot"/f"page_{page:02d}_dot_to_dot.svg"
        dest.parent.mkdir(exist_ok=True); dest.write_text(svg,encoding="utf-8")
        dot_keys[str(page)]={"subject":name,"required_points":count,"points":[[round(x,2),round(y,2)] for x,y in points]}
        report["pages_generated"].append(page)
    (answer/"dot_to_dot_key.json").write_text(json.dumps(dot_keys,indent=2),encoding="utf-8")
    word_keys={}
    for page,title,words,diagonal in WORD_SEARCHES:
        grid,placements=make_word_search(words,diagonal,ROOT_SEED+page)
        dest=output/"word_searches"/f"page_{page:02d}_word_search.svg"; dest.parent.mkdir(exist_ok=True)
        dest.write_text(word_svg(title,words,grid),encoding="utf-8")
        word_keys[str(page)]={"title":title,"grid":grid,"words":placements,"diagonals_allowed":diagonal}
        report["pages_generated"].append(page)
    (answer/"word_search_solutions.json").write_text(json.dumps(word_keys,indent=2),encoding="utf-8")
    game_keys={}
    for page,title,instruction,items,kind in GAME_PAGES:
        dest=output/"travel_games"/f"page_{page:02d}_travel_game.svg"; dest.parent.mkdir(exist_ok=True)
        dest.write_text(game_svg(title,instruction,items,kind),encoding="utf-8")
        if kind.startswith("count"):
            counts=[4,6,3] if kind=="count_a" else [5,7,4]
            game_keys[str(page)]={"type":kind,"answers":dict(zip(items,counts))}
        elif kind=="bingo": game_keys[str(page)]={"type":"bingo","squares":items}
        else: game_keys[str(page)]={"type":kind,"items":items}
        report["pages_generated"].append(page)
    (answer/"travel_game_keys.json").write_text(json.dumps(game_keys,indent=2),encoding="utf-8")
    report["pages_generated"].sort()
    expected=list(range(15,55))+list(range(73,81))
    report["checks"]={
      "all_expected_pages_generated":report["pages_generated"]==expected,
      "maze_count":len(maze_keys),"dot_to_dot_count":len(dot_keys),
      "word_search_count":len(word_keys),"travel_game_count":len(game_keys),
      "all_word_search_words_placed":all(len(v["words"])==len(WORD_SEARCHES[int(k)-43][2]) for k,v in word_keys.items()),
      "all_dot_counts_exact":all(len(v["points"])==v["required_points"] for v in dot_keys.values()),
      "maze_paths_present":all(len(v["solution_path"])>=2 for v in maze_keys.values()),
    }
    report["status"]="GENERATED_NEEDS_VISUAL_REVIEW" if all(report["checks"].values()) else "GENERATION_FAILED"
    (output/"VALIDATION_REPORT.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    if report["status"]!="GENERATED_NEEDS_VISUAL_REVIEW": raise SystemExit("Validation failed")
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",default="generated_activities")
    args=parser.parse_args(); report=build(Path(args.output_dir))
    print(json.dumps({"status":report["status"],"pages":len(report["pages_generated"]),"checks":report["checks"]},indent=2))

if __name__=="__main__": main()

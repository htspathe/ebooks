#!/usr/bin/env python3
"""Deterministic KDP preflight. Exit non-zero when --strict and blocking issues exist."""
import argparse, csv, json, math
from pathlib import Path
from PIL import Image, ImageStat

def audit(project):
    project=Path(project)
    cfg=json.loads((project/"book.json").read_text(encoding="utf-8"))
    rows=list(csv.DictReader((project/"manifest.csv").open(encoding="utf-8-sig",newline="",encoding_errors="replace")))
    expected=int(cfg["artwork_count"])
    results=[]
    problems=[]
    if len(rows)!=expected: problems.append(f"Expected {expected} manifest rows, found {len(rows)}")
    numbers=[int(row["page"]) for row in rows]
    if sorted(numbers)!=list(range(1,expected+1)):
        problems.append("Manifest page numbers not exactly 1.."+str(expected))
    fingerprints=[]
    for row in rows:
        n=int(row["page"])
        path=project/"assets"/"originals"/f"page_{n:02d}.png"
        item={"page":n,"file":str(path),"errors":[],"warnings":[]}
        if not path.is_file():
            item["errors"].append("missing file")
        else:
            try:
                with Image.open(path) as img:
                    img.load()
                    width,height=img.size
                    item["size_px"]=[width,height]
                    # Usable square-inch target, excluding an illustrative 0.5-inch margin.
                    printable_w=float(cfg["trim_width_inches"])-1
                    printable_h=float(cfg["trim_height_inches"])-1
                    ppi=min(width/printable_w,height/printable_h)
                    item["effective_ppi"]=round(ppi,1)
                    if ppi < 300: item["errors"].append(f"Low effective resolution ({ppi:.0f} ppi < 300)")
                    if width>=height: item["warnings"].append("not portrait-oriented")
                    pixels=img.convert("L").resize((32,32))
                    # Basic thumbnail similarity flag, not a certification of uniqueness.
                    fingerprints.append((n,list(pixels.getdata())))
                    if ImageStat.Stat(pixels).mean[0]<155: item["warnings"].append("large dark area; inspect for colorability")
            except Exception as ex: item["errors"].append(f"Invalid image: {ex}")
        # Editorial approval is explicit; the script never auto-approves.
        if row.get("editorial_approved","").strip().lower()!="yes":
            item["errors"].append("editorial approval pending")
        if row.get("count_verified","").strip().lower()!="yes":
            item["errors"].append("counting task not manually checked")
        if row.get("visual_approved","").strip().lower()!="yes":
            item["errors"].append("artwork approval pending")
        results.append(item)
    for i,(na,a) in enumerate(fingerprints):
        for nb,b in fingerprints[i+1:]:
            distance=math.sqrt(sum((x-y)**2 for x,y in zip(a,b))/len(a))
            if distance<12:
                for item in results:
                    if item["page"]==nb: item["warnings"].append(f"Possible similar composition to page {na}")
    blocked=bool(problems or any(x["errors"] for x in results))
    return {"project":str(project),"status":"BLOCKED" if blocked else "TECHNICAL_PREFLIGHT_PASSED_NOT_KDP_APPROVED","problems":problems,"pages":results,"counts":{"expected":expected,"files_found":sum("missing file" not in x["errors"] for x in results),"blocked_pages":sum(bool(x["errors"]) for x in results)}}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("project",type=Path)
    p.add_argument("--out",default="report.json")
    p.add_argument("--strict",action="store_true")
    args=p.parse_args()
    report=audit(args.project)
    Path(args.out).write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print(f'{report["status"]}: {report["counts"]}')
    for page in report["pages"]:
        if page["errors"]: print(f'  Page {page["page"]:02d}: {", ".join(page["errors"])}')
    if report["status"]=="BLOCKED" and args.strict: raise SystemExit(1)

if __name__=="__main__": main()

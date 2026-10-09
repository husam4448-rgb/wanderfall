#!/usr/bin/env python3
"""Phase-independent GitHub CI live reporter; never impersonates ChatGPT activity.

Usage: python tools/sp_live_ci.py STAGE "meaningful milestone description"
Checks issue #35's newer run ID before updating. Every status has UTC timestamp.
"""
from datetime import datetime,timezone
import json,os,re,sys,urllib.request,urllib.error
stage=sys.argv[1] if len(sys.argv)>1 else "UNKNOWN"
detail=sys.argv[2] if len(sys.argv)>2 else "no detail"
repo=os.environ.get("GITHUB_REPOSITORY","husam4448-rgb/wanderfall")
sha=os.environ.get("GITHUB_SHA","UNKNOWN")
branch=os.environ.get("GITHUB_REF_NAME","UNKNOWN")
run_id=int(os.environ.get("GITHUB_RUN_ID","0"))
token=os.environ.get("GH_STATUS_TOKEN","")
phase=os.environ.get("SP_PHASE","PC42")
now=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
run_url=f"https://github.com/{repo}/actions/runs/{run_id}" if run_id else "NOT RUNNING"
terminal=stage in ("FAILED","COMPLETED","HALTED")
owner="NONE — CI finished" if terminal else "GITHUB ACTIONS (NOT ChatGPT)"
state="FAILED" if stage=="FAILED" else "COMPLETED" if stage=="COMPLETED" else "WAITING FOR GITHUB"
body=f"""## Survival Paradise — Independent Development Status

**LAST UPDATE (UTC):** {now}
**STATUS:** {state}
**EXECUTION OWNER:** {owner}
**CURRENT PHASE:** {phase} — male right-facing static rifle reference reconstruction
**CURRENT MILESTONE:** {stage}
**DETAIL:** {detail}
**BRANCH:** \`{branch}\`
**TESTED/CURRENT SOURCE SHA:** \`{sha}\`
**WORKFLOW RUN ID:** {run_id}
**WORKFLOW:** {run_url}
**LAST VISUAL ACCEPTANCE:** None for complete articulated characters. PC41 visually FAILED; {phase} visual review PENDING.
**LATEST VERIFIED APK:** PC33 version code 205, [workflow](https://github.com/{repo}/actions/runs/37918163875), artifact 11610127605; technical PASS, visual FAIL.
**LAST FAILED VISUAL CHECK:** PC41 shoulder/arm/stock contact still unconvincing.
**NEXT:** Visually inspect actual Godot PC42 male-right static pose vs approved source. Refine anatomical segmentation if needed. Do not begin dynamic aiming, female, gait, or APK without static approval.
**RECOVERY:** https://github.com/{repo}/blob/pc42-character-visual-reconstruction/docs/PC42_STATIC_FIRST_POSE.md

**IMPORTANT:** This is independently reported GitHub CI, not an active ChatGPT agent. A stale issue status never proves ChatGPT continues running.
"""
if not token:
    print(f"SP_STATUS_ISSUE_UNAVAILABLE: no GitHub issue token. Inspect {run_url}")
    sys.exit(0)
url=f"https://api.github.com/repos/{repo}/issues/35"
headers={"Authorization":f"Bearer {token}",
         "Accept":"application/vnd.github+json",
         "Content-Type":"application/json",
         "X-GitHub-Api-Version":"2022-11-28",
         "User-Agent":"survival-paradise-ci"}
def request(method,url,data=None):
    req=urllib.request.Request(url,method=method,
       data=json.dumps(data).encode() if data is not None else None,headers=headers)
    with urllib.request.urlopen(req,timeout=15) as res:return json.load(res)
try:
    previous=request("GET",url)
    old=re.search(r"\*\*WORKFLOW RUN ID:\*\* (\d+)",previous.get("body",""))
    if old and run_id and int(old.group(1))>run_id:
        print(f"SP_STATUS_SUPERSEDED: existing run {old.group(1)} newer than {run_id}; skipping dashboard update")
        sys.exit(0)
    request("PATCH",url,{"body":body})
    if stage in ("STARTED","VISUAL_EVIDENCE_READY","FAILED","COMPLETED"):
        request("POST",url+"/comments",{"body":f"**{phase} {stage}** · {now} · [{run_id}]({run_url}) · \`{sha[:12]}\` · {detail}"})
    print(f"SP_STATUS_RECORDED {stage} {now} {run_url}")
except Exception as exc:
    print(f"SP_STATUS_ISSUE_UNAVAILABLE: {type(exc).__name__}: {exc}; workflow logs remain authoritative: {run_url}")

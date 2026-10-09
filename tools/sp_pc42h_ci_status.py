#!/usr/bin/env python3
"""PC42H independent GitHub Actions live-status publisher.

CI can finish while ChatGPT is absent. Owner never claims to be ChatGPT.
A lower GitHub run ID may not overwrite the Issue #35 dashboard of a newer run.
Actions logs/artifacts remain available even when Issues API fails.
"""
from datetime import datetime, timezone
import json, os, re, sys, urllib.error, urllib.request

stage=sys.argv[1] if len(sys.argv)>1 else "UNKNOWN"
detail=sys.argv[2] if len(sys.argv)>2 else "No operation description"
repo=os.getenv("GITHUB_REPOSITORY","husam4448-rgb/wanderfall")
sha=os.getenv("GITHUB_SHA","UNKNOWN")
branch=os.getenv("GITHUB_REF_NAME","UNKNOWN")
run=int(os.getenv("GITHUB_RUN_ID","0"))
token=os.getenv("GH_STATUS_TOKEN","")
now=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
phase=os.getenv("SP_PHASE","PC42H")
url=f"https://github.com/{repo}/actions/runs/{run}"
terminal=stage in ("FAILED","COMPLETED","HALTED")
status="FAILED" if stage=="FAILED" else "COMPLETED" if stage=="COMPLETED" else "WAITING FOR GITHUB"
owner="NONE — workflow complete" if terminal else "GITHUB ACTIONS (not ChatGPT)"
issue_url=f"https://github.com/{repo}/issues/35"
body=f"""# Survival Paradise — Live Development Status

**LAST UPDATE UTC:** {now}
**STATUS:** {status}
**EXECUTION OWNER:** {owner}
**CURRENT DEVELOPMENT PHASE:** {phase} dedicated far-arm source artwork and first rifle small-motion gate
**ACTIVE DEVELOPMENT BRANCH:** \`{branch}\`
**EXACT SOURCE COMMIT:** \`{sha}\`
**CURRENT WORKFLOW RUN ID:** {run}
**CURRENT WORKFLOW URL:** {url}
**CURRENT BUILD STAGE:** {stage}
**LAST COMPLETED OPERATION:** {detail if stage!="FAILED" else "See preceding successful workflow step in GitHub logs"}
**LAST FAILED TEST:** {detail if stage=="FAILED" else "PC42G human visual QA — far-arm flat triangular textile"}
**LATEST VISUAL QA VERDICT:** PENDING independent inspection; all technical CI checks are necessary but NEVER constitute visual acceptance.
**LATEST VERIFIED APK:** PC33 version code 205 (technical pass, visual fail); https://github.com/{repo}/actions/runs/37918163875/artifacts/11610127605
**REMAINING DEFECTS:** Missing visually approved realistic bent support forearm, correct elbow/cuff occlusion; remaining male/female LEFT/RIGHT, rifle/pistol motions, grounded gait and equipment.
**NEXT REQUIRED OPERATION:** Inspect actual clean Godot PC42H screenshots and 32-frame GIF, reject or correct sleeve and wrist visuals. Do not export APK before the art gate passes.
**RECOVERY DOCUMENT:** https://github.com/{repo}/blob/{branch}/docs/PC42G_TWO_ARM_VISUAL_QA.md
**MONITORING NOTE:** A GitHub job reports only its own execution; no automatic ChatGPT development is implied by a running workflow.
"""
if not token:
    print("PC42H_STATUS_WARNING missing GH_STATUS_TOKEN; GitHub workflow logs and artifacts remain authoritative",flush=True)
    sys.exit(0)
headers={
 "Authorization":f"Bearer {token}",
 "Accept":"application/vnd.github+json",
 "Content-Type":"application/json",
 "X-GitHub-Api-Version":"2022-11-28",
 "User-Agent":"survival-paradise-PC42H"}
issue_api=f"https://api.github.com/repos/{repo}/issues/35"
def request(method,url,data=None):
    req=urllib.request.Request(
        url,data=json.dumps(data).encode() if data is not None else None,
        headers=headers,method=method)
    with urllib.request.urlopen(req,timeout=15) as response:
        return json.load(response)
try:
    previous=request("GET",issue_api)
    oldbody=previous.get("body") or ""
    runids=re.findall(r"\*\*(?:CURRENT WORKFLOW RUN ID|WORKFLOW RUN ID):\*\*\s*(\d+)",oldbody)
    if not runids:
        # Hand-written checkpoints sometimes retain only the workflow URL.
        # Never use the last APK's older run as a competing newer run.
        runids=re.findall(r"/actions/runs/(\d+)",oldbody)
    old=max((int(x) for x in runids),default=0)
    if old>run:
        print(f"PC42H_STATUS_SUPERSEDED old={old} current={run} stage={stage}",flush=True)
        sys.exit(0)
    request("PATCH",issue_api,{"body":body})
    if stage in ("STARTED","RUNTIME_TESTED","VISUAL_EVIDENCE_READY","FAILED","COMPLETED"):
        comment=f"**{phase} {stage}** · {now} · [{run}]({url}) · \`{sha[:12]}\` · {detail}. Visual review remains independent from CI. No APK."
        request("POST",issue_api+"/comments",{"body":comment})
    print(f"PC42H_STATUS_RECORDED {stage} {now} {url}",flush=True)
except Exception as exc:
    print(f"PC42H_STATUS_WARNING {type(exc).__name__}: {exc}; evidence remains in {url}",flush=True)

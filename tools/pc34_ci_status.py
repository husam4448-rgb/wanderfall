#!/usr/bin/env python3
"""Last-known GitHub Actions status to issue #35, independent of ChatGPT."""
import json,os,sys,urllib.request,urllib.error
stage=sys.argv[1] if len(sys.argv)>1 else "UNSPECIFIED"
detail=sys.argv[2] if len(sys.argv)>2 else ""
repo=os.getenv("GITHUB_REPOSITORY","husam4448-rgb/wanderfall")
ref=os.getenv("GITHUB_REF_NAME","pc34-weapon-silhouette-feasibility")
sha=os.getenv("GITHUB_SHA","not-yet-known")
run=os.getenv("GITHUB_RUN_ID","not-yet-known")
url=f"https://github.com/{repo}/actions/runs/{run}"
baseline="https://github.com/husam4448-rgb/wanderfall/actions/runs/37918163875/artifacts/11610127605"
token=os.getenv("GH_STATUS_TOKEN","")
state="FAILED" if stage=="FAILED" else "COMPLETED" if stage=="COMPLETED" else "WAITING FOR GITHUB"
body=f"""## Survival Paradise — Independent PC34 Geometry Status

**STATUS:** {state} (GitHub Actions job, NOT continuous ChatGPT execution)
**CURRENT:** {stage} — {detail}
**BRANCH:** \`{ref}\`
**SOURCE SHA:** \`{sha}\`
**WORKFLOW:** {url}
**LATEST VERIFIED APK:** PC33 (technical only, VISUAL FAIL) {baseline}
**CURRENT PC34 APK:** None; full painted-silhouette diagnostic only.
**PREVIOUS VISUAL FAILURE:** PC33 rifle almost vertical near face despite valid stock-line clearance.
**NEXT:** Interpret head/weapon full-alpha collision/IK feasibility. Design multi-state torso/head/shoulder aiming; then actual Godot visual test before any further APK.
**RECOVERY:** https://github.com/husam4448-rgb/wanderfall/blob/pc33-aim-pose-head-clearance/docs/PC33_VISUAL_QA.md

Workflow page indicates whether GitHub still executes. This issue may be stale after ChatGPT stops.
"""
if not token:
    print(f"PC34_STATUS_UNAVAILABLE: missing token; actual workflow {url}")
    sys.exit(0)
req=urllib.request.Request(f"https://api.github.com/repos/{repo}/issues/35",
     data=json.dumps({"body":body}).encode(),method="PATCH",
     headers={"Authorization":f"Bearer {token}","Content-Type":"application/json",
              "Accept":"application/vnd.github+json",
              "X-GitHub-Api-Version":"2022-11-28"})
try:
    with urllib.request.urlopen(req,timeout=15) as response:
        assert response.status==200
    print(f"PC34_STATUS_ISSUE_UPDATED {stage}: {url}")
except Exception as exc:
    print(f"PC34_STATUS_UNAVAILABLE {type(exc).__name__}: {exc}; check {url}")

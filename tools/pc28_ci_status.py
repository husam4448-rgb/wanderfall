#!/usr/bin/env python3
"""Non-fatal GitHub Actions -> Survival Paradise status issue #35.

Workflow stages update independently even if assistant chat terminates.
When GitHub token cannot edit issues, report the restriction to CI logs
without misrepresenting that a dashboard update succeeded.
"""
import os,sys,json,urllib.request,urllib.error
stage=sys.argv[1] if len(sys.argv)>1 else "UNSPECIFIED"
detail=sys.argv[2] if len(sys.argv)>2 else ""
repo=os.getenv("GITHUB_REPOSITORY","husam4448-rgb/wanderfall")
run=os.getenv("GITHUB_RUN_ID","unknown")
sha=os.getenv("GITHUB_SHA","unknown")
ref=os.getenv("GITHUB_REF_NAME","pc28-articulated-knees")
token=os.getenv("GH_STATUS_TOKEN","")
run_url=f"https://github.com/{repo}/actions/runs/{run}"
prev=f"https://github.com/{repo}/actions/runs/37898271147/artifacts/11601057216"
stat="FAILED" if stage=="FAILED" else "COMPLETED" if stage=="COMPLETED" else "WAITING FOR GITHUB"
body=f"""## Survival Paradise — CI-owned live build progress

**STATUS:** {stat}
**CURRENT WORKFLOW STAGE:** {stage}
**STAGE DETAIL:** {detail}
**TESTED SOURCE COMMIT:** \`{sha}\`
**WORKING BRANCH:** \`{ref}\`
**GITHUB RUN:** {run_url}
**LAST VERIFIED BASELINE APK:** {prev}
**PC28 APK:** {"Verified in this workflow; see run artifacts" if stage=="COMPLETED" else "Not verified until all CI checks pass"}
**VISUAL ACCEPTANCE:** Not approved — independent manual review of Godot images required
**REMAINING:** verify real knee articulation/gait; pistol/rifle grip, outfit fidelity, Android device tests
**NEXT:** {"Resume at failed step from Actions logs; preserve PC27 baseline" if stage=="FAILED" else "Inspect new PC28 runtime captures and accept or recalibrate gait" if stage=="COMPLETED" else "Wait for next workflow stage"}

This status is written by **GitHub Actions independently** of ChatGPT.
It describes the actual CI workflow, not an autonomous ongoing assistant.
The action page is authoritative if a stale issue message remains.
"""
if not token:
    print("PC28_STATUS_ISSUE_UNAVAILABLE: no writable GITHUB_TOKEN; consult Actions run",flush=True)
    sys.exit(0)
payload=json.dumps({"body":body}).encode("utf-8")
req=urllib.request.Request(
    f"https://api.github.com/repos/{repo}/issues/35",
    data=payload,method="PATCH",
    headers={"Accept":"application/vnd.github+json",
             "Authorization":f"Bearer {token}",
             "X-GitHub-Api-Version":"2022-11-28","Content-Type":"application/json"})
try:
    with urllib.request.urlopen(req,timeout=15) as response:
        if response.status!=200:
            raise RuntimeError(f"unexpected response {response.status}")
    print(f"PC28_STATUS_ISSUE_UPDATED: {stage}: {run_url}",flush=True)
except (urllib.error.HTTPError,urllib.error.URLError,RuntimeError) as exc:
    print(f"PC28_STATUS_ISSUE_UNAVAILABLE ({type(exc).__name__}): {exc}; consult {run_url}",flush=True)

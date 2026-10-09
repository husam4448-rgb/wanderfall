#!/usr/bin/env python3
"""Phase-independent GitHub Actions status monitor for Survival Paradise.

Each independent GitHub Actions run publishes stage events. An older run may
not overwrite the latest dashboard. Appends concise milestone comments
where permissions permit. Does NOT pretend ChatGPT continues after its turn.
"""
import json,os,sys,datetime,urllib.request,urllib.error,re
repo=os.getenv("GITHUB_REPOSITORY","husam4448-rgb/wanderfall")
run=os.getenv("GITHUB_RUN_ID","0")
ref=os.getenv("GITHUB_REF_NAME","unknown")
sha=os.getenv("GITHUB_SHA","unknown")
stage=sys.argv[1] if len(sys.argv)>1 else "UNKNOWN"
detail=sys.argv[2] if len(sys.argv)>2 else ""
token=os.getenv("GH_STATUS_TOKEN","")
status="FAILED" if stage=="FAILED" else "COMPLETED" if stage=="COMPLETED" else "WAITING FOR GITHUB"
owner="NONE (workflow finished)" if stage in ("FAILED","COMPLETED") else "GITHUB ACTIONS"
url=f"https://github.com/{repo}/actions/runs/{run}"
now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
title="Survival Paradise — Independent Development Status"
body=f"""## {title}

**EXECUTION OWNER:** {owner}; this field describes CI only, never assistant work
**STATUS:** {status}
**CURRENT PHASE:** {ref}
**WORKFLOW RUN ID:** {run}
**WORKFLOW:** {url}
**SOURCE COMMIT:** \`{sha}\`
**CURRENT STAGE:** {stage}
**LAST VERIFIED STAGE DETAIL:** {detail}
**LAST UPDATE (UTC):** {now}
**CURRENT VISUAL ACCEPTANCE:** PENDING / NOT APPROVED. Source: {ref}. Actual Godot renders require human review.
**CURRENT PHASE APK:** NOT EXPORTED (visual validation gate)\n**LAST VERIFIED VISUAL GATE:** PC37 partial improvement, NOT production-approved, workflow https://github.com/{repo}/actions/runs/37928890541
**LATEST SIGNED APK:** PC33 code 205 (technically verified, visually rejected),
https://github.com/{repo}/actions/runs/37918163875/artifacts/11610127605
**REMAINING:** rifle full-silhouette/upper-body pose, pistol contacts, phase-based locomotion, equipped integration, Android on-device QA.
**NEXT:** inspect male/female source-art contacts and 100 time-sequenced Godot captures. A passing CI is not visual acceptance.

This message is an independently written **last-known GitHub job status**.
If ChatGPT has stopped, no assistant development is necessarily active.
Use the workflow page above to determine actual execution state.
"""
def req(url,method,payload=None):
    data=None if payload is None else json.dumps(payload).encode()
    q=urllib.request.Request(url,data=data,method=method,headers={
       "Accept":"application/vnd.github+json",
       "Authorization":f"Bearer {token}",
       "Content-Type":"application/json","X-GitHub-Api-Version":"2022-11-28"})
    with urllib.request.urlopen(q,timeout=18) as r:
        return json.loads(r.read().decode())
if not token:
    print(f"SP_MONITOR_NO_TOKEN: {stage} {url}",flush=True)
    sys.exit(0)
issue=f"https://api.github.com/repos/{repo}/issues/35"
try:
    existing=req(issue,"GET")
    match=re.search(r"\*\*WORKFLOW RUN ID:\*\*\s*(\d+)",existing.get("body",""))
    prior=int(match.group(1)) if match else -1
    # Earlier workflow stages are non-authoritative once a newer job starts.
    if int(run)<prior:
        print(f"SP_MONITOR_OLDER_RUN: {run} vs {prior}; ignored",flush=True)
        sys.exit(0)
    req(issue,"PATCH",{"body":body})
    print(f"SP_MONITOR_UPDATED {stage} {url}",flush=True)
    if stage in ("STARTED","SOURCE_READY","GODOT_PASS","VISUAL_EVIDENCE_READY","COMPLETED","FAILED"):
        try:
            req(issue+"/comments","POST",{"body":f"**{now}** | [Run {run}]({url}) | **{stage}** — {detail} | \`{sha[:12]}\`"})
            print("SP_MONITOR_COMMENT_RECORDED",flush=True)
        except Exception as err:
            print("SP_MONITOR_COMMENT_UNAVAILABLE "+repr(err),flush=True)
except Exception as err:
    print(f"SP_MONITOR_UNAVAILABLE {type(err).__name__}: {err} — consult {url}",flush=True)

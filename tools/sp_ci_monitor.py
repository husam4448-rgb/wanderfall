#!/usr/bin/env python3
"""Independent Survival Paradise GitHub status watchdog and CI reporter.

Only updates a bounded dashboard section in existing Issue #35; preserves
human-authored visual QA and recovery instructions. CI != ChatGPT activity.
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request
import urllib.error
import time

REPO=os.getenv("GITHUB_REPOSITORY","husam4448-rgb/wanderfall")
TOKEN=os.getenv("GH_STATUS_TOKEN",os.getenv("GITHUB_TOKEN",""))
API="https://api.github.com/repos/"+REPO
OPEN="<!-- SP_MONITOR_BEGIN -->"
CLOSE="<!-- SP_MONITOR_END -->"
WATCH_NAME="Survival Paradise Live Status Watchdog"

def call(method,route,data=None):
    if not TOKEN: raise RuntimeError("Missing GitHub status token")
    headers={"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json",
             "X-GitHub-Api-Version":"2022-11-28","User-Agent":"survival-paradise-monitor"}
    if data is not None:headers["Content-Type"]="application/json"
    req=urllib.request.Request(API+route,headers=headers,method=method,
      data=json.dumps(data).encode() if data is not None else None)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=20) as response:
                raw=response.read()
                return json.loads(raw) if raw else {}, dict(response.headers)
        except (urllib.error.HTTPError,urllib.error.URLError) as exc:
            code=getattr(exc,"code",None)
            if attempt==2 or code not in (None,409,429,500,502,503):
                raise
            time.sleep(attempt+1)

def is_dev(r):
    name=r.get("name") or ""
    branch=r.get("head_branch") or ""
    return name!=WATCH_NAME and (bool(re.match(r"pc[0-9]+[a-z]?-",branch,re.I)) or bool(re.match(r"PC[0-9]+",name,re.I)))

def choose(runs):
    valid=sorted((r for r in runs if is_dev(r)),key=lambda r:r["id"],reverse=True)
    active=[r for r in valid if r.get("status") in ("queued","in_progress","waiting","pending","requested")]
    return active[0] if active else (valid[0] if valid else None)

def latest_comment_lease(now):
    items,headers=call("GET","/issues/35/comments?per_page=100&page=1")
    last=re.search(r'[?&]page=([0-9]+)>;\s*rel="last"',headers.get("Link",""))
    if last and int(last.group(1))>1:
        items,_=call("GET","/issues/35/comments?per_page=100&page="+last.group(1))
    for entry in reversed(items):
        m=re.search(r"<!-- SP_ASSISTANT_LEASE expires=([0-9TZ:\-]+) -->",entry.get("body") or "")
        if not m: continue
        expiry=dt.datetime.fromisoformat(m.group(1).replace("Z","+00:00"))
        return ("RECENT SELF-REPORT; expires "+m.group(1)+" (not independently verified)" if expiry>now
                else "STALE/UNKNOWN — last reported ChatGPT lease expired "+m.group(1))
    return "UNKNOWN — no verified current ChatGPT heartbeat"

def last_manual(body,label,fallback):
    other=re.sub(re.escape(OPEN)+r".*?"+re.escape(CLOSE),"",body,flags=re.S)
    m=re.search(r"\*\*"+re.escape(label)+r":\*\*\s*([^\n]+)",other,re.I)
    return m.group(1).strip() if m else fallback

def actual_stage(run):
    if not run:return "No development run", "NONE"
    if run.get("status")=="completed":
        return "Completed: "+str(run.get("conclusion") or "unknown"),"NONE"
    try:
        result,_=call("GET","/actions/runs/"+str(run["id"])+"/jobs?per_page=100")
        for job in reversed(result.get("jobs",[])):
            for step in reversed(job.get("steps",[])):
                if step.get("status")=="in_progress":
                    return step["name"],"GITHUB ACTIONS"
        for job in reversed(result.get("jobs",[])):
            if job.get("status")=="in_progress":
                return "Running job: "+job.get("name","unknown"),"GITHUB ACTIONS"
    except Exception as exc:
        print("SP_MONITOR_STAGE_WARNING "+str(exc),flush=True)
    return "Queued / awaiting stage details","GITHUB ACTIONS"

def dashboard(original, run, stage, owner, lease, when):
    v=last_manual(original,"LATEST VISUAL QA VERDICT","NOT APPROVED; see recovery")
    fail=last_manual(original,"LAST FAILED TEST","See visual QA document")
    source=last_manual(original,"EXACT LAST TECHNICALLY TESTED SOURCE","PC42H 1cfaab1c8198dbfc8a14f73f2a92dad953a8ba78")
    next_step=last_manual(original,"NEXT REQUIRED ACTION","PC42J true painted elbow/cuff, test in Godot")
    if run:
        rid=run["id"]
        url=run.get("html_url") or "https://github.com/"+REPO+"/actions/runs/"+str(rid)
        branch=run.get("head_branch") or "UNKNOWN"
        sha=run.get("head_sha") or "UNKNOWN"
        status=("WAITING FOR GITHUB" if owner=="GITHUB ACTIONS" else
                ("FAILED" if run.get("conclusion")=="failure" else "HALTED — no active CI"))
    else:
        rid=0;url="NONE";branch="NONE";sha="NONE";status="HALTED — no development workflow"
    stamp=when.strftime("%Y-%m-%d %H:%M:%S UTC")
    return "\n".join([
        OPEN,"## Independent GitHub production monitor",
        "**LAST VERIFIED UPDATE UTC:** "+stamp,
        "**STATUS:** "+status,
        "**EXECUTION OWNER:** "+owner,
        "**CHATGPT SESSION:** "+lease,
        "**CURRENT DEVELOPMENT PHASE:** "+branch,
        "**ACTIVE/RECENT BRANCH:** "+branch,
        "**EXACT CANDIDATE COMMIT:** "+sha+" (not automatically accepted)",
        "**LAST HUMAN-REPORTED TESTED SOURCE:** "+source,
        "**CURRENT WORKFLOW RUN ID:** "+str(rid),
        "**CURRENT WORKFLOW URL:** "+url,
        "**CURRENT BUILD STAGE:** "+stage,
        "**LAST COMPLETED OPERATION:** "+(stage if owner=="NONE" else "see workflow steps"),
        "**LAST FAILED TEST:** "+fail,
        "**LATEST VISUAL QA VERDICT (HUMAN):** "+v,
        "**LATEST SIGNED APK:** PC33 code 205 (technical PASS, visual FAIL), no newer approved APK",
        "**REMAINING DEFECTS:** elbow/cuff art, female/LEFT, weapon poses, gait and equipment",
        "**NEXT REQUIRED ACTION:** "+next_step,
        "**ACCURACY:** An active GitHub workflow is independent of ChatGPT; a stale chat response is NOT evidence that development continues. This monitor is scheduled; GitHub may delay runs.",
        CLOSE])

def reconcile():
    issue,_=call("GET","/issues/35")
    runs,_=call("GET","/actions/runs?per_page=100")
    run=choose(runs.get("workflow_runs",[]))
    stage,owner=actual_stage(run)
    now=dt.datetime.now(dt.timezone.utc)
    lease=latest_comment_lease(now)
    old=issue.get("body") or ""
    box=dashboard(old,run,stage,owner,lease,now)
    rx=re.compile(re.escape(OPEN)+r".*?"+re.escape(CLOSE),re.S)
    new=rx.sub(lambda _:box,old,count=1) if rx.search(old) else old.rstrip()+"\n\n"+box+"\n"
    if new!=old:
        call("PATCH","/issues/35",{"body":new})
    print("SP_MONITOR_LIVE_CHECK "+json.dumps({"run":run["id"] if run else None,
        "branch":run.get("head_branch") if run else None,
        "ci_owner":owner,"stage":stage,"assistant":lease,"utc":now.isoformat()}),flush=True)

def event(stage,detail):
    now=dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00","Z")
    run=int(os.getenv("GITHUB_RUN_ID","0"))
    phase=os.getenv("SP_PHASE","PC42J")
    branch=os.getenv("GITHUB_REF_NAME","unknown")
    sha=os.getenv("GITHUB_SHA","unknown")
    body=("<!-- SP_CI_EVENT run="+str(run)+" -->\n"+phase+" | "+stage+
          " | "+now+" | "+branch+" | commit "+sha+"\n\n"+detail+
          "\n\nGitHub Actions event, NOT proof of an active ChatGPT session."+
          "\nhttps://github.com/"+REPO+"/actions/runs/"+str(run))
    call("POST","/issues/35/comments",{"body":body})
    print("SP_MONITOR_EVENT_RECORDED "+stage+" "+now,flush=True)
    reconcile()

def selftest():
    tests=[
        {"id":5,"name":"PC42J test","head_branch":"pc42j-art","status":"completed"},
        {"id":3,"name":"PC42J test","head_branch":"pc42j-art","status":"in_progress"},
        {"id":8,"name":WATCH_NAME,"head_branch":"main","status":"in_progress"}]
    assert choose(tests)["id"]==3
    source="Human QA FAIL\n"+OPEN+"\nold section\n"+CLOSE+"\nProtected"
    new=re.compile(re.escape(OPEN)+r".*?"+re.escape(CLOSE),re.S).sub(OPEN+"fresh"+CLOSE,source)
    assert "Human QA FAIL" in new and "Protected" in new
    assert not is_dev(tests[2])
    print("SP_MONITOR_SELF_TEST_PASS monitor-exclusion older-active-run human-QA-preservation")

if __name__=="__main__":
    mode=sys.argv[1] if len(sys.argv)>1 else "check"
    try:
        if mode=="check":reconcile()
        elif mode=="emit":event(sys.argv[2],sys.argv[3])
        elif mode=="self-test":selftest()
        else:raise ValueError("usage: monitor.py check|emit STAGE DETAIL|self-test")
    except Exception as exc:
        print("SP_MONITOR_FAILED "+type(exc).__name__+" "+str(exc),flush=True)
        sys.exit(1)

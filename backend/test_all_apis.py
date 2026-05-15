"""Full API Test - All endpoints"""
import asyncio, httpx, sys
from datetime import datetime

BASE = "http://localhost:8000/api/v1"
PASS, FAIL = [], []
ACCOUNTS = {
    "student": {"username": "student_test", "password": "student"},
    "tutor": {"username": "tutor_test", "password": "tutor"},
    "coordinator": {"username": "coordinator_test", "password": "coordinator"},
}

async def login(c, role):
    r = await c.post(f"{BASE}/auth/login", data=ACCOUNTS[role])
    return r.json().get("access_token") if r.status_code == 200 else None

def h(t): return {"Authorization": f"Bearer {t}"} if t else {}

async def t(c, method, url, tok=None, name=None, body=None, ok=(200,)):
    label = name or f"{method.upper()} {url.replace(BASE,'')}"
    try:
        kw = {"headers": h(tok), "timeout": 15}
        if body and method in ("post","put","patch","delete"): kw["json"] = body
        r = await getattr(c, method)(url, **kw)
        if r.status_code in ok:
            PASS.append(label)
        else:
            try: detail = str(r.json().get("detail",""))[:120]
            except: detail = r.text[:120]
            FAIL.append(f"{label} → {r.status_code}: {detail}")
        return r
    except Exception as e:
        FAIL.append(f"{label} → ERR: {str(e)[:80]}")
        return None

async def main():
    print("="*60)
    print(f"🧪 FULL API TEST - {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)
    async with httpx.AsyncClient() as c:
        print("\n📌 Auth")
        tokens = {}
        for role in ACCOUNTS:
            tokens[role] = await login(c, role)
            print(f"  {'✅' if tokens[role] else '❌'} {role}")
        st, tt, ct = tokens["student"], tokens["tutor"], tokens["coordinator"]
        if not all([st, tt, ct]): print("❌ Login failed"); return

        await t(c,"get","http://localhost:8000/",name="GET /")
        await t(c,"get","http://localhost:8000/health",name="GET /health")
        await t(c,"get",f"{BASE}/auth/me",st,"GET /auth/me student")
        await t(c,"get",f"{BASE}/auth/me",tt,"GET /auth/me tutor")
        await t(c,"get",f"{BASE}/auth/me",ct,"GET /auth/me coord")
        await t(c,"post",f"{BASE}/auth/refresh-token",st,"POST /auth/refresh-token",ok=(200,401,422))

        print("\n📌 Users")
        await t(c,"get",f"{BASE}/users/",ct,"GET /users/ (coord)")
        await t(c,"get",f"{BASE}/users/profile",st,"GET /users/profile student")
        await t(c,"get",f"{BASE}/users/profile",tt,"GET /users/profile tutor")
        await t(c,"put",f"{BASE}/users/profile",st,"PUT /users/profile",{"full_name":"Test Student"},ok=(200,422))
        await t(c,"get",f"{BASE}/users/search?query=test",st,"GET /users/search")
        await t(c,"get",f"{BASE}/users/stats/dashboard",st,"GET /stats/dashboard student")
        await t(c,"get",f"{BASE}/users/stats/dashboard",tt,"GET /stats/dashboard tutor")
        await t(c,"get",f"{BASE}/users/stats/coordinator",ct,"GET /stats/coordinator")
        r = await c.get(f"{BASE}/users/",headers=h(ct))
        uid = r.json()[0].get("user_id") if r.status_code==200 and r.json() else None
        if uid: await t(c,"get",f"{BASE}/users/{uid}",ct,f"GET /users/{uid}")

        print("\n📌 Sessions")
        r = await t(c,"get",f"{BASE}/sessions/",st,"GET /sessions/")
        sid = None
        if r and r.status_code==200:
            sl = r.json()
            if isinstance(sl,list) and sl: sid = sl[0].get("session_id")
        await t(c,"get",f"{BASE}/sessions/my-sessions",st,"GET /my-sessions student")
        await t(c,"get",f"{BASE}/sessions/my-sessions",tt,"GET /my-sessions tutor")
        await t(c,"get",f"{BASE}/sessions/my-sessions/dashboard",st,"GET /dashboard student")
        await t(c,"get",f"{BASE}/sessions/my-sessions/dashboard",tt,"GET /dashboard tutor")
        await t(c,"get",f"{BASE}/sessions/feedback/bulk?session_ids=1,2",st,"GET /feedback/bulk")
        await t(c,"get",f"{BASE}/sessions/materials/bulk?session_ids=1,2",st,"GET /materials/bulk")
        if sid:
            await t(c,"get",f"{BASE}/sessions/{sid}",st,f"GET /sessions/{sid}")
            await t(c,"get",f"{BASE}/sessions/{sid}/participants",st,"GET /participants")
            await t(c,"get",f"{BASE}/sessions/{sid}/materials",st,"GET /materials")
            await t(c,"get",f"{BASE}/sessions/{sid}/feedback",st,"GET /feedback")
            await t(c,"put",f"{BASE}/sessions/{sid}",tt,f"PUT /sessions/{sid}",{"title":"Test"},ok=(200,403,404,422))
            await t(c,"post",f"{BASE}/sessions/{sid}/join",st,"POST /join",ok=(200,400,409,422))
            await t(c,"post",f"{BASE}/sessions/{sid}/complete",tt,"POST /complete",ok=(200,400,403))
            await t(c,"post",f"{BASE}/sessions/{sid}/publish",tt,"POST /publish",ok=(200,400,403))
            await t(c,"post",f"{BASE}/sessions/{sid}/attendance",tt,"POST /attendance",{"attendees":[]},ok=(200,400,403,422))
            await t(c,"post",f"{BASE}/sessions/{sid}/feedback",st,"POST /session-feedback",{"rating":5,"comment":"Great"},ok=(200,400,409,422))
            await t(c,"post",f"{BASE}/sessions/{sid}/materials",tt,"POST /materials",{"title":"Test","url":"http://t.com"},ok=(200,400,403,422))
        await t(c,"post",f"{BASE}/sessions/",tt,"POST /sessions create",
                {"subject_id":1,"title":"Test","start_time":"2026-12-01T10:00:00","end_time":"2026-12-01T11:00:00"},ok=(200,201,400,403,422))
        await t(c,"get",f"{BASE}/sessions/subject/1/feedbacks",st,"GET /subject/1/feedbacks",ok=(200,404))

        print("\n📌 Tutors")
        r = await t(c,"get",f"{BASE}/tutors/",st,"GET /tutors/")
        tid = None
        if r and r.status_code==200:
            tl = r.json()
            if isinstance(tl,list) and tl: tid = tl[0].get("tutor_id")
        await t(c,"get",f"{BASE}/tutors/me",tt,"GET /tutors/me")
        await t(c,"get",f"{BASE}/tutors/sessions",tt,"GET /tutors/sessions")
        await t(c,"get",f"{BASE}/tutors/my-registrations",tt,"GET /my-registrations")
        await t(c,"get",f"{BASE}/tutors/available-courses",st,"GET /available-courses")
        await t(c,"get",f"{BASE}/tutors/courses/enrolled-students",tt,"GET /enrolled-students")
        await t(c,"post",f"{BASE}/tutors/check-schedule-conflicts",tt,"POST /check-conflicts",
                {"start_time":"2026-12-01T10:00:00","end_time":"2026-12-01T11:00:00"},ok=(200,422))
        if tid:
            await t(c,"get",f"{BASE}/tutors/{tid}",st,f"GET /tutors/{tid}")
            await t(c,"get",f"{BASE}/tutors/{tid}/availability",st,f"GET /availability/{tid}")
            await t(c,"get",f"{BASE}/tutors/{tid}/reviews",st,f"GET /reviews/{tid}")

        print("\n📌 Students")
        await t(c,"get",f"{BASE}/students/",st,"GET /students/")
        r_me = await t(c,"get",f"{BASE}/students/me",st,"GET /students/me")
        stid = r_me.json().get("student_id") if r_me and r_me.status_code==200 else None
        if stid:
            await t(c,"get",f"{BASE}/students/{stid}",st,f"GET /students/{stid}")
            await t(c,"get",f"{BASE}/students/{stid}/enrolled-courses",st,"GET /enrolled-courses")
            await t(c,"post",f"{BASE}/students/{stid}/request-tutor",st,"POST /request-tutor",{"subject":"Math"},ok=(200,400,422))
        await t(c,"get",f"{BASE}/students/by-user/1",st,"GET /by-user/1",ok=(200,404))

        print("\n📌 Courses")
        await t(c,"get",f"{BASE}/courses/subjects",st,"GET /subjects")
        await t(c,"get",f"{BASE}/courses/subjects/1",st,"GET /subjects/1",ok=(200,404))
        await t(c,"get",f"{BASE}/courses/my-courses",st,"GET /my-courses student")
        await t(c,"get",f"{BASE}/courses/my-courses",tt,"GET /my-courses tutor")
        await t(c,"get",f"{BASE}/courses/courses/CS101",st,"GET /courses/CS101",ok=(200,404))

        print("\n📌 Coordinator")
        await t(c,"get",f"{BASE}/coordinator/tutor-registrations",ct,"GET /coord/registrations")
        await t(c,"get",f"{BASE}/coordinator/sessions/pending",ct,"GET /coord/pending")
        await t(c,"get",f"{BASE}/coordinator/tutors",ct,"GET /coord/tutors")
        await t(c,"post",f"{BASE}/coordinator/tutors/update-all-ratings",ct,"POST /update-all-ratings")
        if tid:
            await t(c,"get",f"{BASE}/coordinator/tutors/{tid}/courses",ct,f"GET /coord/{tid}/courses")

        print("\n📌 Study Groups")
        r = await t(c,"get",f"{BASE}/study-groups/",st,"GET /study-groups/")
        gid = None
        if r and r.status_code==200:
            gl = r.json()
            if isinstance(gl,list) and gl: gid = gl[0].get("group_id")
        await t(c,"post",f"{BASE}/study-groups/",st,"POST /study-groups create",
                {"name":"TestGrp","subject_id":1,"description":"test"},ok=(200,201,400,422))
        if gid:
            await t(c,"get",f"{BASE}/study-groups/{gid}",st,f"GET /study-groups/{gid}")
            await t(c,"get",f"{BASE}/study-groups/{gid}/messages",st,"GET /group/messages")
            await t(c,"get",f"{BASE}/study-groups/{gid}/materials",st,"GET /group/materials")
            await t(c,"post",f"{BASE}/study-groups/{gid}/join",st,"POST /group/join",ok=(200,400,409))
            await t(c,"post",f"{BASE}/study-groups/{gid}/messages",st,"POST /group/message",{"content":"Hello"},ok=(200,201,400,422))
            await t(c,"post",f"{BASE}/study-groups/{gid}/activities",st,"POST /group/activity",
                    {"activity_type":"message","description":"test"},ok=(200,201,400,422))

        print("\n📌 Forum")
        await t(c,"get",f"{BASE}/forum/",st,"GET /forum/")
        await t(c,"get",f"{BASE}/forum/posts",st,"GET /forum/posts")
        await t(c,"post",f"{BASE}/forum/posts",st,"POST /forum/post",
                {"title":"Test","content":"Hello","forum_type":"general"},ok=(200,201,400,422))

        print("\n📌 Notifications")
        await t(c,"get",f"{BASE}/notifications/",st,"GET /notifications/")
        await t(c,"get",f"{BASE}/notifications/unread-count",st,"GET /unread-count")
        await t(c,"put",f"{BASE}/notifications/mark-all-read",st,"PUT /mark-all-read")
        await t(c,"delete",f"{BASE}/notifications/delete-read",st,"DELETE /delete-read")

        print("\n📌 Progress")
        if stid:
            await t(c,"get",f"{BASE}/progress/students/{stid}/progress",st,"GET /student-progress",ok=(200,404))
        await t(c,"get",f"{BASE}/progress/courses/1/study-progress",st,"GET /course-progress",ok=(200,404))

        print("\n📌 Reports")
        await t(c,"get",f"{BASE}/reports/statistics",ct,"GET /reports/statistics")
        await t(c,"get",f"{BASE}/reports/courses",ct,"GET /reports/courses")
        if stid: await t(c,"get",f"{BASE}/reports/student/{stid}",ct,f"GET /reports/student/{stid}",ok=(200,404))
        if tid: await t(c,"get",f"{BASE}/reports/tutor/{tid}",ct,f"GET /reports/tutor/{tid}",ok=(200,404))

        print("\n📌 Schedule Preferences")
        await t(c,"get",f"{BASE}/schedule-preferences/my-preferences",st,"GET /my-preferences")
        await t(c,"get",f"{BASE}/schedule-preferences/statistics",tt,"GET /prefs/statistics")
        await t(c,"post",f"{BASE}/schedule-preferences/",st,"POST /schedule-pref",
                {"subject_id":1,"preferred_day":"monday","start_time":"08:00","end_time":"10:00"},ok=(200,201,400,409,422))

        print("\n📌 Scheduling")
        if tid:
            await t(c,"get",f"{BASE}/scheduling/availability/{tid}",tt,f"GET /scheduling/avail/{tid}")
            await t(c,"post",f"{BASE}/scheduling/availability/{tid}",tt,"POST /scheduling/avail",
                    {"day_of_week":"monday","start_time":"08:00","end_time":"17:00"},ok=(200,201,400,422))
        await t(c,"post",f"{BASE}/scheduling/find-slots",st,"POST /find-slots",
                {"tutor_id":1,"date":"2026-12-01"},ok=(200,400,422))
        await t(c,"post",f"{BASE}/scheduling/sessions",tt,"POST /scheduling/session",
                {"subject_id":1,"start_time":"2026-12-01T10:00:00","end_time":"2026-12-01T11:00:00"},ok=(200,201,400,422))

        print("\n📌 Admin")
        await t(c,"get",f"{BASE}/admin/stats",ct,"GET /admin/stats",ok=(200,403))
        await t(c,"get",f"{BASE}/admin/users",ct,"GET /admin/users",ok=(200,403))

        print("\n📌 WebSocket")
        await t(c,"get",f"{BASE}/ws/stats",st,"GET /ws/stats",ok=(200,403,404))
        await t(c,"get",f"{BASE}/ws/status/1",st,"GET /ws/status/1",ok=(200,404))

    print("\n"+"="*60)
    print(f"📊 RESULTS: ✅ {len(PASS)} PASS | ❌ {len(FAIL)} FAIL")
    print("="*60)
    if FAIL:
        print("\n❌ FAILURES:")
        for f in FAIL: print(f"  • {f}")
    print(f"\n✅ PASSED ({len(PASS)}):")
    for p in PASS: print(f"  • {p}")

if __name__=="__main__":
    asyncio.run(main())

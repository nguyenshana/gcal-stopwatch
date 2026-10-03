#!/usr/bin/env python3
"""Calendar Stopwatch - tiny local server (standard library only)."""
import json, os, time, secrets, subprocess, threading, webbrowser
import urllib.parse as up, urllib.request as ur, urllib.error
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

D = os.path.dirname(os.path.abspath(__file__))
PORT = 8765
URL = f"http://127.0.0.1:{PORT}/"
REDIR = URL + "oauth/callback"
SCOPE = ("https://www.googleapis.com/auth/calendar.events "
         "https://www.googleapis.com/auth/calendar.calendarlist.readonly")
STATE = set()

def load():
    try: return json.load(open(os.path.join(D, "data.json")))
    except Exception: return {}
def save(d): json.dump(d, open(os.path.join(D, "data.json"), "w"), indent=1)
def creds():
    try:
        c = json.load(open(os.path.join(D, "credentials.json")))
        return c.get("installed") or c.get("web")
    except Exception: return None
def post(url, data):
    return json.load(ur.urlopen(ur.Request(url, up.urlencode(data).encode())))

def token():
    d = load(); t = d["tokens"]
    if time.time() > t["expires_at"] - 60:
        c = creds()
        n = post(c["token_uri"], dict(client_id=c["client_id"], client_secret=c["client_secret"],
                 refresh_token=t["refresh_token"], grant_type="refresh_token"))
        t["access_token"] = n["access_token"]; t["expires_at"] = time.time() + n["expires_in"]
        d["tokens"] = t; save(d)
    return t["access_token"]

def g(method, path, body=None):
    req = ur.Request("https://www.googleapis.com/calendar/v3" + path, method=method,
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": "Bearer " + token(), "Content-Type": "application/json"})
    return json.load(ur.urlopen(req))

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def out(self, obj, code=200, ctype="application/json"):
        b = obj if isinstance(obj, bytes) else json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def go(self, loc):
        self.send_response(302); self.send_header("Location", loc); self.end_headers()
    def fail(self, e):
        msg = e.read().decode() if isinstance(e, urllib.error.HTTPError) else str(e)
        self.out(dict(error=msg), 500)

    def do_GET(self):
        u = up.urlparse(self.path); q = up.parse_qs(u.query)
        try:
            if u.path == "/":
                return self.out(open(os.path.join(D, "index.html"), "rb").read(), 200, "text/html; charset=utf-8")
            if u.path == "/api/state":
                d = load()
                return self.out(dict(configured=bool(creds()), signedIn=bool(d.get("tokens")),
                                     selected=d.get("selected", []), timer=d.get("timer")))
            if u.path == "/api/login":
                c = creds(); st = secrets.token_urlsafe(8); STATE.add(st)
                return self.go(c["auth_uri"] + "?" + up.urlencode(dict(client_id=c["client_id"],
                    redirect_uri=REDIR, response_type="code", scope=SCOPE,
                    access_type="offline", prompt="consent", state=st)))
            if u.path == "/oauth/callback":
                if q.get("state", [""])[0] not in STATE or "code" not in q:
                    return self.out(b"Login failed. Close this tab and try again.", 400, "text/plain")
                c = creds()
                n = post(c["token_uri"], dict(code=q["code"][0], client_id=c["client_id"],
                    client_secret=c["client_secret"], redirect_uri=REDIR, grant_type="authorization_code"))
                d = load()
                d["tokens"] = dict(access_token=n["access_token"], refresh_token=n["refresh_token"],
                                   expires_at=time.time() + n["expires_in"])
                save(d); return self.go("/")
            if u.path == "/api/calendars":
                items = g("GET", "/users/me/calendarList?minAccessRole=writer")["items"]
                return self.out([dict(id=i["id"], name=i.get("summaryOverride") or i["summary"],
                    color=i.get("backgroundColor", "#888"), primary=i.get("primary", False)) for i in items])
            self.out(b"Not found", 404, "text/plain")
        except Exception as e: self.fail(e)

    def do_POST(self):
        try:
            b = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            d = load()
            if self.path == "/api/selection": d["selected"] = b["ids"]; save(d); return self.out({})
            if self.path == "/api/timer": d["timer"] = b or None; save(d); return self.out({})
            if self.path == "/api/logout": d.pop("tokens", None); save(d); return self.out({})
            if self.path == "/api/events":
                ev = dict(summary=b["summary"], description=b.get("description", ""),
                          start=dict(dateTime=b["start"], timeZone=b["tz"]),
                          end=dict(dateTime=b["end"], timeZone=b["tz"]))
                r = g("POST", "/calendars/" + up.quote(b["calendarId"], safe="") + "/events", ev)
                return self.out(dict(link=r.get("htmlLink")))
            self.out(b"Not found", 404, "text/plain")
        except Exception as e: self.fail(e)

def open_window():
    try:
        for app in ("Google Chrome", "Microsoft Edge", "Brave Browser"):
            if os.path.exists(f"/Applications/{app}.app"):
                subprocess.Popen(["open", "-na", app, "--args", f"--app={URL}", "--window-size=1080,720"])
                return
    except Exception: pass
    webbrowser.open(URL)

if __name__ == "__main__":
    try: srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    except OSError:
        open_window(); raise SystemExit("Already running - opened the window.")
    threading.Timer(0.6, open_window).start()
    print("Calendar Stopwatch running. Close this Terminal window (or press Ctrl+C) to quit.")
    try: srv.serve_forever()
    except KeyboardInterrupt: pass

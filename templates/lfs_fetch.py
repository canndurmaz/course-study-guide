import json, subprocess, sys, urllib.request, hashlib, os
repo, outdir, files = sys.argv[1], sys.argv[2], sys.argv[3:]
auth = json.loads(subprocess.check_output(["ssh","-o","BatchMode=yes","git@github.com","git-lfs-authenticate",repo,"download"]))
objs = {}
for f in files:
    lines = dict(l.split(" ",1) for l in open(f).read().strip().splitlines())
    objs[lines["oid"].split(":")[1]] = (f, int(lines["size"]))
body = json.dumps({"operation":"download","transfers":["basic"],"objects":[{"oid":o,"size":s} for o,(f,s) in objs.items()]}).encode()
h = {"Accept":"application/vnd.git-lfs+json","Content-Type":"application/vnd.git-lfs+json", **auth["header"]}
resp = json.load(urllib.request.urlopen(urllib.request.Request(auth["href"]+"/objects/batch", body, h)))
for o in resp["objects"]:
    f, s = objs[o["oid"]]
    d = o["actions"]["download"]
    data = urllib.request.urlopen(urllib.request.Request(d["href"], headers=d.get("header",{}))).read()
    assert hashlib.sha256(data).hexdigest() == o["oid"]
    open(os.path.join(outdir, os.path.basename(f)), "wb").write(data); print("ok", f, len(data))

#!/usr/bin/env python3
import argparse,json,os,sys,urllib.request,urllib.error
from pathlib import Path
from urllib.parse import urlparse

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise urllib.error.HTTPError(req.full_url,code,'Redirect blocked',headers,fp)

def main():
    a=argparse.ArgumentParser();a.add_argument('request');a.add_argument('--out',required=True);x=a.parse_args()
    url=os.environ.get('HERMES_BRIDGE_URL','');token=os.environ.get('HERMES_BRIDGE_TOKEN','').strip()
    if urlparse(url).scheme!='https' or not token:raise SystemExit('Se requiere URL HTTPS y token en entorno; no pegar secretos en chat.')
    p=json.loads(Path(x.request).read_text())
    if p.get('mode')!='draft_only':raise SystemExit('Solo draft_only')
    req=urllib.request.Request(url,data=json.dumps(p).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+token},method='POST')
    try:
        with urllib.request.build_opener(NoRedirect()).open(req,timeout=420) as r:raw=r.read(1048577)
        if len(raw)>1048576:raise ValueError('oversized_response')
        data=json.loads(raw)
    except urllib.error.HTTPError as e:raise SystemExit('HTTP '+str(e.code)+'; revisar runbook. No reintentar a ciegas.')
    except (OSError,ValueError):raise SystemExit('Conexión, timeout o JSON inválido; revisar ejecución antes de reintentar.')
    dest=Path(x.out);dest.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:json.dump(data,f,ensure_ascii=False,indent=2)
    print('Respuesta guardada; revisar evidencia y decisión humana:',dest)
if __name__=='__main__':main()

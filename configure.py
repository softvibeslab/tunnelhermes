#!/usr/bin/env python3
"""Genera configuración local; NO instala servicios, perfiles, DNS ni firewall."""
import argparse,json,secrets,shutil,socket,os
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--state',required=True);p.add_argument('--profile',required=True);p.add_argument('--workspace',required=True);p.add_argument('--port',type=int,default=8797);p.add_argument('--host',default='127.0.0.1');a=p.parse_args()
if a.profile=='default':raise SystemExit('Se requiere perfil dedicado ya creado por el administrador.')
hermes=shutil.which('hermes')
if not hermes:raise SystemExit('Instalar Hermes desde documentación oficial y configurar proveedor antes de continuar.')
if not 1024<=a.port<=65535:raise SystemExit('Puerto inválido')
with socket.socket() as s:s.bind((a.host,a.port))
state=Path(a.state).expanduser().resolve();state.mkdir(mode=0o700,parents=True,exist_ok=True)
if state.stat().st_mode & 0o077:raise SystemExit('Directorio state debe tener permisos 0700')
workspace=Path(a.workspace).expanduser().resolve()
if not workspace.is_dir():raise SystemExit('Workspace no existe')
for name in ['token','config.json']:
 if (state/name).exists():raise SystemExit('No se sobrescribe configuración existente')
fd=os.open(state/'token',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as f:f.write(secrets.token_urlsafe(48)+'\n')
c={'host':a.host,'port':a.port,'profile':a.profile,'hermes_bin':hermes,'workspace':str(workspace),'token_file':str(state/'token'),'scratch':str(state/'scratch'),'timeout':360,'policy_reviewed':False,'projects':['piloto-interno'],'repositories':{'piloto-interno':[]}}
fd=os.open(state/'config.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as f:json.dump(c,f,indent=2)
print('Configuración creada en',state,'; secreto nuevo NO mostrado. Revisar política y permitir inicio conscientemente.')

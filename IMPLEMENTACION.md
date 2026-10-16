# Implementación al clonar en un VPS con Hermes

Este archivo es el procedimiento. Al clonar el repositorio en una máquina donde Hermes ya está instalado, seguir los pasos en orden, una vez por VPS.

Cada destino genera su propio perfil, su propio token, su propio dominio y su propio directorio de estado. Repetir el procedimiento completo en el segundo Hermes. No copiar `config.json` ni el archivo `token` de una máquina a la otra.

Esta réplica no sustituye el bridge de origen descrito en `documentacion-origen.md`. No reutilizar su dominio, su token ni su unidad systemd.

El kit no instala el servicio, no crea el perfil, no toca el firewall y no publica DNS. Esos pasos quedan en manos de quien administra el VPS, después de revisar la configuración.

## Qué queda en marcha

Cursor envía una historia de usuario a `POST /v1/enrich-user-story`. El proxy HTTPS del VPS la entrega al bridge en un puerto privado. El bridge llama a `hermes chat` con un perfil dedicado y devuelve un borrador JSON. `evidence_verified` queda en `false` hasta que una persona compruebe las fuentes.

## Requisitos en el VPS

- Linux y Python 3.11 o superior.
- `hermes` en el `PATH` del usuario que va a ejecutar el bridge, con proveedor de modelo ya configurado.
- Usuario de servicio sin privilegios. No ejecutar el bridge como root.
- Perfil Hermes dedicado, distinto de `default`. El kit no lo crea.
- Proxy que ya escuche en 443 (Traefik, Coolify u otro). No instalar un segundo proxy si el 80 y el 443 están ocupados.
- Un subdominio nuevo, con registro A hacia la IP pública de este VPS. El valor del registro es solo la IP, sin `https://` y sin puerto.
- Un directorio de workspace que ya exista. Puede estar vacío. Los repositorios de negocio, si se montan, van en solo lectura.

Documentación de Hermes: [docs](https://hermes-agent.nousresearch.com/docs/) y [llms.txt](https://hermes-agent.nousresearch.com/docs/llms.txt).

## 1. Clonar y comprobar el paquete

```bash
git clone https://github.com/softvibeslab/tunnelhermes.git
cd tunnelhermes
python3 verify_package.py
python3 -m unittest discover -s tests -v
```

`verify_package.py` tiene que imprimir `OK`. Los tests usan un runner local y no llaman al modelo.

## 2. Comprobar el CLI de este Hermes

```bash
hermes --help
hermes chat --help
hermes profile --help
python3 --version
ss -lntp
```

El bridge invoca, sin shell:

```text
hermes --profile PERFIL chat --query-file ARCHIVO -Q --source cursor-bridge --run-budget PRESUPUESTO --max-turns 40
```

Si `hermes chat --help` en este VPS no muestra `--query-file`, `-Q`, `--source`, `--run-budget` o `--max-turns`, detenerse. No editar `bridge.py` para forzar el arranque.

Anotar qué proceso ocupa el puerto previsto. El ejemplo usa `8797`. Si está ocupado, elegir otro entre 1024 y 65535. En el origen estos puertos de loopback ya estaban tomados: `3000`, `3100`, `3101`, `4317`, `4318`, `12345`. No asumir que aquí están libres.

## 3. Perfil dedicado y workspace

Crear el perfil con las herramientas oficiales de Hermes, por ejemplo revisando `hermes profile create --help`. Nombre de ejemplo: `cursor-bridge`.

No usar `default`. No clonar secretos ni memoria de otro perfil. No heredar el entorno de un administrador con credenciales de escritura.

```bash
mkdir -p "$HOME/workspace"
```

El nombre `cursor-bridge` puede repetirse en otro VPS. En el mismo host, el segundo puente necesita otro perfil (`cursor-bridge-b`), otro puerto y otro directorio de estado.

## 4. Generar estado y token

Ejecutar como el usuario de servicio, no como root:

```bash
python3 configure.py \
  --state "$HOME/hermes-cursor-state" \
  --profile cursor-bridge \
  --workspace "$HOME/workspace" \
  --port 8797
```

Eso crea `config.json` y `token` con permisos `0600`. El token no se imprime. Si el comando dice que no sobrescribe, el estado ya existe: revisar ese directorio en lugar de borrar el token a ciegas.

`configure.py` prueba que el puerto se puede reservar y luego lo suelta. Volver a mirar `ss -lntp` antes de arrancar el bridge.

Si el proxy corre en Docker y no puede llegar a `127.0.0.1` del host, repetir `configure.py` en un directorio de estado nuevo con `--host` igual a la IP privada real del gateway de esa red Docker. Esa IP se comprueba en el host (`ip route`, red del proxy). No usar `10.0.1.1` salvo que sea el gateway de este VPS. No usar `0.0.0.0`.

## 5. Revisar la política antes de arrancar

Editar `$HOME/hermes-cursor-state/config.json`.

- `projects`: nombres que este puente acepta. El ejemplo deja `piloto-interno`.
- `repositories`: mapa de proyecto a lista de repos exactos. Vacía significa que el cliente no puede pedir repos. Un nombre que no esté en la lista se rechaza con `422`.
- `timeout`: entre 60 y 3600 segundos. El ejemplo es 360.
- `hermes_bin`: ruta absoluta que escribió `configure.py`. Tiene que ser ejecutable por el usuario de servicio.
- `workspace`: directorio real.

El bridge no arranca mientras `policy_reviewed` sea `false`. Pasarlo a `true` solo después de revisar proyectos, repos y permisos del usuario. Ese cambio confirma la revisión. No aísla las herramientas de Hermes.

Cuentas y montajes antes de ese cambio:

- El usuario de servicio no lee datos de otros clientes.
- Credenciales de repositorio en solo lectura.
- Fuentes de negocio montadas en solo lectura.
- El directorio del perfil Hermes sí necesita escritura, porque ahí viven sesiones y transcripts.

## 6. Probar el bridge a mano

```bash
python3 bridge.py --config "$HOME/hermes-cursor-state/config.json"
```

En otra sesión, en el mismo host:

```bash
curl -sS http://127.0.0.1:8797/health
```

La respuesta esperada es `{"status":"ok"}`. Ese 200 no prueba el modelo ni los repos.

Dejar esta prueba en primer plano solo para el diagnóstico. El servicio permanente va en el paso 8.

## 7. Proxy HTTPS

Crear el registro A del subdominio nuevo hacia la IP pública de este VPS. Comprobar que resuelve aquí y no hacia otro Hermes.

Copiar `deploy/traefik.yaml.example` al sitio de configuración dinámica del proxy que ya existe. Sustituir:

- `REPLACE_DOMAIN` por el subdominio de este VPS.
- `REPLACE_CERT_RESOLVER` por el resolver ACME de ese proxy.
- `REPLACE_PRIVATE_BACKEND` por `127.0.0.1` si el proxy está en el host, o por la IP privada usada en `--host` si el proxy está en Docker.

No publicar el archivo mientras todavía contenga `REPLACE`. No abrir el puerto del bridge en la interfaz pública. El firewall, si existe, solo permite el puerto del bridge desde la red del proxy.

El ejemplo de Traefik espera la respuesta hasta 390 segundos. El cliente espera 420 y el bridge 360. Un balanceador intermedio tiene que tolerar al menos ese presupuesto.

Recargar solo la configuración del proxy. No reiniciar un proxy compartido si el cambio es añadir una ruta.

## 8. Servicio systemd

Copiar `deploy/hermes-cursor.service.example` a una unidad con nombre propio, por ejemplo `hermes-cursor.service`. Sustituir cada `REPLACE` por el usuario de servicio, su grupo, la ruta del clon y la ruta del estado.

`ReadWritePaths` cubre el estado y el home del perfil Hermes. `ReadOnlyPaths` cubre los repos de negocio. `TMPDIR` apunta a `scratch` dentro del estado.

```bash
systemd-analyze verify hermes-cursor.service
```

Con autorización de quien administra el host:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now hermes-cursor.service
sudo systemctl status hermes-cursor.service
```

Parar antes el `bridge.py` manual del paso 6, para no dejar dos procesos en el mismo puerto.

## 9. Aceptación en este VPS

Comprobar en este orden:

1. `GET http://127.0.0.1:PUERTO/health` desde el host.
2. El mismo health desde el contenedor del proxy, si el proxy corre en Docker.
3. `GET https://SUBDOMINIO/health` desde fuera.
4. `POST` sin token: HTTP 401.
5. `POST` con token y `"operation":"no-existe"`: HTTP 422. Esa prueba no ejecuta Hermes.
6. `POST` con `examples/request.json`, token válido y `project` igual a uno de `config.json`.

El token se lee del archivo. No pegarlo en el chat, en el historial del shell ni en git.

```bash
TOKEN=$(cat "$HOME/hermes-cursor-state/token")
curl -sS -o /dev/null -w '%{http_code}\n' \
  -H 'Content-Type: application/json' \
  -d '{"operation":"no-existe"}' \
  http://127.0.0.1:8797/v1/enrich-user-story
```

Sin `Authorization`, el código es 401.

Confirmar desde otra red que `http://IP_PUBLICA:8797/health` no responde. El backend queda detrás del proxy.

## 10. Conectar Cursor

En el equipo donde corre Cursor, no en el VPS, exportar en el entorno del proceso:

- `HERMES_BRIDGE_URL`: URL HTTPS completa, por ejemplo `https://SUBDOMINIO/v1/enrich-user-story`.
- `HERMES_BRIDGE_TOKEN`: el contenido del archivo `token`, sin la palabra `Bearer`.

No enviar a Cursor el PAT de Azure DevOps. Son credenciales distintas.

Desde una copia del kit en ese equipo:

```bash
python3 client.py examples/request.json --out output/draft-001.json
```

El cliente exige HTTPS, rechaza redirecciones y no sobrescribe el archivo de salida. Una respuesta 200 es un borrador. Revisar `sources_used` fuera del bridge antes de tratarlo como evidencia.

La regla de ejemplo para el IDE está en `.cursor/rules/hermes-bridge.mdc`. Copiarla solo al proyecto autorizado.

## Segundo Hermes

Repetir del paso 1 al 10 en el otro VPS.

| Pieza | Primer VPS | Segundo VPS |
|---|---|---|
| Clon | Su propia copia | Su propia copia |
| Perfil | `cursor-bridge` | Otro perfil si comparten host; el mismo nombre vale en otro host |
| Puerto | El que esté libre, ejemplo `8797` | Otro puerto si comparten host |
| Estado y token | `$HOME/hermes-cursor-state` | Otro directorio y otro token |
| Dominio | Subdominio A | Subdominio B |
| Cursor | Una URL por sesión | Cambiar `HERMES_BRIDGE_URL` y el token para hablar con el otro |

## Si algo falla

| Código | Qué revisar |
|---|---|
| 401 | URL, token viejo, comillas, espacios o la palabra `Bearer` duplicada |
| 422 | `operation`, `mode=draft_only`, `project` y repos tienen que coincidir con `config.json` |
| 429 | Ya hay una ejecución. Esperar a que termine. No reenviar a ciegas |
| 502 | El CLI o el modelo falló, o la salida no es un objeto JSON |
| 503 | Servicio, bind o permisos del archivo `token`. No abrir `0.0.0.0` |
| 504 | El presupuesto se agotó. Comprobar si la ejecución sigue viva antes de repetir |

Detalle operativo: `wiki/04-despliegue.md`, `wiki/05-seguridad.md`, `wiki/06-operacion.md`.

## Rollback de esta réplica

Quitar solo la ruta de este bridge en el proxy, parar su unidad systemd y sustituir el token. Dejar el proxy compartido en marcha. No detener servicios ajenos a esta unidad.

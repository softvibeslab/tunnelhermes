# Hermes ↔ Cursor: documentación técnica y plan de consolidación

Fecha de verificación: 2026-10-15 UTC.
Alcance: conexión de Cursor con Hermes remoto en el VPS para enriquecimiento de historias de usuario. Este documento describe la implementación inspeccionada, sus límites y el plan recomendado. No autoriza cambios de infraestructura ni escrituras en Azure DevOps.

## 1. Resumen y distinción técnica

La conexión existente no es un túnel SSH, una VPN ni una sesión remota de Cursor. Es un bridge HTTP autenticado publicado mediante reverse proxy HTTPS. Cursor invoca una operación acotada; el bridge ejecuta Hermes en el VPS y devuelve su respuesta. No hay sincronización automática del workspace local de Cursor con los repositorios del VPS.

Endpoint:
https://hermes-harness.iamobilityappsinc.com/v1/enrich-user-story

El bridge es una integración propia; no debe confundirse con una API pública nativa de Hermes ni con un servidor MCP. La arquitectura pertenece a Hermes/VPS y no depende del DNS de una aplicación de cliente.

## 2. Arquitectura

Cursor / regla del proyecto / cliente Python
  → HTTPS 443 + Authorization: Bearer
  → hermes-harness.iamobilityappsinc.com
  → Traefik / Coolify: terminación TLS y enrutamiento
  → HTTP privado 10.0.1.1:8797
  → servicio hermes-harness-bridge.service
  → proceso Hermes CLI
  → contexto autorizado: repositorios, skills y herramientas disponibles
  → JSON o fallback textual encapsulado en JSON
  → Cursor: revisión humana del borrador

DNS observado: 161.97.147.176. Este valor documenta la resolución observada; el cliente debe usar el dominio HTTPS, no la IP.

La conexión Traefik→bridge es HTTP en una red privada del host, no TLS de extremo a extremo. La existencia de herramientas o memoria no demuestra que se hayan consultado en una petición concreta: la respuesta debe aportar evidencia.

## 3. Estado verificado

| Control | Evidencia observada |
|---|---|
| Servicio systemd | active / running |
| DNS | dominio resuelve a 161.97.147.176 |
| HTTPS y health | GET /health devuelve 200 y {"status":"ok"}; cliente verificó TLS con su confianza predeterminada |
| Autenticación negativa | POST sin token devuelve 401 |
| Autenticación del token del servidor | POST con token y operación inválida devuelve 422; no ejecuta Hermes |
| Backend | escucha en 10.0.1.1:8797 |
| Firewall | UFW activo; permite 10.0.1.0/24 hacia 10.0.1.1:8797 |
| Archivo del token | permisos 0600 |
| Servicios protegidos | 3000, 3100, 3101, 4317, 4318 y 12345 escuchan en 127.0.0.1 |
| Puertos del proxy | 80 y 443 escuchan en 0.0.0.0 |

No se ejecutó una HU real en esta revisión ni se probó el equipo de Cursor. El 422 confirma la autenticación del token almacenado en el servidor, no que el token configurado en Cursor coincida. El health confirma el bridge, no la disponibilidad del modelo ni del acceso a repositorios.

La revisión fue de solo lectura; no se reiniciaron servicios ni se cambiaron puertos, firewall, DNS o configuración.

## 4. Componentes y rutas

- Implementación: /opt/hermes-harness/hermes_harness_bridge_stdlib.py
- Plantilla de instrucciones referenciada por el código: /opt/hermes-harness/enrich_user_story.md
- Unidad: /etc/systemd/system/hermes-harness-bridge.service
- Ruta Traefik: /data/coolify/proxy/dynamic/hermes-harness.yaml
- Secreto: /etc/hermes-harness/token. No incluir su contenido en documentación, Git, chat o logs.
- Cliente inspeccionado: /root/filehub/storage/telegramhub/hermes-harness-mvp/cursor-harness/enrich_hu.py
- Paquete MVP documentado en la skill: /root/filehub/storage/telegramhub/hermes-harness-mvp/. La integridad completa del paquete no se auditó en esta revisión.

## 5. Proceso de una solicitud

1. Cursor prepara una HU con identificador, objetivo, contexto de negocio, repositorios candidatos y rama explícita.
2. El cliente lee URL y token de su entorno; envía JSON mediante POST.
3. Traefik termina TLS y enruta al backend privado. /health se usa para comprobar disponibilidad del bridge.
4. El bridge valida ruta, Bearer, Content-Length, JSON, objeto raíz y operación.
5. Registra metadatos como request_id, proyecto y longitudes; no registra el body completo desde ese punto del código.
6. Inserta el JSON recibido en una plantilla y crea un archivo temporal de prompt que intenta eliminar en finally.
7. Ejecuta Hermes CLI mediante una lista de argumentos, sin interpolación de shell. El perfil predeterminado es default; el código permite seleccionar otro con configuración del servicio.
8. Hermes consulta fuentes según permisos, instrucciones y herramientas efectivamente disponibles. Debe declarar fuentes no disponibles y evitar inferir hechos sin evidencia.
9. El bridge intenta parsear stdout como JSON. Si falla, devuelve HTTP 200 con status draft y el texto en markdown_summary y enriched_user_story.
10. Cursor presenta alcance, preguntas, criterios y riesgos al responsable humano. La aceptación del borrador no implica aprobación para escribir en Azure DevOps.

Invocación construida por el código:
hermes [--profile PERFIL] chat --query-file ARCHIVO -Q --source hermes-harness --run-budget PRESUPUESTO --max-turns 80 --skills hermes-harness-bridge,requirements-traceability-assessment

Es una transcripción de la implementación inspeccionada, no una prueba de ejecución funcional en esta revisión. Antes de desplegar una versión distinta se debe contrastar con hermes chat --help y la documentación oficial.

## 6. Contrato y configuración de Cursor

Configuración del cliente existente:
- HERMES_BRIDGE_URL: URL completa del endpoint.
- HERMES_BRIDGE_TOKEN: secreto Bearer, inyectado por mecanismo seguro.

No se requiere X-Api-Key. No hay HMAC obligatorio en esta implementación. No agregar Bearer al valor de la variable: el cliente agrega ese prefijo.

Ejemplo de solicitud propuesto, sin datos confidenciales:

```json
{
  "operation": "enrich_user_story",
  "request_id": "cursor-hu-demo-001",
  "client": "cursor",
  "project": "piloto-interno",
  "stage": "enriquecimiento",
  "mode": "draft_only",
  "story": {
    "title": "Consultar el estado de un pedido",
    "description": "Como usuario autorizado quiero consultar el estado de mi pedido para conocer su avance."
  },
  "repo_candidates": [],
  "business_context": "Piloto sin información de clientes. Seleccionar repositorio y rama antes de solicitar análisis de código.",
  "constraints": [
    "No escribir en Azure DevOps ni modificar repositorios.",
    "Separar hechos verificados, propuestas y pendientes.",
    "Solicitar la rama y las fuentes si faltan; no inventar evidencia."
  ]
}
```

Cuando se usen repositorios reales, acordar primero la forma exacta de repo_candidates y branch con el esquema del MVP; el backend actual no impone un esquema completo.

Uso del cliente, después de copiarlo al proyecto y provisionar el secreto sin exponerlo:
python3 enrich_hu.py request.json --out output/enriched.json

El comando requiere Python 3 y usa biblioteca estándar. Cursor debe tener una instrucción explícita para ejecutar el cliente y leer el resultado; desplegar el bridge por sí solo no integra automáticamente el IDE. El token no debe formar parte de una regla de Cursor ni del repositorio.

Contrato objetivo recomendado:
- request_id y versión del contrato.
- status normalizado y modo efectivo.
- HU enriquecida, alcance y exclusiones.
- questions_by_role y pending_decisions.
- acceptance_criteria y qa_traceability.
- technical_impact, riesgos y confidence.
- sources_used con repositorio, rama, commit y archivo/línea cuando corresponda.
- markdown_summary.

Actualmente esos campos NO están garantizados para toda respuesta. El bridge acepta cualquier JSON parseable de Hermes; el esquema objetivo debe implementarse y validarse antes de automatizar consumidores estrictos.

## 7. Seguridad y límites actuales

Controles observados:
- HTTPS público con redirección desde HTTP configurada en Traefik.
- Backend en interfaz privada y regla UFW por subred.
- Bearer para POST; /health público sin información de negocio.
- Tamaño máximo predeterminado: 262144 bytes.
- Token guardado en archivo con permisos 0600.
- Puertos internos de otros servicios permanecen en loopback.

Límites y recomendaciones:
- draft_only es una intención de entrega, NO un sandbox de solo lectura. El código solo transforma write_requires_approval a draft_only; no restringe por sí mismo las herramientas del proceso.
- Usar un perfil dedicado, sin credenciales de escritura y con herramientas mínimas. Requiere autorización previa si implica crear o cambiar perfiles.
- No exponer Gateway, MCP, memorias, observabilidad ni endpoints de ejecución arbitraria.
- El PAT de Azure DevOps y el Bearer del bridge son credenciales diferentes. El PAT del VPS no debe enviarse a Cursor ni incluido en la HU.
- La validación reciente del PAT confirmó acceso al catálogo mobileApps; no acredita acceso a todos los proyectos, a Boards ni a todas las ramas.
- No usar payload o reglas del cliente como controles de autorización. Definir una allowlist de proyectos, repositorios y operaciones en servidor.
- Implementar comparación constante del token, rotación y revocación. El código actual usa comparación directa de strings.
- El servidor puede devolver stderr parcial en errores: sanearlo antes de enviarlo para evitar exposición accidental de secretos.
- No hay validación completa del esquema, cuota ni límite explícito de procesos concurrentes en el código inspeccionado.
- Capturar TimeoutExpired y devolver un error estable; actualmente no existe manejo explícito de ese timeout en run_hermes.
- El cliente espera 180 s; el backend permite 360 s por defecto. Alinear cliente, proxy y ejecución o migrar a jobs asíncronos.
- Revisar retención y permisos de temporales, transcripts y logs de Hermes: el logging reducido del bridge no garantiza ausencia de datos en otros componentes.
- Proteger contra prompt injection mediante aislamiento y permisos efectivos, no únicamente instrucciones al modelo.

## 8. Plan de creación reproducible y consolidación

No recrear el despliegue actual sin necesidad: ya existe y responde. Las fases siguientes sirven para reproducirlo en otro entorno y completar su operación segura.

| Fase | Trabajo | Responsable propuesto | Criterio de salida |
|---|---|---|---|
| 0. Alcance | Acordar proyecto, fuentes autorizadas, perfil, restricciones y owner | Negocio + Arquitectura + Seguridad | Alcance y permisos aprobados |
| 1. Inventario | Revisar listeners, proxy, red Docker y firewall | DevOps | Puerto interno disponible sin afectar servicios |
| 2. DNS/TLS | A record del subdominio al VPS; reutilizar Traefik existente | DNS owner + DevOps | DNS correcto y HTTPS validado |
| 3. Bridge | Servicio supervisado, token protegido, bind privado y ruta del proxy | Backend + DevOps | Health interno y público; 401 sin token |
| 4. Aislamiento | Perfil dedicado, credenciales mínimas y allowlists | Seguridad + owner Hermes | Pruebas negativas de escritura y acceso cruzado |
| 5. Contrato | Validar request/response, errores, límites y timeouts | Backend + QA | Tests de contrato y errores ejecutados |
| 6. Cursor | Cliente, secret manager, regla de invocación y salida local | Líder técnico | HU enviada desde el equipo real y respuesta leída |
| 7. Fuentes | Repositorio y rama explícitos; comprobar frescura y citas | Owner del repositorio | Evidencia trazable a commit y archivos |
| 8. Piloto | Revisar borradores, riesgos, QA y utilidad | PO + QA + Negocio | Aceptación o devolución explícita documentada |
| 9. Operación | Métricas, alertas, rotación, rollback y runbook | DevOps/SRE + Seguridad | Prueba de recuperación y owner asignado |

No se estima duración ni ahorro sin capacidad, volumen de solicitudes y línea base. El orden anterior expresa dependencias, no fechas comprometidas.

Para una instalación nueva con GoDaddy: tipo A; host hermes-harness; valor IP pública comprobada del VPS; TTL 600 o predeterminado. No introducir protocolo, ruta o puerto en el valor. Si Traefik/Coolify ya usa 80/443, no instalar un segundo proxy que compita por esos puertos.

## 9. Plan de pruebas y aceptación

Infraestructura:
- Resolver DNS y comprobar TLS, HTTP→HTTPS y health.
- Probar backend desde la red del proxy y comprobar que no se puede acceder por la interfaz pública.
- Revisar puertos protegidos antes y después.

Seguridad y contrato:
- Sin token o token incorrecto: 401.
- Operación no permitida con token válido: 422.
- JSON malformado: 400; raíz que no sea objeto: 422.
- Body vacío o superior al límite: 413 según implementación actual.
- Probar tipos incorrectos en campos anidados; deben devolver errores de contrato, no cerrar la conexión.
- Probar timeout, salida no JSON, proceso fallido y concurrencia.
- Comprobar que la entrada no permite elevar permisos ni escribir sin aprobación.

Funcional E2E pendiente:
- Enviar una HU sintética desde Cursor real, con request_id único.
- Repetir con un repositorio autorizado y rama concreta.
- Verificar commit/fuentes, preguntas por rol, criterios y riesgos.
- Revisar que no haya cambios en Azure DevOps o archivos no autorizados.
- Registrar evidencia de ejecución y decisión humana; HTTP 200 no basta.

## 10. Observabilidad y operación

Métricas recomendadas: solicitudes, éxito de transporte, éxito funcional, 401/422/5xx, latencia p50/p95, timeouts, concurrencia y costo por solicitud si el proveedor lo permite. Medir también porcentaje de respuestas con fuentes verificables y borradores aceptados/devueltos.

Owner técnico propuesto: DevOps/SRE para disponibilidad; owner Hermes para contexto y permisos; QA para evidencia; PO para utilidad y aceptación. Asignar personas concretas antes del piloto.

Diagnóstico:
- 401: variable no disponible en el proceso de Cursor, token antiguo, doble Bearer, comillas o espacios, header incorrecto o URL equivocada. No pegar el token en chat.
- 422: revisar operación y contrato; con el probe inválido es el resultado esperado.
- 503: comprobar servicio, bind privado, conectividad desde Traefik y firewall; no abrir el backend públicamente como solución.
- Timeout: alinear presupuestos; evitar reintentos ciegos que dupliquen ejecuciones.
- 200 sin evidencia: revisar prompt, fuentes autorizadas y acceso real; no certificar consulta a repositorios por el nombre de la herramienta.

Rollback recomendado: deshabilitar únicamente la ruta manual del bridge o detener su servicio, revocar credencial y conservar evidencia sanitizada. No detener el proxy compartido ni modificar rutas de otras aplicaciones. Restaurar una versión conocida del bridge/contrato cuando se requiera recuperación. Ejecutar solo con autorización de cambio.

## 11. Próximo paso recomendado

Aprobar un piloto acotado con un repositorio, una rama, un owner y una HU sintética. Resolver primero aislamiento de permisos, contrato y timeouts. Después ejecutar la prueba desde Cursor y registrar evidencias. No habilitar escrituras en Azure DevOps en esta fase.

Principio operativo: IA propone → herramientas ejecutan → personas autorizadas verifican, aceptan riesgo y deciden.

## 12. Fuentes

- Código local inspeccionado: /opt/hermes-harness/hermes_harness_bridge_stdlib.py.
- Configuración local inspeccionada: /data/coolify/proxy/dynamic/hermes-harness.yaml.
- Cliente local inspeccionado: /root/filehub/storage/telegramhub/hermes-harness-mvp/cursor-harness/enrich_hu.py.
- Evidencia en vivo: systemctl show, ss -lnt, DNS, GET /health, POST sin token, POST autenticado de operación inválida y ufw status.
- Procedimiento local: skill hermes-harness-bridge.
- Documentación oficial de Hermes: https://hermes-agent.nousresearch.com/docs/ y su índice https://hermes-agent.nousresearch.com/docs/llms.txt. La API /v1/enrich-user-story es del bridge propio, no del producto Hermes.

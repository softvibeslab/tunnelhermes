# Hermes–Cursor Replica Kit v1

Paquete de documentación y réplica. Abrir wiki/index.html para navegar sin servidor. La wiki también está en Markdown para importar manualmente a Azure DevOps Wiki, GitHub Wiki u Obsidian.

## Clonar en un VPS con Hermes

El procedimiento para dejar el bridge en marcha está en [IMPLEMENTACION.md](IMPLEMENTACION.md). Seguirlo en orden, una vez por VPS. Si el clon lo lee un agente Hermes, el punto de entrada es [AGENTS.md](AGENTS.md).

Cada destino genera su propio token, su propio perfil y su propio dominio. Esta copia no sustituye el bridge de origen.

Esta versión es NUEVA y NO sustituye el bridge de origen. Los tests locales usan un runner controlado y no prueban al proveedor LLM ni Cursor real. Ver evidence/validation.txt y wiki/08-evidencia.md.

## Inicio rápido

Requisitos: Linux, Python 3.11+, Hermes instalado y configurado, usuario de servicio sin privilegios, perfil dedicado previamente autorizado, proveedor disponible y permisos técnicos revisados. El kit no incluye configuración personal, memoria, repositorios, tokens ni credenciales de modelo.

1. Verificar SHA256SUMS.json con python3 verify_package.py.
2. Ejecutar python3 -m unittest discover -s tests -v.
3. Inspeccionar puertos con ss -lntp y proxy existente antes de reservar puerto.
4. Crear/configurar el perfil dedicado con herramientas oficiales de Hermes; no clonar secretos ni usar default. Revisar hermes profile --help, hermes profile create --help y documentación oficial antes de crearlo.
5. Ejecutar como usuario de servicio:
   python3 configure.py --state "$HOME/hermes-cursor-state" --profile cursor-bridge --workspace "$HOME/workspace" --port 8797
   El workspace debe existir. Se genera un token nuevo que NO se imprime. config.json arranca con policy_reviewed=false.
6. Revisar config.json: proyectos, repositorios exactos y permisos efectivos. policy_reviewed=true es una confirmación del operador, NO un sandbox. Usar cuenta sin acceso a datos de otros clientes, credenciales de repositorio read-only y filesystem de negocio read-only. El directorio del perfil requiere escritura para sesiones; no exponer credenciales de escritura.
7. Iniciar solo después de esa revisión:
   python3 bridge.py --config "$HOME/hermes-cursor-state/config.json"
8. Verificar GET http://127.0.0.1:8797/health; exponer mediante proxy HTTPS conforme wiki/04-despliegue.md. No cambiar a 0.0.0.0.
9. Provisionar el token de forma privada en el entorno del proceso Cursor como HERMES_BRIDGE_TOKEN y URL HTTPS como HERMES_BRIDGE_URL. No enviar el PAT de Azure DevOps a Cursor.
10. Desde el kit en el equipo cliente:
    python3 client.py examples/request.json --out output/draft-001.json

El output no se sobrescribe. No hay reintentos automáticos ni deduplicación persistente. request_id correlaciona pero NO garantiza idempotencia. Una respuesta 200 es borrador; evidence_verified permanece false hasta comprobación externa.

Para un alta manual desde la terminal de Cursor sin pegar el token en el chat, consulta [onboarding/README.md](onboarding/README.md). El asistente solicita el token con entrada oculta y no lo guarda; necesita un bridge HTTPS ya publicado y un modelo probado.

Templates systemd y Traefik son ejemplos con sustituciones explícitas, no instaladores ejecutados. No se modifica infraestructura al descomprimir o configurar el kit. El administrador debe instalar y validar esos templates conscientemente.

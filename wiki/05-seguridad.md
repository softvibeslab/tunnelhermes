# Seguridad y privacidad

No contiene PATs, Bearer del origen, OAuth, .env, memoria, historial ni configuración privada del proveedor. Cada destino genera su token y provisiona sus credenciales de forma privada. No compartir el token del origen.

Controles del código: Bearer con compare_digest, bind privado, allowlist proyecto/repositorio, draft_only obligatorio, tipos/tamaño, un proceso de agente a la vez, timeout, salida limitada, errores sin stderr, temporales eliminados y logging de request_id/status. El ThreadingHTTPServer no es un servidor público de alto tráfico: siempre detrás de proxy con rate limit, límites de conexión y timeout. La limitación del semáforo cubre ejecuciones de Hermes, no todos los hilos HTTP.

Límites explícitos: no sandbox de herramientas; no verificación semántica de fuentes; result sin esquema de negocio estricto; stdout/stderr temporales pueden crecer hasta límites del filesystem durante la ejecución. Usar cuotas/cgroups, cuenta dedicada y monitoreo de disco. No prometer prevención de escritura sin permisos efectivos y pruebas negativas. La revisión policy_reviewed es una atestación manual, no un control automático.

Montar repositorios y documentos read-only; evitar shell/MCP/herramientas con credenciales de escritura y acceso a otros clientes. No heredar entorno de un usuario administrador lleno de secretos. Auditar prompts inyectados, hooks y herramientas. El dato del cliente es no confiable. TLS no evita prompt injection.

Rotación: generar un token aleatorio nuevo en un archivo temporal del MISMO directorio con permisos 0600, vaciar buffers y reemplazar el archivo activo mediante os.replace (rename atómico). No truncar ni editar en sitio el token activo. Actualizar Cursor por canal privado. El bridge relee y valida longitud/permisos en cada solicitud y devuelve 503 si el archivo está vacío, es inválido o tiene permisos abiertos. Probar que el token anterior retorna 401. El cliente rechaza todas las redirecciones HTTP para no reenviar el Bearer a otro origen o degradar a HTTP. Nunca registrar tokens. Proteger también backups y transcripts. El endpoint health solo expone estado genérico.

# Contrato del kit e integración Cursor

POST /v1/enrich-user-story con application/json y Authorization: Bearer. Variables cliente: HERMES_BRIDGE_URL y HERMES_BRIDGE_TOKEN, inyectadas por entorno/gestor de secretos, nunca en reglas o prompts. El token no incluye el prefijo Bearer.

Campos requeridos: operation=enrich_user_story, mode=draft_only, request_id y project con letras/números/_/./-, story.title y story.description no vacíos. repo_candidates es lista de strings exactos autorizados por proyecto; si no está vacía, branch es obligatorio. constraints es lista de strings. Campos adicionales no admitidos. Ver examples/request.json y validate() en bridge.py, autoridad ejecutable del contrato.

Respuesta exitosa: schema_version=1.0, request_id, status=draft, mode=draft_only, result (objeto JSON del agente), evidence_verified=false. El objeto result aún no tiene esquema semántico estricto: revisar fuentes y campos requeridos por el negocio. Salida no JSON del modelo: 502, no falso éxito.

Códigos: 400 JSON/transferencia inválida; 401 auth; 404 ruta; 408 lectura de body; 411 Content-Length; 413 tamaño; 415 media type; 422 contrato/allowlist; 429 ejecución ocupada; 500 error interno; 502 Hermes/salida; 503 auth no disponible; 504 timeout. El cliente informa códigos sin imprimir cuerpos sensibles.

La regla .cursor/rules/hermes-bridge.mdc es un ejemplo opt-in para copiar al proyecto autorizado. La invocación depende de las políticas y capacidades de su versión de Cursor; no se configura el IDE remotamente con este paquete.

No hay idempotencia persistente. No reintentar tras timeout sin comprobar ejecución. El cliente espera 420 s, backend 360 s y proxy de ejemplo 390 s; cualquier LB/CDN adicional debe permitir ese presupuesto o requerirá jobs asíncronos.

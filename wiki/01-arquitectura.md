# Arquitectura y alcance

Cursor → client.py → HTTPS/Bearer → proxy del VPS → bridge privado → Hermes CLI → fuentes autorizadas → borrador → revisión humana.

Es un bridge propio, no SSH, VPN, MCP ni API nativa de Hermes. No sincroniza el workspace de Cursor. Se ejecuta una operación enrich_user_story; no hay endpoint de shell arbitraria. TLS termina en el proxy; el tramo backend usa HTTP privado.

Origen observado: https://hermes-harness.iamobilityappsinc.com/v1/enrich-user-story. La réplica usa SU PROPIO dominio y token; no debe apuntar al origen por accidente. El código distribuido es una versión separada con controles adicionales; no fue desplegado sobre el origen.

Límites: un perfil no es aislamiento de seguridad por sí mismo, draft_only no bloquea herramientas, ni una allowlist de nombres impide al agente consultar otras fuentes disponibles. La seguridad requiere usuario/credenciales/montajes/red limitados. No importar memorias o repositorios del origen sin autorización.

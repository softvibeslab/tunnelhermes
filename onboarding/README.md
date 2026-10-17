# Onboarding local de Cursor para Hermes–Cursor

Este onboarding es **para el Mac donde usas Cursor**. No instala ni publica el bridge. Necesitas una URL HTTPS funcional y el token del destino autorizado; **`cursor-bridge.softvibes.cloud` solo tiene DNS en este momento: todavía no hay servicio publicado ni modelo probado**. No confundas un `/health` exitoso con una consulta real al modelo o una verificación de fuentes.

## Preparación por el administrador del VPS

1. Completar `IMPLEMENTACION.md`: proveedor/modelo del perfil aislado, revisión de permisos y política, prueba local real, servicio y ruta HTTPS. No reutilizar tokens de otro VPS o de la cuenta anterior `ubuntu`.
2. Confirmar que el endpoint exacto es `https://cursor-bridge.softvibes.cloud/v1/enrich-user-story` **solo después** de publicar y validar TLS/POST.
3. Entregar la URL (no secreta) por el canal acordado. Entregar el token mediante un gestor de secretos o transferencia cifrada autenticada, **nunca** por un commit, issue, PR, Cursor Chat, archivo compartido o correo. El token está en el archivo protegido `token` del estado de ese VPS; no copiar su valor a la documentación.
4. Rotar el token si se expone. No conceder al bridge PAT de Azure DevOps ni credenciales de escritura en repositorios.

## Uso en Cursor (Mac)

1. Clona este repositorio en tu Mac (o actualiza tu copia) y abre el proyecto autorizado en Cursor. Si quieres una regla de orientación, copia `onboarding/hermes-bridge-onboarding.mdc` a `.cursor/rules/` de ese proyecto; no copies además la regla antigua del kit para evitar instrucciones duplicadas. La regla no contiene secretos ni ejecuta el cliente por ti.
2. Abre **tú mismo** una terminal interactiva integrada en Cursor. Desde la carpeta de este kit, ejecuta:

   ```bash
   python3 onboarding/cursor_onboarding.py \
     --url https://cursor-bridge.softvibes.cloud/v1/enrich-user-story \
     examples/request.json --out output/borrador-001.json
   ```

   Sustituye la URL si el administrador te entrega otra. La URL debe tener certificado TLS válido; el script rechaza HTTP, parámetros y credenciales en la URL. La URL en el ejemplo **aún no está operativa**.
3. Cuando aparezca `Token del bridge (entrada oculta):`, introdúcelo personalmente desde el canal seguro. No pegues el token en Cursor Chat, en la regla, en el comando, en un `.env` del proyecto ni en un mensaje a un agente. No se guarda en disco ni en el historial de shell. Si la terminal no es interactiva, el script falla sin usar el token.
4. Cambia `examples/request.json` por una solicitud real autorizada. El ejemplo es un borrador de prueba; comprueba `project`, `branch` y repositorios contra la política del VPS. `--out` debe ser una ruta nueva: el cliente no sobreescribe respuestas.
5. Abre el JSON de salida y revisa el borrador con una persona. `evidence_verified=false` significa que las fuentes **no** se han comprobado. No escribas ni comentes automáticamente en Azure DevOps.

El script llama al `client.py` del kit: envía `Authorization: Bearer` sin imprimir el token, exige HTTPS, bloquea redirecciones y no hace reintentos automáticos. El token reside solo en la memoria del proceso mientras se ejecuta. Otros procesos del mismo usuario con acceso al entorno podrían verlo durante esa ejecución; usa una sesión local confiable y evita herramientas que registren entornos/procesos. Por comodidad automatizada, el mecanismo documentado en `README.md` permite inyectar variables de entorno desde un gestor de secretos al **proceso** de Cursor, pero no conviertas el token en texto del repositorio.

## Errores y seguridad

- `401`: token/URL equivocados o token rotado. Confirmar el destino; no pegar el token en un ticket.
- `422`: solicitud, proyecto o repo no autorizado. Revisar el contrato y `config.json` del VPS.
- `429`, `502`, `504` o timeout: comprobar primero si la ejecución sigue en curso; no reintentar a ciegas.
- Un `GET /health` responde solo que el servidor escucha; la aceptación necesita un POST válido y una respuesta de modelo real. Ver `IMPLEMENTACION.md` pasos 9–10.
- El archivo `output/` está ignorado por Git. Puede contener datos de negocio: mantenlo privado y bórralo según la política de retención del proyecto.

Si el token quedó expuesto, avisa al administrador para rotarlo en ese VPS y redistribuirlo por un canal seguro. No incluyas su valor en informes.

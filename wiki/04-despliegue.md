# Runbook de réplica

## Preparación

Ejecutar el kit con Python 3.11+ en Linux. Instalar/configurar Hermes consultando https://hermes-agent.nousresearch.com/docs/ y hermes --help. No descargar instaladores a ciegas como parte de este paquete. Crear usuario de servicio sin privilegios y perfil dedicado solo con autorización del administrador del destino. Crear workspace vacío o fuentes autorizadas read-only. El kit NO crea perfiles ni modifica otros perfiles.

Consultar ss -lntp, proxy existente, red Docker y firewall. Evitar puertos ocupados; en origen están reservados 3000/3100/3101/4317/4318/12345. No asumir que 8797 está libre en el destino. configure.py prueba bind, pero hay que verificar listeners de nuevo al iniciar.

## Configuración

Seguir README. configure.py genera token nuevo y config sin sobrescribir archivos. policy_reviewed=false bloquea el inicio hasta que el operador confirme revisión. Establecer proyectos y lista de repositorios exactos; no aceptar URLs arbitrarias del cliente. Configurar aislamiento OS y credenciales read-only antes de poner true. La revisión es manual; el flag no verifica permisos por sí solo.

TEMPORALES: configurar scratch en un directorio privado, respaldado por cuota/retención adecuadas. No usar rutas de otros clientes. Hermes puede guardar sesiones/transcripts además del prompt temporal, por lo que se debe revisar retención del perfil.

## Red y TLS

Proxy en host: usar bind 127.0.0.1. Proxy Docker: usar gateway privado real de esa red, NO suponer 10.0.1.1; autorizar solo la subred del proxy por firewall. Un contenedor no llega al loopback del host. Nunca publicar el backend directamente. La interfaz privada por sí sola no sustituye al firewall.

Crear A record del subdominio hacia IP pública comprobada del VPS; valor solo IP, sin protocolo ni puerto. Verificar DNS. Reutilizar proxy existente para TLS/443; 80 solo para redirect o ACME si se necesita. El template Traefik requiere reemplazar dominio, entrypoints, resolver y backend. Configurar redirect HTTPS y security headers conforme política del proxy. Validar configuración y red desde el contenedor antes de publicar. No instalar otro proxy si 80/443 ya están ocupados.

## Servicio

Adaptar deploy/hermes-cursor.service.example al usuario y rutas reales. Crear scratch y dar acceso SOLO a perfil/estado; ReadOnlyPaths para fuentes. Verificar que hermes_bin sea ejecutable por esa cuenta y HOME resuelva su configuración. Los templates no incluyen secretos. Revisar systemd-analyze verify antes de instalar; después daemon-reload, enable y start con autorización de cambio. No ejecutar templates con valores REPLACE.

## Aceptación

Health interno, conectividad proxy→host, HTTPS público, 401 sin token, 422 autenticado con operación inválida, HU sintética, HU con fuentes autorizadas y revisión humana. Verificar inaccesibilidad del backend desde red pública y ausencia de escrituras no autorizadas. Un health exitoso no verifica el proveedor de modelo.

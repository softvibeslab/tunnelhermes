# Agente en el VPS

Al clonar este repositorio en una máquina con Hermes, seguir [IMPLEMENTACION.md](IMPLEMENTACION.md) en orden. Repetir el procedimiento entero en cada VPS. Cada destino tiene su perfil, su token, su dominio y su directorio de estado.

Detenerse y pedir confirmación de quien administra el host antes de:

- crear o modificar un perfil Hermes
- poner `policy_reviewed` en `true`
- instalar o arrancar la unidad systemd
- publicar la ruta en el proxy
- cambiar firewall o DNS

No imprimir el token, no pegarlo en el chat y no commitearlo. No enlazar el bridge a `0.0.0.0`. No reutilizar el dominio ni el token del origen descrito en `documentacion-origen.md`.

`configure.py` solo escribe estado local. No instala el servicio ni abre la red.

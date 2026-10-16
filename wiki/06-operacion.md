# Operación y rollback

401: comprobar entorno de Cursor, URL, token antiguo, comillas, espacios y doble Bearer. No pegar secretos en soporte. 429: ejecución activa; comprobar estado antes de volver a enviar. 502: revisar proveedor/CLI con logs privados sanitizados; nunca enviar stderr crudo al usuario. 503: revisar servicio/proxy/firewall; NO abrir 0.0.0.0. 504: revisar presupuesto; no duplicar ejecución a ciegas.

Log de aplicación: request_id y código, no HU. Recoger disponibilidad, latencia p50/p95, errores, ocupación, timeouts, costo si está disponible, fuentes comprobadas y aceptación/devolución por PO. No hay backend de métricas incluido. Owner propuesto: DevOps/SRE disponibilidad; responsable Hermes permisos/contexto; QA evidencia; PO utilidad. Asignar personas antes del piloto.

Rollback: deshabilitar solo la ruta del bridge, detener su unidad, revocar token y conservar evidencia sanitizada. No detener Traefik compartido ni alterar otros servicios. Restaurar versión del paquete y contrato previamente aceptados; comprobar health/auth y HU sintética antes de reabrir. El kit no cambia producción en el origen.

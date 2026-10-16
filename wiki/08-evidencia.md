# Evidencia y límites de validación

El documento documentacion-origen.md conserva la fotografía de validación del origen con su fecha; no se debe tratar como inventario del destino. El kit v1 no fue desplegado en el origen.

Ver evidence/validation.txt para las pruebas realmente ejecutadas sobre este paquete. Tests con runner controlado verifican contrato HTTP y manejo de proceso, NO inferencia real ni acceso a repositorios. Ninguna salida de prueba representa datos del negocio o una respuesta real de Hermes.

Pendiente en destino: instalación como usuario de servicio, proveedor/modelo, E2E desde Cursor, aislamiento de permisos, conectividad/firewall público, TLS y validación de fuentes reales. Templates de infraestructura requieren adaptación y validación en el stack de destino.

Fuentes oficiales: https://hermes-agent.nousresearch.com/docs/ ; https://hermes-agent.nousresearch.com/docs/llms.txt . Los flags del CLI se contrastaron con hermes chat --help en origen; comprobar compatibilidad en destino.

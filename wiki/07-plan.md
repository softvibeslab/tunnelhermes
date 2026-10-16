# Plan y criterios de cierre

1. Alcance: PO/arquitectura aprueban proyecto, rama, fuentes y datos autorizados.
2. Seguridad: cuenta/perfil dedicados, repositorios read-only y sin credenciales de escritura; Seguridad verifica pruebas negativas.
3. Infraestructura: DevOps comprueba listeners, DNS, TLS, proxy y firewall sin impacto a servicios existentes.
4. Contrato: Backend/QA ejecutan pruebas del kit y acuerdan campos de result requeridos.
5. Cursor: líder técnico configura entorno privado, ejecuta HU sintética desde equipo real y guarda evidencia.
6. Contexto real: owner del repositorio verifica frescura, commit, referencias y respuestas sin fuentes inventadas.
7. Piloto: PO/QA aceptan o devuelven, revisan riesgos y pendientes explícitos.
8. Operación: SRE documenta rotación, alertas y rollback; patrocinador decide continuar o detener.

No se asignan fechas ni ROI sin capacidad y línea base. Para medir valor: tiempo desde entrada a especificación aceptada, devoluciones por ambigüedad, porcentaje de criterios verificables y cobertura de trazabilidad con evidencia. Distinguir línea base, propuesta y resultado observado.

La réplica se cierra solo al pasar E2E real en destino. Las pruebas de este ZIP no cierran ese criterio.

# Proceso funcional y responsabilidades

1. Negocio/PO presenta una necesidad incompleta.
2. Cursor prepara HU, proyecto, rama y fuentes autorizadas.
3. Bridge valida autenticación, modo y contrato; limita a una ejecución simultánea.
4. Hermes enriquece con fuentes accesibles; identifica vacíos y preguntas para PO, UX, arquitectura, datos, seguridad, desarrollo, QA y DevOps.
5. Se produce un borrador: alcance, reglas, actores, flujos, estados, excepciones, permisos, integraciones, criterios y riesgos.
6. Responsables revisan y aprueban la especificación antes de la HU final.
7. El equipo conecta CP1/CP2/CP3 según sus definiciones oficiales; el kit no inventa su significado.
8. Desarrollo y QA mantienen requisito → riesgo → caso → ejecución → evidencia → defecto → decisión.
9. Negocio acepta o devuelve tras demo y evidencias. Escrituras en Azure DevOps permanecen fuera del bridge.
10. DevOps aplica Quality Gates, artefactos versionados/firmados, CI/CD, cambio, rollback y validación postproducción.
11. SRE observa errores y telemetría; PO mide valor con una línea base y fuentes identificadas. Sentry/analítica son integraciones propuestas, no incluidas en este kit.

El kit implementa el tramo de enriquecimiento, no el ciclo completo. IA propone → herramientas ejecutan → personas autorizadas verifican y deciden.

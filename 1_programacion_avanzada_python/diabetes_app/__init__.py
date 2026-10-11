"""
Paquete diabetes_app: pipeline de calidad de datos de ingresos hospitalarios de pacientes diabéticos.

Dataset: "Diabetes 130-US Hospitals for Years 1999-2008" (UCI Machine Learning Repository).

Módulos:
  - loader:        carga de los encuentros hospitalarios (patrón Repository)
  - validator:     reglas de validación propias del dominio clínico
  - metrics:       métricas de reingreso, estancia y calidad de datos
  - cli:           punto de entrada por línea de comandos
  - crear_muestra: genera la muestra reducida que se versiona en el repositorio
"""
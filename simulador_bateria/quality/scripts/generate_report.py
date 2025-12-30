#!/usr/bin/env python3
"""
Script para generar reporte de calidad en formato Markdown.
"""
import json
import sys
from datetime import datetime
from pathlib import Path


def generate_markdown_report(metrics: dict, validation: dict = None) -> str:
    """Genera un reporte en formato Markdown."""
    lines = []

    # Encabezado
    lines.append("# Reporte de Calidad de Código")
    lines.append("")
    lines.append(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Ruta analizada:** `{metrics.get('source_path', 'N/A')}`")
    lines.append("")

    # Resumen
    if validation:
        grade = validation.get("grade", "N/A")
        passed = validation.get("passed", 0)
        total = validation.get("total", 0)
        lines.append(f"## Calificación: {grade}")
        lines.append("")
        lines.append(f"Quality Gates: {passed}/{total} pasados")
        lines.append("")

    # Métricas de LOC
    loc = metrics.get("loc", {})
    lines.append("## Líneas de Código")
    lines.append("")
    lines.append("| Métrica | Valor |")
    lines.append("|---------|-------|")
    lines.append(f"| Total LOC | {loc.get('total_loc', 0)} |")
    lines.append(f"| SLOC (sin blancos/comentarios) | {loc.get('total_sloc', 0)} |")
    lines.append(f"| Comentarios | {loc.get('total_comments', 0)} |")
    lines.append(f"| Líneas en blanco | {loc.get('total_blank', 0)} |")
    lines.append(f"| Archivos Python | {loc.get('file_count', 0)} |")
    lines.append("")

    # Complejidad Ciclomática
    cc = metrics.get("complexity", {})
    lines.append("## Complejidad Ciclomática")
    lines.append("")
    lines.append("| Métrica | Valor | Umbral |")
    lines.append("|---------|-------|--------|")
    avg_cc = cc.get("average_cc", 0)
    status = "OK" if avg_cc <= 10 else "ALERTA"
    lines.append(f"| CC Promedio | {avg_cc:.2f} | ≤ 10 ({status}) |")
    lines.append(f"| CC Máximo | {cc.get('max_cc', 0)} | - |")
    lines.append(f"| Total funciones | {cc.get('total_functions', 0)} | - |")
    lines.append("")

    # Índice de Mantenibilidad
    mi = metrics.get("maintainability", {})
    lines.append("## Índice de Mantenibilidad")
    lines.append("")
    lines.append("| Métrica | Valor | Umbral |")
    lines.append("|---------|-------|--------|")
    avg_mi = mi.get("average_mi", 0)
    status = "OK" if avg_mi > 20 else "ALERTA"
    lines.append(f"| MI Promedio | {avg_mi:.2f} | > 20 ({status}) |")
    lines.append(f"| MI Mínimo | {mi.get('min_mi', 0):.2f} | - |")
    lines.append("")

    # Pylint Score
    pylint_score = metrics.get("pylint_score", 0)
    lines.append("## Pylint Score")
    lines.append("")
    status = "OK" if pylint_score >= 8.0 else "ALERTA"
    lines.append(f"**Score:** {pylint_score:.2f}/10 ({status}, umbral ≥ 8.0)")
    lines.append("")

    # Quality Gates detallados
    if validation:
        lines.append("## Quality Gates")
        lines.append("")
        lines.append("| Gate | Valor | Umbral | Estado |")
        lines.append("|------|-------|--------|--------|")
        for gate in validation.get("gates", []):
            status_emoji = "✅" if gate["status"] == "PASS" else "❌"
            lines.append(
                f"| {gate['gate']} | {gate['value']:.2f} | "
                f"{gate['operator']} {gate['threshold']} | {status_emoji} {gate['status']} |"
            )
        lines.append("")

    # Pie de página
    lines.append("---")
    lines.append(f"*Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    return "\n".join(lines)


def main():
    """Función principal."""
    if len(sys.argv) < 2:
        print("Uso: python generate_report.py <archivo_metricas.json> [archivo_validacion.json]")
        sys.exit(1)

    metrics_file = Path(sys.argv[1])
    if not metrics_file.exists():
        print(f"Error: El archivo {metrics_file} no existe")
        sys.exit(1)

    with open(metrics_file, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    validation = None
    if len(sys.argv) > 2:
        validation_file = Path(sys.argv[2])
        if validation_file.exists():
            with open(validation_file, "r", encoding="utf-8") as f:
                validation = json.load(f)

    report = generate_markdown_report(metrics, validation)

    # Guardar reporte
    output_file = metrics_file.parent / f"report_{metrics_file.stem}.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Reporte generado: {output_file}")
    print("\n" + "=" * 60 + "\n")
    print(report)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script para calcular métricas de calidad del código.
Calcula: LOC, Complejidad Ciclomática (CC), Índice de Mantenibilidad (MI), Pylint Score.
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze


def count_loc(source_path: Path) -> dict:
    """Cuenta líneas de código usando radon."""
    total_loc = 0
    total_sloc = 0
    total_comments = 0
    total_blank = 0
    file_count = 0

    for py_file in source_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding="utf-8")
            analysis = analyze(content)
            total_loc += analysis.loc
            total_sloc += analysis.sloc
            total_comments += analysis.comments
            total_blank += analysis.blank
            file_count += 1
        except Exception:
            continue

    return {
        "total_loc": total_loc,
        "total_sloc": total_sloc,
        "total_comments": total_comments,
        "total_blank": total_blank,
        "file_count": file_count,
    }


def calculate_complexity(source_path: Path) -> dict:
    """Calcula la complejidad ciclomática promedio."""
    complexities = []

    for py_file in source_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding="utf-8")
            results = cc_visit(content)
            for item in results:
                complexities.append(item.complexity)
        except Exception:
            continue

    if not complexities:
        return {"average_cc": 0, "max_cc": 0, "total_functions": 0}

    return {
        "average_cc": sum(complexities) / len(complexities),
        "max_cc": max(complexities),
        "total_functions": len(complexities),
    }


def calculate_maintainability(source_path: Path) -> dict:
    """Calcula el índice de mantenibilidad promedio."""
    mi_scores = []

    for py_file in source_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding="utf-8")
            mi_score = mi_visit(content, multi=False)
            if mi_score is not None:
                mi_scores.append(mi_score)
        except Exception:
            continue

    if not mi_scores:
        return {"average_mi": 0, "min_mi": 0, "file_count": 0}

    return {
        "average_mi": sum(mi_scores) / len(mi_scores),
        "min_mi": min(mi_scores),
        "file_count": len(mi_scores),
    }


def run_pylint(source_path: Path) -> float:
    """Ejecuta pylint y retorna el score."""
    try:
        result = subprocess.run(
            ["pylint", str(source_path), "--output-format=json"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        # Pylint retorna el score en stderr o hay que parsearlo
        # Intentamos con otra llamada para obtener solo el score
        result = subprocess.run(
            ["pylint", str(source_path), "--score=y"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = result.stdout + result.stderr
        for line in output.split("\n"):
            if "rated at" in line.lower():
                # Extraer score del formato "Your code has been rated at X.XX/10"
                parts = line.split("rated at")
                if len(parts) > 1:
                    score_str = parts[1].split("/")[0].strip()
                    return float(score_str)
        return 0.0
    except Exception:
        return 0.0


def main():
    """Función principal."""
    if len(sys.argv) < 2:
        print("Uso: python calculate_metrics.py <ruta_codigo>")
        sys.exit(1)

    source_path = Path(sys.argv[1])
    if not source_path.exists():
        print(f"Error: La ruta {source_path} no existe")
        sys.exit(1)

    print(f"Calculando métricas para: {source_path}")

    loc_metrics = count_loc(source_path)
    cc_metrics = calculate_complexity(source_path)
    mi_metrics = calculate_maintainability(source_path)
    pylint_score = run_pylint(source_path)

    metrics = {
        "timestamp": datetime.now().isoformat(),
        "source_path": str(source_path),
        "loc": loc_metrics,
        "complexity": cc_metrics,
        "maintainability": mi_metrics,
        "pylint_score": pylint_score,
    }

    # Guardar resultados
    output_dir = Path(__file__).parent.parent / "reports"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nResultados guardados en: {output_file}")
    print(f"\nResumen:")
    print(f"  LOC total: {loc_metrics['total_loc']}")
    print(f"  SLOC: {loc_metrics['total_sloc']}")
    print(f"  Archivos: {loc_metrics['file_count']}")
    print(f"  CC promedio: {cc_metrics['average_cc']:.2f}")
    print(f"  MI promedio: {mi_metrics['average_mi']:.2f}")
    print(f"  Pylint score: {pylint_score:.2f}/10")


if __name__ == "__main__":
    main()

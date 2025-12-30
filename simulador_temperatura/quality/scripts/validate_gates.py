#!/usr/bin/env python3
"""
Script para validar quality gates.
Umbrales: CC promedio ≤ 10, MI promedio > 20, Pylint score ≥ 8.0
"""
import json
import sys
from pathlib import Path

# Quality Gates
GATES = {
    "cyclomatic_complexity": {"threshold": 10, "operator": "<=", "field": "complexity.average_cc"},
    "maintainability_index": {"threshold": 20, "operator": ">", "field": "maintainability.average_mi"},
    "pylint_score": {"threshold": 8.0, "operator": ">=", "field": "pylint_score"},
}


def get_nested_value(data: dict, field: str):
    """Obtiene un valor anidado usando notación de punto."""
    keys = field.split(".")
    value = data
    for key in keys:
        value = value.get(key, 0)
    return value


def validate_gate(value: float, threshold: float, operator: str) -> bool:
    """Valida un gate según el operador."""
    if operator == "<=":
        return value <= threshold
    elif operator == ">=":
        return value >= threshold
    elif operator == ">":
        return value > threshold
    elif operator == "<":
        return value < threshold
    return False


def calculate_grade(passed_gates: int, total_gates: int) -> str:
    """Calcula la calificación según gates pasados."""
    if passed_gates == total_gates:
        return "A"
    elif passed_gates == total_gates - 1:
        return "B"
    elif passed_gates == total_gates - 2:
        return "C"
    else:
        return "F"


def main():
    """Función principal."""
    if len(sys.argv) < 2:
        print("Uso: python validate_gates.py <archivo_metricas.json>")
        sys.exit(1)

    metrics_file = Path(sys.argv[1])
    if not metrics_file.exists():
        print(f"Error: El archivo {metrics_file} no existe")
        sys.exit(1)

    with open(metrics_file, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    print(f"Validando quality gates para: {metrics.get('source_path', 'unknown')}")
    print(f"Timestamp: {metrics.get('timestamp', 'unknown')}")
    print("-" * 60)

    passed = 0
    failed = 0
    results = []

    for gate_name, gate_config in GATES.items():
        value = get_nested_value(metrics, gate_config["field"])
        threshold = gate_config["threshold"]
        operator = gate_config["operator"]
        is_passed = validate_gate(value, threshold, operator)

        status = "PASS" if is_passed else "FAIL"
        if is_passed:
            passed += 1
        else:
            failed += 1

        results.append({
            "gate": gate_name,
            "value": value,
            "threshold": threshold,
            "operator": operator,
            "status": status,
        })

        print(f"  {gate_name}:")
        print(f"    Valor: {value:.2f} {operator} {threshold}")
        print(f"    Estado: {status}")

    grade = calculate_grade(passed, len(GATES))

    print("-" * 60)
    print(f"Gates pasados: {passed}/{len(GATES)}")
    print(f"Calificación: {grade}")

    # Guardar resultados de validación
    validation_result = {
        "metrics_file": str(metrics_file),
        "gates": results,
        "passed": passed,
        "failed": failed,
        "total": len(GATES),
        "grade": grade,
    }

    output_file = metrics_file.parent / f"validation_{metrics_file.stem}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(validation_result, f, indent=2)

    print(f"\nResultados guardados en: {output_file}")

    # Exit code según resultado
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()

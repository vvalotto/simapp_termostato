"""
Tests unitarios para el sistema de tracking de tiempo.

Cubre las funcionalidades principales de TimeTracker, Task, Phase y Pause.
"""
import pytest
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
import tempfile
import shutil
import time

# Ajustar el path para importar desde .claude/tracking
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude"))

from tracking.time_tracker import TimeTracker, Task, Phase, Pause


@pytest.fixture
def temp_tracking_dir(monkeypatch):
    """Crea un directorio temporal para tracking durante los tests."""
    temp_dir = tempfile.mkdtemp()
    tracking_path = Path(temp_dir) / ".claude" / "tracking"
    tracking_path.mkdir(parents=True)

    # Monkey patch para que TimeTracker use el directorio temporal
    original_init = TimeTracker.__init__

    def patched_init(self, us_id, us_title, us_points, producto):
        original_init(self, us_id, us_title, us_points, producto)
        self.storage_path = tracking_path / f"{us_id}-tracking.json"

    monkeypatch.setattr(TimeTracker, "__init__", patched_init)

    yield tracking_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def tracker(temp_tracking_dir):
    """Fixture que provee un TimeTracker limpio."""
    return TimeTracker(
        us_id="US-001",
        us_title="Test Historia",
        us_points=3,
        producto="test_producto"
    )


class TestTask:
    """Tests para la clase Task."""

    def test_crear_task_con_valores_default(self):
        """Test que Task se crea con valores por defecto."""
        task = Task(
            task_id="task_001",
            task_name="Test Task",
            task_type="modelo",
            estimated_minutes=10.0
        )

        assert task.task_id == "task_001"
        assert task.task_name == "Test Task"
        assert task.task_type == "modelo"
        assert task.estimated_minutes == 10.0
        assert task.status == "pending"
        assert task.started_at is None
        assert task.completed_at is None
        assert task.elapsed_seconds == 0

    def test_actual_minutes_calcula_correctamente(self):
        """Test que actual_minutes convierte segundos a minutos."""
        task = Task(
            task_id="task_001",
            task_name="Test",
            task_type="modelo",
            estimated_minutes=10.0
        )
        task.elapsed_seconds = 600  # 10 minutos

        assert task.actual_minutes == 10.0

    def test_variance_minutes_calcula_diferencia(self):
        """Test que variance_minutes calcula diferencia correctamente."""
        task = Task(
            task_id="task_001",
            task_name="Test",
            task_type="modelo",
            estimated_minutes=10.0
        )
        task.elapsed_seconds = 720  # 12 minutos

        assert task.variance_minutes == 2.0  # 12 - 10

    def test_variance_percent_calcula_porcentaje(self):
        """Test que variance_percent calcula porcentaje correctamente."""
        task = Task(
            task_id="task_001",
            task_name="Test",
            task_type="modelo",
            estimated_minutes=10.0
        )
        task.elapsed_seconds = 600  # 10 minutos (0% varianza)
        assert task.variance_percent == 0.0

        task.elapsed_seconds = 1200  # 20 minutos (+100% varianza)
        assert task.variance_percent == 100.0


class TestPhase:
    """Tests para la clase Phase."""

    def test_crear_phase_con_valores_default(self):
        """Test que Phase se crea con valores por defecto."""
        phase = Phase(
            phase_number=0,
            phase_name="Test Phase"
        )

        assert phase.phase_number == 0
        assert phase.phase_name == "Test Phase"
        assert phase.status == "pending"
        assert phase.tasks == []
        assert phase.auto_approved is True

    def test_elapsed_minutes_convierte_segundos(self):
        """Test que elapsed_minutes convierte correctamente."""
        phase = Phase(phase_number=0, phase_name="Test")
        phase.elapsed_seconds = 300  # 5 minutos

        assert phase.elapsed_minutes == 5.0


class TestPause:
    """Tests para la clase Pause."""

    def test_crear_pause(self):
        """Test que Pause se crea correctamente."""
        now = datetime.now(timezone.utc)
        pause = Pause(
            pause_id="pause_001",
            started_at=now,
            reason="Reunión"
        )

        assert pause.pause_id == "pause_001"
        assert pause.started_at == now
        assert pause.reason == "Reunión"
        assert pause.resumed_at is None
        assert pause.is_active is True

    def test_is_active_retorna_false_cuando_resumida(self):
        """Test que is_active es False cuando la pausa está resumida."""
        now = datetime.now(timezone.utc)
        pause = Pause(
            pause_id="pause_001",
            started_at=now
        )
        pause.resumed_at = now + timedelta(minutes=10)

        assert pause.is_active is False


class TestTimeTrackerCreacion:
    """Tests de creación e inicialización de TimeTracker."""

    def test_crear_tracker_con_parametros(self, tracker):
        """Test que TimeTracker se crea con parámetros correctos."""
        assert tracker.us_id == "US-001"
        assert tracker.us_title == "Test Historia"
        assert tracker.us_points == 3
        assert tracker.producto == "test_producto"
        assert tracker.started_at is None
        assert tracker.phases == []
        assert tracker.pauses == []

    def test_storage_path_se_configura_correctamente(self, tracker):
        """Test que el path de almacenamiento se configura bien."""
        assert "US-001-tracking.json" in str(tracker.storage_path)


class TestTimeTrackerTracking:
    """Tests de métodos de tracking."""

    def test_start_tracking_registra_timestamp(self, tracker):
        """Test que start_tracking registra el timestamp de inicio."""
        tracker.start_tracking()

        assert tracker.started_at is not None
        assert isinstance(tracker.started_at, datetime)
        assert tracker.storage_path.exists()

    def test_start_phase_crea_nueva_fase(self, tracker):
        """Test que start_phase crea una nueva fase."""
        tracker.start_tracking()
        tracker.start_phase(0, "Validación")

        assert len(tracker.phases) == 1
        assert tracker.current_phase is not None
        assert tracker.current_phase.phase_number == 0
        assert tracker.current_phase.phase_name == "Validación"
        assert tracker.current_phase.status == "in_progress"

    def test_end_phase_finaliza_fase(self, tracker):
        """Test que end_phase finaliza una fase correctamente."""
        tracker.start_tracking()
        tracker.start_phase(0, "Validación")
        tracker.end_phase(0)

        phase = tracker.phases[0]
        assert phase.status == "completed"
        assert phase.completed_at is not None
        assert phase.elapsed_seconds >= 0  # Puede ser 0 en tests rápidos
        assert tracker.current_phase is None

    def test_start_task_crea_tarea_en_fase_actual(self, tracker):
        """Test que start_task crea una tarea en la fase actual."""
        tracker.start_tracking()
        tracker.start_phase(3, "Implementación")
        tracker.start_task(
            task_id="task_001",
            task_name="Implementar Modelo",
            task_type="modelo",
            estimated_minutes=10.0
        )

        assert len(tracker.current_phase.tasks) == 1
        assert tracker.current_task is not None
        assert tracker.current_task.task_id == "task_001"
        assert tracker.current_task.status == "in_progress"

    def test_start_task_sin_fase_activa_lanza_error(self, tracker):
        """Test que start_task sin fase activa lanza ValueError."""
        tracker.start_tracking()

        with pytest.raises(ValueError, match="No hay fase activa"):
            tracker.start_task(
                task_id="task_001",
                task_name="Test",
                task_type="modelo",
                estimated_minutes=10.0
            )

    def test_end_task_finaliza_tarea(self, tracker):
        """Test que end_task finaliza una tarea correctamente."""
        tracker.start_tracking()
        tracker.start_phase(3, "Implementación")
        tracker.start_task(
            task_id="task_001",
            task_name="Test",
            task_type="modelo",
            estimated_minutes=10.0
        )
        tracker.end_task(task_id="task_001", file_created="test.py")

        task = tracker.current_phase.tasks[0]
        assert task.status == "completed"
        assert task.completed_at is not None
        assert task.elapsed_seconds >= 0  # Puede ser 0 en tests rápidos
        assert task.file_created == "test.py"
        assert tracker.current_task is None


class TestTimeTrackerPausas:
    """Tests de funcionalidad de pausas."""

    def test_pause_crea_pausa_activa(self, tracker):
        """Test que pause crea una pausa activa."""
        tracker.start_tracking()
        tracker.pause(reason="Reunión")

        assert len(tracker.pauses) == 1
        assert tracker.current_pause is not None
        assert tracker.current_pause.pause_id == "pause_001"
        assert tracker.current_pause.reason == "Reunión"

    def test_pause_con_pausa_activa_lanza_error(self, tracker):
        """Test que pause con pausa activa lanza ValueError."""
        tracker.start_tracking()
        tracker.pause()

        with pytest.raises(ValueError, match="Ya hay una pausa activa"):
            tracker.pause()

    def test_resume_finaliza_pausa(self, tracker):
        """Test que resume finaliza la pausa correctamente."""
        tracker.start_tracking()
        tracker.pause(reason="Café")
        tracker.resume()

        pause = tracker.pauses[0]
        assert pause.resumed_at is not None
        assert pause.duration_seconds >= 0  # Puede ser 0 en tests rápidos
        assert tracker.current_pause is None

    def test_resume_sin_pausa_activa_lanza_error(self, tracker):
        """Test que resume sin pausa activa lanza ValueError."""
        tracker.start_tracking()

        with pytest.raises(ValueError, match="No hay pausa activa"):
            tracker.resume()


class TestTimeTrackerStatus:
    """Tests de get_status."""

    def test_get_status_sin_iniciar_retorna_not_started(self, tracker):
        """Test que get_status retorna not_started sin tracking."""
        status = tracker.get_status()

        assert status["status"] == "not_started"

    def test_get_status_retorna_informacion_completa(self, tracker):
        """Test que get_status retorna información completa."""
        tracker.start_tracking()
        tracker.start_phase(0, "Validación")
        tracker.start_task("task_001", "Test", "modelo", 10.0)

        status = tracker.get_status()

        assert status["status"] == "running"
        assert "started_at" in status
        assert status["elapsed_seconds"] >= 0
        assert status["effective_seconds"] >= 0
        assert status["current_phase"] == "Validación"
        assert status["current_task"] == "Test"

    def test_get_status_con_pausa_activa(self, tracker):
        """Test que get_status detecta pausa activa."""
        tracker.start_tracking()
        tracker.pause()

        status = tracker.get_status()

        assert status["status"] == "paused"
        assert status["paused_seconds"] >= 0  # Puede ser 0 en tests rápidos


class TestTimeTrackerPersistencia:
    """Tests de persistencia JSON."""

    def test_save_crea_archivo_json(self, tracker):
        """Test que _save crea archivo JSON."""
        tracker.start_tracking()

        assert tracker.storage_path.exists()

    def test_to_dict_genera_estructura_completa(self, tracker):
        """Test que _to_dict genera estructura completa."""
        tracker.start_tracking()
        tracker.start_phase(0, "Validación")
        tracker.start_task("task_001", "Test", "modelo", 10.0)
        tracker.end_task("task_001")
        tracker.end_phase(0)

        data = tracker._to_dict()

        assert "metadata" in data
        assert data["metadata"]["us_id"] == "US-001"
        assert "timeline" in data
        assert "phases" in data
        assert len(data["phases"]) == 1
        assert "summary" in data

    def test_json_es_valido_y_parseble(self, tracker):
        """Test que el JSON generado es válido."""
        tracker.start_tracking()
        tracker.start_phase(0, "Validación")
        tracker.end_phase(0)

        # Leer el JSON guardado
        with open(tracker.storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert data["metadata"]["us_id"] == "US-001"
        assert len(data["phases"]) == 1


class TestTimeTrackerIntegracion:
    """Tests de integración de flujo completo."""

    def test_flujo_completo_fase_con_tareas(self, tracker):
        """Test de flujo completo: fase con múltiples tareas."""
        # Iniciar tracking
        tracker.start_tracking()

        # Fase con tareas
        tracker.start_phase(3, "Implementación")

        # Tarea 1
        tracker.start_task("task_001", "Modelo", "modelo", 10.0)
        tracker.end_task("task_001", file_created="modelo.py")

        # Tarea 2
        tracker.start_task("task_002", "Vista", "vista", 20.0)
        tracker.end_task("task_002", file_created="vista.py")

        # Finalizar fase
        tracker.end_phase(3)

        # Verificar
        phase = tracker.phases[0]
        assert len(phase.tasks) == 2
        assert phase.tasks[0].status == "completed"
        assert phase.tasks[1].status == "completed"
        assert phase.status == "completed"

    def test_flujo_con_pausas(self, tracker):
        """Test de flujo con pausas."""
        tracker.start_tracking()
        tracker.start_phase(0, "Validación")

        # Pausa 1
        tracker.pause("Reunión")
        tracker.resume()

        # Pausa 2
        tracker.pause("Café")
        tracker.resume()

        tracker.end_phase(0)

        # Verificar
        assert len(tracker.pauses) == 2
        status = tracker.get_status()
        assert status["paused_seconds"] >= 0  # Puede ser 0 en tests rápidos

    def test_calculo_de_varianzas_en_summary(self, tracker):
        """Test que el summary calcula varianzas correctamente."""
        tracker.start_tracking()
        tracker.start_phase(3, "Implementación")

        # Tarea estimada en 10min
        tracker.start_task("task_001", "Test", "modelo", 10.0)
        tracker.end_task("task_001")

        # Simular que tardó más tiempo (modificar después de end_task)
        task = tracker.current_phase.tasks[0]
        task.elapsed_seconds = 720  # 12 minutos

        data = tracker._to_dict()
        summary = data["summary"]

        assert summary["estimated_total_minutes"] == 10.0
        assert summary["actual_total_minutes"] == 12.0
        assert summary["variance_minutes"] == 2.0
        assert summary["variance_percent"] == 20.0

"""Check the recorder switch without starting any processes."""

from pathlib import Path

from launch import LaunchContext
from launch.actions import ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
import pytest


@pytest.mark.parametrize(('record', 'enabled'), [('false', False), ('true', True)])
def test_record_switch(record: str, enabled: bool) -> None:
    """The launch argument controls whether the recorder process is started."""
    context = LaunchContext()
    context.launch_configurations['record'] = record
    launch_path = Path(__file__).resolve().parents[1] / 'launch' / 'patrol.launch.py'
    description = PythonLaunchDescriptionSource(str(launch_path)).get_launch_description(context)
    [recorder] = [action for action in description.entities if isinstance(action, ExecuteProcess)]
    assert recorder.condition is not None
    assert recorder.condition.evaluate(context) is enabled

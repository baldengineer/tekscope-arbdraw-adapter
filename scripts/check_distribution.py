"""Test the built wheel in a fresh environment outside the source directory."""
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
VERIFY = '''
from importlib.metadata import entry_points
from importlib.util import find_spec
from pathlib import Path
import sys
import tekscope_arb_adapter

assert find_spec("python_bridge") is None, "Standalone wheel must not need ArbDraw"
assert Path(tekscope_arb_adapter.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
adapters = {ep.name: ep.load() for ep in entry_points(group="arbdraw.instrument_adapters")}
assert adapters["tekscope-mso2"] is tekscope_arb_adapter.send_waveform_mso2
assert adapters["tekscope-mso6"] is tekscope_arb_adapter.send_waveform_mso6
print("Standalone installed wheel and entry points verified")
'''


def main():
    dist = Path(sys.argv[1]).resolve()
    wheels = list(dist.glob('tekscope_arbdraw_adapter-*.whl'))
    sdists = list(dist.glob('tekscope_arbdraw_adapter-*.tar.gz'))
    assert len(wheels) == len(sdists) == 1, 'Expected one wheel and one sdist'
    with ZipFile(wheels[0]) as archive:
        assert any(name.endswith('/licenses/LICENSE') for name in archive.namelist())
        metadata = next(name for name in archive.namelist() if name.endswith('.dist-info/METADATA'))
        assert '# TekScope ArbDraw adapter' in archive.read(metadata).decode()
    with tarfile.open(sdists[0]) as archive:
        names = archive.getnames()
        for relative in ('README.md', 'LICENSE', 'tekscope_arb_adapter/adapter.py'):
            assert any(name.endswith('/' + relative) for name in names), relative
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        subprocess.run([sys.executable, '-m', 'venv', str(temp / 'venv')], check=True)
        python = temp / 'venv' / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
        subprocess.run([str(python), '-m', 'pip', 'install', str(wheels[0])], check=True, cwd=temp)
        subprocess.run([str(python), '-c', VERIFY], check=True, cwd=temp)
        subprocess.run([str(python), '-m', 'unittest', 'discover', '-s', str(ROOT / 'tests'), '-p', 'test_*.py'], check=True, cwd=temp)
        cli = python.parent / ('arbdraw-tekscope.exe' if sys.platform == 'win32' else 'arbdraw-tekscope')
        subprocess.run([str(cli), '--help'], check=True, cwd=temp)


if __name__ == '__main__':
    main()

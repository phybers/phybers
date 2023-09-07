"""Module for finding and checking atlases."""
from pathlib import Path
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

_atlas_folder: Path = files('phybers.segment.fiberseg').joinpath('data')  # type: ignore
atlases = {k.stem: str(k) for k in _atlas_folder.glob('*')}


def check_atlas(filepath: str):
    """Check correct structure of atlas."""
    atlas_p = Path(filepath)
    info_p = atlas_p / "atlas_info_p.txt"
    bundles_p = atlas_p / "bundles"
    if info_p.is_file():
        names = set()
        with info_p.open() as f:
            names.add(f.readline().split()[0])
    else:
        return False
    if bundles_p.is_dir():
        found_names = set()
        for bundle in bundles_p.glob('*.bundles'):
            found_names.add(bundle.stem)
    else:
        return False
    if names != found_names:
        return False
    return True

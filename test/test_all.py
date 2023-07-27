from pathlib import Path
from json import load

def load_config(file = "config.json"):
    p = Path(file)

    if p.is_absolute():
        if not p.exists():
            raise FileNotFoundError(f"Config file {p} not found.")
    else:
        cwd = Path.cwd()
        if (cwd / p).exists():
            p = cwd / p
        elif (cwd / "test" / p).exists():
            p = (cwd / "test" / p)
        elif (Path(__file__).parent / p).exists():
            p = (Path(__file__).parent / p)
        else:
            raise FileNotFoundError(f"Config file {p} not found.")
    with open(str(p), 'rt') as config_file:
        return load(config_file)

def try_import() -> bool:
    try:
        import phybers
        return True
    except ImportError:
        return False

def call_exit() -> None:
    exit()

def ffclust():
    from phybers.clustering.ffclust import cluster
    try:
        cluster(*load_config()["ffclust"])
        return True
    except SystemError:
        return False

def hclust():
    from phybers.clustering.hclust import cluster
    try:
        cluster(*load_config()["hclust"])
        return True
    except SystemError:
        return False


def segmentation():
    from phybers.segment import segment
    try:
        segment(*load_config()["segmentation"])
        return True
    except SystemError:
        return False


def deform():
    from phybers.utils import deform
    try:
        deform(*load_config()["deform"])
        return True
    except SystemError:
        return False

def intersection():
    from phybers.utils import intersection
    try:
        intersection(*load_config()["intersection"])
        return True
    except SystemError:
        return False

def sampling():
    from phybers.utils import sampling
    try:
        sampling(*load_config()["sampling"])
        return True
    except SystemError:
        return False

def postprocessing():
    from phybers.utils import postprocessing
    try:
        postprocessing(*load_config()["postprocessing"])
        return True
    except SystemError:
        return False


def test_import_succes():
    print(Path.cwd())
    assert try_import()

def test_ffclust():
    assert ffclust()

def test_hclust():
    assert hclust()

def test_segmentation():
    assert segmentation()

def test_deform():
    assert deform()

def test_intersection():
    assert intersection()

def test_sampling():
    assert sampling()

def test_postprocessing():
    assert postprocessing()

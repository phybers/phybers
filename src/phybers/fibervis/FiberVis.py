import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from PyQt5 import QtWidgets

parser = ArgumentParser(add_help=False, exit_on_error=False)
parser.add_argument('miscellaneous_files', nargs='*', default=(),
                    help='List of files or directories to be loaded '
                         'if supported.')
parser.add_argument('--bundles', nargs='*', default=(),
                    help='List of bundles files or directories containing '
                         'bundles files to be loaded.')
parser.add_argument('--mri', nargs='*', default=(),
                    help='List of mri files or directories containing '
                         'mri files to be loaded.')
parser.add_argument('--mesh', nargs='*', default=(),
                    help='List of mesh files or directories containing '
                         'mesh files to be loaded.')
parser.add_argument('--help', action='store_true')


def process_args(known_args: Namespace) -> dict[str, list[str]]:
    processed_paths: dict[str, list[str]] = {'bundles': [],
                                             'mri': [],
                                             'mesh': []}
    path_types = ('bundles', 'mri', 'mesh')
    path_formats = {'bundles': ('.bundles', '.trk', '.tck'),
                    'mri': ('.gz', '.nii'),
                    'mesh': ('.mesh', '.gii')}
    for path_type in path_types:
        for path_str in getattr(known_args, path_type):
            path = Path(path_str)
            if path.is_dir():
                for path_format in path_formats[path_type]:
                    processed_paths[path_type].extend(
                        map(str, path.glob(f'*{path_format}')))
            elif path.is_file():
                processed_paths[path_type].append(str(path))
            else:
                raise FileNotFoundError(path)
        if known_args.miscellaneous_files:
            for path_str in known_args.miscellaneous_files.copy():
                path = Path(path_str)
                if path.is_dir():
                    for path_format in path_formats[path_type]:
                        processed_paths[path_type].extend(
                            map(str, path.glob(f'*{path_format}')))
                elif path.is_file() and path.suffix in path_formats[path_type]:
                    known_args.miscellaneous_files.remove(path_str)
                    processed_paths[path_type].append(str(path))
                else:
                    known_args.miscellaneous_files.remove(path_str)
                    print(f'Path {path} not found, skiping.')
    return processed_paths


def parse_args_and_run():
    namespace, args = parser.parse_known_args(sys.argv[1:])
    app = QtWidgets.QApplication(args)
    if namespace.help:
        message_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                            "Help", f"<pre>{parser.format_help()}</pre>")
        message_box.exec()
    else:
        from .WindowController import WindowController

        paths = process_args(namespace)
        fiber_app = WindowController()
        fiber_app.show()
        fiber_app.contextHandler.addBundleFile(paths['bundles'])
        fiber_app.contextHandler.addMRIFile(paths['mri'])
        fiber_app.contextHandler.addMeshFile(paths['mesh'])
        app.exec()



def main(bundles=(), mri=(), mesh=(), args: list[str] = []):
    
    """
    Initializes the graphical user interface (GUI).
    
    Parameters
    ----------
    None

    Examples
    --------
    To test `fibervis()`, download the data from the links provided above. Then, open a Python terminal and run the following commands:

    .. code:: python

       from phybers.fibervis import start_fibervis
       start_fibervis()
    
    `fibervis()` is installed as a program, allowing you to run it through the command line in Windows or Ubuntu. To execute it on both platforms, use the following command:

    .. code:: python

       fibervis

    For your convenience in using `fibervis()`, a video demonstrating all its features is accessible through the following link:
    :video_link: [Video Link][video].    
    """

    from .WindowController import WindowController

    app = QtWidgets.QApplication(args)
    fiber = WindowController()
    fiber.show()
    fiber.contextHandler.addBundleFile(bundles)
    fiber.contextHandler.addMRIFile(mri)
    fiber.contextHandler.addMeshFile(mesh)
    return app.exec_()

import importlib.util
from pathlib import Path


def import_path(base: Path) -> None:
    if not base.is_dir():
        raise ValueError(f"{base} is not a valid directory")

    imported_modules = {}

    for file_path in base.rglob("*.py"):  # recursive, includes subdirectories
        if file_path.name == "__init__.py":
            continue  # skip package __init__ files

        module_name = file_path.stem  # filename without extension

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            continue  # skip files that can't be loaded

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        imported_modules[module_name] = module

    return imported_modules

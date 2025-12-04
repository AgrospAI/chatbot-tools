from importlib.metadata import PackageNotFoundError, version as v


def version(package_name: str) -> str:
    try:
        return v(package_name)
    except PackageNotFoundError:
        return ""

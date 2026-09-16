from pathlib import Path


def create_folder(path: Path) -> None:
    """
    Create a folder if it does not already exist.

    Parameters
    ----------
    path : Path
        Folder to create.
    """
    path.mkdir(parents=True, exist_ok=True)
    print(f"Created: {path}")

PROJECT_ROOT = Path.cwd()

create_folder(PROJECT_ROOT / "star")
create_folder(PROJECT_ROOT / "docs")
create_folder(PROJECT_ROOT / "examples")
create_folder(PROJECT_ROOT / "tests")

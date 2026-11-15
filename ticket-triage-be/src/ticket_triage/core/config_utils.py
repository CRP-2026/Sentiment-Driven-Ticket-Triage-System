from pathlib import Path


def find_config_file(filename: str) -> Path | None:
    """Tự động duyệt ngược từ vị trí package và CWD để tìm file config YAML."""
    search_roots = [Path(__file__).resolve(), Path.cwd().resolve()]

    for start_path in search_roots:
        for parent in (start_path, *start_path.parents):
            target = parent / "configs" / filename
            if target.is_file():
                return target

            nested_target = parent / "ticket-triage-be" / "configs" / filename
            if nested_target.is_file():
                return nested_target

    return None

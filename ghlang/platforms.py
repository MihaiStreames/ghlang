import platform


def platform_tag() -> str:
    """Return a string identifying the current platform"""
    system = platform.system()
    machine = platform.machine().lower()

    if system == "Linux":
        if machine in {"x86_64", "amd64"}:
            return "linux-x86_64"
        if machine in {"aarch64", "arm64"}:
            return "linux-aarch64"
    elif system == "Darwin":
        if machine in {"x86_64", "amd64"}:
            return "macos-x86_64"
        if machine in {"arm64", "aarch64"}:
            return "macos-arm64"
    elif system == "Windows":
        if machine in {"x86_64", "amd64"}:
            return "windows-x86_64"

    raise ValueError(f"Unsupported platform: {system} {machine}")


def tokount_binary_name() -> str:
    """Return the name of the tokount binary for the current platform"""
    return "tokount.exe" if platform.system() == "Windows" else "tokount"

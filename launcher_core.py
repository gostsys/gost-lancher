from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import minecraft_launcher_lib


DEFAULT_VERSION = "1.20.1"


def _normalize_game_directory(game_dir: str) -> str:
    """Return an absolute, normalized game directory path."""
    return str(Path(game_dir).expanduser().resolve())


def _detect_java_executable() -> str:
    """
    Detect a usable Java executable.

    Priority:
    1) JAVA_HOME/bin/java(.exe)
    2) java from PATH
    3) java.exe from PATH on Windows
    """
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        home_path = Path(java_home).expanduser()
        candidates = [
            home_path / "bin" / ("java.exe" if os.name == "nt" else "java"),
            home_path / "bin" / "java",
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)

    found = shutil.which("java")
    if found:
        return found

    if os.name == "nt":
        found = shutil.which("java.exe")
        if found:
            return found

    raise RuntimeError(
        "Java غير مثبتة أو غير موجودة في PATH. "
        "ثبّت Java 17 أو Java 21 وتأكد من تفعيل Add to PATH."
    )


def _build_options(username: str, game_dir: str, java_executable: str) -> Dict[str, Any]:
    """Build launch options using the documented minecraft-launcher-lib fields."""
    return {
        "username": username,
        "uuid": "",
        "token": "",
        "launcherName": "GOST_Launcher",
        "launcherVersion": "1.0",
        "gameDirectory": game_dir,
        "defaultExecutablePath": java_executable,
        "executablePath": java_executable,
        "customResolution": False,
        "demo": False,
    }


def launch_game(
    username: str,
    game_dir: str,
    version: str = DEFAULT_VERSION,
    callbacks: Optional[Dict[str, Callable]] = None,
) -> None:
    """
    Install the requested Minecraft version if needed and launch it.

    Flow:
    1) detect Java
    2) install_minecraft_version()
    3) get_minecraft_command()
    4) subprocess.Popen()
    """
    version = (version or DEFAULT_VERSION).strip()
    if not version:
        version = DEFAULT_VERSION

    game_dir = _normalize_game_directory(game_dir)
    os.makedirs(game_dir, exist_ok=True)

    java_executable = _detect_java_executable()

    if callbacks and "setStatus" in callbacks:
        callbacks["setStatus"]("جاري فحص ملفات ماينكرافت وتحميل الناقص...")

    if callbacks:
        minecraft_launcher_lib.install.install_minecraft_version(version, game_dir, callbacks)
    else:
        minecraft_launcher_lib.install.install_minecraft_version(version, game_dir)

    options = _build_options(username, game_dir, java_executable)

    if callbacks and "setStatus" in callbacks:
        callbacks["setStatus"]("جاري تجهيز أوامر التشغيل...")

    minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(
        version=version,
        minecraft_directory=game_dir,
        options=options,
    )

    if callbacks and "setStatus" in callbacks:
        callbacks["setStatus"]("جارٍ تشغيل ماينكرافت...")

    subprocess.Popen(minecraft_command, cwd=game_dir)


__all__ = ["DEFAULT_VERSION", "launch_game"]

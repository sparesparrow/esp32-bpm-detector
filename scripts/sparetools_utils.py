#!/usr/bin/env python3
"""
SpareTools Utilities Integration
Provides access to shared SpareTools utilities from sparetools-base package.

This module integrates utilities from the SpareTools ecosystem available via Conan2
from Cloudsmith, providing consistent tooling across all SpareTools projects.
"""

import os
import sys
import logging
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import importlib.util

# Try to import sparetools utilities
SPARETOOLS_AVAILABLE = False
sparetools_module = None

def find_sparetools_base():
    """Find sparetools-base package location from Conan cache."""
    try:
        result = subprocess.run(
            ["conan", "cache", "path", "sparetools-base/2.0.3"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    
    # Try alternative version
    try:
        result = subprocess.run(
            ["conan", "cache", "path", "sparetools-base/2.0.0"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    
    return None

def load_sparetools_utils():
    """Load sparetools utilities if available."""
    global SPARETOOLS_AVAILABLE, sparetools_module
    
    if SPARETOOLS_AVAILABLE:
        return sparetools_module
    
    # Try to find sparetools-base package
    base_path = find_sparetools_base()
    if not base_path:
        logging.debug("sparetools-base not found in Conan cache")
        return None
    
    # Look for Python utilities in common locations
    util_paths = [
        base_path / "python" / "sparetools" / "utils.py",
        base_path / "lib" / "python" / "sparetools" / "utils.py",
        base_path / "share" / "sparetools" / "utils.py",
        base_path / "utils.py",
    ]
    
    for util_path in util_paths:
        if util_path.exists():
            try:
                spec = importlib.util.spec_from_file_location("sparetools_utils", util_path)
                if spec and spec.loader:
                    sparetools_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(sparetools_module)
                    SPARETOOLS_AVAILABLE = True
                    logging.info(f"Loaded sparetools utilities from {util_path}")
                    return sparetools_module
            except Exception as e:
                logging.debug(f"Failed to load {util_path}: {e}")
                continue
    
    return None

# Load utilities on import
sparetools_utils = load_sparetools_utils()

# Fallback implementations if sparetools-base not available
class SpareToolsLogger:
    """Standardized logging for SpareTools projects."""
    
    @staticmethod
    def setup_logger(name: str, level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
        """Set up standardized logger for SpareTools projects."""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Remove existing handlers
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(console_formatter)
            logger.addHandler(file_handler)
        
        return logger

class SpareToolsSubprocess:
    """Standardized subprocess execution for SpareTools projects."""
    
    @staticmethod
    def run(
        cmd: List[str],
        cwd: Optional[Path] = None,
        timeout: Optional[int] = None,
        check: bool = False,
        capture_output: bool = True,
        text: bool = True,
        env: Optional[Dict[str, str]] = None
    ) -> subprocess.CompletedProcess:
        """Run subprocess with standardized error handling."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                timeout=timeout,
                check=check,
                capture_output=capture_output,
                text=text,
                env=env
            )
            return result
        except subprocess.TimeoutExpired as e:
            logging.error(f"Command timed out after {timeout}s: {' '.join(cmd)}")
            raise
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed with code {e.returncode}: {' '.join(cmd)}")
            if e.stderr:
                logging.error(f"Error output: {e.stderr}")
            raise
        except FileNotFoundError:
            logging.error(f"Command not found: {cmd[0]}")
            raise

class SpareToolsConfig:
    """Configuration management for SpareTools projects."""
    
    @staticmethod
    def load_config(config_path: Path) -> Dict[str, Any]:
        """Load JSON configuration file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.warning(f"Config file not found: {config_path}")
            return {}
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in config file {config_path}: {e}")
            return {}
    
    @staticmethod
    def save_config(config_path: Path, config: Dict[str, Any]):
        """Save configuration to JSON file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

class SpareToolsPaths:
    """Path utilities for SpareTools projects."""
    
    @staticmethod
    def get_project_root(start_path: Optional[Path] = None) -> Path:
        """Find project root by looking for conanfile.py or .git."""
        if start_path is None:
            start_path = Path.cwd()
        
        current = Path(start_path).resolve()
        
        while current != current.parent:
            if (current / "conanfile.py").exists() or (current / ".git").exists():
                return current
            current = current.parent
        
        return Path.cwd()
    
    @staticmethod
    def ensure_dir(path: Path):
        """Ensure directory exists."""
        path.mkdir(parents=True, exist_ok=True)

class SpareToolsPython:
    """Python interpreter management for SpareTools projects."""
    
    @staticmethod
    def is_sparetools_python() -> bool:
        """Check if current Python is sparetools bundled CPython."""
        python_exe = sys.executable
        python_path = os.path.dirname(python_exe)
        python_exe_lower = python_exe.lower()
        python_path_lower = python_path.lower()
        
        # Check if Python path contains sparetools indicators
        if "sparetools" in python_exe_lower or "sparetools" in python_path_lower:
            return True
        
        # Check for common sparetools paths
        sparetools_indicators = [
            "sparetools-base",
            "sparetools-cpython",
            "sparetools/bin",
            ".sparetools/bin"
        ]
        for indicator in sparetools_indicators:
            if indicator in python_exe_lower or indicator in python_path_lower:
                return True
        
        # Check environment variables
        if os.environ.get("SPARETOOLS_PYTHON") or os.environ.get("SPARE_PYTHON"):
            return True
        
        return False
    
    @staticmethod
    def find_bundled_python() -> Optional[List[str]]:
        """Find sparetools bundled CPython interpreter."""
        # Check if already running under sparetools Python
        if SpareToolsPython.is_sparetools_python():
            logging.debug(f"Already using sparetools bundled CPython: {sys.executable}")
            return [sys.executable]
        
        # Try to get from Conan cache (sparetools-cpython package)
        try:
            # Try different versions
            for version in ["3.12.7", "3.12.0", "3.11.0"]:
                package_path = SpareToolsConan.get_package_path(f"sparetools-cpython/{version}")
                if package_path:
                    # Look for Python executable in common locations
                    python_paths = [
                        package_path / "bin" / "python3",
                        package_path / "bin" / "python",
                        package_path / "python3",
                        package_path / "python",
                    ]
                    for py_path in python_paths:
                        if py_path.exists() and os.access(py_path, os.X_OK):
                            logging.info(f"Found sparetools CPython in Conan cache: {py_path}")
                            return [str(py_path)]
        except Exception as e:
            logging.debug(f"Could not find sparetools-cpython in Conan cache: {e}")
        
        # Try sparetools command
        try:
            result = subprocess.run(
                ["sparetools", "python", "--version"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                logging.info("Using sparetools bundled CPython (via sparetools command)")
                return ["sparetools", "python"]
        except Exception:
            pass
        
        # Try common sparetools installation paths
        sparetools_paths = [
            os.path.expanduser("~/sparetools/packages/foundation/sparetools-base/test_env/bin/python"),
            os.path.expanduser("~/sparetools/bin/python"),
            os.path.expanduser("~/.sparetools/bin/python"),
            "/opt/sparetools/bin/python",
            "/usr/local/sparetools/bin/python",
            os.environ.get("SPARETOOLS_PYTHON"),
            os.environ.get("SPARE_PYTHON"),
        ]
        
        for path in sparetools_paths:
            if path and os.path.exists(path) and os.access(path, os.X_OK):
                logging.info(f"Found sparetools bundled CPython: {path}")
                return [path]
        
        return None
    
    @staticmethod
    def ensure_bundled_python() -> List[str]:
        """Ensure bundled CPython is used, return Python command."""
        bundled = SpareToolsPython.find_bundled_python()
        if bundled:
            return bundled
        
        # Fallback to system Python with warning
        logging.warning("sparetools bundled CPython not found, using system Python")
        logging.warning("To use bundled CPython: conan install sparetools-cpython/3.12.7 -r sparetools")
        return [sys.executable]

class SpareToolsConan:
    """Conan operations for SpareTools projects."""
    
    @staticmethod
    def get_package_path(package_ref: str) -> Optional[Path]:
        """Get path to Conan package in cache."""
        try:
            result = subprocess.run(
                ["conan", "cache", "path", package_ref],
                capture_output=True,
                text=True,
                timeout=10,
                check=True
            )
            return Path(result.stdout.strip())
        except Exception as e:
            logging.debug(f"Failed to get package path for {package_ref}: {e}")
            return None
    
    @staticmethod
    def install_dependencies(
        profile: Optional[str] = None,
        build_missing: bool = True,
        remote: str = "sparetools"
    ) -> bool:
        """Install Conan dependencies."""
        cmd = ["conan", "install", ".", "--build=missing" if build_missing else ""]
        
        if profile:
            cmd.extend(["--profile", f"{profile}.profile"])
        
        if remote:
            cmd.extend(["-r", remote])
        
        try:
            result = SpareToolsSubprocess.run(cmd, check=True)
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Failed to install Conan dependencies: {e}")
            return False

# Export utilities (use sparetools-base if available, otherwise fallbacks)
if sparetools_utils:
    Logger = getattr(sparetools_utils, 'Logger', SpareToolsLogger)
    Subprocess = getattr(sparetools_utils, 'Subprocess', SpareToolsSubprocess)
    Config = getattr(sparetools_utils, 'Config', SpareToolsConfig)
    Paths = getattr(sparetools_utils, 'Paths', SpareToolsPaths)
    Conan = getattr(sparetools_utils, 'Conan', SpareToolsConan)
    Python = getattr(sparetools_utils, 'Python', SpareToolsPython)
else:
    Logger = SpareToolsLogger
    Subprocess = SpareToolsSubprocess
    Config = SpareToolsConfig
    Paths = SpareToolsPaths
    Conan = SpareToolsConan
    Python = SpareToolsPython

# Convenience functions
def setup_logging(name: str, level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
    """Set up standardized logging."""
    return Logger.setup_logger(name, level, log_file)

def run_command(
    cmd: List[str],
    cwd: Optional[Path] = None,
    timeout: Optional[int] = None,
    check: bool = False
) -> subprocess.CompletedProcess:
    """Run command with standardized error handling."""
    return Subprocess.run(cmd, cwd=cwd, timeout=timeout, check=check)

def get_project_root(start_path: Optional[Path] = None) -> Path:
    """Get project root directory."""
    return Paths.get_project_root(start_path)

def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration file."""
    return Config.load_config(config_path)

def save_config(config_path: Path, config: Dict[str, Any]):
    """Save configuration file."""
    return Config.save_config(config_path, config)

def get_python_command() -> List[str]:
    """Get Python command, preferring sparetools bundled CPython."""
    return Python.ensure_bundled_python()

def is_using_bundled_python() -> bool:
    """Check if currently using sparetools bundled CPython."""
    return Python.is_sparetools_python()

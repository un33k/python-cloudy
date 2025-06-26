import logging
import subprocess

from fabric import task

from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.context import Context

logger = logging.getLogger(__name__)


@task
@Context.wrap_context
def sys_python_install_common(c: Context, py_version: str = "3.11") -> None:
    """Install common Python application packages and dependencies.

    Args:
        c: Fabric context object
        py_version: Python version to install (default: '3.11')

    Raises:
        subprocess.CalledProcessError: If package installation fails
    """
    try:
        # Parse Python version
        major_version = py_version.split(".")[0]

        # Modern package list - removed deprecated packages
        base_packages = [
            f"python{major_version}-dev",
            f"python{major_version}-setuptools",
            f"python{major_version}-pip",
            f"python{major_version}-venv",  # Modern replacement for virtualenv
            "python3-dev",  # Keep generic python3-dev
            "build-essential",  # Essential build tools
            "pkg-config",
        ]

        # Image processing libraries (updated versions)
        image_packages = [
            "libfreetype6-dev",
            "libjpeg-dev",  # Updated from libjpeg62-dev
            "libpng-dev",  # Updated from libpng12-dev
            "zlib1g-dev",
            "liblcms2-dev",
            "libwebp-dev",
            "libtiff5-dev",  # Added TIFF support
            "libopenjp2-7-dev",  # Added JPEG2000 support
        ]

        # System utilities
        utility_packages = [
            "gettext",
            "curl",
            "wget",
            "git",  # Often needed for pip installs from git
        ]

        all_packages = base_packages + image_packages + utility_packages
        package_list = " ".join(all_packages)

        logger.info(f"Installing Python {py_version} and common packages...")

        # Update package list first
        c.sudo("apt update")

        # Install packages
        c.sudo(f"apt -y install {package_list}")

        # Handle PEP 668 externally-managed-environment
        # Use system packages where possible, pip with --break-system-packages for others

        # Install system Python packages via apt (preferred method)
        system_python_packages = [
            "python3-wheel",
            "python3-setuptools",
            "python3-pil",  # Pillow via system package
        ]

        system_package_list = " ".join(system_python_packages)
        logger.info("Installing Python packages via system package manager...")
        c.sudo(f"apt -y install {system_package_list}")

        # For packages not available as system packages, use pip with --break-system-packages
        # Only do this for essential packages that aren't available via apt
        pip_cmd = f"pip{major_version}" if major_version != "2" else "pip"

        # Check if psycopg2 is available as system package first
        try:
            c.sudo("apt -y install python3-psycopg2")
            logger.info("Installed psycopg2 via system package")
        except Exception:
            logger.info("Installing psycopg2-binary via pip (system package not available)")
            c.sudo(f"{pip_cmd} install --break-system-packages psycopg2-binary")

        # Verify installation
        c.run(f"python{major_version} --version")
        c.run(f"{pip_cmd} --version")

        logger.info("Python installation completed successfully")
        sys_etc_git_commit(c, f"Installed Python {py_version} and common packages")

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install Python packages: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during Python installation: {e}")
        raise

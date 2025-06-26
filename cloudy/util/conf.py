import configparser
import logging
import os
from typing import Any, Dict, Optional

LOG_LEVEL = logging.INFO
FORMAT = "%(levelname)-10s %(name)s %(message)s"
logging.basicConfig(format=FORMAT, level=LOG_LEVEL)


class CloudyConfig:
    """
    CloudyConfig loads and manages configuration from multiple files.
    The last file in the list has the highest precedence.
    """

    def __init__(self, filenames: Any = None, log_level: int = logging.WARNING) -> None:
        self.log = logging.getLogger(os.path.basename(__file__))
        self.log.setLevel(log_level)
        self.cfg = configparser.ConfigParser()
        self.cfg_grid: Dict[str, Dict[str, Optional[str]]] = {}

        # Prepare config file paths
        paths: list[str] = []

        # 1. Config file in current directory
        cwd_path = os.path.abspath("./.cloudy")
        if os.path.exists(cwd_path):
            paths.append(cwd_path)

        # 2. Config file in home directory
        home_path = os.path.expanduser("~/.cloudy")
        if os.path.exists(home_path):
            paths.append(home_path)

        # 3. Explicitly passed config file(s)
        if filenames:
            if isinstance(filenames, str):
                filenames = [filenames]
            for f in filenames:
                p = os.path.expanduser(f)
                if os.path.exists(p) and p not in paths:
                    paths.append(p)

        # 4. Defaults file (lowest precedence)
        defaults_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../cfg/defaults.cfg")
        )
        if os.path.exists(defaults_path):
            paths.insert(0, defaults_path)

        # Read all valid config files
        try:
            self.cfg.read(paths)
        except Exception as e:
            self.log.error(f"Unable to open config file(s): {e}")
        else:
            for section in self.cfg.sections():
                self.cfg_grid[section.upper()] = self._section_map(section)

    def _section_map(self, section: str) -> Dict[str, Optional[str]]:
        """Create a dict of options for a section."""
        valid: Dict[str, Optional[str]] = {}
        options = self.cfg.options(section)
        for option in options:
            try:
                value = self.cfg.get(section, option)
                if value == "-1":
                    self.log.debug(f"skip: {option}")
                valid[option] = value
            except Exception as e:
                self.log.warning(f"Exception on {option}: {e}")
                valid[option] = None
        return valid

    def get_variable(self, section: str, variable: str, fallback: str = "") -> str:
        """
        Get a variable value from a section, with optional fallback.
        Section is case-insensitive.
        """
        try:
            value = self.cfg_grid[section.upper()][variable]
            return value.strip() if value else fallback
        except Exception:
            return fallback

    def add_variable_to_environ(self, section: str, variable: str) -> None:
        """
        Set an environment variable from the config, if present.
        """
        try:
            var = self.cfg_grid[section.upper()][variable]
            if var:
                os.environ[variable] = var
            else:
                self.log.warning(f"No such variable ({variable}) in section [{section}]")
        except Exception as e:
            self.log.warning(
                f"Failed to set environment variable ({variable}) from section [{section}]: {e}"
            )

    def get_boolean_config(self, section: str, key: str, default: bool = False) -> bool:
        """
        Get a boolean configuration value from a section.

        Accepts various formats: YES/NO, TRUE/FALSE, 1/0, ON/OFF (case-insensitive)

        Args:
            section: Configuration section name
            key: Configuration key name
            default: Default value if key not found

        Returns:
            Boolean value
        """
        value = self.get_variable(section, key, "").upper()
        return value in ("YES", "TRUE", "1", "ON")

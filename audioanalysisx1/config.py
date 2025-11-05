"""
Configuration Management
========================

Centralized configuration system with environment variable support.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class AnalysisConfig:
    """Configuration for analysis parameters."""

    # F0 Analysis
    f0_min: float = 75.0
    f0_max: float = 400.0
    f0_threshold: float = 0.1

    # Formant Analysis
    max_formants: int = 5
    formant_window_length: float = 0.025
    formant_time_step: float = 0.01

    # Artifact Detection
    mel_bins: int = 128
    noise_floor_percentile: int = 10
    stft_n_fft: int = 2048
    stft_hop_length: int = 512

    # AI Detection
    ai_model_name: str = "mo-thecreator/Deepfake-audio-detection"
    ai_confidence_threshold: float = 0.7

    # Performance
    use_gpu: bool = False
    n_jobs: int = -1  # -1 means use all CPUs
    enable_caching: bool = True
    cache_dir: str = "./.cache"

    # Output
    default_output_dir: str = "./results"
    save_visualizations: bool = True
    export_formats: list = field(default_factory=lambda: ["json", "md"])


@dataclass
class APIConfig:
    """Configuration for API server."""

    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    max_workers: int = 4
    reload: bool = False
    log_level: str = "info"

    # Storage
    storage_path: str = "./api_results"
    max_file_size_mb: int = 100
    max_duration_seconds: int = 600

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60

    # Authentication
    require_api_key: bool = False
    api_keys: list = field(default_factory=list)

    # CORS
    cors_origins: list = field(default_factory=lambda: ["*"])


@dataclass
class PluginConfig:
    """Configuration for plugin system."""

    enabled: bool = True
    plugin_dirs: list = field(default_factory=lambda: ["./plugins"])
    auto_discover: bool = True
    allowed_plugins: Optional[list] = None  # None means all allowed


@dataclass
class Config:
    """Main configuration object."""

    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    api: APIConfig = field(default_factory=APIConfig)
    plugins: PluginConfig = field(default_factory=PluginConfig)

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None

    @classmethod
    def from_file(cls, file_path: str) -> 'Config':
        """
        Load configuration from JSON or YAML file.

        Args:
            file_path: Path to config file

        Returns:
            Config object
        """
        file_path = Path(file_path)

        if not file_path.exists():
            logger.warning(f"Config file not found: {file_path}, using defaults")
            return cls()

        try:
            if file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
            elif file_path.suffix in ['.yaml', '.yml']:
                import yaml
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
            else:
                logger.error(f"Unsupported config file format: {file_path.suffix}")
                return cls()

            return cls.from_dict(data)

        except Exception as e:
            logger.error(f"Failed to load config from {file_path}: {str(e)}")
            return cls()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """
        Create Config from dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            Config object
        """
        analysis_config = AnalysisConfig(**data.get('analysis', {}))
        api_config = APIConfig(**data.get('api', {}))
        plugin_config = PluginConfig(**data.get('plugins', {}))

        return cls(
            analysis=analysis_config,
            api=api_config,
            plugins=plugin_config,
            log_level=data.get('log_level', 'INFO'),
            log_file=data.get('log_file')
        )

    @classmethod
    def from_env(cls) -> 'Config':
        """
        Load configuration from environment variables.

        Environment variables should be prefixed with AUDIOANALYSIS_
        Example: AUDIOANALYSIS_API_PORT=9000

        Returns:
            Config object
        """
        config = cls()

        # Analysis config
        config.analysis.f0_min = float(os.getenv('AUDIOANALYSIS_F0_MIN', config.analysis.f0_min))
        config.analysis.f0_max = float(os.getenv('AUDIOANALYSIS_F0_MAX', config.analysis.f0_max))
        config.analysis.use_gpu = os.getenv('AUDIOANALYSIS_USE_GPU', 'false').lower() == 'true'
        config.analysis.enable_caching = os.getenv('AUDIOANALYSIS_ENABLE_CACHING', 'true').lower() == 'true'

        # API config
        config.api.host = os.getenv('AUDIOANALYSIS_API_HOST', config.api.host)
        config.api.port = int(os.getenv('AUDIOANALYSIS_API_PORT', config.api.port))
        config.api.workers = int(os.getenv('AUDIOANALYSIS_API_WORKERS', config.api.workers))
        config.api.max_workers = int(os.getenv('AUDIOANALYSIS_API_MAX_WORKERS', config.api.max_workers))
        config.api.log_level = os.getenv('AUDIOANALYSIS_API_LOG_LEVEL', config.api.log_level)
        config.api.storage_path = os.getenv('AUDIOANALYSIS_API_STORAGE_PATH', config.api.storage_path)

        # Plugin config
        config.plugins.enabled = os.getenv('AUDIOANALYSIS_PLUGINS_ENABLED', 'true').lower() == 'true'

        # Logging
        config.log_level = os.getenv('AUDIOANALYSIS_LOG_LEVEL', config.log_level)
        config.log_file = os.getenv('AUDIOANALYSIS_LOG_FILE')

        return config

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Config to dictionary.

        Returns:
            Configuration dictionary
        """
        return {
            'analysis': asdict(self.analysis),
            'api': asdict(self.api),
            'plugins': asdict(self.plugins),
            'log_level': self.log_level,
            'log_file': self.log_file
        }

    def save(self, file_path: str):
        """
        Save configuration to file.

        Args:
            file_path: Path to save config
        """
        file_path = Path(file_path)
        data = self.to_dict()

        try:
            if file_path.suffix == '.json':
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
            elif file_path.suffix in ['.yaml', '.yml']:
                import yaml
                with open(file_path, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False)
            else:
                logger.error(f"Unsupported config file format: {file_path.suffix}")
                return

            logger.info(f"Saved configuration to {file_path}")

        except Exception as e:
            logger.error(f"Failed to save config to {file_path}: {str(e)}")


# Global configuration instance
_global_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get global configuration instance.

    Returns:
        Config object
    """
    global _global_config

    if _global_config is None:
        # Try to load from file
        config_path = os.getenv('AUDIOANALYSIS_CONFIG_FILE', 'config.json')
        if Path(config_path).exists():
            _global_config = Config.from_file(config_path)
        else:
            # Try environment variables
            _global_config = Config.from_env()

    return _global_config


def set_config(config: Config):
    """
    Set global configuration instance.

    Args:
        config: Config object
    """
    global _global_config
    _global_config = config


def reload_config():
    """Reload configuration from source."""
    global _global_config
    _global_config = None
    return get_config()

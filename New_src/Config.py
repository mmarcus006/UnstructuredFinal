import yaml
from pathlib import Path


def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Ensure paths are absolute Path objects
    config['input_dir'] = Path(config['input_dir']).resolve()
    config['output_dir'] = Path(config['output_dir']).resolve()

    # Set default values if not present
    config['parallel_processing'] = config.get('parallel_processing', True)
    config['log_level'] = config.get('log_level', 'INFO')
    config['num_workers'] = config.get('num_workers', 4)
    config['batch_size'] = config.get('batch_size', 3)

    return config
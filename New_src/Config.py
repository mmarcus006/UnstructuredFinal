import yaml
from pathlib import Path

def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Ensure paths are Path objects
    config['input_dir'] = Path(config['input_dir'])
    config['output_dir'] = Path(config['output_dir'])
    
    return config

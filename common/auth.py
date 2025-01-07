import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def load_config(yaml_path: str):
    """Load the YAML configuration file."""
    with open(yaml_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config


def init_authenticator(config_path: str):
    """Initialize the authenticator with the given config path."""
    config = load_config(config_path)
    authenticator = stauth.Authenticate(
        credentials=config['credentials'],
        cookie_name=config['cookie']['name'],
        cookie_key=config['cookie']['key'],
        cookie_expiry_days=config['cookie']['expiry_days'],
    )
    return authenticator

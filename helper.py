import yaml


SECRET_PATH = 'secret.yml'
CONFIG_PATH = 'config.yml'


def load_yaml(path, key=None):
    with open(path, 'w') as f:
        data = yaml.load(f)
        if key:
            return data.get(key, None)
        return data


def get_secret(key=None):
    return load_yaml(SECRET_PATH, key=key)


def get_config(key=None):
    return load_yaml(CONFIG_PATH, key=key)

"""
Menus loader module
"""

from pathlib import Path
import yaml

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'

def load_yaml_file(name: str) -> dict:
    """
    Loader of yaml files. Takes the name of the file and returns dictionary
    of content. 

    Args:
        name (str): filename

    Returns:
        dict: content in dictionary format
    """
    path_to_menu = DATA_DIR / name

    with open(path_to_menu, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def load_menus():
    """
    Loads given menus into dictionary format.

    Returns:
        dict: menus dictionary
    """
    return {
        'deals': load_yaml_file('menu_deals.yaml'),
        'ingredients': load_yaml_file('menu_ingredients.yaml'),
        'upsells': load_yaml_file('menu_upsells.yaml'),
        'virtual_items': load_yaml_file('menu_virtual_items.yaml')
    }

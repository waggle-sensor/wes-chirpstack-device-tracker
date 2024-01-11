import re

def replace_spaces(str: str) -> str:
    """
    replace spaces with "-"
    """
    temp = str.replace(" ", "-")
    temp = re.sub(r'-+', '-', temp) # replace consecutive hyphens with a single hyphen
    return temp

def clean_hw_model(str: str) -> str:
    """
    Makes the string compatible with hw_model field
    """
    temp = re.sub(r'\([^)]*\)', '', str) # Remove characters inside parentheses including parantheses
    temp = temp.strip()
    temp = replace_spaces(temp)
    temp = temp[:30]
    return temp
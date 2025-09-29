"""
Fix pylint duplication error and added urllib3 config
"""
import json
import urllib3

def create_record_from_json(line):
    """Processes a JSON string and returns a data record tuple."""
    json_data = json.loads(line)
    return (
        json_data.get('program'),
        json_data.get('comments'),
        json_data.get('date_added'),
        json_data.get('url'),
        json_data.get('status'),
        json_data.get('term'),
        json_data.get('US/International'),
        json_data.get('GPA'),
        json_data.get('GRE'),
        json_data.get('GRE V'),
        json_data.get('GRE AW'),
        json_data.get('Degree'),
        json_data.get('llm-generated-program'),
        json_data.get('llm-generated-university')
    )

HTTP_POOL_MANAGER = urllib3.PoolManager()
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/139.0.0.0 Safari/537.36"
)

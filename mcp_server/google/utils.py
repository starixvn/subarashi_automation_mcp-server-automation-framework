import json
import logging
from typing import List, Any, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def format_data_as_table(data: List[List[Any]], include_headers: bool = True) -> str:
    """
    Format data as a markdown table for display.

    Args:
        data: Data to format
        include_headers: Whether to include headers in the table

    Returns:
        Formatted table string
    """
    if not data:
        return "No data found"

    col_widths = []
    for i in range(max(len(row) for row in data)):
        col_widths.append(max(len(str(row[i])) if i < len(row) else 0 for row in data))

    result = []

    if include_headers and len(data) > 0:
        header = data[0]
        header_str = (
            "| "
            + " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(header))
            + " |"
        )
        result.append(header_str)
        result.append("|" + "".join("-" * (width + 2) + "|" for width in col_widths))
        data = data[1:]

    for row in data:
        row_str = (
            "| "
            + " | ".join(
                (
                    str(row[i]).ljust(col_widths[i])
                    if i < len(row)
                    else "".ljust(col_widths[i])
                )
                for i in range(len(col_widths))
            )
            + " |"
        )
        result.append(row_str)

    return "\n".join(result)


def parse_json_data(data_str: str) -> List[List[Any]]:
    """
    Parse JSON data into a 2D list suitable for Google Sheets.

    Args:
        data_str: JSON string representing data

    Returns:
        2D list of values
    """
    try:
        parsed_data = json.loads(data_str)

        if (
            parsed_data
            and isinstance(parsed_data, list)
            and isinstance(parsed_data[0], dict)
        ):
            all_keys = []
            for item in parsed_data:
                for key in item.keys():
                    if key not in all_keys:
                        all_keys.append(key)

            values = [all_keys]
            for item in parsed_data:
                row = [item.get(key, "") for key in all_keys]
                values.append(row)
            return values
        else:
            return parsed_data
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON data format")


def is_service_account_credentials(credentials_file: str) -> bool:
    """
    Check if the credentials file contains service account credentials.

    Args:
        credentials_file: Path to the credentials JSON file

    Returns:
        True if file contains service account credentials, False otherwise
    """
    try:
        with open(credentials_file, 'r') as f:
            creds_data = json.load(f)
            return creds_data.get('type') == 'service_account'
    except Exception:
        return False


def get_service_account_email(credentials_file: str) -> Optional[str]:
    """
    Extract service account email from credentials file.

    Args:
        credentials_file: Path to the service account credentials JSON file

    Returns:
        Service account email if found, None otherwise
    """
    try:
        with open(credentials_file, 'r') as f:
            creds_data = json.load(f)
            if creds_data.get('type') == 'service_account':
                return creds_data.get('client_email')
    except Exception as e:
        logger.error(f"Error reading service account email: {str(e)}")
    return None


def validate_service_account_file(credentials_file: str) -> Dict[str, Any]:
    """
    Validate service account credentials file structure.

    Args:
        credentials_file: Path to the service account credentials JSON file

    Returns:
        Dictionary with validation results and details
    """
    result = {
        "valid": False,
        "email": None,
        "project_id": None,
        "error": None
    }

    try:
        with open(credentials_file, 'r') as f:
            creds_data = json.load(f)

        required_fields = [
            'type', 'project_id', 'private_key_id', 'private_key',
            'client_email', 'client_id', 'auth_uri', 'token_uri'
        ]

        missing_fields = [field for field in required_fields if field not in creds_data]

        if missing_fields:
            result["error"] = f"Missing required fields: {', '.join(missing_fields)}"
            return result

        if creds_data.get('type') != 'service_account':
            result["error"] = "Credentials type is not 'service_account'"
            return result

        result["valid"] = True
        result["email"] = creds_data.get('client_email')
        result["project_id"] = creds_data.get('project_id')

    except FileNotFoundError:
        result["error"] = f"Credentials file not found: {credentials_file}"
    except json.JSONDecodeError:
        result["error"] = "Invalid JSON format in credentials file"
    except Exception as e:
        result["error"] = f"Error validating credentials: {str(e)}"

    return result


def generate_sharing_instructions(service_account_email: str) -> str:
    """
    Generate instructions for sharing spreadsheets with service account.

    Args:
        service_account_email: Email address of the service account

    Returns:
        Formatted sharing instructions
    """
    instructions = f"""
To allow the service account to access your Google Sheets:

1. Open your Google Sheet in your browser
2. Click the "Share" button (top right corner)
3. In the "Add people and groups" field, enter: {service_account_email}
4. Set the permission level:
   - "Viewer" for read-only access
   - "Editor" for read and write access
5. Click "Send"

The service account email is: {service_account_email}

Note: You need to share each spreadsheet individually with the service account.
"""
    return instructions.strip()


def extract_sheet_id_from_response(response: Dict[str, Any]) -> Optional[str]:
    """
    Extract sheet ID from Google Sheets API response.

    Args:
        response: Response from Google Sheets API

    Returns:
        Sheet ID if found, None otherwise
    """
    try:
        return (
            response.get("replies", [{}])[0]
            .get("addSheet", {})
            .get("properties", {})
            .get("sheetId")
        )
    except (IndexError, AttributeError):
        return None

from mcp.server.fastmcp import FastMCP, Context
from context import ServerContext
from services import GoogleSheetsService
import json


def parse_values_string(values_str: str) -> list:
    if not values_str:
        return [[""]]

    try:
        parsed = json.loads(values_str)
        if isinstance(parsed, list) and all(isinstance(row, list) for row in parsed):
            return parsed
        elif isinstance(parsed, list):
            return [parsed]
        else:
            return [[str(parsed)]]
    except (json.JSONDecodeError, TypeError):
        pass

    if "\n" in values_str:
        rows = []
        for line in values_str.strip().split("\n"):
            if line.strip():
                if "\t" in line:
                    row = [
                        cell.strip().strip('"').strip("'") for cell in line.split("\t")
                    ]
                else:
                    row = [
                        cell.strip().strip('"').strip("'") for cell in line.split(",")
                    ]
                rows.append(row)
        return rows if rows else [[values_str]]

    elif "\t" in values_str:
        row = [cell.strip().strip('"').strip("'") for cell in values_str.split("\t")]
        return [row]

    elif "," in values_str:
        row = [cell.strip().strip('"').strip("'") for cell in values_str.split(",")]
        return [row]

    else:
        return [[values_str]]


def register_google_sheets_tools(app: FastMCP, server_context: ServerContext) -> None:
    @app.tool()
    async def sheets_create_spreadsheet(title: str, context: Context) -> str:
        service = GoogleSheetsService(server_context)
        result = await service.create_spreadsheet(title)
        return (
            f"Created spreadsheet: {result.data['spreadsheet_url']}"
            if result.success
            else f"Failed to create: {result.error}"
        )

    @app.tool()
    async def sheets_open_spreadsheet(spreadsheet_id: str, context: Context) -> str:
        service = GoogleSheetsService(server_context)
        result = await service.open_spreadsheet(spreadsheet_id)
        return (
            f"Opened spreadsheet: {result.data['title']}"
            if result.success
            else f"Failed to open: {result.error}"
        )

    @app.tool()
    async def sheets_share_spreadsheet(
        spreadsheet_id: str, email: str, role: str, context: Context
    ) -> str:
        service = GoogleSheetsService(server_context)
        result = await service.share_spreadsheet(spreadsheet_id, email, role)
        return (
            f"Shared with {email} as {role}"
            if result.success
            else f"Failed to share: {result.error}"
        )

    @app.tool()
    async def sheets_list_spreadsheets(context: Context) -> str:
        service = GoogleSheetsService(server_context)
        result = await service.list_spreadsheets()
        if result.success:
            sheets = result.data["spreadsheets"]
            if not sheets:
                return "No spreadsheets found"
            output = "Spreadsheets:\n\n"
            for sheet in sheets:
                output += f"• {sheet['name']}: {sheet['id']}\n"
            return output
        else:
            return f"Failed to list spreadsheets: {result.error}"

    @app.tool()
    async def sheets_create_worksheet(
        spreadsheet_id: str, title: str, context: Context
    ) -> str:
        service = GoogleSheetsService(server_context)
        result = await service.create_worksheet(spreadsheet_id, title)
        return (
            f"Created worksheet: {title}"
            if result.success
            else f"Failed to create worksheet: {result.error}"
        )

    @app.tool()
    async def sheets_read_range(
        spreadsheet_id: str, range_name: str, context: Context
    ) -> str:
        service = GoogleSheetsService(server_context)
        result = await service.read_range(spreadsheet_id, range_name)
        if result.success:
            values = result.data["values"]
            if not values:
                return f"No data in range {range_name}"
            output = f"Data from {range_name}:\n\n"
            for row in values:
                output += f"{', '.join(str(cell) for cell in row)}\n"
            return output
        else:
            return f"Failed to read range: {result.error}"

    @app.tool()
    async def sheets_write_range(
        spreadsheet_id: str, range_name: str, values: str, context: Context
    ) -> str:
        service = GoogleSheetsService(server_context)
        parsed_values = parse_values_string(values)
        result = await service.write_range(spreadsheet_id, range_name, parsed_values)

        return (
            f"Written to range {range_name}"
            if result.success
            else f"Failed to write: {result.error}"
        )

    @app.tool()
    async def sheets_append_data(
        spreadsheet_id: str, range_name: str, values: str, context: Context
    ) -> str:
        service = GoogleSheetsService(server_context)
        parsed_values = parse_values_string(values)
        result = await service.append_data(spreadsheet_id, range_name, parsed_values)
        return (
            f"Appended data to {range_name}"
            if result.success
            else f"Failed to append: {result.error}"
        )

    @app.tool()
    async def sheets_clear_range(
        spreadsheet_id: str, range_name: str, context: Context
    ) -> str:
        service = GoogleSheetsService(server_context)
        result = await service.clear_range(spreadsheet_id, range_name)
        return (
            f"Cleared range {range_name}"
            if result.success
            else f"Failed to clear: {result.error}"
        )

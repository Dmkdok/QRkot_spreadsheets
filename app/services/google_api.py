from datetime import datetime, timedelta
from typing import List

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.models.charity_project import CharityProject

REPORT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

SHEET_CONFIG = {
    "properties": {"title": "Отчет QRKot", "locale": "ru_RU"},
    "sheets": [
        {
            "properties": {
                "sheetType": "GRID",
                "sheetId": 0,
                "title": "Закрытые проекты",
                "gridProperties": {"rowCount": 100, "columnCount": 4},
            }
        }
    ],
}


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    """Создает новую Google-таблицу и возвращает её идентификатор."""
    sheet_body = SHEET_CONFIG.copy()
    sheet_body["properties"][
        "title"
    ] = f"QRKot Report {datetime.now().strftime(REPORT_DATE_FORMAT)}"

    sheets_service = await wrapper_services.discover("sheets", "v4")
    response = await wrapper_services.as_service_account(
        sheets_service.spreadsheets.create(json=sheet_body)
    )
    return response["spreadsheetId"]


async def set_user_permissions(
    spreadsheet_id: str, wrapper_services: Aiogoogle
) -> None:
    """
    Предоставляет права доступа вашему личному email
    для редактирования таблицы.
    """
    permission_body = {
        "type": "user",
        "role": "writer",
        "emailAddress": settings.email,
    }

    drive_service = await wrapper_services.discover("drive", "v3")
    await wrapper_services.as_service_account(
        drive_service.permissions.create(
            fileId=spreadsheet_id, json=permission_body, fields="id"
        )
    )


def format_duration(duration: timedelta) -> str:
    days = duration.days
    seconds = duration.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    microseconds = duration.microseconds
    return (
        f"{days} day{'s' if days != 1 else ''}, "
        f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"
        f".{microseconds:06d}"
    )


async def spreadsheets_update_value(
    spreadsheet_id: str,
    projects: List[CharityProject],
    wrapper_services: Aiogoogle,
) -> None:
    """Заполняет таблицу данными о закрытых проектах."""
    sheets_service = await wrapper_services.discover("sheets", "v4")

    report_content = [
        [
            "Отчет по закрытым проектам",
            datetime.now().strftime(REPORT_DATE_FORMAT),
        ],
        ["Название проекта", "Время сбора", "Описание"],
    ]

    for project in projects:
        if project.close_date:
            duration = project.close_date - project.create_date
            duration_str = format_duration(duration)
            report_content.append(
                [project.name, duration_str, project.description]
            )

            report_content.append(
                [project.name, duration_str, project.description]
            )

    total_rows = len(report_content)
    if total_rows > 100:
        raise ValueError("Превышено максимальное количество строк (100)")

    update_body = {"majorDimension": "ROWS", "values": report_content}
    await wrapper_services.as_service_account(
        sheets_service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f"A1:C{total_rows}",
            valueInputOption="USER_ENTERED",
            json=update_body,
        )
    )

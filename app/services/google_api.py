from datetime import datetime, timedelta
from typing import List

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.models.charity_project import CharityProject

MAX_ROW_COUNT = 100
MAX_COLUMN_COUNT = 4

REPORT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
PROJECT_TIME_FORMAT = '%H:%M:%S'

SHEET_CONFIG = {
    'properties': {'title': 'Отчет QRKot', 'locale': 'ru_RU'},
    'sheets': [
        {
            'properties': {
                'sheetType': 'GRID',
                'sheetId': 0,
                'title': 'Закрытые проекты',
                'gridProperties': {
                    'rowCount': MAX_ROW_COUNT,
                    'columnCount': MAX_COLUMN_COUNT,
                },
            }
        }
    ],
}

PERMISSION_BODY = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': settings.email,
}

REPORT_CONTENT_BASE = [
    ['Отчет по закрытым проектам', None],
    ['Название проекта', 'Время сбора', 'Описание'],
]


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    """Создает новую Google-таблицу и возвращает её идентификатор."""
    sheet_body = SHEET_CONFIG.copy()
    sheet_body['properties'][
        'title'
    ] = f'QRKot Report {datetime.now().strftime(REPORT_DATE_FORMAT)}'

    sheets_service = await wrapper_services.discover('sheets', 'v4')
    response = await wrapper_services.as_service_account(
        sheets_service.spreadsheets.create(json=sheet_body)
    )
    return response['spreadsheetId']


async def set_user_permissions(
    spreadsheet_id: str, wrapper_services: Aiogoogle
) -> None:
    """
    Предоставляет права доступа вашему личному email
    для редактирования таблицы.
    """

    drive_service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        drive_service.permissions.create(
            fileId=spreadsheet_id, json=PERMISSION_BODY, fields='id'
        )
    )


async def spreadsheets_update_value(
    spreadsheet_id: str,
    projects: List[CharityProject],
    wrapper_services: Aiogoogle,
) -> None:
    """Заполняет таблицу данными о закрытых проектах."""
    sheets_service = await wrapper_services.discover('sheets', 'v4')

    report_content = [row.copy() for row in REPORT_CONTENT_BASE]
    report_content[0][1] = datetime.now().strftime(REPORT_DATE_FORMAT)

    for project in projects:
        if project.close_date:
            duration = project.close_date - project.create_date
            time_str = (
                datetime(1970, 1, 1) + timedelta(seconds=duration.seconds)
            ).strftime(PROJECT_TIME_FORMAT)
            duration_str = (
                f"{duration.days} day{'s' if duration.days != 1 else ''},"
                f" {time_str}"
            )
            report_content.append(
                [project.name, duration_str, project.description]
            )

    total_rows = len(report_content)
    if total_rows > MAX_ROW_COUNT:
        raise ValueError(
            f'Превышено максимальное количество строк {MAX_ROW_COUNT}.'
        )

    update_body = {'majorDimension': 'ROWS', 'values': report_content}
    await wrapper_services.as_service_account(
        sheets_service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'A1:C{total_rows}',
            valueInputOption='USER_ENTERED',
            json=update_body,
        )
    )

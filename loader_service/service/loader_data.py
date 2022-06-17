from __future__ import print_function

import os.path
from datetime import date
from time import sleep
import requests
from xml.etree import ElementTree
from typing import Iterable

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GoogleSheetParser:
    """Класс для работы с гугл-таблицами"""
    def __init__(self,
                 spreadsheet_id: str,
                 sheet_range: str,
                 orders_repo: "OrdersRepo"
            ):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        self.SAMPLE_SPREADSHEET_ID = spreadsheet_id
        self.SAMPLE_RANGE_NAME = sheet_range
        self.orders_repo = orders_repo
        self.today = date.today()
        self.rub_to_usd = None

    def _convert_rub_to_usd(self):
        """Функция перевода доллара в рубли"""
        url = "https://www.cbr.ru/scripts/XML_daily.asp"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/90.0.4430.93 Safari/537.36'
        }

        res = requests.get(url, headers=headers)

        root = ElementTree.fromstring(res.text)
        for child in root:
            if child[1].text == "USD":
                self.rub_to_usd = float(child[4].text.replace(",", "."))

    def _read_from_google_sheet(self, creds: Credentials):
        """Метод для подключения к гугл-таблице и считывание оттуда строк"""
        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()

        result = sheet.values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                    range=self.SAMPLE_RANGE_NAME).execute()

        data = result.get('values', [])

        return data

    def _get_google_api_credentials(self) -> Credentials:
        """Получаем учетные данные для работы с google API"""
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
            return creds

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Сохраняем токен для последующих подключений
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            return creds

    def fill_database(self):
        """Метод для заполнения БД строками из гугл-таблицы"""
        orders = self.orders_repo.get_all()

        actual_idx = []

        if orders:
            for order in orders:
                actual_idx.append(order.order_id)

        idx_for_delete = actual_idx[:]

        while True:
            credentials = self._get_google_api_credentials()
            data = self._read_from_google_sheet(credentials)

            if not self.rub_to_usd:
                self._convert_rub_to_usd()
            else:
                if self.today != date.today():
                    self.today = date.today()
                    self._convert_rub_to_usd()

            for row in data:
                if row and len(row) == 4:
                    order_id = int(row[0])
                    order_number = int(row[1])
                    price_usd = float(row[2])
                    delivery_date_str = row[3].split('.')
                    year = int(delivery_date_str[2])
                    month = int(delivery_date_str[1])
                    day = int(delivery_date_str[0])
                    delivery_date = date(year, month, day)

                    if order_id not in actual_idx:

                        actual_idx.append(order_id)

                        self.orders_repo.add(
                            order_id=order_id,
                            order_number=order_number,
                            price_usd=price_usd,
                            price_rub=round(price_usd * self.rub_to_usd, 2),
                            delivery_date=delivery_date
                        )

                    else:
                        try:
                            idx_for_delete.remove(order_id)
                        except ValueError:
                            pass
                        order = self.orders_repo.get_by_id(order_id)
                        if order:
                            if order.order_number == order_number and order.price_usd == price_usd\
                                    and order.delivery_date == delivery_date:
                                continue
                            else:
                                self.orders_repo.update(
                                    order_id=order_id,
                                    order_number=order_number,
                                    price_usd=price_usd,
                                    price_rub=round(price_usd * self.rub_to_usd, 2),
                                    delivery_date=delivery_date
                                )

            if idx_for_delete:
                for idx in idx_for_delete:
                    actual_idx.remove(idx)
                    self.orders_repo.delete(idx)

            idx_for_delete = actual_idx[:]

            sleep(2)

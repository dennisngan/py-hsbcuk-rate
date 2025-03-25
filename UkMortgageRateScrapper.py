"""
pip install https://github.com/nithinmurali/pygsheets/archive/staging.zip
"""
import os.path
from datetime import datetime

import pygsheets
import requests
from dotenv import load_dotenv
from loguru import logger
from lxml import etree
from pygsheets import Spreadsheet, Worksheet

from TelBot import TelBot

load_dotenv()
log_path = os.path.dirname(__file__) + "/log"
os.makedirs(log_path, exist_ok=True)
logger.add(log_path + "/uk_mortgage_rate_scrapper.log", rotation="10 MB", encoding="utf-8")


def get_date():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


class GSheet:
    def __init__(self):
        self.gs = pygsheets.authorize(service_file="credentials.json")
        self.gsheet_url = os.getenv("GSHEET_URL")
        self.gsheet: Spreadsheet = self.gs.open_by_url(self.gsheet_url)

    def append_gsheet(self, sheet_title, values):
        sheet: Worksheet = self.gsheet.worksheet_by_title(sheet_title)
        sheet.append_table(values=values)

        end_address = self.get_last_address(
            sheet.get_all_values(include_tailing_empty=False, include_tailing_empty_rows=False)
        )

        sheet.set_basic_filter(start="A2", end=end_address)

    @staticmethod
    def get_last_address(all_values):
        end_address_row = len(all_values)
        #  all_values[1] will be the title row, get the number of headers to determine the no of columns
        end_address_col = len(all_values[1])
        return pygsheets.Cell((end_address_row, end_address_col)).label


class HsbcRate:
    def __init__(self, gsheet: GSheet):
        self.url = 'https://www.hsbc.co.uk/mortgages/buy-to-let/rates/'
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'referer': 'https://www.hsbc.co.uk/mortgages/buy-to-let/rates/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        }

        self.rate_record = {}

    def get_page(self):
        logger.info("Starting to get the latest rate from HSBC UK...")
        response = requests.get(self.url, headers=self.headers).content.decode("utf-8")
        return response

    def parse_data(self, response, table_no):

        insert_time = get_date()
        tree = etree.HTML(response)

        caption = tree.xpath(f"//*[@id='content_main_basicTable_{table_no}']/table/caption//strong/text()")[0]
        print(caption)
        rates_table = tree.xpath(f"//*[@id='content_main_basicTable_{table_no}']/table/tbody/tr")

        self.rate_record[caption] = []

        for rate in rates_table[1:]:
            header = rate.xpath("./th/text()")[0]
            initial_interest_rate = rate.xpath("./td[1]//strong/text()")[0]
            follow_variable_rate = rate.xpath("./td[2]//strong/text()")[0]
            rate_period = rate.xpath("./td[3]//strong/text()")[0]
            ARPC = rate.xpath("./td[4]//strong/text()")[0]
            booking_fee = rate.xpath("./td[5]//text()")[0].replace("£", "")
            annual_overpayment_allowance = rate.xpath("./td[6]//text()")[0]
            cashback = rate.xpath("./td[7]//text()")[0].replace("£", "")
            max_loan = rate.xpath("./td[8]//text()")[0].replace("£", "")

            rate_detail = [insert_time, header, initial_interest_rate, follow_variable_rate, rate_period, ARPC,
                           booking_fee, annual_overpayment_allowance, cashback, max_loan]
            logger.info(f'HSBC UK RATE - {caption} \'s rate : {rate_detail}')

            self.rate_record[caption].append(rate_detail)

    def main(self):
        try:
            response = self.get_page()
            for i in range(1, 4):
                self.parse_data(response, i)

            logger.info("Start appending latest rates to google sheet...")
            for sheet_title in self.rate_record.keys():
                gsheet.append_gsheet(sheet_title, self.rate_record[sheet_title])
            logger.info("Finish appending latest rates to google sheet...")

            for option in self.rate_record:
                tg.send_message(f'{option} : {self.rate_record[option]}')

        except Exception as e:
            logger.error(f'Error - {e}')
            tg.send_message(e)


class SoniaSwaps:
    def __init__(self, gsheet: GSheet):
        self.sonia_swaps_url = "https://www.chathamfinancial.com/getrates/195403"
        self.headers = {
            "referer": "https://www.chathamfinancial.com/technology/european-market-rates",
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            "x-requested-with": "XMLHttpRequest"
        }
        self.sheet_title = "SONIA swaps"

    def get_data(self):
        logger.info("Starting to get the latest sonia swaps rate from chathamfinancial.com...")
        response = requests.get(self.sonia_swaps_url, headers=self.headers)
        return response.json()

    @staticmethod
    def parse_data(response):
        insert_time = get_date()

        record_date = response["PreviousDayDate"]
        updated_time = response["Updated"].replace(" | ", " ")

        sonia_swaps_rate = [insert_time, record_date, updated_time]

        for data in response["Rates"]:
            rate = data["PreviousDay"]
            sonia_swaps_rate.append(rate)

        logger.info(f'Latest sonia swaps rate : {sonia_swaps_rate}')
        return sonia_swaps_rate

    def main(self):
        try:
            response = self.get_data()
            sonia_swaps_rate = self.parse_data(response)

            logger.info("Start appending latest rates to google sheet...")
            gsheet.append_gsheet(self.sheet_title, sonia_swaps_rate)
            logger.info("Finish appending latest rates to google sheet...")
            tg.send_message(f'Latest sonia swaps rate : {sonia_swaps_rate}')
        except Exception as e:
            logger.error(f'Error - {e}')
            tg.send_message(e)


if __name__ == '__main__':
    gsheet = GSheet()
    hsbc_rate = HsbcRate(gsheet)
    sonia_swaps = SoniaSwaps(gsheet)
    tg = TelBot(logger)

    hsbc_rate.main()
    sonia_swaps.main()

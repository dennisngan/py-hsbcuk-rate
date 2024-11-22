import os.path
from datetime import datetime

import pygsheets
import requests
from loguru import logger
from lxml import etree
from pygsheets import Spreadsheet, Worksheet

from TelBot import TelBot


class HsbcRate:
    def __init__(self):
        log_path = os.path.dirname(__file__) + "/log"
        os.makedirs(log_path, exist_ok=True)
        logger.add(log_path + "/hsbc_rate.log", rotation="10 MB", encoding="utf-8")

        self.url = 'https://www.hsbc.co.uk/mortgages/buy-to-let/rates/'
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'referer': 'https://www.hsbc.co.uk/mortgages/buy-to-let/rates/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        }

        self.gs = pygsheets.authorize(service_file="credentials.json")
        self.gsheet_url = os.getenv("GSHEET_URL")
        self.record_date = None
        self.rate_record = {}

    def get_page(self):
        logger.info("Starting to get latest rate...")
        response = requests.get(self.url, headers=self.headers).content.decode("utf-8")
        return response

    def parse_data(self, response, table_no):

        record_date = datetime.now().strftime("%Y-%m-%d %H:%M")
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

            rate_detail = [record_date, header, initial_interest_rate, follow_variable_rate, rate_period, ARPC,
                           booking_fee, annual_overpayment_allowance, cashback, max_loan]
            logger.info(f'HSBC UK RATE - {caption} \'s rate : {rate_detail}')

            self.rate_record[caption].append(rate_detail)

    def connect_gsheet(self):
        return self.gs.open_by_url(self.gsheet_url)

    def append_gsheet(self, gsheet: Spreadsheet, sheet_title, values):
        sheet: Worksheet = gsheet.worksheet_by_title(sheet_title)
        sheet.append_table(values=values)

        end_address = self.get_last_address(
            sheet.get_all_values(include_tailing_empty=False, include_tailing_empty_rows=False)
        )

        sheet.set_basic_filter(start="A1", end=end_address)

    @staticmethod
    def get_last_address(all_values):
        end_address_row = len(all_values)
        end_address_col = len(all_values[0])
        return pygsheets.Cell((end_address_row, end_address_col)).label

    def main(self):
        try:
            response = self.get_page()
            for i in range(1, 4):
                self.parse_data(response, i)

            gsheet = self.connect_gsheet()

            logger.info("Start appending latest rates to google sheet...")
            for sheet_title in self.rate_record.keys():
                self.append_gsheet(gsheet, sheet_title, self.rate_record[sheet_title])
            logger.info("Finish appending latest rates to google sheet...")
            tg.send_message(f'Latest rates : {self.rate_record}')
        except Exception as e:
            logger.error(f'Error - {e}')
            tg.send_message(e)


if __name__ == '__main__':
    hsbc_rate = HsbcRate()
    tg = TelBot(logger)
    hsbc_rate.main()

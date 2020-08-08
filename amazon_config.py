from selenium import webdriver

DIRECTORY = 'reports'
NAME = 'PS4'
CURRENCY = '$'
MIN_PRICE = '200'
MAX_PRICE = '600'
FILTER = {
    'min': MIN_PRICE,
    'max': MAX_PRICE
}
BASE_URL = "http://www.amazon.ca/"


def get_chrome_web_driver(options):
    return webdriver.Chrome("./chromedriver.exe", chrome_options=options)


def get_chrom_options():
    return webdriver.ChromeOptions()


def set_ignore_certificate(options):
    options.add_argument('--ignore-certificate-errors')


def set_incognito(options):
    options.add_argument('--incognito')


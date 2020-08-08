from amazon_config import (
    get_chrome_web_driver,
    get_chrom_options,
    set_ignore_certificate,
    set_incognito,
    NAME, 
    BASE_URL,
    FILTER,
    DIRECTORY,
    CURRENCY,
)

from selenium.webdriver.common.keys import Keys
import time
from selenium.common.exceptions import NoSuchElementException
import json
from datetime import datetime

class AmazonAPI:
    def __init__(self, search_term, filters, base_url, currency):
        self.base_url = base_url
        options = get_chrom_options()
        set_ignore_certificate(options)
        set_incognito(options)
        self.search_term = search_term
        self.driver = get_chrome_web_driver(options)
        self.currency = currency
        self.price_filter = f"&rh=p_36%3A{filters['min']}00-{filters['max']}00"
    
    def run(self):
        print("Starting script....")
        print(f"Looking for {self.search_term} products...")
        links = self.get_product_links()
        print(f'got {len(links)} links to products')
        products = self.get_product_info(links)
        time.sleep(2)
        self.driver.quit()
        return products

    def get_product_links(self):
        self.driver.get(self.base_url)
        searchbar = self.driver.find_element_by_id('twotabsearchtextbox')   
        searchbar.send_keys(self.search_term)
        searchbar.send_keys(Keys.ENTER)
        self.driver.get(f'{self.driver.current_url}{self.price_filter}')
        result_list = self.driver.find_elements_by_class_name('s-search-results')
        
        links = []
        try:
            results = result_list[0].find_elements_by_xpath(
                "//div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a")
            links = [link.get_attribute('href') for link in results]
            print('got links ')
            return links
        except Exception as e:
            print("Didn't get any products...")
            print(e)
            return links

    def get_product_info(self, links):
        asins = self.get_asins(links)
        products = []
        for asin in asins:
           product = self.get_single_product_info(asin)
           if product:
               products.append(product)
        return products
    
    def get_single_product_info(self, asin):
        print(f'Product ID: {asin}. Getting product info...')
        product_short_url = self.shorten_url(asin)  
        self.driver.get(f'{product_short_url}')
        title = self.get_title()
        seller = self.get_seller()
        price = self.get_price()
        if(title and seller and price):
            product_info = {
                'asin': asin,
                'title' : title,
                'seller' : seller,
                'price': price,
                'url' : product_short_url
            }
            return product_info
    
    def get_price(self):
        price = None
        try:
            price = self.driver.find_element_by_id('priceblock_ourprice').text
            price = self.convert_price(price)
        except NoSuchElementException:
            try:
                availability = self.driver.find_element_by_id('availability').text
                if 'Available' in availability:
                    price = self.driver.find_element_by_class_name('olp-padding-right').text
                    price = price[price.find(self.currency):]
                    price = self.convert_price(price)
            except Exception as e:
                print(e)
                print(f"Can't get price of a product - {self.driver.current_url}")
                return None
        except Exception as e:
            print(e)
            print(f"Can't get price of a product - {self.driver.current_url}")
            return None
        return price

    def get_seller(self):
        return self.driver.find_element_by_id('bylineInfo').text

    def get_title(self):
        return self.driver.find_element_by_id('productTitle').text

    def shorten_url(self, asin):
        return self.base_url + 'dp/' + asin

    def get_asins(self, links):
        return [self.get_asin(link) for link in links]

    def get_asin(self, link):
        return link[link.find('/dp/')+4 : link.find('ref')]

    def convert_price(self, price):
        price = price.split(self.currency)[1]
        try:
            price = price.split("\n")[0] + "." + price.split("\n")[1]
        except:
            Exception()
        try:
            price = price.split(",")[0] + price.split(",")[1]
        except:
            Exception()
        return float(price)

class GenerateReport:
    def __init__(self,file_name, filters, base_url, currency, data):
        self.data = data
        self.filters = filters
        self.file_name = file_name
        self.currency = currency
        self.base_url = base_url
        report = {
            'title' : self.file_name, 
            'date' : self.get_now(),
            'best_item' : self.get_best_item(),
            'currency': self.currency,
            'filters': self.filters,
            'base_link': self.base_url,
            'products' : self.data
         }
        print('creating report...')
        with open(f'{DIRECTORY}/{file_name}.json', 'w') as f:
            json.dump(report, f)
        print('Done...')

    def get_now(self):
        now = datetime.now()
        return now.strftime("%d/%m/%Y %H:%M:%S")
    
    def get_best_item(self):
        try:
          return sorted(self.data, key=lambda k: k['price'])[0]
        except Exception as e:
            print(e)
            return None
     
if __name__ == '__main__':
    print('bruh')
    amazon = AmazonAPI(NAME, FILTER, BASE_URL, CURRENCY)
    print(amazon.price_filter)
    data = amazon.run()
    GenerateReport(NAME, FILTER, BASE_URL, CURRENCY, data)
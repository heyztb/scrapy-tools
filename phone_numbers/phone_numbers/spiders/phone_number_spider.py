import scrapy
import uuid
from pony.orm import Database, PrimaryKey, Required, db_session

db = Database()
db.bind(provider='sqlite', filename='../../../data.sqlite', create_db=True)


class PhoneNumber(db.Entity):
    id = PrimaryKey(uuid.UUID, default=uuid.uuid4)
    phone_number = Required(str)
    city = Required(str)
    state = Required(str)


db.generate_mapping(create_tables=True)


class PhoneSpider(scrapy.Spider):
    name = "phones"

    def create_url(self):
        try:
            city = getattr(self, 'city')
            url = f'https://randomphonenumbers.com/Generator/us_phone_number?state={self.state}&city={city}'
        except AttributeError:
            url = f'https://randomphonenumbers.com/Generator/us_phone_number?state={self.state}&city='

        return url

    def parse_location(self, location):
        try:
            city = location.split(',')[1].strip(
                ' ').replace('from', '').strip(' ')
            return city
        except Exception as e:
            print(e)

    def start_requests(self):
        url = self.create_url()
        yield scrapy.Request(url=url, callback=self.parse, headers={'User-Agent': 'Mozilla/5.0'})

    def parse(self, response):
        phone_numbers = response.xpath(
            '/html/body/div[1]/div[2]/div[1]//a/text()').getall()
        locations = response.xpath('//p[@class="des"]/text()').getall()

        for number, location in zip(phone_numbers, locations):
            city = self.parse_location(location)

            with db_session:
                PhoneNumber(phone_number=number, city=city, state=self.state)

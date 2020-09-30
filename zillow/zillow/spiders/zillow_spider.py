import scrapy
import uuid
from pony.orm import Database, PrimaryKey, Required, Optional, db_session

db = Database()
db.bind(provider='sqlite', filename='../../../data.sqlite', create_db=True)


class PropertyListing(db.Entity):
    id = PrimaryKey(uuid.UUID, default=uuid.uuid4)
    street_address = Required(str)
    city = Required(str)
    state = Required(str)
    zip_code = Required(str)
    # listings apparently can be made without a price explicitly listed? make this optional to avoid errors
    price = Optional(str)


db.generate_mapping(create_tables=True)


# usage: scrapy crawl zillow -a zipcode={zipcode}
class ZillowSpider(scrapy.Spider):
    name = "zillow"

    def create_url(self):
        url = "https://www.zillow.com/homes/for_sale/{0}_rb/?fromHomePage=true&shouldFireSellPageImplicitClaimGA=false&fromHomePageTab=buy".format(
            self.zipcode)
        return url

    def parse_address(self, address):
        try:
            address = address.split(', ')
            street_address = address[0]
            city = address[1]
            state_and_zip = address[2].split()
            state = state_and_zip[0]
            zip_code = state_and_zip[1]
            return [street_address, city, state, zip_code]
        except IndexError:
            # if we encounter a listing that for whatever reason is formatted in a manner we aren't expecting, just skip it
            pass

    def start_requests(self):
        url = self.create_url()
        yield scrapy.Request(url=url, callback=self.parse, headers={'User-Agent': 'Mozilla/5.0'})

    def parse(self, response):
        listing_cards = response.xpath("//*/div[@class='list-card-info']")
        # to keep pylance from complaining about a potentially unbound variable
        addressList = []
        priceList = []
        for card in listing_cards:
            addressList = card.xpath("//address/text()").getall()
            priceList = card.xpath(
                "//div[@class='list-card-price']/text()").getall()

        for address, price in zip(addressList, priceList):
            address = self.parse_address(address)

            # some listings, particularly those for building plans on lots in unfinished housing developments (i.e those without a mailing address), will cause the parse_address method to error as it of course is expecting a properly formatted mailing address -- check that address != none and continue
            if address is not None:
                with db_session:
                    PropertyListing(
                        street_address=address[0], city=address[1], state=address[2], zip_code=address[3], price=price)
            else:
                # if it turns out we got a bad address, then just skip this
                pass

        next_page = response.xpath(
            "//a[@title='Next page']/@href").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(url=next_page, callback=self.parse, headers={'User-Agent': 'Mozilla/5.0'})

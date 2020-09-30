### Scrapy Tools

Just a few scrapy spiders. Currently, I've got a spider for Zillow (pls no lawsuit) as well as randomphonenumbers.com.

Usage is pretty simple.

1. If you don't have a virtual environment with scrapy installed, do so with `python3 -m venv <virtualenv-name-here> && pip install scrapy`
2. `cd` into the appropriate directory for the spider you want to use
3. `scrapy crawl zillow -a zipcode=<zipcode>` OR `scrapy crawl phones -a state=WA [-a city=Seattle]`
4. Browse the data you just scraped by opening the `data.sqlite` file that's been created at the root of the repository

In the future I intend to create more spiders as I find websites that offer up interesting or useful data.

import scrapy
from scrapy_playwright.page import PageMethod

class AmazonspiderSpider(scrapy.Spider):
    name = "amazonspider"

    async def start(self):
        yield scrapy.Request(url="https://www.amazon.com/s?k=wireless+mouse&page=1&crid=43RV9567KF7C&qid=1766867260&sprefix=wireless+mouse%2Caps%2C259&xpid=kB1BLP41LOMRX&ref=sr_pg_1", callback=self.parse,
                             meta=dict(
                                 playwright = True,
                                 playwright_include_page = True,
                                 playwright_page_method = {
                                     PageMethod("wait_for_selector", "div[role='listitem']")
                                 }
                             )
                            )

    async def parse(self, response):
        mouses = response.css('div[role="listitem"]')
        page = response.meta['playwright_page']
        await page.close()
        for mouse in mouses:
            try:
                price = mouse.css('span[class="a-price"] span::text').get().strip()
            except:
                price = 'N/A'

            try:
                title = mouse.css('h2.a-size-medium::attr(aria-label)').get().strip()
            except:
                continue

            yield {
                "title": title,
                "price": price,
                "rating": mouse.css('span.a-size-small::text').get().strip(),
                "link": response.urljoin(mouse.css('a[class="a-link-normal s-line-clamp-2 s-line-clamp-3-for-col-12 s-link-style a-text-normal"]::attr(href)').get()),
            }
        next_page = response.css('span[class="a-list-item"] a.s-pagination-next::attr(href)').get()
        if next_page is not 1:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url,
                                    meta=dict(
                                    playwright = True,
                                    playwright_include_page = True,
                                    playwright_page_method = {
                                        PageMethod("wait_for_selector", "div[role='listitem']")
                                    }),
                                    callback=self.parse)
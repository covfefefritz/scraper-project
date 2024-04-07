import scrapy
import json
from fin_scraper.items import FinScraperItem
from datetime import date

class NewsSpider(scrapy.Spider):
    name = "news"
    start_urls = [
                  'https://www.zerohedge.com/', 
                  'https://www.cnbc.com/world/',
                  'https://www.cnbc.com/personal-finance/',
                  'https://www.cnbc.com/investing/',
                  'https://www.cnbc.com/economy/',
                  'https://www.cnbc.com/finance/',
                  'https://www.ft.com/'
                  ]

    def parse(self, response):
        if 'zerohedge.com' in response.url:
            # Find all the article links on the landing page for ZeroHedge
            article_links = response.css('h2.Article_lineClamp__yljIN a::attr(href)').getall()
            for link in article_links:
                # Use response.follow to handle relative URLs automatically
                yield response.follow(link, self.parse_zerohedge)
        elif 'cnbc.com' in response.url:
            # Find all the article links on the landing page for CNBC
            article_links = response.css('div.RiverHeadline-headline a::attr(href)').getall()
            card_links = response.css('div.Card-titleContainer a::attr(href)').getall()
            for link in article_links:
                # Use response.follow to handle relative URLs automatically
                yield response.follow(link, self.parse_cnbc)

            for link in card_links:
                # Use response.follow to handle relative URLs automatically
                yield response.follow(link, self.parse_cnbc)

        elif 'ft.com' in response.url:
            article_links = response.css('div.story-group__item a.link::attr(href)').getall()
            for link in article_links:
                # Use response.follow to handle relative URLs automatically
                yield response.follow(link, self.parse_ft)


    def parse_ft(self, response):
        # Initialize an empty string to hold the article text
        article_text = ''
        
        # Select all the paragraph tags within the article body div
        paragraphs = response.css('div.js-article__body p')
        
        # Loop through the paragraphs and concatenate their text to the article_text string
        for p in paragraphs:
            # Extract the text from each paragraph, stripping leading/trailing whitespace
            paragraph_text = p.css('::text').get().strip()
            article_text += paragraph_text + ' '

        # Here you could do further processing, cleaning, or yield the data as an item
        # For example, to yield the article text as part of a Scrapy item:
        item = FinScraperItem()
        item['article_text'] = article_text
        item['collection_date'] = date.today()
        yield item

    def parse_cnbc(self, response):
        # Initialize an empty string to hold the article text
        article_text = ''
        
        # Select all the paragraph tags within the article body div
        paragraphs = response.css('div.ArticleBody-articleBody p')
        title = response.css('h1.ArticleHeader-headline::text').get()

        # Loop through the paragraphs and concatenate their text to the article_text string
        for p in paragraphs:
            # Extract the text from each paragraph, stripping leading/trailing whitespace
            paragraph_text = p.css('::text').get().strip()
            article_text += paragraph_text + ' '

        # Here you could do further processing, cleaning, or yield the data as an item
        # For example, to yield the article text as part of a Scrapy item:
        item = FinScraperItem()
        item['article_text'] = article_text
        item['title'] = title
        item['collection_date'] = date.today()
        yield item


    def parse_zerohedge(self, response):
        # This is your existing parse method for a single article
        try:
            json_string = response.xpath("//script[@id='__NEXT_DATA__']/text()").get()
            data = json.loads(json_string)

            # Assuming the path to the article data is correct
            article_data = data['props']['pageProps']['node']

            item = FinScraperItem()
            item['title'] = article_data.get('title')
            item['author'] = article_data.get('author')
            item['collection_date'] = date.today()

            # Ensure you use the correct key for the article text
            article_text_key = 'body'  # Replace with the actual key if different
            if article_text_key in article_data:
                item['article_text'] = article_data[article_text_key]
            else:
                self.logger.error(f"Key {article_text_key} not found in article_data.")
                return

            yield item
            
        except Exception as e:
            self.logger.error(f"Error processing the response: {e}")
            self.logger.error('Traceback:', exc_info=True)
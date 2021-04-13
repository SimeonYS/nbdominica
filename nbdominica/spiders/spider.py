import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import NnbdominicaItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class NnbdominicaSpider(scrapy.Spider):
	name = 'nbdominica'
	start_urls = ['https://online.nbdominica.com/news/']

	def parse(self, response):
		articles = response.xpath('//header[@class="article-header"]')
		for article in articles:
			date = article.xpath('.//time/text()').get()
			post_links = article.xpath('.//a[@rel="bookmark"]/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

		next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()|//h2/text()').get()
		content = response.xpath('//div[@class="elementor-element elementor-element-51f624f4 elementor-widget elementor-widget-theme-post-content"]/div[@class="elementor-widget-container"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=NnbdominicaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()

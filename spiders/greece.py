# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item

class DogSpider(CrawlSpider):
    name = 'greece'
    allowed_domains = ['cnn.gr',
                    'reader.gr',
                    'thetoc.gr',
                    'protagon.gr',
                    'periodista.gr',
                    'in.gr',
                    'newpost.gr',
                    ]
    start_urls = [
                'http://www.periodista.gr/',
                'https://www.cnn.gr/',
                'https://www.reader.gr/news/koinonia',
                'https://www.thetoc.gr/',
                'https://www.protagon.gr/epikairotita/ellada',
                'https://www.in.gr/greece/',
                'https://newpost.gr/ellada/',
                ]

    rules = (
        Rule(LinkExtractor(allow=('periodista.gr/koinwnia'), deny=()), callback='parseInfinitePeriodista', follow=True), 
        Rule(LinkExtractor(allow=('thetoc.gr/koinwnia')), callback='parseItemThetoc', follow=True),
        Rule(LinkExtractor(allow=('cnn.gr/news/ellada'), deny=('cnn.gr/news/ellada/gallery/','protoselida')), callback='parseItemCnn', follow=True),
        Rule(LinkExtractor(allow=('reader.gr/news/koinonia'), deny=('vid')), callback='parseItemReader', follow=True), 
        Rule(LinkExtractor(allow=('protagon.gr/epikairotita/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemProtagon', follow=True),
        Rule(LinkExtractor(allow=(r".in\.gr.+greece"), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemIn', follow=True),
        Rule(LinkExtractor(allow=('newpost.gr/ellada'), deny=()), callback='parseInfiniteNewpost', follow=True), 
    )

    def parseItemCnn(self,response):
        title = response.xpath('//h1[@class="story-title"]/text()').get() 
        text = response.xpath('//div[@class="story-content"]//p/*/text()|//div[@class="story-content"]//p/text()|//div[@class="story-content"]//p/a/*/text()').getall()
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        clearcharacters = re.sub( "\xa0","",finaltext)
        url = response.url
        if title is not None:
            yield {
                "subtopic": "Greece",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": title,
                "date": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get()),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                "text": re.sub( r'\n|\t',"",clearcharacters),
                "url": url,                
            }

    def parseItemReader(self,response):
        title = response.xpath('//h1/text()').get() 
        text = response.xpath('//div[@class="article-summary"]//p/text()|//div[@class="article-body"]//p/text()|//div[@class="article-body"]//p/*/text()').getall()
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        clearcharacters = re.sub( "\xa0","",finaltext)
        author = response.xpath('//p[@class="article-author"]/a/text()').get()
        if author is not None:
            author = re.sub("\xa0","",author)
        else:
            author = "Reader"
        url = response.url
        if title is not None:
            yield {
                "subtopic": "Society",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": re.sub( r'\n|\t',"",title),
                "date": re.sub( r'\n|\t',"",response.xpath('//time/text()').get()),
                "author": author,
                "text": re.sub( r'\n|\t',"",clearcharacters),
                "url": url,              
            }
            
    def parseItemThetoc(self,response):
        title = response.xpath('//div[@class="article-title"]//h1/text()').get() 
        text = response.xpath('//div[@class="article-content articleText"]//p/text()|//div[@class="article-content articleText"]//strong/text()|//div[@class="article-content articleText"]//p/*/text()').getall()
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        clearcharacters = re.sub( "\xa0","",finaltext)
        url = response.url
        if title is not None and len(clearcharacters)>10:
            yield {
                "subtopic": "Society",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": title,
                "date": " ".join(re.findall(r"[0-9]+.[α-ωΑ-Ω]+\..[0-9]+",response.xpath('//span[@class="article-date"]/text()').get())),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="author-social"]//h5/a/span[2]/text()').get()),
                "text": re.sub( r'\n|\t',"",clearcharacters),
                "url": url,                
            }

    def parseItemProtagon(self,response):
        sub = response.xpath('//span[@class="s_roumpr"]/a/text()').get()
        if sub == "Greece":
            title = response.xpath('//h1[@class="entry-title"]/text()').get() 
            text = response.xpath('//div[@class="left-single-column "]//p/text()|//div[@class="left-single-column "]//strong/text()|//div[@class="left-single-column "]//p/*/text()').getall()
            listtostring = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",listtostring)
            uneededspaces = re.sub( " ", "",markspaces)
            finaltext = re.sub( "space", " ",uneededspaces)
            clearcharacters = re.sub( "\xa0","",finaltext)
            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clearcharacters)
            url = response.url
            author = re.findall(r"(\w+).(\w+)",response.xpath('//strong[@class="generalbold uppercase"]/a/text()').get())
            #from list to tuple to string
            author = author[0]
            author = ' '.join(author)
            date = re.findall(r"(\d+).(\w+).(\d+)",response.xpath('//span[@class="generalight uppercase"]/text()').get())
            date = date[0]
            date = ' '.join(date)
            #check if we are in an article, and if it doesn't have images
            if title is not None and len(clearcharacters)>10 and flag is None:
                yield {
                    "subtopic": sub,
                    "website": re.search(r"www.+\.gr",url).group(0),
                    "title": title,
                    "date": date, 
                    "author": author,
                    "text": re.sub( r'\s\s\s',"",clearcharacters),
                    "url": url,                
                }

    def parseInfinitePeriodista(self,response):
        pages =  450
        for page in range(0 ,pages , 30):
            url = 'http://www.periodista.gr/koinwnia?start={}'.format(page)
            yield Request(url, callback = self.parseItemPeriodista) 

    def parseItemPeriodista(self,response):
        links = response.xpath('//h2[@itemprop="headline"]/a/@href').getall()
        for link in links:
            url = response.urljoin(link)
            yield Request(url,callback=self.parseItem) 

            
    def parseItem(self,response):
        title = response.xpath('//h1[@itemprop="headline"]/text()').get() 
        text = response.xpath('//div[@class="per-item-page-part per-article-body"]//p/text()|//div[@class="per-item-page-part per-article-body"]//strong/text()|//div[@class="per-item-page-part per-article-body"]//p/*/text()').getall()
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        clearcharacters = re.sub( "\xa0","",finaltext)
        url = response.url
        #flag to see later on if we have videos
        flag = re.search(r"binteo|foto",url)
        #check if we are in an article, and if it doesn't have videos
        if title is not None and len(clearcharacters)>10 and flag is None:
            yield {
                "subtopic": "Society",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": re.sub( r'\t|\n|\r',"",title),
                "date": re.sub(r'\t|\n|\r',"",response.xpath('//div[@class="col-md-4 per-color-grey per-font-size-md per-padding-top-20"]/text()').get()), 
                "author": "Periodista",
                "text": re.sub( r'\s\s\s',"",clearcharacters),
                "url": url,                
            }
    def parseItemIn(self,response):
        title = response.xpath('//h1[@class="entry-title black-c"]/text()').get() 
        text = response.xpath('//div[@class="main-content pos-rel article-wrapper"]//p/text()|//div[@class="main-content pos-rel article-wrapper"]//strong/text()|//div[@class="main-content pos-rel article-wrapper"]//p/*/text()').getall()
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        clearcharacters = re.sub( "\xa0","",finaltext)
        #flag to see later on if we have tweets ect
        flag = re.search(r"@",clearcharacters)
        url = response.url
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(clearcharacters)>10 and flag is None:
            yield {
                "subtopic": "Greece",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": title,
                "date": response.xpath('//time/text()').get(), 
                "author": response.xpath('//span[@class="vcard author"]//a/text()').get(),
                "text": re.sub( r'\s\s\s',"",clearcharacters),
                "url": url,                
            }
#next three functions for newpost.gr
    def parseInfiniteNewpost(self,response):
        pages =  18708
        for page in range(1 ,pages):
            url = 'http://www.newpost.gr/ellada?page={}'.format(page)
            yield Request(url, callback = self.parseItemNewpost) 

    def parseItemNewpost(self,response):
        links = response.xpath('//h2[@class="cp-title"]/a/@href').getall()
        for link in links:
            url = response.urljoin(link)
            yield Request(url,callback=self.parseNewpost) 

            
    def parseNewpost(self,response):
        title = response.xpath('//h1[@class="article-title"]/text()').get() 
        text = response.xpath('//div[@class="article-main clearfix"]//p/text()|//div[@class="article-main clearfix"]//strong/text()|//div[@class="article-main clearfix"]//p/*/text()').getall()
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        clearcharacters = re.sub( "\xa0","",finaltext)
        #flag to see later on if we have tweets ect
        flag = re.search(r"@",clearcharacters)
        url = response.url
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(clearcharacters)>10 and flag is None:
            yield {
                "subtopic": "Greece",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": title,
                "date": (response.xpath('//small[@class="article-created-time"]/text()').get()).split('/')[0], 
                "author": "Newpost.gr",
                "text": re.sub( r'\s\s\s',"",clearcharacters),
                "url": url,                
           }
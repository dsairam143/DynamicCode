'''
Find Article Main urls and extract data from each url
'''

import re
from collections import defaultdict
import dateutil.parser as dparser
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import extruct
from datetime import datetime
import pandas as pd


today = datetime.today()

class ArticlesXpaths():
    '''
    Find all Articles xpaths and their data.
    '''

    @staticmethod
    def find_news_links(url):
        resp = requests.get(url)
        jsoup = BeautifulSoup(resp.content)
        url_list = []
        for k in jsoup.find_all('a', text=re.compile('news|press', re.IGNORECASE)):
            if 'href' in k.attrs:
                link = k['href']
                if link[0]=='/':
                    link = url+link
                url_list.append(link)
        return list(set(url_list))

    @staticmethod
    def get_all_classes(domain):
        '''
        :param class_filters: Loads all html tags with class attributes
        :param domain: Domain Url
        :return: classFilter Data
        '''
        # self.domain = 'https://www.apple.com'
        resp = requests.get(domain)
        jsoup = BeautifulSoup(resp.content)
        body = jsoup.find('body')
        chils = body.descendants
        class_filters = []
        for c_h in list(chils)[::-1]:
            if c_h.name and  c_h.name != 'script':
                check_attributes = ['class']
                for c_a in check_attributes:
                    if c_a in c_h.attrs:
                        class_filters.append(c_h)
                        break

        return class_filters

    @staticmethod
    def pickmore_common_classes(mainData):
        '''
        :param main_list: Stores All Repeated classes i.e more than 5times
        :return:
        '''
        main_list = []
        filter_list = []
        for id, k in enumerate(mainData):
            if len(k[1]) >= 5:
                main_list.append(k)
                filter_list.append(k)
                # print(k[0], len(k[1]))
        found_indexes = []
        for mid, mlv in enumerate(main_list):
            classname = mlv[0]
            for fid, flv in enumerate(filter_list):
                if mid == fid:
                    continue
                found = False
                for k in flv[1][0].descendants:
                    try:
                        if classname == ' '.join(k.attrs['class']):
                            found_indexes.append(mid)
                            found = True
                    except Exception as e:
                        pass
                if found:
                    break

        return [k for id, k in enumerate(main_list) if id not in found_indexes]

    @staticmethod
    def find_dates_available_tags(common_classes):
        '''
        This method is used to find date available tags
        :param date_filter_list: It stores all date tags
        :return:
        '''
        date_filter_list = []
        for k in common_classes[1:]:

            date_count = 0
            for l in k[1]:
                content = l.text
                newdate = re.search(r'[a-zA-Z\.]* \d?\d, \d{4}|\d{4}[-\.]\d\d[-\.]\d\d|\d\d?[-\/.]\d\d?[-\/.]\d{4}|[a-zA-Z]* \d\d?, [a-zA-Z]* \d{4}|\d\d? [a-zA-Z]*  ?\d{4}|[a-zA-Z]* \d\d?, \d{4}|\d\d?/\d\d?/\d\d?', content)
                newdate = newdate.group(0) if newdate else newdate
                # print(newdate)
                if not newdate:
                    try:
                        newdate = dparser.parse(content, fuzzy=True).strftime('%m-%d-%Y')
                    except:
                        newdate = None
                if newdate:
                    date_count += 1
            if date_count >= 3:
                # print('date = ', date_count)
                date_filter_list.append([date_count, k[1]])
        date_filter_list.sort(key=lambda x: x[0], reverse=True)

        return date_filter_list
        # print(self.date_filter_list)

    @staticmethod
    def group_all_classes(class_data):
        '''
        :param mainData: Stores All grouped Data
        :return:
        '''
        dict_marks = defaultdict(list)
        for key, value in class_data:
            dict_marks[key].append(value)

        return list(dict_marks.items())

    @staticmethod
    def get_class_names_and_tags(class_filters):
        '''
        Make Dictionary class name is key and tags are values.
        :param class_data: Stores data in tuple format (key, tagsData)
        :return:
        '''
        class_data = []
        for cf in class_filters:
            class_name = ' '.join(cf.attrs['class'])
            class_data.append((class_name, cf))
        return class_data

    @staticmethod
    def extract_date_article_urls(url, domain):
        '''
        Extract all Article urls
        :param final_articles_data: Stores all article urls.
        :return:
        '''

        class_filters = ArticlesXpaths.get_all_classes(url)
        class_data = ArticlesXpaths.get_class_names_and_tags(class_filters)
        grouped_classes = ArticlesXpaths.group_all_classes(class_data)
        common_classes = ArticlesXpaths.pickmore_common_classes(grouped_classes)
        date_filter_list = ArticlesXpaths.find_dates_available_tags(common_classes)

        if date_filter_list:

            final_articles_data = []
            final_articles = date_filter_list[0]
            for fa in final_articles[1]:
                final_articles_data.extend([(domain + k['href'] if k['href'][0] =='/' else k['href']) for k in fa.find_all('a') if 'href' in k.attrs])
            return list(set(final_articles_data))
        else:
            return None


    def getMetaDataContent(self, content):

        try:
            jsoup = BeautifulSoup(content)
            metas = [k.attrs for k in jsoup.find_all('meta')]
            self.finalResult['metaData'] = metas

        except:
            pass

        try:
            data = extruct.extract(content)
            self.finalResult['jsonId'] = data
        except:
            self.finalResult['jsonId'] = None

        try:
            metaList = metas
            Title = None
            TitleFound = None
            Description = None
            DescriptionFound = None
            DateFound = None
            Date_ = None
            author = None
            authorFound = None
            # image = None
            imageFound = None
            subImage = None
            if metaList:
                for k in metaList:
                    for i in k.items():

                        if 'title' in i[1].lower():
                            Title = k.get('content', '')
                            if len(Title) > 5 and not TitleFound:
                                TitleFound = True
                        if 'description' in i[1].lower():
                            Description = k.get('content', '')
                            if len(Description) > 5 and not DescriptionFound:
                                DescriptionFound = True
                        if 'datep' in i[1].lower():
                            Date_ = k.get('content', '')
                            if len(Date_) > 5 and not DateFound:
                                DateFound = True
                        if 'author' in i[1].lower():
                            author = k.get('content', '')
                            if len(author) > 5 and not authorFound:
                                authorFound = True
                        if 'image' in i[1].lower():
                            image = k.get('content', '') if 'http' in k.get('content', '') else ''
                            if 'http' in image and (not imageFound):
                                imageFound = True
                                subImage = image

            ArticleData = {'Title': Title, 'Author': author, 'Description': Description, 'PublishedDate': Date_, 'image_url':subImage}
            self.finalResult['ArticleData'] = ArticleData
        except Exception as e:
            print(e)
            self.finalResult['ArticleData'] = None

    def articl_data(self, url):
        self.finalResult = dict()

        self.finalResult['CompanyUrl'] = url
        article = Article(url)
        article.download()
        self.getMetaDataContent(article.html)
        article.parse()

        self.finalResult['body_content'] = re.sub(r'[^\x00-\x7F]', '',
                                                  re.sub(' +', ' ', ' '.join(article.text).replace('\n', ' '))) \
            if article.text else None

        self.finalResult['publish_date'] = article.publish_date
        self.finalResult['Title'] = re.sub(r'[^\x00-\x7F]', '',
                                                  re.sub(' +', ' ',  article.title.replace('\n', ' '))) \
            if article.title else None
        # article.nlp()
        self.finalResult['tags'] = article.keywords

        return self.finalResult



domain = 'https://www.jnj.com/'.strip('/')
article = ArticlesXpaths()
links = article.find_news_links(domain)
finalResult = []
for news_url in links:
    print(news_url)
    articles_urls = article.extract_date_article_urls(news_url, domain)
    for article_url in articles_urls:
        print(article_url)
        data = article.articl_data(article_url)
        if not data:
            continue
        print(data)

        company_name = re.search('\.[\w\d]+\.', domain)
        if company_name:
            company_name = company_name.group(0).strip('.')

        company_url = domain
        news_url = news_url
        article_url = article_url
        title = data['Title']
        published_date = data['publish_date']
        if not published_date:
            published_date = data.get('ArticleData', {}).get('PublishedDate')
            if not published_date:
                date = data.get('jsonId', {}).get('json-ld', '')
                date = str(date)
                date = re.search('datePublished.*', date)
                date = re.search(':[\W]+([^\'\"]+)', date.group(0)) if date else date
                published_date = date.group(1).strip('Z') if date else date


        description = data.get('ArticleData', {}).get('Description')
        summary = data.get('body_content')
        tags = data.get('tags')
        author = data.get('ArticleData', {}).get('Author')
        if author:
            if len(author)>30:
                author = None
        image_url = data.get('ArticleData',{}).get('image_url')


        result = {'Date':today, 'Company_Name':company_name, 'Company_Url':company_url,
                  'News_Url':news_url, 'Article_Url':article_url,
                  'Title':title, 'Published_Date':published_date, 'Description':description,
                  'Summary':summary, 'Tags':tags, 'Author':author, 'Image_Url':image_url}

        if result.get('Published_Date'):
            finalResult.append(result)

        # print('Final Data = ', data)
    #     break
    # break


df = pd.DataFrame(finalResult)
order = ["Date", "Company_Name", "Company_Url", "News_Url", "Article_Url", "Title", "Published_Date",
         "Author", "Description", "Summary", "Tags", "Image_Url"]
df = df[order]

writer = pd.ExcelWriter(r'file.xlsx', engine='xlsxwriter',options={'strings_to_urls': False})
df.to_excel(writer, index=False)
writer.close()


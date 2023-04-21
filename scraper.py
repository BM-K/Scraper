import re
import requests as rq
from bs4 import BeautifulSoup

class JtbcScraper():
    # Initialization function
    def __init__(self, args, config):
        self.args = args
        self.last_checker = False
        self.last_file_name = config['Last_file_name']

        self.parser = 'lxml'

        self.base_url = "https://news.jtbc.co.kr/"
        self.banner_url = "section/list.aspx?scode="
        self.banner_copy_selector = "#section_list"

        self.cur_news_copy_selector = "dl > dt > a"
        self.inner_copy_selector = "#articlebody > div:nth-child(1)"

        self.writer_copy_selector = "dl > dd.info > span.writer"
        self.date_copy_selector = "dl > dd.info > span.date"
        self.category_copy_selector = "dl > dd.info > span.location"
        self.unnecessary_content_copy_selector = "div > img"

        self.vision_copy_selector = "div.html_photo_center > img"
        self.email_copy_selector = "dd.sns > a"

        self.scraping_data = dict()
        self.replace_email_dummy = "mailto:"
        self.contents_split_tag = "     "

    # Access the [Breaking News] page and parse the HTML
    def banner_xml_parsing(self
    ):
        response = rq.get(self.base_url + self.banner_url)
        soup = BeautifulSoup(response.content, self.parser)

        return soup.select_one(self.banner_copy_selector)

    # Access the article's detail page and parse the HTML
    def inner_xml_parsing(self,
                          href=None
    ):
        response = rq.get(self.base_url + href)
        soup = BeautifulSoup(response.content, self.parser)

        return soup.select_one(self.inner_copy_selector)

    # Perform validation checks for each value
    def checking_value(self,
                       value=None,
                       task_name=None
    ):
        if task_name == 'writer':
            if value == '': return 'None'
            value = value.split(' ')[0]

        elif task_name == 'date':
            pass
            #if value == self.last_file_name: self.last_checker = True

        elif task_name == 'category':
            value = value.split()[-2]

        return value

    # Extract the article's title, link, author, and date information
    def get_metadata(self,
                     parm=None,
                     tags=None
    ):
        writer = self.checking_value(tags.select_one(self.writer_copy_selector).text.strip(),
                                     task_name='writer')
        date = self.checking_value(tags.select_one(self.date_copy_selector).text.strip().replace(' ', ''),
                                   task_name='date')
        category = self.checking_value(tags.select_one(self.category_copy_selector).text.strip(),
                                       task_name='category')
        title, href = parm.text.strip(), parm['href']
        
        if title == self.last_file_name: self.last_checker = True

        return title, href, writer, date, category

    # Extract the article's image URL
    def scrape_vision(self,
                      xml=None
    ):
        try:
            vision_url = xml.select_one(self.vision_copy_selector )['src']
        except TypeError:
            # JTBC does not grant permission to scrape video files.
            vision_url = 'None'

        return vision_url

    # Extract the article's content
    def scrape_content(self,
                       xml=None
    ):
        # 필요없는 사진 글귀 길이 탐색 후 main contents에서 slice., 글귀가 단어일 경우 replace로 하면 다 삭제됨.
        try:
            unnecessary_content = xml.select_one(self.unnecessary_content_copy_selector)['alt']
            len_unnecessary_content = len(unnecessary_content)

            if unnecessary_content == xml.text.strip()[:len_unnecessary_content]:
                len_unnecessary_content = len(unnecessary_content)
                contents = xml.text.strip()[len_unnecessary_content:].strip()
                return '<br>'.join(contents.split(self.contents_split_tag))
            else:
                contents = xml.text.strip()
                return '<br>'.join(contents.split(self.contents_split_tag))
        except TypeError:
            contents = xml.text.strip()
            return '<br>'.join(contents.split(self.contents_split_tag))

    # Extract the writer's email
    def scrape_email(self,
                     href=None
    ):
        response = rq.get(self.base_url + href)
        soup = BeautifulSoup(response.content, self.parser)

        try:
            low_email = soup.select_one(self.email_copy_selector)['href']
        except TypeError:
            return 'None'

        return low_email.replace(self.replace_email_dummy, '')

    # Extract the article's image and content
    def get_inner_data(self,
                       href=None
    ):
        inner_xml = self.inner_xml_parsing(href)

        vision = self.scrape_vision(inner_xml)
        contents = clean_contents(self.scrape_content(inner_xml))
        writer_email = self.scrape_email(href)

        return vision, contents, writer_email

    # Extract the entire information of the article
    def get_info(self,
                 tags=None
    ):
        try:
            news_parm = tags.select_one(self.cur_news_copy_selector)
            news_title, news_href, news_writer, news_date, news_category = self.get_metadata(news_parm, tags)

            if self.last_checker: return 0
            vision, contents, writer_email = self.get_inner_data(news_href)

            info = {'date': news_date,
                    'category': news_category,
                    'title': news_title,
                    'writer': news_writer,
                    'writer_email': writer_email,
                    'vision': vision,
                    'contents': contents}

            return info

        except AttributeError:
            return 1

    # Run the scraping operation and return the extracted data
    def run(self):
        banner_xml = self.banner_xml_parsing()

        # [속보]에 있는 각 뉴스 타이틀에 접근
        for index, tags in enumerate(banner_xml):
            information = self.get_info(tags)

            if type(information) != int:
                self.scraping_data[str(information['title'])] = information

            if information == 0: break

        return self.scraping_data

class SbsScraper():
    # Initialization function
    def __init__(self, args, config):
        self.args = args
        self.last_checker = False
        self.last_file_name = config['Last_file_name']

        self.parser = 'lxml'

        self.base_url = "https://news.sbs.co.kr/"
        self.banner_url = "news/newsflash.do?plink=NEW&cooper=SBSNEWSMAIN"
        self.banner_copy_selector = "div > div.w_news_list.type_issue > ul"

        self.cur_news_copy_selector = "a"
        self.inner_copy_selector = "div.article_cont_area"

        self.writer_copy_selector = "em.name"
        self.writer_dummy = ["북한전문", "의학전문", "환경전문", "문화전문", "국방전문"]
        self.date_copy_selector = "span.date"

        self.content_copy_selector = "div.main_text"
        # contents의 맨 마지막 줄 -> (사진 = ~~~) 제거용
        self.dummy_content = "("

        self.vision_copy_selector_mainimg = "img.mainimg"
        self.vision_copy_selector_lazy = "img.lazy"
        self.video_copy_selector = "div.movie_area"

        self.email_copy_selector = "a.email_v2"
        self.category_copy_selector = "li.cate03"

        self.scraping_data = dict()
        self.replace_email_dummy = "mailto:"
        self.contents_split_tag = " \n  \n "

    # Access the [Breaking News] page and parse the HTML
    def banner_xml_parsing(self
    ):
        response = rq.get(self.base_url + self.banner_url)
        soup = BeautifulSoup(response.content, self.parser)

        return soup.select_one(self.banner_copy_selector)

    # Access the article's detail page and parse the HTML
    def inner_xml_parsing(self,
                          href=None
    ):
        response = rq.get(self.base_url + href)
        soup = BeautifulSoup(response.content, self.parser)

        return soup.select_one(self.inner_copy_selector)

    # Perform validation checks for each value
    def checking_value(self,
                       value=None,
                       task_name=None
    ):
        if task_name == 'writer':
            if value == None: return 'None'

            value = value.text.strip().split()
            index_of_dummy = [idx for idx, dm in enumerate(self.writer_dummy) if value[-1].replace('기자', '') == dm]

            if len(index_of_dummy) > 0 :
                value[-1] = value[-1].replace(self.writer_dummy[index_of_dummy[0]])

            try:
                try:
                    reporter_index = value.index('기자')
                except:
                    reporter_index = value.index('에디터')

                value = value[reporter_index - 1]
                # 이름 2개 잡히는 것 ex) 박규리,최희진 | PD,최희진
                value = value.split(',')[-1]

            except:
                # '기자'도 '에디터'도 없다면 ex) UBC 배윤주, JTV
                # [SBS, |, JTV, 강훈]
                if len(value) == 4: value = value[-1]
                else: value = 'None'

        elif task_name == 'date':
            pass
            #if value == self.last_file_name: self.last_checker = True

        return value

    # Extract the article's title, link, author, and date information
    def get_metadata(self,
                     parm=None,
                     tags=None
    ):
        writer = self.checking_value(tags.select_one(self.writer_copy_selector),
                                     task_name='writer')
        date = self.checking_value(tags.select_one(self.date_copy_selector).text.replace(' ', '_'),
                                   task_name='date')

        title = parm['title'].strip()
        href = parm['href']
        
        if title == self.last_file_name: self.last_checker = True

        return title, href, writer, date

    # Extract the article's image URL
    def scrape_vision(self,
                      xml=None
    ):
        # SBS does not grant permission to scrape video files.
        isVideo = xml.select_one(self.video_copy_selector) != None

        if not isVideo:
            try:
                dummy_vision_url = xml.select_one(self.vision_copy_selector_mainimg)['onerror']
                slice_index = dummy_vision_url.find('"')
                vision_url = dummy_vision_url[slice_index+1:-1]
            except TypeError:
                vision_url = xml.select_one(self.vision_copy_selector_lazy)['data-src']
        else:
            vision_url = 'None'

        return vision_url

    # Extract the article's content
    def scrape_content(self,
                       xml=None
    ):
        raw_contents = xml.select_one(self.content_copy_selector).text.strip() # or contents for using tag
        raw_contents_last = raw_contents.split('\n')[-1].strip()
        if self.dummy_content in raw_contents_last:
            contents = '\n'.join(raw_contents.split('\n')[:-1])
        else:
            contents = raw_contents

        return '<br>'.join(contents.split(self.contents_split_tag))

    # Extract the writer's email
    def scrape_email(self,
                     href=None
    ):
        response = rq.get(self.base_url + href)
        soup = BeautifulSoup(response.content, self.parser)
        try:
            low_email = soup.select_one(self.email_copy_selector)['href']
        except TypeError:
            return 'None'

        return low_email.replace(self.replace_email_dummy, '')

    def scrape_category(self,
                        href=None
    ):
        response = rq.get(self.base_url + href)
        soup = BeautifulSoup(response.content, self.parser)

        return soup.select_one(self.category_copy_selector).text.strip()

    # Extract the article's image and content
    def get_inner_data(self, href):
        inner_xml = self.inner_xml_parsing(href)

        vision = self.scrape_vision(inner_xml)
        contents = clean_contents(self.scrape_content(inner_xml))
        writer_email = self.scrape_email(href)
        category = self.scrape_category(href)

        return vision, contents, writer_email, category

    # Extract the entire information of the article
    def get_info(self,
                 tags=None
    ):
        if len(tags) > 1:
            news_parm = tags.select_one(self.cur_news_copy_selector)
            news_title, news_href, news_writer, news_date = self.get_metadata(news_parm, tags)

            if self.last_checker: return 0
            vision, contents, writer_email, category = self.get_inner_data(news_href)

            info = {'date': news_date,
                    'category': category,
                    'title': news_title,
                    'writer': news_writer,
                    'writer_email': writer_email,
                    'vision': vision,
                    'contents': contents}

            return info

        else:
            return 1

    # Run the scraping operation and return the extracted data
    def run(self):
        banner_xml = self.banner_xml_parsing()

        # [속보]에 있는 각 뉴스 타이틀에 접근
        for index, tags in enumerate(banner_xml):
            information = self.get_info(tags)

            if type(information) != int:
                self.scraping_data[str(information['title'])] = information

            if information == 0: break

        return self.scraping_data

class NewsisScraper():
    # Initialization function
    def __init__(self, args, config):
        self.args = args
        self.last_checker = False
        self.last_file_name = config['Last_file_name']

        self.parser = 'lxml'

        self.base_url = "https://newsis.com/"
        self.banner_url = "realnews/"
        self.banner_copy_selector = "div.article > ul"

        self.cur_news_copy_selector = "div.thumCont"
        self.inner_copy_selector = "div.viewer"

        self.writer_copy_selector = "span"
        self.date_copy_selector = "p.time"
        self.title_href_copy_selector = "div.txtCont > p.tit > a"

        self.content_copy_selector = "article"
        self.summ_copy_selector = "div.summury"
        self.vision_cont_copy_selector = "p.photojournal"

        self.vision_copy_selector = "div.thumCont > div > div > tbody > tr > td.img > img"
        self.email_copy_selector = "a.email_v2"
        self.email_starter = "◎공감언론 뉴시스"
        self.email_domain = "newsis.com"
        self.category_copy_selector = "p.tit"

        self.scraping_data = dict()
        self.replace_email_dummy = "mailto:"
        self.contents_split_tag = "\r"

    # Access the [Breaking News] page and parse the HTML
    def banner_xml_parsing(self
    ):
        response = rq.get(self.base_url + self.banner_url)
        soup = BeautifulSoup(response.content, self.parser)

        return soup.select_one(self.banner_copy_selector)

    # Access the article's detail page and parse the HTML
    def inner_xml_parsing(self,
                          href=None
    ):
        response = rq.get(self.base_url + href)
        soup = BeautifulSoup(response.content, self.parser)

        return soup.select_one(self.inner_copy_selector)

    # Perform validation checks for each value
    def checking_value(self,
                       value=None,
                       task_name=None
    ):
        if task_name == 'writer':
            value = value.replace('기자', '')
            value = value.split()[0]

        elif task_name == 'date':
            value = value.replace(' ', '_')
            #if value == self.last_file_name: self.last_checker = True

        return value

    # Extract the article's title, link, author, and date information
    def get_metadata(self,
                     parm=None,
    ):
        writer = self.checking_value(parm.select_one(self.writer_copy_selector).text,
                                     task_name='writer')
        date = self.checking_value(parm.select_one(self.date_copy_selector).contents[-1],
                                   task_name='date')

        title = parm.select_one(self.title_href_copy_selector ).text.strip()
        href = parm.select_one(self.title_href_copy_selector )['href']
        
        if title == self.last_file_name: self.last_checker = True

        return title, href, writer, date

    # Extract the article's image URL
    def scrape_vision(self,
                      xml=None
    ):
        try:
            vision_url = xml.select_one(self.vision_copy_selector)['src']
        except:
            vision_url = 'None'

        return vision_url

    def extract_email_addresses(self,
                                string=None
    ):
        try:
            starter_index = string.find(self.email_starter)
            email_addresses = string[starter_index:].split()[2]
            if self.email_domain not in email_addresses: email_addresses = 'None'

        except:
            email_addresses = 'None'

        return email_addresses

    # Extract the article's content
    def scrape_content(self,
                       xml=None
    ):
        try:
            summary = xml.select_one(self.summ_copy_selector).text.strip()
        except AttributeError:
            summary = None

        try:
            vision_contents = xml.select_one(self.vision_cont_copy_selector).text.strip()
        except AttributeError:
            vision_contents = None

        raw_contents = xml.select_one(self.content_copy_selector).text.strip()

        if summary != None:
            raw_contents = raw_contents.replace(summary, '')

        if vision_contents != None:
            raw_contents = raw_contents.replace(vision_contents, '')

        cy_check = 0
        contents = ''
        for text in raw_contents.split(self.contents_split_tag):
            if text == '':
                continue

            if cy_check == 0:
                contents += text.replace('\n', '').strip()
            else:
                contents += '<br>'+text.replace('\n', '').strip()
            cy_check += 1

        return contents

    # Extract the writer's email
    def scrape_email(self,
                     string=None
    ):
        return self.extract_email_addresses(string)

    def scrape_category(self,
                        href=None
    ):
        response = rq.get(self.base_url + href)
        soup = BeautifulSoup(response.content, self.parser)

        return soup.select_one(self.category_copy_selector).text.strip()

    # Extract the article's image and content
    def get_inner_data(self, href):
        inner_xml = self.inner_xml_parsing(href)

        vision = self.scrape_vision(inner_xml)
        contents = clean_contents(self.scrape_content(inner_xml))
        writer_email = self.scrape_email(contents)
        category = self.scrape_category(href)

        return vision, contents, writer_email, category

    # Extract the entire information of the article
    def get_info(self,
                 tags=None
    ):
        if len(tags) > 1:
            news_title, news_href, news_writer, news_date = self.get_metadata(tags)

            if self.last_checker: return 0
            vision, contents, writer_email, category = self.get_inner_data(news_href)

            info = {'date': news_date,
                    'category': category,
                    'title': news_title,
                    'writer': news_writer,
                    'writer_email': writer_email,
                    'vision': vision,
                    'contents': contents}

            return info

        else:
            return 1

    # Run the scraping operation and return the extracted data
    def run(self):
        banner_xml = self.banner_xml_parsing()

        # [속보]에 있는 각 뉴스 타이틀에 접근
        for index, tags in enumerate(banner_xml):
            information = self.get_info(tags)

            if type(information) != int:
                self.scraping_data[str(information['title'])] = information

            if information == 0: break

        return self.scraping_data

class NocutScraper():
    # Initialization function
    def __init__(self, args, config):
        self.args = args
        self.last_checker = False
        self.last_file_name = config['Last_file_name']

        self.parser = 'lxml'

        self.base_url = "https://www.nocutnews.co.kr/"
        self.banner_url = "news/list/"
        self.banner_copy_selector = "div.newslist > ul"

        self.cur_news_copy_selector = "div.thumCont"
        self.inner_copy_selector = "div.viewbox"

        self.title_copy_selector = "dt"
        self.href_copy_selector = "dt > a"

        self.writer_copy_selector = "ul.bl_b > li.email"
        self.writer_dummpy = ['기자', '기상리포터', '특파원']
        self.date_copy_selector = "ul.bl_b"

        self.content_copy_selector = "div"
        self.content_id_copy_selector = "pnlContent"
        self.unnecessary_content_copy_selector = "div > span"

        self.vision_copy_selector = "span.fr-img-wrap > img"
        self.email_copy_selector = "ul.bl_b > li.email > a.e_ico"
        self.category_copy_selector = "ul.head_subtit > li > strong > a"
        self.inner_category_copy_selector = "div.sub_group > p > strong"

        self.scraping_data = dict()
        self.replace_email_dummy = "mailto:"
        self.contents_split_tag = "<br/>"

    # Access the [Breaking News] page and parse the HTML
    def banner_xml_parsing(self
    ):
        response = rq.get(self.base_url + self.banner_url)
        soup = BeautifulSoup(response.content, self.parser)

        return soup.select_one(self.banner_copy_selector)

    # Access the article's detail page and parse the HTML
    def inner_xml_parsing(self,
                          href=None
    ):
        response = rq.get(self.base_url + href)
        soup = BeautifulSoup(response.content, self.parser)

        return soup.select_one(self.inner_copy_selector)

    # Perform validation checks for each value
    def checking_value(self,
                       value=None,
                       task_name=None
    ):
        if task_name == 'writer':
            for dummy in self.writer_dummy:
                value = value.replace(dummy, '')
            
        elif task_name == 'date':
            value = value.replace(' ', '_')
            #if value == self.last_file_name: self.last_checker = True

        return value

    # Extract the article's title, link, author, and date information
    def get_metadata(self,
                     parm=None,
    ):
        try:
            title = parm.select_one(self.title_copy_selector).text.strip()
            href = parm.select_one(self.href_copy_selector)['href']
        # 중간에 광고 배너가 있음
        except:
            title, href = None, None
        
        if title == self.last_file_name: self.last_checker = True

        return title, href

    # Extract the article's image URL
    def scrape_vision(self,
                      xml=None
    ):
        try:
            vision_url = xml.select_one(self.vision_copy_selector)['src']
        except:
            vision_url = 'None'

        return vision_url

    # Extract the article's content
    def scrape_content(self,
                       xml=None
    ):
        try:
            # contents가 있는 부분 너무 복잡함
            text = xml.find(self.content_copy_selector, id=self.content_id_copy_selector).text.strip()
            try:
                text = text.split('\n')[2:][0][:10]
            except:
                text = text[:10]

            contents = xml.find(self.content_copy_selector, id=self.content_id_copy_selector).contents
            index_of_text = [idx for idx, val in enumerate(contents) if text in val]

            try:
                contents = [str(val).replace(self.contents_split_tag, '').replace(u'\xa0',u'') for val in contents[index_of_text[0]:]
                            if str(val).replace(self.contents_split_tag, '').replace(u'\xa0',u'')!='']
            except:
                return xml.find(self.content_copy_selector, id=self.content_id_copy_selector).text.strip()
            contents = '<br>'.join(contents)

            if '<div' in contents:
                index_of_start_div = contents.find('<div')
                index_of_end_div = contents.find('</div>')
                contents_part_1 = contents[:index_of_start_div]
                contents_part_2 = contents[index_of_end_div+10:]  # +10 -> </div><br> char 개수
                contents = contents_part_1 + contents_part_2


            if '<span' in contents:
                index_of_start_div = contents.find('<span')
                index_of_end_div = contents.find('</span')
                contents_part_1 = contents[:index_of_start_div]
                contents_part_2 = contents[index_of_end_div+7:].replace('</span>', '')
                contents = contents_part_1 + contents_part_2

            return contents.replace('<br><br>', '<br>').strip()

        except TypeError:
            return 'Error'

    # Extract the writer's email
    def scrape_email(self,
                     href=None
    ):
        response = rq.get(self.base_url + href)
        soup = BeautifulSoup(response.content, self.parser)

        try:
            email = soup.select_one(self.email_copy_selector)['href'].replace(self.replace_email_dummy, '')
        except:
            email = 'None'

        return email

    def scrape_category(self,
                        href=None
    ):
        response = rq.get(self.base_url + href)
        soup = BeautifulSoup(response.content, self.parser)

        try:
            return soup.select_one(self.category_copy_selector).text.strip()
        except AttributeError:
            return soup.select_one(self.inner_category_copy_selector).text.strip()

    def scrape_writer(self,
                      href=None
    ):
        response = rq.get(self.base_url + href)
        soup = BeautifulSoup(response.content, self.parser)

        try:
            writer_data_split = soup.select_one(self.writer_copy_selector).text.split()
            if '기자' in ' '.join(writer_data_split):
                index_of_reporter = writer_data_split.index('기자')
            elif '특파원' in ' '.join(writer_data_split):
                index_of_reporter = writer_data_split.index('특파원')
            elif '기상리포터' in ' '.join(writer_data_split):
                index_of_reporter = writer_data_split.index('기상리포터')
            else: return 'None'

            writer = writer_data_split[index_of_reporter-1]
        
        except:
            writer = 'None'

        return writer

    def scrape_date(self,
                      href=None
    ):
        response = rq.get(self.base_url + href)
        soup = BeautifulSoup(response.content, self.parser)

        try:
            date_data_split = soup.select_one(self.date_copy_selector).text.split()
            date = f'{date_data_split[-2]}_{date_data_split[-1]}'
        except:
            date = 'None'

        return date

    # Extract the article's image and content
    def get_inner_data(self, href):
        inner_xml = self.inner_xml_parsing(href)

        vision = self.scrape_vision(inner_xml)
        contents = clean_contents(self.scrape_content(inner_xml))
        news_writer = self.scrape_writer(href)
        writer_email = self.scrape_email(href)
        news_date = self.scrape_date(href)
        category = self.scrape_category(href)

        return news_date, news_writer, vision, contents, writer_email, category

    # Extract the entire information of the article
    def get_info(self,
                 tags=None
    ):
        if len(tags) > 1:
            news_title, news_href = self.get_metadata(tags)
            if news_title == None: return 1
            if self.last_checker: return 0

            news_date, news_writer, vision, contents, writer_email, category = self.get_inner_data(news_href)

            info = {'date': news_date,
                    'category': category,
                    'title': news_title,
                    'writer': news_writer,
                    'writer_email': writer_email,
                    'vision': vision,
                    'contents': contents}

            return info

        else:
            return 1

    # Run the scraping operation and return the extracted data
    def run(self):
        banner_xml = self.banner_xml_parsing()

        # [속보]에 있는 각 뉴스 타이틀에 접근
        for index, tags in enumerate(banner_xml):
            information = self.get_info(tags)

            if type(information) != int:
                self.scraping_data[str(information['title'])] = information

            if information == 0: break

        return self.scraping_data

def clean_contents(contents):
    try:
        index_of_br = contents.find('<br>')
        if index_of_br == 0:
            contents = contents[2:]
    except:
        pass

    split_contents = contents.split('<br>')
    clr_contents = '<br>'.join([sen.strip() for sen in split_contents if sen!=''])

    return clr_contents
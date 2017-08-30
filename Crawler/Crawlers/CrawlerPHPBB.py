from Crawler.CrawlerBasic import CrawlerBasic

class CrawlerPHPBB(CrawlerBasic):

    name = 'CrawlerPHPForums'

    url = 'http://antena3.ro'
    domain = 'antena3.ro'
    rejectionSubstr =  ["/memberlist.php?","/posting.php?","/search.php?","/ucp.php?","/cron.php?","/help-others/","/parteneri/"]

    start_urls = (url,)
    allowed_domains = [domain]

    removeLastMessage = True

    #CSS
    bodyFilterCSS = "#pagecontent"

    repliesCSS = "div.postbody"
    authorsCSS = "div.postauthor"
    datesCSS = "td.postbottom"
    avatarsCSS = "div.postavatar img"
    titlesCSS = "div.postsubject"

    breadcrumbsCSS = ''
    breadcrumbsChildrenCSS = 'p.breadcrumbs > a'

    rejectReplyTitle = True

    def crawlerProcess(self, response, url):

        self.title = self.extractFirstElement(response.css('#pageheader > h2 > a::text'))
        self.fullDescription = ''
        self.shortDescription = ''


        self.replies = []

        if self.bodyFilterCSS != '':
            response = response.css(self.bodyFilterCSS)

        replies = response.css(self.repliesCSS)
        authors = response.css(self.authorsCSS)
        dates = response.css(self.datesCSS)
        avatars = response.css(self.avatarsCSS)
        titles = response.css(self.titlesCSS)

        if len(replies) == len(authors)+1:
            if self.removeLastMessage: del replies[-1]

        if len(replies) > 0 and len(authors) > 0 and len(dates) > 0 and len(titles) > 0:
            for i, reply in enumerate(replies):
                reply = replies[i]
                reply = '<br/>'.join(reply.css("::text").extract())

                if i < len(authors):
                    author = authors[i]
                    author = ' '.join(author.css("::text").extract())
                else: author = ''

                if i < len(dates):
                    if len(dates) == 2 * len(replies): date = dates[2*i]
                    else: date = dates[i]

                    date = ' '.join(date.css('::text').extract())

                if i < len(avatars):
                    avatar = avatars[i]
                    avatar = avatar.css('::attr(src)').extract_first()
                else: avatar = ''

                if i < len(titles):
                    title = titles[i]
                    title = ' '.join(title.css('::text').extract())
                else: title = ''


                if i == 0:
                    self.fullDescription = reply
                    self.shortDescription = ''
                    self.author = author
                    self.date = date
                    self.authorAvatar = avatar
                    #self.title = title
                else:
                    if self.rejectReplyTitle:
                        title = ''
                    self.replies.append({'description': reply, 'title':title, 'author':author, 'date':date, 'authorAvatar': avatar })

        self.parents = []

        if len(self.title) > 0:
            for i in reversed(range(1, 100)):
                parent = response.css(self.breadcrumbsChildrenCSS+':nth-child('+str(i)+')')
                parentText = self.extractFirstElement(parent.css('::text'))
                parentURL = self.extractFirstElement(parent.css('::attr(href)'))

                if parentText != '':
                    self.parents.append({'name':parentText, 'url':parentURL, 'index': i})

        if len(self.parents) > 0:
            ok = False
            for parent in self.parents:
                if parent['name'] == '':
                    ok = True
            if ok == False:
                self.parents.append({'name':'','url': self.url})

        self.parents = list(reversed(self.parents)) #changing the order



    def validate(self):
        if len(self.title) > 0 and len(self.fullDescription) > 0:
            return 'topic'

        return ''
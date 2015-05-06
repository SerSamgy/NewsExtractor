from bs4 import BeautifulSoup, UnicodeDammit
import textwrap

class ExtractException(Exception):
    """
    Custom exception. Needs for errors raised in Extractor class methods.
    Inherits from base Exception class.
    """
    pass

class Extractor(BeautifulSoup):
    """
    Inherits from class BeautifulSoup of the same name parser
    for the most convenient syntax parsing HTML/XML files.
    """
    # _header_tags = ("h1", "h2", "h3", "h4", "h5", "h6")
    _header_tags = ("h1", "h2")  # restrict by these headers

    def __init__(self, request, **kwargs):
        _markup = "lxml"  # set default parser
        super(Extractor, self).__init__(request, _markup, **kwargs)

    def _get_news_text(self, element):
        """
        Returns formatted string with article's text.

        element: Page's element to extract text from.
        """

        body = ""
        ps_tag_list = element.find_all("p")
        for ps_tag in ps_tag_list:
            a_tag = ps_tag.find_all("a")
            if (a_tag):
                for a_item in a_tag:
                    text_url = "%s[%s]" % (a_item.string, a_item["href"])
                    a_item.replace_with(text_url)  # replace <a href="h_text">Text</a> to Text[h_text]
            for script in ps_tag.find_all("script"):
                script.decompose()  # delete unnecessary element script
            for s_tag in ps_tag.stripped_strings:
                tag_text = textwrap.fill(  # simple variant textwrap.wrap()
                    (UnicodeDammit(s_tag)).unicode_markup,  # create paragraph from strings..
                    80  # .. with maximum length 80 symbols each
                ) + "\n"
                body += tag_text

        return body

    def _get_article_body(self):
        """
        Returns div element contains text of article.
        """

        by_class = self.select('div[class*="text"]')
        by_itemprop = self.select('div[itemprop="articleBody"]')
        if (by_class): element = by_class[0]
        elif (by_itemprop): element = by_itemprop[0]
        else:
            raise ExtractException("Article's text hasn't been found!")
        return element

    def get_news(self):
        """
        Returns string with headers and text of article.
        """
        news_body = ""
        # choose headers
        for header_tag in self._header_tags:
            if (self.find(header_tag)):
                header = UnicodeDammit(  # set Unicode for strings
                    " ".join(self.find(header_tag).stripped_strings)
                )
                header.unicode_markup += "\n"  # separate headers from each other and main body
                news_body += header.unicode_markup
        news_body += "\n"
        # choose main text
        ab = self._get_article_body()
        text_body = self._get_news_text(ab)
        news_body += text_body
        return news_body
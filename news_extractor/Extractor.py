from bs4 import BeautifulSoup, UnicodeDammit
import textwrap

class ExtractException(Exception):
    """
    Пользовательский класс исключения. Необходим для вывода ошибок,
    вызванных в методах класса Extractor.
    Наследует от базового класса.
    """
    pass

class Extractor(BeautifulSoup):
    """
    Наследует от класса BeautifulSoup одноимённого парсера, предназначенного
    для максимально комфортного синтаксического разбора файлов HTML/XML.
    """
    # _header_tags = ("h1", "h2", "h3", "h4", "h5", "h6")
    _header_tags = ("h1", "h2")  # ограничимся этими заголовками

    def __init__(self, request, **kwargs):
        _markup = "lxml"  # зададим парсер по-умолчанию
        super(Extractor, self).__init__(request, _markup, **kwargs)

    def _get_news_text(self, element):
        """
        Возвращает форматированную строку с текстом статьи.

        element: Элемент страницы, из которого будет извлекаться текст.
        """

        body = ""
        ps_tag_list = element.find_all("p")
        for ps_tag in ps_tag_list:
            a_tag = ps_tag.find_all("a")
            if (a_tag):
                for a_item in a_tag:
                    text_url = "%s[%s]" % (a_item.string, a_item["href"])
                    a_item.replace_with(text_url)  # заменяем <a href="h_text">Text</a> на Text[h_text]
            for script in ps_tag.find_all("script"):
                script.decompose()  # удаляем лишние элементы script
            for s_tag in ps_tag.stripped_strings:
                tag_text = textwrap.fill(  # упрощённый вариант textwrap.wrap()
                    (UnicodeDammit(s_tag)).unicode_markup,  # создаём абзац из строк..
                    80  # ..с максимальной длиной 80 символов каждая
                ) + "\n"
                body += tag_text

        return body

    def _get_article_body(self):
        """
        Возвращает div элемент, содержащий текст статьи.
        """

        by_class = self.select('div[class*="text"]')
        by_itemprop = self.select('div[itemprop="articleBody"]')
        if (by_class): element = by_class[0]
        elif (by_itemprop): element = by_itemprop[0]
        else:
            raise ExtractException("Текст статьи не найден!")
        return element

    def get_news(self):
        """
        Возвращает строку с заголовками и текстом статьи.
        """
        news_body = ""
        # выбираем заголовки
        for header_tag in self._header_tags:
            if (self.find(header_tag)):
                header = UnicodeDammit(  # задаём кодировку Unicode для строк
                    " ".join(self.find(header_tag).stripped_strings)
                )
                header.unicode_markup += "\n"  # отделяем заголовки друг от друга и от основного текста
                news_body += header.unicode_markup
        news_body += "\n"
        # выбираем основной текст
        ab = self._get_article_body()
        text_body = self._get_news_text(ab)
        news_body += text_body
        return news_body
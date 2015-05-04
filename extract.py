#!python3
import click
from urllib import request
from news_extractor.Extractor import Extractor, ExtractException


class URL(object):
    """
    Сохраняет информацию, прочитанную из командной строки
    и свалидированную, в переменную context для передачи в
    тело функции extract.
    """
    def __init__(self, context):
        self.context = context

def validate_url(ctx, param, value):
    """
    Функция для валидации введённого url'а. Возвращает экземпляр класса URL.
    """
    try:
        return URL(request.urlopen(value).read())
    except ValueError:
        raise click.BadParameter('url need to be a correct URL string')

@click.command()
@click.option('-o', '--output', default="news.txt", type=click.Path(writable=True),
              help='File where information to extract.')
@click.option('-u', '--url', prompt='Input URL', callback=validate_url, help='Url to extract information from.')
def extract(url, output):
    """Извлекает текст статьи по адресу url и записывает его в файл output."""
    click.echo("Start progress..")
    news = url.context
    e = Extractor(news)
    click.echo("Extract information..")
    try:
        news_text = e.get_news()
    except ExtractException as exception:
        # чтобы не выводить трейсбек пользователю, просто пишем сообщение об ошибке
        return click.echo("Page parsing error: %s" % exception.args[0])

    with open(output, "w", encoding="utf-8") as out_file:
        # print(news_text, file=out_file, flush=True)
        with click.progressbar(news_text, length=len(news_text.encode()), label="Writing to file") as bar:
            for item in bar:
                print(item, end='', file=out_file, flush=True)

    click.echo("Finished!")

if __name__ == '__main__':
    extract()
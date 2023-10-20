from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
import numpy as np
import bs4
import re
from w3lib.html import remove_tags
from crawler.items import TheNumbersComItem

class ThenumbersComSpider(CrawlSpider):
    name = "the-numbers_com"
    allowed_domains = ["www.the-numbers.com"]
    start_urls = ["https://www.the-numbers.com/United-States/movies#tab=year"]
    follow_pat = r"https://www.the-numbers.com/United-States/movies/year/\d+"
    parse_pat = r"https://www.the-numbers.com/movie/.+"

    rules = (
        Rule(LinkExtractor(allow=follow_pat, deny=parse_pat)),
        Rule(
            LinkExtractor(allow=parse_pat),
            callback="parse_item"
        ),
    )

    def parse_item(self, response: Response):
        loader = ItemLoader(
            item=TheNumbersComItem(),
            response=response
        )
        soup = bs4.BeautifulSoup(response.text, "lxml")

        url = re.search(r"^(.+)(#.+)?$", response.url).group()
        _id = re.search(r"(?<=/)[^/]+$", url).group()
        name, year = re.search(r"^(.+)\s\((\d+)\)$", soup.h1.string).groups()
        summary = soup.find("div", {"id": "summary"}).p.string
        movie_finances = self.find_table(soup, "Theatrical Performance")
        dom_bo = movie_finances.find("td", {"class": "data"})
        int_bo = movie_finances.find("td", {"class": "data sum"})

        metrics_tbl = self.find_table(soup, "Metrics")
        (opening_weekend,) = self.table_lookup(metrics_tbl, pattern=r"Opening\sWeekend")
        (legs,) = self.table_lookup(metrics_tbl, pattern=r"Legs")
        (budget,) = self.table_lookup(metrics_tbl, pattern=r"Production\sBudget")
        (theater_counts,) = self.table_lookup(metrics_tbl, pattern=r"Theater\scounts")
        (infl_bo,) = self.table_lookup(metrics_tbl, pattern=r"Infl.\sAdj.\sDom.\sBO")

        detail_tbl = self.find_table(soup, "Movie Details")
        (domestic_releases,) = self.table_lookup(detail_tbl, pattern="Domestic\sReleases")
        (mpaa,) = self.table_lookup(detail_tbl, pattern=r"MPAA\sRating")
        (running_time,) = self.table_lookup(detail_tbl, pattern=r"Running\sTime")
        (franchise,) = self.table_lookup(detail_tbl, pattern=r"Franchise")
        (genre,) = self.table_lookup(detail_tbl, pattern=r"Genre")
        (production_method,) = self.table_lookup(detail_tbl, pattern="Production\sMethod")
        (creative_type,) = self.table_lookup(detail_tbl, pattern="Creative\sType")
        (keywords,) = self.table_lookup(detail_tbl, pattern=r"Keywords")
        (source,) = self.table_lookup(detail_tbl, pattern=r"Source")
        (production_financing,) = self.table_lookup(detail_tbl, pattern=r"Production/Financing")
        (languages,) = self.table_lookup(detail_tbl, pattern=r"Languages")

        cast_tbls = soup.find("div", {"id": "cast-and-crew"})
        leading_tbl = self.find_table(cast_tbls, "Leading Cast") if cast_tbls else None
        supporting_tbl = self.find_table(cast_tbls, "Supporting Cast") if cast_tbls else None
        technical_tbl = self.find_table(cast_tbls, "Production and Technical Credits") if cast_tbls else None

        loader.add_value("_id", _id)
        loader.add_value("url", url)
        loader.add_value("name", name)
        loader.add_value("year", year)
        loader.add_value("summary", summary)
        loader.add_value("dom_bo", dom_bo.string if dom_bo else None)
        loader.add_value("int_bo", int_bo.string if int_bo else None)
        loader.add_value("opening_weekend", opening_weekend)
        loader.add_value("legs", legs)
        loader.add_value("budget", budget)
        loader.add_value("theater_counts", theater_counts)
        loader.add_value("infl_bo", infl_bo)

        loader.add_value("domestic_releases", remove_tags(domestic_releases.decode_contents().replace("<br/>", " -- ").replace("\n", "")) if domestic_releases  else None)
        loader.add_value("domestic_distributors", np.unique([el.string for el in domestic_releases.find_all("a")]) if domestic_releases else None)
        loader.add_value("mpaa", mpaa.a.string if mpaa else None)
        loader.add_value("running_time", running_time)
        loader.add_value("franchise", [el.string for el in franchise.find_all("a")] if franchise else None)
        loader.add_value("genre", genre.a.string if genre else None)
        loader.add_value("production_method", production_method.a.string if production_method else None)
        loader.add_value("creative_type", creative_type.a.string if creative_type else None)
        loader.add_value("keywords", keywords.text if keywords else None)
        loader.add_value("source", source.a.string if source else None)
        loader.add_value("production_financing", [el.string for el in production_financing.find_all("a")] if production_financing else None)
        loader.add_value("languages", [el.string for el in languages.find_all("a")] if languages else None)

        loader.add_value("leading_cast", self.get_cast(leading_tbl) if leading_tbl else None)
        loader.add_value("supporting_cast", self.get_cast(supporting_tbl) if supporting_tbl else None)
        loader.add_value("technical_credits", self.get_cast(technical_tbl) if technical_tbl else None)

        item = loader.load_item()
        return item
    
    def find_table(self, soup: bs4.BeautifulSoup, table_name: str):
        title_el = soup.find_all("tr", {"class": "heading"})
        matched = None
        for el in title_el:
            if re.search(table_name, el.text):
                matched = el.find_parent("table")
                break
        else:
            title = soup.find(["h2", "h1"], string=table_name)
            matched = title.find_next_sibling("table") if title else None
        return matched

    def table_lookup(self, table: bs4.Tag, label: str = None, pattern: str = None):
        rows = table.find_all("tr")
        vals = []
        for row in rows:
            key_cell, value_cell = row.find_all("td")
            key, val = key_cell.string, value_cell
            if pattern is not None:
                matched = re.search(pattern, key) is not None
            else:
                matched = key == label
            if matched:
                vals.append(val)
        return vals if len(vals) > 0 else [None]

    def get_cast(self, table: bs4.BeautifulSoup):
        id_regex = re.compile(r"/person/(.+)")
        person_ids = [id_regex.search(tr.a["href"]).group(1) for tr in table.find_all("tr")]
        return person_ids
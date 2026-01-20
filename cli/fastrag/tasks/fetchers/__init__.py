from fastrag.tasks.fetchers.crawler import CrawlerFetcher
from fastrag.tasks.fetchers.http import HttpFetcher
from fastrag.tasks.fetchers.path import PathFetcher
from fastrag.tasks.fetchers.sitemap import SitemapXMLFetcher

__all__ = [PathFetcher, HttpFetcher, SitemapXMLFetcher, CrawlerFetcher]

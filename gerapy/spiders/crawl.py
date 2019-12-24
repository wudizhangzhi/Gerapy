# -*- coding: utf-8 -*-
from furl import furl
from scrapy.spiders import CrawlSpider as BaseSpider, signals, Rule as OldRule
from scrapy_splash import SplashRequest
from scrapy import Request
from gerapy.server.core.utils import str2list, str2dict, str2body
from scrapy.utils.spider import iterate_spider_output


class Rule(OldRule):
    def __init__(self, link_extractor, method='GET', data=None, params=None, headers=None,
                 callback=None, cb_kwargs=None, follow=None, priority=0, dont_filter=False,
                 meta=None, proxy=None, render=False, dont_redirect=None, dont_retry=None,
                 handle_httpstatus_list=None, handle_httpstatus_all=None,
                 dont_cache=None, dont_obey_robotstxt=None,
                 download_timeout=None, max_retry_times=None,
                 process_links=None, process_request=lambda x: x, process_body=None):
        self.link_extractor = link_extractor
        self.callback = callback
        self.method = method
        self.data = str2body(data)
        self.params = str2dict(params)
        self.headers = str2dict(headers)
        self.priority = priority
        self.dont_filter = dont_filter
        self.meta = str2dict(meta)
        self.cb_kwargs = str2dict(cb_kwargs)
        self.proxy = proxy
        self.render = render
        self.dont_redirect = dont_redirect
        self.dont_retry = dont_retry
        self.handle_httpstatus_list = str2list(handle_httpstatus_list, lambda x: int(x))
        self.handle_httpstatus_all = handle_httpstatus_all
        self.dont_cache = dont_cache
        self.dont_obey_robotstxt = dont_obey_robotstxt
        self.download_timeout = download_timeout
        self.max_retry_times = max_retry_times
        self.process_links = process_links
        self.process_request = process_request
        self.process_body = process_body
        if follow is None:
            self.follow = False if callback else True
        else:
            self.follow = follow

    def __str__(self):
        """
        object to str
        :return:
        """
        return str(self.__dict__.items())


class CrawlSpider(BaseSpider):
    name = None

    def start_requests(self):
        """
        override start requests
        :return:
        """
        self.crawler.signals.connect(self.make_start_requests, signal=signals.spider_idle)
        return []

    def make_start_requests(self):
        """
        make start requests
        :return:
        """
        for request in self.start():
            self.crawler.engine.slot.scheduler.enqueue_request(request)

    def start(self):
        """
        start requests
        :return:
        """
        for url in self.make_start_urls():
            yield Request(url)

    def make_start_urls(self):
        """
        get start urls
        :return:
        """
        return self.start_urls

    def splash_request(self, request, args=None):
        """
        change request to SplashRequest
        :param request:
        :param args:
        :return:
        """
        args = args if args else {'wait': 1, 'timeout': 30}
        meta = request.meta
        meta.update({'url': request.url})
        return SplashRequest(url=request.url, dont_process_response=True, args=args, callback=request.callback,
                             meta=meta)

    def _generate_request(self, index, rule, link, response):
        """
        generate request by rule
        :param index: rule index
        :param rule: rule object
        :param link: link object
        :return: new request object
        """
        url = furl(link.url).add(rule.params).url if rule.params else link.url

        # init request body
        body = None
        # process by method
        if rule.method.upper() == 'POST':
            # if process_body defined, use its result
            if callable(rule.process_body):
                body = rule.process_body(response)
            # if data defined in rule, use data
            if rule.data:
                body = rule.data

        r = Request(url=url, method=rule.method, body=body, headers=rule.headers,
                    priority=rule.priority,
                    dont_filter=rule.dont_filter, callback=self._response_downloaded)

        # update meta args
        r.meta.update(**rule.meta)

        meta_items = ['dont_redirect', 'dont_retry', 'handle_httpstatus_list', 'handle_httpstatus_all',
                      'dont_cache', 'dont_obey_robotstxt', 'download_timeout', 'max_retry_times', 'proxy', 'render']
        meta_args = {meta_item: getattr(rule, meta_item) for meta_item in meta_items if
                     not getattr(rule, meta_item) is None}
        # update extra meta args
        r.meta.update(**meta_args)
        # super _build_request
        r.meta.update(rule=index, link_text=link.text)
        return r

    def _requests_to_follow(self, response):
        """
        requests to follow
        :param response:
        :return:
        """
        seen = set()
        for index, rule in enumerate(self._rules):
            links = [lnk for lnk in rule.link_extractor.extract_links(response)
                     if lnk not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                seen.add(link)
                # change _build_request to _generate_request
                r = self._generate_request(index, rule, link, response)
                yield rule.process_request(r)


class SplashSpider(CrawlSpider):
    DEFAULT_SPLASH_ARGS = {'wait': 10, 'timeout': 60}

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SplashSpider, cls).from_crawler(crawler, *args, **kwargs)
        # splash settings
        spider._splash_custom_settings = crawler.settings.get('SPLASH_CUSTOM_SETTINGS', None)
        return spider

    def _parse_response(self, response, callback, cb_kwargs, follow=True):
        if callback:
            # update url to real url
            response.replace(url=response.meta.get('url') or response.url)
            cb_res = callback(response, **cb_kwargs) or ()
            cb_res = self.process_results(response, cb_res)
            for requests_or_item in iterate_spider_output(cb_res):
                yield requests_or_item

        if follow and self._follow_links:
            for request_or_item in self._requests_to_follow(response):
                yield request_or_item

    def _requests_to_follow(self, response):
        seen = set()
        for n, rule in enumerate(self._rules):
            links = [lnk for lnk in rule.link_extractor.extract_links(response)
                     if lnk not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                seen.add(link)
                request = self._build_request(n, link)
                yield rule._process_request(request, response)

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args=self._splash_custom_settings or self.DEFAULT_SPLASH_ARGS)

    def _build_request(self, rule, link):
        r = Request(url=link.url, callback=self._response_downloaded)
        r.meta.update(rule=rule, link_text=link.text)
        return self.splash_request(r, args=self._splash_custom_settings)

    def splash_request(self, request, args=None):
        """
        change request to SplashRequest
        :param request:
        :param args:
        :return:
        """
        args = args if args else self.DEFAULT_SPLASH_ARGS
        meta = request.meta
        meta.update({'url': request.url})
        return SplashRequest(url=request.url, dont_process_response=True, args=args, callback=request.callback,
                             meta=meta)

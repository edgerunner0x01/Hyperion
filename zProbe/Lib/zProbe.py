#########################################################
#   zProbe - Scrape And Extract Data From The Web       #
# 			  Author   - edgerunner0x01                 #
# 		https://www.github.com/edgerunner0x01           #
#########################################################

from bs4 import BeautifulSoup, Comment
import requests
import re
import urllib3
from typing import Union, List, Tuple, Dict
import xml.etree.ElementTree as ET
import logging
import json
from random import randint 
import os

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

USER_AGENTS_PATH:str=str(os.path.dirname(__file__))+"/../Require/User-Agents.json"
UserAgents:List[str]=json.load(open(USER_AGENTS_PATH,"r"))

DEFAULT_HEADERS: Dict[str, str] = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en",
    "User-Agent": str(UserAgents[randint(0,len(UserAgents)-1)])
}

# Configure the logging
class Log:
    LOG_LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    def __init__(self, log_method: str = "DEBUG", logger_name: str = "zProbe"):
        self.logger = logging.getLogger(logger_name)
        self.configure_logging(log_method)

    def configure_logging(self, log_method: str):
        try:
            log_level = self.LOG_LEVELS.get(log_method, logging.DEBUG)
            logging.basicConfig(level=log_level,
                                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                handlers=[
                                    logging.FileHandler("Log/Log.log"),
                                    logging.StreamHandler()
                                ])
        except Exception as e:
            self.logger.error("Error setting up logging: %s", e)

class Target:
    def __init__(self, url: str, proxies : Dict[str, str]=None ,headers: Dict[str, str] = DEFAULT_HEADERS):
        self.url = url
        self.headers = headers
        self.headers["User-Agent"]=str(UserAgents[randint(0,len(UserAgents)-1)])
        self.source = None
        self.HTTP_STATUS = None
        self.proxies=proxies
        try:
            req = requests.get(self.url, headers=headers, proxies=self.proxies ,verify=False)
            self.HTTP_STATUS = req.status_code
            if self.HTTP_STATUS == 200:
                self.source = req.text
            else:
                logger.error(f"Failed to retrieve URL {self.url}. Status code: {self.HTTP_STATUS}")
        except Exception as E:
            logger.error(f"Exception occurred while fetching URL {self.url}: {E}")

    def Extract_Comments(self) -> Union[Tuple[List[str], bool], Tuple[str, bool]]:
        if self.HTTP_STATUS != 200:
            return "HTTP Status not 200", False
        try:
            soup = BeautifulSoup(self.source, 'html.parser')
            comments = [str(comment.extract()) for comment in soup.find_all(string=lambda text: isinstance(text, Comment))]
            return comments, True
        except Exception as E:
            logger.error(f"Exception occurred while extracting comments: {E}")
            return str(E), False

    def Extract_MetaData(self) -> Union[Tuple[List[Dict[str, str]], bool], Tuple[str, bool]]:
        if self.HTTP_STATUS != 200:
            return "HTTP Status not 200", False
        try:
            soup = BeautifulSoup(self.source, 'html.parser')
            metadata = [{'name': tag.get('name', ''), 'content': tag.get('content', '')} for tag in soup.find_all('meta')]
            return metadata, True
        except Exception as E:
            logger.error(f"Exception occurred while extracting metadata: {E}")
            return str(E), False

    def Extract_URLS(self) -> Union[Tuple[List[str], bool], Tuple[str, bool]]:
        if self.HTTP_STATUS != 200:
            return "HTTP Status not 200", False
        try:
            soup = BeautifulSoup(self.source, 'html.parser')
            urls = [tag.get('href') or tag.get('src') for tag in soup.find_all(['a', 'img', 'script', 'link', 'source'])]
            filtered_urls = [url for url in urls if url and url.startswith(('http://', 'https://', 'ftp://'))]
            return filtered_urls, True
        except Exception as E:
            logger.error(f"Exception occurred while extracting URLs: {E}")
            return str(E), False

    def Extract_Emails(self) -> Union[Tuple[List[str], bool], Tuple[str, bool]]:
        if self.HTTP_STATUS != 200:
            return "HTTP Status not 200", False
        try:
            email_pattern = re.compile(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4})')
            email_matches = re.findall(email_pattern, self.source)
            return email_matches, True
        except Exception as E:
            logger.error(f"Exception occurred while extracting emails: {E}")
            return str(E), False

    def Extract_Robots(self) -> Union[Tuple[str, int, bool], Tuple[str, bool]]:
        def filter_url(url: str) -> str:
            return url.rstrip('/')

        try:
            req = requests.get(f"{filter_url(self.url)}/robots.txt", headers=self.headers, proxies=self.proxies ,verify=False)
            status_code = req.status_code
            if status_code == 200:
                return req.text, status_code, True
            else:
                logger.error(f"Failed to retrieve robots.txt from {self.url}. Status code: {status_code}")
                return "", status_code, False
        except Exception as E:
            logger.error(f"Exception occurred while fetching robots.txt: {E}")
            return str(E), False

    def Extract_Sitemap(self) -> Union[Tuple[List[str], int, bool], Tuple[str, bool]]:
        def filter_url(url: str) -> str:
            return url.rstrip('/')

        try:
            req = requests.get(f"{filter_url(self.url)}/sitemap.xml", headers=self.headers, proxies=self.proxies ,verify=False)
            status_code = req.status_code
            if status_code == 200:
                urls = [url.text for url in ET.fromstring(req.text).findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
                return urls, status_code, True
            else:
                logger.error(f"Failed to retrieve sitemap.xml from {self.url}. Status code: {status_code}")
                return [], status_code, False
        except Exception as E:
            logger.error(f"Exception occurred while fetching sitemap.xml: {E}")
            return str(E), False

    def Extract_XML_URLS(self) -> Union[Tuple[List[str], int, bool], Tuple[str, bool]]:
        try:
            req = requests.get(self.url, headers=self.headers, proxies=self.proxies ,verify=False)
            status_code = req.status_code
            if status_code == 200:
                urls = [url.text for url in ET.fromstring(req.text).findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
                return urls, status_code, True
            else:
                logger.error(f"Failed to retrieve XML content from {self.url}. Status code: {status_code}")
                return [], status_code, False
        except Exception as E:
            logger.error(f"Exception occurred while fetching XML content: {E}")
            return str(E), False

    def Extract_WPLOGIN(self) -> Union[Tuple[Dict[str, Dict[str, str]], int, bool], Tuple[str, bool]]:
        def extract_form_params(html_content):
            form_params = {}
            soup = BeautifulSoup(html_content, 'html.parser')
            forms = soup.find_all('form')
            
            for form in forms:
                form_name = form.get('name') or form.get('id')
                if form_name:
                    form_params[form_name] = {}
                    inputs = form.find_all('input')
                    for inp in inputs:
                        name = inp.get('name')
                        value = inp.get('value')
                        if name:
                            form_params[form_name][name] = value
            return form_params

        def filter_url(url: str) -> str:
            return url.rstrip('/')

        try:
            req = requests.get(f"{filter_url(self.url)}/wp-login.php", headers=self.headers, proxies=self.proxies ,verify=False)
            status_code = req.status_code
            if status_code == 200:
                form_params = extract_form_params(req.text)
                return form_params, status_code, True
            else:
                logger.error(f"Failed to retrieve wp-login.php from {self.url}. Status code: {status_code}")
                return {}, status_code, False
        except Exception as E:
            logger.error(f"Exception occurred while fetching wp-login.php: {E}")
            return str(E), False

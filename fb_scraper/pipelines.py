import json
from datetime import datetime

import psycopg2
from psycopg2 import Error
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline

from w3lib.url import url_query_cleaner

from .items import *
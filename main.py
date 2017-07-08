import webapp2

import os
import jinja2
from amzmri.request_handlers.rank_report_request_handler import RankReportRequestHandler
from amzmri.request_handlers.reports_handler import ReportsHandler
from amzmri.request_handlers.asin_summary_handler import AsinSummaryHandler
from amzmri.request_handlers.asin_history_handler import AsinHistoryHandler
from asklogin import LoginPage
from amzmri.request_handlers.crone import Crone
from amzmri.request_handlers.keywords_asin_report import KeywordsAsinReport
from amzmri.request_handlers.asin_changes_report import AsinChangesReport

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


config = {'jinja' : JINJA_ENVIRONMENT}

app = webapp2.WSGIApplication([
    ('/', LoginPage),
    ('/rank_crone', Crone),
    ('/reports', ReportsHandler),
    ('/asin_summary', AsinSummaryHandler),#AsinSummaryHandler
    ('/asin_history', AsinHistoryHandler),
    ('/get_rank_report', RankReportRequestHandler), 
    ('/get_our_asin_keywords_report', KeywordsAsinReport),  
    ("/asin_changes_report", AsinChangesReport)   
], debug=True, config=config)
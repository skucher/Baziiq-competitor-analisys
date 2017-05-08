
import logging
import webapp2
from google.appengine.api import mail
from amzmri.dal.xsellDataAccessLayer import XSellDataAccessLayer
from amzmri.dal.amazonDataAccessLayer import AmazonDataAccessLayer
from amzmri.services.product_fields_handler import ProductFieldsHandler
from amzmri.request_handlers.fomatters.rank_report_formatters import RankFormatterFactory
import datetime
from amzmri.services.rank_report_service import RankReportService
import json
from google.appengine.ext import ndb

REPORT_TYPE_HTML, REPORT_TYPE_EMAIL = range(2)
REPORT_TYPE = {
    REPORT_TYPE_HTML:       'html',
    REPORT_TYPE_EMAIL:      'email'
}

class ReportsHandler(webapp2.RequestHandler):
    def get(self):
        return self.post();
    def post(self):
        report_type = self.request.get('type', REPORT_TYPE[REPORT_TYPE_HTML])        
        if report_type == REPORT_TYPE[REPORT_TYPE_HTML]:
            self.getReportHtml()
        elif report_type == REPORT_TYPE[REPORT_TYPE_EMAIL]:
            self.sendReportEmail()
    
    def getReportHtml(self):
        logging.info('getReportHtml')
        template_values = {} 
        template = self.app.config.get('jinja').get_template('reports.html')
        self.response.write(template.render(template_values))
        
    def sendReportEmail(self):
        logging.info('sendEmailReport')
        
        html = ''
        db_access_layer = XSellDataAccessLayer()
        amazon_access_layer = AmazonDataAccessLayer()
        update_products_fields_service = ProductFieldsHandler(amazon_access_layer, db_access_layer)
        
        asin_list = db_access_layer.getAsins()
        asin_to_url = {}
        for asin in asin_list:
            product_key = ndb.Key('ProductListing', asin)
            db_product = product_key.get()
            if db_product:
                asin_to_url[asin] = db_product.url
            
        html += '<b>Sampled cometitors (#{}): {}</b><br>'.format(str(len(asin_list)), str(asin_list))
        html += '<h2>Products changes</h2>'
        
        
        change_history = update_products_fields_service.getProductChangeHistory()
        color=''
        if change_history:
            table_html = '<table border="1" style="width:800px; text-align:center;">'
            table_html += '<tr>'
            table_html += '  <th style="color: #ffffff; background-color: #555555;padding: 3px;"></th>'
            table_html += '  <th style="color: #ffffff; background-color: #555555;padding: 3px;">Date</th>'
            table_html += '  <th style="color: #ffffff; background-color: #555555;padding: 3px;">ASIN</th>'
            table_html += '  <th style="color: #ffffff; background-color: #555555;padding: 3px;">Property</th>'
            table_html += '  <th style="color: #ffffff; background-color: #555555;padding: 3px;">Change from</th>'
            table_html += '  <th style="color: #ffffff; background-color: #555555;padding: 3px;">Change to</th>'        
            table_html += '</tr>'
            last_date = None
            index = 1
            color = 'background-color: #FFFFFF;'
            for change in change_history:
                current_date = str(change.creation_date.day) + '.' + str(change.creation_date.month)  + '.' + str(change.creation_date.year)
                
                if last_date == current_date:
                    table_html += '<tr style="{}">'.format(color)
                    table_html += '<td>{}. </td>'.format(str(index))
                    table_html += '<td class="table_empty_td"></td>'
                else:
                    if color == 'background-color: #FFFFFF;':
                        color = 'background-color: #E8E8E8;'
                    else:
                        color = 'background-color: #FFFFFF;'
                    table_html += '<tr style="{}">'.format(color)
                    table_html += '<td>{}. </td>'.format(str(index))
                    table_html += '<td>{}</td>'.format(current_date)
                    last_date = current_date
                
                if change.asin in asin_to_url:
                    table_html += '<td><a href="{0}" target="_blank">{1}</a></td>'.format(asin_to_url[change.asin], change.asin)
                else:
                    table_html += '<td>{}</td>'.format(change.asin)
                
                first_property_change = True
                for property_name, (change_from, change_to) in change.change_history.iteritems():
                    if not first_property_change:
                        table_html += '</tr>'
                        table_html += '<tr style="{}">'.format(color)
                        table_html += '<td class="table_empty_td"></td>'    # index
                        table_html += '<td class="table_empty_td"></td>'    # same date
                        table_html += '<td class="table_empty_td"></td>'    # same ASIN
                    first_property_change = False 
                    table_html += '<td>{}</td>'.format(property_name)
                    table_html += '<td>{}</td>'.format(str(change_from))
                    table_html += '<td>{}</td>'.format(str(change_to))
                        
                table_html += '</tr>'
                
                index += 1
                
            table_html += '</table>'
        else:
            table_html = 'No changes found'

        html += table_html
        html += '<br><br>'
        
        
        html += '<h2>Products performance changes</h2>'
        formatter = RankFormatterFactory.create('table_report')
        now = datetime.datetime.utcnow()
        week_ago = now - datetime.timedelta(days=7)
        
        list_keywords = db_access_layer.getKeywords()
        
        service = RankReportService(db_access_layer)
        
        list_asin_reports = service.reportRank(week_ago, now, asin_list, list_keywords)
        as_json = formatter.format(list_asin_reports, list_keywords)
        report = json.loads(as_json)
        rows = report['rows']
        columns = report['columns']
        
        table_html = '<table border="1" style="width:800px; text-align:center;">'
        table_html += '<tr>'
        for column in columns:
            table_html += '  <th style="color: #ffffff; background-color: #555555;padding: 3px;">{}</th>'.format(column)
        table_html += '</tr>'
        last_date = None
        for row in rows:
            if color == 'background-color: #FFFFFF;':
                color = 'background-color: #E8E8E8;'
            else:
                color = 'background-color: #FFFFFF;'
            table_html += '<tr style="{}">'.format(color)
            is_asin_column = True
            for field in row:
                if is_asin_column and field in asin_to_url:
                    table_html += '<td><a href="{0}" target="_blank">{1}</a></td>'.format(asin_to_url[field], field)
                else:
                    table_html += '<td>{}</td>'.format(field)
                is_asin_column = False
            table_html += '</tr>'
        table_html += '</table>'
        html += table_html
        
        logging.debug('sending email...')
        mail.send_mail(sender = 'Baziliq <info@amazon-competitor-analisys.appspotmail.com>', 
                       to = ['povichu4er@gmail.com'], 
                       subject = 'Daily Report', 
                       body = "",
                       html = html)
        
        self.response.write(html)
        
        
        
        
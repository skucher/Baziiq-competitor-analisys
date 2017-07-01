import json

FORMATTER_KEY = '_formatter'
def get_result_for_keyword(asin_report, keyword):
    result = asin_report.dict_keyword_ranks.get(keyword)
    if not result:
        return 'NA', None
    return result

class RankFormatterFactory(object):
    
    @staticmethod
    def create(report_type):
        if report_type == 'table_report':
            return RankTableFormatter()
        if report_type == 'table_chart_report':
            return RankTableChartFormatter()


class RankTableFormatter(object):  
    '''
    prepares table:
    columns - 'Asin', 'Bsr', + list_keywords
    rows - asin, bsrs joined by '->', keyword_order joined by '->'
    '''



    def format(self, list_asin_reports, list_keywords):        
        
        columns = ['Asin', 'Bsr']
        columns.extend(list_keywords)
        
        rows = []
        for asin, asin_report in list_asin_reports:
            row = []
            row.append(asin)
            row.append(' -> '.join(str(bsr) for bsr,_ in asin_report.list_bsr_ranks))           
            
            for keyword in list_keywords:
                try:
                    row.append(' -> '.join(str(order) for order,_ in get_result_for_keyword(asin_report, keyword)))
                except Exception, e:
                    print e
            
            rows.append(row)
        
        dict_res = {'columns':columns, 'rows': rows}
        
        return json.dumps(dict_res)

                
class RankTableChartFormatter(object): 
               
    '''
    prepares table:
    rows - asin, <div> for bsr result, <div> for keyword result
    columns - 'Asin', 'Bsr', 'Keywords'
    asins_data - list of dictionaries
        bsrs - day, bsr tuple list
        asin - is asin
        keyword_rows - list
            day, asin_day_result_for_keyword
    '''
    def format(self, list_asin_reports, list_keywords):       
        columns = ['Asin', 'Bsr', 'Keywords']
        rows = []
        for asin, asin_report in list_asin_reports:
            row = []
            row.append(asin)
            row.append('<div id="baziliq_result_bsr_%s"></div>' % asin)
            row.append('<div id="baziliq_result_keywords_%s"></div>' % asin)          
            rows.append(row)
        
        asins_data = []        
        for asin, asin_report in list_asin_reports:
            curr_asin_data = {}            
            curr_asin_data['bsrs'] = [(date.day, bsr) for bsr, date in asin_report.list_bsr_ranks]
            curr_asin_data['asin'] = asin
            day_to_keywords = {}
            for keyword in list_keywords:
                for order, date in get_result_for_keyword(asin_report, keyword):
                    day_to_keywords.setdefault(date.day, {})[keyword] = order
            keyword_rows = []
            items = day_to_keywords.items()
            sorted_items = sorted(items, key=lambda tpl:tpl[0])
            for day, day_results in sorted_items:
                keyword_row = []
                keyword_row.append(day)
                keyword_row.extend([day_results[keyword] for keyword in list_keywords])
                keyword_rows.append(keyword_row)
            
            curr_asin_data['keyword_rows'] = keyword_rows
            
            asins_data.append(curr_asin_data)
        
        dict_res = {'columns':columns, 'rows': rows, 'asins_data':asins_data, 'keyword_names': list_keywords}
        
        return json.dumps(dict_res)
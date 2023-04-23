# -*- coding: utf-8 -*-

from odoo.addons.web.controllers import main as report
from odoo.http import content_disposition, route, request
from odoo.tools.safe_eval import safe_eval
from odoo.tools.safe_eval import safe_eval, datetime, dateutil, time
import json


class ReportController(report.ReportController):
    @route()
    def report_download(self, data, context=None):
        requestcontent = json.loads(data)
        url, type = requestcontent[0], requestcontent[1]
        if type == 'xlsx':
            converter = 'xlsx'
            pattern = '/report/xlsx/'
            reportname = url.split(pattern)[1].split('?')[0]
            docids = None
            if '/' in reportname:
                reportname, docids = reportname.split('/')
                if docids:
                    response = self.report_routes(reportname, docids=docids, converter=converter, context=context)
                    return response

        return super(ReportController, self).report_download(data, context)
        
    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == 'xlsx':
            report = request.env['ir.actions.report']._get_report_from_name(reportname)
            context = dict(request.env.context)
            if docids:
                docids = [int(i) for i in docids.split(',')]
            if data.get('options'):
                data.update(json.loads(data.pop('options')))
            if data.get('context'):
                data['context'] = json.loads(data['context'])
                if data['context'].get('lang'):
                    del data['context']['lang']
                context.update(data['context'])

            xlsx = report.with_context(context).render_xlsx(docids, data=data)[0]
            filename = "odoo_report" + '.xlsx'
            if docids and report.print_report_name:
                report_name = safe_eval(report.print_report_name,
                                        {'object': request.env[report.model].browse(docids[0]), 'time': time})
                filename = "%s.%s" % (report_name, 'xlsx')
            xlsxhttpheaders = [
                ('Content-Type', 'application/vnd.openxmlformats-'
                                 'officedocument.spreadsheetml.sheet'),
                ('Content-Length', len(xlsx)),
                (
                    'Content-Disposition',
                    content_disposition(filename)
                )
            ]
            return request.make_response(xlsx, headers=xlsxhttpheaders)

        return super(ReportController, self).report_routes(reportname, docids, converter, **data )

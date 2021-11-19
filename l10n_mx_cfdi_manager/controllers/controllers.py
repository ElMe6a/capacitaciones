# -*- coding: utf-8 -*-
# from odoo import http


# class L10nMxCfdiManager(http.Controller):
#     @http.route('/l10n_mx_cfdi_manager/l10n_mx_cfdi_manager/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_mx_cfdi_manager/l10n_mx_cfdi_manager/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_mx_cfdi_manager.listing', {
#             'root': '/l10n_mx_cfdi_manager/l10n_mx_cfdi_manager',
#             'objects': http.request.env['l10n_mx_cfdi_manager.l10n_mx_cfdi_manager'].search([]),
#         })

#     @http.route('/l10n_mx_cfdi_manager/l10n_mx_cfdi_manager/objects/<model("l10n_mx_cfdi_manager.l10n_mx_cfdi_manager"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_mx_cfdi_manager.object', {
#             'object': obj
#         })

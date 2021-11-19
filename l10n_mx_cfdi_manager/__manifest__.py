# -*- coding: utf-8 -*-
{
    'name': "l10n_mx_cfdi_manager",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'contacts',
        'account_accountant',
        'l10n_mx',
        'l10n_mx_edi',
        'l10n_mx_reports',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        
        'views/account_move.xml',
        'views/l10n_mx_cfdi_document.xml',
        'views/l10n_mx_cfdi_manager.xml',
        'views/l10n_mx_cfdi_request.xml',
        'views/l10n_mx_cfdi_fiel.xml',
#         'views/l10n_mx_cfdi_efos.xml',
        'views/res_company.xml',
        'views/cron_verificar_solicitudes_auto.xml',
        'views/cron_descargar_solicitudes_auto.xml',
        'views/cron_verificar_cfdi_states.xml',
        'views/cron_daily_request.xml',
        'views/cron_daily_efos.xml',
#         'views/cron_prueba.xml',
        'views/wizard_l10n_mx_cfdi_document.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

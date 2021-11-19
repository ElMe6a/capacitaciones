# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time
import datetime
import pytz
import logging
import tempfile
import base64


import OpenSSL
import time
from dateutil import parser

_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError , UserError

class res_company_inheritance(models.Model):
    _inherit = 'res.company'
    _description = 'Modelo para agregar los certificados'
    
    fiel_ids=fields.One2many(
        'l10n_mx.cfdi_fiel',
        'company_id',
        string="FIEL"
    )
    
    sat_account_journal_id = fields.Many2one(
        'account.journal',
        string = 'diario',
        domain = "[('type','=','purchase')]"
    )
    
#     @api.onchange('fiel_ids')
#     def read_cer_file(self):
#         file_path = tempfile.gettempdir()+'/cerfile.cer'
#         f = open(file_path,'wb')
#         f.write(base64.decodestring(self.fiel_ids[0].clave))
#         f.close()
#         cer_der = open(file_path, 'rb').read()
        
#         cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cer_der)
#         certIssue = cert.get_issuer()
        
#         datetime_struct_from = parser.parse(cert.get_notBefore().decode("UTF-8"))
#         datetime_struct = parser.parse(cert.get_notAfter().decode("UTF-8"))
        
#         raise UserError(datetime_struct.strftime('%Y-%m-%d %H:%M:%S'))
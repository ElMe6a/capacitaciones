# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import os
import csv
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError , UserError

_EFOS_DOWNLOAD_PATH_ROOT = '/home/odoo/data/filestore/EFOS/'

class l10n_mx_cfdi_fiel(models.Model):
    _name = 'l10n_mx.cfdi_efos'
    _description = 'Modelo para efos'
    
    status = fields.Char(
        string="Situación del contribuyente"
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string="Proveedor",
        required=True
    )    
    
    def download_efos_list_sat(self):
        if not os.path.exists(_EFOS_DOWNLOAD_PATH_ROOT):
            os.makedirs(_EFOS_DOWNLOAD_PATH_ROOT)
        
        url = 'http://omawww.sat.gob.mx/cifras_sat/Documents/Listado_Completo_69-B.csv'
        r = requests.get(url, allow_redirects=True)
        filename = url.split('/')[-1]
        open(_EFOS_DOWNLOAD_PATH_ROOT+filename, 'wb').write(r.content)
        
#         datafile = open(_EFOS_DOWNLOAD_PATH_ROOT+filename, 'r', encoding='latin-1')
#         myreader = csv.reader(datafile)
        partners_list = self.env['res.partner'].search([])
        
        self.env.cr.execute("""select distinct vat from res_partner;""")
        
        rfc_list = self.env.cr.dictfetchall()
        
        for rfc in rfc_list:
            if rfc['vat'] != None:
                datafile = open(_EFOS_DOWNLOAD_PATH_ROOT+filename, 'r', encoding='latin-1')
                myreader = csv.reader(datafile)
                for line in myreader:
                    if rfc['vat'] == line[1]:
                        partner = self.env['res.partner'].search([('vat','=',rfc['vat']),('is_company','=','t')])
                        
                        partner_efo = self.env['l10n_mx.cfdi_efos'].search([('partner_id','=',partner.id)])
                        
                        if partner_efo:
                            partner_efo.write({
                                'status': line[3]
                            })
                        else:
                            self.env['l10n_mx.cfdi_efos'].create({
                                'status': line[3],
                                'partner_id': partner.id
                            })
# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError , UserError

class WizardMoveDocument(models.TransientModel):

    _name = 'l10n_mx.cfdi_document_wizard'
    _description = 'Wizard para vincular documento cfdi a moves'
    
    move_id = fields.Integer(
        string="Factura"
    )
    date = fields.Date(
        string="Fecha"
    )
    cfdi_document=fields.Many2one(
        'l10n_mx.cfdi_document',
        string="Documento cfdi"
    )
    total=fields.Float(
        string="Total",
        related='cfdi_document.total'
    )
    metadata=fields.Text(
        string="Metadata",
        related='cfdi_document.metadata_pretty'
    )
    
    def event_wizard(self):
        if self.cfdi_document != False:
            move = self.env['account.move'].search([('id','=',self.move_id)])
            move.write({
                'cfdi_document':self.cfdi_document.id
            })
        else:
            raise UserError("Seleccione un documento")
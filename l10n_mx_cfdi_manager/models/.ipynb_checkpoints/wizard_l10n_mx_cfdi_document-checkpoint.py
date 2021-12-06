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
        if self.cfdi_document:
            move = self.env['account.move'].search([('id','=',self.move_id)])
            if self.cfdi_document.rfc_emisor != move.partner_id.vat:
                raise UserError("RFC de documento CFDI no corresponde al del proveedor")
                
            if self.cfdi_document.total != move.amount_total:
                _logger.warning(abs(self.cfdi_document.total - move.amount_total))
                if round(abs(self.cfdi_document.total - move.amount_total),2) > 0.05:
                    raise UserError("Difeerencia es mayor a 0.05 centavos")
            
            move.write({
                'cfdi_document':self.cfdi_document.id
            })
            
            self.cfdi_document.write({
                'link_state':'link'
            })
        else:
            raise UserError("Seleccione un documento")
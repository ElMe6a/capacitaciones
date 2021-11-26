# -*- coding: utf-8 -*-

from odoo import models, fields, api


class l10n_mx_cfdi_manager(models.Model):
    _inherit = 'account.move'
    _description = 'Herencia para relacion cfdi - facturas'
    
    cfdi_document=fields.Many2one(
        'l10n_mx.cfdi_document',
        string="Documento relacionado"
    )
    date=fields.Date(
        string="Fecha"
    )
    
    def asignar_cfdi(self):
        context = {
            'default_move_id': self.id,
        }
            
        return {
            # Retorno una vista formulario
            'name': 'Relacionar Documento',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('l10n_mx_cfdi_manager.wz_account_move_related_doc').id,
            'res_model': 'l10n_mx.cfdi_document_wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
    
    def unlink_cfdi(self):
        for rec in self:
            rec.cfdi_document.write({
                'link_state':'unlink'
            })
            rec.cfdi_document = False
# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time
import datetime
import pytz
import logging
import io
import base64
from xml.dom import minidom
from xml.etree import ElementTree
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError , UserError
from cfdiclient import Autenticacion, Fiel, SolicitaDescarga, VerificaSolicitudDescarga, DescargaMasiva, Validacion

class l10n_mx_cfdi_document(models.Model):
    _name = 'l10n_mx.cfdi_document'
    _description = 'Modelo de documentos'
    _order = 'id desc'
    
    cfdi_request=fields.Many2one(
        'l10n_mx.cfdi_request',
        string="Solicitud CFDI"
    )
    uuid=fields.Char(
        string="UUID"
    )
    partner_id=fields.Many2one(
        'res.partner',
        string="ID de socio"
    )
    cfdi_state=fields.Char(
        string="Estado CFDI"
    )
    attatch=fields.Binary(
        string="Adjunto"
    )
    attatch_name=fields.Char(
        string="Nombre del archivo"
    )
    company_id=fields.Many2one(
        'res.company',
        string="ID de compañía"
    )
    rfc_emisor=fields.Char(
        string="RFC Emisor"
    )
    emisor=fields.Char(
        string="Emisor"
    )
    rfc_receptor=fields.Char(
        string="RFC Receptor"
    )
    total=fields.Float(
        string="Total"
    )
    metadata=fields.Text(
        string="Metadata"
    )
    
    moves_ids=fields.One2many(
        'account.move',
        'cfdi_document',
        string="Factura relacionada"
    ) 
    date=fields.Date(
        string="Fecha"
    )
    
    metadata_pretty = fields.Text(
        string="Metadata",
        compute='_pretty_xml_data'
    )
    
    folio = fields.Char(
        string="Folio"
    )
    
    link_state = fields.Selection([
        ('link', 'Vinculado'),
        ('unlink', 'No vinculado')],
        default='unlink'
#         compute = "_is_doc_linked",
#         store=True
    )
    
    type_comprobante = fields.Selection([
        ('I', 'Ingreso'),
        ('E', 'Egreso'),
        ('T', 'Traslado'),
        ('p', 'Pago'),
        ('N', 'Nomina')],
        string="Tipo de documento",
        default="I"
    )
    
    def _is_doc_linked(self):
        for rec in self:
            if rec.moves_ids:
                rec.link_state = 'link'
            else:
                rec.link_state = 'unlink'
    
    def _pretty_xml_data(self):
        for rec in self:
            xml_data = minidom.parseString(rec.metadata)
            rec.metadata_pretty = xml_data.toprettyxml()
    
    def _extract_metada(self):
        for rec in self:
            with io.BytesIO(base64.b64decode(self.attatch)) as xml_data:
                xml = minidom.parse(xml_data)
                self.write({
                    'metadata':xml.toxml()
                })
    
    def verify_state(self):            
        validacion = Validacion()
        estado = validacion.obtener_estado(self.rfc_emisor, self.rfc_receptor, str(self.total), self.uuid)
        self.write({
            'cfdi_state': estado['estado']
        })
        
    def automated_cfdi_state(self):
        cfdi_documents = self.env['l10n_mx.cfdi_document'].search([])
        for document in cfdi_documents:
            document.verify_state()
    
    def name_get(self):
        result = []
        for document in self:
            result.append((document.id,document.uuid))
        return result
        
    def _read_cfdi(self,data):
        with io.BytesIO(base64.b64decode(data)) as xml_data:
            xml = minidom.parse(xml_data)
            
            UUID = xml.getElementsByTagName('tfd:TimbreFiscalDigital')[0].getAttribute('UUID')
            EMISOR = xml.getElementsByTagName('cfdi:Emisor')[0].getAttribute('Nombre')
            RFC_EMISOR = xml.getElementsByTagName('cfdi:Emisor')[0].getAttribute('Rfc')
            RFC_RECEPTOR = xml.getElementsByTagName('cfdi:Receptor')[0].getAttribute('Rfc')
            TOTAL = xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('Total')
            DATE = xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('Fecha').split('T')
            METODO_PAGO = xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('CondicionesDePago')
            CONCEPTOS = xml.getElementsByTagName('cfdi:Concepto')
            
            validacion = Validacion()
            estado = validacion.obtener_estado(RFC_EMISOR, RFC_RECEPTOR, TOTAL, UUID)
            
            return {
                'uuid': UUID,
                'cfdi_state': estado['estado'],
                'rfc_emisor': RFC_EMISOR,
                'emisor': EMISOR,
                'rfc_receptor': RFC_RECEPTOR,
                'total': float(TOTAL),
                'date': DATE,
                'metodo_pago': METODO_PAGO,
                'conceptos':CONCEPTOS
            }
        
    def create_bill(self):
        data = self._read_cfdi(self.attatch)
        if data['rfc_receptor'] == self.env.company.vat:
            partner = self.env['res.partner'].search([('vat','=',data['rfc_emisor']),('is_company','=',True)])
            if not partner:
                try:
                    partner = self.env['res.partner'].create({
                        'name': data['emisor'],
                        'vat': data['rfc_emisor']
                    })
                except:
                    pass
            payment_term = self.env['account.payment.term'].with_context(lang='es_MX').search([('name', '=', data['metodo_pago'])])
            account_move = self.env['account.move'].create({
                'invoice_date': datetime.datetime.strptime(data['date'][0],'%Y-%m-%d'),
                'date': datetime.datetime.strptime(data['date'][0],'%Y-%m-%d'),
                'state': 'draft',
                'move_type': 'in_invoice',
                'extract_state': 'no_extract_requested',
                'journal_id': self.env.company.sat_account_journal_id.id,
                'l10n_mx_edi_sat_status': 'undefined',
                'currency_id': self.env.company.currency_id.id,
                'invoice_payment_term_id': payment_term.id if payment_term else None,
                'cfdi_document': self.id
            })
            
            move_lines_list = self.env['account.move.line']

            lines = []
            
            for concepto in data['conceptos']:
                importe = concepto.getAttribute('Importe')
                is_gasoline = False
                base = 0.0
                tasas = []
                rets = []
                traslados = concepto.getElementsByTagName('cfdi:Traslado')
                retenciones = concepto.getElementsByTagName('cfdi:Retencion')
                for traslado in traslados:
                    base = traslado.getAttribute('Base')
                    if traslado.getAttribute('TipoFactor') == 'Tasa':
                        tasas.append(float(traslado.getAttribute('TasaOCuota'))*100)
                    if float(base) != importe and concepto.getAttribute('Unidad') == 'Litro':
                        is_gasoline = True
                for retencion in retenciones:
                    if traslado.getAttribute('TipoFactor') == 'Tasa':
                        rets.append(round(-float(retencion.getAttribute('TasaOCuota'))*100,2))
                lines.append({
                    'importe':importe,
                    'base': base,
                    'tasas': tasas if tasas else [0.00],
                    'retenciones':rets if rets else [0.00],
                    'is_gasoline':is_gasoline,
                    'description':concepto.getAttribute('Descripcion')
                })
                
            for line in lines:
                if line['is_gasoline']:
                    tax_list = self.env['account.tax'].search(['&',('amount','in',line['tasas']),('type_tax_use','=','purchase'),('cash_basis_transition_account_id.company_id.id','=',self.env.company.id)])
                    
                    move_line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                        'name': "Saldo pendiente " + line['description'] + " Tasa",
                        'move_id': account_move.id,
                        'quantity':  1,
                        'price_unit': float(line['base']),
                        'tax_ids': tax_list.ids,
                        'journal_id': self.env.company.sat_account_journal_id.id,
                        'account_id': 34,
                    })
                    move_lines_list += move_line

                    move_line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                        'name': "Saldo pendiente " + ''.format(float(line['importe'])-float(line['base'])) + " Tasa",
                        'move_id': account_move.id,
                        'quantity':  1,
                        'price_unit': float(line['importe']) - float(line['base']),
                        'tax_ids': [9],
                        'journal_id': self.env.company.sat_account_journal_id.id,
                        'account_id': 34,
                    })
                    move_lines_list += move_line
                    
                else:
                    rets_id = []
                    for ret in line['retenciones']:
                        if ret == -4.00:
                            rets_id.append(3)
                        elif ret == -10.00:
                            rets_id.append(4)
                        elif ret == -10.67:
                            rets_id.append(8)
                    tax_list = self.env['account.tax'].search(['&',('amount','in',line['tasas']),('type_tax_use','=','purchase'),('cash_basis_transition_account_id.company_id.id','=',self.env.company.id)])
                    tax_rets = self.env['account.tax'].search([('id','in',rets_id)])

                    tax_list = tax_list + tax_rets

                    move_line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                        'name': "Saldo pendiente " + line['description'] + " Tasa",
                        'move_id': account_move.id,
                        'quantity':  1,
                        'price_unit': float(line['importe']),
                        'tax_ids': tax_list.ids,
                        'journal_id': self.env.company.sat_account_journal_id.id,
                        'account_id': 34,
                    })
                    move_lines_list += move_line
                
            account_move.with_context(check_move_validity=False).write({
                'invoice_line_ids':move_lines_list.ids,
            })
                
            diferencia = data['total']-account_move.amount_total
            if  diferencia == 0:
                account_move.message_post(
                    body='FACTURA creada a partir de CFDI <b>[{}]</b>. \nTotal CFDI: <b>{}</b> \nTotal FACTURA: <b>{}</b>'.format(
                        data['uuid'],
                        data['total'],
                        '{:20,.2f}'.format(account_move.amount_total)
                    )
                )
            else:
                account_move.message_post(
                    body = 'FACTURA creada a partir de CFDI <b>[{}]</b>. \nTotal CFDI: <b>{}</b> \nTotal FACTURA: <b>{}</b> \nDiferencia: <b>{}</b>'.format(
                        data['uuid'],
                        data['total'],
                        '{:20,.2f}'.format(account_move.amount_total),
                        '{:20,.2f}'.format(abs(diferencia))
                    )
                )

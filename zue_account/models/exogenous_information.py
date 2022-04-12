from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _

import base64
import io
import xlsxwriter
import math

#Código fiscal
class fiscal_accounting_code_details(models.Model):
    _name = 'fiscal.accounting.code.details'
    _description = 'Código Fiscal - Cuentas'

    fiscal_accounting_id = fields.Many2one('fiscal.accounting.code',string='Código fiscal', required=True)
    account_id = fields.Many2one('account.account',string='Cuenta', required=True)
    move_type = fields.Selection([('debit', 'Débito'),
                                     ('credit', 'Crédito'),
                                     ('net', 'Neto')], string='Tipo de movimiento', required=True)

    _sql_constraints = [('fiscal_account_id_uniq', 'unique(fiscal_accounting_id,account_id)',
                         'Ya existe la cuenta en este código fiscal, por favor verficar.')]

class fiscal_accounting_code(models.Model):
    _name = 'fiscal.accounting.code'
    _description = 'Código Fiscal'
    _rec_name = 'code_description'

    company_id = fields.Many2one('res.company', string='Compañía', readonly=True, required=True,
                                 default=lambda self: self.env.company)
    concept_dian = fields.Char(string="Código Fiscal", required=True)
    code_description = fields.Char(string="Descripción del Código", required=True)
    format_id = fields.Many2one('format.encab', string='Formato')
    #concept = fields.Char(string="Concepto")
    account_type = fields.Selection([('movement', 'Movimiento'),
                              ('balance', 'Balance'),
                              ], 'Tipo de cuenta')
    move_type = fields.Selection([('debit', 'Débito'),
                                  ('credit', 'Crédito'),
                                  ('net', 'Neto')], string='Tipo de movimiento', required=True)
    #account_code = fields.Char(string="Código de cuenta")
    accounting_details_ids = fields.Many2many('account.account',string='Cuentas')
    #excluded_documents_ids = fields.Many2many('account.journal', string="Documentos Excluidos")
    #fiscal_group_id = fields.Many2one('fiscal.accounting.group',string="Grupo Fiscal")

    _sql_constraints = [('fiscal_code_uniq', 'unique(company_id,concept_dian)',
                         'El concepto DIAN digitado ya esta registrado para esta compañía, por favor verificar.')]

#Grupo Fiscal
class fiscal_accounting_group(models.Model):
    _name = 'fiscal.accounting.group'
    _description = 'Grupo Fiscal'
    _rec_name = 'group_description'

    company_id = fields.Many2one('res.company', string='Compañía', readonly=True, required=True,
                                 default=lambda self: self.env.company)
    fiscal_group = fields.Char(string="Grupo Fiscal", required=True)
    group_description = fields.Char(string="Descripción del Grupo", required=True)
    operator = fields.Selection([('>', 'Mayor que'),
                              ('<', 'Menor que'),
                              ('=', 'Igual que'),
                              ('!=', 'Distinto de'),
                              ('<=','Menor o igual que'),
                              ('>=', 'Mayor o igual que'),
                              ], 'Operador')
    amount = fields.Float(string="Monto")
    tax_type = fields.Selection([('dian', "DIAN Art 631"),
                              ('treasury', "Tesoreria Distrital"),
                              ], "Tipo de impuesto")
    concept_dian_ids = fields.Many2many('fiscal.accounting.code', string="Códigos Fiscales")
    excluded_thirdparty_ids = fields.Many2many('res.partner', string="Tercero Excluido")
    partner_minor_amounts = fields.Many2one('res.partner', string="Tercero Cuantías menores")

    _sql_constraints = [('fiscal_group_uniq', 'unique(company_id,fiscal_group)',
                         'El grupo fiscal digitado ya esta registrado para esta compañía, por favor verificar.')]


class format_encab(models.Model):
    _name = 'format.encab'
    _description = 'Formato de Código Fiscal Encabezado'

    format_id = fields.Char(string="Código Formato", required=True)
    description = fields.Char(string="Descripción del formato", required=True)
    details_ids = fields.One2many('format.detail','format_id',string = 'Campos Disponibles')
    company_id = fields.Many2one('res.company', string='Compañía', readonly=True, required=True,default=lambda self: self.env.company)
    format_associated_id = fields.Many2one('format.encab', string='Formato Asociado')
    fields_associated_code_fiscal_ids = fields.Many2many('fiscal.accounting.code', string='Conceptos Asociados')

    _sql_constraints = [('format_encab_uniq', 'unique(format_id,company_id)',
                         'El formato fiscal digitado ya esta registrado para esta compañía, por favor verificar.')]

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{}/{}".format(record.format_id,record.description)))
        return result

    @api.onchange('format_associated_id')
    def get_code_fiscal(self):
        for record in self:
            record.fields_associated_code_fiscal_ids = self.env['fiscal.accounting.code'].search(
                [('format_id', '=', self.format_associated_id.id), ('format_id', '!=', False)]).ids

class format_detail(models.Model):
    _name = 'format.detail'
    _description = 'Formato de Código Fiscal Detalle'

    format_id = fields.Many2one('format.encab',string='Código Formato', required=True, ondelete='cascade')
    sequence = fields.Integer(string="Secuencia", required=True)
    available_fields = fields.Selection([('fiscal_accounting_id', 'Concepto Fiscal'),
                              ('concept_dian',  'Concepto DIAN'),
                              ('format',  'Formato Archivo'),
                              ('x_document_type', 'Tipo Documento Tercero'),
                              ('vat', 'Número Documento Tercero'),
                              ('x_first_name', 'Primer Nombre'),
                              ('x_second_name', 'Segundo Nombre'),
                              ('x_first_lastname', 'Primer Apellido'),
                              ('x_second_lastname', 'Segundo Apellido'),
                              ('commercial_company_name', 'Razón Social'),
                              ('x_digit_verification', 'Dígito de Verificación'),
                              ('street', 'Dirección'),
                              ('state_id', 'Código Departamento'),
                              ('x_city', 'Código Ciudad'),
                              ('amount', 'Valor Pesos'),
                              ('operator', 'Operador'),
                              ('tax', 'Base Impuestos'),
                              ('x_code_dian', 'Código País DIAN'),
                              ('phone', 'Teléfono Tercero'),
                              ('unit_rate', 'Tarifa Aplicada'),
                              ('email', 'Email'),
                              ('higher_value_iva', 'Mayor Valor Iva'),
                              ], 'Campos Seleccionados', required=True)

class generate_media_magnetic(models.TransientModel):
    _name = 'generate.media.magnetic'
    _description = 'Generar Medios Magneticos'

    company_id = fields.Many2one('res.company',string='Compañia', required=True, default=lambda self: self.env.company)
    type_media_magnetic = fields.Selection([('dian', 'Generar Artículo 631'),
                                            ('distrital', 'Generar Impuesto Distrital')],'Tipo de medio magnético', default='dian')
    year =  fields.Integer(string="Año", required=True)

    excel_file = fields.Binary('Excel file')
    excel_file_name = fields.Char('Excel name')

    def generate_media_magnetic_dian(self):
        #Variables excel
        filename = f'MedioMagtenico_{str(self.year)}.xlsx'
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})
        #Variables proceso
        date_start = str(self.year) +'-01-01'
        date_end = str(self.year) +'-12-31'
        date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_end = datetime.strptime(date_end, '%Y-%m-%d').date()

        #Traer todos los formatos
        obj_formats = self.env['format.encab'].search([('id','!=',False)])

        for format in obj_formats:
            obj_account_fiscal = self.env['fiscal.accounting.code'].search([('format_id','=',format.id)])
            lst_Mvto = []
            for fiscal in obj_account_fiscal:
                obj_group_fiscal = self.env['fiscal.accounting.group'].search([('concept_dian_ids', 'in', fiscal.ids)],
                                                                              limit=1)
                format_fields = fiscal.format_id.details_ids

                partner_ids = self.env['account.move.line'].search([('date', '>=', date_start), ('date', '<=', date_end),
                                                                      ('account_id', 'in', fiscal.accounting_details_ids.ids)]).partner_id.ids
                obj_partner_ids = self.env['res.partner'].search([('id','in',partner_ids)])

                for partner in obj_partner_ids:
                    moves = self.env['account.move.line'].search(
                        [('date', '>=', date_start), ('date', '<=', date_end),
                         ('account_id', 'in', fiscal.accounting_details_ids.ids),('partner_id', '=', partner.id)])

                    amount = 0
                    tax_base_amount = 0
                    for i in moves:
                        if fiscal.move_type == 'debit':
                            amount += i.debit
                        elif fiscal.move_type == 'credit':
                            amount += i.credit
                        else:
                            amount += i.balance
                        tax_base_amount += i.tax_base_amount

                    #Armamos el dict con la información
                    dict_documents = dict(self.env['res.partner']._fields['x_document_type'].selection)
                    document_type = dict_documents.get(partner.x_document_type) if partner.x_document_type else ''
                    info = {'fiscal_accounting_id': fiscal.concept_dian,
                             'concept_dian': fiscal.code_description,
                             'format':fiscal.format_id.format_id,
                             'x_document_type': document_type,
                             'vat': partner.vat,
                             'x_first_name': partner.x_first_name,
                             'x_second_name': partner.x_second_name,
                             'x_first_lastname': partner.x_first_lastname,
                             'x_second_lastname': partner.x_second_lastname,
                             'commercial_company_name': partner.name,
                             'x_digit_verification': partner.x_digit_verification,
                             'street': partner.street,
                             'state_id': partner.state_id.name,
                             'x_city': partner.x_city.name,
                             'amount': amount,
                             'operator':obj_group_fiscal.operator,
                             'tax': tax_base_amount,
                             'x_code_dian':partner.x_city.code,
                             'phone': partner.phone or partner.mobile,
                             'unit_rate': 0,
                             'email': partner.email,
                             'higher_value_iva': 0,
                          }
                    #Formatos asociados
                    info_associated = {}
                    obj_account_fiscal_associated = self.env['fiscal.accounting.code'].search([('format_id', '=', format.format_associated_id.id)])
                    for fiscal_associated in obj_account_fiscal_associated:
                        moves_associated = self.env['account.move.line'].search(
                            [('date', '>=', date_start), ('date', '<=', date_end),
                             ('account_id', 'in', fiscal_associated.accounting_details_ids.ids), ('partner_id', '=', partner.id)])
                        amount_associated = sum([i.balance for i in moves_associated])
                        name_associated = fiscal_associated.code_description.replace(' ','_')
                        info_associated[name_associated] = amount_associated
                    #Guardado final
                    media_magnetic = {}
                    for field in sorted(format_fields, key=lambda x: x.sequence):
                        if field.available_fields in info:
                            media_magnetic[field.available_fields] = info.get(field.available_fields)
                    lst_Mvto.append({**media_magnetic, **info_associated})
            #Generar hoja de excel
            sheet = book.add_worksheet(fiscal.format_id.format_id)
            columns = []
            for field in lst_Mvto[0].keys():
                field_name = dict(self.env['format.detail']._fields['available_fields'].selection).get(field,field.replace('_',' '))
                columns.append(field_name)
            # Agregar columnas
            aument_columns = 0
            for column in columns:
                sheet.write(0, aument_columns, column)
                aument_columns = aument_columns + 1
            # Agregar valores
            aument_columns = 0
            aument_rows = 1
            for info in lst_Mvto:
                for row in info.values():
                    width = len(str(row)) + 10
                    sheet.write(aument_rows, aument_columns, row)
                    # Ajustar tamaño columna
                    sheet.set_column(aument_columns, aument_columns, width)
                    aument_columns = aument_columns + 1
                aument_rows = aument_rows + 1
                aument_columns = 0

            # Convertir en tabla
            array_header_table = []
            for i in columns:
                dict_h = {'header': i}
                array_header_table.append(dict_h)
            sheet.add_table(0, 0, aument_rows-1, len(columns)-1, {'style': 'Table Style Medium 2', 'columns': array_header_table})

        book.close()
        self.write({
            'excel_file': base64.encodestring(stream.getvalue()),
            'excel_file_name': filename,
        })

        action = {
            'name': 'Export Medio magnetico información exogena',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=generate.media.magnetic&id=" + str(
                self.id) + "&filename_field=excel_file_name&field=excel_file&download=true&filename=" + self.excel_file_name,
            'target': 'self',
        }
        return action

    def generate_media_magnetic_distrital(self):
        date_start = str(self.year) +'-01-01'
        date_end = str(self.year) +'-12-31'
        lst_Mvto = []

    def generate_media_magnetic(self):
        if self.type_media_magnetic == 'dian':
            return self.generate_media_magnetic_dian()
        if self.type_media_magnetic == 'distrital':
            return self.generate_media_magnetic_distrital()

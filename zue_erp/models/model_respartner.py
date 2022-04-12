# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

#---------------------------Modelo RES-PARTNER / TERCEROS-------------------------------#
class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    type_account = fields.Selection([('A', 'Ahorros'), ('C', 'Corriente')], 'Tipo de Cuenta', required=True, default='A')
    is_main = fields.Boolean('Es Principal')
    
class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'name'

    #TRACK VISIBILITY OLD FIELDS
    vat = fields.Char(tracking=True)
    street = fields.Char(tracking=True)
    country_id = fields.Many2one(tracking=True)
    state_id = fields.Many2one(tracking=True)
    zip = fields.Char(tracking=True)
    phone = fields.Char(tracking=True)
    mobile = fields.Char(tracking=True)
    email = fields.Char(tracking=True)
    website = fields.Char(tracking=True)
    lang = fields.Selection(tracking=True)
    category_id = fields.Many2many(tracking=True)
    user_id = fields.Many2one(tracking=True)    
    comment = fields.Text(tracking=True)
    name = fields.Char(tracking=True)
    city = fields.Char(string='Descripción ciudad')

    #INFORMACION BASICA
    same_vat_partner_id = fields.Many2one('res.partner', string='Partner with same Tax ID', compute='_compute_no_same_vat_partner_id', store=False)
    x_type_thirdparty = fields.Many2many('zue.type_thirdparty',string='Tipo de tercero',required=True, tracking=True, ondelete='restrict', domain="['|',('is_company','=',is_company),('is_individual','!=',is_company)]") 
    x_document_type = fields.Selection([
                                        ('11', 'Registro civil de nacimiento'),
                                        ('12', 'Tarjeta de identidad'),
                                        ('13', 'Cédula de ciudadanía'),
                                        ('21', 'Tarjeta de extranjería'),
                                        ('22', 'Cedula de extranjería'),
                                        ('31', 'NIT'),
                                        ('41', 'Pasaporte'),
                                        ('42', 'Tipo de documento extranjero'),
                                        ('43', 'Sin identificación del exterior o para uso definido por la DIAN'),
                                        ('44', 'Documento de identificación extranjero persona jurídica')
                                    ], string='Tipo de documento', tracking=True)
    x_digit_verification = fields.Integer(string='Digito de verificación', tracking=True,compute='_compute_verification_digit', store=True)
    x_business_name = fields.Char(string='Nombre de negocio', tracking=True)
    x_first_name = fields.Char(string='Primer nombre', tracking=True)
    x_second_name = fields.Char(string='Segundo nombre', tracking=True)
    x_first_lastname = fields.Char(string='Primer apellido', tracking=True)
    x_second_lastname = fields.Char(string='Segundo apellido', tracking=True)
    
    #UBICACIÓN PRINCIPAL
    x_city = fields.Many2one('zue.city', string='Ciudad', tracking=True, ondelete='restrict')

    #CLASIFICACION
    x_organization_type = fields.Selection([('1', 'Empresa'),
                                            ('2', 'Universidad'),
                                            ('3', 'Centro de investigación'),
                                            ('4', 'Multilateral'),
                                            ('5', 'Gobierno'),
                                            ('6', 'ONG: Organización no Gubernamental')], string='Tipo de organización', tracking=True)
    x_work_groups = fields.Many2many('zue.work_groups', string='Grupos de trabajo', tracking=True, ondelete='restrict')
    x_sector_id = fields.Many2one('zue.sectors', string='Sector', tracking=True, ondelete='restrict')
    x_ciiu_activity = fields.Many2one('zue.ciiu', string='Códigos CIIU', tracking=True, ondelete='restrict')

    #GRUPO EMPRESARIAL
    x_is_business_group = fields.Boolean(string='¿Es un Grupo Empresarial?', tracking=True)
    x_name_business_group = fields.Char(string='Nombre Grupo Empresarial', tracking=True)

    #VINCULACION 
    x_active_vinculation = fields.Boolean(string='Estado de la vinculación', tracking=True)
    x_date_vinculation = fields.Date(string="Fecha de vinculación", tracking=True)
    x_type_vinculation = fields.Many2many('zue.vinculation_types', string='Tipo de vinculación', tracking=True, ondelete='restrict')
    #Campos Informativos
    x_acceptance_data_policy = fields.Boolean(string='Acepta política de tratamiento de datos', tracking=True)
    x_acceptance_date = fields.Date(string='Fecha de aceptación', tracking=True)
    x_not_contacted_again = fields.Boolean(string='No volver a ser contactado', tracking=True)
    x_date_decoupling = fields.Date(string="Fecha de desvinculación", tracking=True)
    x_reason_desvinculation_text = fields.Text(string='Motivo desvinculación') 
    
    #INFORMACION FINANCIERA
    x_asset_range = fields.Many2one('zue.asset_range', string='Rango de activos', tracking=True, ondelete='restrict')
    x_date_update_asset = fields.Date(string='Fecha de última modificación', compute='_date_update_asset', store=True, tracking=True)
    x_company_size = fields.Selection([
                                        ('1', 'Mipyme'),
                                        ('2', 'Pyme'),
                                        ('3', 'Mediana'),
                                        ('4', 'Grande')
                                    ], string='Tamaño empresa', tracking=True)

    #INFORMACION TRIBUTARIA
    x_tax_responsibilities = fields.Many2many('zue.responsibilities_rut', string='Responsabilidades Tributarias', tracking=True, ondelete='restrict')

    #INFORMACION COMERCIAL
    x_account_origin = fields.Selection([
                                        ('1', 'Campañas'),
                                        ('2', 'Eventos'),
                                        ('3', 'Referenciado'),
                                        ('4', 'Telemercadeo'),
                                        ('5', 'Web'),
                                        ('6', 'Otro')
                                    ], string='Origen de la cuenta', tracking=True)
    

    #INFORMACIÓN CONTACTO
    x_contact_type = fields.Many2many('zue.contact_types', string='Tipo de contacto', tracking=True, ondelete='restrict')
    x_contact_job_title = fields.Many2one('zue.job_title', string='Cargo', tracking=True, ondelete='restrict')
    x_contact_area = fields.Many2one('zue.areas', string='Área', tracking=True, ondelete='restrict')
    
    #INFORMACION FACTURACION ELECTRÓNICA
    x_email_invoice_electronic = fields.Char(string='Correo electrónico para recepción electrónica de facturas', tracking=True)

    #MANTENIMIENTO
    #is_work_place = fields.Boolean('Is Work Place?')

    @api.depends('x_asset_range')
    def _date_update_asset(self):
        for record in self:
            record.x_date_update_asset = fields.Date.today()

    @api.depends('vat')
    def _compute_no_same_vat_partner_id(self):
        for partner in self:
            partner.same_vat_partner_id = ""

    @api.depends('vat')
    def _compute_verification_digit(self):
        #Logica para calcular digito de verificación
        multiplication_factors = [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3]

        for partner in self:
            if partner.vat and partner.x_document_type == '31' and len(partner.vat) <= len(multiplication_factors):
                number = 0
                padded_vat = partner.vat

                while len(padded_vat) < len(multiplication_factors):
                    padded_vat = '0' + padded_vat

                # if there is a single non-integer in vat the verification code should be False
                try:
                    for index, vat_number in enumerate(padded_vat):
                        number += int(vat_number) * multiplication_factors[index]

                    number %= 11

                    if number < 2:
                        partner.x_digit_verification = number
                    else:
                        partner.x_digit_verification = 11 - number
                except ValueError:
                    partner.x_digit_verification = False
            else:
                partner.x_digit_verification = False

    #---------------Search
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if self._context.get('search_by_vat', False):
            if name:
                args = args if args else []
                args.extend(['|', ['name', 'ilike', name], ['vat', 'ilike', name]])
                name = ''
        return super(ResPartner, self).name_search(name=name, args=args, operator=operator, limit=limit)

    #Onchange
    # @api.onchange('x_type_thirdparty')
    # def _onchange_type_thirdparty(self):
    #     for record in self:
    #         if record.x_type_thirdparty:
    #             for i in record.x_type_thirdparty:
    #                 print(i.id)
    #                 if i.id == 2 and record.company_type == 'company':
    #                     raise UserError(_('Una compañia no puede estar catalogada como contacto, por favor verificar.')) 
        
    @api.onchange('email')
    def _onchange_email(self):
        for record in self:
            if record.email:
                if not '@' in str(record.email):
                    self.email = False
                    raise UserError(_('El correo digitado no es valido, por favor verificar.'))

    @api.onchange('vat')
    def _onchange_vatnumber(self):
        for record in self:
            if record.vat:
                lst_character = ['.',',','*','@','-','_','°','!','|','"','#','$','%','&','/','(',')','=','?','¡','¿','{','}','<','>','^','+','[',']','~']
                for character in lst_character:
                    if character in record.vat:
                        raise UserError(_('El campo número de documento no debe contener caracteres especiales.'))                    
                if record.x_document_type == '31' and len(record.vat) > 9:
                    raise UserError(_('El campo número de documento no debe tener mas de 9 dígitos cuando el tipo de documento es NIT.'))   

                obj = self.search([('x_type_thirdparty','in',[1,3]),('vat','=',record.vat)])
                if obj:
                    self.vat = ""
                    raise UserError(_('Ya existe un Cliente con este número de NIT.'))                    
                objArchivado = self.search([('x_type_thirdparty','in',[1,3]),('vat','=',record.vat),('active','=',False)])
                if objArchivado:
                    self.vat = ""
                    raise UserError(_('Ya existe un Cliente con este número de NIT pero se encuentra archivado.')) 
    
    #-----------Validaciones

    @api.depends('x_document_type')
    @api.onchange('x_document_type')
    def assign_identification_type(self):
        if self.x_document_type:
            label = ''
            kay_val_dict = dict(self._fields['x_document_type'].selection)
            for key, val in kay_val_dict.items():
                if key == self.x_document_type:
                    label = val
                    break

            obj_identification = self.env['l10n_latam.identification.type'].search([('name', '=', label)], limit=1)

            if obj_identification:
                self.l10n_latam_identification_type_id = obj_identification.id
            else:
                obj_identification = self.env['l10n_latam.identification.type'].search([('name', '=', 'NIT')], limit=1)
                self.l10n_latam_identification_type_id = obj_identification.id

    #Se elimina el campo vat de los commercial_fields cuando es un contacto hijo para que no herede la identificacion del padre
    @api.model
    def _commercial_fields(self):
        res = super(ResPartner, self)._commercial_fields()
        if self.parent_id:
            res.remove('vat')
        return res

    @api.constrains('vat')
    def _check_vatnumber(self):
        for record in self:
            cant_vat = 0
            cant_vat_archivado = 0
            cant_vat_ind = 0
            cant_vat_archivado_ind = 0
            name_tercer =  ''
            user_create = ''
            if record.vat:
                obj = self.search([('is_company', '=', True),('vat','=',record.vat)])
                if obj:
                    for tercer in obj:
                        cant_vat = cant_vat + 1
                        if tercer.id != record.id:
                            name_tercer = tercer.name
                            user_create = tercer.create_uid.name

                objArchivado = self.search([('is_company', '=', True),('vat','=',record.vat),('active','=',False)])
                if objArchivado:
                    for tercer in objArchivado:
                        cant_vat_archivado = cant_vat_archivado + 1
                        if tercer.id != record.id:
                            name_tercer = tercer.name
                            user_create = tercer.create_uid.name

                obj_ind = self.search([('is_company', '=', False),('vat','=',record.vat)])
                if obj_ind:
                    for tercer in obj_ind:
                        cant_vat_ind = cant_vat_ind + 1
                        if tercer.id != record.id:
                            name_tercer = tercer.name
                            user_create = tercer.create_uid.name

                objArchivado_ind = self.search([('is_company', '=', False),('vat','=',record.vat),('active','=',False)])
                if objArchivado_ind:
                    for tercer in objArchivado_ind:
                        cant_vat_archivado_ind = cant_vat_archivado_ind + 1
                        if tercer.id != record.id:
                            name_tercer = tercer.name
                            user_create = tercer.create_uid.name
            if cant_vat > 1:
                raise ValidationError(_('Ya existe un Cliente ('+name_tercer+') con este número de NIT creado por '+user_create+'.'))                
            if cant_vat_archivado > 1:
                raise ValidationError(_('Ya existe un Cliente ('+name_tercer+') con este número de NIT pero se encuentra archivado, fue creado por '+user_create+'.'))                
            if cant_vat_ind > 1:
                raise ValidationError(_('Ya existe un Tercero ('+name_tercer+') con este número de ID creado por '+user_create+'.'))                
            if cant_vat_archivado_ind > 1:
                raise ValidationError(_('Ya existe un Tercero ('+name_tercer+') con este número de ID pero se encuentra archivado, fue creado por '+user_create+'.'))

    @api.constrains('bank_ids')
    def _check_bank_ids(self):
        for record in self:
            if len(record.bank_ids) > 0:
                count_main = 0
                for bank in record.bank_ids:
                    count_main += 1 if bank.is_main else 0
                if count_main > 1:
                    raise ValidationError(_('No puede tener más de una cuenta principal, por favor verificar.'))

    @api.constrains('x_type_thirdparty','name','x_document_type','vat','street','state_id','country_id','x_city','phone','mobile','email')
    def _check_fields_required(self):  
        if self.env.user.name != 'OdooBot' and self.env.user.login != '__system__': # Se omite esta validación con datos DEMO ESTANDAR DE ODOO
            for record in self:
                responsable = 'tercero'
                if record.parent_id:
                    name = ' '+record.name if record.name else ''
                    responsable = 'contacto'+name
                
                if not record.parent_id:
                    if not record.x_document_type:     
                        raise ValidationError(_('Debe seleccionar el tipo de documento del '+responsable+', por favor verificar.'))  
                    if not record.vat:           
                        raise ValidationError(_('Debe digitar el número de documento del '+responsable+', por favor verificar.'))  
                    if not record.phone and not record.mobile:
                        raise ValidationError(_('Debe digitar el telefono o móvil del '+responsable+', por favor verificar.'))  

                if not record.name:
                    raise ValidationError(_('Debe digitar el nombre del '+responsable+', por favor verificar.'))             
                if len(record.x_type_thirdparty)==0:
                    raise ValidationError(_('Debe seleccionar un tipo de tercero, por favor verificar.'))        
                if not record.street:
                    raise ValidationError(_('Debe digitar la dirección del '+responsable+', por favor verificar.'))  
                if not record.state_id:
                    raise ValidationError(_('Debe digitar el departamento del '+responsable+', por favor verificar.'))  
                if not record.x_city:
                    raise ValidationError(_('Debe digitar la ciudad del '+responsable+', por favor verificar.'))  
                if not record.country_id:
                    raise ValidationError(_('Debe digitar el país del '+responsable+', por favor verificar.'))  
                if not record.email:
                    raise ValidationError(_('Debe digitar el correo electrónico del '+responsable+', por favor verificar.'))  
    
    @api.onchange('x_first_name','x_second_name','x_first_lastname','x_second_lastname')
    def _onchange_info_names(self):
        for record in self:
            if record.company_type == 'person':
                fn = record.x_first_name if record.x_first_name else ''
                sn = record.x_second_name if record.x_second_name else ''
                fl = record.x_first_lastname if record.x_first_lastname else ''
                sl = record.x_second_lastname if record.x_second_lastname else ''

                name_partner = ''
                name_partner = name_partner+fn if fn != '' else name_partner
                name_partner = name_partner+" "+sn if sn != '' and name_partner != '' else name_partner+sn            
                name_partner = name_partner+" "+fl if fl != '' and name_partner != '' else name_partner+fl            
                name_partner = name_partner+" "+sl if sl != '' and name_partner != '' else name_partner+sl

                record.name = name_partner
# -*- coding: utf-8 -*-
import base64
import pyotp
import pyqrcode
import io

from odoo import models, fields, api, _, tools
from odoo.http import request
from odoo.exceptions import AccessDenied

import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    otp_type = fields.Selection(selection=[('time', _('Time based')), ('count', _('Counter based'))], default='time',
                                string="Type",
                                help="Type of OTP, time = new pin for each period, counter = new pin for each login")

    @api.model
    def _otp_secret(self):
        return pyotp.random_base32()

    otp_secret = fields.Char(string="Secret", size=16, help='16 character base32 secret',
                             default=lambda s: pyotp.random_base32())
    otp_counter = fields.Integer(string="Counter", default=1)
    otp_digits = fields.Integer(string="Digits", default=6, help="Length of the PIN")
    otp_period = fields.Integer(string="Period", default=30, help="Number seconds PIN is active")

    def _qr_create(self, uri):
        buffer = io.BytesIO()
        qr = pyqrcode.create(uri)
        qr.png(buffer, scale=3)
        return base64.b64encode(buffer.getvalue()).decode()

    def _otp_qrcode(self):
        self.ensure_one()
        self.otp_qrcode = self._qr_create(self.otp_uri)

    otp_qrcode = fields.Binary(compute="_otp_qrcode")

    @api.one
    def _otp_uri(self):
        if self.otp_type == 'time':
            otp = pyotp.TOTP(self.otp_secret)
            otp.period = self.otp_period
            provisioning_uri = otp.provisioning_uri(self.login)
        else:
            otp = pyotp.HOTP(self.otp_secret)
            otp.digits = self.otp_digits
            provisioning_uri = otp.provisioning_uri(self.login, self.otp_counter)
        self.otp_uri = provisioning_uri + '&issuer=%s' % self.company_id.name

    otp_uri = fields.Char(compute='_otp_uri', string="URI")

    @api.model
    def check_otp(self, otp_code):
        user = self.env['res.users'].browse(self.env.uid)
        if user.otp_type == 'time':
            totp = pyotp.TOTP(user.otp_secret)
            return totp.verify(otp_code)
        elif user.otp_type == 'count':
            hotp = pyotp.HOTP(user.otp_secret)
            for c in range(user.otp_counter - 5, user.otp_counter + 5):
                if c > 0 and hotp.verify(otp_code, c):
                    user.otp_counter = c + 1
                    return True
        return False

    def _check_credentials(self, password):
        super(ResUsers, self)._check_credentials(password)
        if not self.check_otp(request.params.get('tfa_code')):
            # pass
            raise AccessDenied(u'双因子验证错误！')
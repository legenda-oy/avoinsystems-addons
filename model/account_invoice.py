# coding=utf-8

__author__ = 'aisopuro'
from openerp import models, fields, api
from openerp.tools.translate import _
from itertools import cycle
import re
import logging

log = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('number', 'state')
    def _compute_ref_number(self):
        if self.number:
            invoice_number = re.sub(r'\D', '', self.number)
            checksum = sum((7, 3, 1)[idx % 3] * int(val) for idx, val in enumerate(invoice_number[::-1]))
            self.ref_number = invoice_number + str((10 - (checksum % 10)) % 10)
            self.invoice_number = invoice_number
        else:
            self.invoice_number = False
            self.ref_number = False

    @api.one
    def _compute_barcode_string(self):
        if (self.amount_total and self.partner_bank_id.acc_number and self.ref_number and self.date_due):
            amount_total_string = str(self.amount_total)
            if amount_total_string[-2:-1] == '.':
                amount_total_string = amount_total_string + '0';
            amount_total_string = amount_total_string.zfill(9)
            receiver_bank_account = re.sub("[^0-9]", "", str(self.partner_bank_id.acc_number))
            ref_number_filled = self.ref_number.zfill(20)
            self.barcode_string = '4' + receiver_bank_account + amount_total_string[:-3] + amount_total_string[-2:] + "000" + ref_number_filled + self.date_due[2:4] + self.date_due[5:-3] + self.date_due[-2:] 
        else:
            self.barcode_string = False

    invoice_number = fields.Char(
        'Invoice number',
        compute='_compute_ref_number',
        store=True,
        help=_('Identifier number used to refer to this invoice in accordance with https://www.fkl.fi/teemasivut/sepa/tekninen_dokumentaatio/Dokumentit/kotimaisen_viitteen_rakenneohje.pdf')
    )

    ref_number = fields.Char(
        'Reference Number',
        compute='_compute_ref_number',
        store=True,
        help=_('Invoice reference number in accordance with https://www.fkl.fi/teemasivut/sepa/tekninen_dokumentaatio/Dokumentit/kotimaisen_viitteen_rakenneohje.pdf')
    )

    date_delivered = fields.Date(
        'Date delivered',
        help=_('The date when the invoiced product or service was considered delivered, for taxation purposes.')
    )

    barcode_string = fields.Char(
        'Barcode String',
        compute='_compute_barcode_string',
        help=_('https://www.fkl.fi/teemasivut/sepa/tekninen_dokumentaatio/Dokumentit/Pankkiviivakoodi-opas.pdf')
    )

#!/usr/bin/env python3

# set server timezone in UTC before time module imported
import os
import sys
__import__('os').environ['TZ'] = 'UTC'

LIB_PATH = os.path.join(os.path.split(os.path.realpath(__file__))[0], '.', 'odoo12')
sys.path.append(LIB_PATH)

import odoo
from core import init_patch

if __name__ == "__main__":
    init_patch()
    from odoo.modules.module import (
        load_openerp_module,
    )
    load_openerp_module('web')

    from core import patch
    patch.monkey_patch()

    odoo.cli.main()

from dataclasses import dataclass
import datetime
from typing import Dict, List, Union
    

@dataclass
class AdminRights:
    main_admin: bool
    admins_edit: bool
    admins_view: bool
    bot_config: bool
    help_requests: bool
    users_edit: bool
    mailing: bool
    promo_codes: bool
    auction: bool
    contest: bool
    products: bool
    replacement: bool
    analytics: bool
    notifications: bool
    history: bool
    payment_system: bool
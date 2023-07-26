from dataclasses import dataclass
import datetime
from typing import Dict, List, Union
    

@dataclass
class UserProfile:
    user_id: int
    rank: str  #  UserRank
    balance: float
    count_payments: int
    amount_payments: float
    count_purchases: int
    amount_purchases: float
    asset_symbol: str
    currency: str
    asset_text: str
    language: str
    promocode: Union[None, str]
    time_reg: float
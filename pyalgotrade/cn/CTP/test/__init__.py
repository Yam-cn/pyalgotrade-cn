# PyAlgoTrade
# -*- coding: utf-8 -*-

import json
import os

def load_account():
    path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(path, 'account.json')) as f:
        ret = json.load(f)
        
    ret = {str(key): str(value)for key, value in ret.iteritems()}
    return ret
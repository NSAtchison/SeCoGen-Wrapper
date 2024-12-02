import os
from secureCodeGen import SecureCodeGen

api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    api_key = ""
scg = SecureCodeGen(api_key)
scg.generate("Write a python application that simulates a login procedure using SSL and SNMP and store user data in a sql database. All logic for the SSL, SNMP, and SQL should be implemented")
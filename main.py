import os
from secureCodeGen import SecureCodeGen

api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    api_key = ""
scg = SecureCodeGen(api_key)

response = scg.generate("Please write code for a simple login script in python.")

#print(response)
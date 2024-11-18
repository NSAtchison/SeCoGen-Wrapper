#https://ai.google.dev/api?lang=python

import google.generativeai as genai
import re
import pandas as pd
import os

class SecureCodeGen():
    def __init__(self, api_key, model_type="gemini-1.5-flash"):
        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(model_type)

        self.draft_file = "draft.py"

        self.secure_prompt = "\nMake sure to make the code free from security vulnerabilities. Please only return code."
        self.regenerate_prompt = "\nRewrite this code to fix the errors mentioned in the error report."

        self.warning_message = "# ===== LLM GENERATED CODE - USE WITH CAUTION ====="

        self.code_dict = {
            "B101": "Consider raising a semantically meaningful error or AssertionError instead of an assert",
            "B102": "Do not use the exec method or keyword",
            "B103": "Use secure file permissions",
            "B104": "Do not use any hardcorded bindings to all network interfaces",
            "B105": "Do not hardcode any passwords",
            "B106": "Do not use hard-coded password function arguments",
            "B107": "Do not use any hard-coded password argument defaults",
            "B108": "Do not use a temporary file or directory insecurely",
            "B109": "Ensure that password based config option is marked secret",
            "B110": "Do not use the pass keyword in an exception block",
            "B112": "Do not use the continue keyword in an exception block",
            "B113": "Do not use reqests or httpx calls without a specified timeout",
            "B201": "Do not run a flask app with debug set to true",
            "B202": "Only use Use tarfile.extractall(members=function_name) and define a function that will inspect each member. Discard files that contain a directory traversal sequences such as ../ or \\.. along with all special filetypes unless you explicitly need them.",
            "B324": "Do not use MD4, MD5, or SHA1 hash functions as these are insecure",
            "B501": "Ensure that certificate validation is turned on",
            "B502": "Avoid using the following SSL and TLS versions: SSL v2, SSL v3, TLS v1, TLS v1.1",
            "B503": "Avoid using the following versions of SSL and TLS versions as default parameters: SSL v2, SSL v3, TLS v1, TLS v1.1",
            "B504": "Make sure to specify a SSL/TLS version that is not one of the following: SSL v2, SSL v3, TLS v1, TLS v1.1",
            "B505": "Make sure to use RSA and DSA key lengths of atleast size 2048 or EC key length sizes of atleast 224",
            "B506": "Please use yaml.safe_load instead of yaml.load",
            "B507": "Ensure that host key verification is enabled",
            "B508": "The use of SNMPv1 and SNMPv2 is insecure. You should use SNMPv3 if able.",
            "B509": "You should not use SNMPv3 without encryption. noAuthNoPriv & authNoPriv is insecure",
            "B601": "Possible shell injection via Paramiko call, Ensure that inputs are properly sanitized.",
            "B602": "Subprocess call with shell=True seems safe, Try rewriting without shell",
            "B603": "Subprocess call - ensure that there is no execution of untrusted input.",
            "B604": "Function call with shell=True parameter identified, Try to refrain from do this.",
            "B605": "Starting a process with a shell: Ensure that no injection can take place",
            "B606": "Ensure that process is started securely despite running without a shell",
            "B607": "Starting a process with a partial executable path. Try to refrain from doing so",
            "B608": "Try to protect against SQL injection by avoiding hardcoded SQL expressions",
            "B609": "Previous code had possible wildcard injection. Try to avoid using the wildcard character in place of a file system path",
            "B610": "Try to protect against extra potential SQL injection attack vector in django",
            "B611": "Try to protect against RawSQL potential SQL injection attack vector in django",
            "B612": "Ensure that the logging.config.listen function is used securely",
            "B613": "Avoid using unicode bidirectional control characters",
            "B614": "Use torch.load with the safetesnors library from hugingface",
            "B701": "Use autoescape=True to mitigate XSS vulnerabilities.",
            "B702": "Ensure variables in all templates are properly sanitized via the 'n', 'h' or 'x' flags (depending on context)",
            "B703": "Protect against XSS on mark_safe functions",
        }

    def call_llm(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text

    def parse_code(self, text):
        match = re.search(r"```python\n(.*?)```", text, re.DOTALL)

        if match:
            code = match.group(1)
            return

    # This function creates the initial Bandit report to be analyzed
    # Input: code_filename: This is the file name for the python code that we want a Bandit report on
    # Output: A file called results.csv will be created containing all data generated by the Bandit package on the given python file
    # NOTE: Might need to change this to deal with full directories.
    def create_bandit_report(self, code_filename, bandit_report_filename):
        os.system(f"bandit {code_filename} -f csv -o {bandit_report_filename}")

    def generate(self, prompt):
        response1 = self.call_llm(prompt + self.secure_prompt)
        draft_code = self.parse_code(response1)

        with open(self.draft_file, "w") as file:
            file.write(draft_code)

        # TODO: Pass response1 to Bandit

        # TODO: Pass response1, Bandit report, and LLM report to llm
        # NOTE: We should be checking if Bandit reports no issues, if so prob don't need to rewrite code.

        # TODO: Report code output, and reports
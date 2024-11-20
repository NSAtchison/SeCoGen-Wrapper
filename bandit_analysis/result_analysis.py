# importing pandas and os modules
import pandas as pd
import os

# These are the file names for the bandit report and the python code given by ChatGPT.
# These can be adjusted here and work everywhere else
# BANDIT_REPORT_FILE_NAME = "results.csv"

# This is a Dictionary that has the Issue codes as keys and the desired prompt to be used as the values
code_dict = {
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

# This function creates the initial Bandit report to be analyzed
# Input: code_filename: This is the file name for the python code that we want a Bandit report on
# Output: A file called results.csv will be created containing all data generated by the Bandit package on the given python file
# NOTE: Might need to change this to deal with full directories.
# def create_bandit_report(code_filename, bandit_report_filename):
#     os.system(f"bandit {code_filename} -f csv -o {bandit_report_filename}")

# This function goes through the .csv created by Bandit and finds all the unique issue codes found
# Input: report_filename: This is the filename of the .csv generated by Bandit
# Output: A list of all unique issue codes that were generated by Bandit
def find_issue_code(report_filename):
    df = pd.read_csv(report_filename)
    all_codes = df.test_id
    unique_codes = list(set(all_codes))
    return unique_codes

# This function takes all the unique issue codes generated by Bandit and turns them into the prompts we want to use when constructing our 2nd secure prompt
# Input: unique_codes: A list of all unique codes that were generated by Bandit
# Output: A list of all the prompts we want to add to the prompt given back to ChatGPT based on the codes we added
def codes_to_issues(unique_codes):
    issue_prompts = []
    for code in unique_codes:
        issue_prompts.append(code_dict[code])
    return issue_prompts

# This function will create the final prompt that we want to return to ChatGPT for the second iteration
# Input: issue_prompts: This is the list of all prompts we want ChatGPT to be aware of when generating code
# Output: The final prompt that ChatGPT will use when generating code will be created and returned
def create_prompt(issue_prompts):
    base_prompt = "Rewrite the attached code with the following in mind: "
    if len(issue_prompts) > 0:
        for prompt in issue_prompts:
            base_prompt += prompt + ". "
    base_prompt += "Ensure the best possible security while writing the code."
    return base_prompt

def result_analysis(bandit_file_path):
    # dir = os.path.realpath(os.path.dirname(__file__))
    # bandit_file_path = f"{dir}/{BANDIT_REPORT_FILE_NAME}"
    # create_bandit_report(code_filename, bandit_file_path)
    codes = find_issue_code(bandit_file_path)
    prompts = codes_to_issues(codes)
    return create_prompt(prompts)


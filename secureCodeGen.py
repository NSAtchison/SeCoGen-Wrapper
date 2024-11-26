import google.generativeai as genai
import re
import os
from bandit_analysis.result_analysis import result_analysis

PASS_1_BANDIT_REPORT_FILE_NAME = "reports/bandit_results_pass_1.csv"
PASS_2_BANDIT_REPORT_FILE_NAME = "reports/bandit_results_pass_2.csv"
PASS_1_PY_FILE_NAME = "generated_code/gemini_output_pass_1.py"
PASS_2_PY_FILE_NAME = "generated_code/gemini_output_pass_2.py"

class SecureCodeGen():
    def __init__(self, api_key, model_type="gemini-1.5-flash"):
        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(model_type)

        self.draft_file = "gpt_output.py"

        self.secure_prompt = "\nMake sure to make the code free from security vulnerabilities. Please only return code."

        self.regenerate_prompt = ("\nRewrite this code: {code} to fix these"
                                  " issues: {issues}. Additionally, write a detailed report of the security of the code you generate.")
        self.report_only_prompt = "Please write a detailed report about the security of this code: {code}."

        self.warning_message = "# ===== LLM GENERATED CODE - USE WITH CAUTION ====="

    def call_llm(self, prompt, fileFlag):
        if(fileFlag):
            upload_file = genai.upload_file("SecurityEval.txt")
            response = self.model.generate_content([upload_file, prompt + " The attached file has IDs, prompts, and Insecure Code. Keep these in mind while generating the code."])
        else:
            response = self.model.generate_content(prompt)
        return response.text

    def parse_code(self, text):
        match = re.search(r"```python\n(.*?)```", text, re.DOTALL)

        if match:
            return match.group(1)

    def create_bandit_report(self, code_filename, bandit_report_filename):
        os.system(f"bandit {code_filename} -f csv -o {bandit_report_filename}")

    def generate_python_script(self, output_file: str, gemini_output: str):
        """
        Generate a python script based on the code in the given string.

        Args:
        gpt_output: the output string from Chat-GPT.
        """
        dir = os.path.realpath(os.path.dirname(__file__))
        file_name = f"{dir}/{output_file}"

        with open(file_name, "w") as file_to_write:
            file_to_write.write(gemini_output)

    def generate(self, prompt):
        # Generate the first pass of the code
        response1 = self.call_llm(prompt + self.secure_prompt, True)
        pass_1_code = self.parse_code(response1)

        if not pass_1_code:
            print("Error: no code was generated by prompt 1.")
            return

        # Save the generated code to file
        self.generate_python_script(PASS_1_PY_FILE_NAME, pass_1_code)

        dir = os.path.realpath(os.path.dirname(__file__))
        code_file_path = f"{dir}/{PASS_1_PY_FILE_NAME}"
        bandit_report_file_path = f"{dir}/{PASS_1_BANDIT_REPORT_FILE_NAME}"

        # Generate the Bandit report for the generated code
        self.create_bandit_report(code_file_path, bandit_report_file_path)

        # Analyze the Bandit report to find security issues
        issues = result_analysis(bandit_report_file_path)

        if issues:
            # If issues were found, ask the LLM to regenerate the code to fix those issues
            response2 = self.call_llm(self.regenerate_prompt.format(
                code=pass_1_code,
                issues=issues
            ), False)

            print(response2)
            
            # Extract the regenerated code
            pass_2_code = self.parse_code(response2)

            # Save the regenerated code to file
            self.generate_python_script(PASS_2_PY_FILE_NAME, pass_2_code)

            # Generate the Bandit report for the regenerated code
            code_file_path = f"{dir}/{PASS_2_PY_FILE_NAME}"
            bandit_report_file_path = f"{dir}/{PASS_2_BANDIT_REPORT_FILE_NAME}"
            self.create_bandit_report(code_file_path, bandit_report_file_path)
            
            # Save the AI's security report to a file
            self.save_security_report(response2)

        else:
            # If no issues were found, generate only the security report
            response2 = self.call_llm(self.report_only_prompt.format(code=pass_1_code), False)

            print(response2)
            
            # Save the AI's security report to a file
            self.save_security_report(response2)

    def save_security_report(self, response_text):
        """
        Save the AI-generated security report to a text file.

        Args:
        response_text: The text generated by the AI, including the security report.
        """
        # Extract the security report section from the AI's response
        security_report = response_text.strip()

        # Define a file to save the report
        report_file_name = "security_report.txt"

        # Write the security report to a file
        with open(report_file_name, "w") as report_file:
            report_file.write(security_report)

        print(f"Security report saved to {report_file_name}")

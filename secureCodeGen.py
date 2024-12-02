import google.generativeai as genai
import re
import os
import shutil
from bandit_analysis.result_analysis import result_analysis

PASS_1_PY_FILE_NAME = "generated_code/gemini_output_pass_1.py"
PASS_1_BANDIT_REPORT_FILE_NAME = "reports/bandit_results_pass_1.csv"

PASS_2_BANDIT_REPORT_FILE_NAME = "reports/bandit_results_pass_2.csv"
PASS_2_PY_FILE_NAME = "generated_code/gemini_output_pass_2.py"

LLM_SECURITY_REPORT_FILE_NAME = "output/gemini_security_report.txt"
FINAL_BANDIT_REPORT_FILE_NAME = "output/bandit_results_final.csv"
FINAL_PY_FILE_NAME = "output/gemini_output_final.py"

DATA_SET_FILE_NAME = "data_sets/SecurityEval.txt"

class SecureCodeGen():
    """
    This class contains functionality to securely prompt an LLM
    to generate Python code. All code output is LLM generated.
    Use with caution.

    To prompt, use the self.generate function.

    Attributes:
      model: The model being used. Currently only interfaces
        with Google Gemini.
      secure_prompt: A message to ensure prompting is secure.
      regenerate_prompt: A prompt to re-generate code based on
        issues identified by automated security testing.
      report_only_prompt: A prompt to ask only for a security report.
      warning_message: A message indicated code is LLM generated.
    """
    def __init__(self, api_key, model_type="gemini-1.5-flash"):
        """
        Initializes key features of the SecureCodeGen model.

        Args:
          api_key: The API key for the LLM being used to generate code.
          model_type: The type of model being used (optional).
        """
        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(model_type)

        self.secure_prompt = "\nMake sure to make the code free from security vulnerabilities. Please only return code."

        self.regenerate_prompt = ("\nRewrite this code: {code} to fix these"
                                  " issues: {issues}. Additionally, write a detailed report of the security of the code you generate.")
        self.report_only_prompt = "Please write a detailed report about the security of this code: {code}."

        self.warning_message = "# ===== LLM GENERATED CODE - USE WITH CAUTION =====\n"

    def call_llm(self, prompt, include_data_set=False):
        """
        Performs an API call to the current model.

        Args:
          prompt: The prompt to issue to the model.
          include_data_set: Indicates if the current security data
            set should be included (optional).
        """
        if(include_data_set):
            upload_file = genai.upload_file(get_file_path(DATA_SET_FILE_NAME))
            response = self.model.generate_content([upload_file, prompt + " The attached file has IDs, prompts, and Insecure Code. Keep these in mind while generating the code."])
        else:
            response = self.model.generate_content(prompt)
        return response.text

    def parse_code(self, text):
        """
        Parses the given text to identify only the python code
        within it. Used on LLM output since there will often be more text
        than just the code requested.

        Args:
          text: The text to parse.
        Returns:
          The code or None if not found.
        """
        match = re.search(r"```python\n(.*?)```", text, re.DOTALL)

        if match:
            return match.group(1)

        return None

    def create_bandit_report(self, code_filename, bandit_report_filename):
        """
        Creates a Bandit report by making an OS system call to Bandit.
        Assumes that Bandit has been installed by the user.
        
        Args:
          code_filename: The name of the Python file to analyze.
          bandit_report_filename: The name of the target output file for Bandit.
        """
        os.system(f"bandit {code_filename} -f csv -o {bandit_report_filename}")

    def generate_python_script(self, output_file: str, gemini_output: str):
        """
        Generate a python script based on the code in the given string.

        Args:
          output_file: The name of the output file.
          gemini_output: the output string from the LLM API call.
        """
        file_name = get_file_path(output_file)

        with open(file_name, "w") as file_to_write:
            file_to_write.write(self.warning_message)
            file_to_write.write(gemini_output)

    def generate(self, prompt):
        """
        This is the heart of SeCoGen.

        Modifies the given prompt to be more secure and consider a security data set.
        Generates a Python file from the generated code.
        Uses Bandit to perform automatic static analysis on the generated code.

        Re-prompts the LLM if any security issues were found by Bandit.

        Ask the LLM to generate a security report on the final code.

        Collects the generated code, final Bandit report, and LLM
        security report and places them all into the output folder.

        Args:
          prompt: The prompt issued by the user.
        """
        # Generate the first pass of the code
        response1 = self.call_llm(prompt + self.secure_prompt, include_data_set=True)
        pass_1_code = self.parse_code(response1)

        if not pass_1_code:
            print("Error: no code was generated by initial prompt. Please retry or modify input prompt.")
            return

        # Save the generated code to file.
        self.generate_python_script(PASS_1_PY_FILE_NAME, pass_1_code)

        # Identify file paths.
        code_file_path = get_file_path(PASS_1_PY_FILE_NAME)
        bandit_report_file_path = get_file_path(PASS_2_BANDIT_REPORT_FILE_NAME)

        # Generate the Bandit report for the generated code.
        self.create_bandit_report(code_file_path, bandit_report_file_path)

        # Analyze the Bandit report to find security issues.
        issues = result_analysis(bandit_report_file_path)

        if issues:
            # If issues were found, ask the LLM to regenerate the code to fix those issues.
            response2 = self.call_llm(self.regenerate_prompt.format(
                code=pass_1_code,
                issues=issues
            ))

            # Extract the regenerated code.
            pass_2_code = self.parse_code(response2)

            if pass_2_code:
                # Save the regenerated code to file.
                self.generate_python_script(PASS_2_PY_FILE_NAME, pass_2_code)

                # Generate the Bandit report for the regenerated code.
                code_file_path = get_file_path(PASS_2_PY_FILE_NAME)
                bandit_report_file_path = get_file_path(PASS_2_BANDIT_REPORT_FILE_NAME)
                self.create_bandit_report(code_file_path, bandit_report_file_path)

                # Identify which files should be sent to final output.
                final_py_file = PASS_2_PY_FILE_NAME
                final_bandit_report_file = PASS_2_BANDIT_REPORT_FILE_NAME
            else:
                print("Error: no code was generated by the modified prompt.")
        else:
            # If no issues were found, generate only the security report.
            response2 = self.call_llm(self.report_only_prompt.format(code=pass_1_code))

            # Identify which files should be sent to final output.
            final_py_file = PASS_1_PY_FILE_NAME
            final_bandit_report_file = PASS_1_BANDIT_REPORT_FILE_NAME

        # Copy the final code and bandit report.
        shutil.copy(get_file_path(final_py_file), get_file_path(FINAL_PY_FILE_NAME))
        shutil.copy(get_file_path(final_bandit_report_file), get_file_path(FINAL_BANDIT_REPORT_FILE_NAME))

        # Save the AI's security report to a file in the output folder.
        self.save_security_report(response2, get_file_path(LLM_SECURITY_REPORT_FILE_NAME))

        print("Generated code, Bandit analysis, and LLM security report are located in the output folder.")

    def save_security_report(self, response_text, output_file):
        """
        Saves the AI-generated security report to a specified file, extracting only the relevant portion.

        Args:
            response_text: The text generated by the AI, including the security report.
            output_file: The path to the output file.
        """

        # Extract the security report using the `extract_security_report` function
        security_report = self.extract_security_report(response_text)

        # Create the output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)

        with open(output_file, "w") as report_file:
            report_file.write(security_report)

    def extract_security_report(self, report):
        """
        Extracts and filters out unnecessary content before the actual security analysis.

        Args:
            report: The raw security report text.

        Returns:
            The filtered security report text, starting from the actual security analysis.
        """
        # Remove code blocks, if any.
        cleaned_report = re.sub(r'```python\n(.*?)```', '', report, flags=re.DOTALL).strip()

        # Look for the section where the security analysis starts and remove unwanted introductory text.
        match = re.search(r"(Security analysis|Security report|Analysis of the code security|.*security.*analysis.*)", cleaned_report, re.IGNORECASE)

        # If a match is found, start the report from this point onward.
        if match:
            start_index = match.start()
            return cleaned_report[start_index:].strip()

        # If no matching phrase is found, return the entire report.
        return cleaned_report.strip()

def get_file_path(file_name):
    """
    Returns the file path of a file relative to the current
    file's directory.

    Args:
      file_name: The name of the file.
    Returns:
      The file path of the given file.
    """
    dir = os.path.realpath(os.path.dirname(__file__))
    return f"{dir}/{file_name}"
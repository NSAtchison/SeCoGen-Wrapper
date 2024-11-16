import os

GPT_PY_FILE_NAME = "gpt_output.py"

def generate_python_script(gpt_output:str):
    """
    Generate a python script based on the code in the given string.
    Expected to be output from a Chat-GPT prompt of a specific format
    (will update once I can view the output format from the API).

    Args:
      gpt_output: the output string from Chat-GPT.
    """

    dir = os.path.realpath(os.path.dirname(__file__))
    file_name = f"{dir}/{GPT_PY_FILE_NAME}"

    with open(file_name, "w") as file_to_write:
        file_to_write.write(gpt_output)

if __name__ == "__main__":
    generate_python_script("print(\"Hello World!\")")

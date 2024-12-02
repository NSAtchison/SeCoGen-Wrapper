import os
from secure_code_gen import SecureCodeGen

def main():
    """
    Main driver for testing SeCoGen framework.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        api_key = ""
    scg = SecureCodeGen(api_key)

    print(" ==== Using the SeCoGen Framework ====\n")

    while True:
        user_prompt = input("Please enter a prompt or q to quit: ")
        if user_prompt == 'q':
            break
        scg.generate(user_prompt)

if __name__=="__main__":
    main()
# SeCoGen: A Secure Code Generation Framework

Created by Zayn Abou-Harb, Nathan Atchison, Hunter Smith, and Sebastian Smith.

School of Electrical Engineering & Computer Science, Washington State University, Pullman, WA.

SeCoGen is a framework that integrates automatic security analysis, data sets, and prompt modifcation into LLM API prompting. The goal of this framework is to emphasize the importance of security when it comes to LLM generated code, provide more secure code to users of LLMs for this purpose without increasing the workload, and provide information to users about the security of the code they are generating. SeCoGen serves as a proof of concept that LLM code generation security can be improved with a cohesive, modular framework.

The [experiment_results](https://github.com/NSAtchison/SeCoGen-Wrapper/tree/main/experiment_results) directory contains the results of a set of experiments conducted as a precursor to this product. The analysis of these results motivated the creation of SeCoGen.

The [wrapper_test](https://github.com/NSAtchison/SeCoGen-Wrapper/tree/main/wrapper_Test) directory contains the results of the test run of SeCoGen described in the project's final presentation.

## Prerequisites:
Generate a Google Gemini API key at the link below, and store as an environment variable titled GEMINI_API_KEY.

```
https://ai.google.dev/api?lang=python
```

Install Gemini API, bandit, and pandas

```
pip install -q -U google-generativeai
```

```
pip install bandit
```

```
pip install pandas
```

### Optional
Suppress warnings from Gemini API
```
pip install grpcio==1.60.1
```

## Usage

Navigate to the SeCoGen-Wrapper directory and run the main script. This will enter an input loop requesting prompts from the user.
```
python3 main.py
```

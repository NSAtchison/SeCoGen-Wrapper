## This folder is where we cam place the results of our experiments.

This directory contains all of our results from the LLMs. This directory contains several folders within them that represent different security issues that we experimented with in the first part of our project. An example of the folder structure for one of these security issues is as follows:

```
├── Buffer-Overflow
│   ├── ChatGPT
│   │   ├── Iteration-1.docx
|   |   ├── Iteration-2.docx
|   |   ├── Iteration-3.docx
│   ├── Google-Gemini
│   │   ├── Iteration-1.docx
|   |   ├── Iteration-2.docx
|   |   ├── Iteration-3.docx
│   ├── Microsoft-Copilot
│   │   ├── Iteration-1.docx
|   |   ├── Iteration-2.docx
|   |   ├── Iteration-3.docx
```

In this folder structure, we can see that our primary security issue is Buffer Overflow. Within this folder, there is a folder for each of the LLMs that we used in our experiments, in our case it was ChatGPT, Google Gemini and Microsoft Copilot. Finally within those folders, there are three .docx files that contain the LLMs responses for each iteration of the experiments. These include the code generated in iterations 1 & 3 and the potential security risks found in iteration 2.  
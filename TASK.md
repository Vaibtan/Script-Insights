AI Engineer Assignment Bullet – Generative AI & Content Intelligence 

Overview 

At Bullet we are building AI systems that understand and evaluate storytelling. Our platform focuses on short-form scripted content, and one of the core problems we solve is helping creators and internal teams understand the quality and engagement potential of scripts. 

This assignment is designed to evaluate how you approach building a practical AI system using modern language models. The focus is not on building a perfect product, but on demonstrating your thinking, system design, and ability to use LLMs effectively. 

The task 

Build a small AI system that analyzes a short script and generates insights about the story. 

The system should accept a script as input and produce a structured analysis that helps understand the story, emotional tone, and engagement potential. 

You may use any language model or tooling you prefer (OpenAI, Claude, open-source models, etc.). 

Input 

The system should accept a short script (for example 1–3 pages or a few dialogue scenes). 

Example input format: 

Title: The Last Message 

Scene 

Riya receives a message from her ex-boyfriend after five years. 

Dialogue Riya: Why now? Arjun: Because today I learned the truth. Riya: What truth? Arjun: That the accident wasn't your fault. 

Expected system behavior 

The system should generate a short summary of the story in three to four lines. 

It should analyze the emotional tone of the script and identify the dominant emotions and how the emotional arc evolves through the scene. 

The system should also estimate the engagement potential of the script. This can be represented as an overall score along with factors that influenced the score, such as strength of the opening hook, character conflict, tension, or the presence of a cliffhanger. 

Finally, the system should suggest several ways the script could be improved. These suggestions should focus on storytelling elements such as pacing, conflict, dialogue, or emotional impact. 

As an optional enhancement, the system may attempt to identify the most suspenseful or “cliffhanger” moment in the script and explain why it works. 

Technical expectations 

The solution should demonstrate practical use of modern LLM tooling. Python is preferred but not mandatory. 

Candidates may use any of the following if helpful: 

- LLM APIs (OpenAI, Claude, etc.) 

- Prompt engineering techniques 

- LangChain or LlamaIndex 

- A lightweight interface such as CLI, Streamlit, or a simple web endpoint 

The implementation does not need to be complex, but the code should be reasonably structured and easy to understand. 

Deliverables 

Please submit a GitHub repository containing the working code. 

Include a README that briefly explains: 

- your overall approach 

- how the prompts or model interactions were designed 

- which model or tools you used 

- limitations of the current system 

- possible improvements if you had more time 

Provide a short demo video (approximately five minutes) showing the system working and explaining your design decisions. 

Evaluation 

We will evaluate submissions based on the following: 

- clarity and structure of the implementation 

- quality of prompt design and model usage 

- usefulness and coherence of the generated insights 

- practicality of the system design 

- clarity of documentation and explanation 
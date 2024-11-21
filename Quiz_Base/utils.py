# utils.py
from PyPDF2 import PdfReader
import os
import google.generativeai as genai
import json
import os
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re 
from django.utils.html import format_html

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text


groq_api_key = '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'  # Retrieve the API key for Groq

# Set up the Groq model for generating MCQs
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-8b-8192")


def generate_mcqs_with_groq(pdf_text, output_filename='generated_mcqs.json'):
    # Split text into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(pdf_text)
    mcqs = []

    # Define the prompt template
    prompt_template = """
    You are an AI designed to create multiple-choice questions. Based on the provided text, generate an insightful MCQ with one correct answer and three distractors.

    Text:
    {chunk}

    Instructions:
    - Create exactly one multiple-choice question.
    - Include four answer options, clearly identifying the correct one.
    - Exclude explanations or any additional comments beyond the question and options.
    """

    for i, chunk in enumerate(chunks):
        prompt = prompt_template.format(chunk=chunk)
        response = llm.invoke(prompt)

        if response:
            mcqs.append(response.content.strip())
        else:
            mcqs.append(f"No valid MCQ generated for chunk {i+1}.")

    with open(output_filename, 'w') as json_file:
        json.dump(mcqs, json_file, indent=4)

    print(f"MCQs saved to {output_filename}")
    return mcqs


    
import re

def parse_mcqs(mcq_text):
    parsed_mcqs = []
    for chunk in mcq_text:
        try:
            # Extract the question
            question_match = re.search(r"(?:Question \d+:|Here(?:'s| is) .*?:)\s*(.*?)(?=\n[A-D]\))", chunk, re.DOTALL | re.IGNORECASE)
            
            # Extract options
            options_match = re.findall(r"([A-D])\)\s*(.*?)(?=(?:\n[A-D]\)|\nCorrect answer:|\Z))", chunk, re.DOTALL)
            
            # Extract correct answer
            correct_answer_match = re.search(r"Correct answer:\s*([A-D])", chunk)

            # Ensure explanation does not merge with options
            explanation_match = re.search(r"(Explanation:.*)", chunk, re.DOTALL)

            if question_match and options_match and correct_answer_match:
                question = question_match.group(1).strip()
                options = {opt[0]: re.split(r"(?:Correct answer:|Explanation:)", opt[1].strip())[0].strip() for opt in options_match}
                correct_answer = correct_answer_match.group(1)
                explanation = explanation_match.group(1).strip() if explanation_match else None

                parsed_mcqs.append({
                    'question': question,
                    'options': options,
                    'correct_answer': correct_answer,
                    'explanation': explanation  # Optional field
                })
            else:
                print(f"Failed to parse MCQ: {chunk}")

        except Exception as e:
            print(f"Error parsing chunk: {chunk}, error: {e}")

    return parsed_mcqs


def generate_html_for_quiz(mcq_list):
    html_output = ''
    for idx, mcq in enumerate(mcq_list):
        if 'options' not in mcq or not mcq['options']:
            html_output += format_html('<p>{}</p>', mcq)  # Display error message
        else:
            # Format question
            html_output += format_html('<div class="question"><p><strong>Question {0}: {1}</strong></p>', idx + 1, mcq['question'])
            for opt_key, option in mcq['options'].items():
                html_output += format_html(
                    '<label><input type="radio" name="q{0}" value="{1}"> {2}) {3}</label><br>',
                    idx, opt_key, opt_key, option
                )
            html_output += '</div>'
    return html_output

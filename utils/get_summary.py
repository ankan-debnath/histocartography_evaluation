import os
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

def get_summarised_response(question, image_analysis_data, history_str):
    # Combine image descriptions into a formatted string
    formatted_image_info = "\n".join(
        [f"{filename}:\n{description}" for item in image_analysis_data for filename, description in item.items()]
    )

    # Initialize the LLM
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.0,
        max_retries=2,
        api_key=str(os.getenv("GROQ_API_KEY"))
    )

    # Define the prompt
    prompt_template = PromptTemplate(
        input_variables=["question", "image_info", "history"],
        template="""
        You are a medical pathology assistant AI.
        Bellow is the prompt to be answered.
        Prompt:
        {qestion}
        
        Below are descriptions of histopathology image patches. Each description corresponds to an image filename. Analyze all the provided information and produce a overall summary of the pathological findings across the images.
        Without mentioning any image or patch name or descriptions.
        
        Descriptions:
        {image_info}
        
        Please provide a comprehensive summary.
        """
    )

    chain = LLMChain(llm=llm, prompt=prompt_template)

    # Run the chain
    response = chain.run({
        "image_info": formatted_image_info,
        "history": history_str,
        "question": question
    })

    return response

# print(get_summarised_response("Hello who is this"))
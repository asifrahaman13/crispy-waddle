import logging
import os
import json
from pymongo import MongoClient
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

open_ai_api_key=os.getenv("OPENAI_API_KEY")
assert open_ai_api_key, "Please set the OPENAI_API_KEY environment variable"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Sentiment(BaseModel):
    sentiment: str = Field(
        description="The sentiment of the review. It can be either positive, negative or neutral."
    )


class SentimentAssistant:
    def __init__(self):
        self.model = "gpt-4o"
        self.openai_api_key = open_ai_api_key
        self.max_tokens = 500
        self.chat_model = ChatOpenAI(
            model=self.model,
            openai_api_key=self.openai_api_key,
            max_tokens=self.max_tokens,
        )

    def process_output(self, output):

        # Extract the JSON content
        json_content = output.content.strip("```json\n").strip("```")
        try:
            return json.loads(json_content)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return None

    def format_input(self, user_query):

        # Create a prompt
        parser = PydanticOutputParser(pydantic_object=Sentiment)

        # Create a prompt
        prompt = ChatPromptTemplate(
            messages=[
                HumanMessagePromptTemplate.from_template(
                    "Format the user product review into the schema provided to you. You should extract the features mentioned by the user and whether user liked it nor not. Label them as either positive, negative or neutral. There can be multiple feature under a single review. Only give the json schema having features as the key and list of objects containing feature and the corresponding sentiment where no other text. The review: \n \n{question}"
                )
            ],
            # Define the input variables
            input_variables=["question"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        return prompt.format_prompt(question=user_query)

    def run_sentiment_assistant(self, user_query):

        # Format the input
        input_prompt = self.format_input(user_query)

        logging.info("The input prompt %s", input_prompt.to_messages())

        # Invoke the model
        output = self.chat_model.invoke(input_prompt.to_messages())

        logging.info("The LLM output %s", output.content)

        # Process the output
        return self.process_output(output)

class MongoDBHandler:
    """
    A class to handle MongoDB operations.
    """
    def __init__(self, mongo_uri, db_name, collection_name):
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client[db_name]
        self.collection = self.db[collection_name]

    def store_in_mongodb(self, result):
        try:
            self.collection.insert_one(result)
            logging.info("Stored result in MongoDB: %s", result)
        except Exception as e:
            logging.error("Failed to store result in MongoDB: %s", e)


class AspectBasedSentimentAnalyzer:
    """
    A class to analyze reviews using the Aspect-Based Sentiment Analysis model. 
    """
    def __init__(self, mongo_handler):
        self.mongo_handler = mongo_handler
    
    # Analyze reviews from a file
    def analyze_reviews_from_file(self, input_file, output_file):
        with open(input_file, "r") as file:
            reviews = [line.strip() for line in file if line.strip()]
        
        # Store the results
        results = []

        for review in reviews:
            try:
                # Run the sentiment assistant
                json_schema = SentimentAssistant().run_sentiment_assistant(review)
                logging.info("The json schema %s", json_schema)

                # Add the review to the JSON schema
                json_schema["review"] = review

                # Store the result in MongoDB
                results.append(json_schema)

                # Store the result in MongoDB
                self.mongo_handler.store_in_mongodb(json_schema)  # Store the result in MongoDB
            except Exception as e:
                logging.error("Failed to analyze the review: %s", e)

        with open(output_file, "w") as file:

            # Write the results to the output file
            for result in results:
                file.write(str(result) + "\n")


def main():
    mongo_uri = os.getenv("MONGO_URI")  
    db_name = "sentiment_analysis_db" 
    collection_name = "reviews_analysis"  

    mongo_handler = MongoDBHandler(mongo_uri, db_name, collection_name)
    analyzer = AspectBasedSentimentAnalyzer(mongo_handler)
    input_file = "src/input/reviews.txt" 
    output_file = "src/output/output.txt" 
    analyzer.analyze_reviews_from_file(input_file, output_file)

if __name__ == "__main__":
    main()
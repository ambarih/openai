from flask import Flask, jsonify
from flask_restplus import Api, Resource, reqparse
from flask_cors import CORS
import openai
from pymongo import MongoClient
from bson import ObjectId  # Import ObjectId for generating unique identifiers
from collections import OrderedDict  # Import OrderedDict for maintaining key order
import logging

app = Flask(__name__)
CORS(app)
api = Api(app, version='1.0', title='OPEN AI', description='Generating the Endpoints from OpenAI')

ns = api.namespace('Openai', description='Generating the Endpoints from OpenAI')

# Request parser for query parameters
parser = reqparse.RequestParser()
parser.add_argument('openai_api_key', type=str, help='OpenAI API key', location='args')
parser.add_argument('mongodb_uri', type=str, help='MongoDB URI', location='args')
parser.add_argument('mongodb_database', type=str, help='MongoDB database name', location='args')
parser.add_argument('mongodb_collection', type=str, help='MongoDB collection name', location='args')
parser.add_argument('user_input', type=str, help='User input for chat', location='args')

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@ns.route('/chat')
class ChatResource(Resource):
    @ns.expect(parser)
    def post(self):
        # Get parameters from the Swagger UI
        args = parser.parse_args()
        openai.api_key = args.get('openai_api_key', 'default_openai_api_key')

        # Get MongoDB connection details from Swagger UI
        mongodb_uri = args['mongodb_uri']
        mongodb_database = args['mongodb_database']
        mongodb_collection_name = args['mongodb_collection']

        # Connect to MongoDB using the obtained details
        client = MongoClient(mongodb_uri)
        db = client[mongodb_database]
        collection = db[mongodb_collection_name]

        user_input = args['user_input']

        # Call chat_with_gpt function
        response = chat_with_gpt(user_input)

        response_content = response['choices'][0]['message']['content']

        logging.debug("Raw Chatgpt Response:\n%s", response_content)

        # Ask user for confirmation
        confirmation = ask_for_confirmation(response_content)

        if confirmation == 'yes':
            # Extract method, endpoint, and description
            extracted_data = extract_method_and_endpoint(response_content)

            # Insert into MongoDB
            if extracted_data:
                formatted_data = format_data_for_mongodb(extracted_data, collection)
                logging.debug("Data inserted into MongoDB.")
                return jsonify({"message": "Success"})
            else:
                logging.warning("No data to insert into MongoDB.")
                return jsonify({"message": "No data to insert into MongoDB."})
        else:
            # Handle the case where the user does not confirm
            return jsonify({"message": "User did not confirm. No data inserted."})

def chat_with_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response

def extract_method_and_endpoint(response_content):
    method_endpoint_description_list = []

    # Split the response into sections for each API endpoint
    sections = response_content.split('\n\n')

    for section in sections:
        lines = section.split('\n')

        # Print the lines for debugging
        logging.debug("Lines: %s", lines)

        # Skip sections with fewer than 3 lines (not a complete API endpoint entry)
        if len(lines) < 3:
            continue

        # Extract information from the lines
        method_line = lines[1].strip()
        endpoint_line = lines[2].strip()

        # Check if there are enough lines before accessing description_line
        if len(lines) > 3:
            description_line = lines[3].strip()
        else:
            description_line = "Description not available"

        # Extract method, endpoint, and description
        method = method_line.split(':')[-1].strip()
        endpoint = endpoint_line.split(':')[-1].strip()
        description = description_line.split(':')[-1].strip()

        method_endpoint_description_list.append(OrderedDict([
            ("method", method),
            ("endpoint", endpoint),
            ("description", description)
        ]))

    return method_endpoint_description_list

def format_data_for_mongodb(extracted_data, collection):
    formatted_data = []

    for data_point in extracted_data:
        method = data_point.get("method", "N/A")
        endpoint = data_point.get("endpoint", "N/A")
        description = data_point.get("description", "Description not available")

        # Generate a unique _id using ObjectId
        data_point['_id'] = str(ObjectId())

        # Use OrderedDict to maintain the order of keys
        ordered_data_point = OrderedDict([
            ('_id', data_point['_id']),
            ('method', method),
            ('endpoint', endpoint),
            ('description', description),
        ])

        formatted_data.append(ordered_data_point)

    # Insert formatted data into MongoDB
    collection.insert_many(formatted_data)

    return formatted_data

def ask_for_confirmation(prompt):
    user_confirmation = input(f"GPT-3.5-turbo generated the following response:\n{prompt}\nDo you want to proceed? (yes/no): ")
    return user_confirmation.lower()

if __name__ == "__main__":
    app.run(debug=True, port=5100)

from flask import Flask
from flask_restplus import Api, Resource, fields
from pymongo import MongoClient

# MongoDB configuration
mongo_uri = 'mongodb://localhost:27017/'
database_name = 'Jfrog-Nexus'
collection_name = 'e'

# Create a Flask application
app = Flask(__name__)

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client[database_name]
collection = db[collection_name]

# Create a Flask-RESTPlus API
api = Api(app, version='1.0', title='My API', description='API documentation dynamically generated from MongoDB')

# Define the Swagger model
model = api.model('Item', {
    'name': fields.String(required=True, description='The item name'),
    'description': fields.String(required=True, description='The item description')
})

# Function to create resource class dynamically
def create_resource_class(api, endpoint_name, methods, description):
    namespace = api.namespace(endpoint_name, description=description)

    class DynamicResource(Resource):
        @namespace.marshal_with(model)
        def get(self, repository):
            """Get method description"""
            # Implement your logic here
            return {'name': 'Item 1', 'description': 'Description for Item 1'}

        @namespace.expect(model)
        @namespace.marshal_with(model)
        def post(self, repository):
            """Post method description"""
            # Implement your logic here
            return {'name': 'Item 1', 'description': 'Description for Item 1'}

        @namespace.expect(model)
        @namespace.marshal_with(model)
        def put(self, repository):
            """Put method description"""
            # Implement your logic here
            return {'name': 'Item 1', 'description': 'Description for Item 1'}

        @namespace.marshal_with(model)
        def delete(self, repository):
            """Delete method description"""
            # Implement your logic here
            return {'name': 'Item 1', 'description': 'Description for Item 1'}

    namespace.add_resource(DynamicResource, f'/repositories/{endpoint_name}/<string:repository>')

# Create endpoints dynamically from MongoDB data
for document in collection.find():
    endpoint_name = document.get('endpoint')
    endpoint_description = document.get('description')
    endpoint_methods = document.get('methods', ['GET'])

    # Create resource class dynamically under a namespace with the endpoint name
    create_resource_class(api, endpoint_name, endpoint_methods, endpoint_description)

if __name__ == '__main__':
    # Run the Flask application with Swagger documentation
    app.run(debug=True)

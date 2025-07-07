from pymongo import MongoClient

uri = "mongodb+srv://Hitesh-admin:0NJSMORTSg6Fmj4e@cluster0.dzr401v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
print(client.list_database_names())

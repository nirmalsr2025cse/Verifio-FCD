from pymongo import MongoClient
import os
import gridfs

client = MongoClient(os.getenv("MONGO_URI"))
db = client['Fake_Certification_Detector']
FCD_collection = db['Login_and_Signup']
Count = db['Count']
Colleges = db['College_DB']
Excel = db['Excel']
fs = gridfs.GridFS(db)
excel_fs = gridfs.GridFS(db,collection="excel_files")

Excel.create_index(
    [("email",1),("project_name",1)],
    unique = True
)
from flask import Flask,url_for,redirect,render_template,request
import ibm_boto3 #provides complete access to ibm-cos api library
from ibm_botocore.client import Config,ClientError

#Constants for IBM COS available in Service Credentials
COS_ENDPOINT="https://s3.jp-tok.cloud-object-storage.appdomain.cloud"
COS_API_KEY_ID="hMcZeq-nJYJYWXeFtLXJV-zqpiiweBWTYoKGfWmyDyxC"
COS_INSTANCE_CRN="crn:v1:bluemix:public:cloud-object-storage:global:a/25bb3eb3897244e2b841bc9d9f820185:cb37a635-42db-4789-871d-ca2d837f8f49::"

#Resource to access our COS
cos=ibm_boto3.resource("s3",
ibm_api_key_id=COS_API_KEY_ID,
ibm_service_instance_id=COS_INSTANCE_CRN,
config=Config(signature_version="oauth"),
endpoint_url=COS_ENDPOINT)

app=Flask(__name__)

def get_items(bucket_name):
    print(f"Retrieving bucket contents from: {bucket_name}")
    try:
        files = cos.Bucket(bucket_name).objects.all()
        files_names = []
        for file in files:
            files_names.append(file.key)
            print(f"Item: {file.key} ({file.size} bytes).")
        return files_names
    except ClientError as ce:
        print(f"CLIENT ERROR: {ce}\n")
    except Exception as e:
        print(f"Unable to retrieve bucket contents: {e}")

def multi_part_upload(bucket_name,item_name,file_path):
    try:
        print(f"Starting file transfer for {item_name} to bucket: {bucket_name}\n")
        part_size = 1024 * 1024 * 5
        file_threshold = 1024 * 1024 * 15

        transfer_config = ibm_boto3.s3.transfer.TransferConfig(
            multipart_threshold=file_threshold,
            multipart_chunksize=part_size
        )

        with open(file_path, "rb") as file_data:
            cos.Object(bucket_name, item_name).upload_fileobj(
                Fileobj=file_data,
                Config=transfer_config
            )

        print(f"Transfer of {item_name} Complete!\n")
    except ClientError as ce:
        print(f"CLIENT ERROR: {ce}\n")
    except Exception as e:
        print(f"Unable to complete multi-part upload: {e}")
    

#Now the flask implementation
@app.route("/",methods=["GET","POST"])
def index():
    return render_template("index.html",files=get_items("trialdemo001"))

@app.route("/file_upload",methods=["POST","GET"])
def upload():
    if request.method=="POST":
        bucket_name=request.form['bucket']
        item_name=request.form['filename']
        upload_item=request.files['file']
        multi_part_upload(bucket_name,item_name,upload_item.filename)
        return '<p>Go to <a href="/">Homepage</a></p>'
    if request.method=="GET":
        return render_template('upload.html')



if __name__=="__main__":
    app.run()





import os ,io
from config import *
from google.oauth2 import service_account
import sys
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

from importlib import reload
reload(sys)
#sys.setdefaultencoding('utf8')
from google.cloud import vision
from google.cloud import storage
from google.protobuf import json_format
from doc_txt_detect import detect_hand_writtent_text
credentials = service_account.Credentials.from_service_account_file(GCP_SERVICE_AUTH_FILE)


print("""
                Welcome
                
Choose the Option :
1.Insert Extracted Patient Details into Database . 
2.Display Details of all Patients.
3.Display Specific Data of a Patient.


""")
print("-".ljust(140,"-"))
slct=int(input("Please Enter your Choice from given Options :"))
print("-".ljust(140,"-"))
if slct==1:
    input_dir=str(input("Please enter top level directory of the test data: "))
    print("-".ljust(140,"-"))
    if os.path.isdir(input_dir):
        print("Input directory path is valid")
    else:
        print("\n Entered path is not valid please check the format and enter again ")
        os._exit(1)

    data_dir=os.path.abspath(input_dir)

    if not os.path.isdir(os.path.abspath(data_dir)+"/001"):
        print("Could not find the input directory (001) in entered path. Please check the input path")
        os._exit(2)

    if not os.path.exists(os.path.abspath(data_dir)+"/output/"):
            os.makedirs(os.path.abspath(data_dir)+"/output/")



    for input_file in os.listdir(data_dir+"/001"):
        storage_client = storage.Client(credentials=credentials,project="ocrnew")
        bucket = storage_client.get_bucket(BUCKET_NAME)
        blob = bucket.blob("input/"+input_file)
        blob.upload_from_filename(os.path.abspath(data_dir)+"/001/"+input_file)
        gcs_source_uri = "gs://" + BUCKET_NAME + INPUT_BUCKET_PATH+input_file
        gcs_destination_uri= "gs://" + BUCKET_NAME + OUTPUT_BUCKET_DIR
        detect_hand_writtent_text(gcs_source_uri,gcs_destination_uri ,os.path.abspath(data_dir)+"/output/"+input_file)
    print("All files are processed. Please find the output in data/output directory..")


elif slct==2:
    try:
        connection = mysql.connector.connect(host='localhost',
                                                     database='ocr',
                                                     user='root',
                                                     password='')
        sql_select_Query = "select * from patient_details"
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        print("Total number of Patients is: ", cursor.rowcount)
        print("No".ljust(5),"P.Id".ljust(12),"Patient Name".ljust(30),"Age".ljust(4),   "Gender".ljust(9),"Address".ljust(31),"Date" )
        print("-".ljust(105,"-"))
        for row in records:
            print(str(row[0]).ljust(5),str(row[1]).ljust(12),row[2].ljust(31),str(row[3]).ljust(4),row[4].ljust(9),row[5].ljust(30),row[6])
    
    except mysql.connector.Error as error:
        print("Failed to Display Record".format(error))  


elif slct==3:
    try:
        srr=int(input("Enter Patient Serial No :"))
        print("-".ljust(140,"-"))
        connection = mysql.connector.connect(host='localhost',
                                                     database='ocr',
                                                     user='root',
                                                     password='')
        sql_select_Query = "select * from patient_details WHERE sno=%s"
        sdd=(srr, )
        cursor = connection.cursor()
        cursor.execute(sql_select_Query,sdd)
        records = cursor.fetchall()
        print("No".ljust(5),"P.Id".ljust(12),"Patient Name".ljust(31),"Age".ljust(4),   "Gender".ljust(9),"Address".ljust(30),"Date" )
        print("-".ljust(105,"-"))
        for row in records:
            print(str(row[0]).ljust(5),str(row[1]).ljust(12),row[2].ljust(31),str(row[3]).ljust(4),row[4].ljust(9),row[5].ljust(30),row[6])
       
    
    except mysql.connector.Error as error:
        print("Failed to Display Record".format(error))   
        
else:
    print("Wrong Choice...")
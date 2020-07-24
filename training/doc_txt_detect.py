from google.oauth2 import service_account
from config import *
import os
# encoding=utf8
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
import sys
import re 
from importlib import reload
reload(sys)
#sys.setdefaultencoding('utf8')
from google.cloud import vision
from google.cloud import storage
from google.protobuf import json_format
credentials = service_account.Credentials.from_service_account_file(r"C:\Users\Samarth Yalameli\Desktop\1\handwritingrecognization_ml-master\training\ocrnew-270606-1a5cddc0d79e.json")#credentions of our bucket in Google cloud service
from PyPDF2 import PdfFileReader


#this function counts number of pages in fule
def numpages():
        input_dir1=str("")#Enter path of training file

        pdf = PdfFileReader(open(input_dir1,'rb'))
        pages = pdf.getNumPages()
        return pages
  
 #this function splits the result/information of single page and send it to database
def connections(result):
    k=2 
    a=6
    b=5
    c=4
    d=7
    e=8
    f=5
    
    heroRegex = re.compile (r'S.No.:|S.No.') 
    s2 = heroRegex.search(result) 
    s1=s2.group()
    
    if('S.No.'==s1):
        a=a+1
        
    heroRegex1 = re.compile (r'Name|Name:') 
    n2 = heroRegex1.search(result) 
    n1=n2.group()
    
    if('Name'==n1):
        b+=1
        
    heroRegex2 = re.compile (r'Age|Age:') 
    a2 = heroRegex2.search(result) 
    a1=a2.group()
    
    
    if('Age'==a1):
        c+=1
        
    heroRegex3 = re.compile (r'Gender|Gender:') 
    g2 = heroRegex3.search(result) 
    g1=g2.group()
   
    if('Gender'==g1):
        d+=1
    
    heroRegex4 = re.compile (r'Address|Address:') 
    ad2 = heroRegex4.search(result) 
    ad1=ad2.group()
   
    if('Address'==ad1):
        e+=1
    
    heroRegex5 = re.compile (r'Date|Date:') 
    d2 = heroRegex5.search(result) 
    d1=d2.group()
    
    if('Date'==d1):
        f+=1
    
    
   # print(s1)
    #print(a1)
    #print(n1)
    #print(g1)
    #print(ad1)
    #print(d1)
    
    data = result.replace('\n', ' ')
    s = data
    sl = s.split()
    #print(type(sl))
    print(sl)
    def nextword(target, source):
        for i, w in enumerate(source):
            if w == target:
                return source[i-1]
    def nextword1(target, source):
        for i, w in enumerate(source):
            if w == target:
                return source[i+1]        
    
    if("Patient"==nextword1('2202', sl)):
        #srno =nextword('Gender:', sl)

        srno = data[data.find(s1)+a:data.find(g1)]
        name = data[data.find(n1)+b:data.find(ad1)]
        age = data[data.find(a1)+c:data.find(d1)]
        gender = data[data.find(g1)+d:data.find(a1)]
        adress = data[data.find(ad1)+e:data.find(s1)]
        #adress =nextword1('Address:', sl)
        date = data[data.find(d1)+f:data.find("Rx")]
    
    else:
        #srno =nextword('Patient', sl)
    
        srno = data[data.find(s1)+a:data.find("Patient")]
        name = data[data.find(n1)+b:data.find(g1)]
        age = data[data.find(a1)+c:data.find(ad1)]
        gender = data[data.find(g1)+d:data.find(a1)]
        adress = data[data.find(ad1)+e:data.find(d1)]
        date = data[data.find(d1)+f:data.find("Rx")]
    
   
    #file.close()

            #Store to database

    try:
       # print(str(srno) + name)
        connection = mysql.connector.connect(host='localhost',
                                                 database='ocr',
                                                 user='root',
                                                 password='')
        mySql_insert_query = """INSERT INTO patient_details (sno, pname, age, gender,address,date) VALUES (%s, %s, %s, %s ,%s ,%s) """
        db=(srno, name, age, gender,adress,date)
        cursor = connection.cursor()
        cursor.execute(mySql_insert_query,db)
        connection.commit()
        print(cursor.rowcount, "Record inserted successfully into Laptop table")
        cursor.close()

    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))

    finally:
        if (connection.is_connected()):
            connection.close()
            print("MySQL connection is closed")    
    

    #Tis function puts the file in bucket and fetch json file
def detect_hand_writtent_text(gcs_source_uri, gcs_destination_uri,input_file):
    """OCR with PDF/TIFF as source files on GCS"""

    import re
    # Supported mime_types are: 'application/pdf' and 'image/tiff'
    mime_type = 'application/pdf'
    #Calling page count
    p=numpages()
    # How many pages should be grouped into each json output file.
    batch_size = p
    client = vision.ImageAnnotatorClient(credentials=credentials)
    feature = vision.types.Feature(
        type=vision.enums.Feature.Type.DOCUMENT_TEXT_DETECTION)
    gcs_source = vision.types.GcsSource(uri=gcs_source_uri)
    print("Processing File "+input_file.split("/")[-1]+" ...")
    input_config = vision.types.InputConfig(
        gcs_source=gcs_source, mime_type=mime_type)
    gcs_destination = vision.types.GcsDestination(uri=gcs_destination_uri)
    output_config = vision.types.OutputConfig(
        gcs_destination=gcs_destination, batch_size=batch_size)
    async_request = vision.types.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config,
        output_config=output_config)
    operation = client.async_batch_annotate_files(
        requests=[async_request])

    print('Waiting for the operation to finish.')
    operation.result(timeout=180)

    storage_client = storage.Client(credentials=credentials,project="ocrnew")
    bucket = storage_client.get_bucket(BUCKET_NAME)
    # Process the first output from API
    blob=bucket.blob("output/output-1-to-21.json")
    #json file is converted to text file
    json_string = blob.download_as_string()
    response = json_format.Parse(
        json_string, vision.types.AnnotateFileResponse())
    
    # The actual response for the first page of the input file.
   
    for x in range(p):
        #Here p is number of pages and x is page no to fetch ....it will fetch on by one
        page_response = response.responses[x]
        annotation = page_response.full_text_annotation

        f = open(input_file.split('.')[0]+".txt", "a")
        result=annotation.text
        print("-".ljust(140,"-"))
        pg=x+1
        print("Page No: "+ str(pg))#prints page number
        print("-".ljust(140,"-"))
        print(result)#prints result
        print("-".ljust(140,"-"))
        
        # The below line gives info about type of result
        #print(type(result))
        
        #connection functions is called to save data in database 
        connections(result)
        f.write(annotation.text)
    f.close()
    
    return True

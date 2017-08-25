from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib
import urllib2
import shutil
import os,tarfile

def make_targz(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def upload_and_savedb(dirpath,json_path_source):
    # tar file      
    shutil.rmtree(os.path.join(dirpath,"binary"))
    json_path=os.path.join(dirpath,os.path.basename(json_path_source))
    shutil.copyfile(json_path_source,json_path)
    output_file=dirpath+".tar.gz"
    make_targz(output_file,dirpath)

    # upload
    register_openers()
    datagen, headers = multipart_encode({'file':open(output_file, 'rb')})
    request = urllib2.Request('http://localhost:8000/test_post', datagen, headers)
    response = urllib2.urlopen(request)
    save_path = response.read()

    # save db
    db_values={"save_path":save_path,"json_path":json_path}
    db_data = urllib.urlencode(db_values)
    db_url = "http://localhost:8000/save_data"
    db_request = urllib2.Request(db_url,db_data)
    db_response = urllib2.urlopen(db_request)
    print db_response.read()

# example
dirpath = "C:\\Users\\yangtt\\Desktop\\fanxh-OptiPlex-3020_WS_17-08-07_11-03-46" 
json_path_source="C:\\Users\\yangtt\\Desktop\\Normalised_Logs\\ts-OptiPlex-3020_score_post.json"
upload_and_savedb(dirpath,json_path_source)
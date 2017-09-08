from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

import urllib
import urllib2
import shutil
import os,tarfile
import json
from caliper.client.shared import caliper_path
import caliper.server.utils as server_utils

def make_targz(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def upload_result(target,server_url):
    '''
    upload result to server
    :param target: target machine running test
    :return: None
    '''
    #workspace dir path for the test, for example: /home/fanxh/caliper_output/hansanyang-OptiPlex-3020_WS_17-05-03_11-29-29
    dirpath = caliper_path.WORKSPACE;

    #dir path for score, for example: /home/fanxh/caliper_output/frontend/frontend/data_files/Normalised_Logs
    dir_score_path = caliper_path.HTML_DATA_DIR_OUTPUT

    target_name = server_utils.get_host_name(target)
    #score json file name , for example:hansanyang-OptiPlex-3020_score_post.json
    score_json_file_name = target_name + '_score_post.json'

    #for example, /home/fanxh/caliper_output/frontend/frontend/data_files/Normalised_Logs/hansanyang-OptiPlex-3020_score_post.json
    score_json_file_fullname = os.path.join(dir_score_path,score_json_file_name)

    upload_and_savedb(dirpath,score_json_file_fullname,server_url)


def upload_and_savedb(dirpath,json_path_source,server_url):
    # tar file 
    bin_file = os.path.exists(os.path.join(dirpath,"binary"))
    if bin_file:   
        shutil.rmtree(os.path.join(dirpath,"binary"))
    json_path=os.path.join(dirpath,os.path.basename(json_path_source))
    shutil.copyfile(json_path_source,json_path)
    output_file=dirpath+".tar.gz"
    make_targz(output_file,dirpath)

    # upload
    register_openers()
    datagen, headers = multipart_encode({'file':open(output_file, 'rb')})
    request = urllib2.Request('http://'+server_url+'/test_post', datagen, headers)
    response = urllib2.urlopen(request)
    save_path = response.read()

    # save db
    with open(json_path,'r') as load_f:
        json_data = json.load(load_f)
    db_values={"save_path":save_path,"json_data":json_data}
    db_data = urllib.urlencode(db_values)
    db_url = "http://"+server_url+"/save_data"
    db_request = urllib2.Request(db_url,db_data)
    db_response = urllib2.urlopen(db_request)
    print db_response.read()

# example
#dirpath = "C:\\Users\\yangtt\\Desktop\\fanxh-OptiPlex-3020_WS_17-08-07_11-03-46"
# dirpath = caliper_path.workspace;
#json_path_source="C:\\Users\\yangtt\\Desktop\\Normalised_Logs\\ts-OptiPlex-3020_score_post.json"
# json_path_source = caliper_path.HTML_DATA_DIR_OUTPUT
# upload_and_savedb(dirpath,json_path_source)
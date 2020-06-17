#! python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 19:56:16 2020

@author: 劉又聖
"""

import socket, sys, os, logging
from networkAPI import NetAPI

#TODO 寫個check file routine
def scan_dir_and_cktime(dir_path, previous_file=None):
    def scan_dir(dir_path):
        if 'update_dict' not in dir(scan_dir):
            scan_dir.update_dict = {}
            
        """ Scan the directory recursively """
        if os.path.isdir(dir_path):
            for filename in os.listdir(dir_path):
                fullpath = os.path.join(dir_path, filename)
                scan_dir(fullpath)
        else:
            # Here dir_path is full path file name
            scan_dir.update_dict[dir_path] = [ os.path.getsize(dir_path),
                                               os.path.getmtime(dir_path) ]
            
        return scan_dir.update_dict
    """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
    ###################
    # Error Detection #
    if not os.path.exists(previous_file):
        raise FileNotFoundError(f'{previous_file} is not found.')
    ###################
    import json
    
    if os.path.exists('previous.json'):
        previous_file = 'previous.json'
    
    file_status = scan_dir(dir_path)
    update_list = {}
    if not previous_file:
        # 第一次掃描目錄，需要建立 previous status file    
        logging.debug('First, create previous status file.')
    else:
        pre_file_status = json.load(open(previous_file, 'r'))
        
        for fn, st in file_status.items():
            if not pre_file_status.get(fn):
                logging.debug('Come up an new file.')
                update_list[fn] = st  # 出現新檔案
            else:
                if pre_file_status[fn] != file_status[fn]:
                    logging.debug('File has been modify.')
                    update_list[fn] = st  # 檔案資料有變動
                else:
                    pass  # 檔案沒有變動
    # Save file status
    json.dump(file_status, open('previous.json', 'w'), indent=2)
    return update_list

def send_dir(handle, dir_paths):
    if isinstance(dir_paths, (list, tuple)):
        for dir_path in dir_paths:
            for file in scan_dir_and_cktime(dir_path).keys():
                handle.send_file(file)

def client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect( (host, port) )

    handle = NetAPI(sock)
    handle.send_file('server.py')

    sock.close()
    
def main():
    msg = "Usage: %s host port" % sys.argv[0]
    if len(sys.argv) != 3:
        print(msg)
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])
        client(host, port)

if __name__ == "__main__":
    main()
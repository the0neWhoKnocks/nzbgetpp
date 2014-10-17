#!/usr/bin/env python
#
##############################################################################
### NZBGET SCAN SCRIPT                                          ###

# Unzips zipped nzbs.
#
# NOTE: This script requires Python to be installed on your system.

##############################################################################
### OPTIONS                                                                ###
### NZBGET SCAN SCRIPT                                          ###
##############################################################################

import os
import sys
import zipfile
import pickle
import datetime

filename = os.environ['NZBNP_FILENAME']
ext = os.path.splitext(filename)[1].lower()
cat = os.environ['NZBNP_CATEGORY']
dir = os.environ['NZBNP_DIRECTORY']
prio = os.environ['NZBNP_PRIORITY']
top = os.environ['NZBNP_TOP']
pause = os.environ['NZBNP_PAUSED']
if 'NZBNP_DUPEKEY' in os.environ:
    dupekey = os.environ['NZBNP_DUPEKEY']
    dupescore = os.environ['NZBNP_DUPESCORE']
    dupemode = os.environ['NZBNP_DUPEMODE']
else:
    dupekey = None
    dupescore = None
    dupemode = None


tmp_zipinfo = os.path.join(os.environ.get('NZBOP_TEMPDIR'), r'nzbget\unzip_scan\info')
nzb_list = []

def save_obj(obj, name):
    tp = os.path.dirname(name)
    if not os.path.exists(tp):
        try:
            os.makedirs(tp)
        except:
            print "Error creating Dir " + tp
            return
    try:
        with open(name, 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
    except:
        print "Error saving: " + name

def load_obj(name):
    if os.path.isfile(name):
        try:
            with open(name, 'r') as f:
                return pickle.load(f)
        except:
            print "Error loading " + name
            return None
    else:
        return None

def save_nzb_list():
    if nzb_list:
        save_obj(nzb_list, tmp_zipinfo)
    else:
        if os.path.isfile(tmp_zipinfo):
            try:
                os.unlink(tmp_zipinfo)
            except:
                print "Error deleting " + tmp_zipinfo

def load_nzb_list():
    global nzb_list
    nzb_list = load_obj(tmp_zipinfo)
    if nzb_list:
        now = datetime.datetime.now()
        for i, n in enumerate(nzb_list):
            # remove files from the list that were added over 1 day ago
            if (now - n[8]).days >= 1:
                del nzb_list[i] 

def get_files(zf):
    zi = zf.infolist()
    zi[:] = [el for el in zi if os.path.splitext(el.filename)[1].lower() == '.nzb']
    return zi

if ext == '.zip':
    load_nzb_list()
    zipf = zipfile.ZipFile(filename, mode='r')
    zf = get_files(zipf)
    if zf:
        zipf.extractall(path = dir, members = zf)
        now = datetime.datetime.now()
        for z in zf:
            if nzb_list:
                nzb_list.append([z.filename, cat, prio, top, pause, dupekey, dupescore, dupemode, now])
            else:
                nzb_list = [[z.filename, cat, prio, top, pause, dupekey, dupescore, dupemode, now]]
        save_nzb_list()
    zipf.close()
    try:
        os.unlink(filename)
    except:
        print "Error deleting " + filename

elif ext == '.nzb' and os.path.exists(tmp_zipinfo):
    load_nzb_list()
    ni = None
    f_l = os.path.basename(filename).lower()
    for i, nf in enumerate(nzb_list):
        if nf[0].lower() == f_l:
            ni = i
            break
    if ni is not None:
        print "[NZB] CATEGORY=" + str(nzb_list[ni][1])
        print "[NZB] PRIORITY=" + str(nzb_list[ni][2])
        print "[NZB] TOP=" + str(nzb_list[ni][3])
        print "[NZB] PAUSED=" + str(nzb_list[ni][4])
        if dupekey is not None:
            print "[NZB] DUPEKEY=" + str(nzb_list[ni][5])
            print "[NZB] DUPESCORE=" + str(nzb_list[ni][6])
            print "[NZB] DUPEMODE=" + str(nzb_list[ni][7])
        del nzb_list[ni]
        save_nzb_list()
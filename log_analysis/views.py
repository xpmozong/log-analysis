#encoding:utf8
import os
import json
import math
import datetime
import time
import cgi
import re

from django.template import loader, Context
from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.db import connection
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

COMBINED_LOGLINE_PAT1 = re.compile(
  r'(?P<origin>\d+\.\d+\.\d+\.\d+) '
+ r'\[(?P<date>[^\[\]:]+):(?P<time>\d+:\d+:\d+) (?P<tz>[\-\+]?\d\d\d\d)\] '
+ r'"(?P<method>\w+) (?P<path>[\S]+) (?P<protocol>[^"]+)" '
+ r'(?P<status>\d+) (?P<size>\d+) '
+ r'(?P<referrer>"[^"]*") (?P<client>"[^"]*") "(?P<identd>-|\w*)" '
+ r'(?P<times>\d+\.\d+\d+\d+)'
)

BIGCOUNT = 30000

FILE = os.getcwd()+"/log_analysis/www.xxx.com.log"

def home(request):
    context = {}
    pvcount = 0
    size = 0
    pathlist = {}
    iphitlist = {}
    methodlist = {}
    statuslist = {}
    clientlist = {}
    timeslist = {}
    for logline in open(FILE):
        match_info = COMBINED_LOGLINE_PAT1.match(logline)
        ilist = {}
        if not match_info:
            continue
        else:
            pvcount += 1
            if(pvcount > BIGCOUNT):
                break
            for key, value in match_info.groupdict().items():
                ilist[key] = value

            timeslist[ilist['path']] = ilist['times']
            path = ilist['path']
            if(path != '/'):
                if(path != '/index.php'):
                    pathlist[path] = pathlist.get(path, 0) + 1

            ip = ilist['origin']
            iphitlist[ip] = iphitlist.get(ip, 0) + 1

            method = ilist['method']
            methodlist[method] = methodlist.get(method, 0) + 1

            status = ilist['status']
            statuslist[status] = statuslist.get(status, 0) + 1

            client = ilist['client']
            clientlist[client] = clientlist.get(client, 0) + 1

            size += int(ilist['size'])

    pathdict = sorted(pathlist.iteritems(), key=lambda d:d[1], reverse = True)
    context['pathdict'] = pathdict[0:10]

    ipdict = sorted(iphitlist.iteritems(), key=lambda d:d[1], reverse = True)
    ipcount = len(ipdict)
    context['ipdict'] = ipdict[0:10]

    methoddict = sorted(methodlist.iteritems(), key=lambda d:d[1], reverse = True)[0:20]
    context['methoddict'] = methoddict

    statusdict = sorted(statuslist.iteritems(), key=lambda d:d[1], reverse = True)[0:20]
    context['statusdict'] = statusdict

    clientdict = sorted(clientlist.iteritems(), key=lambda d:d[1], reverse = True)[0:20]
    context['clientdict'] = clientdict

    context['ipcount'] = ipcount
    context['pvcount'] = pvcount
    context['size'] = size

    timesdict = sorted(timeslist.iteritems(), key=lambda d:d[1], reverse = True)
    context['timesdict'] = timesdict[0:10]
    print context['timesdict']

    return render_to_response('home.html', context)

def more(request):
    context = {}
    pvcount = 0
    context['itype'] = itype = request.GET.get('type','path')
    if(itype == 'path'):
        context['itypestr'] = '页面'
    else:
        context['itypestr'] = 'IP'
    pagelist = {}
    for logline in open(FILE):
        pvcount += 1
        if(pvcount > BIGCOUNT):
            break
        match_info = COMBINED_LOGLINE_PAT1.match(logline)
        if not match_info:
            continue
        else:
            for key, value in match_info.groupdict().items():
                if(itype == 'path'):
                    if(key == 'path'):
                        path = value
                        if(path != '/'):
                            if(path != '/index.php'):
                                pagelist[path] = pagelist.get(path, 0) + 1
                else:
                    if(key == 'origin'):
                        ip = value
                        pagelist[ip] = pagelist.get(ip, 0) + 1

    pagedict = sorted(pagelist.iteritems(), key=lambda d:d[1], reverse = True)
    context['pagedict'] = pagedict[0:1000]

    return render_to_response('more.html', context)

def detail(request):
    context = {}
    context['itype'] = itype = request.GET.get('type','method')
    context['path'] = request.GET.get('path','')
    context['path'] = context['path'].replace('"','')
    pagelist = []
    pathlist = {}
    iphitlist = {}
    statuslist = {}
    methodlist = {}
    clientlist = {}
    pvcount = 0
    totalpvcount = 0
    size = 0
    if context['path']:
        for logline in open(FILE):
            totalpvcount += 1
            if(totalpvcount > BIGCOUNT):
                break

            match_info = COMBINED_LOGLINE_PAT1.match(logline)
            ilist = {}
            if not match_info:
                continue
            else:
                for key, value in match_info.groupdict().items():
                    ilist[key] = value
                if(ilist[itype] == context['path']):
                    pvcount += 1
                    size += int(ilist['size'])
                    path = ilist['path']
                    pathlist[path] = pathlist.get(path, 0) + 1
                    ip = ilist['origin']
                    iphitlist[ip] = iphitlist.get(ip, 0) + 1
                    status = ilist['status']
                    statuslist[status] = statuslist.get(status, 0) + 1
                    method = ilist['method']
                    methodlist[method] = methodlist.get(method, 0) + 1
                    client = ilist['client']
                    clientlist[client] = clientlist.get(client, 0) + 1
##                    pagelist.append(ilist)

##    context['list'] = pagelist[0:1000]

    pathdict = sorted(pathlist.iteritems(), key=lambda d:d[1], reverse = True)
    context['pathdict'] = pathdict[0:20]

    ipdict = sorted(iphitlist.iteritems(), key=lambda d:d[1], reverse = True)
    context['ipdict'] = ipdict[0:20]

    statusdict = sorted(statuslist.iteritems(), key=lambda d:d[1], reverse = True)[0:20]
    context['statusdict'] = statusdict[0:20]

    methoddict = sorted(methodlist.iteritems(), key=lambda d:d[1], reverse = True)[0:20]
    context['methoddict'] = methoddict[0:20]

    clientdict = sorted(clientlist.iteritems(), key=lambda d:d[1], reverse = True)[0:20]
    context['clientdict'] = clientdict[0:20]

    context['ipcount'] = len(ipdict)
    context['pvcount'] = pvcount
    context['size'] = size

    return render_to_response('detail.html', context)









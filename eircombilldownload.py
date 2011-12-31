#!/usr/bin/python

import cookielib
import json
import mechanize
import os
import re
import subprocess
import sys
import time
import urllib
import urlparse

# Create .eircombilldownload in your home directory like this:
# { "username": "user@example.com", "passsword": "letmein" }
with open(os.path.expanduser('~/.eircombilldownload')) as fp:
  config = json.load(fp)

if len(sys.argv) > 1:
  os.chdir(sys.argv[1])

# Browser
br = mechanize.Browser()
ajax = mechanize.Browser()

# Browser options
br.set_handle_robots(False)
ajax.set_handle_robots(False)

# Want debugging messages?
def debug():
  br.set_debug_http(True)
  br.set_debug_responses(True)
  ajax.set_debug_http(True)
  ajax.set_debug_responses(True)

br.addheaders = [('User-Agent', 'eircombilldownload/0.1')]
ajax.addheaders = br.addheaders + [('Accept', 'application/json')]

# Index
br.open('http://www.eircom.net/myeircom/')

# Login
br.select_form(nr=0)
br.form['username'] = config['username']
br.form['password'] = config['password']

br.form.action = 'https://secure.eircom.net/FixedLineServices/login'
data = json.loads(ajax.open(br.click()).read())

# Accounts
sessionId = data['envelope']['broadvisionSession']['sessionId']
engineId = data['envelope']['broadvisionSession']['engineId']

data = json.loads(ajax.open('accounts').read())

# Pdf urls
for account in data['envelope']['data']:
  current_account = account['accountNumber']

  pdfUrl = ('https://www.eircom.ie/cgi-bin/bvsm/bveircom/acctmgt/viewbill.jsp?'
    + urllib.urlencode({
        'BV_SessionID' : sessionId,
        'BV_EngineID' : engineId,
        'viewBillAction' : 'viewPDFFile',
        'pdfAccountNo' : current_account,
  }))

  page = br.open(pdfUrl).read()

  m = re.search("replace\('(.*)'\)", page)
  pdfUrl = urlparse.urljoin(pdfUrl, m.group(1))
  localPdf = pdfBase = 'eircom-%s-%s.pdf' % (
      current_account, time.strftime('%Y-%m'))
  index = 0
  while os.path.exists(localPdf):
    index += 1
    localPdf = '%s.%d' % (pdfBase, index)
  subprocess.call(['wget', '-O', localPdf, pdfUrl])

#!/usr/bin/env python
from urlgrabber import urlread
import re
from BeautifulSoup import BeautifulSoup, SoupStrainer
import datetime
import shutil
import MySQLdb

now = datetime.datetime.now()
nowstring = str(now)

urlgrab = urlread('https://www.facebase.org/node/215')
output = """{
title: "axel genes to enhancers",
chr: "http://localhost",
start: 1111,
end: 2222,
items: ["""

conn = MySQLdb.connect(host='genome-mysql.cse.ucsc.edu', user='genome', db='mm9')
curs = conn.cursor()

for link in BeautifulSoup(urlgrab, parseOnlyThese=SoupStrainer('a')):
    if link.has_key('href'):
            if 'transgenic' in link['href']:
                 url2 = 'https://www.facebase.org'+link['href']
                 url2 = str(url2)
                 urlgrab2 = urlread(url2)
                 soup2 = BeautifulSoup(urlgrab2)
                 for el in soup2.findAll({'p' : True}):
                     for item in el:
                         if re.search('ouse genom', str(item)):
                             item = re.sub('&nbsp;','',item)
                             chrom = re.sub('Mouse genome mm9, ','',item)
                             start = re.sub('chr\d*:','',chrom)
                             end = re.sub('.*-','',start)
                             start = re.sub('-.*','',start)
                             chrom = re.sub(':.*','',chrom)
                             chrom = re.sub(' ','',chrom)

                             startMinusOneMb  = int(start)-1000000
                             startMinusOneMb  = str(startMinusOneMb)
                             endPlusOneMb = int(end)+1000000
                             endPlusOneMb = str(endPlusOneMb)
                             sql = 'SELECT DISTINCT geneSymbol FROM kgXref WHERE kgID IN (SELECT name from knownGene WHERE chrom = "'+chrom+'" AND cdsStart > '+startMinusOneMb+' AND  cdsEnd < '+endPlusOneMb+');'
                             print(sql)
                             curs.execute(sql)
                             print(curs.rowcount)
                             genesAsJsonArray = "[ "
                             for row in curs.fetchall():
                                 print(row)
                                 row = str(row)
                                 print(row)
                                 row = re.sub("^..","",row)
                                 row = re.sub("...$","",row)
                                 print(row)
                                 genesAsJsonArray += '"'
                                 genesAsJsonArray += row
                                 genesAsJsonArray += '", '
                                 
                             genesAsJsonArray = genesAsJsonArray[:-1]
                             genesAsJsonArray = genesAsJsonArray[:-1]
                             genesAsJsonArray += "]"

                             #output += "{chr:\""+chrom+"\", start: "+start+", end: "+end+", url: \""+url2+"\"},"
                             output += "{chr:\""+chrom+"\", start: "+start+", end: "+end+", url: \""+url2+"\", genes: "+genesAsJsonArray+" },"

#remove last comma:
output = output[:-1]
output += "]}"
copyOld= '/u01/www/html/trash/enhancers2'+nowstring+'.json'
fileorig = '/u01/www/html/trash/enhancers2.json'
shutil.copy2(fileorig, copyOld)
fileout = open('/u01/www/html/trash/enhancers2.json','w')
fileout.write(output)
fileout.close()
import cgi
print("Content-type: text/html")
print
print """<HTML><HEAD><TITLE>JSON OK</TITLE></HEAD><BODY>JSON OK"""
print(output)
print """</BODY></HTML>"""


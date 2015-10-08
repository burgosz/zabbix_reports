# zabbix_reports
# Zabbix Reports

Zabbix reports is a Django based web application which can generate well readable SLA reports from IT services.

### Installation
Install pip:
```sh
$ sudo apt-get install python-pip
```
Install dependencies with pip:
```sh
$ sudo pip install django
$ sudo pip install py-zabbix
$ sudo pip install python-dateutil
$ sudo pip install python-memcached
```
Clone the repository to somewhere in your Python. To check this:
```sh
$ python -c '                                                                         
import sys
print(sys.path)
'
```
Install apache2 with mod_wsgi:
```sh
$ sudo apt-get install apache2
$ sudo apt-get install libapache2-mod-wsgi
```
To enable caching install memcached, or use memcache from other host. This can be configured in the setup.py:
```sh
$ sudo apt-get install memcached
```
### Configuration

Configure Apache to serve the page. Replace the locations with the location of the installed zabbix_reports.

        WSGIScriptAlias / /usr/local/lib/python2.7/dist-packages/zabbix_reports/wsgi.py
        WSGIDaemonProcess zabbix_reports user=www-data group=www-data  processes=3 threads=10 home=/usr/local/lib/python2.7/dist-packages/zabbix_reports display-name=%{GROUP}
        WSGIApplicationGroup %{GLOBAL}
        <Directory "/usr/local/lib/python2.7/dist-packages/zabbix_reports/">
                Options Indexes FollowSymLinks MultiViews
                AllowOverride None
                Require all granted
        </Directory>
### Usage
The site accepts 3 get parameters:
* tid: is the ID of the top service (the first parent), you can add more than one top id seperated with '-'
* from: the start of the time period in YYYYMMDDhhmm format.
* till: the end of the time period in YYYYMMDDhhmm format.

For example:
localhost/report/?tid=30&from=201505010000&till=201506010000

### PDF generation
Download wkhtml2pdf and install it. http://wkhtmltopdf.org/downloads.html

To generate the pdf use the command below:
```sh
LANG=hu_HU.utf8 wkhtmltopdf --load-error-handling ignore --footer-left "[date]" --footer-center "Oldal: [page] / [toPage]" --footer-font-size 8 http://localhost/report/\?tid\=30\&from\=201508010000\&till\=201509010000 report.pdf
```

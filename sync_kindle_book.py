# coding: utf-8
import os
import sys
import smtplib
import mimetypes
from getpass import getpass
from functools import partial
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart


if sys.version_info.major < 3:
    INPUT = raw_input
    from ConfigParser import ConfigParser as cparser
else:
    INPUT = input
    from configparser import ConfigParser as cparser


config = cparser()
config.read('config.ini')
get_config = partial(config.get, 'INFO')

smtp_addr = get_config('smtp_addr')
smtp_port = get_config('smtp_port')
from_addr = get_config('from_addr')
to_addr = get_config('to_addr')
password = get_config('password')


if smtp_port in (465, 994):
    connect_class = smtplib.SMTP_SSL
else:
    connect_class = smtplib.SMTP


def send_mail(smtp_addr, smtp_port, from_addr, password, to_addr, message, set_debug=0):
    if smtp_port in (465, 994):
        connect_class = smtplib.SMTP_SSL
    else:
        connect_class = smtplib.SMTP
    server = connect_class(smtp_addr, smtp_port, timeout=10)
    server.set_debuglevel(set_debug)
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr, message.as_string())


def gen_message(file_path, from_addr, to_addr):
    msg = MIMEMultipart()
    msg['Subject'] = os.path.basename(file_path)
    msg['From'] = from_addr
    msg['To'] = to_addr
    mi = file_mime(file_path)
    msg.attach(mi)
    return msg


def file_mime(file_path):
    ctype, _ = mimetypes.guess_type(file_path)
    maintype, subtype = ctype.split('/', 1)
    msg = MIMEBase(maintype, subtype)
    msg.set_payload(open(file_path).read())
    msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
    return msg


if __name__ == '__main__':
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1].strip()):
        print('请确认是否输入待上传路径，或文件是否存在')
        sys.exit(1)
    
    set_debug = 1 if len(sys.argv) > 2 else 0

    file_path = sys.argv[1]
    if os.stat(file_path).st_size > 20 * 1024 * 1024:
        print('同步文件不得大于20M')
        sys.exit(2)

    message = gen_message(file_path, from_addr, to_addr)
    send_mail(smtp_addr, int(smtp_port), from_addr, password, to_addr, message, set_debug)
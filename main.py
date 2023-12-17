import socket
import string
import netifaces
import smtplib
from email.mime.text import MIMEText
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
data_file_path = os.path.join(current_dir, 'data.json')
html_file_path = os.path.join(current_dir, 'data.html')
config_file_path = os.path.join(current_dir, 'config.json')


def get_iface_ips() -> dict:
    ifaces = netifaces.interfaces()
    ip_dict: dict = {}

    for iface in ifaces:
        addresses = netifaces.ifaddresses(iface)
        iface_ip = {'name': iface, 'ipv4': [], 'ipv6': []}
        if netifaces.AF_INET in addresses:
            for address in addresses[netifaces.AF_INET]:
                ipv4_address = address['addr']
                iface_ip['ipv4'].append(ipv4_address)

            # 获取IPv6地址
        if netifaces.AF_INET6 in addresses:
            for address in addresses[netifaces.AF_INET6]:
                ipv6_address = address['addr']
                iface_ip['ipv6'].append(ipv6_address)
        ip_dict[iface_ip['name']] = iface_ip
    return ip_dict


def send_email(_title: str, _content: str):
    with open(config_file_path, 'r') as file:
        config = json.load(file)

    message = MIMEText(_content, 'html', 'utf-8')
    message['Subject'] = _title
    message['From'] = config['sender_email']
    message['To'] = config['receivers'][0]

    try:
        smtp_obj = smtplib.SMTP_SSL(host=config['smtp_host'], port=config['smtp_port'])
        smtp_obj.login(config['sender_email'], config['sender_passwd'])
        smtp_obj.sendmail(config['sender_email'], config['receivers'], message.as_string())
        smtp_obj.quit()
    except smtplib.SMTPException as e:
        print('发送邮件失败', e)
        os.remove(data_file_path)


def is_iface_changed(_iface_ips: dict) -> bool:
    if os.path.isfile(data_file_path):
        with open(data_file_path, 'r') as file:
            file_content = json.load(file)

        if file_content == _iface_ips:
            print('IP not changed')
            return False
        else:
            with open(data_file_path, 'w') as file:
                file.write(json.dumps(iface_ips))
            print('IP changed')
            return True
    else:
        json_str = json.dumps(_iface_ips)
        with open(data_file_path, 'w') as file:
            file.write(json_str)
            print('data.json not exists')
        return True


def gen_html(_iface_ips: dict) -> str:
    data_str = ''
    for value in _iface_ips.values():
        data_str += string.Template("""
        <tr>
            <td>$name</td>
            <td>$ipv4</td>
            <td>$ipv6</td>
        </tr>
        """).substitute(value)
    with open(html_file_path, 'r') as file:
        html_content = file.read()
        return html_content.replace('${content}', data_str)


if __name__ == '__main__':
    hostname = socket.gethostname()
    iface_ips = get_iface_ips()

    if is_iface_changed(iface_ips):
        title = hostname + ' IP Changed'
        content = gen_html(iface_ips)
        send_email(title, content)

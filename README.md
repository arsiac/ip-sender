# IP Sender

## Usage

1. pull the repository
    ```shell
    cd /opt && git clone https://github.com/arsiac/ip-sender.git
    ```

2. add `config.json` to /opt/ip-sender/
   ```json
   {
       "smtp_host": "smtp.email.example",
       "smtp_port": 465,
       "sender_email": "sender@email.example",
       "sender_passwd": "sender email password",
       "receivers": [
            "receiver@email.example"
       ]
   }
    ```

3. add cron job
    ```shell
    pip install netifaces2 
    ```

    ```text
    */5 8-20 * * * /usr/bin/python3 /opt/ip-sender/main.py
    ```
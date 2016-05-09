# adxseller2slack
I wrote this simple Slack bot to help people to pull Google Adexchange Seller performance data into Slack. It is inspired by brooksc/gmail2slack and use standard Google OAuth/Adexchange Seller API plus lins05/slackbot.


# Instructions:
1. Clone this repository
2. Create a virtual environment and install required packages (virtualenv + pip install)
3. Config your Google Adexchange seller API access and your Slack API integration
4. Put your Google API client ID and client secret in adxseller_client_secrets.json and your Slack API token in slackbot_settings.py
5. Run 'python adxseller2slack.py'

# Notes:
If you query the Adx performance data for the first time, the bot will ask you for authorization. This is done via stand Google OAuth. Once permission is granted, the access/refresh token will be saved in adxseller_client_secrets.json so that you don't have to jump through the same hoop again. If you want to revoke the credentials later, you can easily do it in Google API dashboard.

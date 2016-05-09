import StringIO
import datetime
from datetime import timedelta

import httplib2
from googleapiclient.discovery import build
from oauth2client import multistore_file
from oauth2client.client import flow_from_clientsecrets
from slackbot.bot import *


@respond_to('query (.*) (.*)', re.IGNORECASE)
def query(message, ad_client_id, end_date):
    global as2s
    as2s.cache_ad_client_id_and_end_date(ad_client_id, end_date)
    oauth_status = as2s.do_google_oauth()
    if 'success' in oauth_status:
        message.reply('Pulling nubmers for you. Sit tight ... ')
        say = as2s.query_performance()
        message.reply(say.getvalue())
    else:
        say = "*Please first grant me permission to access your AdX Seller account by:* \n" \
              "1. visit this URL: \n"
        say = say + oauth_status['pending']
        say = say + "\n2. send me the verification code by typing 'verify: [code]'"
        message.reply(say)


@respond_to('verify: (.*)', re.IGNORECASE)
def verify(message, code):
    global as2s
    as2s.continue_google_oauth(code.strip())
    message.reply('We are ready to pulling nubmers for you. Sit tight ... ')
    say = as2s.query_performance()
    message.reply(say.getvalue())


class AdxSeller2Slack():
    def __init__(self):
        self.http = None

    def cache_ad_client_id_and_end_date(self, ad_client_id, end_date):
        self.ad_client_id = ad_client_id
        self.end_date_str = end_date

    def do_google_oauth(self):
        oauth_scope = 'https://www.googleapis.com/auth/adexchange.seller.readonly'
        self.flow = flow_from_clientsecrets('adxseller_client_secrets.json',
                                            scope=oauth_scope,
                                        redirect_uri='urn:ietf:wg:oauth:2.0:oob')

        self.storage = multistore_file.get_credential_storage(filename='credentials.file',
                                                              client_id=self.ad_client_id,
                                                              user_agent='',
                                                              scope=oauth_scope)
        credentials = self.storage.get()
        
        if credentials is None or credentials.invalid:
            authorize_url = self.flow.step1_get_authorize_url(redirect_uri='urn:ietf:wg:oauth:2.0:oob')
            return {'pending': authorize_url}
            # print authorize_url
            # code = raw_input('Enter verification code: ').strip()
        else:
            self.http = credentials.authorize(httplib2.Http())
            return {'success': None}

    def continue_google_oauth(self, verification_code):
        credentials = self.flow.step2_exchange(verification_code)
        self.storage.put(credentials)
        http = credentials.authorize(httplib2.Http())
        self.http = credentials.authorize(httplib2.Http())

    def query_performance(self):
        start_date = datetime.datetime.strptime(self.end_date_str, '%Y-%m-%d').date() - timedelta(7)
        adxseller_service = build('adexchangeseller', 'v2.0', http=self.http)
        result = adxseller_service.accounts().reports().generate(
            accountId=self.ad_client_id.replace('ca-pub-', 'pub-', 1),
            startDate=start_date.strftime('%Y-%m-%d'),
            endDate=self.end_date_str,
            filter=['AD_CLIENT_ID==' + self.ad_client_id],
            metric=['PAGE_VIEWS', 'AD_REQUESTS', 'AD_REQUESTS_COVERAGE',
                    'COST_PER_CLICK', 'AD_REQUESTS_RPM', 'EARNINGS'],
            dimension=['DATE'],
            sort=['+DATE']).execute()

        replyMsg = StringIO.StringIO()
        # Print headers.
        for header in result['headers']:
            print >> replyMsg, '*%20s*' % header['name'],
        print >> replyMsg

        # Print results.
        for row in result['rows']:
            for column in row:
                print >> replyMsg, '%20s' % column,
            print >> replyMsg
        return replyMsg


def main():
    bot = Bot()
    bot.run()


as2s = AdxSeller2Slack()

if __name__ == "__main__":
    main()
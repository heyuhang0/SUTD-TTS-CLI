''' SUTD Temperature Taking System Command Line Interface '''
from typing import Any, Dict
import requests
import logging
import re
import argparse


class AspxSession():
    def __init__(self) -> None:
        self.session = requests.Session()
        self.view_state = None
        self.view_state_generator = None
        self.event_validation = None

    def _update_state(self, r: requests.Response) -> None:
        if r.status_code != 200:
            return
        self.view_state = re.findall(r'id="__VIEWSTATE" value="(.*?)"', r.text)
        self.view_state_generator = re.findall(r'id="__VIEWSTATEGENERATOR" value="(.*?)"', r.text)
        self.event_validation = re.findall(r'id="__EVENTVALIDATION" value="(.*?)"', r.text)

    def get(self, url: str) -> requests.Response:
        response = self.session.get(url)
        self._update_state(response)
        return response

    def post(self, url: str, data: Dict[str, Any]) -> requests.Response:
        data.update({
            '__VIEWSTATE': self.view_state,
            '__VIEWSTATEGENERATOR': self.view_state_generator,
            '__EVENTVALIDATION': self.event_validation,
        })
        response = self.session.post(url, data=data)
        self._update_state(response)
        return response


def main():
    logging.basicConfig(
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        level=logging.DEBUG
    )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', '--temperature', action='store_true',
                        help='submit temperature taking result')
    parser.add_argument('-d', '--daily-declaration', action='store_true',
                        help='submit daily declaration')
    parser.add_argument('username', type=str, help='SUTD Student ID')
    parser.add_argument('password', type=str, help='SUTD Password')
    args = parser.parse_args()

    s = AspxSession()

    s.get('https://tts.sutd.edu.sg/tt_home_user.aspx')
    resp = s.post('https://tts.sutd.edu.sg/tt_login.aspx', data={
        'ctl00$pgContent1$uiLoginid': args.username,
        'ctl00$pgContent1$uiPassword': args.password,
        'ctl00$pgContent1$btnLogin': 'Sign-In'
    })
    if 'Logout' not in resp.text:
        logging.error(f'Login failed, body: {resp.text}')
        return
    logging.info('Login successfully')

    if args.temperature:
        s.get('https://tts.sutd.edu.sg/tt_temperature_taking_user.aspx')
        resp = s.post('https://tts.sutd.edu.sg/tt_temperature_taking_user.aspx', data={
            'ctl00$uiMenu': 'Choose an Action',
            'ctl00$pgContent1$uiTemperature': 'Less than or equal to 37.6°C',
            'ctl00$pgContent1$uiRemarks': '',
            'ctl00$pgContent1$btnSave': 'Submit',
            'ctl00$pgContent1$uiCountries': '',
        })
        if 'successful' not in resp.text:
            logging.error(f'Failed to submit temperature, body: {resp.text}')
        else:
            logging.info('Temperature submitted successfully')

    if args.daily_declaration:
        s.get('https://tts.sutd.edu.sg/tt_daily_dec_user.aspx')
        resp = s.post('https://tts.sutd.edu.sg/tt_daily_dec_user.aspx', data={
            'ctl00$uiMenu': 'Choose an Action',
            'ctl00$pgContent1$OtherCountryVisited': 'rbVisitOtherCountryNo',
            'ctl00$pgContent1$Notice': 'rbNoticeNo',
            'ctl00$pgContent1$Contact': 'rbContactNo',
            'ctl00$pgContent1$MC': 'rbMCNo',
            'ctl00$pgContent1$btnSave': 'Submit'
        })
        if 'successful' not in resp.text:
            logging.error(f'Failed to submit daily declaration, body: {resp.text}')
        else:
            logging.info('Daily declaration submitted successfully')


if __name__ == "__main__":
    main()

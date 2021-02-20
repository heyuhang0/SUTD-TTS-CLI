''' SUTD Temperature Taking System Command Line Interface '''
from typing import Any, Dict
import logging
import re
import time
import argparse
import requests
import muggle_ocr


OCR_MODEL = muggle_ocr.SDK(conf_path="./captcha_model/TTS_Captcha-CNNX-GRU-H64-CTC-C1_model.yaml")


class AspxSession():
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session_states = {
            '__VIEWSTATE': None,
            '__VIEWSTATEGENERATOR': None,
            '__EVENTTARGET': None,
            '__EVENTARGUMENT': None,
            '__EVENTVALIDATION': None,
            '__LASTFOCUS': None,
        }
        self.headers = {
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/85.0.4183.121 Safari/537.36"
        }

    def _update_state(self, r: requests.Response) -> None:
        if r.status_code != 200:
            return
        for key in self.session_states:
            matches = re.findall(rf'id="{key}" value="(.*?)"', r.text)
            self.session_states[key] = matches[0] if matches else None

    def get(self, url: str, update_state=True) -> requests.Response:
        response = self.session.get(url)
        if update_state:
            self._update_state(response)
        return response

    def post(self, url: str, data: Dict[str, Any]) -> requests.Response:
        data.update({k: v for k, v in self.session_states.items() if v is not None})
        response = self.session.post(url, data=data, headers=self.headers)
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

    for _ in range(5):
        s.get('https://tts.sutd.edu.sg')

        captcha_img = s.get('https://tts.sutd.edu.sg/CImage.aspx', update_state=False)
        captcha = OCR_MODEL.predict(captcha_img.content)
        logging.info('CAPTCHA recognized: {}'.format(captcha))

        resp = s.post('https://tts.sutd.edu.sg/tt_login.aspx', data={
            'ctl00$pgContent1$uiLoginid': args.username,
            'ctl00$pgContent1$uiPassword': args.password,
            'ctl00$pgContent1$txtVerificationCode': captcha,
            'ctl00$pgContent1$btnLogin': 'Sign-In'
        })
        if 'Logout' in resp.text:
            break
        logging.error('Login failed, retry in 5 seconds')
        time.sleep(5)
    else:
        logging.error('Login failed, body: {}'.format(resp.text))
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
            logging.error('Failed to submit temperature, body: {}'.format(resp.text))
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
            logging.error('Failed to submit daily declaration, body: {}'.format(resp.text))
        else:
            logging.info('Daily declaration submitted successfully')

    logging.info('Submitted :)')


if __name__ == "__main__":
    main()

import os
import pickle
import requests
from typing import Optional, List

from bs4 import BeautifulSoup
from loguru import logger

from sen_api import IntervalReading, Config, Bill, AuthenticationError


__all__ = [
    'SENProvider'
]


class SENProvider(object):
    _base_url = 'https://www.servizioelettriconazionale.it/it-IT'
    _meter_url = f'{_base_url}/clienti/SEN/servizi/Areaclienti/Contatore/a.ser?tab=3'
    _client_area_url = f'{_base_url}/clienti/SEN/servizi/Areaclienti/HomePage/homepage.jsp'
    _bills_url = f'{_base_url}/clienti/SEN/servizi/Areaclienti/SelezionaBolletteServlet/a.ser'
    _bill_download_url = f'{_base_url}/clienti/SEN/servizi/Areaclienti/DettaglioBolletta/vediPDF.ser?from=bollettaPDF'
    _meter_readings_url = f'{_base_url}/clienti/SEN/servizi/Areaclienti/LeggiConsumi/a.ser?funz=A09&destMenu=areaclienti_left.jsp&from=modifica'

    def __init__(self, config: Config):
        self._session = requests.Session()
        self._session_path = os.path.join(config.base_path, 'session.pickle')
        self._config = config
        self._client_id = None
        self._client_name = None

    @staticmethod
    def _get_soup(data) -> BeautifulSoup:
        return BeautifulSoup(data, 'html.parser')

    def _send_form(self, form=None, soup_data: Optional[str] = None, form_data: Optional[dict] = None):
        if not form:
            soup = self._get_soup(soup_data)
            if not form_data:
                form_data = dict()
            form = soup.find('form')

        action_url = form.get('action')
        for field in form.find_all('input'):
            name = field.get('name')
            value = field.get('value', None)
            if name not in form_data.keys():
                form_data[name] = value

        response = self._session.post(action_url, data=form_data, allow_redirects=True)
        return response

    def _real_auth(self, username, password):
        self._session = requests.Session()

        logger.debug('Getting base url...')
        response = self._session.get(self._base_url)

        # first login form
        login_data = {
            'txtUsername': username,
            'txtPassword': password
        }
        login_response = self._send_form(soup_data=response.text, form_data=login_data)
        logger.debug('Got login response')

        # saml request
        response = self._send_form(soup_data=login_response.text)
        logger.debug('Done saml request')

        # saml response
        response = self._send_form(soup_data=response.text)
        logger.debug('Got saml response')

        soup = self._get_soup(response.text)
        self._client_name = soup.find('h3', id='nomeCliente').text.strip()
        self._client_id = soup.find('a', id='tabsForniture_selezionata').find('b').text
        logger.debug(f'Client name is: {self._client_name}')
        logger.debug(f'Client ID is: {self._client_id}')
        self._config.write(section='client', values={'name': self._client_name, 'id': self._client_id})

    @property
    def is_authenticated(self) -> bool:
        """
        Check if it is still authenticated
        """
        if not self.load_session():
            return False
        if not self._session.cookies:
            return False
        logger.debug('Checking if session is still valid...')
        response = self._session.get(self._client_area_url)
        return response.url == self._client_area_url

    @property
    def client_info(self) -> dict:
        return {
            'id': self._client_id if self._client_id else self._config.get_value('client', 'id'),
            'name': self._client_name if self._client_name else self._config.get_value('client', 'name')
        }

    def save_session(self):
        logger.debug('Saving session...')
        with open(self._session_path, 'wb') as f:
            pickle.dump(self._session, f)

    def load_session(self) -> bool:
        """
        :return: True if loaded, False otherwise
        """
        logger.debug('Loading session...')
        if os.path.isfile(self._session_path):
            with open(self._session_path, 'rb') as f:
                self._session = pickle.load(f)
                return True
        return False

    def authenticate(self, username: Optional[str] = None, password: Optional[str] = None, force=False):
        if not username:
            username = self._config.get_value('auth', 'username')
        if not password:
            password = self._config.get_value('auth', 'password')

        if username is None or password is None:
            raise ValueError('Credentials cannot be None.')

        if not force:
            self.load_session()
        if force or not self.is_authenticated:
            try:
                self._real_auth(username, password)
                self.save_session()
            except AttributeError:
                message = 'Authentication error or wrong credentials.'
                logger.error(message)
                raise AuthenticationError(message)
        logger.debug('Successfuly authenticated.')

    def get_last_reading(self) -> dict:
        response = self._session.get(self._meter_url)
        soup = self._get_soup(response.text)
        table = soup.find('table', attrs={'class': 'pe_tabsData tabella_contatore'})
        cells = table.find_all('td')
        reading_date = cells[7].text
        readings = cells[5].text.split()
        return {
            'reading_date': reading_date,
            'readings': {
                'A1': readings[1],
                'A2': readings[3],
                'A3': readings[5]
            }
        }

    def get_all_readings(self) -> List[IntervalReading]:
        response = self._session.get(self._meter_readings_url)
        soup = self._get_soup(response.text)
        table = soup.find('table', id='tabella_consumi')
        readings = []
        for row in table.find_all('tr', attrs={'class': 'border border-right'}):
            cells = row.find_all('td')
            r = IntervalReading(
                interval_start=cells[0].text,
                interval_end=cells[1].text,
                total_consumption=int(cells[3].text)
            )
            readings.append(r)
        return readings

    def get_bills_available_years(self) -> List[str]:
        response = self._session.post(self._bills_url)
        soup = self._get_soup(response.text)
        years = soup.find('div', id='sceltaanni').find_all('a')
        return [y.text for y in years]

    def get_bills(self, year: str) -> List[Bill]:
        if year not in self.get_bills_available_years():
            error = f'Year {year} is not available'
            logger.debug(error)
            raise ValueError(error)
        data = {'annoScelto': year}
        response = self._session.post(self._bills_url, data=data)
        soup = self._get_soup(response.text)
        table = soup.find('table', id='tab_bollette')
        bills = []
        for row in table.find_all('tr', attrs={'class': year}):
            # store hidden inputs in params dict, used later to download the bill
            params_input = row.find_all('input')
            params = dict()
            for p in params_input:
                key = p.get('name')
                value = p.get('value')
                params[key] = value

            # get '1' from 'codFatt_1', '2' from 'codFatt_2'...
            params['occorrenzaForm'] = list(params.keys())[0].split('_')[1]

            cells = row.find_all('td')
            bill = Bill(
                number=int(cells[0].text),
                due_date=cells[1].text,
                amount=float(cells[2].text.replace(',', '.')),
                is_payed=(cells[5].text.strip() == 'Incassata totalmente'),
                params=params
            )
            bills.append(bill)

        return bills

    def download_bill(self, bill: Bill, download_path: Optional[str] = None) -> Optional[str]:
        data = {
            'tipoRichiesta': '2',
        }
        data.update(bill.params)
        response = self._session.post(self._bill_download_url, data=data)
        if response.headers['content-type'] == 'application/pdf':
            path = os.path.join(self._config.base_path, 'bills')
            if download_path:
                path = download_path
            if not os.path.isdir(path):
                os.mkdir(path)
            path = os.path.join(path, bill.document_name)
            with open(path, 'wb') as f:
                f.write(response.content)
            return path
        return None

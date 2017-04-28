from bs4 import BeautifulSoup
import requests
import re

def parse_response(response):
    return BeautifulSoup(response.text, 'html.parser')

class AuthException(Exception):
    pass

class MITAuth(object):
    IDP_AUTH_URL = 'https://idp.mit.edu:443/idp/Authn/MIT'
    IDP_AUTH_CERTIFICATE_URL = 'https://idp.mit.edu:446/idp/Authn/Certificate'
    IDP_AUTH_REDIRECT_URL = 'https://idp.mit.edu:446/idp/profile/SAML2/Redirect/SSO'

    def __init__(self, session):
        self._session = session

    def _authenticate(self):
        auth_request = self._session.get(self.IDP_AUTH_CERTIFICATE_URL, cert='/Users/pat/Desktop/pat.pem')
        if auth_request.url.startswith(self.IDP_AUTH_REDIRECT_URL) and auth_request.status_code == 200:
            auth_soup = parse_response(auth_request)
            redirect_form = auth_soup.body.find('form')
            redirect_form_action = redirect_form['action']
            redirect_form_payload = {}
            for field in redirect_form.find_all('input'):
                if field.get('name') != None:
                    redirect_form_payload[field.get('name')] = field.get('value')
            auth_redirect_request = self._session.post(redirect_form_action, data=redirect_form_payload)
            return auth_redirect_request
        else:
            raise AuthException

    # TODO Clean this up
    def _on_request(self, request):
        r = request
        if request.url.startswith(self.IDP_AUTH_URL):
            try:
                r = self._authenticate()
            except AuthException:
                pass
        return r

class AlreadyAuthed(object):
    def _on_request(self, request):
        if request.url.startswith(MITAuth.IDP_AUTH_URL):
            raise AuthException
        return request

class PEBot(object):
    APP_ENDPOINT = 'https://edu-apps.mit.edu/mitpe/student/registration'
    REG_INFO_PATTERN = re.compile(r'Registered:(?:\D+)(?P<registered>\d+)((?:\D+)Waitlist:(?:\D+)(?P<waitlisted>\d+)(\D+))?')
    SEC_LINK_PATTERN = re.compile(r'sectionId\=(?P<section_id>[0-9A-Z]{32})')
    REG_DATE_PATTERN = re.compile(r'Registration Period: (\d{2}\/\d{2}\/\d{4}) - (\d{2}\/\d{2}\/\d{4})')

    def __init__(self, cookies):
        self._session = requests.Session()
        #self._auth = MITAuth(self._session)
        self._auth = AlreadyAuthed()
        for k, v in cookies.items():
            self._session.cookies.set(k, v)

    def get_section_list(self):
        sl = parse_response(self._get('sectionList'))
        start_reg_date = self.REG_DATE_PATTERN.search(sl.find('div', id='nav2').find('h2').text).group(1)
        sl_t = sl.find('table', id="section").find("tbody")
        sections = []
        for row in sl_t.find_all('tr'):
            cols = row.find_all('td')
            link = cols[0].find('a')['href']
            section_id = self.SEC_LINK_PATTERN.search(link).group('section_id')
            activity = cols[1].text.strip()
            title = cols[2].find('p').text.strip()
            days = cols[3].text.strip()
            times = cols[4].text.strip()
            sections.append({'section_id': section_id, 'activity': activity, 'title': title, 'days': days, 'time': times})
        return (sections, start_reg_date)

    def register_for_section(self, section_id, mit_id):
        payload = {
            'sectionId': section_id,
            'mitId': mit_id,
            'wf': '/registration/quick'
        }
        registration_request = self._post('create', data=payload)
        confirmation_soup = parse_response(registration_request)
        success_msg = confirmation_soup.find(class_="portlet-msg-success").text.lower()

        registration_status = 'UNKNOWN'

        if 'successfully registered' in success_msg:
            registration_status = 'REGISTERED'
        elif 'successfully been placed on the waitlist' in success_msg:
            registration_status = 'WAITLISTED'

        capacity = int(confirmation_soup
                        .find('th', text=re.compile(r'(.*)Capacity(.*)'))
                        .findNext('td').text.strip())

        reg_info_parsed = self.REG_INFO_PATTERN.search(soup.find('th', text=re.compile(r'(.*)Registration(.*)')).findNext('td').text)

        return {
            'status': registration_status,
            'capacity': capacity,
            'registered': reg_info_parsed.group('registered'),
            'waitlisted': reg_info_parsed.group('waitlisted') or 0
        }

    def _get(self, endpoint, *args, **kwargs):
        r = self._session.get('%s/%s' % (self.APP_ENDPOINT, endpoint), *args, **kwargs)
        return self._auth._on_request(r)

    def _post(self, endpoint, *args, **kwargs):
        r = self._session.post('%s/%s' % (self.APP_ENDPOINT, endpoint), *args, **kwargs)
        return self._auth._on_request(r)

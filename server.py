import json
import http.server
import requests
import socketserver
from http import HTTPStatus
from urllib.parse import parse_qs

VALID_CREDS = {
    "user1@unacademy.com": "passworduser1",
    "user2@unacademy.com": "passworduser2",
}

SITE_KEY = "10000000-ffff-ffff-ffff-000000000001"
SECRET_KEY = "0x0000000000000000000000000000000000000000"


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/signin":
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()
            return

        fields = dict()
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            fields = parse_qs(body)
        except Exception as err:
            print("Got exception: ", err)
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.end_headers()
            return

        if not self._captcha_valid(fields):
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.end_headers()
            return

        if not self._creds_valid(fields):
            self.send_response(HTTPStatus.UNAUTHORIZED)
            self.end_headers()
            return

        self.send_response(HTTPStatus.OK)
        self.end_headers()

    def _captcha_valid(self, fields):
        token = fields.get(b'h-captcha-response', [None])[0]
        if not token:
            return False
        token = token.decode("utf-8")

        success = False
        try:
            resp = requests.post(url='https://hcaptcha.com/siteverify',
                                 data={'sitekey': SITE_KEY, 'secret': SECRET_KEY, 'response': token})
            success = resp.json()['success']
        except Exception as err:
            print("Got exception: ", err)
            return False

        return success

    def _creds_valid(self, fields):
        email = fields.get(b'email', [None])[0]
        password = fields.get(b'password', [None])[0]
        if (not email) or (not password):
            return False

        email = email.decode("utf-8")
        password = password.decode("utf-8")

        stored_password = VALID_CREDS.get(email, None)
        if not stored_password:
            return False

        return password == stored_password


httpd = socketserver.TCPServer(('', 8080), Handler)
httpd.serve_forever()

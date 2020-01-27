import tornado.ioloop
import tornado.web
from oauth2lib.client import Client
from oauth2lib.provider import AuthorizationProvider
import logging

CLIENT_ID = 'abc'
CLIENT_SECRET = 'xyz'
SERVER_URI = 'https://localhost:8888/app'
REDIRECT_URI = 'https://localhost:8888/callback'
AUTHORIZATION_CODE = 'authcode'
REFRESH_TOKEN = 'refreshcode'

class MockAuthorizationProvider(AuthorizationProvider):
    """Implement an authorization oauth2lib provider for testing purposes."""

    def validate_client_id(self, client_id):
        return client_id == CLIENT_ID

    def validate_client_secret(self, client_id, client_secret):
        return client_id == CLIENT_ID and client_secret == CLIENT_SECRET

    def validate_scope(self, client_id, scope):
        requested_scopes = scope.split()
        if client_id == CLIENT_ID and requested_scopes == ['example']:
            return True
        return False

    def validate_redirect_uri(self, client_id, redirect_uri):
        return redirect_uri.startswith(REDIRECT_URI)

    def from_authorization_code(self, client_id, code, scope):
        if code == AUTHORIZATION_CODE:
            return {'session': '12345'}
        return None

    def from_refresh_token(self, client_id, refresh_token, scope):
        if refresh_token == REFRESH_TOKEN:
            return {'session': '56789'}
        return None

    def validate_access(self):
        return True



class MainHandler(tornado.web.RequestHandler):
    client = Client(client_id=CLIENT_ID,
                    client_secret=CLIENT_SECRET,
                    authorization_uri=SERVER_URI + '/authorize',
                    token_uri=SERVER_URI + '/token',
                    redirect_uri=REDIRECT_URI + '?param=123')
    provider = MockAuthorizationProvider()                
    uri =  client.get_authorization_code_uri()
    data = provider.get_authorization_code_from_uri(uri)
    logger = logging.getLogger(data)
    
    print(data.headers)
    def get(self):
        self.write("""<html>
    <body>
        <p>
            <a href="https://localhost:8888/callback?confirm=1">confirm</a>
        </p>
        <p>
            <a href="https://localhost:8888/callback?confirm=0">deny</a>
        </p>
    </body>
</html>""")

class CallbackHandler(tornado.web.RequestHandler):
    def get(self):
        print(self.get_query_argument("confirm"))
        if self.get_query_argument("confirm") == "1" :
            self.write("""<html>
                            <body>
                                <p>
                                    AAYA</p>
                            </body>
                        </html>""")
        else : 
            self.write("""<html>
                        <body>
                            <p>
                                GAYA</p>
                        </body>
                    </html>""")


if __name__ == "__main__":
    
    application = tornado.web.Application([
        (r"/app", MainHandler),
        (r"/callback.*", CallbackHandler)
    ])
    http_server = tornado.httpserver.HTTPServer(application, ssl_options={
        "certfile": "/home/sakku/Desktop/localhost.crt",
        "keyfile": "/home/sakku/Desktop/localhost.key",
    })
    print("https://localhost:8888/app")
    http_server.listen(8888)
    tornado.ioloop.IOLoop.current().start()
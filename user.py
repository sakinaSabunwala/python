import tornado.ioloop
import tornado.web
import client
import provider
import json

import logging
logging.basicConfig()

CLIENT_ID = 'abc'
CLIENT_SECRET = 'xyz'
SERVER_URI = 'https://localhost:8888'
REDIRECT_URI = 'https://localhost:8888/oauth2redirect'

class MockAuthorizationProvider(provider.AuthorizationProvider):
    """Implement an authorization oauth2lib provider for testing purposes."""

    def validate_client_id(self, client_id):
        return client_id == CLIENT_ID

    def validate_client_secret(self, client_id, client_secret):
        return client_id == CLIENT_ID and client_secret == CLIENT_SECRET

    def validate_scope(self, client_id, scope):
        requested_scopes = scope.split()
        if client_id == CLIENT_ID :
            return True
        return False

    def validate_redirect_uri(self, client_id, redirect_uri):
        return True

    def from_authorization_code(self, client_id, code, scope):
            return {'session': '12345'}
       

    def from_refresh_token(self, client_id, refresh_token, scope):
        return {'session': '56789'}
       

    def validate_access(self):
        return True

    def persist_authorization_code(self, client_id, code, scope):
        pass

    def persist_token_information(self, client_id, scope, access_token,
                                  token_type, expires_in, refresh_token,
                                  data):
        pass

    def discard_authorization_code(self, client_id, code):
        pass

    def discard_refresh_token(self, client_id, refresh_token):
        pass



class MainHandler(tornado.web.RequestHandler):
    client = client.Client(client_id=CLIENT_ID,
                    client_secret=CLIENT_SECRET,
                    authorization_uri=SERVER_URI + '/auth',
                    token_uri=SERVER_URI + '/token',
                    redirect_uri=REDIRECT_URI)
    provider = MockAuthorizationProvider() 

    uri =  client.get_authorization_code_uri()
    data = provider.get_authorization_code_from_uri(uri)
    d = data.headers['Location'].split('code=')
    print(d[1])
    ser = provider.get_token('authorization_code',
                  CLIENT_ID,
                  CLIENT_SECRET,
                  data.headers['Location'],
                  d)
    print(ser)
    
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
        (r"/callback.*", CallbackHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application, ssl_options={
        "certfile": "/home/sakku/Desktop/localhost.crt",
        "keyfile": "/home/sakku/Desktop/localhost.key",
    })
    print("https://localhost:8888/app")
    http_server.listen(8888)
    tornado.ioloop.IOLoop.current().start()
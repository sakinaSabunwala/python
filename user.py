import tornado.ioloop
import tornado.web
import client
import provider
import json
import requests
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
        if client_id == CLIENT_ID:
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


myClient = client.Client(client_id=CLIENT_ID,
                         client_secret=CLIENT_SECRET,
                         authorization_uri=SERVER_URI + '/auth',
                         token_uri=SERVER_URI + '/token',
                         redirect_uri=REDIRECT_URI)
provider = MockAuthorizationProvider()


class MainHandler(tornado.web.RequestHandler):
    def get(self):

        uri = myClient.get_authorization_code_uri()
        data = provider.get_authorization_code_from_uri(uri)

        if self.request.uri.startswith("/get_authorization_code"):
            print(data.headers)
            if self.get_query_argument("client_id") == CLIENT_ID:
                self.redirect(data.headers['Location'])
            else:
                self.write("acess denied")
        else:
            d = data.headers['Location'].split('code=')
            print(d)
            ser = provider.get_token('authorization_code',
                                     CLIENT_ID,
                                     CLIENT_SECRET,
                                     SERVER_URI + self.request.uri,
                                     d)

            print(ser.headers['data'])
            self.write(ser.headers['data'])


class CallbackHandler(tornado.web.RequestHandler):
    def get(self):
        print(self.get_query_argument("confirm"))
        if self.get_query_argument("confirm") == "1":
            self.write("""<html>
                            <body>
                                <p>
                                    AAYA</p>
                            </body>
                        </html>""")
        else:
            self.write("""<html>
                        <body>
                            <p>
                                GAYA</p>
                        </body>
                    </html>""")


class ClientHandler(tornado.web.RequestHandler):
    def get(self):

        if self.request.uri.startswith("/app"):
            print("....")
            self.write("""<html>
                            <body>
                               <a href="https://localhost:8888/get_authorization_code?client_id=abc">get code</a>
                            </body>
                        </html>""")
        else:
            self.write("Not found")


if __name__ == "__main__":

    # Auth server
    server_application = tornado.web.Application([
        (r"/get_authorization_code.*", MainHandler),
        (r"/callback.*", CallbackHandler),
        (r"/oauth2redirect.*", MainHandler),
    ])
    http_auth_server = tornado.httpserver.HTTPServer(server_application, ssl_options={
        "certfile": "/Users/imac/Desktop/localhost.crt",
        "keyfile": "/Users/imac/Desktop/localhost.key",
    })
    print("https://localhost:8888/")
    http_auth_server.listen(8888)

    #Client :Browser
    client_application = tornado.web.Application([
        (r"/app", ClientHandler),

    ])
    http_client_server = tornado.httpserver.HTTPServer(client_application, ssl_options={
        "certfile": "/Users/imac/Desktop/localhost.crt",
        "keyfile": "/Users/imac/Desktop/localhost.key",
    })
    print("https://localhost:9999/app")

    http_client_server.listen(9999)
    tornado.ioloop.IOLoop.current().start()

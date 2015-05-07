"""
Tests for messaging_contentstore.contentstore.
"""

from unittest import TestCase

from requests import HTTPError
from requests.adapters import HTTPAdapter
from requests_testadapter import TestSession, Resp, TestAdapter

from fake_contentstore import Request, FakeContentStoreApi

from messaging_contentstore.contentstore import ContentStoreApiClient


class FakeContentStoreApiAdapter(HTTPAdapter):

    """
    Adapter for FakeContentStoreApi

    This inherits directly from HTTPAdapter instead of using TestAdapter
    because it overrides everything TestAdaptor does.
    """

    def __init__(self, contentstore_api):
        self.contentstore_api = contentstore_api
        super(FakeContentStoreApiAdapter, self).__init__()

    def send(self, request, stream=False, timeout=None,
             verify=True, cert=None, proxies=None):
        # print request.path_url
        req = Request(
            request.method, request.path_url, request.body, request.headers)
        resp = self.contentstore_api.handle_request(req)
        response = Resp(resp.body, resp.code, resp.headers)
        r = self.build_response(request, response)
        # print r.status_code
        return r


make_messageset_dict = FakeContentStoreApi.make_messageset_dict


class TestContentStoreApiClient(TestCase):
    API_URL = "http://example.com/"
    AUTH_TOKEN = "auth_token"

    def setUp(self):
        self.messageset_data = {}
        self.messageset_backend = FakeContentStoreApi(
            "/", self.AUTH_TOKEN, self.messageset_data)
        self.session = TestSession()
        adapter = FakeContentStoreApiAdapter(self.messageset_backend)
        self.session.mount(self.API_URL, adapter)

    def make_client(self, auth_token=AUTH_TOKEN):
        return ContentStoreApiClient(
            auth_token, api_url=self.API_URL, session=self.session)

    def make_existing_messageset(self, messageset_data):
        existing_messageset = make_messageset_dict(messageset_data)
        self.messageset_data[existing_messageset[u"id"]] = existing_messageset
        return existing_messageset

    # def assert_messageset_status(self, messageset_id, exists=True):
    #     exists_status = (messageset_id in self.messageset_data)
    #     self.assertEqual(exists_status, exists)

    # def assert_http_error(self, expected_status, func, *args, **kw):
    #     print "Asserting"
    #     try:
    #         func(*args, **kw)
    #     except HTTPError as err:
    #         print err.response.status_code
    #         self.assertEqual(err.response.status_code, expected_status)
    #     else:
    #         self.fail(
    #             "Expected HTTPError with status %s." % (expected_status,))

    # def test_assert_http_error(self):
    #     self.session.mount("http://bad.example.com/", TestAdapter("", 500))

    #     def bad_req():
    #         r = self.session.get("http://bad.example.com/")
    #         r.raise_for_status()

    #     # Fails when no exception is raised.
    #     self.assertRaises(
    #         self.failureException, self.assert_http_error, 404, lambda: None)

    #     # Fails when an HTTPError with the wrong status code is raised.
    #     self.assertRaises(
    #         self.failureException, self.assert_http_error, 404, bad_req)

    #     # Passes when an HTTPError with the expected status code is raised.
    #     self.assert_http_error(500, bad_req)

    #     # Non-HTTPError exceptions aren't caught.
    #     def raise_error():
    #         raise ValueError()

    #     self.assertRaises(ValueError, self.assert_http_error, 404, raise_error)

    # def test_default_session(self):
    #     import requests
    #     contentstore = ContentStoreApiClient(self.AUTH_TOKEN)
    #     self.assertTrue(isinstance(contentstore.session, requests.Session))

    # def test_default_api_url(self):
    #     contentstore = ContentStoreApiClient(self.AUTH_TOKEN)
    #     self.assertEqual(
    #         contentstore.api_url, "http://testserver/contentstore")

    # def test_auth_failure(self):
    #     contentstore = self.make_client(auth_token="bogus_token")
    #     res = contentstore.get_messagesets()
    #     self.assertEqual(True, False)
        #
        # print type(res.status_code)
        # self.assert_http_error(403, contentstore.get_messagesets)

    def test_auth_failure(self):
        contentstore = self.make_client(auth_token="bogus_token")
        res = contentstore.get_messageset(1)
        print res
        self.assertEqual(True, False)

    # def test_get_messageset(self):
    #     expected_messageset = self.make_existing_messageset({
    #         u"short_name": u"Full Set",
    #         u"notes": u"A full set of messages.",
    #         u"default_schedule": 1
    #     })
    #     contentstore = self.make_client()
    #     # print contentstore
    #     res = contentstore.get_messagesets()
    #     # print type(res)
    #     [messageset] = list(contentstore.get_messagesets())
    #     self.assertEqual(messageset, expected_messageset)

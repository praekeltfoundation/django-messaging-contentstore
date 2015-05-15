import json
import pkg_resources
from rest_framework import status
from pprint import pprint

class ContentStoreApiTestMixin(object):

    # def test_login(self):
    #     request = self.client.post(
    #         '/api-token-auth/',
    #         {"username": "testuser", "password": "testpass"})
    #     token = request.data.get('token', None)
    #     self.assertIsNotNone(
    #         token, "Could not receive authentication token on login post.")
    #     self.assertEqual(request.status_code, 200,
    #                      "Status code on /auth/login was %s (should be 200)."
    #                      % request.status_code)

    def test_create_schedule(self):
        post_data = {
            "minute": "1",
            "hour": "2",
            "day_of_week": "3",
            "day_of_month": "4",
            "month_of_year": "5",
        }
        response = self.client.post('/schedule/',
                                    json.dumps(post_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = self.get_schedule()
        self.assertEqual(d["minute"], "1")
        self.assertEqual(d["hour"], "2")
        self.assertEqual(d["day_of_week"], "3")
        self.assertEqual(d["day_of_month"], "4")
        self.assertEqual(d["month_of_year"], "5")

    def tests_update_schedule(self):
        existing_schedule = self.make_schedule()
        existing_schedule_id = existing_schedule.id
        patch_data = {
            "minute": "1",
            "hour": "2",
            "day_of_week": "3",
            "day_of_month": "4",
            "month_of_year": "5",
        }
        response = self.client.put('/schedule/%s/' % existing_schedule_id,
                                   json.dumps(patch_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        d = self.get_schedule(existing_schedule_id)
        self.assertEqual(d["minute"], "1")
        self.assertEqual(d["hour"], "2")
        self.assertEqual(d["day_of_week"], "3")
        self.assertEqual(d["day_of_month"], "4")
        self.assertEqual(d["month_of_year"], "5")

    def tests_delete_schedule(self):
        existing_schedule = self.make_schedule()
        existing_schedule_id = existing_schedule.id
        response = self.client.delete('/schedule/%s/' % existing_schedule_id,
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        check = self.get_schedules()
        self.assertEqual(len(check), 0)

    def test_create_messageset(self):
        default_schedule = self.make_schedule()
        schedule_id = default_schedule.id
        post_data = {
            "short_name": "Full Set",
            "notes": "A full set of messages.",
            "default_schedule": schedule_id
        }
        response = self.client.post('/messageset/',
                                    json.dumps(post_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = self.get_messageset()
        self.assertEqual(d["short_name"], "Full Set")
        self.assertEqual(d["notes"], "A full set of messages.")
        self.assertEqual(d["default_schedule"], schedule_id)
        self.assertEqual(d["next_set"], None)

    def test_create_messageset_missing_schedule(self):
        post_data = {
            "short_name": "Full Set",
            "notes": "A full set of messages."
        }
        response = self.client.post('/messageset/',
                                    json.dumps(post_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_messageset_duplicate_shortname(self):
        schedule = self.make_schedule()
        self.make_messageset(default_schedule=schedule.id,
                             short_name="Fuller Set")
        post_data = {
            "short_name": "Fuller Set",
            "notes": "Another fuller set of messages.",
            "default_schedule": schedule.id
        }
        response = self.client.post('/messageset/',
                                    json.dumps(post_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_messageset(self):
        schedule = self.make_schedule()
        default_messageset = self.make_messageset(default_schedule=schedule.id,
                                                  short_name="Full Set")
        default_messageset_id = default_messageset.id
        patch_data = {
            "notes": "A full set of messages with more notes."
        }
        response = self.client.patch('/messageset/%s/' % default_messageset_id,
                                     json.dumps(patch_data),
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        d = self.get_messageset(default_messageset_id)
        self.assertEqual(d["short_name"], "Full Set")
        self.assertEqual(d["notes"], "A full set of messages with more notes.")

    def tests_delete_messageset(self):
        schedule = self.make_schedule()
        default_messageset = self.make_messageset(default_schedule=schedule.id,
                                                  short_name="Full Set")
        default_messageset_id = default_messageset.id
        response = self.client.delete('/messageset/%s/' %
                                      (default_messageset_id, ),
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        check = self.get_messagesets()
        self.assertEqual(len(check), 0)

    def test_create_message_text(self):
        schedule = self.make_schedule()
        messageset = self.make_messageset(default_schedule=schedule.id,
                                          short_name="Full Set")
        post_data = {
            "messageset": messageset.id,
            "sequence_number": 2,
            "lang": "afr_ZA",
            "text_content": "Message two"
        }
        response = self.client.post('/message/',
                                    json.dumps(post_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = self.get_message()
        self.assertEqual(d["messageset"], messageset.id)
        self.assertEqual(d["sequence_number"], 2)
        self.assertEqual(d["lang"], "afr_ZA")
        self.assertEqual(d["text_content"], "Message two")

    def test_update_message_text(self):
        schedule = self.make_schedule()
        messageset = self.make_messageset(default_schedule=schedule.id,
                                          short_name="Full Set")
        message = self.make_message(messageset)
        message_id = message.id
        patch_data = {
            "text_content": "Message one updated"
        }
        response = self.client.patch('/message/%s/' % message_id,
                                     json.dumps(patch_data),
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        d = self.get_message(message_id)
        self.assertEqual(d["text_content"], "Message one updated")

    def tests_delete_message_text(self):
        schedule = self.make_schedule()
        messageset = self.make_messageset(default_schedule=schedule.id,
                                          short_name="Full Set")
        message = self.make_message(messageset)
        message_id = message.id
        response = self.client.delete('/message/%s/' % message_id,
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        check = self.get_messages()
        self.assertEqual(len(check), 0)

    # def test_create_binary_content(self):
    #     simple_png = pkg_resources.resource_stream('contentstore', 'test.png')

    #     post_data = {
    #         "content": simple_png
    #     }
    #     response = self.client.post('/binarycontent/',
    #                                 post_data,
    #                                 format='multipart',
    #                                 )
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     d = self.get_binary_content()
    #     self.assertEqual(d["content"].split('.')[-1], 'png')

    # def tests_delete_binary_content(self):
    #     binarycontent = self.make_binary_content()
    #     binarycontent_id = binarycontent.id
    #     response = self.client.delete('/binarycontent/%s/' % binarycontent_id,
    #                                   content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    #     check = self.get_binary_contents()
    #     self.assertEqual(len(check), 0)

    # def test_create_message_binary(self):
    #     schedule = self.make_schedule()
    #     messageset = self.make_messageset(default_schedule=schedule,
    #                                       short_name="Full Set")
    #     binarycontent = self.make_binary_content()
    #     binarycontent_id = binarycontent.id
    #     post_data = {
    #         "messageset": messageset.id,
    #         "sequence_number": 2,
    #         "lang": "afr_ZA",
    #         "binary_content": binarycontent_id
    #     }
    #     response = self.client.post('/message/',
    #                                 json.dumps(post_data),
    #                                 content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     d = self.get_message()
    #     self.assertEqual(d["messageset"], messageset.id)
    #     self.assertEqual(d["sequence_number"], 2)
    #     self.assertEqual(d["lang"], "afr_ZA")
    #     self.assertEqual(d["binary_content"], binarycontent_id)

    # def test_create_message_binary_and_text(self):
    #     schedule = self.make_schedule()
    #     messageset = self.make_messageset(default_schedule=schedule,
    #                                       short_name="Full Set")
    #     binarycontent = self.make_binary_content()
    #     binarycontent_id = binarycontent.id
    #     post_data = {
    #         "messageset": messageset.id,
    #         "sequence_number": 2,
    #         "lang": "afr_ZA",
    #         "text_content": "Message two",
    #         "binary_content": binarycontent_id
    #     }
    #     response = self.client.post('/message/',
    #                                 json.dumps(post_data),
    #                                 content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     d = self.get_message()
    #     self.assertEqual(d["messageset"], messageset.id)
    #     self.assertEqual(d["sequence_number"], 2)
    #     self.assertEqual(d["lang"], "afr_ZA")
    #     self.assertEqual(d["binary_content"], binarycontent_id)
    #     self.assertEqual(d["text_content"], "Message two")

    # def test_create_message_no_content_rejected(self):
    #     schedule = self.make_schedule()
    #     messageset = self.make_messageset(default_schedule=schedule,
    #                                       short_name="Full Set")
    #     post_data = {
    #         "messageset": messageset.id,
    #         "sequence_number": 2,
    #         "lang": "afr_ZA"
    #     }
    #     response = self.client.post('/message/',
    #                                 json.dumps(post_data),
    #                                 content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_get_message_content(self):
    #     schedule = self.make_schedule()
    #     messageset = self.make_messageset(default_schedule=schedule,
    #                                       short_name="Full Set")
    #     binarycontent = self.make_binary_content()
    #     message = self.make_message(messageset=messageset,
    #                                 text_content="Message two",
    #                                 binary_content=binarycontent)

    #     response = self.client.get('/message/%s/content' % message.id,
    #                                content_type='application/json')
    #     content = json.loads(response.content)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(content["binary_content"]["id"], binarycontent.id)
    #     self.assertEqual(content["text_content"], message.text_content)
    #     self.assertEqual(content["lang"], message.lang)
    #     self.assertEqual(content["messageset"], messageset.id)
    #     self.assertEqual(
    #         content["sequence_number"], message.sequence_number)
    #     self.assertEqual("created_at" in content, True)
    #     self.assertEqual("updated_at" in content, True)
    #     self.assertEqual("id" in content, True)

    # def test_get_messageset_messages_content(self):
    #     schedule = self.make_schedule()
    #     messageset = self.make_messageset(default_schedule=schedule,
    #                                       short_name="Three Message Set")
    #     binarycontent = self.make_binary_content()
    #     message2 = self.make_message(messageset=messageset,
    #                                  text_content="Message two",
    #                                  sequence_number=2,
    #                                  binary_content=binarycontent)
    #     message1 = self.make_message(messageset=messageset,
    #                                  sequence_number=1,
    #                                  text_content="Message one",
    #                                  binary_content=binarycontent)
    #     message3 = self.make_message(messageset=messageset,
    #                                  sequence_number=3,
    #                                  text_content="Message three",
    #                                  binary_content=binarycontent)

    #     response = self.client.get('/messageset/%s/messages' % messageset.id,
    #                                content_type='application/json')
    #     content = json.loads(response.content)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(content["short_name"], "Three Message Set")
    #     self.assertEqual(len(content["messages"]), 3)
    #     messages = content["messages"]  # They should be sorted by seq num now
    #     self.assertEqual(messages[0]["binary_content"]["id"], binarycontent.id)
    #     self.assertEqual(messages[0]["text_content"], "Message one")
    #     self.assertEqual(messages[0]["id"], message1.id)
    #     self.assertEqual(messages[1]["id"], message2.id)
    #     self.assertEqual(messages[2]["id"], message3.id)

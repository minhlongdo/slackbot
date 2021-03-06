from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from slackclient import SlackClient
from slackbot.settings import SETTING_MANAGE_BASE_URL

import logging
import requests


class ChatView(APIView):
    def post(self, request):
        data = request.data

        logging.info("Received data: ", data)

        instance_id = data['instance_id']
        user_email = data['user_email']
        msg = data['msg']

        logging.info("Instance ID={}".format(instance_id))
        logging.info("User email={}".format(user_email))
        logging.info("Message={}".format(msg))

        logging.info("Retrieving token and channel for slack...")
        params = {'instance_id': instance_id, 'user_email': user_email}
        logging.warn("parameters: ", params)
        r = requests.get(SETTING_MANAGE_BASE_URL + 'v1/tokenstorage/', params=params)
        logging.warn("Message from: ", r.text)
        logging.info("Received json=", r.json())
        slack_token = r.json()['slack_token']
        slack_channel = r.json()['slack_channel']

        logging.info("slack_token={}".format(slack_token))
        logging.info("slack_channel={}".format(slack_channel))

        if slack_token is None or slack_token == '':
            logging.warn('No slack token found in database, cant post to channel')
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Default to general if it is empty
        if slack_channel is None or slack_channel == '':
            logging.info('Going to set slack channel to #general')
            slack_channel = '#general'

        if msg is None or msg == '':
            logging.warn('Empty message, abort post')
            return Response(data='empty message', status=status.HTTP_406_NOT_ACCEPTABLE)

        logging.info('Posting to slack_channel={}'.format(slack_channel))

        try:
            sc = SlackClient(slack_token)

            rvc_response = sc.api_call(
                'chat.postMessage',
                channel=slack_channel,
                text=msg
            )

            if not rvc_response['ok']:
                return Response(data=rvc_response['error'], status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            return Response(data=e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

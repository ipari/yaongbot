import os
import threading
from flask import Flask
from slackclient import SlackClient

from bot import Bot
from view import viewer


app = Flask(__name__)
app.register_blueprint(viewer)

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
sc = SlackClient(SLACK_BOT_TOKEN)


if __name__ == '__main__':
    if sc.rtm_connect():
        bot = Bot(sc)
        thread = threading.Thread(target=bot.listen, args=())
        thread.daemon = True
        thread.start()
        app.run(host='0.0.0.0', port=2888, threaded=True)
    else:
        print('export SLACK_BOT_TOKEN=xoxb-your-token 을 먼저 실행하세요.')
        print('또는 올바른 Slack Token 인지 확인해보세요.')

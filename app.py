import threading
from flask import Flask
from slackclient import SlackClient

from bot import Bot
from audiobot import AudioBot
from helper import get_secret
from view import viewer


app = Flask(__name__)
app.register_blueprint(viewer)

token = get_secret('slack')['bot']
sc = SlackClient(token)


if __name__ == '__main__':
    if sc.rtm_connect():
        bot = Bot(sc)
        slack_thread = threading.Thread(target=bot.listen, args=())
        slack_thread.daemon = True
        slack_thread.start()

        audiobot = AudioBot()
        audio_thread = threading.Thread(target=audiobot.listen, args=())
        audio_thread.daemon = True
        audio_thread.start()
        app.run(host='0.0.0.0', port=2888, threaded=True)
    else:
        print('export SLACK_BOT_TOKEN=xoxb-your-token 을 먼저 실행하세요.')
        print('또는 올바른 Slack Token 인지 확인해보세요.')

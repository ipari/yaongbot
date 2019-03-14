import sys
sys.path.insert(0, 'ai-makers-kit/python')


import datetime
import hmac
import hashlib
import gigagenieRPC_pb2
import gigagenieRPC_pb2_grpc
import grpc
import ktkws
import pyaudio
import wave
from ctypes import *
from six.moves import queue

from helper import get_secret


__all__ = ['recognize_self', 'get_speech_to_text', 'get_text_to_speech']


kt_secret = get_secret('kt')
CLIENT_ID = kt_secret['client_id']
CLIENT_KEY = kt_secret['client_key']
CLIENT_SECRET = kt_secret['client_secret']

KWS_MODEL_PATH = 'ai-makers-kit/data/kwsmodel.pack'

RATE = 16000
CHUNK = 512


def getMetadata():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
    message = CLIENT_ID + ':' + timestamp
    signature = hmac.new(CLIENT_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()
    metadata = [('x-auth-clientkey', CLIENT_KEY),
                ('x-auth-timestamp', timestamp),
                ('x-auth-signature', signature)]

    return metadata


def credentials(context, callback):
    callback(getMetadata(), None)


def getCredentials():
    sslCred = grpc.ssl_channel_credentials()
    authCred = grpc.metadata_call_credentials(credentials)
    return grpc.composite_channel_credentials(sslCred, authCred)


ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
    dummy_var = 0
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
asound = cdll.LoadLibrary('libasound.so')
asound.snd_lib_error_set_handler(c_error_handler)


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)


def play_file(fname):
    # create an audio object
    wf = wave.open(fname, 'rb')
    p = pyaudio.PyAudio()
    chunk = 1024

    # open stream based on the wave object which has been input.
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # read data (based on the chunk size)
    data = wf.readframes(chunk)

    # play stream (looping from beginning of file to the end)
    while len(data) > 0:
        # writing to the stream is what *actually* plays the sound.
        stream.write(data)
        data = wf.readframes(chunk)

        # cleanup stuff.
    stream.close()
    p.terminate()


def detect():
    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()

        for content in audio_generator:
            rc = ktkws.detect(content)
            if rc == 1:
                play_file("ai-makers-kit/data/sample_sound.wav")
                return 200


def recognize_self(keyword_index):
    ktkws.init(KWS_MODEL_PATH)
    ktkws.start()
    ktkws.set_keyword(keyword_index)
    rc = detect()
    ktkws.stop()
    return rc


# Config for GiGA Genie gRPC
HOST = 'gate.gigagenie.ai'
PORT = 4080


def generate_request():
    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()

        for content in audio_generator:
            message = gigagenieRPC_pb2.reqVoice()
            message.audioContent = content
            yield message


def get_speech_to_text():
    print('[STT] started')
    channel = grpc.secure_channel('{}:{}'.format(HOST, PORT), getCredentials())
    stub = gigagenieRPC_pb2_grpc.GigagenieStub(channel)
    request = generate_request()
    result = ''
    for response in stub.getVoice2Text(request):
        if response.resultCd == 200:  # partial
            print('{:>3} | {}'.format(response.resultCd, response.recognizedText))
            result = response.recognizedText
        elif response.resultCd == 201:  # final
            print('{:>3} | {}'.format(response.resultCd, response.recognizedText))
            result = response.recognizedText
            break
        else:
            print('{:>3} | {}'.format(response.resultCd, response.recognizedText))
            break
    print('>>> | {}'.format(result))
    return result


def get_text_to_speech(text, filename='answer.wav'):
    print('[TTS] started')
    channel = grpc.secure_channel('{}:{}'.format(HOST, PORT), getCredentials())
    stub = gigagenieRPC_pb2_grpc.GigagenieStub(channel)

    message = gigagenieRPC_pb2.reqText()
    message.lang = 0
    message.mode = 0
    message.text = text
    rc = None
    with open(filename, 'wb') as f:
        for response in stub.getText2VoiceStream(message):
            rc = response.resOptions.resultCd
            if response.HasField("resOptions"):
                print('{:>3} |'.format(rc))
            if response.HasField("audioContent"):
                print('{:>3} | Save as {}'.format(rc, filename))
                f.write(response.audioContent)
    play_file(filename)
    print('>>> | play {}'.format(filename))
    return rc

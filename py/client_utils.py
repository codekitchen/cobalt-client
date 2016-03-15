import Queue
from threading import Thread
import json
import time
import wave
import requests

def get_file_data(file):
    wave_read = wave.open(file, 'r')
    sample_rate = wave_read.getframerate()
    frames = wave_read.getnframes()
    file_audio_seconds = float(frames) / sample_rate
    wave_read.close()
    return sample_rate, frames, file_audio_seconds

def get_stt_one_best(stt_result):
    one_best = list()
    for item in stt_result['nbest'][0]['hypothesis']:
        one_best.append(item['value'])
    return one_best

def check_recognizer_construct(recognizer_construct):
    allowed_keys = ['model-id', 'model-domain', 'transcripts', 'recognizer-type', 'timeout', 'synchronous']
    for key in recognizer_construct:
        if key not in allowed_keys:
            raise Exception('unknown key found in recognizer_construct ' + key)

def send_wav_audio_file(base_url, audio_filepath, recognizer_construct):
    url = base_url+"/recognize"
    headers = {'event-type': 'file', 'file-type':'wav'}
    if recognizer_construct is not None:
        check_recognizer_construct(recognizer_construct)
        headers.update(recognizer_construct)
    data = open(audio_filepath, 'rb').read()
    start = time.time()
    r = requests.post(url, headers=headers, data=data)
    end = time.time()

    return r.text, end - start

def send_fail_call(url, expected_error_msg=None, header=None, data=None, verbose=True):
    response = requests.post(url, headers=header, data=data)
    if verbose:
        print response.text
    response_dict = json.loads(response.text)
    if expected_error_msg:
        assert(expected_error_msg in response_dict['error']['message'])

# expect this call to succeed
def send_create_recognizer(url, recognizer_construct, is_extended=False, requests_obj=requests):
    header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    if is_extended:
        data = {'type': 'create-extended-recognizer'}
    else:
        data = {'type': 'create-recognizer'}
    if recognizer_construct is not None:
        check_recognizer_construct(recognizer_construct)
        data.update(recognizer_construct)
    response = requests_obj.post(url, headers=header, data=json.dumps(data))
    if response.status_code != 200:
        raise Exception('create recognizer api failed: ' +response.text )
    response_dict = json.loads(response.text)
    recognizer_id = response_dict['recognizer-id']
    return recognizer_id

# expect this call to succeed
def send_delete_recognizer(url, recognizer_id, requests_obj=requests):
    header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {'type': 'delete-recognizer', 'recognizer-id':recognizer_id}
    response = requests_obj.post(url, headers=header, data=json.dumps(data))
    if response.status_code != 200:
        raise Exception('delete recognizer api call failed.')
    return response.text

def check_response_success(response, expected_message=None):
    if response.status_code != 200:
        raise Exception('api call failed! ' + response.text)
    if expected_message:
        response_dict = json.loads(response.text)
        assert(expected_message in response_dict['message'])
    return response.text

def send_model_attributes(base_url, model_id):
    get_attributes = {'type': 'get-model-attributes', 'model-id': model_id}
    header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    api_url = base_url + "/api"
    response = requests.post(api_url, headers=header, data=json.dumps(get_attributes))
    if response.status_code != 200:
        raise Exception('get-model-attributes api call failed!')
    return json.loads(response.text)

def send_stream_audio(post_obj, url, recognizer_id, bytes):
    header = {'event-type': 'streaming-audio', 'recognizer-id': recognizer_id}
    response = post_obj.post(url, headers=header, data=bytes)
    return check_response_success(response, expected_message='pushed audio')

def send_clear_audio_queue(post_obj, url, recognizer_id):
    header = {'event-type': 'clear-audio-queue', 'recognizer-id': recognizer_id}
    response = post_obj.post(url, headers=header)
    return check_response_success(response, expected_message='pushed clear audio queue')

def send_end_session(post_obj, url, recognizer_id):
    header = {'event-type': 'end-session', 'recognizer-id': recognizer_id}
    response = post_obj.post(url, headers=header)
    return check_response_success(response, expected_message='pushed end session')

def send_get_result(post_obj, url, recognizer_id, expected_message=None):
    header = {'event-type': 'get-result', 'recognizer-id': recognizer_id}
    response = post_obj.post(url, headers=header)
    return check_response_success(response, expected_message=expected_message)

def wav_file_iter(audio_filepath):
    # for a 16khz file, this is 3200 samples -> 200 msec per chunk
    chunk_size = 6400
    # this is a .wav file, so we remove the first 44 bits.
    begin_index = 44

    with open(audio_filepath, 'rb') as infile:
        infile.read(begin_index)
        while True:
            data = infile.read(chunk_size)
            if data:
                yield data
            else:
                break

def recognize_stream_audio(base_url, audio_filepath, recognizer_construct=None):
    recognize_url = base_url+ '/recognize'
    api_url = base_url+ '/api'
    start = time.time()
    requests_obj = requests.Session()
    recognizer_id = send_create_recognizer(api_url, recognizer_construct, is_extended=False, requests_obj=requests_obj)
    for chunk in wav_file_iter(audio_filepath):
        send_stream_audio(requests_obj, recognize_url, recognizer_id, chunk)
    send_clear_audio_queue(requests_obj, recognize_url, recognizer_id)
    send_end_session(requests_obj, recognize_url, recognizer_id)

    results = send_get_result(requests_obj, recognize_url, recognizer_id,
                              expected_message='returning results')
    send_delete_recognizer(api_url, recognizer_id, requests_obj=requests_obj)
    end = time.time()
    return results, end - start

def recognize_stream_audio_async(base_url, audio_filepath, recognizer_construct=None):
    recognize_url = base_url + '/recognize'
    api_url = base_url + '/api'

    start = time.time()
    requests_obj = requests.Session()
    recognizer_construct = recognizer_construct or {}
    recognizer_construct['synchronous'] = False
    recognizer_id = send_create_recognizer(api_url, recognizer_construct, requests_obj=requests_obj)

    results = []

    def producer(queue):
        for chunk in wav_file_iter(audio_filepath):
            send_stream_audio(requests_obj, recognize_url, recognizer_id, chunk)
        # block until the recognizer is done, and then we'll update the flag for the consumer
        send_clear_audio_queue(requests_obj, recognize_url, recognizer_id)
        send_end_session(requests_obj, recognize_url, recognizer_id)
        # poison pill
        queue.put(None)

    def consumer(queue):
        while True:
            try:
                result = send_get_result(requests_obj, recognize_url, recognizer_id, expected_message='returning results')
                results.append(result)
            except Exception:
                pass

            done_flag = False
            try:
                item = queue.get(block=False, timeout=None)
                if item is None:
                    done_flag = True
            except Exception as e:
                pass
            if done_flag:
                send_delete_recognizer(api_url, recognizer_id, requests_obj=requests_obj)
                break

    queue = Queue.Queue()
    producer_queue = Thread(target=producer, args=(queue,))
    consumer_queue = Thread(target=consumer, args=(queue,))
    producer_queue.start()
    consumer_queue.start()

    consumer_queue.join()
    producer_queue.join()

    end = time.time()
    return results, end - start

def recognize_long_wav_file(base_url, audio_filepath, recognizer_construct=None, verbose=False):
    recognize_url = base_url + '/recognize'
    api_url = base_url + '/api'

    requests_obj = requests.Session()
    recognizer_id = send_create_recognizer(api_url, recognizer_construct, is_extended=True, requests_obj=requests_obj)

    start = time.time()

    results = []
    for chunk in wav_file_iter(audio_filepath):
        send_stream_audio(requests_obj, recognize_url, recognizer_id, chunk)
        try:
            result = send_get_result(requests_obj, recognize_url, recognizer_id, expected_message='returning results')
            if verbose:
                print result
            results.append(result)
        except Exception:
            pass

    send_end_session(requests_obj, recognize_url, recognizer_id)
    result = send_get_result(requests_obj, recognize_url, recognizer_id)
    results.append(result)
    send_delete_recognizer(api_url, recognizer_id, requests_obj=requests_obj)

    end = time.time()
    return results, end - start

# work is the JSON version of 'listfile work'.
# audio_file is the audio path.
# recognizer construct is the rest of the JSON
def get_audio_and_construct(work):
    audio_file = work['audio_file']
    recognizer_construct = {}
    allowed_keys = ['model_id', 'model_domain', 'transcripts', 'recognizer_type']
    for key in allowed_keys:
        if key in work:
            recognizer_construct[key.replace('_', '-')] = work[key]
    if len(recognizer_construct) == 0:
        recognizer_construct = None
    return audio_file, recognizer_construct

import os, json
import scipy.io.wavfile
from multiprocessing import Process, Queue
from client_utils import get_audio_and_construct, send_wav_audio_file, recognize_stream_audio

def writer(dest_filename, queue, stop_token):
    with open(dest_filename, 'w') as dest_file:
        while True:
            line = queue.get()
            if line == stop_token:
                return
            dest_file.write(line)
            dest_file.write('\n')

class MultiProcessFileWriter:
    def __init__(self, dest_filename):
        self.queue = Queue()
        self.stop_token="STOP!!!"
        writer_process = Process(target = writer, args=(dest_filename, self.queue, self.stop_token))
        writer_process.start()

    def stop(self):
        self.queue.put(self.stop_token)

    def write(self, line):
        self.queue.put(line)

class AudioSender:
    def __init__(self, audio_files, url, transmit_method, loop, results_writer=None, metrics_writer=None):
        self.audio_files = audio_files
        self.url = url
        self.transmit_method = transmit_method
        self.loop = loop
        self.results_writer = results_writer
        self.metrics_writer = metrics_writer

    def save_results_and_metrics(self, results, time_elapsed_seconds, file):
        # save metrics
        if self.metrics_writer:
            rate, data = scipy.io.wavfile.read(file)
            file_audio_seconds = float(len(data)) / rate
            metrics_dict = {'filename': file,
                            'file_audio_seconds': file_audio_seconds,
                            'time_elapsed_seconds': time_elapsed_seconds,
                            'real_time_factor': float(time_elapsed_seconds)/file_audio_seconds}
            self.metrics_writer.write(json.dumps(metrics_dict))

        # save results
        if self.results_writer:
            # this helps with our results, this is the format we expect for results.
            recognition_name = os.path.basename(file)
            if recognition_name.endswith('.wav'):
                recognition_name = recognition_name.rstrip('.wav')
            msg = ' '.join([recognition_name, results])
            self.results_writer.write(msg)
        else:
            print results

    def run(self):
        while True:
            for work in self.audio_files:
                audio, recognizer_construct = get_audio_and_construct(work)
                if self.transmit_method == 'file':
                    results, time_elapsed_seconds = send_wav_audio_file(self.url, audio, recognizer_construct)
                    self.save_results_and_metrics(results, time_elapsed_seconds, audio)
                elif self.transmit_method == 'streaming':
                    results, time_elapsed_seconds = recognize_stream_audio(self.url, audio, recognizer_construct)
                    self.save_results_and_metrics(results, time_elapsed_seconds, audio)
                else:
                    raise Exception('unsupported transmit method: ' + self.transmit_method)

            if not self.loop:
                break

def run_stt(audio_files, url, transmit_method, loop, results_writer, metrics_writer):
    sender = AudioSender(audio_files, url, transmit_method, loop, results_writer, metrics_writer)
    sender.run()

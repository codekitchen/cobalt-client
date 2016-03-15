import argparse
from multiprocessing import Process
from listfile_parser import ListfileParser
from work_partitioner import RoundRobinPartitioner
from run_stt import run_stt, MultiProcessFileWriter

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('audiofile', type=str,
                   help='audio file path.')
    parser.add_argument('--url', type=str, default='http://localhost:8888',
                   help='url to send requests to')
    parser.add_argument('--transmit_method', type=str, default='file',
                   help='method for data transmission')
    parser.add_argument('--loop', type=int, default=1,
                   help='loop the file(s)')
    parser.add_argument('--processes', type=int, default=1,
                   help='send the files in parallel')
    parser.add_argument('--metrics_file', type=str, default='',
                   help='file to save metrics')
    parser.add_argument('--results_file', type=str, default='',
                   help='file to save results')
    parser.add_argument('--list_file', type=bool, default=False,
                   help='boolean to indicate whether audiofile was a listfile.')
    parser.add_argument('--stress_same', type=bool, default=False,
                        help='boolean to indicate whether we want to just send the same file (or list of files) over processes.')
    args = parser.parse_args()

    metrics_writer = None
    if args.metrics_file != '':
        metrics_writer = MultiProcessFileWriter(args.metrics_file)

    results_writer = None
    if args.results_file != '':
        results_writer = MultiProcessFileWriter(args.results_file)

    if args.list_file:
        parser = ListfileParser(args.audiofile)
        audio_files = parser.parse_listfile()
    else:
        # the argument is an audio file, but we make it a JSon so we can execute the same processing code later.
        audio_files = [{'audio_file': args.audiofile}]

    running_time = None # no limit for running time
    processes = list()
    partitioner = RoundRobinPartitioner(audio_files, args.processes)
    partitions = partitioner.partition(args.stress_same)
    for t in range(0, len(partitions)):
        p = Process(target=run_stt,
                    args=(partitions[t], args.url, args.transmit_method, args.loop, running_time, results_writer, metrics_writer))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    if metrics_writer:
        metrics_writer.stop()

    if results_writer:
        results_writer.stop()

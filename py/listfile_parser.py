import os, json

class ListfileParser:
    def __init__(self, listfile_path):
        self.listfile_dir = os.path.dirname(listfile_path)
        self.listfile = listfile_path

    def make_work(self, line):
        work = dict()
        # check if work is a json line
        try:
            work = json.loads(line)
            # 'audio_path' is a required key
            assert('audio_path' in work)
            audiopath = self.get_audiopath(work['audio_path'], self.listfile_dir)
            work['audio_path'] = audiopath
            return work
        except ValueError: # json decoding exception.
            # exceptions are ok.
            pass
        if len(line.split()) == 1:
            filename = line
        if len(line.split()) == 2:
            filename = line.split()[1]
        if len(line.split()) > 2:
            raise Exception('Unknown listfile format ' + line)

        audiopath = self.get_audiopath(filename, self.listfile_dir)
        work['audio_path'] = audiopath
        return work

    def get_audiopath(self, filename, listfile_dirpath):
        relative_path = os.path.join(listfile_dirpath, filename)
        if os.path.isfile(filename):
            return filename
        elif os.path.isfile(relative_path):
            return relative_path
        else:
            raise Exception('Unable to find file ' + filename)
    # We'll support 3 forms of input in each non-comment, non-empty line of a listfile
    # (1) filepath only (audio.wav)
    # (2) speaker-id filepath (speaker-1 audio.wav)
    # (3) Json
    def parse_listfile(self):
        work_list = list()
        with open(self.listfile, 'r') as in_file:
            for line in in_file:
                if line.startswith('#') or line.strip() == '':
                    continue
                work = self.make_work(line.strip())
                work_list.append(work)
        return work_list


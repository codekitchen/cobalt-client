# a very simple work partitioner that ignores speaker-ids, file size etc.
# files are simply partitioned in round-robin format.

class RoundRobinPartitioner:
    def __init__(self, audio_files, requested_partitions):
        self.audio_files = audio_files
        self.requested_partitions = requested_partitions

    def partition(self, stress_same):
        # return the same exact audio files for each partition.
        if stress_same:
            num_partitions = self.requested_partitions
            partitions = list()
            for i in range(num_partitions):
                partitions.append(self.audio_files)
            return partitions

        num_partitions = min(len(self.audio_files), self.requested_partitions)
        partitions = list()
        for i in range(num_partitions):
            partitions.append(list())
        count = 0
        index = 0
        while count < len(self.audio_files):
            partitions[index].append(self.audio_files[count])
            index += 1
            if (index == len(partitions)):
                index = 0
            count += 1

        return partitions
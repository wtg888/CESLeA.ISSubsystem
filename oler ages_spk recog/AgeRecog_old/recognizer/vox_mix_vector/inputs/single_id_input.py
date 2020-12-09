import numpy as np

keep_out_size = 3


class TrainGenerator:
    def __init__(self):
        self.xids = np.load('/home/swlee/data/voxceleb/xvector_final/open/xvector_train/train_cluster_id.npy')
        self.dids = np.load('/home/swlee/data/voxceleb/dvector/open/dvector_train/train_cluster_id.npy')
        self.iids = np.load('/home/swlee/data/voxceleb/ivector/ivector_train/train_cluster_id.npy')
        self.xvectors = np.load('/home/swlee/data/voxceleb/xvector_final/open/xvector_train/train_sequence.npy')
        self.dvectors = np.load('/home/swlee/data/voxceleb/dvector/open/dvector_train/train_sequence.npy')
        self.ivectors = np.load('/home/swlee/data/voxceleb/ivector/ivector_train/train_sequence.npy')
        self.id_count = 5994

        print(len(self.xids))
        self.x_split_ids = []
        self.d_split_ids = []

        last_id = ''
        for i in range(len(self.xids)):
            if self.xids[i] != last_id:
                self.x_split_ids.append(i)
                last_id = self.xids[i]
        last_id = ''
        for i in range(len(self.iids)):
            if self.iids[i] != last_id:
                self.d_split_ids.append(i)
                last_id = self.iids[i]

        # size = np.array(self.split_ids[1:]) - np.array(self.split_ids[0:-1])
        # print(min(size), max(size))

    def get_batch(self, batch_size):
        data = []
        target = []
        for _ in range(batch_size):
            temp = self._get_single_pair()
            data.append(temp[0])
            target.append(temp[1])

        data = np.stack(data, axis=0)
        target = np.stack(target, axis=0)

        return data, target

    def _get_single_pair(self):
        rand_id = np.random.randint(0, self.id_count-1)
        x_clip = np.random.randint(self.x_split_ids[rand_id]+keep_out_size, self.x_split_ids[rand_id+1])
        d_clip = np.random.randint(self.d_split_ids[rand_id]+keep_out_size, self.d_split_ids[rand_id+1])

        # clip = np.concatenate([self.xvectors[x_clip], self.dvectors[d_clip], self.ivectors[d_clip]], axis=0)
        clip = np.concatenate([self.xvectors[x_clip], self.ivectors[d_clip]], axis=0)
        # clip = self.xvectors[x_clip]

        one_hot = np.zeros(self.id_count)
        one_hot[rand_id] = 1
        return clip, one_hot


class ValidGenerator:
    def __init__(self):
        self.ids = np.load('/home/swlee/data/voxceleb/xvector_final/fix/xvector_vox1_test/test_cluster_ids.npy')
        self.iids = np.load('/home/swlee/data/voxceleb/ivector/ivector_vox1_test/test_cluster_ids.npy')
        self.dids = np.load('/home/swlee/data/voxceleb/dvector/open/dvector_test/test_cluster_ids.npy')
        self.xvectors = np.load('/home/swlee/data/voxceleb/xvector_final/fix/xvector_vox1_test/test_sequences.npy')
        self.dvectors = np.load('/home/swlee/data/voxceleb/dvector/open/dvector_test/test_sequences.npy')
        self.ivectors = np.load('/home/swlee/data/voxceleb/ivector/ivector_vox1_test/test_sequences.npy')
        self.id_count = 118
        self.batch_count = 0

    def get_all(self):
        batch1 = []
        batch2 = []
        target = []
        for i in range(len(self.ids)):
            ids = self.ids[i]
            d_temp = self.xvectors[i]
            i_temp = self.ivectors[i]
            batch1.append(np.concatenate([d_temp[0], i_temp[0]], axis=0))
            batch2.append(np.concatenate([d_temp[1], i_temp[1]], axis=0))
            # batch1.append(d_temp[0])
            # batch2.append(d_temp[1])

            gt = 1 if ids[0]==ids[1] else 0
            target.append(gt)

            self.batch_count+=1

        batch1 = np.stack(batch1, axis=0)
        batch2 = np.stack(batch2, axis=0)
        target = np.stack(target, axis=0)

        return batch1, batch2, target


class TestGenerator:
    def __init__(self):
        self.ids = np.load('/home/swlee/data/voxceleb/xvector_final/open/xvector_voxsrc_test/test_cluster_ids.npy')
        self.iids = np.load('/home/swlee/data/voxceleb/ivector/ivector_voxsrc_test/test_cluster_ids.npy')
        self.xvectors = np.load('/home/swlee/data/voxceleb/xvector_final/open/xvector_voxsrc_test/test_sequences.npy')
        self.ivectors = np.load('/home/swlee/data/voxceleb/ivector/ivector_voxsrc_test/test_sequences.npy')
        self.id_count = 118
        self.batch_count = 0

    def get_all(self):
        batch1 = []
        batch2 = []
        target = []
        for i in range(len(self.ids)):
            ids = self.ids[i]
            d_temp = self.xvectors[i]
            i_temp = self.ivectors[i]
            batch1.append(np.concatenate([d_temp[0], i_temp[0]], axis=0))
            batch2.append(np.concatenate([d_temp[1], i_temp[1]], axis=0))
            # batch1.append(d_temp[0])
            # batch2.append(d_temp[1])

            gt = 1 if ids[0]==ids[1] else 0
            target.append(gt)

            self.batch_count+=1

        batch1 = np.stack(batch1, axis=0)
        batch2 = np.stack(batch2, axis=0)
        target = np.stack(target, axis=0)

        return batch1, batch2, target

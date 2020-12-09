import numpy as np

keep_out_size = 3


class TrainGenerator:
    def __init__(self):
        self.xids = np.load('/home/craftkim/vectors/open/xvector_train_final_open.npz_FILES/train_cluster_id.npy')
        self.dids = np.load('/home/craftkim/vectors/open/dvector_train_open.npz_FILES/train_cluster_id.npy')
#        self.iids = np.load('/home/swlee/data/voxceleb/ivector/ivector_train/train_cluster_id.npy')
        self.xvectors = np.load('/home/craftkim/vectors/open/xvector_train_final_open.npz_FILES/train_sequence.npy')
        self.dvectors = np.load('/home/craftkim/vectors/open/dvector_train_open.npz_FILES/train_sequence.npy')
#        self.ivectors = np.load('/home/swlee/data/voxceleb/ivector/ivector_train/train_sequence.npy')
        self.id_count = 5994

        self.x_split_ids = []
        self.d_split_ids = []

        last_id = ''
        for i in range(len(self.xids)):
            if self.xids[i] != last_id:
                self.x_split_ids.append(i)
                last_id = self.xids[i]
        last_id = ''
        for i in range(len(self.dids)):
            if self.dids[i] != last_id:
                self.d_split_ids.append(i)
                last_id = self.dids[i]

        # size = np.array(self.split_ids[1:]) - np.array(self.split_ids[0:-1])
        # print(min(size), max(size))

    def get_batch(self, batch_size):
        data1 = []
        data2 = []
        target = []
        for _ in range(int(batch_size//2)):
            temp = self._get_single_pair()
            data1.append(temp[0])
            data2.append(temp[1])
            target.append(temp[2])

        data1 = np.concatenate(data1, axis=0)
        data2 = np.concatenate(data2, axis=0)
        target = np.concatenate(target, axis=0)

        return data1, data2, target

    def _get_single_clip(self, id):
        rand_id = id
        x_clip = np.random.randint(self.x_split_ids[rand_id]+keep_out_size, self.x_split_ids[rand_id+1])
        d_clip = np.random.randint(self.d_split_ids[rand_id]+keep_out_size, self.d_split_ids[rand_id+1])

        clip = np.concatenate([self.xvectors[x_clip], self.dvectors[d_clip]], axis=0)
        # clip = np.concatenate([self.xvectors[x_clip], self.ivectors[d_clip]], axis=0)
        # clip = self.xvectors[x_clip]

        one_hot = np.zeros(self.id_count)
        one_hot[rand_id] = 1
        return clip, one_hot

    def _get_single_pair(self):
        rand_id = np.random.randint(0, self.id_count-1, size=3)

        clip, _ = self._get_single_clip(rand_id[0])
        rand_clip = [clip]
        for i in range(3):
            clip, _ = self._get_single_clip(rand_id[i])
            rand_clip.append(clip)

        if rand_id[1]==rand_id[2]:
            rand_target = 1
        else:
            rand_target = 0

        return [rand_clip[0], rand_clip[2]], \
               [rand_clip[1], rand_clip[3]], \
               [1, rand_target]


class ValidGenerator:
    def __init__(self):
        self.ids = np.load('/home/craftkim/vectors/open/xvector_vox1_test_final_open.npz_FILES/test_cluster_ids.npy')
#        self.iids = np.load('/home/swlee/data/voxceleb/ivector/ivector_vox1_test/test_cluster_ids.npy')
        self.dids = np.load('/home/craftkim/vectors/open/dvector_test_open.npz_FILES/test_cluster_ids.npy')
        self.xvectors = np.load('/home/craftkim/vectors/open/xvector_vox1_test_final_open.npz_FILES/test_sequences.npy')
        self.dvectors = np.load('/home/craftkim/vectors/open/dvector_test_open.npz_FILES/test_sequences.npy')
#        self.ivectors = np.load('/home/swlee/data/voxceleb/ivector/ivector_vox1_test/test_sequences.npy')
        self.id_count = 118
        self.batch_count = 0

    def get_all(self):
        batch1 = []
        batch2 = []
        target = []
        for i in range(len(self.ids)):
            ids = self.ids[i]
            x_temp = self.xvectors[i]
            d_temp = self.dvectors[i]
#            i_temp = self.ivectors[i]
            batch1.append(np.concatenate([x_temp[0], d_temp[0]], axis=0))
            batch2.append(np.concatenate([x_temp[0], d_temp[1]], axis=0))
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
        self.dids = np.load('/home/swlee/data/voxceleb/dvector/open/dvector_test/test_cluster_ids.npy')
        self.xvectors = np.load('/home/swlee/data/voxceleb/xvector_final/open/xvector_voxsrc_test/test_sequences.npy')
        self.dvectors = np.load('/home/swlee/data/voxceleb/dvector/open/dvector_test/test_sequences.npy')
        self.ivectors = np.load('/home/swlee/data/voxceleb/ivector/ivector_voxsrc_test/test_sequences.npy')
        self.id_count = 118
        self.batch_count = 0

    def get_all(self):
        batch1 = []
        batch2 = []
        target = []
        for i in range(len(self.ids)):
            ids = self.ids[i]
            x_temp = self.xvectors[i]
            d_temp = self.dvectors[i]
            i_temp = self.ivectors[i]
            batch1.append(np.concatenate([x_temp[0], d_temp[0], i_temp[0]], axis=0))
            batch2.append(np.concatenate([x_temp[0], d_temp[1], i_temp[1]], axis=0))
            # batch1.append(d_temp[0])
            # batch2.append(d_temp[1])

            gt = 1 if ids[0]==ids[1] else 0
            target.append(gt)

            self.batch_count+=1

        batch1 = np.stack(batch1, axis=0)
        batch2 = np.stack(batch2, axis=0)
        target = np.stack(target, axis=0)

        return batch1, batch2, target

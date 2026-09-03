from termios import VINTR
import tensorflow 

import pandas as pd
import numpy as np
import os
import keras
import random
import cv2
import math
import seaborn as sns

from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.model_selection import train_test_split
# from sklearn import preprocessing

import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras.applications.densenet import preprocess_input

from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator,img_to_array

from tensorflow.keras.optimizers import Adam

from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau

import warnings

import torch
warnings.filterwarnings("ignore")

from Dataset import AudioDataset
from DenseNet_Model import DenseNet
from torch.utils.data import DataLoader, random_split
from tensorflow.python.client import device_lib
from sklearn.utils import shuffle
import datetime
from torch.utils.tensorboard import SummaryWriter
from torch.utils.data.dataloader import default_collate

class Classifier(object):

    def __init__(self, data_path, metadata_path):
        self.dataset = AudioDataset(data_path=data_path, metadata_path=metadata_path)
        self.device = torch.device("cuda:0" if torch.cuda.is_available else "cpu")
        self.encode_labels()
        self.model = DenseNet()
        self.model.freeze_layers()
        self.model.model_summary()
        self.loss_fn = torch.nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.0001)

    def encode_labels(self, labels=None):
        fetched = False
        if labels is None:
            labels = self.dataset.fetch_labels()
            fetched = True
        # print('Labels before encoding:', labels)
        # integer_encoded = LabelEncoder().fit_transform(labels)
        # integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
        # if fetched:
        #     self.le = OneHotEncoder(sparse=False)
        #     self.le.fit(integer_encoded)
        # one_hot_encoded = self.le.transform(integer_encoded)
        # print('Labels after encoding: ', one_hot_encoded.shape, one_hot_encoded[0].shape)
        if fetched:
            self.le = LabelEncoder()
            self.le.fit(labels)
        integer_encoded = self.le.transform(labels)
        # print('Encoded labels: ', integer_encoded)
        return integer_encoded
        # return one_hot_encoded
        # self.label_map = {l: None for l in le.classes_}

    def my_dataloader_collate(self, batch):
        len_batch = len(batch) # original batch length
        batch = list(filter (lambda x:x is not None, batch)) # filter out all the Nones
        # print(f'No. of audios received - {len(batch)}')
        if len_batch > len(batch): # if there are samples missing just use existing members, doesn't work if you reject every sample in a batch
            diff = len_batch - len(batch)
            for i in range(diff):
                batch = batch + batch[:diff]
        return default_collate(batch)

    def generate_batch(self):
        total_samples = len(self.dataset)
        train_sample = round(total_samples * 0.7)
        val_sample = round(total_samples * 0.1)
        test_sample = total_samples - (train_sample + val_sample)

        self.train_data, self.validation_data, self.test_data = random_split(self.dataset, [train_sample, val_sample, test_sample])

        self.train_dl = torch.utils.data.DataLoader(self.train_data, batch_size=2, shuffle=True, collate_fn=self.my_dataloader_collate)
        self.val_dl = torch.utils.data.DataLoader(self.validation_data, batch_size=2, shuffle=True, collate_fn=self.my_dataloader_collate)
        self.test_dl = torch.utils.data.DataLoader(self.test_data, batch_size=2, shuffle=True, collate_fn=self.my_dataloader_collate)
        print('Lengths: ', len(self.train_dl), len(self.val_dl), len(self.test_dl))

    def collate_batch(self, X, Y):
        train_data = []
        labels = []

        for i, item in enumerate(X):
            for j, x in enumerate(item):
                train_data.append(x)
        
        for i, item in enumerate(Y):
            for j, y in enumerate(item):
                labels.append(y)
        
        labels = np.asarray(labels)
        # labels = self.encode_labels(labels).astype('float32')
        labels = self.encode_labels(labels).astype('uint8')
        labels = torch.from_numpy(labels)
        train_data = torch.stack(train_data)
        train_data, labels = shuffle(train_data, labels)
        # train_data = tf.cast(train_data, tf.float32)
        # labels = tf.cast(labels, tf.float32)
        train_data, labels = train_data.to(self.device, dtype=torch.float), labels.to(self.device, dtype=torch.uint8)
        return train_data, labels


    def train_one_epoch(self, epoch_index, tb_writer):
        running_loss = 0.
        last_loss = 0.

        for i, batch in enumerate(self.train_dl):
            X, Y = batch

            # print('Batch: ', batch)
            # print('X attributes: ', X, len(X))
            # print('Y attributes: ', Y, len(Y))
            if len(Y) == 0: continue
                   
            train_data, labels = self.collate_batch(X, Y)
            # continue

            self.optimizer.zero_grad()
            outputs = self.model(train_data)
            loss = self.loss_fn(outputs, labels)
            loss.backward()

            self.optimizer.step()

            running_loss += loss.item()

            if i % 16 == 15:
                last_loss = running_loss / 16
                print('  batch {} loss: {}'.format(i + 1, last_loss))
                tb_x = epoch_index * len(self.train_dl) + i + 1
                tb_writer.add_scalar('Loss/train', last_loss, tb_x)
                running_loss = 0.
        
        return last_loss


    # def train_model(self, checkpoint_path, retrain=False):

    #     # self.x_train, self.y_train = x_train, y_train
    #     # dense = DenseNet()
    #     # self.model = dense.build_model()

    #     # data.fetch_train_data()
    #     # xtrain, ytrain, xtest, ytest = data.train_and_test_data()
    #     # retrain = False if os.path.exists('/mnt/f/Code/Thesis/model.h5') else retrain

    #     print('Now in training model')
    #     if retrain:
    #         print('Retraining the model.')
    #         mod_LR = ReduceLROnPlateau(monitor='accuracy', factor=0.5, patience=5, verbose=1, min_lr=1e-5)
    #         checkpoint = ModelCheckpoint(checkpoint_path, verbose=1, save_best_only=True, monitor='loss')

    #         for epoch in range(20):
    #             print("\n==============================\n")
    #             print("Epoch = " + str(epoch))
    #             # self.train_dl = [b for batch in self.train_dl for b in batch]
    #             # self.train_dl = np.array(self.train_dl)
    #             # print('Type and shape: ', type(self.train_dl), self.train_dl.shape)
    #             # break
                
    #             for (idx, batch) in enumerate(self.train_dl):
    #                 print("Iteration: ", idx)

    #                 X, Y = batch
    #                 # Y = np.asarray(Y)
    #                 # print('Y: ', Y, Y.shape)
    #                 # Y = self.le.transform(Y)
    #                 # print('X attributes: ', len(X), X[0].shape)
    #                 # print('Y attributes: ', len(Y), Y[0])
    #                 train_data = []
    #                 labels = []

    #                 for i, item in enumerate(X):
    #                     for j, x in enumerate(item):
    #                         train_data.append(x)
                    
    #                 for i, item in enumerate(Y):
    #                     for j, y in enumerate(item):
    #                         labels.append(y)
                    
    #                 labels = np.asarray(labels)
    #                 labels = self.encode_labels(labels).astype('float32')
    #                 labels = torch.from_numpy(labels)
    #                 # train_data = np.asarray(train_data)
    #                 train_data = torch.stack(train_data)
    #                 train_data, labels = shuffle(train_data, labels)

    #                 train_data = tf.cast(train_data, tf.float32)
    #                 labels = tf.cast(labels, tf.float32)
    #                 # print('Train_data: ', train_data, type(train_data[0][0]), len(train_data))
    #                 # train_data = torch.cat(train_data)

    #                 # train_data = np.asarray(train_data).astype('float32')
    #                 # print('data: ', train_data, labels, train_data.shape, labels.shape, train_data.dtype, labels.dtype)
    #                 # device = torch.cuda.current_device()
    #                 # print('Current torch device is: ', train_data.device, device)
    #                 # train_data, labels = tf.convert_to_tensor(train_data), tf.convert_to_tensor(labels)
    #                 # print(type(train_data), type(labels))
    #                 # train_data, labels = train_data.to(self.device), labels.to(self.device)
    #                 # print(device_lib.list_local_devices()) 
    #                 # train_data, labels = train_data.cuda(), labels.cuda()
    #                 tf.debugging.set_log_device_placement(True)
    #                 # tf.config.list_physical_devices('GPU')
    #                 # with tf.device("/GPU:0"):
    #                 # print('Labels: ', labels)\
    #                 print('Checking if gpu is available: ', tf.config.list_physical_devices('GPU'))
    #                 history = self.model.fit(x=train_data, y=labels, validation_split=0.1, shuffle=True, batch_size=len(train_data), verbose=2, callbacks=[mod_LR, checkpoint])
    #     else:
    #         self.model.load_weights(checkpoint_path)

    def train_torch_model(self, checkpoint_path, writer, timestamp, retrain=False):
        best_vloss = 1_000_000.
        if retrain:
            for epoch in range(50):
                print('EPOCH {}:'.format(epoch + 1))

                if epoch >= 20:
                    print('Fine tuning')
                    self.model.fine_tune()
    
                # Make sure gradient tracking is on, and do a pass over the data
                self.model.train(True)
                avg_loss = self.train_one_epoch(epoch, writer)
                # return
                
                # We don't need gradients on to do reporting
                self.model.train(False)
                
                running_vloss = 0.0
                for i, vdata in enumerate(self.val_dl):
                    vX, vY = vdata
                    vinputs, vlabels = self.collate_batch(vX, vY)
                    voutputs = self.model(vinputs)
                    vloss = self.loss_fn(voutputs, vlabels)
                    running_vloss += vloss
                
                avg_vloss = running_vloss / (i + 1)
                print('LOSS train {} valid {}'.format(avg_loss, avg_vloss))
                
                # Log the running loss averaged per batch
                # for both training and validation
                writer.add_scalars('Training vs. Validation Loss',
                                { 'Training' : avg_loss, 'Validation' : avg_vloss },
                                epoch + 1)
                writer.flush()
                
                # Track best performance, and save the self.model's state
                if avg_vloss < best_vloss:
                    best_vloss = avg_vloss
                    model_path = 'model_{}_{}'.format(timestamp, epoch)
                    torch.save(self.model.state_dict(), model_path)
                
                epoch += 1
        else:
            self.model.load_state_dict(torch.load(checkpoint_path))
    
    def predict(self):

        # self.x_test, self.y_test = x_test, y_test

        # y_pred = self.model.predict(self.x_test)

        preds = []

        total, accurate, accurate_index, wrong_index = 0, 0, [], []
        with torch.no_grad():
            for (idx, batch) in enumerate(self.test_dl):
                print("Iteration: ", idx)

                if idx == 10:
                    break

                X, Y = batch
                # Y = np.asarray(Y)
                # print('Y: ', Y, Y.shape)
                # Y = self.le.transform(Y)
                # print('X attributes: ', len(X), X[0].shape)
                # print('Y attributes: ', len(Y), Y[0])

                test_data, labels = self.collate_batch(X, Y)

                #print('Test data is: ', test_data)
                y_pred = self.model(test_data)
                y_pred.cpu()
                #print('Predictions are: ', y_pred)
                #print('Labels are: ', labels)
                # print('Length of predictions: ', len(y_pred))
                # print('Length of labels: ', len(labels))
                # print('Batch size was: ', len(test_data))
                # print('Test data shape was: ', test_data.shape)

                # preds.append(y_pred)

                for i in range(len(y_pred)):
                    if np.argmax(y_pred[i].cpu()) == np.argmax(labels[i].cpu()):
                        accurate += 1
                        accurate_index.append(i)
                    else:
                        wrong_index.append(i)
                    
                        total += 1

        print(f'Total test data: {total}, \taccurately predict data: {accurate}, \t wrongly predicted data: {total - accurate}')
        print(f'Accuracy: {round(accurate/total*100, 3)}%')

def main():
    clf = Classifier('/home/sshar201/fma_small/fma_small/', '/home/sshar201/fma_small/fma_metadata/tracks.csv')
    clf.generate_batch()
    timestamp = datetime.datetime.now()
    writer = SummaryWriter('runs/fashion_trainer_{}'.format(timestamp))
    clf.train_torch_model('/home/sshar201/model_run_07_16/', writer, timestamp, retrain=True)
    print('Training finished.')
    # preds = clf.predict()
    # return clf

if __name__ == '__main__':
    clf = main()

    





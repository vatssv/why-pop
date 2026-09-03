from tensorflow.keras.applications import DenseNet121
from tensorflow.keras.layers import Dense,GlobalAveragePooling2D,Convolution2D,BatchNormalization
from tensorflow.keras.layers import Flatten,MaxPooling2D,Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import torch.nn as nn
import torchvision.models as models
import torch
from torchsummary import summary
from torchvision.models.feature_extraction import create_feature_extractor
from sklearn.preprocessing import LabelEncoder
from Dataset import AudioDataset
from torch.autograd import grad
import numpy as np

class DenseNet(nn.Module):

    def __init__(self):        
        super(DenseNet, self).__init__()
        self.le = None #label encoder for ACE
        self.device = torch.device("cuda:0" if torch.cuda.is_available else "cpu")
        # model_d = DenseNet121(weights = 'imagenet', include_top = False, input_shape = (128, 128, 3)) 

        # x = model_d.output

        # x = GlobalAveragePooling2D()(x)
        # x = BatchNormalization()(x)
        # x = Dropout(0.5)(x)
        # x = Dense(1024, activation = 'relu')(x) 
        # x = Dense(512, activation = 'relu')(x) 
        # x = BatchNormalization()(x)
        # x = Dropout(0.5)(x)

        # preds = Dense(8,activation = 'softmax')(x) #FC-layer
        # model = Model(inputs = model_d.input, outputs = preds)

        # for layer in model.layers[:-8]:
        #     layer.trainable = False

        # for layer in model.layers[-8:]:
        #     layer.trainable = True

        # super(DenseNet, self).__init__()
        self.model = models.resnet34(pretrained=True)
        last_layer_features = self.model.fc.in_features
        self.model.fc = nn.Linear(last_layer_features, 8)

        # self.model.compile(optimizer = Adam(learning_rate=0.0001), loss = 'categorical_crossentropy', metrics = ['accuracy'])
        # self.model.summary()
    
        # print('Current device: ', torch.cuda.current_device())
        # print('Trying to change device.')
        # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        # print('Current device: ', self.device)
        # model = model.to(device)

        # print('Model device type: ', next(self.model.parameters()).device)
        # device = torch.cuda.current_device()
        # print('Current device: ', torch.cuda.get_device_name(device))
        # print('Model object type: ', type(model))
        self.model.to(self.device)
        self.images = None
        # print('Model device type: ', next(self.model.parameters()).device)

    def model_summary(self):
        summary(self.model, (3, 224, 224))

    def forward(self, xb):
        return self.model(xb)

    def freeze_layers(self):
        print('Freezing all layers except last.')
        for param in self.model.parameters():
            param.requires_grad = False
        for param in self.model.fc.parameters():
            param.requires_grad = True

    def unfreeze(self):
        print('Unfreezing all layers.')
        for param in self.model.parameters():
            param.requires_grad = True

    def fine_tune(self):
        print('Unfreezing second last layer')
        for param in self.model.layer4.parameters():
            param.requires_grad = True



    def get_image_shape(self):
        return (3, 224, 224)

    def run_examples(self, images, BOTTLENECK_LAYER='layer4'):
        images = np.moveaxis(images, -1, 1)
        self.images = torch.from_numpy(images)
        # print('Images shape: ', self.images.shape)

        return_nodes = {BOTTLENECK_LAYER: 'layer4'}
        intermediate_layer = create_feature_extractor(self.model, return_nodes=return_nodes)
        intermediate_layer.to(self.device)
        self.images = self.images.to(self.device).float().cuda()
        # print('Getting devices of tensors: ', self.images.get_device())
        intermediate_outputs = intermediate_layer(self.images)
        return intermediate_outputs

    def label_to_id(self, CLASS_NAME):
        if self.le:
            return self.le.transform(CLASS_NAME)
        self.le = LabelEncoder()
        self.le.fit(AudioDataset.fetch_labels())
        return self.le.transform(CLASS_NAME)

    def get_gradient(self, activations, CLASS_ID, BOTTLENECK_LAYER='fc'):
        return_nodes = {BOTTLENECK_LAYER: 'fc'}
        logit_layer = create_feature_extractor(self.model, return_nodes=return_nodes)
        logit_layer_outputs = logit_layer(self.images)
        output_count = len(self.images)
        labels = [CLASS_ID for i in range(output_count)]
        labels = torch.FloatTensor(labels)
        loss_fn = torch.nn.CrossEntropyLoss()
        loss = loss_fn(logit_layer_outputs, labels)
        grad_calc = grad(loss, activations)
        return grad_calc
        
        # loss = torch.nn.CrossEntropyLoss()
        pass
        # grad_calc = grad()
    

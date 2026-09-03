from venv import create
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
from torch.autograd import grad, Variable
import numpy as np
from torch.nn.modules.module import register_module_backward_hook

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
        self.gradients = []
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

    def fine_tune(self):
        for name, param in self.model.named_parameters():
            if name == 'layer4.2.conv2.weight':
                param.requires_grad = True
            if name == 'layer4.2.bn2.weight':
                param.requires_grad = True
            if name == 'layer4.2.bn2.bias':
                param.requires_grad = True

    def unfreeze(self):
        print('Unfreezing all layers.')
        for param in self.model.parameters():
            param.requires_grad = True

    def get_image_shape(self):
        return (224, 224, 3)

    def create_intermediate_model(self, bottleneck):
        return_nodes = {bottleneck: bottleneck}
        return create_feature_extractor(self.model, return_nodes=return_nodes)

    def run_examples(self, images, activation_layer, BOTTLENECK_LAYER='layer4'):
        print('Number of images passed: ', len(images), type(images))
        # if len(images) == 2:
        #     print('Images type: ', type(images))
        #     print('Tuple images are: ', images)
        images = torch.from_numpy(np.moveaxis(images, -1, 1)).float().cuda()
        images.requires_grad = True
        images.retain_grad()
        # print('Activation layer attributes: ', activation_layer)
        # self.images = torch.from_numpy(images)
        # print('Images shape: ', self.images.shape)
        # self.model = self.model.cpu()
        # intermediate_layer = create_feature_extractor(self.model, return_nodes=return_nodes)
        # intermediate_layer.to(self.device)
        # self.images = self.images.float().cuda()
        # print('Getting devices of tensors: ', self.images.get_device())
        with torch.no_grad():
            intermediate_outputs = activation_layer(images)

        # print('Activation output was: ', intermediate_outputs[BOTTLENECK_LAYER].shape, intermediate_outputs[BOTTLENECK_LAYER].requires_grad)
        return intermediate_outputs[BOTTLENECK_LAYER].cpu().numpy()

    def label_to_id(self, CLASS_NAME):
        # print('Finding id for label: ', CLASS_NAME, type(CLASS_NAME))
        CLASS_NAME = np.array([CLASS_NAME])
        if self.le:
            return torch.from_numpy(self.le.transform(CLASS_NAME))
        self.le = LabelEncoder()
        self.le.fit(AudioDataset.fetch_labels())
        return torch.from_numpy(self.le.transform(CLASS_NAME))

    def hook(self, module, grad_input, grad_output):
        self.gradients.append(grad_output)

    def get_gradient(self, activations, CLASS_ID, logit_model, images, BOTTLENECK_LAYER='layer4'):
        # activations = torch.from_numpy(activations)
        # activations.requires_grad = True
        # activations.retain_grad()
        # logit_layer = create_feature_extractor(self.model, return_nodes=return_nodes)
        # print('Self.images is: ', self.images)
        output_count = len(images)
        # labels = [CLASS_ID[0] for i in range(output_count)]
        # labels = torch.stack(labels)
        labels = CLASS_ID[0]
        labels = labels.repeat(1, output_count)[0].cuda()
        # print('Finally labels are: ', labels, labels.shape)
        images = torch.from_numpy(np.moveaxis(images, -1, 1)).float().cuda()
        hook_handle = self.model.layer4[2].conv2.register_full_backward_hook(self.hook)
        model_predictions = self.model.forward(images)
        self.model.layer4[2].conv2.weight.retain_grad()
        # print('After adding hooks: ', self.model.layer4[2].conv2._backward_hooks)
        # with torch.no_grad():
        # logit_layer_outputs = logit_model(images)['fc'].cuda()
        loss_fn = torch.nn.CrossEntropyLoss()
        loss = loss_fn(model_predictions, labels).cuda()
        # loss.requires_grad = True
        # print('Grads: ', logit_layer_outputs.grad, activations.grad)
        # print('Loss calculated is: ', loss)
        # print('Before zero grad: ', self.model.layer4[2].conv2)
        self.model.zero_grad()
        # print('After: ', self.model.layer4[2].conv2)
        loss.backward()
        result = self.gradients[0][0]
        self.gradients = []
        hook_handle.remove()
        return result.cpu().numpy()
        # print('Total grads: ', len(self.gradients), self.gradients[0][0].shape)
        # grad_calc = self.model.layer4[2].conv2.weight.grad
        # print('Grad after loss: ', grad_calc.shape)
        # return torch.flatten(grad_calc).cpu().numpy()
        # grad_calc = grad(loss, activations, allow_unused=True)
        # print('Grad calc returned: ', grad_calc)
        # return grad_calc
        
        # loss = torch.nn.CrossEntropyLoss()
        pass
        # grad_calc = grad()
    
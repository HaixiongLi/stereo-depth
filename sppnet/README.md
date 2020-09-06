# sppnet-pytorch
SPP layer could be added in CNN model between convolutional layer and fully-connected lay, so that you can input multi-size images into your CNN model. We use this structure in the paper <a href="https://arxiv.org/abs/1804.02047">Pedestrian-Synthesis-GAN: Generating Pedestrian Data in Real Scene and Beyond</a>
</br>
</br>
The function `spatial_pyramid_pool()` in file `spp_layer.py` is independent. It could be added in your own models.
</br>
</br>
See this:<a href="https://arxiv.org/abs/1406.4729">Spatial Pyramid Pooling in Deep Convolutional Networks for Visual Recognition</a>


## original repo
https://github.com/yueruchen/sppnet-pytorch
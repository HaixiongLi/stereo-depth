python inference.py --KITTI 2015 \
--datapath /media/yoko/SSD-PGU3/workspace/datasets/KITTI/data_scene_flow/testing/ \
--loadmodel /media/yoko/SSD-PGU3/workspace/datasets/stereo-depth/PSMNET/pretrained_model_KITTI2015.tar \
--model stackhourglass \
--maxdisp 192 \
--seed 1
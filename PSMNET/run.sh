python main.py --maxdisp 192 \
               --model stackhourglass \
               --datapath /media/yoko/SSD-PGU3/workspace/datasets/KITTI/data_scene_flow/training/ \
               --epochs 10 \
               --loadmodel /media/yoko/SSD-PGU3/workspace/datasets/stereo-depth/PSMNET/pretrained_model_KITTI2015.tar \
               --savemodel ./result \
               --seed 1
               
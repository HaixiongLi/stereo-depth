## installation
download png++-0.2.9.tar.gz
http://download.savannah.nongnu.org/releases/pngpp/

untar

make && sudo make install

## compile
cd devkit /cpp
g++ -O3 -DNDEBUG -o evaluate_scene_flow evaluate_scene_flow.cpp -lpng

## evalate
please read evaluate_scene_flow.cpp the directory is annoying
./evaluate_scene_flow {result_path}

*make sure you have result_data and traing_data with correct path
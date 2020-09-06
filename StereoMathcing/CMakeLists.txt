cmake_minimum_required(VERSION 2.8.3)
project(stereo_matching)

#C++11
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON 11)

#pcl
find_package(PCL REQUIRED)
include_directories(${PCL_INCLIDE_DIRS})
link_directories(${PCL_LIBRARY_DIRS})

#opencv
find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})
link_directories(${OpenCV_LIBRARY_DIRS})

add_executable(blockMatching blockMatching.cpp)
add_executable(semiGlobalMatching semiGlobalMatching.cpp)


target_link_libraries(blockMatching ${OpenCV_LIBS} ${PCL_LIBS})
target_link_libraries(semiGlobalMatching ${OpenCV_LIBS} ${PCL_LIBS})



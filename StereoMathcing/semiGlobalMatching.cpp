/*
OpenCV Stereo Matching の性能比較 1
http://daily-tech.hatenablog.com/entry/2016/06/25/233203
OpenCV 3.1がリリースされたらしいのでC++でSGBMを試してみる
http://nodemand.hatenablog.com/entry/2016/02/07/123210
*/
#include <iostream>
#include <string>
using namespace std;

#include "opencv2/opencv.hpp"

int main()
{
    string rightImg = "../data/right.png";
    string leftImg = "../data/left.png";

    cv::Mat imgR = cv::imread(rightImg, 1);
    cv::Mat imgL = cv::imread(leftImg, 1);
    cv::Mat dispMat(imgR.rows, imgR.cols, 1);

    int disp = 32;
    int minDisparity = 0;
    int numDisparities = 32;
    int SADWindowSize = 3;
    int P1 = 0;
    int P2 = 0;
    int disp12MaxDiff = 0;
    int preFilterCap = 0;
    int uniquenessRatio = 0;
    int speckleWindowSize = 0;
    int speckleRange = 0;
    int mode = cv::StereoSGBM::MODE_SGBM;

    cv::Ptr<cv::StereoSGBM> sgbm = cv::StereoSGBM::create(minDisparity, numDisparities, SADWindowSize, P1, P2,
                                                          disp12MaxDiff, preFilterCap, uniquenessRatio,
                                                          speckleWindowSize, speckleRange, mode);

    cv::Mat disparity; //((cv::MatSize)leftImg.size, CV_16S);
    cv::TickMeter meter;
    meter.start();

    for (int i = 0; i < 100; i++)
    {
        // Calcuate Disparity
        sgbm->compute(imgL, imgR, disparity);
    }

    meter.stop();
    std::cout << "Average Time for Calculation : "
              << meter.getTimeMilli() / 100.0 << "[ms]" << std::endl;

    double min, max;
    cv::minMaxLoc(disparity, &min, &max);
    cv::convertScaleAbs(disparity, disparity, 255 / (max - min), 255 / min);

    cv::namedWindow("Right Image", CV_WINDOW_AUTOSIZE);
    cv::namedWindow("Left Image", CV_WINDOW_AUTOSIZE);
    cv::namedWindow("Disparity", CV_WINDOW_AUTOSIZE);

    cv::imshow("Right Image", imgR);
    cv::imshow("Left Image", imgL);
    cv::imshow("Disparity", disparity);

    cvWaitKey(0);
    cvDestroyAllWindows();

    return 0;
}
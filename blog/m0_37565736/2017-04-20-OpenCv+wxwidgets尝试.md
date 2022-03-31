---
title: OpenCv+wxwidgets尝试
categories:
  - 上位机
  - wxWidgets
tags:
  - opencv
  - wxwidgets
  - 图像
  - 转换
  - 数组
---

# OpenCv+wxwidgets尝试

wxwidgets对图片的处理是按24bit来的（直接打开8bit位图不算），我需要从串口读取的数据显示图片，而受到的数据是8bit的灰度图，目前发现想把数据转成wxbitmap或wximage都要给他的每个RGB通道拷贝一份灰度数据，三个通道的合起来才是灰度图，而我找到的wxbitmap的一个构造函数确实可以从char构造bitmap，但它的位深度默认为1，即单色图，改变深度为8不能显示了直接。。。之前显示出来图片好高兴的说。。。拷贝三遍感觉好傻，我就去找别的解决办法了，我看Opencv不错，网上的例子也比较多，不像wxwidgets例子少。

基本思路是使用Mat从指向char数据区的指针创建一个Mat实例，再从Mat实现到wxbitmap转换（实际还是拷贝三遍，但这个有相应函数，比较方便），先找从char*构建Mat的方法

备选1：

 
|cv::Mat::Mat|(|int |**rows**,
| | |int |**cols**,
| | |int |**type**,
| | |void * |**data**,
| | |<a>size_t</a> |**step** = `<a>AUTO_STEP</a>` 
| |)

备选2：

 

 
|<a>Mat</a> cv::imdecode|(|<a>InputArray</a> |**buf**,
| | |int |**flags** 
| |)| 

从存储缓冲区读一副图像。

网上推荐的用法：

Mat im=imdecode(Mat(buff),CV_LOAD_IMAGE_COLOR);

buff的定义：char buff[BUFF_SIZE]={0};

应该是直接用char*构造了Mat。。

先尝试第一种：

使用线程：

 

```
MyThread::MyThread(aframeFrame*frame,char* rawdata,int col,int row)
        :wxThread()
{

    data=rawdata;
    width=col;
    heigth=row;
    gui=frame;
}
void *MyThread::Entry()
{
    //int linebyte=(width+3)/4*4;//存储图像的宽度要满足是4的倍数
    Mat mat(width,heigth,CV_8UC1,data);
    wxImage image;
    Mat2wxImage(mat,image);
    ToFrame(image);
    //wxCommandEvent event(wxEVT_COMMAND_MENU_SELECTED,ID_THREAD_TEST);
    //wxGetApp().AddPendingEvent(event);
    return NULL;
}
Mat MyThread::convertType(const Mat&amp; srcImg, int toType, double alpha, double beta)
{
  Mat dstImg;
  srcImg.convertTo(dstImg, toType, alpha, beta);
  return dstImg;
}
void MyThread::Mat2wxImage(Mat &amp;mat, wxImage  &amp;image)
{
    // data dimension
    int w = mat.cols, h = mat.rows;//获取MAT宽度，高度
    int size = w*h*3*sizeof(unsigned char);//为WxImage分配空间数，因为其为24bit，所以*3

// allocate memory for internal wxImage data
unsigned char * wxData = (unsigned char*) malloc(size);//分配空间

// the matrix stores BGR image for conversion
Mat cvRGBImg = Mat(h, w, CV_8UC3, wxData);//转换存储用MAT

    switch (mat.channels())//根据MAT通道数进行转换
    {
    case 1: // 1-channel case: expand and copy灰度到RGB
    {
      // convert type if source is not an integer matrix
      if (mat.depth() != CV_8U)//不是unsigned char先转化
      {
        cvtColor(convertType(mat, CV_8U, 255,0), cvRGBImg, CV_GRAY2RGB);//把图片从一个颜色空间转换为另一个
      }
      else
      {
        cvtColor(mat, cvRGBImg, CV_GRAY2RGB);
      }
    } break;

    case 3: // 3-channel case: swap R&amp;B channels
    {
      int mapping[] = {0,2,1,1,2,0}; // CV(BGR) to WX(RGB)
      // bgra[0] -&gt; bgr[2], bgra[1] -&gt; bgr[1], bgra[2] -&gt; bgr[0]，即转成RGB，舍弃alpha通道
      mixChannels(&amp;mat, 1, &amp;cvRGBImg, 1, mapping, 3);//一个输入矩阵，一个输出矩阵，maping中三个索引对
    } break;

    default://通道数量不对
    {
      wxLogError(wxT("Cv2WxImage : input image (#channel=%d) should be either 1- or 3-channel"), mat.channels());
    }
  }

  image.Destroy(); // free existing data if there's any
  image = wxImage(w, h, wxData);
}
void MyThread::ToFrame(wxImage &amp;image)
{
    gui-&gt;Notify(image);
}

```

转换的程序时从网上找来的，具体参考：

[点击打开链接](http://blog.csdn.net/u010126684/article/details/8912032)

测试成功，图像数据如下：

 

```
static char buff[]={//16*20
2,	4,	6,	8,	10,	12,	14,	16,	18,	20,	22,	24,	26,	28,	30,	32,
3,	5,	7,	9,	11,	13,	15,	17,	19,	21,	23,	25,	27,	29,	31,	33,
4,	6,	8,	10,	12,	14,	16,	18,	20,	22,	24,	26,	28,	30,	32,	34,
5,	7,	9,	11,	13,	15,	17,	19,	21,	23,	25,	27,	29,	31,	33,	35,
6,	8,	10,	12,	14,	16,	18,	20,	22,	24,	26,	28,	30,	32,	34,	36,
7,	9,	11,	13,	15,	17,	19,	21,	23,	25,	27,	29,	31,	33,	35,	37,
8,	10,	12,	14,	16,	18,	20,	22,	24,	26,	28,	30,	32,	34,	36,	38,
9,	11,	13,	15,	17,	19,	21,	23,	25,	27,	29,	31,	33,	35,	37,	39,
10,	12,	14,	16,	18,	20,	22,	24,	26,	28,	30,	32,	34,	36,	38,	40,
11,	13,	15,	17,	19,	21,	23,	25,	27,	29,	31,	33,	35,	37,	39,	41,
12,	14,	16,	18,	20,	22,	24,	26,	28,	30,	32,	34,	36,	38,	40,	42,
13,	15,	17,	19,	21,	23,	25,	27,	29,	31,	33,	35,	37,	39,	41,	43,
14,	16,	18,	20,	22,	24,	26,	28,	30,	32,	34,	36,	38,	40,	42,	44,
15,	17,	19,	21,	23,	25,	27,	29,	31,	33,	35,	37,	39,	41,	43,	45,
16,	18,	20,	22,	24,	26,	28,	30,	32,	34,	36,	38,	40,	42,	44,	46,
17,	19,	21,	23,	25,	27,	29,	31,	33,	35,	37,	39,	41,	43,	45,	47,
18,	20,	22,	24,	26,	28,	30,	32,	34,	36,	38,	40,	42,	44,	46,	48,
19,	21,	23,	25,	27,	29,	31,	33,	35,	37,	39,	41,	43,	45,	47,	49,
20,	22,	24,	26,	28,	30,	32,	34,	36,	38,	40,	42,	44,	46,	48,	50,
21,	23,	25,	27,	29,	31,	33,	35,	37,	39,	41,	43,	45,	47,	49,	51,
};
```

图像显示如下：

 

备选2未完待续。。。。<br/>  

<br/>  

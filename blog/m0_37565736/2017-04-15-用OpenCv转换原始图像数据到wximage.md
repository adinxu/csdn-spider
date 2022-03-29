---
title: 用OpenCv转换原始图像数据到wximage
categories:
  - 上位机
tags:
  - ctb
  - 图像数据
  - 串口
  - bitmap
  - 接收
---
{% include toc %}

# 用OpenCv转换原始图像数据到wximage

接收数据部分好了，显示图片也会了，wxwi中wxBitmap有个构造函数原型如下：

```
wxBitmap::wxBitmap	(	const char 	bits[],
int 	width,
int 	height,
int 	depth = 1 
)	
```

这个函数可以从数组指针生成位图，有了这个函数就可以把从串口接收的数据变成位图。

理想总是美好的。。我搞了个数组测试了下，位图深度设为8，结果不显示。。所以我像前面说的，尝试了opencv库，并且成功了，现在完成的部分有：

1.基本界面

2.能从我的USB口接收单片机发送来的数据，并显示在wxctrltext中（文字模式与10进制模式）

3.能在wxwidgets中显示图片

4.能用opencv把char*指向的存储数据转换为wxwidgets中的wximage（也就是可以实现opencv中图片操作）

现在大致还有两个问题要处理，1.选择到底用opencv还是wxwidgets显示图片（想了想好像不用非要用wxwidgets显示）2.对图片数据的接收

对于第二点，因为图片数据判断接收一副完整图片后要进行处理，所以要对接收函数做一定处理。

第二点目前有三个思路1.自己用WIN32API实现接收2.重载ctb库中的函数3.ctb库中其他read函数封装。

如果是第一种，可以用setcommmask设置串口关联事件，可以用接收缓冲有数据来通知，判断是否读取完了一副图，有读帧头和数数这种笨办法或者结合一下。

第二种，函数自带eos但是如果图像两个帧头就不太方便，所以尝试重载。第三种，判断帧头后调用读取指定字节

先尝试第二种，然后结合一下第一种。读取是采用线程，主线程负责图形界面，还有接收数据线程，处理数据线程等。

好吧，最后虽然差强人意，但大致的样子如下：

```
    int mySerialPort::ReadAnImage(char*&amp; databuf,char* eos)
    {
        DWORD Event;
        DWORD read;
        size_t readed;
        DCB dcb;
        char ch;
        PurgeComm(fd,PURGE_RXCLEAR);
        GetCommState(fd,&amp;dcb);
        dcb.EvtChar=*eos;
        SetCommState(fd,&amp;dcb);
        SetCommMask(fd,EV_RXFLAG);//设定串口接收事件
        while(1)
        {
            if(!WaitCommEvent(fd,&amp;Event,&amp;m_ov))//等待事件没有立即发生
            {
                switch(GetLastError())
                {
                case ERROR_IO_PENDING: break;
                default : return -1;
                }
            }
        WaitForSingleObject(m_ov.hEvent,INFINITE);
        if(!GetOverlappedResult(fd,&amp;m_ov,&amp;read,false))
            return -2;
        ReadFile(fd,&amp;ch,1,&amp;read,&amp;m_ov);
        if(ch==*eos)
            {
                ReadUntilEOS(databuf,&amp;readed,eos,500);
                return 0;
            }
            PurgeComm(fd,PURGE_RXCLEAR);
        }

    }
```

这个函数放在线程中使用

<br/> 

改进版如下，吸收了前辈们的经验：

```
char* mySerialPort::ReadBetweenEos(DWORD ReadBYteNum,char eos)
{
    char* buffer=new char[ReadBYteNum];
    DWORD Event;//wiatcommevent用
    DWORD read;//GetOverlappedResult，ReadFile用
    char ch;//校检帧头用
    Set_RXFLAG(&amp;eos);
    while(1)
    {
        PurgeComm(fd,PURGE_RXCLEAR);
        if(!WaitCommEvent(fd,&amp;Event,&amp;m_ov))//等待事件没有立即发生
        {
            switch(GetLastError())
            {
            case ERROR_IO_PENDING: break;
            default : continue;
            }
        }
    WaitForSingleObject(m_ov.hEvent,INFINITE);
    if(!GetOverlappedResult(fd,&amp;m_ov,&amp;read,false))
        continue;
    while(1)
    {
        ReadFile(fd,&amp;ch,1,&amp;read,&amp;m_ov);
        if(ch==eos) break;
    }
    while(GetCacheByteNum()&lt;(ReadBYteNum+1)) {Sleep(50);}//1是结尾帧头
    ReadFile(fd,buffer,ReadBYteNum,&amp;read,&amp;m_ov);
    ReadFile(fd,&amp;ch,1,&amp;read,&amp;m_ov);
    if(ch==eos) return buffer;
    else PurgeComm(fd,PURGE_RXCLEAR);
    }
}

```

<br/> <br/> 

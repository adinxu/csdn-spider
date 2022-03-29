---
title: codeblocks下OpenCv搭建
categories:
  - 上位机
  - opencv
tags:
---
{% include toc %}

# codeblocks下OpenCv搭建

前面用了wxWidgets写好了图形界面，串口接收数据部分，因为其24位位图原因，于是我又选择了OpenCv库，下载完源码后自己编译，因为wxWidgets使用MinGW编的，而两者第后面又要集成到一起，所以OpenCv也要用MinGW编了，使用cMake工具+MinGW。第一次编译失败了，到41%失败，这时候没去看出错信息，又得知用64位MinGW可编，于是乎再次cMake工具+MinGW_x64，编译成功了，但是我忘记了我的wxWidgets使用自带MinGW编的了，哭。。。

后面继续尝试用自带MinGW编译，得到原有错误，这次看了错误，如下：

```
opencv-3.2.0\modules\highgui\src\window_w32.cpp:50:6: warning: "_WIN32_IE" is not defined [-Wundef]
```

对于错误，百度之，fq谷歌之，得到在CodeBlocks\MinGW\include目录下，即gcc编译器的头文件commctrl.h中有这么一段：

```
#ifdef __cplusplus
extern "C" {
#endif
#ifndef _WIN32_IE
/* define _WIN32_IE if you really want it */
#if 0
#define _WIN32_IE	0x0300
#endif
#endif
```

外国友人推荐改成如下：（红字部分）

```
#ifdef __cplusplus
extern "C" {
#endif
#ifndef _WIN32_IE
/* define _WIN32_IE if you really want it */
#if 1
#define _WIN32_IE	0x0500
#endif
#endif
```

```
D:\opencv-3.2.0\modules\highgui\src\window_w32.cpp:50:6: warning: "_WIN32_IE" is not defined [-Wundef]
 #if (_WIN32_IE &lt; 0x0500)
      ^
D:\opencv-3.2.0\modules\highgui\src\window_w32.cpp:51:99: note: #pragma message: WARNING: Win32 UI needs to be compiled with _WIN32_IE &gt;= 0x0500 (_WIN32_IE_IE50)
 #pragma message("WARNING: Win32 UI needs to be compiled with _WIN32_IE &gt;= 0x0500 (_WIN32_IE_IE50)")
```

他喵的明明别人说编译通过了

```
#if (_WIN32_IE &lt; 0x0500)
#pragma message("WARNING: Win32 UI needs to be compiled with _WIN32_IE &gt;= 0x0500 (_WIN32_IE_IE50)")
#define _WIN32_IE 0x0500
#endif
#include &lt;commctrl.h&gt;//注意这行
```

换顺序。。。。。再次编译之.......

```
D:\opencv-3.2.0\modules\highgui\src\window_w32.cpp: In function 'void cvSetModeWindow_W32(const char*, double)':
D:\opencv-3.2.0\modules\highgui\src\window_w32.cpp:473:47: error: 'MONITOR_DEFAULTTONEAREST' was not declared in this scope
             hMonitor = MonitorFromRect(&amp;rect, MONITOR_DEFAULTTONEAREST);
                                               ^
D:\opencv-3.2.0\modules\highgui\src\window_w32.cpp:473:71: error: 'MonitorFromRect' was not declared in this scope
             hMonitor = MonitorFromRect(&amp;rect, MONITOR_DEFAULTTONEAREST);
                                                                       ^
D:\opencv-3.2.0\modules\highgui\src\window_w32.cpp: In function 'LRESULT MainWindowProc(HWND, UINT, WPARAM, LPARAM)':
D:\opencv-3.2.0\modules\highgui\src\window_w32.cpp:1376:45: error: 'MONITOR_DEFAULTTONEAREST' was not declared in this scope
           hMonitor = MonitorFromRect(&amp;rect, MONITOR_DEFAULTTONEAREST);
                                             ^
D:\opencv-3.2.0\modules\highgui\src\window_w32.cpp:1376:69: error: 'MonitorFromRect' was not declared in this scope
           hMonitor = MonitorFromRect(&amp;rect, MONITOR_DEFAULTTONEAREST);
```

即这一句

```
          hMonitor = MonitorFromRect(&amp;rect, MONITOR_DEFAULTTONEAREST);
```
|Minimum supported client|Windows 2000 Professional [desktop apps only]

Windows 2000 Professional [desktop apps only]
|Minimum supported server|Windows 2000 Server [desktop apps only]

Windows 2000 Server [desktop apps only]
|Header|<dl>           Winuser.h (include Windows.h)         </dl>

找到winuser.h有

```
#if (_WIN32_WINNT &gt;= 0x0500 || _WIN32_WINDOWS &gt;= 0x0410)
WINUSERAPI HMONITOR WINAPI MonitorFromPoint(POINT,DWORD);
WINUSERAPI HMONITOR WINAPI MonitorFromRect(LPCRECT,DWORD);
WINUSERAPI HMONITOR WINAPI MonitorFromWindow(HWND,DWORD);
```

就是说MinGW里windows版本可能是0x0400，呵呵

找到然后改掉。。

投降了，换成2.4.13，编译一次通过。。。。强烈怀疑我刚开始下的是develop版本。。

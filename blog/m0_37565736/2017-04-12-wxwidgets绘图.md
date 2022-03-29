---
title: wxwidgets绘图
categories:
  - 上位机
  - wxWidgets
tags:
  - wxwidgets
  - 图片
  - 绘图
  - 设备上下文
  - bitmap
---
{% include toc %}

# wxwidgets绘图

## 图片文件显示

以下，绘图相关函数：

### 加载位图

```
    wxBitmap bitmap("test.bmp",wxBITMAP_TYPE_BMP);
    if(!bitmap.IsOk())
    {
        wxMessageBox("狗日的图片读不出来");
    }
```

当然

当然还有其他的加载方式，比较特殊的是xpm文件，它以c代码保存，可以用include直接包含进文件。

### 选择文件：

```
    wxMemoryDC temp_dc;
    temp_dc.SelectObject(bitmap);
```

可用的设备上下文：

窗口类一般会收到两种类型的绘画事件：wxPaintEvent事件用来绘制窗口客户区的主要图形而wxEraseEvent事件则用来通知应用程序擦除背景。

而如果你打算绘制一个长时间存在的不会被重绘事件和擦除背景事件所擦除的东西（就叫东西好了。。。），你可以定义一个OnPaint函数，并且与wxPaintEvent通过事件表关联，在《使用wxwidgets进行跨平台开发》一书中说如果你定了窗重画事件处理函数，那么在这里面你必须创建一个wxPaintDC，就算你根本不用它。。。但是我试过直接用clientDC绘图，貌似没什么区别。。书上解释说产生的这个对象将告诉窗口体系需要重画区域已经被重画，这样窗口系统就不会重复发送消息给这个窗口了。也不知新版还有没有这个特性，书的版本可能适合老版本wxwi，因为有些类都已经弃置不用了。。。不过wxwiki也有：

另外wxWindow::GetUpdateRegion()可以获得需要重画区域，wxWindow::IsExposed()函数可以用来判断某个点或者某个矩形是否需要被重画。然后优化代码使得只有这个区域的内容被重画。重画事件还可以通过调用wxWindow::Refresh和wxWindow::RefreshRect函数手动产生。这两个函数可能不会立即响应，可以调用后用wxWindow::Update。

如果你不想使用EVT_PAINT()这个事件宏可以用wxClientDC来绘图。

说起wxClientDC，一把辛酸泪，用了两三天都没搞好，今天终于搞明白之前为什么显示不出来了。。之前用wxPaintEvent事件试过，可以显示，然后wxEraseEvent事件也可以，鼠标拖拽画图也行，但是我直接在窗口构建函数里显示就是没东西了，今天我突然想起来是不是构建函数构建完之后wxClientDC无效了，然后直接在MyApp::OnInit()里实现。。。竟然真的显示了。。高兴！！wahahahaha去整合到之前写的上位机中去了

<a>wxMemoryDC</a>：

可以在位图上作图。

在单色位图上绘图时, 使用 `wxWHITE`, `wxWHITE_PEN` 和 `wxWHITE_BRUSH` 将绘制背景色，所有其他颜色都会绘制前景色。

想使用这个位图干任何事都必须先用wxmemorydc选择图片，(原文：A bitmap must be selected into the new memory DC before it may be used for anything. )但是我加载完位图后直接drawbitmap还是可以显示，所以这句话应该是相对图片进行改动必须调用吧。。

```
1.temp_dc.SelectObject(wxNullBitmap);
```

2.完全销毁设备上下文。。也就是创建的<a>wxMemoryDC</a>的实例
<td align="right">void </td>|<a>SelectObject</a> (<a>wxBitmap</a> &amp;bitmap)
<td align="right">void </td>|<a>SelectObjectAsSource</a> (const <a>wxBitmap</a> &amp;bitmap)

```
    wxPaintDC* adc=new wxPaintDC(this);
    wxDC* clientDC=adc;
    wxSize sz(100,100);
    wxPen pen(*wxRED,1);
    clientDC-&gt;SetPen(pen);
    clientDC-&gt;DrawRectangle(wxPoint(0,0),sz);
```

## 原始像素显示

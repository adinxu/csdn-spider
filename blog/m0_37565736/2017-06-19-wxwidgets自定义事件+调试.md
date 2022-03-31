---
title: wxwidgets自定义事件+调试
categories:
  - wxWidgets
  - 上位机
tags:
  - wxwidgets
  - 自定义
  - 事件
---

# wxwidgets自定义事件+调试

自定义事件

大体方法

就像每个事件被其事件类型所唯一确定一样，定义一个自定义事件从为它定义一个新事件类型开始。这通过使用<a title="Define a new event type associated with the specified event class.">**wxDEFINE_EVENT()**</a>宏来完成。就像事件类型是可变的，如果有必要它也可以通过使用<a title="Declares a custom event type.">**wxDECLARE_EVENT()**</a>宏来声明。

另一件要做的事情就是决定你是否需要为事件定义一个自定义事件类或使用已经存在的类，代表性的有<a title="An event is a structure holding information about an event passed to a callback or member function...">**wxEvent**</a>（它不会提供任何额外的信息）或<a title="This event class contains information about command events, which originate from a variety of simple ...">**wxCommandEvent**</a>（它包含几种额外的域，并且默认把事件向上传递）。这两种方式的细节都将都将在下面描述。代码详细说明和使用自定义事件类型的完整例子也可以在**事件示例**中查看。

最后你将需要产生并发送你的自定义事件。产生事件就像实例化你的自定义事件类并初始化其内部值那样简单。为了发送事件到一个特定的事件句柄，这里有两种可选：使用<a title="Post an event to be processed later.">**wxEvtHandler::AddPendingEvent**</a>或<a title="Queue event for a later processing.">**wxEvtHandler::QueueEvent**</a>**。**当进行内部线程通信时，你基本上只需要使用后者。当你只使用主线程时，你也可以安全的使用前者。

最后需要注意的是，还有两个简单的全局封装函数关联到提到的那两个<a title="A class that can handle events from the windowing system.">**wxEvtHandler**</a>函数，即<a title="In a GUI application, this function posts event to the specified dest object using wxEvtHandler::AddP...">**wxPostEvent()**</a> 和 <a title="Queue an event for processing on the given object.">**wxQueueEvent()**</a>。

使用存在的事件类

如果你仅打算使用<a title="This event class contains information about command events, which originate from a variety of simple ...">**wxCommandEvent**</a>和一个新事件类型，可以使用下面列出的事件表宏之一而不用自己定义一个新事件类。

Example:

```
wxDECLARE_EVENT(MY_EVENT, wxCommandEvent);//这句很明显应该位于头文件中：它仅仅声明了MY_EVENT这个事件类型

wxDEFINE_EVENT(MY_EVENT, wxCommandEvent);//这是事件类型定义，所以不能位于头文件

wxBEGIN_EVENT_TABLE(MyFrame, wxFrame)//用事件表处理事件的示例代码
EVT_MENU (wxID_EXIT, MyFrame::OnExit)
...
EVT_COMMAND (ID_MY_WINDOW, MY_EVENT, MyFrame::OnMyEvent)
wxEND_EVENT_TABLE()
void MyFrame::OnMyEvent(wxCommandEvent&amp; event)//事件处理函数
{
// do something
wxString text = event.GetString();
}

MyFrame::MyFrame()// 使用Bind&lt;&gt;()处理事件的示例代码:
{
Bind(MY_EVENT, &amp;MyFrame::OnMyEvent, this, ID_MY_WINDOW);
}

void MyWindow::SendEvent()// 产生事件的示例代码
{
wxCommandEvent event(MY_EVENT, GetId());
event.SetEventObject(this);
event.SetString("Hello");// 给它一些包含的信息
ProcessWindowEvent(event);//发送它
}

```

实验图：

定义你自己的事件类

在一些环境下，你必须定义你自己的事件类，例如从一个地方发送一些很复杂的数据到另一个地方。除了定义你的事件类，如果你打算事件表来处理这种类型的事件，你还需要定义你自己的事件表宏。

Here is anexample:

```
class MyPlotEvent: public wxEvent// 定义新事件类
{
public:
MyPlotEvent(wxEventType eventType, int winid, const wxPoint&amp; pos)
: wxEvent(winid, eventType),
m_pos(pos)
{
}
wxPoint GetPoint() const { return m_pos; }// 获取成员变量
virtual wxEvent *Clone() const { return new MyPlotEvent(*this); }//实现纯虚函数
private:
const wxPoint m_pos;
};

//我们定义了一个关联到上面的类的单独的事件类型 MY_PLOT_CLICKED ，但很明显你需要不止一个事件类型，例如，
//你还可以拥有MY_PLOT_ZOOMED或MY_PLOT_PANNED，在这种情况下你只需要在这添加更多相似的内容。
wxDEFINE_EVENT(MY_PLOT_CLICKED, MyPlotEvent);

/**************************************************************************************************/
// 如果你想支持旧编译器你需要使用下面这些繁琐的宏:
typedef void (wxEvtHandler::*MyPlotEventFunction)(MyPlotEvent&amp;);
#define MyPlotEventHandler(func) wxEVENT_HANDLER_CAST(MyPlotEventFunction, func)

//如果你的代码使用现在流行的编译器编译，你就可以这样做：
#define MyPlotEventHandler(func) (&amp;func)

//最后定义一个宏为新的事件类型创建一个完整的事件表
//记住如果你使用Bind&lt;&gt;() 你就完全不需要这些，你可以仅使用 &amp;func来代替MyPlotEventHandler(func)，除非你用的是非常老的编译器。

#define MY_EVT_PLOT_CLICK(id, func)  \
wx__DECLARE_EVT1(MY_PLOT_CLICKED, id, MyPlotEventHandler(func))

//处理事件的示例代码（你将使用两者之一，而不是两个都用）
事件表：
wxBEGIN_EVENT_TABLE(MyFrame, wxFrame)
EVT_PLOT(ID_MY_WINDOW, MyFrame::OnPlot)
wxEND_EVENT_TABLE()

动态绑定：
MyFrame::MyFrame()
{
Bind(MY_PLOT_CLICKED, &amp;MyFrame::OnPlot, this, ID_MY_WINDOW);
}

void MyFrame::OnPlot(MyPlotEvent&amp; event)
{
... do something with event.GetPoint() ...
}

// 产生事件的示例代码：
void MyWindow::SendEvent()
{
MyPlotEvent event(MY_PLOT_CLICKED, GetId(), wxPoint(...));
event.SetEventObject(this);
ProcessWindowEvent(event);
}

```

实验图如下：

需要注意的是这句：

```
#define MY_EVT_PLOT_CLICK(id, func)  \
wx__DECLARE_EVT1(MY_PLOT_CLICKED, id, MyPlotEventHandler(func))
```

\是继续符，代表下一行接本行，我本来以为上面那个是说明文档里出错了，实际上是我错了。。还有里面有两个_接起来，我本来以为怎么可能起这种宏名，没想到真的是两个。。还有一个就是标识id是窗口id，我原来理解不到位，把触发事件的按钮的id当多了标识id，结果事件找不到对应的处理函数了。。。。

再一个，这句：

```
#define MyPlotEventHandler(func) (&amp;func)
```

不知道干嘛用的，我不用这句，使用事件表依旧工作正常。。。

事件表的向上传递寻找之类的我现在也没怎么搞清楚，我从一个线程传递事件到非父窗口的窗口时大概如下：

自定义事件类：

```
class MyThreadEvent: public wxThreadEvent
{
public:
    MyThreadEvent(wxEventType eventType, int winid,unsigned char* pdate);

    virtual wxEvent *Clone() const {return new MyThreadEvent(*this);}

    unsigned char* GetPointer() const {return p;};
private:
    unsigned char* p;
};
```

事件类型也定义声明Ok：

头文件中：

```
wxDECLARE_EVENT(WX_POINTER_ARR,MyThreadEvent);
```

```
wxDEFINE_EVENT(WX_POINTER_ARR,MyThreadEvent);
```

然后写好事件映射宏：

```
#define EVT_POINTER_ARR(id,fn) DECLARE_EVENT_TABLE_ENTRY(WX_POINTER_ARR\
                                  ,id\
                                  ,-1\
                                  ,&amp;fn\
                                  ,(wxObject*)NULL\
                                  ),
```

事件表：

```
BEGIN_EVENT_TABLE(showpic,wxFrame)
	EVT_POINTER_ARR(wxID_ANY,showpic::OnProcessThreadEvent)
END_EVENT_TABLE()
```

```
void showpic::OnProcessThreadEvent(MyThreadEvent&amp; event)
{
    image.Destroy();//清除原来的图片
    image=wxImage(col,row,event.GetPointer());//生成新的图片
    bitmap = wxBitmap(image.Scale(800,600));//调整大小
    Refresh(false);
}
```

```
wxQueueEvent(windows,new MyThreadEvent(WX_POINTER_ARR,wxID_ANY,imgdate));
```

其中windows是处理事件的窗口的指针。

## 关于事件的产生
|<table><tbody><tr><td>virtual void wxEvtHandler :: QueueEvent|（|<a>wxEvent</a> * |事件|）| 

事件放入队列以便进行后续处理。

该方法类似于<a title="处理事件，搜索事件表并调用零个或多个合适的事件处理函数">ProcessEvent（），</a>但是后者是同步的，即事件在函数返回之前立即被处理，这一个是异步的，并且将在稍后的时间（通常在下一个事件期间）处理事件循环迭代）。

另一个重要的区别是这个方法会获取**事件**参数的所有权，即它会自动删除它。这意味着事件应该在堆上分配，并且在函数返回之后指针不能再被使用（因为它可以随时被删除）。

<a title="队列事件进行后续处理。">QueueEvent（）</a>可用于从工作线程到主线程的线程间通信，它在内部使用锁定，并通过确保正在调用的线程不会再使用**事件**对象来避免<a title="发布事件稍后处理。">AddPendingEvent（）</a>文档中提到的问题。应该注意避免该对象的某些字段被它使用，特别是事件对象的任何<a title="String class for passing textual data to or receiving it from wxWidgets.">wxString</a>成员不能是另一个<a title="String class for passing textual data to or receiving it from wxWidgets.">wxString</a>对象的浅层副本，因为这将导致它们在后台仍然使用相同的字符串缓冲区。例如：

请注意，您可以使用<a title="该类为wxEvent增加了一些简单的功能，以促进线程间通信。">wxThreadEvent</a>而不是<a title="此事件类包含有关命令事件的信息，这些信息源自各种简单的...">wxCommandEvent</a>来避免此问题：

最后注意到，如果通过调用<a title="此功能唤醒（内部和平台依赖）空闲系统，即">wxWakeUpIdle（）</a>当前处于空闲状态，则此方法会自动唤醒事件循环，因此在使用它时不需要手动执行。
|事件|要排队的堆分配事件，<a title="队列事件进行后续处理。">QueueEvent（）</a>拥有它的所有权。该参数不应该`NULL`。

在<a>wxWindow中</a>重新实现。
|<table><tbody><tr><td>virtual void wxEvtHandler :: AddPendingEvent|（|const <a>wxEvent</a>＆ |事件|）| 

发布事件稍后处理。

这个功能类似于<a title="队列事件进行后续处理。">QueueEvent（） </a>，但不能用于发布来自工作线程事件与事件对象<a title="将文本数据传递到wxWidgets或从wxWidgets接收的String类。">wxString</a>场（即在实践中大多数），因为不安全使用相同的<a title="将文本数据传递到wxWidgets或从wxWidgets接收的String类。">wxString</a>对象，是因为该<a title="将文本数据传递到wxWidgets或从wxWidgets接收的String类。">wxString</a>原始**事件**对象中的字段及其由该函数内部创建的副本在内部共享相同的字符串缓冲区。使用<a title="队列事件进行后续处理。">QueueEvent（）</a>来避免这种情况。

一个**事件**副本由函数进行，所以一旦函数返回（原来是在堆栈上创建的），原来的代码就可以被删除。这要求<a title="返回事件的副本。">wxEvent :: Clone（）</a>方法由事件实现，以便可以将其复制并存储直到被处理。
|事件|事件添加到挂起的事件队列。

在<a>wxWindow中</a>重新实现。
|<table><tbody><tr><td>virtual bool wxEvtHandler :: ProcessEvent|（|<a>wxEvent</a>＆ |事件|）| 

处理事件，搜索事件表并调用零个或多个合适的事件处理函数。

通常，您的应用程序不会调用此函数：它在wxWidgets实现中调用，以将传入的用户界面事件分派到框架（和应用程序）。

但是，如果实现定义新事件类型的新功能（例如新控件），则可能需要调用它，而不是允许用户覆盖虚拟函数。

请注意，您通常不需要重写<a title="处理事件，搜索事件表并调用零个或多个合适的事件处理函数">ProcessEvent（）</a>来自定义事件处理，覆盖特别提供的<a title="在检查此对象事件表之前，ProcessEvent（）调用的方法。">TryBefore（）</a>和<a title="ProcessEvent（）调用的方法是最后的手段。">TryAfter（）</a>函数通常就足够了。例如，<a title="一个MDI（多文档界面）父帧是一个可以包含MDI子帧的窗口">wxMDIParentFrame</a>可以覆盖<a title="在检查此对象事件表之前，ProcessEvent（）调用的方法。">TryBefore（），</a>以确保在父框架本身处理之前在活动子帧中处理菜单事件。

事件表搜索的正常顺序如下：
1. <a title="覆盖wxEventFilter方法。">wxApp :: FilterEvent（）</a>被调用。如果它返回任何东西`-1`（默认），处理在这里停止。1. <a title="在检查此对象事件表之前，ProcessEvent（）调用的方法。">TryBefore（）</a>被调用（这是<a title="wxValidator是一系列验证器类的基类，它们在一个类之间进行调用">wxWalidator</a>被考虑在<a title="wxWindow是所有窗口的基类，表示屏幕上的任何可见对象。">wxWindow</a>对象的地方）。如果返回true，则退出该函数。1. 如果对象被禁用（通过调用<a title="启用或禁用事件处理程序。">wxEvtHandler :: SetEvtHandlerEnabled</a>），该函数跳到步骤（7）。1. 使用<a title="使用事件动态绑定给定的函数，函子或方法。">Bind &lt;&gt;（）绑定</a>的处理程序的动态事件表在最近期绑定到最早绑定的顺序中进行搜索。如果找到一个处理程序，它将被执行，并且该函数返回true，除非使用<a title="这个方法可以在一个事件处理程序中使用，来控制是否有更多的事件处理程序绑定到...">wxEvent :: Skip（）</a>处理程序来表示它没有处理事件，在这种情况下搜索继续。1. 使用事件表宏绑定的处理程序的静态事件表按源代码中事件表宏的出现顺序搜索该事件处理程序。如果失败，则会尝试使用基类事件表，直到不再存在表或找到适当的函数为止。如果找到一个处理程序，则与上一步相同的逻辑适用。<li>搜索被应用在整个事件处理程序链上（通常链的长度为1）。这个链可以使用<a title="将指针设置为下一个处理程序。">wxEvtHandler :: SetNextHandler（）</a>形成：
   （指图像，如果`A-&gt;ProcessEvent`被调用，并且不处理事件，`B-&gt;ProcessEvent`将被调用等等）。请注意，在<a title="wxWindow是所有窗口的基类，表示屏幕上的任何可见对象。">wxWindow</a>的情况下，您可以构建一堆事件处理程序（有关更多信息，请参阅<a title="将此事件处理程序推送到窗口的事件堆栈。">wxWindow :: PushEventHandler（）</a>）。如果任何链接的处理程序返回true，则该函数退出。</li>1. <a title="ProcessEvent（）调用的方法是最后的手段。">TryAfter（）</a>被调用：对于<a title="wxWindow是所有窗口的基类，表示屏幕上的任何可见对象。">wxWindow</a>对象，这可能会将事件传播到窗口父（递归）。如果仍未处理该事件，则将wxTheApp对象上的<a title="处理事件，搜索事件表并调用零个或多个合适的事件处理函数">ProcessEvent（）</a>作为最后一步进行调用。
注意步骤（2） - （6）在该函数调用的<a title="尝试处理这个处理程序中的事件和所有链接的事件。">ProcessEventLocally（）</a>中执行。
|事件|事件处理。

在<a>wxWindow中</a>重新实现。

还有这两个，它们是全局函数：
|void wxQueueEvent|（|<a>wxEvtHandler</a> * |dest，
| | |<a>wxEvent</a> * |事件 
| |）| | 

对给定对象进行处理排队事件。

这是围绕<a title="队列事件进行后续处理。">wxEvtHandler :: QueueEvent（）</a>的包装器，有关更多详细信息，请参阅其文档。

包含文件：
|DEST|对象将事件排队，不能`NULL`。
|事件|堆分配和非`NULL`事件队列，该函数拥有它的所有权。
|void wxPostEvent|（|<a>wxEvtHandler</a> * |dest，
| | |const <a>wxEvent</a>＆ |事件 
| |）| | 

在GUI应用程序中，此函数使用<a title="发布事件稍后处理。">wxEvtHandler :: AddPendingEvent（）将</a>**事件发布**到指定的**dest**对象。

否则，它使用<a title="处理事件，搜索事件表并调用零个或多个合适的事件处理函数">wxEvtHandler :: ProcessEvent（）</a>立即调度**事件**。有关详细信息，请参阅各自的文档（和警告）。由于限制<a title="发布事件稍后处理。">wxEvtHandler :: AddPendingEvent（）</a>这个函数是不是线程安全具有事件对象<a title="将文本数据传递到wxWidgets或从wxWidgets接收的String类。">wxString</a>字段，使用<a title="对给定对象进行处理排队事件。">wxQueueEvent（）</a>来代替。

包含文件：

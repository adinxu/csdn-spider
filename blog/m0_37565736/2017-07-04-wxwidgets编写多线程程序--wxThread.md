---
title: wxwidgets编写多线程程序--wxThread
categories:
  - wxWidgets
  - 上位机
tags:
  - 多线程
  - wxthread
  - wxwidgets
---

# wxwidgets编写多线程程序--wxThread

细节描述

线程基本上来说是应用程序中一条单独执行的路径。线程有时被称为轻量级进程，但线程与进程的根本不同之处在于不同进程存储空间是相互独立的，而同一进程里的所有线程共享同一地址空间。尽管这使得它更容易共享几个线程间的普通数据，但这也使得它有了另一个麻烦，即可能有多个线程同时访问一个变量，所以要小心的使用用于同步对象访问的变量，例如使用信号量（mutexes）和关键区域（critical sections）是被推荐的。另外，不要创建全局变量对象，因为在他们的构造函数里分配空间将会造成内存检查系统出现问题。

线程类型

wxWidgets有两种类型的线程：分离线程和联合线程，它们参考了POSIX 线程 API。这与win32API不同，其线程全部都是联合的。wxWidgets默认wxThreads为分离线程。分离线程一旦结束就会删除它们自己，不论是它们完成处理是自己完成删除还是通过调用**Delete()**，分离线程必须创建在堆上（例如通过new）。如果你想对你分配的分离线程上调用函数，你可以保存它们的实例（这句好像有问题啊，原文：Typically you'llwant to store the instances of the detached wxThreads you allocate, so that youcan call functions on them.）。因为它们的特性所致，你每次访问它们都必须使用关键区域。

 

```
//声明一个新的事件种类用于我们的MyThread类
wxDECLARE_EVENT(wxEVT_COMMAND_MYTHREAD_COMPLETED, wxThreadEvent);
wxDECLARE_EVENT(wxEVT_COMMAND_MYTHREAD_UPDATE, wxThreadEvent);

wxDEFINE_EVENT(wxEVT_COMMAND_MYTHREAD_COMPLETED, wxThreadEvent);//定义事件种类
wxDEFINE_EVENT(wxEVT_COMMAND_MYTHREAD_UPDATE, wxThreadEvent);


class MyFrame;//前置声明

class MyThread : public wxThread
{
public:
	MyThread(MyFrame *handler)
        	: wxThread(wxTHREAD_DETACHED)
        { 
		m_pHandler = handler 
	}
	
	~MyThread();
protected:
	virtual ExitCode Entry();
	MyFrame *m_pHandler;
};

class MyFrame : public wxFrame
{
public:
	...
	~MyFrame()
	{
	//任何对线程的清理相对于在析构函数来说最好在事件处理函数OnClose()中进行。
	//这是因为顶层窗口的事件循环在调用它的析构函数处不会激活，如果在窗口析构时线程发送事件，
	//这些事件不会被处理除非你在OnClose结束线程
	}
	...
	void DoStartThread();
	void DoPauseThread();
	//线程恢复和DoPauseThread()非常相似

	void DoResumeThread() { ... }

	void OnThreadUpdate(wxThreadEvent&amp;);
	void OnThreadCompletion(wxThreadEvent&amp;);
	void OnClose(wxCloseEvent&amp;);
protected:
	MyThread *m_pThread;
	wxCriticalSection m_pThreadCS; // 保护m_pThread指针
	friend class MyThread; //友元函数，允许访问我们的线程m_pThread
	wxDECLARE_EVENT_TABLE();
};

wxBEGIN_EVENT_TABLE(MyFrame, wxFrame)
EVT_CLOSE(MyFrame::OnClose)
EVT_MENU(Minimal_Start, MyFrame::DoStartThread)
EVT_COMMAND(wxID_ANY, wxEVT_COMMAND_MYTHREAD_UPDATE, MyFrame::OnThreadUpdate)
EVT_COMMAND(wxID_ANY, wxEVT_COMMAND_MYTHREAD_COMPLETED, MyFrame::OnThreadCompletion)
wxEND_EVENT_TABLE()


void MyFrame::DoStartThread()
{
	m_pThread = new MyThread(this);
	if ( m_pThread-&gt;Run() != wxTHREAD_NO_ERROR )
	{
		wxLogError("Can't create the thread!");
		delete m_pThread;
		m_pThread = NULL;
	}
	//在调用wxThread::Run()之后，指针m_pThread是不安全的：
	//在任何时候线程都有可能结束（因为它完成了自己的工作）
	//为了避免调用无效的指针，在线程结束时OnThreadExit()中将会把指针赋值为空。
}
wxThread::ExitCode MyThread::Entry()
{
	while (!TestDestroy())
	{
		// ... 干一些事情...
		wxQueueEvent(m_pHandler, new wxThreadEvent(wxEVT_COMMAND_MYTHREAD_UPDATE));//发送事件
	}

	//通知事件句柄这个线程将会被销毁。注意：这里我们假定使用m_pHandler是安全的
	//（在这种情况下这将由MyFrame的析构函数确保）
	wxQueueEvent(m_pHandler, new wxThreadEvent(wxEVT_COMMAND_MYTHREAD_COMPLETED));//发送事件
	return (wxThread::ExitCode)0; // 成功
}

MyThread::~MyThread()
{
	wxCriticalSectionLocker enter(m_pHandler-&gt;m_pThreadCS);
	//线程正在被销毁，确保不要调用了无效的指针
	m_pHandler-&gt;m_pThread = NULL;
}

void MyFrame::OnThreadCompletion(wxThreadEvent&amp;)
{
	wxMessageOutputDebug().Printf("MYFRAME: MyThread exited!\n");
}

void MyFrame::OnThreadUpdate(wxThreadEvent&amp;)
{
	wxMessageOutputDebug().Printf("MYFRAME: MyThread update...\n");
}

void MyFrame::DoPauseThread()
{

	//任何时候我们访问m_pThread时必须先确认在此期间它不会被修改；由于一个单独线程在给出时位于一个
	//安全区域，所以下面的代码是安全的。
	wxCriticalSectionLocker enter(m_pThreadCS);
	if (m_pThread) // 线程仍旧存在？
	{
	//不在安全区域，一旦到达这里，下列情况可能会发生：系统调度把控制权给MyThread::Entry()，
	//而这时候线程可能会因为完成了处理而使指针无效

	if (m_pThread-&gt;Pause() != wxTHREAD_NO_ERROR )

	wxLogError("Can't pause the thread!");
	}
}

void MyFrame::OnClose(wxCloseEvent&amp;)
{
	{
		wxCriticalSectionLocker enter(m_pThreadCS);
		if (m_pThread) // 线程仍旧存在？
			{
				wxMessageOutputDebug().Printf("MYFRAME: deleting thread");
				if (m_pThread-&gt;Delete() != wxTHREAD_NO_ERROR )
				wxLogError("Can't delete the thread!");
			}
	}
	//离开安全区域来给线程进入析构函数的可能（安全区域保护m_pThreadCS）
	while (1)
	{
		{ // 析构函数执行了吗？
		wxCriticalSectionLocker enter(m_pThreadCS);
		if (!m_pThread) break;
		}
		// wait for thread completion
		wxThread::This()-&gt;Sleep(1);
	}
	Destroy();
}
```

 

 

 

相反的，联合线程不会自我删除当他们完成处理，它可以安全创建在栈上。联合线程同样提供了通过**Wait()**来获得**Entry()****的**返回值的功能。你不需要急着把所有的线程都创建为联合线程，因为它们也拥有不利之处：你必须使用**Wait()**函数来给联合线程释放资源，不然它占用的系统资源不会被释放，而且你必须手动的正确的删除线程对象如果你没在栈上创建它。相反的，分离线程是“点火即忘”：你只需要开始分离线程，当它完成处理，它会自动停止并销毁它自己

线程删除

不管它是否已经停止，你都应该在联合线程调用**Wait()**来释放内存，就像前面线程种类里说的那样。如果你在堆上创建了一个线程，记得手动删除它们使用delete操作或类似的只有分离线程处理这种内存管理类型（后半句好奇怪，原文：If you created ajoinable thread on the heap, remember to delete it manually with thedelete operator or similar means as onlydetached threads handle this type of memory management.）

因为分离线程完成处理会自我删除，你要小心在其上调用程序。如果你确定线程正在运行，并想结束它，你可以优雅的调用来**Delete()**结束他（这意味着线程会在调用**Delete()**后删除掉）。这意味着你永远都不应该尝试使用delete或相似的操作来删除分离线程。

就像是上面提到的，**Wait()** 和 **Delete()**都分别尝试优雅的删除分离与联合线程。它们通过等待直到线程调用**TestDestroy()**或结束处理（例如从**wxThread::Entry**返回）

（这句也有问题，原文：They do this by waiting until the thread in questioncalls**TestDestroy()** or endsprocessing）

明显的，如果线程已经调用**TestDestroy()**并且没有结束，调用**Wait()** 或**Delete()**的线程将会停止。这就是为什么要在你的线程的**Entry()**尽可能频繁的调用**TestDestroy()**并在它返回true时立即结束。

万不得已你可以使用**Kill()**立即结束线程。这种方式极度不推荐你用，因为这样并不能释放与对象相联系的资源（尽管分离线程的线程对象仍会被删除）并会是c运行库处于不安全状态。

 第二线程调用绘图wxwidgets

 

除了“主程序线程”(运行wxApp:OnInit()或主函数运行的一个函数)之外的所有线程都被认为是“二级线程”。

GUI调用，例如对wxWindow或wxBitmap的调用，在二级线程中是不安全的，可能会过早结束你的应用程序。这是由于好几个原因：包括底层的nativeAPI，类似于其他api如MFC一样，wxThread不在二级线程运行aGUI事件循环。

工作区的一些wxWidgets端口会在任何GUI调用前调用 wxMutexGUIEnter() ，然后调用wxMutexGUILeave()。但是，推荐的方法是通过wxQueueEvent()发送的事件，在主线程中简单地处理GUI调用。但这并不代表调用这些类是线程安全的，包括 **wxString**在内许多类都不是线程安全的。

 不要轮询wxThread

用户使用**wxThread**的一个普遍问题是在主线程它们会每次调用**IsRunning()**检查线程看他们是否已经结束，结果发现它们的应用程序出现问题了，因为线程是默认的分离线程而且线程已经自我删除。自然的，它们会尝试使用联合线程来取代前面的分离特性。然而，轮询一个来看他们是否已结束通常来说不是个好主意—实际上，如果可能，任何对正在运行的线程调用的函数都应该避免。相反的，当线程已经结束寻找一种方法来通知你自己。

通常你只需要通知主线程，在这种情况你可以通过**wxQueueEvent()**来发送事件给他。第二线程的情况时，如有必要，你可以调用别的类的程序当线程：完成处理、使用信号量对变量赋值、别的同步操作

测试图：

运行时

使用Delete()函数删除线程

我现在感觉联合线程应当是用于当另一线程需要等待联合线程完成某项任务时再运行，这时就可以在联合线程周期调用TestDesdory()而等待线程调用联合线程的wait()，这样就可以避免等待线程白白消耗资源。而分离线程就是自己运行完自己删除，如果需要和别的线程通信还可以用事件通知。

**用于线程同步的对象**

1.wxMutex--互斥量

 
|<a>wxMutexError</a> |<a>Lock</a> ()<br/> 锁定互斥对象，相当于参数为infinite的<a>LockTimeout</a>（） 函数。<br/> 注意：若此互斥量早已被调用线程锁定，则函数不会阻塞而会立即返回

 
|<a>wxMutexError</a> |<a>LockTimeout</a> (unsigned long msec)<br/> 尝试锁定互斥量，在特定时间周期内
|<a>wxMutexError</a> |<a>TryLock</a> ()
| |尝试锁定互斥量，若不能锁定，函数会立即返回，并且返回 `wxMUTEX_BUSY错误`
<td colspan="2"> </td>
|<a>wxMutexError</a> |<a>Unlock</a> ()
| |解锁互斥量

wxMutexLocker

wxmutex的辅助函数，构造函数中以一个互斥量为参数，他将在析构函数中解锁互斥量，这使得互斥量的解锁更加可靠，即使忘记解锁也不会造成死锁。

bool wxMutexLocker::IsOk()const

若取得互斥量所有权，返回true，否则返回false.

2.wxCriticalSection--关键区域

 
|void |<a>Enter</a> ()
| |进入关键区域，如果早已经有别的线程进入，则本次调用将会被阻塞，直到那个线程调用了 <a>Leave()</a>.<br/> 注意：如果一个线程多次进入关键区域，这并不会导致死锁，事实上在这种情况下函数会立刻返回。
<td colspan="2"> </td>
|bool |<a>TryEnter</a> ()
| |尝试进入关键区域，如果不能进入，它会立即返回false。
<td colspan="2"> </td>
|void |<a>Leave</a> ()
| |离开关键区域使得其他线程得以访问被他保护的全局数据。

wxCriticalSectionLocker，作用类似wxMutexLocker

 

3.wxCondition--条件变量

 

 
|<a>wxCondError</a> |<a>Broadcast</a> ()
| |通知所有线程，把他们都唤醒<br/> 注意：这个函数可能会被调用，无论与之相关联的互斥量是否为锁定状态，
<td colspan="2"> </td>
|bool |<a>IsOk</a> () const
| |若对象早已被成功初始化则返回true，若有错误发生返回false
<td colspan="2"> </td>
|<a>wxCondError</a> |<a>Signal</a> ()
| |唤醒最多一个对象。<br/> 若多个线程等待同一条件变量，确切的被唤醒线程是未定义的。若无线程在等待，这次信号将会丢失，而条件变量必须再次发信号，以唤醒那些稍后可能会开始等待的线程。<br/>注意：这个函数可能会被调用，无论与之相关联的互斥量是否为锁定状态
<td colspan="2"> </td>
|<a>wxCondError</a> |<a>Wait</a> ()
| |等待直到条件变量激发。此方法将会自动解锁与条件变量相关联的互斥量的锁。然后使线程进入睡眠状态直到<a>Signal()</a>或<a>Broadcast()</a>被调用，它会再次锁定互斥量然后返回。<br/> 注意：即使<a>Signal()</a>在<a>Wait()</a>之前已经被调用，且没有唤醒任何线程，线程仍旧会继续等待下一个信号，所以确保<a>Signal()</a>在<a>Wait()</a>之后调用是很重要的，不然线程也许将一直睡眠下去
<td colspan="2"> </td>
<td colspan="2">template&lt;typename Functor &gt;</td>
|<a>wxCondError</a> |<a>Wait</a> (const Functor &amp;predicate)
| |等待直到条件变量发出信号，且与之关联的条件为真。这是一个方便的重载用来忽略假的唤醒当等待特定条件变为true时。<br/>这个函数相当于： while ( !predicate() ) { <a>wxCondError</a> e =<a>Wait</a>(); if ( e != <a>wxCOND_NO_ERROR</a> ) return e; } return <a>wxCOND_NO_ERROR</a>; 

{

if ( e != <a>wxCOND_NO_ERROR</a> )

}
<td colspan="2"> </td>
|<a>wxCondError</a> |<a>WaitTimeout</a> (unsigned long milliseconds)
| |等待直到条件被激发或超时时间到达。

 

4.wxSemaphore--信号量

 

 

<a>wxSemaphore</a>是一个计数器，用于限制并发访问共享资源的线程数。

该计数器始终在0和创建信号量期间指定的最大值之间。当计数器严格大于0时，调用<a>wxSemaphore :: Wait（）</a>将立即返回并递减计数器。一旦达到0，任何后续的对<a>wxSemaphore :: Wait</a>的调用，只有当信号量计数器再次变为严格的正值时，才会返回，因为调用<a>wxSemaphore :: Post</a>会增加计数器的结果。

一般来说，信号量对于限制只能同时被某些固定数量的客户端访问的共享资源的访问是有用的。例如，当建模酒店预订系统时，可以创建一个具有等于可用房间总数的计数器的信号量。每次保留一个房间时，通过调用<a>wxSemaphore :: Wait</a>来获取信号量，并且每次释放房间时，都应该通过调用<a>wxSemaphore :: Post</a>来释放信号量。

 
|<a>wxSemaError</a> |<a>Post</a> ()
| |增加信号量计数值并通知等待的线程里面的一个
<td colspan="2"> </td>
|<a>wxSemaError</a> |<a>TryWait</a> ()
| |与<a>Wait()</a>相似，但他会立即返回
<td colspan="2"> </td>
|<a>wxSemaError</a> |<a>Wait</a> ()
| |无限等待直到信号量计数值变为正值，稍后会减一并返回
<td colspan="2"> </td>
|<a>wxSemaError</a> |<a>WaitTimeout</a> (unsigned long timeout_millis)
| |与<a>Wait()</a>相似，但有超时限制

 

 

 

 

 

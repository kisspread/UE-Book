# StylusInputRealTimeStylus

> Windows RealTimeStylus COM API 后端模块

## 概述

`StylusInputRealTimeStylus` 是 StylusInput 的 Windows 后端实现，基于 Microsoft 的 **RealTimeStylus COM API**（也称为 Tablet PC API）。这是 Windows 上的**默认首选接口**。

RealTimeStylus 是微软为 Tablet PC 和数位板设备提供的 COM 接口，支持现代数位板设备（包括 Surface Pen、Wacom 数位板等）。它比 Wintab API 更现代，支持更多的笔属性。

## 技术细节

### 平台限制

- **仅限 Win64**
- **仅限编辑器**（EditorNoCommandlet）
- 加载阶段：PostDefault

### COM 插件架构

RealTimeStylus 使用 COM 插件模式。本模块实现了两个 COM 插件：

| COM 插件类 | 接口 | UE 线程映射 |
|---|---|---|
| `FRealTimeStylusPluginSync` | `IStylusSyncPlugin` | 游戏线程（同步） |
| `FRealTimeStylusPluginAsync` | `IStylusAsyncPlugin` | 异步线程 |

每个 `IStylusInputEventHandler` 注册到实例时，会根据 `EEventHandlerThread` 参数创建对应的 COM 插件：

- `EEventHandlerThread::OnGameThread` → 创建 `FRealTimeStylusPluginAsync`（COM 异步插件，但数据通过 `FTickableEditorObject` 转发到游戏线程）
- `EEventHandlerThread::Asynchronous` → 创建 `FRealTimeStylusPluginSync`（COM 同步插件，在 COM 线程上直接调用）

> 注意：命名有些反直觉——COM 的 "Sync" 插件实际上在 COM 线程上运行（对 UE 来说是异步的），而 COM 的 "Async" 插件通过 marshaling 在游戏线程上调用。

### COM 事件

插件接收以下 COM 事件：

- `StylusDown` / `StylusUp` — 笔尖触碰/离开
- `Packets` — 笔在板面上移动时的数据包
- `InAirPackets` — 笔在板面上方悬停时的数据包
- `StylusInRange` / `StylusOutOfRange` — 笔进入/离开检测范围
- `StylusButtonDown` / `StylusButtonUp` — 笔按钮按下/释放
- `TabletAdded` / `TabletRemoved` — 数位板连接/断开

### 源文件

| 文件 | 说明 |
|---|---|
| `RealTimeStylusInterface.h/cpp` | `IStylusInputInterface` 实现，注册/注销接口 |
| `RealTimeStylusInstance.h/cpp` | `IStylusInputInstance` 实现，管理 COM 对象生命周期 |
| `RealTimeStylusPluginSync.h/cpp` | `IStylusSyncPlugin` COM 同步插件 |
| `RealTimeStylusPluginAsync.h/cpp` | `IStylusAsyncPlugin` COM 异步插件 |
| `RealTimeStylusPluginBase.h/cpp` | 两个插件的共享基类 |
| `RealTimeStylusAPI.h/cpp` | RealTimeStylus DLL 加载和函数绑定 |
| `RealTimeStylusInterface.h/cpp` | COM 接口初始化 |
| `RealTimeStylusTabletContext.h` | 数位板上下文实现 |
| `RealTimeStylusStats.h` | 性能统计 |
| `RealTimeStylusUtils.h/cpp` | 工具函数（坐标转换等） |

### 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 基础库 |
| `Slate` | SWindow 引用 |
| `SlateCore` | Slate 核心 |
| `StylusInput` | 核心接口定义 |

### 注意事项

- 每个实例只能有一个事件处理器（每个线程类型一个 COM 插件）
- COM 插件使用 `IUnknown` 引用计数管理生命周期
- `FRealTimeStylusPluginSync` 实现了 `IMarshal` 的自由线程 marshaling
- 事件处理器必须快速返回，否则会阻塞后续事件处理

## 源码

[源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/StylusInput/Source/StylusInputRealTimeStylus)

# StylusInputDebugWidget

> 数位板输入调试/可视化控件模块

## 概述

`StylusInputDebugWidget` 提供一个 Slate 控件，用于实时可视化数位板输入数据。它在编辑器中显示一个绘画区域，可以展示笔触轨迹、压力变化等信息，是开发和调试数位板工具的有用辅助。

## 功能

- **实时绘画**：在控件区域内用笔绘画，显示笔触轨迹
- **压力可视化**：笔触粗细反映压力大小
- **数据面板**：显示当前数据包的所有属性值
- **接口切换**：可以在运行时切换不同的 stylus input 接口（RealTimeStylus / Wintab / NSEvent）
- **线程模式切换**：可以选择在游戏线程或异步线程上接收事件
- **调试消息**：显示底层接口的调试信息

## 技术细节

### 平台限制

- **全平台**（会自动使用当前平台可用的接口）
- **仅限编辑器**（EditorNoCommandlet）
- 加载阶段：PostEngineInit

### 架构

```
SStylusInputDebugWidget (主控件)
├── 接口选择菜单
├── 线程模式选择菜单
├── 数据面板（压力、坐标、倾斜等）
├── 调试消息面板
└── SStylusInputDebugPaintWidget (绘画区域)
```

### 事件处理器

模块提供了两种事件处理器实现：

| 类 | 线程 | 说明 |
|---|---|---|
| `FDebugEventHandlerOnGameThread` | 游戏线程 | 直接在游戏线程上接收并处理 |
| `FDebugEventHandlerAsynchronous` | 异步线程 | 通过 `TSpscQueue`（单生产者单消费者队列）转发到游戏线程，使用 `FTickableEditorObject` 每 tick 处理 |

### 绘画控件

`SStylusInputDebugPaintWidget` 使用 `TRingBuffer` 存储最近的绘画数据点，在 `OnPaint` 中绘制笔触轨迹。每个数据点包含：
- 位置（2D）
- 压力值
- 笔状态
- 时间戳

### 源文件

| 文件 | 说明 |
|---|---|
| `StylusInputDebugWidget.h/cpp` | 主调试控件 `SStylusInputDebugWidget` |
| `StylusInputDebugPaintWidget.h/cpp` | 绘画区域控件 `SStylusInputDebugPaintWidget` |
| `StylusInputDebugWidgetModule.cpp` | 模块注册，创建编辑器 Tab |

### 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 基础库 |
| `Engine` | 引擎核心 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心 |
| `StylusInput` | 核心接口 |
| `UnrealEd` | 编辑器框架（Tab 注册） |
| `WorkspaceMenuStructure` | 编辑器菜单结构 |

### 使用方法

1. 启用 StylusInput 插件
2. 在编辑器菜单中找到 Stylus Input Debug 面板
3. 用数位板笔在绘画区域中绘画
4. 观察数据面板中的实时数据

### 注意事项

- 当调试控件移动到不同的编辑器窗口时，需要重新获取 stylus input 实例（通过 `NotifyWidgetRelocated()`）
- 异步模式使用 SPSC 队列保证线程安全，但可能有微小延迟
- 绘画区域使用环形缓冲区，只保留最近的数据点

## 源码

[源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/StylusInput/Source/StylusInputDebugWidget)

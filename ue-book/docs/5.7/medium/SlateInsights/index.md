# Slate Insights

> Allows debugging of Slate via Unreal Insights

| 属性 | 值 |
|---|---|
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateInsights` (EditorAndProgram) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Slate/SlateInsights) | |

## 用途

Slate Insights 是一个将 Slate UI 框架的性能数据集成到 Unreal Insights 分析工具中的插件。它解决的核心问题是：**当你遇到 Slate UI 性能瓶颈时，如何精确定位是哪些 Widget 导致了卡顿**。

在没有这个插件之前，开发者只能通过 `stat slate` 命令获取粗粒度的统计信息。Slate Insights 通过 Unreal Trace 系统记录详细的 Slate 事件流（Widget 创建/销毁、Invalidation、Update/Paint 步骤等），并在 Unreal Insights 的 Timing 视图中以可视化 Track 的形式展示，使开发者可以像分析 CPU/GPU 性能一样分析 UI 性能。

插件仅在 UnrealInsights 程序中加载（通过 `SupportedPrograms` 和 `ProgramAllowList` 限制），不影响游戏运行时或编辑器的性能。

## 使用场景

- 你的编辑器或游戏 UI 出现卡顿，需要找出哪些 Widget 的 Paint/Layout 操作耗时过长
- 你想分析 Widget Invalidation 的传播链路，找出不必要的 Invalidation
- 你需要对比不同帧的 Slate 统计数据（Widget 数量、Tick 次数、Paint 次数等）
- 你想通过 Widget ID 反查其路径、生命周期和 Debug 信息

## C++ 用法

Slate Insights 是一个纯分析端插件，不提供运行时 API。它的使用方式是：

1. **采集端**：在游戏/编辑器中启用 Slate Trace 日志（`-trace=Slate` 或 `-trace=slatetrace`）
2. **分析端**：在 Unreal Insights 中打开对应的 `.utrace` 文件，Slate Insights 插件会自动注册自定义 Track

### Trace 事件类型

插件通过 `FSlateAnalyzer` 注册了以下 Trace 事件路由（均在 `"SlateTrace"` 通道下）：

| 事件名 | 说明 |
|---|---|
| `ApplicationTickAndDrawWidgets` | 每帧的 Slate 应用级统计（Widget 数、Tick/Paint/Invalidate 次数等） |
| `AddWidget` | Widget 被创建 |
| `WidgetInfo` | Widget 的元信息（路径、Debug 信息） |
| `RemoveWidget` | Widget 被销毁 |
| `WidgetUpdated` | Widget 被更新（耗时、影响的 Widget 数量、更新标志） |
| `WidgetInvalidated` | Widget 失效（原因：Layout/Paint/ChildOrder/Visibility 等） |
| `RootInvalidated` | 根 Widget 失效 |
| `RootChildOrderInvalidated` | 根 Widget 子节点顺序变化 |
| `InvalidationCallstack` | Invalidation 的调用栈（支持脚本追踪和 C++ 调用栈） |
| `WidgetUpdateSteps` | Widget 的 Paint 步骤详情（嵌套的 Paint 事件） |

### 头文件引入

由于这是分析端插件，通常不需要在自己的代码中直接引用。如果要扩展 Insights 的分析功能：

```cpp
#include "TraceServices/ModuleService.h"       // 实现 IModule
#include "Insights/ITimingViewExtender.h"       // 扩展 Timing 视图
#include "Insights/ViewModels/GraphTrack.h"     // 自定义图表 Track
```

### 模块注册模式

插件通过 `IModularFeatures` 注册两个扩展点：

```cpp
// 注册 Trace 分析模块（负责解析 Slate 事件并创建 Provider）
IModularFeatures::Get().RegisterModularFeature(
    TraceServices::ModuleFeatureName, &TraceModule);

// 注册 Timing 视图扩展器（负责添加自定义 Track 到 Timing 视图）
IModularFeatures::Get().RegisterModularFeature(
    UE::Insights::Timing::TimingViewExtenderFeatureName, &TimingViewExtender);
```

## 架构概览

插件的架构分为三层：

### 1. 数据层：FSlateProvider

`FSlateProvider` 实现 `TraceServices::IProvider` 接口，存储所有分析后的 Slate 数据：

- **Widget 生命周期**：通过 `FWidgetTimeline`（Interval Timeline）追踪每个 Widget 的创建到销毁时间
- **帧统计**：`FApplicationTickedTimeline` 记录每帧的 Widget 数量、Tick/Paint/Invalidate 计数
- **Widget 更新**：`FWidgetUpdatedTimeline` 记录每个 Widget 更新事件的耗时和影响范围
- **Invalidation**：`FWidgetInvalidatedTimeline` 记录每次失效事件及原因
- **Paint 步骤**：`FWidgetUpdateStepsTimeline` 记录嵌套的 Paint 操作

### 2. 分析层：FSlateAnalyzer

`FSlateAnalyzer` 实现 `UE::Trace::IAnalyzer` 接口，负责将原始 Trace 事件解析为结构化数据并写入 `FSlateProvider`。它处理上述 10 种事件类型。

### 3. 视图层

- **FSlateFrameGraphTrack**：在 Timing 视图中显示帧级 Slate 统计图表（Widget Count、Tick Count、Paint Count 等多条曲线）
- **FSlateWidgetUpdateStepsTimingTrack**：显示每个 Widget 的 Paint 操作耗时条
- **SSlateFrameSchematicView**：独立面板，显示选定帧的 Invalidated Widget 树和 Updated Widget 列表，支持按 Widget ID 搜索

## Timing 视图中的 Track

在 Unreal Insights 的 Timing Profiler 中，Slate Insights 通过 Filter 菜单添加了两个可切换的 Track：

### Frame Info Track（Slate Frame Info）

显示每帧的 Slate 统计数据图表，默认启用。包含以下系列（可通过右键菜单选择显示/隐藏）：

| 系列 | 默认显示 | 说明 |
|---|---|---|
| Widget Count | ❌ | 当前 Widget 总数 |
| Tick Count | ✅ | 被 Tick 的 Widget 数量 |
| Timer Count | ✅ | 有 Active Timer 的 Widget 数量 |
| Repaint Count | ❌ | 被重绘的 Widget 数量 |
| Paint Count | ✅ | 执行 Paint 的 Widget 数量 |
| Invalidate Count | ✅ | 被标记失效的 Widget 数量 |
| Root Invalidated Count | ✅ | 根 Widget 被标记失效的次数 |

支持两种布局模式（右键菜单切换）：
- **Overlay**：所有系列叠在一起
- **Stack**：每个系列独立一行（默认），可显示标签和数值范围

### Update Steps Track（Steps）

显示 Widget 的 Paint 操作时间条，默认隐藏（需通过 Filter 菜单的 "Update Steps" 开启）。每个事件显示 Widget 的 Debug Info 作为标签，支持嵌套深度展示。

## Slate Frame View 面板

通过 Frame Info Track 的右键菜单 → "View Properties" 打开。面板包含三个区域：

### Widget 搜索（可折叠）

输入 Widget ID（数字），显示：
- Widget ID、路径、Debug Info
- 创建时间、销毁时间

### Invalidation 列表

Tree View 形式展示当前帧内被 Invalidated 的 Widget：
- **Widget** 列：Widget 名称，有子项时显示展开箭头
- **Amount** 列：被 Invalidation 的次数
- **Reason** 列：用颜色方块显示 Invalidation 原因标志

Invalidation 原因标志（`EInvalidateWidgetReason`）：

| 标志 | 缩写 | 含义 |
|---|---|---|
| ChildOrder | C | 子节点添加/移除（隐含 Layout） |
| Layout | L | Widget 期望尺寸变化 |
| Paint | P | 需要重绘但不影响尺寸 |
| Volatility | V | 波动性变化 |
| RenderTransform | R | 渲染变换变化 |
| Visibility | V | 可见性变化（隐含 Layout） |
| AttributeRegistration | A | 属性绑定/解绑 |
| Prepass | P | 递归重新缓存子节点期望尺寸 |

右键菜单支持：
- **Search Widget**：在搜索框中查找选中的 Widget
- **Go to Root Widget**：定位到失效传播的根节点
- **View Script and Call Stack**：查看脚本追踪和 C++ 调用栈

### Update 列表

List View 形式展示当前帧内被 Updated 的 Widget：
- **Widget** 列：Widget 名称
- **Amount** 列：更新次数
- **Affected Count** 列：受影响的 Widget 数量
- **Duration** 列：更新耗时
- **Flag** 列：更新标志

更新标志（`EWidgetUpdateFlags`）：

| 标志 | 缩写 | 含义 |
|---|---|---|
| NeedsTick | T | Widget 被 Tick/更新 |
| NeedsActiveTimerUpdate | T | Widget 有 Active Timer |
| NeedsRepaint | P | Widget 脏了需要重绘 |
| NeedsVolatilePaint | V | Widget 是 Volatile 的需要重绘 |

支持按列排序，右键菜单可搜索 Widget。

## 模块依赖

所有依赖均为 `PrivateDependencyModuleNames`（插件内部使用，不对外暴露）：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `InputCore` | 输入系统 |
| `SlateCore` | Slate 核心（Widget 基础设施） |
| `Slate` | Slate UI 框架 |
| `TraceLog` | Trace 日志系统 |
| `TraceAnalysis` | Trace 分析框架 |
| `TraceServices` | Trace 服务（Provider/Analyzer 接口） |
| `TraceInsights` | Unreal Insights 主模块 |
| `TraceInsightsCore` | Insights 核心 API |
| `AssetRegistry` | 资产注册表 |
| `ApplicationCore` | 应用核心 |
| `SourceCodeAccess` | 源码访问（查看调用栈时跳转到源码） |
| `Engine` | 引擎（条件依赖，仅当 `bCompileAgainstEngine` 时） |

## 维护状态

### 近期更新

1. **`a1810e8`** (2024-06-27) — 修复 Insights 插件中的 API 废弃警告
   - Insights API 命名空间迁移后的适配工作

2. **`1d4beb2`** (2024-06-20) — TraceInsights 模块大规模重构
   - 新增 `TraceInsightsCore` 模块，将公共 API 迁移到 `UE::Insights` 命名空间
   - SlateInsights 适配新的模块结构和命名空间

3. **`e046478`** (2024-05-02) — SListView/STreeView ItemHeight 废弃
   - 非 SlateInsights 直接改动，但影响了相关 Widget 的实现方式

### 维护评价

- **创建于 2020 年**，约 6 年历史
- 最近一次实质性更新在 2024 年 6 月，主要是适配 Insights 模块重构，**不是新功能开发**
- 自 2024 年 6 月以来（约 2 年）没有实质性功能更新
- 插件功能已经相对完整和稳定，但部分功能存在注释掉的代码（如 `VolatilePaintCount`、Layout Events 过滤），暗示仍有未完成的特性
- **EnabledByDefault=false**，需要手动启用
- 作为纯开发工具插件，功能稳定，推荐在需要 Slate 性能分析时使用

⚠️ 注意：部分 Layout/Paint 过滤功能仍处于注释状态，Widget Update Steps Track 默认关闭。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Slate/SlateInsights)
- 官方文档：无（.uplugin 中 DocsURL 为空）

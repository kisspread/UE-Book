# Concert Insights Visualizer

> Analyses and provides visualization widgets for Concert message types in Unreal Insights.

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertInsightsVisualizer` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-06 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsVisualizer) | |

## 用途

ConcertInsightsVisualizer 是 Unreal Insights 的扩展插件，在 Insights 的 Timing View 中为 Concert（UE5 的多用户编辑系统）协议消息添加可视化轨道。

**解决的问题**：在多用户编辑场景中，多个编辑器实例通过 Concert 协议同步对象数据。当需要排查同步延迟、理解对象数据在各端之间的流转过程时，需要在 Unreal Insights 中看到这些事件的时间线。此插件将 Concert 的 `.utrace` 日志数据解析后，以可视化的 timeline 形式展现在 Insights 的 Timing Profiler 中。

**核心功能**：
- 解析 Concert 协议 trace 事件（`Init`、`ObjectTraceBegin`、`ObjectTraceEnd`、`ObjectTransmissionStart`、`ObjectTransmissionReceive`、`ObjectSink`）
- **聚合多个 `.utrace` 文件**：自动关联同一会话中其他机器录制的 trace 文件，实现跨机器的时间线对齐
- **跨机器时间同步**：通过 UTC 时间戳将不同机器的 trace 时间转换到主 trace 的时间轴上
- 在 Insights Timing View 中以分层轨道显示：对象序列 → 网络作用域（客户端/传输中）→ CPU 处理步骤

**注意**：此插件标记为 `IsExperimentalVersion=true`，且 `SupportedPrograms` 仅限 `UnrealInsights`（不是编辑器插件，是 Insights 程序的插件）。聚合功能默认通过 CVar `Insights.Concert.EnableGameThreadAggregation` 关闭，因为当前实现仅支持在游戏线程上运行，可能冻结 UI。

## 使用场景

- **多用户编辑延迟排查**：你在多用户编辑中发现同步延迟，需要看对象从一个客户端发送到另一个客户端的完整时间线（包括网络传输时间、各端处理时间）
- **Concert 协议调试**：你在开发 Concert 相关功能，需要验证对象复制的事件序列是否正确
- **跨机器性能分析**：你需要了解同一会话中各个编辑器实例的处理耗时，需要在同一个 Insights 视图中对齐多个 trace 文件

## 蓝图用法

此插件无蓝图接口。它是 Unreal Insights 程序的扩展，不暴露任何 `BlueprintCallable` 函数。使用方式是在 Unreal Insights 中打开 Concert 的 `.utrace` 文件后，Timing View 会自动显示 Concert 轨道。

## C++ 用法

此插件的典型使用场景不是作为库被其他模块引用，而是作为 Insights 的内置扩展。但如果你需要在 Insights 扩展开发中参考其架构，以下是一些关键类和用法。

### 头文件引入

```cpp
#include "IConcertInsightsVisualizerModule.h"
```

### 模块访问

```cpp
// 检查模块是否可用
if (UE::ConcertInsightsVisualizer::IConcertInsightsVisualizerModule::IsAvailable())
{
    // 获取模块实例
    UE::ConcertInsightsVisualizer::IConcertInsightsVisualizerModule& Module =
        UE::ConcertInsightsVisualizer::IConcertInsightsVisualizerModule::Get();
}
```

### 架构说明

插件的核心架构分为三层：

**1. 分析层（Trace Analysis）**
- `FProtocolEndpointAnalyzer`：从 `.utrace` 流中解析 `ConcertLogger` 事件，生成结构化的消息（`FInitMessage`、`FObjectTraceMessage` 等）
- `IProtocolDataTarget`：分析结果的接收接口，支持不同的数据目标
- `FProtocolDataQueue`：线程安全的队列，用于聚合分析线程与主线程之间的数据同步

**2. 数据聚合层（Aggregation）**
- `FTraceAggregator`：查找与主 trace 时间戳相近（±5秒）的其他 `.utrace` 文件，在独立线程上启动分析
- `FProtocolMultiEndpointProvider`：聚合多个端点的数据，计算跨机器的时间对齐，维护对象→序列→网络作用域→CPU处理步骤的层级数据结构
- `TimeSyncUtils::ConvertSourceToTargetTime`：通过 UTC 时间戳将不同机器的时间映射到主 trace 的时间轴

**3. 可视化层（Visualization）**
- `FConcertTimingViewExtender`：实现 `ITimingViewExtender` 接口，在 Insights 的 Timing View 中注册扩展
- `FConcertTimingViewSession`：每个 Insights 会话对应一个实例，管理轨道和过滤菜单
- `FProtocolTrack`：继承 `FTimingEventsTrack`，负责在 Insights 中绘制 Concert 事件轨道

**Insights Timing View 中的显示层级**：
```
[-------------------- FObjectSequence - ActorName - Sequence 1 -------------------]  ← 第1行
[------- Client 1 -------][---- Transmission ----][------- Client 2 -------]        ← 第2行
[CPU Step 1] [CPU Step 2]                            [CPU Step 1] [CPU Step 2]      ← 第3行+
```

### 跨机器时间同步算法

```cpp
// TimeSyncUtils::ConvertSourceToTargetTime 的核心逻辑
// 将 Source 时间轴上的事件时间转换到 Target 时间轴
//
// 全局时间轴:  0 1 2 3 4 5 6 7 8 9
// Target 时间:  [I n i t 5 6 7 x 9]    （TargetInitTime = 1）
// Source 时间:    - [1 I n i t 6 y 8]   （SourceInitTime = 2）
//
// 已知 Source 上的时间 y = 7，求 Target 上的 x
// x = ConvertSourceToTargetTime(TargetInitUtc, SourceInitUtc, 1, 2, 7) = 8

double TimeSyncUtils::ConvertSourceToTargetTime(
    const FDateTime& TargetInitUtc,   // 主 trace 的 Init 事件 UTC 时间
    const FDateTime& SourceInitUtc,   // 被聚合 trace 的 Init 事件 UTC 时间
    double TargetInitTime,            // 主 trace 上 Init 事件的相对时间
    double SourceInitTime,            // 被聚合 trace 上 Init 事件的相对时间
    double SourceTime                 // 要转换的时间（Source 时间轴）
)
{
    const FTimespan Delta = TargetInitUtc - SourceInitUtc;
    const double RelativeTime = SourceTime - SourceInitTime;
    const double TargetRelative = RelativeTime - Delta.GetTotalSeconds();
    return TargetInitTime + TargetRelative;
}
```

### 协议消息类型

| 消息类型 | 说明 |
|---|---|
| `FInitMessage` | 端点初始化信息，包含端点 ID、是否为服务器、客户端显示名、UTC 时间戳 |
| `FObjectTraceBeginMessage` | 对象处理开始，标记 CPU 处理步骤的起始 |
| `FObjectTraceEndMessage` | 对象处理结束，标记 CPU 处理步骤的结束 |
| `FObjectTransmissionStartMessage` | 对象开始网络传输，关闭当前端点的网络作用域 |
| `FObjectTransmissionReceiveMessage` | 对象接收完成，开启接收端的网络作用域 |
| `FObjectSinkMessage` | 对象被消费（sink），标记序列结束 |

### 作用域标识体系

```cpp
// 三级作用域标识，逐级嵌套
FObjectScopeInfo      // ProtocolId + ObjectPath：标识一个协议中的一个对象
  └─ FSequenceScopeInfo  // + SequenceId：标识该对象的一次更新序列
       └─ FEndpointScopeInfo  // + EndpointId：标识该序列中某个端点的处理
```

### 测试用例

```cpp
// 来源: Source/.../Private/Tests/TimeSyncUtils.spec.cpp
// 测试跨机器时间同步算法

// 模拟场景：
// Target 的 Init 事件在 UTC 12:00:01，本地时间 = 1s
// Source 的 Init 事件在 UTC 12:00:03，本地时间 = 2s
// Source 上某事件发生在本地时间 = 7s
// 期望转换到 Target 的本地时间 = 8s

const FDateTime TargetInitUtc(2024, 2, 22, 12, 0, 1);
const FDateTime SourceInitUtc(2024, 2, 22, 12, 0, 3);
constexpr double TargetInitTime = 1;
constexpr double SourceInitTime = 2;
constexpr double SourceTime = 7;

const double ConvertedTime = TimeSyncUtils::ConvertSourceToTargetTime(
    TargetInitUtc, SourceInitUtc, TargetInitTime, SourceInitTime, SourceTime
);
// ConvertedTime == 8.0
```

## Demo 示例

此插件没有可独立运行的 demo，因为它本身是 Unreal Insights 的扩展。要体验它的功能：

1. 在 `DefaultEngine.ini` 中启用插件：
```ini
[/Script/Insights.Settings]
bEnableConcertInsightsVisualizer=True
```

2. 或通过控制台变量启用聚合功能：
```
Insights.Concert.EnableGameThreadAggregation true
```

3. 在多用户编辑会话中录制 `.utrace` 文件，然后在 Unreal Insights 中打开主 trace 文件，Timing View 中将自动出现 "Concert" 轨道。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础模块（公开依赖） |
| `CoreUObject` | UObject 系统支持（FSoftObjectPath 等） |
| `Projects` | 模块管理 |
| `Slate` / `SlateCore` | UI 框架，用于 Insights 中的轨道绘制和过滤菜单 |
| `TraceAnalysis` | Unreal Insights 的 trace 分析框架（`Trace::IAnalyzer`） |
| `TraceInsights` | Insights 集成，提供 StoreClient 等 |
| `TraceServices` | Trace 服务层（`IAnalysisSession`、Timeline 模型等） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-09-12 | `ce6ff39` | 修复 `FTSTicker::RemoveTicker` 的 `nodiscard` 警告 | 编译器警告修复，无功能变化 |
| 2024-07-31 | `3d86248` | 修复聚合功能拖慢 Insights 的问题 | 引入 CVar `Insights.Concert.EnableGameThreadAggregation`，默认关闭聚合以避免 UI 冻结 |
| 2024-06-27 | `de0f403` | 修复缺失的版权注释模板 | 格式修复 |

### 维护评价

- **创建时间**：2024-05-06，约 2 年历史
- **维护状态**：**维护不活跃**。自创建以来仅有 3 次提交（含 1 次编译警告修复、1 次性能问题缓解、1 次格式修复），无功能性更新
- **已知限制**：
  - 标记为实验性（`IsExperimentalVersion=true`）
  - 聚合功能仅支持在游戏线程运行，默认禁用
  - 跨机器 trace 关联基于时间戳近似匹配（±5 秒），不是精确的 session ID 匹配（代码中有 TODO 标记待改进）
  - 仅支持已完成的 trace 文件，不支持实时 trace
- **推荐**：仅推荐用于调试 Concert 协议同步问题。作为实验性功能，生产环境中不应依赖它。Epic 的 TODO 注释暗示未来可能用 session ID 替代时间戳近似匹配，但目前没有进展。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsVisualizer)
- [ConcertInsightsClient](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsClient)（兄弟模块，Insights 客户端侧的 Concert 集成）
- [ConcertInsightsCore](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsCore)（兄弟模块，核心数据结构）
- [ConcertSync](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertSync)（Concert 同步系统）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsVisualizer/Source/ConcertInsightsVisualizer/Private/Tests/TimeSyncUtils.spec.cpp)

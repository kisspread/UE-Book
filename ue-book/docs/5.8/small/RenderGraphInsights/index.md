# RDG Insights

> Allows debugging of RDG via Unreal Insights

| 属性 | 值 |
|---|---|
| 中文名 | RDG调试 |
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RenderGraphInsights` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-02-03 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/RenderGraphInsights) | |

## 用途

RenderGraphInsights 是一个专门用于 **Unreal Insights** 工具的插件，它为 **渲染依赖图 (Render Dependency Graph, RDG)** 提供了深度调试和可视化能力。RDG 是 Unreal Engine 5 的核心渲染架构，用于自动化管理 Pass 的调度、资源生命周期和依赖关系。

这个插件解决了以下问题：
1.  **可视化 RDG 图结构**：将复杂的 RDG 执行图（包括 Scope、Pass、纹理和缓冲区）转换为时间轴上的直观图形，帮助开发者理解渲染管线的执行顺序。
2.  **调试资源生命周期**：清晰地显示每个纹理和缓冲区（包括瞬态和外部资源）的创建、使用和销毁时间点，以及它们的分配状态（如是否被剔除、是否使用瞬态缓存）。
3.  **分析性能瓶颈**：通过查看每个 Pass 的执行时间、并行计算（Async Compute）情况以及资源大小，定位渲染管线中的性能热点。
4.  **检查资源关系**：通过可视化的连线（Splines），展示资源（如纹理）在不同 Pass 之间的使用和所有权转移关系。

## 使用场景

-   你在开发一个使用 RDG 的自定义渲染 Pass，需要验证其在渲染管线中的执行顺序和依赖是否正确。
-   游戏中出现了渲染伪影或资源错误，你需要追踪特定纹理或缓冲区在帧内的生命周期，确认其是否被意外过早释放或复用。
-   你正在优化渲染性能，需要分析哪些 Pass 耗时过长，或者哪些大型资源导致了显存压力。
-   你想理解引擎或项目中某个复杂渲染功能（如体积雾、光线追踪）在 RDG 层面的具体实现流程。

## 蓝图用法

无（非蓝图插件）。此插件不提供任何蓝图可调用的节点或属性，它完全作为 Unreal Insights 的扩展存在。

## C++ 用法

此插件主要作为 Insights 的 Trace 分析模块运行，不直接向游戏运行时或编辑器暴露公共 C++ API。它的核心功能是通过 Unreal Insights 的扩展接口实现的。

### 头文件引入

通常，你不需要直接引入此插件的头文件，除非你正在编写 Insights 的扩展。

### 基本用法（注册 Trace 模块）

插件的核心是注册了一个名为 `rdgtrace` 的 Trace 分析模块。在 Insights 工具中，可以通过命令行参数 `-trace=rdgtrace` 启用 RDG 事件的捕获。
```cpp
// 注册过程发生在 FRenderGraphTraceModule::GetModuleInfo 中
// 命令行参数： -trace=rdgtrace
```
**来源文件**：`Source/RenderGraphInsights/Private/RenderGraphTraceModule.h`

### 进阶用法（分析事件）

插件定义了一系列 Trace 事件用于收集 RDG 数据：
```cpp
// 定义路由ID，用于在分析器中区分不同事件
enum : uint16
{
    RouteId_Graph,       // RDG 图开始
    RouteId_GraphEnd,    // RDG 图结束
    RouteId_Scope,       // 作用域
    RouteId_Pass,        // Pass
    RouteId_Buffer,      // 缓冲区资源
    RouteId_Texture      // 纹理资源
};
```
**来源文件**：`Source/RenderGraphInsights/Private/RenderGraphAnalyzer.h`

## Demo 示例

以下是一个最小化的示例，展示如何为你的自定义 RDG Pass 添加 Trace 事件，以便在 RDG Insights 中进行可视化（需要引擎支持）。

### MyRDGPass.h
```cpp
#pragma once
#include "RenderGraphEventUtils.h"
```

### MyRDGPass.cpp
```cpp
#include "MyRDGPass.h"
#include "RenderGraphUtils.h"

class FMyRDGPass : public FRenderGraphPass
{
public:
    virtual void Execute(FRDGBuilder& GraphBuilder, const FSceneView& View) override
    {
        // 使用 RDG 作用域宏，这会在 RDG Insights 中显示为一个层级结构
        RDG_EVENT_SCOPE(GraphBuilder, "MyCustomRDGPass");

        // 使用 RDG Pass 宏，这会注册一个具体的 Pass 事件
        RDG_PASS_EVENT(GraphBuilder, MyActualPass);

        // ... 你的 Pass 实现 ...
        // 例如，创建并绑定纹理
        FRDGTextureDesc TextureDesc = /* ... */;
        FRDGTextureRef MyTexture = GraphBuilder.CreateTexture(TextureDesc, TEXT("MyTexture"));
        GraphBuilder.EnqueueRenderPass(/* ... */);
    }
};
```
当你捕获带有 `rdgtrace` 通道的 Trace 时，就可以在 Unreal Insights 的 RDG 选项卡中看到 "MyCustomRDGPass" 作用域和 "MyActualPass" Pass，以及 "MyTexture" 纹理资源的生命周期。

## 模块依赖

从源码结构和插件功能推断，此插件有以下关键依赖。省略了常见的 Core, Engine 等模块。

| 模块 | 用途 |
|---|---|
| `RenderCore` | 核心渲染功能，提供 RDG 基础类型和构建器 |
| `TraceServices` | 提供 Trace 分析和数据提供者的基础设施 |
| `Insights` | Unreal Insights 工具的运行时和 UI 框架 |
| `RHICore` | 提供 RHI 管道、瞬态资源统计等定义 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-02-03 | `01fea416` | Added missing includes for some enums used to call StaticEnum. | 为用于调用 `StaticEnum` 的枚举添加了缺失的头文件包含。 |
| 2026-01-30 | `bbcb0b5f` | Undo changelist 50351065 | 撤销了变更列表 50351065。 |
| 2026-01-30 | `efe24135` | Added a UE::CUEnum concept for testing if a type is a UEnum. This requires testing for a legal Stat | 添加了 `UE::CUEnum` 概念用于测试类型是否为 `UEnum`。这需要测试一个合法的 `Stat`。 |
| 2024-10-23 | `820f2b31` | [Insights] Fixed crash in RenderGraphInsights plugin. Added support for late connect (i.e. enabling the plugin after the application has started). | 修复了 RenderGraphInsights 插件中的崩溃。添加了对后期连接的支持（即在应用程序启动后启用插件）。 |

### 维护评价

该插件创建于 2021 年，约有 4 年历史。最近的更新（2024年10月）修复了一个崩溃并添加了新功能（后期连接），表明它仍在**维护中**。然而，此后的提交都是小的编译警告修复或内部调整，没有新的用户可见功能。作为 Epic 官方维护的 Insights 插件，它通常会随着引擎版本更新而得到维护，但可能不会频繁添加新特性。

**综合评价**：插件功能稳定，是调试 RDG 的重要工具。目前没有废弃迹象，但由于功能相对专一且成熟，更新频率不高。对于需要深入调试 RDG 的开发者，它是**推荐使用**的官方工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/RenderGraphInsights)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests)（通常引擎测试位于此目录下，需根据具体插件搜索）
# RDG Insights

> Allows debugging of RDG via Unreal Insights

| 属性 | 值 |
|---|---|
| 中文名 | 渲染图洞察 |
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RenderGraphInsights` (EditorAndProgram) |
| 实验性 | 否 |
| 创建时间 | 2021-02-03 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/RenderGraphInsights) | |

## 用途

该插件为 Unreal Insights 性能分析工具扩展了对 Render Dependency Graph (RDG) 的调试和可视化能力。它通过实现一个 Trace 分析器 (`FRenderGraphAnalyzer`) 和一个 Provider (`FRenderGraphProvider`)，能够捕获和解析运行时或分析会话中 RDG 的执行信息，并将这些信息（如 Graph、Pass、Scope、Texture、Buffer 资源等）集成到 Insights 的 Timing 视图中。其主要目的是帮助开发者分析和优化渲染管线的性能、理解 Pass 的执行顺序和依赖关系、以及调试资源（特别是 Transient 资源）的分配与生命周期问题。

## 使用场景

- 当你需要分析一个复杂场景的渲染性能瓶颈时，可以通过此插件在 Insights 中直观地查看各个 Render Pass 的耗时、执行顺序和并行情况。
- 在优化渲染内存时，你可以利用它可视化 Transient 资源的分配、复用和释放过程，找出内存峰值或泄漏问题。
- 当渲染结果出现错误（如 Pass 执行顺序混乱、资源引用错误）时，可以通过 RDG 可视化图表来调试 Pass 之间的依赖关系。

## 蓝图用法

此插件为 Unreal Insights 的内部扩展，不包含可直接在蓝图中使用的 `UFUNCTION` 节点。其功能主要在 Unreal Insights 应用程序的图形界面中体现。

## C++ 用法

此插件作为 Insights 的扩展模块工作，不提供直接的运行时或编辑器 C++ API 供游戏代码调用。其核心是通过 `TraceServices::IModule` 和 `UE::Insights::Timing::ITimingViewExtender` 接口集成到 Insights 框架中。对 RDG 数据的解析和可视化逻辑封装在 `Private` 目录下。

### 模块入口

插件的模块入口是 `FRenderGraphInsightsModule`，它在启动时注册 Trace 模块和 Timing 视图扩展器。
```cpp
// Source/RenderGraphInsights/Private/RenderGraphInsightsModule.h
class FRenderGraphInsightsModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
private:
    FRenderGraphTraceModule TraceModule;
    FRenderGraphTimingViewExtender TimingViewExtender;
};
```

### Trace 分析与数据提供

`FRenderGraphAnalyzer` 负责解析来自 RDG 的 Trace 事件，`FRenderGraphProvider` 则将分析后的数据以 `TIntervalTimeline` 的形式提供给 Insights 的 Timing 视图进行显示。
```cpp
// Source/RenderGraphInsights/Private/RenderGraphAnalyzer.h
class FRenderGraphAnalyzer : public UE::Trace::IAnalyzer
{
public:
    FRenderGraphAnalyzer(TraceServices::IAnalysisSession& InSession, FRenderGraphProvider& InRenderGraphProvider);
    virtual bool OnEvent(uint16 RouteId, EStyle Style, const FOnEventContext& Context) override;
    // ...
};

// Source/RenderGraphInsights/Private/RenderGraphProvider.h
class FRenderGraphProvider : public TraceServices::IProvider
{
public:
    using TGraphTimeline = TraceServices::TIntervalTimeline<TSharedPtr<FGraphPacket>>;
    const TGraphTimeline& GetGraphTimeline() const;
    // ...
};
```

## Demo 示例

不适用。此插件的功能通过 Unreal Insights 工具界面提供，没有独立的可运行示例项目。要测试此插件，你需要：
1.  运行你的项目或一个启用 RDG 的引擎可执行文件。
2.  确保连接了 Unreal Insights (`-trace=rdg,frame,cpu`)，其中 `rdg` 是此插件注册的通道名。
3.  打开 Unreal Insights 应用程序，加载捕获的 Trace 文件。
4.  在 Timing 视图中，右键点击轨道区域，在弹出的菜单中应能看到“Render Graph”相关的选项来启用或过滤 RDG 轨道。

## 模块依赖

无特殊依赖（仅标准 Insights/TraceServices 框架模块）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量隐式转换为浮点数产生的编译警告。 |
| 2026-02-03 | `01fea416` | Added missing includes for some enums used to call StaticEnum. | 添加了缺失的头文件，以修复调用 `StaticEnum` 时依赖的枚举类型前向声明问题。 |
| 2026-01-30 | `bbcb0b5f` | Undo changelist 50351065 | 撤销了变更列表 50351065 的改动。 |
| 2024-10-23 | `820f2b31` | [Insights] Fixed crash in RenderGraphInsights plugin. Added support for late connect (i.e. enabling | [Insights] 修复了 RenderGraphInsights 插件中的一个崩溃。增加了对“后期连接”（即在跟踪开始后启用 RDG 通道）的支持。 |

### 维护评价

该插件创建于 2021 年，最近一次实质性更新（修复崩溃并增加新功能）发生在 2024 年 10 月，之后的更新主要是编译兼容性修复。作为 Epic Games 官方维护的 Insights 扩展，其稳定性有保障。虽然更新频率不高，但作为底层调试工具，它随着引擎 RDG 模块的发展而维护。**目前状态为“维护中”，推荐在需要进行 RDG 性能分析和调试时使用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/RenderGraphInsights)
- [官方文档]() （无）
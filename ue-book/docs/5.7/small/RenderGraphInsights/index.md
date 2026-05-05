# RDG Insights

> Allows debugging of RDG via Unreal Insights

| 属性 | 值 |
|---|---|
| 分类 | Insights |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | RenderGraphInsights (EditorAndProgram) |
| 创建时间 | 2021-02-03 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/RenderGraphInsights) | |

## 用途

RDG Insights 是一个 Unreal Insights 扩展插件，为 **Render Dependency Graph (RDG)** 提供可视化调试和分析功能。

RDG 是 UE5 的核心渲染框架，负责管理渲染 Pass 之间的资源依赖关系。当渲染出现问题（如资源生命周期错误、性能瓶颈、不必要的同步点）时，传统工具很难直观地看到整个 RDG 图的执行情况。

这个插件在 Unreal Insights 的 Timing 视图中添加了一个专用的 **RDG Track**，可以：
- 可视化每个 RDG Graph 的完整执行结构（Scopes、Passes、资源）
- 显示 Texture 和 Buffer 的生命周期（创建到销毁的时间跨度）
- 区分不同类型的资源（External、Transient、Extracted、Pooled）
- 显示 Transient Memory 的分配和释放情况
- 标记 Async Compute 和 Parallel Execute 相关的 Pass
- 通过过滤器按资源类型、名称、大小等条件筛选

## 使用场景

- 你在优化渲染性能，需要查看哪些 RDG Pass 耗时最长 → 使用 RDG Insights 的 Timing 视图
- 你怀疑某个 Texture/Buffer 的生命周期过长导致显存浪费 → 查看资源时间线
- 你需要确认 Transient Resource 是否正确地被复用 → 切换到 Transient Memory 可视化模式
- 你在调试 Async Compute 的 Pass 调度问题 → 关注 Pass 的 Pipeline 标记
- 你需要分析 RDG Graph 的 Scope 嵌套结构 → 查看 Scope 层次视图

## 使用方法

### 启用 Trace Channel

RDG Insights 通过 Unreal Trace 系统工作，需要启用 `RDG` trace channel。

**方式一：启动参数**

```bash
UnrealEditor.exe -trace=rdgtrace
```

**方式二：运行时连接**

支持 Late Connect（运行时连接），可以在编辑器运行后通过 Unreal Insights 客户端连接并启用 RDG channel。

### 在 Unreal Insights 中查看

1. 启动 Unreal Insights (`UnrealInsights.exe`)
2. 加载包含 RDG trace 数据的 `.utrace` 文件，或连接到正在运行的编辑器
3. 切换到 **Timing Insights** 视图
4. 在 Track 列表中找到 **RDG** track（可通过 Filter 菜单显示/隐藏）

### Track 内容说明

RDG Track 显示以下信息：

| 元素 | 说明 |
|---|---|
| **Graph** | 整个 RDG Graph 的执行时间跨度 |
| **Scope** | 嵌套的渲染作用域（如 Lighting、BasePass 等） |
| **Pass** | 单个渲染 Pass，纵向贯穿整个 Track（列状） |
| **Texture** | 纹理资源的生命周期条 |
| **Buffer** | 缓冲区资源的生命周期条 |

### 资源过滤

通过 Track 的 Filter 菜单可以控制显示的资源类型：

| 过滤选项 | 说明 |
|---|---|
| Textures | 显示/隐藏纹理资源 |
| Buffers | 显示/隐藏缓冲区资源 |
| Transient | 显示/隐藏瞬态资源 |
| External | 显示/隐藏外部资源 |
| Internal | 显示/隐藏内部资源 |
| Extracted | 显示/隐藏被提取的资源 |
| Pooled | 显示/隐藏池化资源 |
| Tracked | 显示/隐藏被追踪的资源 |

### 资源排序方式

| 排序方式 | 说明 |
|---|---|
| Creation | 按创建顺序 |
| LargestSize | 按大小降序 |
| SmallestSize | 按大小升序 |
| StartOfLifetime | 按生命周期开始时间 |
| EndOfLifetime | 按生命周期结束时间 |

### 资源着色方式

| 着色方式 | 说明 |
|---|---|
| Name | 按资源名称着色 |
| Type | 按资源类型着色 |
| Size | 按资源大小着色（颜色深浅表示大小） |
| TransientCache | 按 Transient Cache 命中状态着色 |

### 可视化模式

| 模式 | 说明 |
|---|---|
| Resources | 标准资源生命周期视图 |
| TransientMemory | Transient 内存分配视图，显示内存范围和分配偏移 |

## 蓝图用法

本插件不提供蓝图接口。它是一个纯 Editor/Program 类型的 Insights 扩展插件，仅通过 Unreal Insights 的 UI 进行交互。

## C++ 用法

本插件不暴露公共 C++ API。它的所有类都在 `Private` 目录下，作为 Unreal Insights 的 Modular Feature 注册。

### 命令行参数

要从代码中启用 RDG trace：

```cpp
// RDG trace 的命令行参数由 FRenderGraphTraceModule 提供
// 对应的 channel 名称为 "RDG"，命令行参数为 "rdgtrace"
// 在启动时通过 -trace=rdgtrace 启用
```

### 架构概览

插件的核心架构由以下组件组成：

```
FRenderGraphInsightsModule (模块入口)
├── FRenderGraphTraceModule (Trace 分析模块)
│   ├── FRenderGraphProvider (数据提供者)
│   └── FRenderGraphAnalyzer (Trace 事件分析器)
└── FRenderGraphTimingViewExtender (Timing 视图扩展)
    └── FRenderGraphTimingViewSession (会话管理)
        └── FRenderGraphTrack (RDG Track 渲染)
```

### Trace 事件

`FRenderGraphAnalyzer` 接收以下 Trace 事件（来自 `RDGTrace` channel）：

| 事件 | 路由 | 说明 |
|---|---|---|
| `GraphMessage` | RouteId_Graph | RDG Graph 开始 |
| `GraphEndMessage` | RouteId_GraphEnd | RDG Graph 结束 |
| `ScopeMessage` | RouteId_Scope | 作用域事件 |
| `PassMessage` | RouteId_Pass | 渲染 Pass 事件 |
| `TextureMessage` | RouteId_Texture | 纹理资源事件 |
| `BufferMessage` | RouteId_Buffer | 缓冲区资源事件 |

## 模块依赖

本插件的所有依赖都是 Private，使用者无需额外依赖。以下是插件内部依赖的模块：

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | 对象系统 |
| `RenderCore` | 渲染核心（RDG 相关类型） |
| `RHI` | RHI 层（TransientResourceAllocator） |
| `SlateCore` | Slate UI 核心 |
| `Slate` | Slate UI 框架 |
| `TraceLog` | Trace 日志系统 |
| `TraceAnalysis` | Trace 分析框架 |
| `TraceServices` | Trace 服务（Provider/Module 注册） |
| `TraceInsights` | Insights UI 扩展接口 |
| `TraceInsightsCore` | Insights 核心组件 |
| `InputCore` | 输入系统 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2024-10-23 | `820f2b3120c9` | Fixed crash in RenderGraphInsights plugin. Added support for late connect. | **Bug 修复 + 功能增强**：修复了崩溃问题，新增 Late Connect 支持，允许在运行时启用 RDGTrace channel |
| 2024-09-03 | `443f6d333168` | Implemented asynchronous task support for RDG execution lambdas. | **RDG 核心改动**（非 Insights 直接相关）：为 RDG 执行引入异步任务支持 |
| 2024-06-27 | `a1810e8063ad` | Enabled deprecation warnings for API moved in another namespace. Fixed deprecation warnings. | **维护性更新**：修复 API 命名空间迁移导致的废弃警告 |

### 维护评价

- **年龄**: 约 5 年（2021-02 创建），属于较成熟的插件
- **最近更新**: 最近一次实质性更新在 2024-10，包含 bug 修复和功能增强
- **维护状态**: **活跃维护** — 最近 6 个月内有功能性更新
- **已知限制**: 
  - 仅在 `UnrealInsights` 程序中加载（`ProgramAllowList: ["UnrealInsights"]`）
  - 需要通过 trace channel 显式启用 RDG 数据采集
  - 所有类均为 Private，不提供公共 API
- **推荐程度**: **推荐使用** — 这是调试 RDG 渲染问题的官方工具，由 Epic 直接维护，功能完善且仍在持续更新

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/RenderGraphInsights)
- 官方文档: 无（.uplugin 中 DocsURL 为空）
- RDG 核心源码: `Engine/Source/Runtime/RenderCore/Public/RenderGraphResources.h`

# Trace Source Filters

> Source data filtering for Unreal Insights.

| 属性 | 值 |
|---|---|
| 中文名 | 追踪源过滤 |
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器UI组件、过滤器逻辑） |
| 模块 | `SourceFilteringCore` (Runtime), `SourceFilteringTrace` (Runtime), `SourceFilteringEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-10-30 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/TraceSourceFiltering) | |

## 用途

Trace Source Filters 插件为 Unreal Insights 性能分析工具提供了强大的数据源过滤能力。它解决的核心问题是：在复杂的性能分析场景中，Insights 会收集海量的追踪数据，导致分析变得困难且低效。

该插件允许开发者和性能分析师在运行时或分析会话中，精细地控制哪些数据源（Source）的数据需要被记录和显示。通过过滤掉不相关的追踪事件（如特定世界、特定类型的Actor、特定蓝图类等），可以显著减少数据量，提高分析效率，并快速定位性能瓶颈。它将 Insights 从一个被动的数据查看器，升级为主动的性能分析工作流工具。

## 使用场景

- **大型开放世界项目性能分析**：当你的项目包含多个世界（如持久关卡、子关卡、过渡关卡）时，你只想分析当前游戏主世界的性能数据，而忽略编辑器预览世界、流式加载过渡世界的噪音。
- **复杂蓝图性能优化**：当你怀疑某个特定蓝图类或蓝图子类导致了性能问题时，可以过滤只追踪该类及其派生类的事件，忽略其他所有蓝图。
- **关注特定系统**：你正在调试物理系统，希望只显示与物理碰撞和模拟相关的追踪事件，过滤掉渲染、音频、AI等系统的事件。
- **对比分析**：在优化前后，通过保存和加载不同的过滤器预设（Presets），快速应用相同的过滤条件进行数据对比。

## 蓝图用法

该插件主要服务于编辑器内的 Unreal Insights 面板，不直接暴露蓝图节点。其核心交互是通过 Slate UI 在 Insights 窗口中完成的。

### 核心UI与交互

| 组件 | 说明 |
|---|---|
| `STraceSourceFilteringWidget` | Insights 中的过滤器主面板，整合了世界、类和用户自定义过滤器。 |
| `SWorldTraceFilteringWidget` | 用于管理 UWorld 过滤器的子面板，可控制哪些世界输出数据。 |
| `SClassTraceFilteringWidget` | 用于管理基于类（Class）的过滤器的子面板，可过滤特定类型的 Actor。 |
| `SUserTraceFilteringWidget` | 用于管理用户自定义过滤器（Data Source Filters）的子面板，支持过滤器集合（Filter Sets）和拖拽操作。 |
| `FFilterDragDropOp` | 支持在过滤器树视图中拖拽移动过滤器，以重新组织过滤器集合。 |

### 使用示例（Slate UI 描述）

1. 打开 **Unreal Insights** 窗口。
2. 连接到一个运行中的应用程序或加载一个 .utrace 文件。
3. 在 Insights 侧边栏中，找到并切换到 **"Source Filtering"** 标签页。
4. 在 **"World Filtering"** 区域，勾选或取消勾选特定的 UWorld，以控制其是否输出追踪数据。
5. 在 **"Class Filtering"** 区域，点击 **"+"** 按钮添加一个类（如 `BP_MyCharacter`），并可选地勾选 “Include Derived Classes”。
6. 在 **"User Filters"** 区域：
   - 点击 **"+"** 按钮，从列表中选择一个预定义的 `UDataSourceFilter`（如“Physics Collision Filter”）。
   - 可以通过拖拽将单个过滤器组合成 **Filter Set (AND/OR)**。
   - 通过右键上下文菜单管理过滤器（启用/禁用、重置、保存为预设）。

## C++ 用法

该插件的公共 API 较少，主要设计为在编辑器模块内使用。以下是从源码中提取的核心接口和用法。

### 头文件引入

```cpp
#include "Insights/ViewModels/FilterObject.h" // 包含 IFilterObject 接口
#include "Insights/ViewModels/ISessionSourceFilterService.h" // 核心服务接口
```

### 基本用法

主要通过 `ISessionSourceFilterService` 接口与过滤系统交互。以下是管理过滤器的示例。

**来源文件**: `Source/SourceFilteringEditor/Private/EditorSessionSourceFilterService.h`

```cpp
// 假设你已经有一个 TSharedPtr<ISessionSourceFilterService> FilterService 实例

// 1. 添加一个自定义数据源过滤器（需要知道其类名）
FString FilterClassName = TEXT("/Game/MyFilters/BP_FootstepSoundFilter.BP_FootstepSoundFilter_C");
FilterService->AddFilter(FilterClassName);

// 2. 添加一个基于Actor类的过滤器
FString ActorClassName = TEXT("BP_InteractableActor");
FilterService->AddClassFilter(ActorClassName);

// 3. 设置一个世界（通过哈希标识）是否可追踪
TArray<TSharedPtr<FWorldObject>> WorldObjects;
FilterService->GetWorldObjects(WorldObjects);
if (WorldObjects.Num() > 0)
{
    FilterService->SetWorldTraceability(WorldObjects[0].ToSharedRef(), false); // 禁用第一个世界的追踪
}

// 4. 重置所有过滤器
FilterService->ResetFilters();
```

### 进阶用法

组合使用过滤器集合和事件监听。

**来源文件**: `Source/SourceFilteringEditor/Private/ISessionSourceFilterService.h`, `Source/SourceFilteringEditor/Private/EditorSessionSourceFilterService.h`

```cpp
// 创建过滤器集合
void CreateAdvancedFilterSet(TSharedRef<ISessionSourceFilterService> FilterService)
{
    // 步骤1: 添加两个过滤器
    FilterService->AddFilter(TEXT("FilterA_ClassName"));
    FilterService->AddFilter(TEXT("FilterB_ClassName"));

    // 步骤2: 获取当前已添加的过滤器对象（通常通过树视图数据构建器）
    // 此处为伪代码，实际需要通过 PopulateTreeView 获取
    TSharedPtr<IFilterObject> FilterA = /* ... */;
    TSharedPtr<IFilterObject> FilterB = /* ... */;

    // 步骤3: 将这两个过滤器组合成一个 AND 集合
    FilterService->MakeFilterSet(FilterA.ToSharedRef(), FilterB.ToSharedRef());

    // 步骤4: 监听过滤状态的变化
    FilterService->GetOnSessionStateChanged().AddLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("Insights过滤器状态已更新！"));
        // 在这里可以触发UI刷新或其他逻辑
    });

    // 步骤5: 通过过滤器集合模式进行精细控制
    // EFilterSetMode::And, EFilterSetMode::Or
    FilterService->SetFilterSetMode(FilterA.ToSharedRef(), EFilterSetMode::Or);
}
```

## Demo 示例

该插件本身是编辑器工具，不包含可独立编译的运行时示例。其最佳“示例”就是其自身的 `ISessionSourceFilterService` 实现（`FEditorSessionSourceFilterService`），它展示了如何构建一个完整的过滤会话服务。

## 模块依赖

从各模块的 `Build.cs` 文件分析，该插件依赖以下模块。已省略 Core, CoreUObject, Engine, Slate, SlateCore 等常见依赖。

| 模块 | 用途 |
|---|---|
| `TraceSourceFiltering` | 核心的源码过滤逻辑和数据结构。 |
| `TraceInsights` | Unreal Insights 的核心框架和UI。 |
| `GameplayInsights` | 提供 Gameplay 相关的洞察数据和接口。 |
| `Slate`, `SlateCore` | (常见，但本插件大量使用) 构建复杂的过滤器编辑器 UI。 |
| `PropertyEditor` | (常见，但本插件用于显示过滤器实例的详细属性视图)。 |
| `TraceServices` | 与底层的追踪会话服务通信。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译器警告。 |
| 2026-04-29 | `bef86caa` | Whitespace: followup to migrate UE_LOG to UE_LOGF: Restore newlines in multi-line format strings tha... | 对 UE_LOG 迁移至 UE_LOGF 的后续空格修复，恢复了多行格式字符串中的换行符。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件中的日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了 printf 格式说明符。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 使用代码修正工具，将所有自定义的空析构函数体 `~Type() {}` 替换为默认的 `~Type() = default`。 |

### 维护评价

- **年龄与活跃度**：该插件已存在约6年，属于“老古董”。从提交历史看，最近更新集中在 **2026年4月-5月**，主要是**维护性修复**（编译警告、日志宏迁移、代码规范统一），而非功能性更新。这表明插件已进入**稳定维护期**，而非活跃开发期。
- **稳定性**：最后一次功能性相关的提交是 **2025年10月** 的析构函数标准化。整体来看，核心功能已经非常稳定，近期的改动都是为了跟进引擎代码风格和编译标准的变化。
- **启用要求**：插件默认未启用（`EnabledByDefault: false`），这符合其作为专业分析工具的定位，用户需要按需手动开启。
- **推荐度**：**推荐在需要深度性能分析的项目中使用**。它提供了官方支持的、稳定的过滤方案，是优化 Insights 分析体验的必备工具。对于新项目，建议在项目初期就启用并配置，以建立良好的性能分析习惯。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/TraceSourceFiltering)
- [官方文档]() (链接为空，请参考插件内UI和相关代码注释)
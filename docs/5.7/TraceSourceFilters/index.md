# Insights Data Source Filters

> Source data filtering for Unreal Insights.

| 属性 | 值 |
|---|---|
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据资产） |
| 模块 | `SourceFilteringCore` (Runtime), `SourceFilteringTrace` (Runtime), `SourceFilteringEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-01-28 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/TraceSourceFiltering) | |

## 用途

Trace Source Filtering 插件为 **Unreal Insights** 提供运行时数据源过滤功能。它允许开发者在 Trace 采集阶段精确控制哪些 Actor、World 和数据源会被记录到 Trace 流中。

核心解决的问题：当使用 Unreal Insights 进行性能分析时，默认情况下所有对象都会被 trace，导致巨大的数据量和分析噪音。此插件让你可以：

1. **按 Actor 类过滤**：只追踪特定类及其子类的 Actor
2. **按自定义规则过滤**：编写 Blueprint 或 C++ 过滤器，基于任意条件决定是否追踪某个 Actor
3. **按 World 过滤**：按 World 类型（Editor、PIE、Game）和网络模式（Standalone、Dedicated Server、Client）过滤
4. **组合过滤逻辑**：使用 AND/OR/NOT 操作组合多个过滤器

**注意**：此插件默认禁用（`EnabledByDefault: false`），且在 Shipping 构建中被排除（`TargetConfigurationDenyList: ["Shipping"]`）。需要依赖 `GameplayInsights` 插件。

## 使用场景

- 你正在分析一个大型开放世界游戏的性能 → 使用 Actor 类过滤只追踪玩家角色和关键 NPC
- 你在调试网络同步问题 → 过滤只保留 Dedicated Server 的 World 数据
- 你需要对比特定 Actor 在 PIE 和 Standalone 模式下的行为差异 → 按 World 实例过滤
- 你想为团队创建一套可复用的 Trace 过滤预设 → 使用 SourceFilterCollection 数据资产

## 模块架构

```
TraceSourceFilters (插件)
├── SourceFilteringCore    ← 接口层：定义 IDataSourceFilterInterface、EFilterSetMode、FActorClassFilter
├── SourceFilteringTrace   ← 运行时层：UDataSourceFilter、FSourceFilterManager、FTraceWorldFiltering
└── SourceFilteringEditor  ← 编辑器层：UI 面板、TreeView、拖放操作、Session 服务
```

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DoesActorPassFilter` | 判断 Actor 是否通过过滤（可 Blueprint 重写） | `UDataSourceFilter` |
| `GetDisplayText` | 获取过滤器显示文本（可 Blueprint 重写） | `UDataSourceFilter`（通过 `IDataSourceFilterInterface`） |
| `GetToolTipText` | 获取过滤器工具提示文本（可 Blueprint 重写） | `UDataSourceFilter`（通过 `IDataSourceFilterInterface`） |

### 创建自定义过滤器（Blueprint）

1. 在 Content Browser 中右键 → **Blueprint Class** → 选择 `DataSourceFilter` 作为父类
2. 重写 `DoesActorPassFilter` 函数，返回 `true` 表示允许追踪，`false` 表示过滤掉
3. 可选：重写 `GetDisplayText` 提供自定义显示名称

示例逻辑：创建一个 "Only Player Controlled" 过滤器，在 `DoesActorPassFilter` 中检查 `GetInstigatorController` 是否为 PlayerController。

## C++ 用法

### 头文件引入

```cpp
// 核心接口和数据结构
#include "DataSourceFiltering.h"
#include "IDataSourceFilterInterface.h"
#include "IDataSourceFilterSetInterface.h"

// 运行时过滤器基类和集合
#include "DataSourceFilter.h"
#include "DataSourceFilterSet.h"
#include "SourceFilterCollection.h"

// World 过滤
#include "TraceWorldFiltering.h"

// Trace 输出宏
#include "SourceFilterTrace.h"

// 设置
#include "TraceSourceFilteringSettings.h"
#include "TraceSourceFilteringProjectSettings.h"
```

### 自定义过滤器

创建自定义过滤器需要继承 `UDataSourceFilter` 并重写 `DoesActorPassFilter_Internal`：

```cpp
// MyActorFilter.h
#pragma once
#include "DataSourceFilter.h"
#include "MyActorFilter.generated.h"

UCLASS()
class UMyActorFilter : public UDataSourceFilter
{
    GENERATED_BODY()

protected:
    /** 只允许被标记为 "Important" 的 Actor 通过过滤 */
    virtual bool DoesActorPassFilter_Internal(const AActor* InActor) const override
    {
        // 自定义逻辑：检查 Actor 是否有特定标签
        return InActor && InActor->ActorHasTag(FName("Important"));
    }

    virtual void GetDisplayText_Internal(FText& OutDisplayText) const override
    {
        OutDisplayText = NSLOCTEXT("MyActorFilter", "Display", "Important Actors Only");
    }
};
```

### 编程操作 FilterCollection

```cpp
#include "TraceSourceFiltering.h"
#include "SourceFilterCollection.h"
#include "DataSourceFilterSet.h"

// 获取全局 FilterCollection
USourceFilterCollection* Collection = FTraceSourceFiltering::Get().GetFilterCollection();

// 添加过滤器
UDataSourceFilter* Filter = Collection->AddFilterOfClass(UMyActorFilter::StaticClass());

// 创建 FilterSet (AND 模式)
UDataSourceFilterSet* FilterSet = Collection->MakeFilterSet(FilterOne, FilterTwo, EFilterSetMode::AND);

// 添加 Actor 类过滤
Collection->AddClassFilter(ACharacter::StaticClass());
Collection->UpdateClassFilter(ACharacter::StaticClass(), true);  // 包含子类
```

### World 级别过滤

```cpp
#include "TraceWorldFiltering.h"

// 按 World 类型过滤
FTraceWorldFiltering::SetStateByWorldType(EWorldType::Editor, false);       // 不追踪 Editor World
FTraceWorldFiltering::SetStateByWorldType(EWorldType::PIE, true);           // 追踪 PIE World

// 按网络模式过滤
FTraceWorldFiltering::SetStateByWorldNetMode(ENetMode::NM_DedicatedServer, true);  // 追踪专用服务器

// 按 World 实例过滤
const UWorld* MyWorld = GetWorld();
bool bTraceable = FTraceWorldFiltering::IsWorldTypeTraceable(MyWorld->WorldType);
```

### 操作系统操作（Trace 宏）

```cpp
#include "SourceFilterTrace.h"

// 在 SOURCE_FILTER_TRACE_ENABLED 条件下可用的宏：
TRACE_FILTER_CLASS(UClass)          // 输出过滤器类信息
TRACE_FILTER_INSTANCE(Filter)       // 输出过滤器实例
TRACE_FILTER_SET(Set)               // 输出过滤器集合
TRACE_FILTER_OPERATION(Instance, Op, Param)  // 输出过滤器操作
TRACE_FILTER_SETTINGS_VALUE(Name, Value)     // 输出设置变更
TRACE_WORLD_INSTANCE(World)         // 输出 World 实例
TRACE_WORLD_OPERATION(World, Op, Param)      // 输出 World 操作
```

## 测试基类

插件提供了 `FTraceSourceFilteringTestBase` 用于编写自动化测试：

```cpp
#include "TraceSourceFilteringTestBase.h"

class FMyFilterTest : public FTraceSourceFilteringTestBase
{
public:
    FMyFilterTest(const FString& InName)
        : FTraceSourceFilteringTestBase(InName, true) {}

protected:
    virtual void SetupTest(const FString& Parameters) override
    {
        // 添加过滤器
        auto& Filter = AddFilter<UMyActorFilter>();

        // 添加 Actor 并设定预期结果
        auto* Player = AddActor<ACharacter>(true);   // 预期通过
        auto* NPC = AddActor<ANPC>(false);           // 预期被过滤
    }
};
```

测试流程：`Init()` → `SetupTest()` → `TickFiltering()` → `CompareExpectedResults()` → `Cleanup()`

## 模块依赖

### SourceFilteringCore（使用者无需直接依赖）

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |

### SourceFilteringTrace（使用者需依赖）

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `TraceLog` | Trace 日志基础设施 |
| `Engine` | AActor、UWorld 等引擎类型 |
| `SourceFilteringCore` | 核心接口定义 |
| `PropertyPath` | 属性路径访问 |
| `AssetRegistry` | 资产注册表 |
| `DeveloperSettings` | 项目设置基类 |

### SourceFilteringEditor（编辑器专用）

| 模块 | 用途 |
|---|---|
| `Slate` / `SlateCore` / `InputCore` | UI 框架 |
| `TraceServices` / `TraceInsights` / `TraceAnalysis` | Insights 分析服务 |
| `SourceFilteringCore` | 核心接口 |
| `GameplayInsights` | Gameplay Insights 集成 |
| `WorkspaceMenuStructure` | 编辑器菜单结构 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-06-25 | `3022aed` | Clean up Type tracing code to remove all the "Class" references, now that it supports tracing Struct types as well | 类型追踪扩展到 Struct，重构命名 |
| 2025-05-20 | `c1d4eec` | Replaced bool arguments with EFindObjectFlags | 代码质量改进，用枚举替换 bool 参数 |
| 2025-04-23 | `939cc6e` | Used FortniteClient build target to find and convert all files to have dllstorage | DLL 导出宏规范化 |

### 维护评价

- **创建时间**：2020 年 1 月，约 6 年历史
- **活跃状态**：**活跃维护中** — 2025 年仍有功能性更新（Struct 类型追踪支持）
- **更新质量**：最近更新为实质性改进（扩展功能 + 代码清理），不是仅编译修复
- **依赖关系**：依赖 `GameplayInsights` 插件，与 Insights 系统深度耦合
- **限制**：Shipping 构建中不可用，默认禁用需手动启用
- **推荐**：✅ 对于需要精细控制 Unreal Insights Trace 数据采集的项目，推荐使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/TraceSourceFiltering)
- [测试基类](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringTrace/Public/TraceSourceFilteringTestBase.h)

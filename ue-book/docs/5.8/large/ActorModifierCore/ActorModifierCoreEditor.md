# Actor Modifier Core

> Use modifier objects on actors to apply a custom behavior（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Actor修改器核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ActorModifierCore` (Runtime), `ActorModifierCoreBlueprint` (UncookedOnly), `ActorModifierCoreEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifierCore) | |

## 用途
该插件是 Unreal Engine **Motion Design** 工具链的核心组件。它提供了一个框架，允许用户在编辑器中为 Actor 附加“修改器”（Modifier）对象。这些修改器可以程序化地修改 Actor 的各种属性（如变换、网格体数据、材质等），以实现自定义的、非破坏性的行为和效果。其核心解决的问题是：为虚拟制片和 Motion Design 流程提供一个可扩展的、可叠加的、用于驱动 Actor 状态变化的系统。

## 使用场景
- 你在使用 Motion Design 工具创建动态图形或虚拟制片效果时，需要对一组 Actor 应用一致的、参数化的程序化修改（例如，根据时间或数据改变位置、旋转、缩放、材质等）。
- 你需要构建一个可复用的效果逻辑，并将其作为组件轻松地添加到场景中的不同 Actor 上。
- 你希望开发自定义的修改器蓝图节点，以扩展 Motion Design 系统的功能。

## 蓝图用法
该插件的 `ActorModifierCoreBlueprint` 模块（类型为 `UncookedOnly`）主要负责提供在蓝图中创建和编辑修改器的资产定义和工厂，而运行时和编辑器功能主要通过 C++ API 暴露。蓝图用户主要通过编辑器 UI（如 Operator Stack 面板）与修改器交互，而不是直接通过蓝图节点调用。核心的蓝图可调用函数主要集中在编辑器子系统上。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `FillModifierMenu` | 填充一个工具菜单，用于添加、插入、删除、移动或启用/禁用修改器。 | `UActorModifierCoreEditorSubsystem` |
| `RegisterProfilerWidget` | 注册一个自定义的分析器控件类，用于可视化显示特定类型修改器的性能数据。 | `UActorModifierCoreEditorSubsystem` |
| `UnregisterProfilerWidget` | 取消注册一个之前注册的自定义分析器控件类。 | `UActorModifierCoreEditorSubsystem` |
| `CreateProfilerWidget` | 为给定的修改器分析器实例创建其对应的分析器控件。 | `UActorModifierCoreEditorSubsystem` |
| `AddProfilerStat` | 向分析器控件添加一个名为 `InName` 的统计信息条目，并返回其指针以便后续更新。 | `SActorModifierCoreEditorProfiler` |
| `GetProfilerStat` | 获取分析器控件中名为 `InName` 的统计信息条目。 | `SActorModifierCoreEditorProfiler` |

### 使用示例（蓝图描述）
1.  **获取编辑器子系统**：在编辑器工具蓝图中，使用 `Get Actor Modifier Core Editor Subsystem` 节点获取 `UActorModifierCoreEditorSubsystem` 的实例。
2.  **动态生成菜单**：将一个 `UToolMenu` 对象和 `FActorModifierCoreEditorMenuContext`（通常从选中的对象创建）以及配置好类型的 `FActorModifierCoreEditorMenuOptions` 传入 `FillModifierMenu` 节点，即可动态生成管理修改器的上下文菜单。
3.  **注册自定义分析器 UI**：在插件或项目的编辑器模块启动时，调用 `RegisterProfilerWidget` 节点，指定你的自定义分析器数据类（继承自 `FActorModifierCoreProfiler`）和自定义控件类（继承自 `SActorModifierCoreEditorProfiler`）。之后，当系统需要显示该类型修改器的性能分析时，就会使用你注册的控件。

## C++ 用法
### 头文件引入
```cpp
#include "ActorModifierCoreEditorSubsystem.h"
```
### 基本用法
获取编辑器子系统实例并注册一个自定义分析器控件。
```cpp
// 获取编辑器子系统单例
UActorModifierCoreEditorSubsystem* EditorSubsystem = UActorModifierCoreEditorSubsystem::Get();

// 假设你有一个自定义分析器数据类 FMyModifierProfiler 和自定义控件类 SMyModifierProfilerWidget
// 在某个初始化函数中注册
EditorSubsystem->RegisterProfilerWidget<FMyModifierProfiler, SMyModifierProfilerWidget>();

// 取消注册
EditorSubsystem->UnregisterProfilerWidget<FMyModifierProfiler>();
```
*（来源：`Public/Subsystems/ActorModifierCoreEditorSubsystem.h` 中 `RegisterProfilerWidget` 和 `UnregisterProfilerWidget` 模板函数定义）*

### 进阶用法
实现一个自定义的分析器控件（Widget），用于展示自定义的统计数据。
```cpp
// MyModifierProfilerWidget.h
#pragma once
#include "Modifiers/Widgets/SActorModifierCoreEditorProfiler.h"

class SMyModifierProfilerWidget : public SActorModifierCoreEditorProfiler
{
public:
    SLATE_BEGIN_ARGS(SMyModifierProfilerWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs, TSharedPtr<FActorModifierCoreProfiler> InProfiler);

protected:
    // 重写以添加自定义统计信息
    virtual void SetupProfilerStats(TSharedPtr<FActorModifierCoreProfiler> InProfiler) override;
    virtual void OnProfilerStatAdded(FActorModifierCoreEditorProfilerStat& InStat) override;
};
```
```cpp
// MyModifierProfilerWidget.cpp
#include "MyModifierProfilerWidget.h"
#include "MyModifierProfiler.h" // 你的自定义分析器数据类

void SMyModifierProfilerWidget::Construct(const FArguments& InArgs, TSharedPtr<FActorModifierCoreProfiler> InProfiler)
{
    SActorModifierCoreEditorProfiler::Construct(FArguments(), InProfiler);
}

void SMyModifierProfilerWidget::SetupProfilerStats(TSharedPtr<FActorModifierCoreProfiler> InProfiler)
{
    // 先调用父类，它会扫描分析器数据的属性并自动添加统计条目
    SActorModifierCoreEditorProfiler::SetupProfilerStats(InProfiler);

    // 手动添加一个额外的自定义统计条目
    if (FActorModifierCoreEditorProfilerStat* CustomStat = AddProfilerStat(FName("CustomValue")))
    {
        // 可以绑定一个动态属性，例如从你的分析器数据类获取
        CustomStat->ValueText = FText::AsNumber(MyProfiler->GetCustomValue());
        CustomStat->Suffix = TEXT("units");
    }
}

void SMyModifierProfilerWidget::OnProfilerStatAdded(FActorModifierCoreEditorProfilerStat& InStat)
{
    // 可以在这里自定义某个统计条目的默认颜色、前缀等
    if (InStat.Name == FName("Duration"))
    {
        InStat.Suffix = TEXT("ms");
    }
}
```
*（来源：`Public/Modifiers/Widgets/SActorModifierCoreEditorProfiler.h` 中的类声明和保护方法）*

## Demo 示例
一个最小化的自定义分析器控件实现。
**MyCustomModifierProfiler.h**
```cpp
#pragma once
#include "Modifiers/ActorModifierCoreProfiler.h"

UCLASS()
class UMyCustomModifierProfiler : public FActorModifierCoreProfiler
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadOnly, Category = "Stats")
    float ExecutionTime = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "Stats")
    int32 VerticesAffected = 0;
};
```
**SMyCustomProfilerWidget.h**
```cpp
#pragma once
#include "Modifiers/Widgets/SActorModifierCoreEditorProfiler.h"

class SMyCustomProfilerWidget : public SActorModifierCoreEditorProfiler
{
public:
    SLATE_BEGIN_ARGS(SMyCustomProfilerWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs, TSharedPtr<FActorModifierCoreProfiler> InProfiler);

protected:
    virtual void SetupProfilerStats(TSharedPtr<FActorModifierCoreProfiler> InProfiler) override;
};
```
**SMyCustomProfilerWidget.cpp**
```cpp
#include "SMyCustomProfilerWidget.h"
#include "MyCustomModifierProfiler.h"

void SMyCustomProfilerWidget::Construct(const FArguments& InArgs, TSharedPtr<FActorModifierCoreProfiler> InProfiler)
{
    SActorModifierCoreEditorProfiler::Construct(FArguments(), InProfiler);
}

void SMyCustomProfilerWidget::SetupProfilerStats(TSharedPtr<FActorModifierCoreProfiler> InProfiler)
{
    // 调用父类，它会自动处理 UPROPERTY 标记的属性（如 ExecutionTime, VerticesAffected）
    SActorModifierCoreEditorProfiler::SetupProfilerStats(InProfiler);

    // 可以手动添加或覆盖自动扫描的统计条目
    if (FActorModifierCoreEditorProfilerStat* TimeStat = GetProfilerStat(FName("ExecutionTime")))
    {
        TimeStat->Suffix = TEXT(" ms");
    }
}
```

## 模块依赖
该插件依赖 `OperatorStack` 插件提供编辑器堆栈面板功能。

| 模块 | 用途 |
|---|---|
| `OperatorStack` | 为修改器在编辑器中提供可视化的堆栈（Stack）列表和自定义面板。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `2d1c7712` | Motion Design: fixed issue where duplicating actors with modifiers and deleting those new duplicates | 修复了在带修改器的Actor被复制并删除新副本时出现的问题。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用的作用域枚举可能导致输出乱码的问题。 |
| 2026-04-14 | `abb26688` | Actor Modifiers: added experimental freeze modifier feature. | 为Actor修改器添加了实验性的“冻结”修改器功能。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-04-09 | `bdd66985` | Motion Design: made render state dirty reason optional + added some fixes to the text3d update causi | 让渲染状态脏标记的原因变为可选，并修复了导致 Text3D 更新的一些问题。 |

### 维护评价
- **创建时间**：插件于 2025 年 5 月创建，非常年轻。
- **近期更新**：最近一次更新在 2026 年 5 月，且近几个月有多次功能性更新（如新增冻结功能、修复复制删除 bug）和底层优化，表明插件正在**积极维护和开发**中。
- **维护状态**：**活跃维护**。
- **已知限制**：插件默认未启用（`Installed: false`），且其 `ActorModifierCoreBlueprint` 模块为 `UncookedOnly` 类型，意味着蓝图修改器资产仅在编辑器中可用。
- **推荐使用**：✅ **推荐**。该插件是 Motion Design 工具链的核心，如果你需要进行虚拟制片或程序化效果制作，它是必不可少的。作为新插件，其 API 和功能可能仍在演进中。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifierCore)
- 官方文档 (无)
- 测试用例 (未在插件目录内发现标准测试)
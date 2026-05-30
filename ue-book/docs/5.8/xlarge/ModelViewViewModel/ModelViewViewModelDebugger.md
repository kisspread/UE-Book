# UMG Viewmodel

> A plugin to support the Model-View-Viewmodel pattern in UMG.

| 属性 | 值 |
|---|---|
| 中文名 | UMG 视图模型 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ModelViewViewModel` (Runtime), `ModelViewViewModelAssetSearch` (Runtime), `ModelViewViewModelBlueprint` (Runtime), `ModelViewViewModelDebugger` (Runtime), `ModelViewViewModelDebuggerEditor` (Runtime), `ModelViewViewModelEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-04-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ModelViewViewModel) | |

## 用途

该插件为 Unreal Motion Graphics (UMG) 提供了 Model-View-ViewModel (MVVM) 架构模式的实现。MVVM 是一种设计模式，用于将用户界面（View）与业务逻辑和数据（Model）分离，通过 ViewModel 作为中间层进行连接。这使得 UI 逻辑和业务逻辑解耦，提高了代码的可维护性、可测试性和可复用性。

插件的核心思想是：
- **Model（模型）**：代表应用程序的数据和业务逻辑。
- **View（视图）**：代表 UI 元素，在 UE 中即为 UMG Widget。
- **ViewModel（视图模型）**：作为 View 和 Model 之间的桥梁，负责将 Model 的数据转换为 View 可以显示的格式，并将 View 的用户操作转发给 Model。

该插件解决了在复杂 UI 项目中，UI 代码与业务逻辑紧密耦合导致难以维护和测试的问题。它通过提供一套框架，让开发者能够以声明式的方式将数据绑定到 UI，从而专注于业务逻辑的实现。

**注意**：此插件为 **实验性（Beta）** 功能，默认未启用，需要在项目设置中手动开启。

## 使用场景

- 你需要构建一个数据驱动的复杂 UI 界面（例如：RPG 游戏的背包系统、策略游戏的数据面板），并且希望将 UI 显示与游戏逻辑（如背包数据管理、战斗计算）清晰地分开。
- 你的项目包含多个不同的 UI 界面，它们需要共享相同的数据源（例如：玩家状态、任务列表），使用 MVVM 可以轻松地在不同 View 之间同步数据。
- 你希望编写可测试的 UI 逻辑，将 ViewModel 作为单独的模块进行单元测试，而无需依赖真实的 UI 或游戏世界。
- 你在开发需要频繁迭代 UI 的项目，MVVM 模式允许设计师和程序员并行工作，设计师可以调整 View 布局，而程序员可以独立开发 ViewModel。

## 蓝图用法

基于源码分析，该插件提供了大量用于在蓝图中创建和管理 ViewModel 以及绑定数据的节点。核心功能集中在 `ModelViewViewModelBlueprint` 和 `ModelViewViewModelEditor` 模块中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create View Model` | 为指定的 UMG Widget 创建并关联一个 ViewModel 实例。 | `UK2Node_MVVMCreateViewModel` |
| `Bind Property` | 将 ViewModel 的一个属性（通过 FieldId 指定）绑定到 Widget 的某个属性上。 | `UK2Node_MVVMAddBinding` |
| `Get ViewModel` | 获取与当前 Widget 关联的 ViewModel 对象。 | `UMVVMBlueprintViewExtension` |
| `Set Property Value` | 在 ViewModel 上设置一个属性的值，并自动通知所有绑定的 View 更新。 | (通常通过自动生成的蓝图节点) |
| `Field Notification` | 当 ViewModel 的某个属性值发生变化时触发的委托，用于通知 View 进行更新。 | `INotifyFieldValueChanged` |

### 使用示例（蓝图描述）

1. **创建并绑定 ViewModel**：
   - 在 Widget 蓝图中，使用 `Create View Model` 节点为当前 Widget 创建一个自定义的 ViewModel（例如 `BP_InventoryViewModel`）。
   - 在 ViewModel 的类蓝图中，使用 `Bind Property` 节点将 ViewModel 中的 `GoldAmount` 属性（类型为 `int32`）绑定到 Widget 中的 `TextBlock_Gold` 的 `Text` 属性（类型为 `FText`）。绑定时可能需要一个转换函数，将 `int32` 转换为 `FText`。

2. **更新 ViewModel 数据**：
   - 在游戏逻辑（例如 C++ 中的 `APlayerController`）中，获取到 ViewModel 对象（通过 `Get ViewModel` 节点）。
   - 直接修改 ViewModel 中的 `GoldAmount` 属性值。
   - 修改后，所有绑定了 `GoldAmount` 的 UI 控件（如 `TextBlock_Gold`）将自动更新显示。

## C++ 用法

在 C++ 中使用此插件需要定义自己的 ViewModel 和绑定关系，并与 UMG Widget 集成。

### 头文件引入

```cpp
// 核心 MVVM 功能
#include "MVVMViewModelBase.h"
#include "MVVMSubsystem.h"

// 调试相关
#include "MVVMDebugSnapshot.h"
```

### 基本用法

**1. 定义 ViewModel 类**

```cpp
// MyViewModel.h
#pragma once
#include "MVVMViewModelBase.h"
#include "MyViewModel.generated.h"

// ViewModel 需要继承自 UMVVMViewModelBase
UCLASS(BlueprintType)
class UMyViewModel : public UMVVMViewModelBase
{
    GENERATED_BODY()

public:
    // 使用 FIELD_NOTIFY 宏声明一个字段，使其支持变更通知
    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "ViewModel")
    int32 PlayerHealth = 100;

    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "ViewModel")
    FText PlayerName = FText::FromString(TEXT("Hero"));

    // 用于更新字段并自动触发通知的函数
    UFUNCTION(BlueprintCallable, Category = "ViewModel")
    void SetPlayerHealth(int32 NewHealth);
};
```

```cpp
// MyViewModel.cpp
#include "MyViewModel.h"

void UMyViewModel::SetPlayerHealth(int32 NewHealth)
{
    // 使用 SET_FIELD_NOTIFY 宏更新字段并触发通知
    UE_MVVM_SET_PROPERTY_VALUE(PlayerHealth, NewHealth);
}
```
*来源参考：`MVVMViewModelBase` 的用法模式*

**2. 在 Widget 中获取和使用 ViewModel**

```cpp
// MyWidget.h
#pragma once
#include "Blueprint/UserWidget.h"
#include "MyWidget.generated.h"

class UMyViewModel;

UCLASS()
class UMyWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    // 用于在蓝图中设置的 ViewModel 类
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ViewModel")
    TSubclassOf<UMyViewModel> ViewModelClass;

protected:
    virtual void NativeConstruct() override;

private:
    // 持有 ViewModel 的实例
    UPROPERTY()
    TWeakObjectPtr<UMyViewModel> CurrentViewModel;
};
```

```cpp
// MyWidget.cpp
#include "MyWidget.h"
#include "MVVMSubsystem.h"

void UMyWidget::NativeConstruct()
{
    Super::NativeConstruct();

    // 通过 MVVM 子系统创建 ViewModel 实例
    if (UMVVMGameSubsystem* MVVMSubsystem = GetGameInstance()->GetSubsystem<UMVVMGameSubsystem>())
    {
        if (ViewModelClass)
        {
            CurrentViewModel = Cast<UMyViewModel>(MVVMSubsystem->CreateViewModelInstance(ViewModelClass));
        }
    }
}
```
*来源参考：`UMVVMGameSubsystem` 和 Widget 扩展的典型用法*

### 进阶用法

**1. 在 C++ 中设置绑定（通常由编辑器工具生成，但底层原理如下）**

```cpp
// 假设你已经通过编辑器工具创建了一个绑定视图类（UMVVMViewClass），并获取了其实例。
// 在运行时，你可以手动触发绑定的更新。

// 获取 Widget 关联的 View 对象
UMVVMView* MVVMView = ...; // 通常由框架管理
if (MVVMView)
{
    // 手动评估所有绑定，这会根据当前 ViewModel 的数据更新 View
    MVVMView->EvaluateBindings();
}
```

**2. 使用调试快照**

```cpp
// 在调试时，可以获取当前所有 ViewModel 和 View 的快照进行分析
TSharedPtr<UE::MVVM::FDebugSnapshot> Snapshot = UE::MVVM::FDebugSnapshot::CreateSnapshot();
if (Snapshot.IsValid())
{
    // 查看所有 ViewModel 实例
    TArrayView<TSharedPtr<FMVVMViewModelDebugEntry>> ViewModelEntries = Snapshot->GetViewModels();
    for (const auto& Entry : ViewModelEntries)
    {
        UE_LOG(LogTemp, Log, TEXT("ViewModel Found: %s"), *Entry->Name.ToString());
    }
}
```
*来源参考：`MVVMDebugSnapshot.h` 中的 API*

## Demo 示例

一个最小的可运行示例，展示一个显示玩家名字的 Widget。

**1. ViewModel 类 (UMySimpleViewModel.h)**

```cpp
#pragma once
#include "MVVMViewModelBase.h"
#include "UMySimpleViewModel.generated.h"

UCLASS(BlueprintType)
class UMySimpleViewModel : public UMVVMViewModelBase
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Data")
    FText DisplayName;

    UFUNCTION(BlueprintCallable)
    void SetDisplayName(const FText& NewName);
};
```

```cpp
// UMySimpleViewModel.cpp
#include "UMySimpleViewModel.h"

void UMySimpleViewModel::SetDisplayName(const FText& NewName)
{
    UE_MVVM_SET_PROPERTY_VALUE(DisplayName, NewName);
}
```

**2. UMG Widget 蓝图 (WBP_PlayerName)**
在蓝图编辑器中：
1. 创建一个 `UMySimpleViewModel` 类型的变量。
2. 在 `Construct` 事件中，通过 `Create View Model` 节点创建实例并赋值给该变量。
3. 使用 `Bind Property` 节点，将 ViewModel 的 `DisplayName` 属性绑定到 `TextBlock` 的 `Text` 属性上。

**3. 游戏逻辑调用**
```cpp
// 在某个游戏逻辑类中（例如 PlayerController）
// 获取 Widget 实例
UUserWidget* NameWidget = ...;
// 假设通过某种方式获取了它的 ViewModel
UMySimpleViewModel* VM = ...;
if (VM)
{
    VM->SetDisplayName(FText::FromString(TEXT("New Player Name")));
    // UI 将自动更新
}
```

## 模块依赖

该插件本身由多个模块组成，相互依赖。若要在你的项目或插件中使用 MVVM 功能，需要在你的模块的 `.Build.cs` 文件中添加对 `ModelViewViewModel` 核心模块的依赖。

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "UMG",
    "Slate",
    "SlateCore",
    "ModelViewViewModel" // 核心运行时模块
});
```

**其他模块依赖说明**：
- **调试功能**：如果你需要使用调试快照等功能，需要额外依赖 `ModelViewViewModelDebugger`。
- **编辑器工具**：编辑器扩展和蓝图节点支持由 `ModelViewViewModelEditor` 和 `ModelViewViewModelBlueprint` 提供，这些通常是编辑器插件，仅在编辑器环境下依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `f172f2b0` | MVVMToolset: Initial MVVM toolset plugin that supports creating and modifying Viewmodel via blueprin | 初始 MVVM 工具集插件，支持通过蓝图创建和修改 Viewmodel |
| 2026-05-13 | `825be502` | Listview/Panel Extension: use widget blueprint class directly to get the MVVM view during compilatio | 列表视图/面板扩展：编译时直接使用 Widget 蓝图类获取 MVVM 视图 |
| 2026-05-12 | `21f108ac` | Cherry-pick UMGToolSet | 合并 UMG 工具集功能 |
| 2026-04-23 | `e24ce23f` | MVVM: Remove unused USTRUCT specifiers | 移除未使用的 USTRUCT 说明符，进行代码清理 |
| 2026-04-22 | `cd8175a0` | MVVM: Resolve invalid transient outer when importing copyied conditions and events. UMVVMBlueprintVi | 修复导入复制的条件和事件时无效的瞬态外层问题 |

### 维护评价

该插件处于**活跃开发**状态。
- **年龄**：创建于 2022 年，至今约 4 年。
- **近期活动**：最近几次提交集中在 2026 年 4 月和 5 月，包括新功能（MVVM 工具集）、Bug 修复（列表视图绑定、瞬态外层问题）和代码优化，表明 Epic 官方仍在积极迭代和完善此功能。
- **状态**：插件标记为 Beta（`IsBetaVersion=true`），且默认未启用。这意味着 API 可能在未来版本中发生变化，不建议在需要长期稳定的核心项目中完全依赖。但对于新项目或原型开发，是尝试 MVVM 架构的良好起点。
- **推荐**：推荐希望在 UE5 中采用现代 UI 架构、改善代码组织和测试性的开发者使用。建议关注官方更新日志，因为 Beta 状态的 API 可能调整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ModelViewViewModel)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/umg-model-view-viewmodel-in-unreal-engine/) (Beta 功能，文档可能不完整或变动)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ModelViewViewModel/Tests) (路径推测，插件内通常包含测试)
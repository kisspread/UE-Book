# UMG Viewmodel

> A plugin to support the Model-View-Viewmodel pattern in UMG.

| 属性 | 值 |
|---|---|
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ModelViewViewModel` (Runtime), `ModelViewViewModelAssetSearch` (Runtime), `ModelViewViewModelBlueprint` (Runtime), `ModelViewViewModelDebugger` (Runtime), `ModelViewViewModelDebuggerEditor` (Runtime), `ModelViewViewModelEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-04-01 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ModelViewViewModel) | |

## 用途

此插件为 Unreal Engine 的 UMG (Unreal Motion Graphics) UI 框架提供了 Model-View-ViewModel (MVVM) 设计模式的官方支持。它旨在将 UI 的显示逻辑（View）与业务逻辑和状态（ViewModel）解耦，从而提升 UI 代码的可维护性、可测试性和复用性。

插件的核心功能包括：
1.  **声明式数据绑定**：允许在蓝图或 C++ 中定义 UI 控件（View）的属性与 ViewModel 属性之间的绑定关系，实现数据的自动同步。
2.  **ViewModel 生命周期管理**：提供机制来创建、初始化和管理 ViewModel 实例，并将其与 View 关联。
3.  **字段变更通知**：基于 `FieldNotification` 系统，当 ViewModel 的属性值发生变化时，能够自动通知绑定的 UI 控件进行更新。
4.  **调试与可视化**：提供专门的调试工具（`ModelViewViewModelDebugger` 模块），用于在运行时检查和诊断 MVVM 绑定的状态、数据流和潜在问题。

## 使用场景

-   你正在开发一个数据驱动的复杂 UI（如游戏内商店、背包系统、角色属性面板），希望将 UI 显示逻辑与游戏数据逻辑清晰分离。
-   你需要在多个不同的 UI 界面中复用同一份业务逻辑和状态管理代码。
-   你希望 UI 能够自动响应数据变化，而无需手动编写大量的事件监听和更新代码。
-   你需要在开发过程中调试 UI 数据绑定问题，查看哪些属性被绑定、当前值是什么以及绑定是否生效。

## 蓝图用法

由于提供的 `ModelViewViewModelDebugger` 模块头文件主要定义了调试数据结构，而非可调用的蓝图函数，因此本章节将基于 MVVM 模式的一般用法和插件其他模块的预期功能进行说明。具体节点需查阅 `ModelViewViewModel` 和 `ModelViewViewModelBlueprint` 模块。

### 核心概念

-   **ViewModel**：一个 UObject 派生类，其属性使用 `UPROPERTY(BlueprintReadWrite)` 和 `FieldNotify` 标记，代表需要暴露给 UI 的数据。
-   **View**：通常是一个 UMG Widget 蓝图，通过 `ViewModel` 属性关联一个 ViewModel 实例。
-   **绑定**：在 Widget 蓝图的属性面板中，可以将某个控件的属性（如 Text）绑定到 ViewModel 的某个属性上。

### 使用示例（蓝图描述）

1.  **创建 ViewModel 蓝图**：创建一个继承自 `UMVVMViewModelBase` 的蓝图类（例如 `BP_PlayerViewModel`）。在其中添加变量（如 `PlayerName`, `Health`），并确保勾选 `FieldNotify`。
2.  **创建 View (Widget)**：创建一个 UMG Widget 蓝图（例如 `WBP_PlayerHUD`）。
3.  **关联 ViewModel**：在 `WBP_PlayerHUD` 的类默认值中，找到 `ViewModel` 属性，将其设置为 `BP_PlayerViewModel` 类。
4.  **设置绑定**：在 `WBP_PlayerHUD` 的设计器中，选择一个 Text 控件，在其 `Text` 属性旁点击“绑定”按钮，从列表中选择 `BP_PlayerViewModel` 的 `PlayerName` 属性。
5.  **运行时设置数据**：在游戏逻辑中，获取到 `WBP_PlayerHUD` 的实例后，通过其 `GetViewModel` 函数获取 `BP_PlayerViewModel` 实例，然后设置其 `PlayerName` 属性。UI 将自动更新。

## C++ 用法

### 头文件引入

```cpp
#include "MVVMViewModelBase.h"
#include "MVVMSubsystem.h"
#include "MVVMViewModelContext.h"
// 调试相关
#include "MVVMDebugSnapshot.h"
#include "MVVMDebugView.h"
#include "MVVMDebugViewModel.h"
```

### 基本用法：定义 ViewModel

创建一个继承自 `UMVVMViewModelBase` 的类，并使用 `FieldNotify` 宏标记需要通知的属性。

```cpp
// MyViewModel.h
#pragma once
#include "MVVMViewModelBase.h"
#include "MyViewModel.generated.h"

UCLASS(BlueprintType)
class UMyViewModel : public UMVVMViewModelBase
{
    GENERATED_BODY()

public:
    // 使用 FieldNotify 标记属性，使其变化时能通知绑定的 View
    UPROPERTY(BlueprintReadWrite, FieldNotify, Setter, Getter)
    FString PlayerName;

    UPROPERTY(BlueprintReadWrite, FieldNotify, Setter, Getter)
    float Health;

    // 必须实现的 Setter 和 Getter，用于触发通知
    void SetPlayerName(const FString& NewName);
    const FString& GetPlayerName() const;

    void SetHealth(float NewHealth);
    float GetHealth() const;
};
```

```cpp
// MyViewModel.cpp
#include "MyViewModel.h"

void UMyViewModel::SetPlayerName(const FString& NewName)
{
    // 使用 UE_MVVM_SET_PROPERTY_VALUE 宏来设置值并触发通知
    UE_MVVM_SET_PROPERTY_VALUE(PlayerName, NewName);
}

const FString& UMyViewModel::GetPlayerName() const
{
    return PlayerName;
}

void UMyViewModel::SetHealth(float NewHealth)
{
    UE_MVVM_SET_PROPERTY_VALUE(Health, NewHealth);
}

float UMyViewModel::GetHealth() const
{
    return Health;
}
```

### 进阶用法：使用调试快照

`ModelViewViewModelDebugger` 模块提供了运行时检查 MVVM 状态的能力。

```cpp
#include "MVVMDebugSnapshot.h"

void DebugCurrentMVVMState()
{
    // 创建当前所有 MVVM 视图和视图模型的快照
    TSharedPtr<UE::MVVM::FDebugSnapshot> Snapshot = UE::MVVM::FDebugSnapshot::CreateSnapshot();

    if (Snapshot.IsValid())
    {
        // 遍历所有捕获的视图模型
        for (const TSharedPtr<FMVVMViewModelDebugEntry>& ViewModelEntry : Snapshot->GetViewModels())
        {
            UE_LOG(LogTemp, Log, TEXT("ViewModel: %s, Path: %s"), *ViewModelEntry->Name.ToString(), *ViewModelEntry->PathName);

            // 检查该视图模型上的字段绑定
            for (const FMVVMViewModelFieldBoundDebugEntry& FieldBound : ViewModelEntry->FieldBound)
            {
                UE_LOG(LogTemp, Log, TEXT("  Bound Field: %s, To: %s::%s"),
                    *FieldBound.KeyFieldId.ToString(),
                    *FieldBound.BindingObjectPathName,
                    *FieldBound.BindingFunctionName.ToString());
            }
        }

        // 遍历所有捕获的视图
        for (const TSharedPtr<FMVVMViewDebugEntry>& ViewEntry : Snapshot->GetViews())
        {
            UE_LOG(LogTemp, Log, TEXT("View Widget: %s"), *ViewEntry->UserWidgetInstanceName.ToString());
            // ... 可以进一步检查视图的源（ViewModels）和绑定
        }
    }
}
```

## Demo 示例

以下是一个最小化的 C++ ViewModel 示例，演示如何定义一个可绑定的属性。

**MySimpleViewModel.h**
```cpp
#pragma once
#include "MVVMViewModelBase.h"
#include "MySimpleViewModel.generated.h"

UCLASS(BlueprintType)
class UMySimpleViewModel : public UMVVMViewModelBase
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, FieldNotify, Setter, Getter)
    int32 Score;

    void SetScore(int32 NewScore);
    int32 GetScore() const;
};
```

**MySimpleViewModel.cpp**
```cpp
#include "MySimpleViewModel.h"

void UMySimpleViewModel::SetScore(int32 NewScore)
{
    UE_MVVM_SET_PROPERTY_VALUE(Score, NewScore);
}

int32 UMySimpleViewModel::GetScore() const
{
    return Score;
}
```

在蓝图中，你可以创建一个 `UMySimpleViewModel` 的实例，将其赋给一个 Widget 的 `ViewModel` 属性，然后将该 Widget 的某个 Text 控件的文本绑定到 `Score` 属性。当在 C++ 或蓝图中调用 `SetScore` 时，UI 会自动更新。

## 模块依赖

由于未提供具体的 Build.cs 文件，以下依赖基于 MVVM 插件的典型需求推断。实际使用时，请以项目 Build.cs 中的配置为准。

| 模块 | 用途 |
|---|---|
| `FieldNotification` | 提供字段变更通知的核心基础设施 (`FieldNotify`, `FFieldNotificationId`) |
| `UMG` | UMG UI 框架，是 MVVM 模式中 View 层的基础 |
| `Slate`, `SlateCore` | 底层 UI 框架，UMG 构建于其上 |
| `PropertyEditor` | (编辑器相关) 可能用于在编辑器中可视化编辑绑定 |

## 维护状态

### 近期更新

```
- 2739c3d30ebc (2025-10-03) Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n
- fa42c9b6094c (2025-09-15) MVVM: Rework for the view runtime data. The new format allows for better error detection and new features in progress. The view owns the bindings and events. The source has a list of the bindings. That saves runtime of memory, the delegate doesn't store the binding id. All bindings, events, sources are now sorted for better incremental build performance. Add a different “key” structures to prevent mistakes with indexes. Unregister the delay bindings when the source is released. Store the FieldId, in the source itself. That reduces the amount of work when loading the view. Add option to delay the events initialization (like we do for bindings). The binding to evaluate “long path” view models are now separated from regular bindings. #jira UE-194167 #rb editor-ui-systems
- 63b4b620a76b (2025-08-20) MVVM: Test if the Binding library is loaded before accessing it. #rb editor-ui-systems
```

### 维护评价

-   **活跃维护**：插件创建于 2022 年，属于较新的功能。从最近的提交记录看，维护非常活跃，尤其是在 2025 年 9 月进行了一次重大的运行时数据重构（`fa42c9b6094c`），旨在提升性能、内存效率和错误检测能力。这表明 Epic 正在积极开发和完善此功能。
-   **实验性状态**：插件在 `.uplugin` 中明确标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`。这意味着它尚未稳定，API 可能发生变化，不建议在追求稳定性的生产项目中直接使用。
-   **推荐使用**：对于新项目或愿意承担 API 变更风险以获取先进 UI 架构的团队，可以尝试使用。它代表了 UE 官方对 UMG 架构的改进方向。对于现有项目，建议在实验性分支中评估。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ModelViewViewModel)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/model-view-viewmodel-in-unreal-engine/) (UE 5.7 文档中应有相关章节)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ModelViewViewModel/Tests) (路径为推测，需确认)
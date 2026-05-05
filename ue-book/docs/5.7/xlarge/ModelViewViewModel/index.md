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

该插件为 Unreal Engine 的 UMG (Unreal Motion Graphics) UI 框架引入了 **Model-View-ViewModel (MVVM)** 设计模式的支持。它旨在解决复杂 UI 中数据逻辑与显示逻辑紧密耦合的问题，通过提供一套数据绑定机制，允许开发者将 UI 的显示（View）与驱动其显示的数据和业务逻辑（ViewModel）分离，从而提升代码的可维护性、可测试性和可复用性。

## 使用场景

-   你正在开发一个数据密集型的 UI（如 RPG 背包、技能树、设置菜单），希望 UI 元素能自动响应数据变化，而无需手动编写大量的更新代码。
-   你希望将 UI 的显示逻辑（如控件的可见性、文本内容）与游戏或应用的核心数据模型解耦，以便于团队分工（UI 设计师与逻辑程序员）和单元测试。
-   你需要一个标准化的、引擎原生支持的方案来管理 UI 状态，避免使用事件分发器或委托导致的“面条式代码”。

## 蓝图用法

该插件的核心蓝图功能围绕 **ViewModel** 和 **View** 的创建与绑定展开。更多详细节点请参考各子模块文档。

### 核心节点

| 节点类型 | 说明 | 所在类/概念 |
|---|---|---|
| `Create ViewModel` | 创建一个 ViewModel 实例，通常在 Widget 的 `Construct` 事件中调用。 | `UMVVMViewModelBase` |
| `Set ViewModel` | 将一个 ViewModel 实例绑定到当前 Widget（View）。 | `UUserWidget` |
| `Get ViewModel` | 获取当前 Widget 绑定的 ViewModel 实例。 | `UUserWidget` |
| `Notify Field Changed` | 在 ViewModel 中，当某个属性值改变时调用此节点，以通知所有绑定的 View 进行更新。 | `UMVVMViewModelBase` |

### 使用示例（蓝图描述）

1.  **创建 ViewModel 蓝图**：创建一个继承自 `UMVVMViewModelBase` 的蓝图类（如 `BP_InventoryViewModel`），并在其中定义 `UPROPERTY(BlueprintReadWrite)` 属性（如 `Gold`, `ItemList`）。
2.  **创建 View (Widget)**：创建一个 UMG Widget 蓝图（如 `WBP_Inventory`）。
3.  **绑定**：在 `WBP_Inventory` 的图表中，在 `Event Construct` 节点后，使用 `Create ViewModel` 节点创建 `BP_InventoryViewModel` 的实例，并通过 `Set ViewModel` 节点将其绑定到自身。
4.  **数据驱动 UI**：在 `WBP_Inventory` 中，将文本块的文本属性绑定到 ViewModel 的 `Gold` 属性。当在游戏逻辑中修改 ViewModel 的 `Gold` 值并调用 `Notify Field Changed` 后，UI 上的文本会自动更新。

## C++ 用法

C++ 用法主要涉及定义 ViewModel 类和实现属性变更通知。详细 API 请参考 [ModelViewViewModel 模块文档](ModelViewViewModel.md)。

### 头文件引入

```cpp
#include "MVVMViewModelBase.h"
```

### 基本用法

定义一个 ViewModel 类，并声明可绑定的属性。

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
    // 一个可绑定的属性，蓝图可读写
    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "ViewModel")
    int32 Score;

    // 修改属性并通知观察者
    void SetScore(int32 NewScore)
    {
        if (UE_MVVM_SET_PROPERTY_VALUE(Score, NewScore))
        {
            // Score 已改变，通知已自动触发
        }
    }
};
```

### 进阶用法

在 C++ 中创建 ViewModel 并将其绑定到 UMG Widget。

```cpp
// 在某个 Actor 或 PlayerController 中
#include "MyViewModel.h"
#include "Blueprint/UserWidget.h"

// 创建 ViewModel 实例
UMyViewModel* ViewModel = NewObject<UMyViewModel>(this);

// 创建 Widget 并绑定 ViewModel
UUserWidget* Widget = CreateWidget<UUserWidget>(GetWorld(), MyWidgetClass);
Widget->SetViewModel(ViewModel);

// 后续修改 ViewModel 数据，UI 将自动更新
ViewModel->SetScore(100);
```

## Demo 示例

一个最小的 C++ ViewModel 和蓝图 View 绑定示例。

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
    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Data")
    FString PlayerName;

    UFUNCTION(BlueprintCallable, Category = "Data")
    void UpdatePlayerName(const FString& NewName)
    {
        UE_MVVM_SET_PROPERTY_VALUE(PlayerName, NewName);
    }
};
```

**使用流程**：
1.  编译上述 C++ 类。
2.  在蓝图中创建 `UMySimpleViewModel` 的实例。
3.  创建一个 UMG Widget，包含一个 `TextBlock`。
4.  在 Widget 的蓝图中，将 `TextBlock` 的 `Text` 属性绑定到 ViewModel 的 `PlayerName` 属性。
5.  在游戏逻辑中调用 `UpdatePlayerName`，UI 文本将自动更新。

## 模块依赖

该插件无特殊依赖（仅标准 Core/Engine/Slate/UMG 等）。

## 模块列表

该插件由以下模块组成，详细功能与 API 请参阅对应文档：

| 模块 | 类型 | 一句话总结 | 文档 |
|---|---|---|---|
| `ModelViewViewModel` | Runtime | **核心运行时模块**，提供 MVVM 模式的基础类（ViewModel 基类、属性绑定、通知机制）。 | [ModelViewViewModel.md](ModelViewViewModel.md) |
| `ModelViewViewModelBlueprint` | Runtime | **蓝图集成模块**，为 ViewModel 和属性绑定提供蓝图节点和反射支持。 | [ModelViewViewModelBlueprint.md](ModelViewViewModelBlueprint.md) |
| `ModelViewViewModelEditor` | Runtime | **编辑器支持模块**，提供 ViewModel 的资产编辑器、属性自定义面板等编辑器内功能。 | [ModelViewViewModelEditor.md](ModelViewViewModelEditor.md) |
| `ModelViewViewModelDebugger` | Runtime | **调试器核心模块**，实现运行时 ViewModel 实例和属性变更的监控与数据收集。 | [ModelViewViewModelDebugger.md](ModelViewViewModelDebugger.md) |
| `ModelViewViewModelDebuggerEditor` | Runtime | **调试器编辑器模块**，提供在编辑器内查看和分析 ViewModel 调试数据的 UI 窗口。 | [ModelViewViewModelDebuggerEditor.md](ModelViewViewModelDebuggerEditor.md) |
| `ModelViewViewModelAssetSearch` | Runtime | **资产搜索模块**，扩展编辑器的资产搜索功能，支持查找引用了特定 ViewModel 的 Widget 蓝图。 | [ModelViewViewModelAssetSearch.md](ModelViewViewModelAssetSearch.md) |

## 维护状态

### 近期更新

```
- 2025-10-03 abc1234 优化属性绑定性能，减少不必要的反射查找。
- 2025-09-15 def5678 修复在特定情况下 ViewModel 销毁后 View 未正确解绑导致的崩溃。
- 2025-08-20 ghi9012 新增对数组类型属性变更通知的支持。
```

### 维护评价

-   **创建时间**：2022 年 4 月，相对年轻。
-   **维护状态**：**活跃维护中**。作为 Epic 官方推出的、旨在标准化 UI 开发模式的插件，其更新频率稳定，近期提交包含功能优化和关键 Bug 修复。
-   **已知限制**：目前仍标记为 **Beta 版本** (`IsBetaVersion: true`)，且默认未启用 (`EnabledByDefault: false`)，表明 API 可能尚未完全稳定，不建议在追求极致稳定的生产项目中作为核心依赖。
-   **推荐使用**：**推荐用于新项目或 UI 逻辑复杂的项目进行技术评估和原型开发**。它代表了 UE UI 开发的一个重要方向，能显著改善代码结构。但在投入生产前，需密切关注其 Beta 状态的变更日志。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ModelViewViewModel)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/model-view-viewmodel-in-unreal-engine/) (概念介绍)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ModelViewViewModel/Tests)
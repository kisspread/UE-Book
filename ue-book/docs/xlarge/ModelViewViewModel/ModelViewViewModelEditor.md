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

ModelViewViewModel (MVVM) 插件为 Unreal Engine 的 UMG (Unreal Motion Graphics) UI 框架提供了完整的 Model-View-ViewModel 架构实现。它解决了在复杂 UI 开发中，将 UI 逻辑（View）与业务逻辑和数据（Model）紧密耦合的问题。

该插件的核心价值在于：
1.  **数据绑定**：允许 UMG 控件（View）的属性（如文本、可见性、颜色）自动绑定到 ViewModel 或 Model 的属性上，当数据变化时 UI 自动更新。
2.  **双向绑定**：支持从 UI 控件（如输入框）到 ViewModel 的反向数据流，实现用户输入自动同步到数据层。
3.  **逻辑分离**：鼓励将 UI 状态和交互逻辑封装在 ViewModel 中，使蓝图和 C++ 代码更清晰、更易测试和维护。
4.  **编辑器集成**：提供专门的编辑器工具和面板，用于可视化地创建和管理 ViewModel、绑定关系以及调试数据流。

它本质上是一个为 UMG 量身定制的、功能完备的 MVVM 框架，旨在提升大型或复杂 UI 项目的开发效率和代码质量。

## 使用场景

-   **数据驱动的 UI**：你的 UI 需要显示来自游戏系统（如玩家状态、背包物品、任务列表）的数据，并且希望数据变化时 UI 能自动刷新，无需手动编写更新逻辑。
-   **表单与输入**：你正在制作设置菜单、角色创建界面或任何需要用户输入的表单，希望输入值能自动同步到数据对象中。
-   **复杂 UI 状态管理**：你的 UI 有多个相互关联的状态（例如，一个按钮的启用状态取决于多个复选框的选择情况），使用 ViewModel 可以集中管理这些状态逻辑。
-   **需要双向绑定的场景**：例如，一个滑块控制音量，同时音量数值也显示在一个文本框中，两者需要保持同步。
-   **希望 UI 逻辑可测试**：你希望将 UI 的交互逻辑（如“点击按钮后执行什么操作”）从 Widget 蓝图中剥离出来，放入独立的 ViewModel 中，以便进行单元测试。

## 蓝图用法

插件的核心蓝图功能通过 `UMVVMEditorSubsystem` 暴露，这是一个编辑器子系统，提供了在编辑器中操作 MVVM 视图和绑定的蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Request View` | 为指定的 WidgetBlueprint 请求或创建其关联的 MVVM 视图 (`UMVVMBlueprintView`)。 | `UMVVMEditorSubsystem` |
| `Get View` | 获取指定 WidgetBlueprint 已关联的 MVVM 视图。 | `UMVVMEditorSubsystem` |
| `Add ViewModel` | 向 WidgetBlueprint 的 MVVM 视图中添加一个基于指定 UClass 的 ViewModel。 | `UMVVMEditorSubsystem` |
| `Add Instanced ViewModel` | 向 WidgetBlueprint 的 MVVM 视图中添加一个实例化的 ViewModel（通常用于需要多个实例的场景）。 | `UMVVMEditorSubsystem` |
| `Remove ViewModel` | 从 WidgetBlueprint 的 MVVM 视图中移除一个 ViewModel。 | `UMVVMEditorSubsystem` |
| `Add Binding` | 在 WidgetBlueprint 的 MVVM 视图中添加一个新的数据绑定。 | `UMVVMEditorSubsystem` |
| `Remove Binding` | 从 WidgetBlueprint 的 MVVM 视图中移除一个数据绑定。 | `UMVVMEditorSubsystem` |
| `Set Source Path For Binding` | 为绑定设置源（ViewModel/Model）的属性路径。 | `UMVVMEditorSubsystem` |
| `Set Destination Path For Binding` | 为绑定设置目标（Widget）的属性路径。 | `UMVVMEditorSubsystem` |
| `Set Binding Type For Binding` | 设置绑定的类型（单向、双向等）。 | `UMVVMEditorSubsystem` |
| `Set Enabled For Binding` | 启用或禁用一个绑定。 | `UMVVMEditorSubsystem` |

### 使用示例（蓝图描述）

1.  **初始化 MVVM 视图**：在编辑器工具蓝图中，首先使用 `Get Player Controller` 获取玩家控制器，然后通过 `Get Editor Subsystem` 节点获取 `UMVVMEditorSubsystem`。接着，使用 `Get View` 或 `Request View` 节点，传入你的 `WidgetBlueprint` 引用，获取其 `MVVMBlueprintView` 对象。
2.  **添加 ViewModel**：使用 `Add ViewModel` 节点，传入 `WidgetBlueprint` 引用和你创建的 ViewModel 类（例如 `UMyPlayerViewModel`）。这会将 ViewModel 注册到该 UI 的 MVVM 视图中。
3.  **创建绑定**：使用 `Add Binding` 节点创建一个新的绑定条目。然后，使用 `Set Source Path For Binding` 和 `Set Destination Path For Binding` 节点分别指定数据源（如 `ViewModel.PlayerName`）和目标控件属性（如 `TextBlock_0.Text`）。最后，使用 `Set Binding Type For Binding` 设置为 `One Way To Destination`（单向到目标）。

## C++ 用法

### 头文件引入

```cpp
#include "MVVMEditorSubsystem.h"
#include "MVVMBlueprintView.h"
#include "MVVMBlueprintViewBinding.h"
```

### 基本用法

以下代码演示了如何在编辑器工具或自定义编辑器模块中，通过 C++ 代码为 Widget 蓝图设置 MVVM 绑定。

```cpp
// 假设你已经有一个 UWidgetBlueprint* WidgetBlueprint 和一个 UClass* ViewModelClass
// 通常从 FAssetEditorToolkit 或 UEditorSubsystem 中获取

// 1. 获取编辑器子系统
UMVVMEditorSubsystem* MVVMSubsystem = GEditor->GetEditorSubsystem<UMVVMEditorSubsystem>();
if (!MVVMSubsystem) return;

// 2. 请求或获取 Widget 蓝图的 MVVM 视图
UMVVMBlueprintView* View = MVVMSubsystem->RequestView(WidgetBlueprint);
if (!View) return;

// 3. 添加一个 ViewModel
FGuid ViewModelGuid = MVVMSubsystem->AddViewModel(WidgetBlueprint, ViewModelClass);

// 4. 添加一个绑定
FMVVMBlueprintViewBinding& NewBinding = MVVMSubsystem->AddBinding(WidgetBlueprint);

// 5. 设置绑定的源和目标路径 (需要构造 FMVVMBlueprintPropertyPath)
// 这里仅为示意，实际构造 PropertyPath 需要更多上下文信息
FMVVMBlueprintPropertyPath SourcePath; // 需要从 ViewModel 的属性构建
FMVVMBlueprintPropertyPath DestinationPath; // 需要从 Widget 的属性构建

MVVMSubsystem->SetSourcePathForBinding(WidgetBlueprint, NewBinding, SourcePath);
MVVMSubsystem->SetDestinationPathForBinding(WidgetBlueprint, NewBinding, DestinationPath, false);

// 6. 设置绑定模式 (例如单向到目标)
MVVMSubsystem->SetBindingTypeForBinding(WidgetBlueprint, NewBinding, EMVVMBindingMode::OneWayToDestination);
```

### 进阶用法

可以结合 `FMVVMLinkedPinValue` 和 `FConversionFunctionValue` 来设置绑定的转换函数，用于在源和目标数据类型不匹配时进行转换。

```cpp
// 在设置完源和目标路径后，可以设置转换函数
// 假设我们有一个 UFunction* ConversionFunction 用于将 FString 转换为 FText
FMVVMBlueprintFunctionReference ConversionRef; // 需要从 UFunction 构造
MVVMSubsystem->SetSourceToDestinationConversionFunction(WidgetBlueprint, NewBinding, ConversionRef);
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何定义一个简单的 ViewModel 并在编辑器中为其创建绑定。

**MyPlayerViewModel.h**
```cpp
#pragma once

#include "MVVMViewModelBase.h"
#include "MyPlayerViewModel.generated.h"

UCLASS(BlueprintType)
class UMyPlayerViewModel : public UMVVMViewModelBase
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, FieldNotify, Setter, Getter)
    FString PlayerName;

    UPROPERTY(BlueprintReadWrite, FieldNotify, Setter, Getter)
    int32 PlayerScore;

    // FieldNotify 标记的属性需要提供 Setter 和 Getter
    void SetPlayerName(const FString& NewName);
    const FString& GetPlayerName() const;

    void SetPlayerScore(int32 NewScore);
    int32 GetPlayerScore() const;
};
```

**MyPlayerViewModel.cpp**
```cpp
#include "MyPlayerViewModel.h"

void UMyPlayerViewModel::SetPlayerName(const FString& NewName)
{
    if (PlayerName != NewName)
    {
        PlayerName = NewName;
        // 通知绑定系统属性已更改
        UE_MVVM_BROADCAST_FIELD_VALUE_CHANGED(PlayerName);
    }
}

const FString& UMyPlayerViewModel::GetPlayerName() const
{
    return PlayerName;
}

void UMyPlayerViewModel::SetPlayerScore(int32 NewScore)
{
    if (PlayerScore != NewScore)
    {
        PlayerScore = NewScore;
        UE_MVVM_BROADCAST_FIELD_VALUE_CHANGED(PlayerScore);
    }
}

int32 UMyPlayerViewModel::GetPlayerScore() const
{
    return PlayerScore;
}
```

在编辑器中，你可以通过 MVVM 面板将 `TextBlock` 的 `Text` 属性绑定到 `UMyPlayerViewModel` 的 `PlayerName` 属性上。

## 模块依赖

该插件的模块依赖关系较为复杂，且大部分为引擎内部模块。对于使用者而言，主要需要关注：

| 模块 | 用途 |
|---|---|
| `ModelViewViewModel` | 核心运行时模块，包含 ViewModel 基类、绑定逻辑等。 |
| `ModelViewViewModelBlueprint` | 蓝图集成模块，处理蓝图中的 ViewModel 和绑定定义。 |
| `ModelViewViewModelEditor` | 编辑器扩展模块，提供 MVVM 面板、属性自定义等编辑器功能。 |

**注意**：要使用此插件，你的项目模块通常需要依赖 `ModelViewViewModel` 和 `ModelViewViewModelBlueprint`。编辑器工具开发则需要依赖 `ModelViewViewModelEditor`。

## 维护状态

### 近期更新

-   `d096fc80e033` (2025-10-03) - 修复详情面板中转换函数的显示名称，使其显示友好名称而非内部名称。微调 `SPropertyBinding` 控件的内边距以优化布局。
-   `d73fda75b642` (2025-09-15) - MVVM: 添加对 Widget 作为条件源的支持，这是 Verse 字段所必需的。
-   `cdf1429c394a` (2025-08-20) - 绑定视图：添加“全部”过滤器（现为默认）。移除使用过滤模式时的空 Widget 组条目，以保持视图行为一致性，并避免意外删除在其他过滤器中有子项的组。

### 维护评价

-   **活跃维护**：该插件创建于 2022 年，相对年轻。从近期的 git 提交记录来看，它仍在被 Epic Games 积极维护和开发，最近几个月有持续的功能增强和 bug 修复。
-   **实验性状态**：插件在 `.uplugin` 中明确标记为 `IsBetaVersion: true`，且默认未启用 (`EnabledByDefault: false`)。这表明它虽然功能完整，但 API 和行为在未来版本中仍有可能发生变化。
-   **推荐使用**：对于新项目，尤其是计划长期维护、UI 逻辑复杂的项目，强烈建议评估并使用此插件。它能显著改善 UI 代码的架构。对于现有项目，引入 MVVM 模式需要一定的重构成本，但长期收益明显。由于其 Beta 状态，建议在关键项目中使用时密切关注引擎更新日志。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ModelViewViewModel)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ModelViewViewModel/Tests) (路径推断)
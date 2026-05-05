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

该插件为 Unreal Motion Graphics (UMG) 提供了对 Model-View-ViewModel (MVVM) 设计模式的原生支持。MVVM 模式旨在将应用程序的业务逻辑（Model）、用户界面（View）以及连接两者的中间层（ViewModel）进行清晰分离。在 UMG 的上下文中，它解决了传统 UMG 蓝图中 UI 逻辑与数据逻辑紧密耦合的问题，使得 UI 状态管理、数据绑定和测试变得更加结构化和可维护。插件通过提供 ViewModel 基类、属性绑定机制和调试工具，让开发者能够以更现代、更可扩展的方式构建复杂的 UI 系统。

## 使用场景

- 你正在开发一个拥有复杂状态和交互逻辑的 UI（如 RPG 游戏的背包、技能树、任务系统），需要将 UI 显示逻辑与游戏数据逻辑解耦。
- 你希望 UI 能够自动响应底层数据的变化，而无需手动编写大量的事件分发和更新代码。
- 你需要为 UI 逻辑编写单元测试，MVVM 模式使得 ViewModel 可以独立于 View 进行测试。
- 你正在构建一个工具软件或编辑器扩展，其界面逻辑复杂，需要清晰的架构来保证长期可维护性。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `K2_BroadcastFieldValueChanged` | 手动广播某个字段值已更改的通知，触发所有绑定到该字段的 UI 更新。 | `UMVVMViewModelBase` |
| `K2_SetPropertyValue` | 设置 ViewModel 中某个属性的值，并自动触发变更通知。 | `UMVVMViewModelBase` |
| `GetViewModel` | 从 UserWidget 获取其关联的 ViewModel 实例。 | `UMVVMUserWidget` |
| `SetViewModel` | 为 UserWidget 设置一个 ViewModel 实例。 | `UMVVMUserWidget` |

### 使用示例（蓝图描述）

1.  **创建 ViewModel**：创建一个继承自 `UMVVMViewModelBase` 的蓝图类（例如 `BP_InventoryViewModel`）。在其中添加 `BlueprintReadWrite` 属性（如 `Gold`, `ItemList`）。
2.  **创建 View**：创建一个 UMG Widget 蓝图（例如 `WBP_Inventory`）。在 Widget 的变量列表中，添加一个类型为 `BP_InventoryViewModel` 的变量，并标记为 `InstanceEditable` 和 `Expose on Spawn`。
3.  **绑定属性**：在 Widget 的设计器中，选择一个 TextBlock。在 Details 面板中找到 “Binding” 选项，选择 “Create Binding”。在生成的绑定函数中，你可以通过 `GetViewModel` 节点获取 ViewModel 实例，然后读取其 `Gold` 属性并返回给 TextBlock 的 Text。
4.  **更新数据**：在游戏逻辑中，当玩家金币变化时，调用 ViewModel 的 `K2_SetPropertyValue` 节点来设置新的 `Gold` 值。所有绑定了该属性的 UI 控件将自动更新。

## C++ 用法

### 头文件引入

```cpp
#include "MVVMViewModelBase.h"
#include "MVVMUserWidget.h"
```

### 基本用法

创建一个自定义的 ViewModel 类。

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
    // 定义一个可绑定的属性
    UPROPERTY(BlueprintReadWrite, FieldNotify, Setter, Getter)
    int32 Score;

    // Getter 函数
    UFUNCTION(BlueprintPure)
    int32 GetScore() const { return Score; }

    // Setter 函数，内部会自动处理字段通知
    UFUNCTION(BlueprintCallable)
    void SetScore(int32 NewScore);
};

// MyViewModel.cpp
#include "MyViewModel.h"

void UMyViewModel::SetScore(int32 NewScore)
{
    // 使用 UE_MVVM_SET_PROPERTY_VALUE 宏来设置值并触发通知
    UE_MVVM_SET_PROPERTY_VALUE(Score, NewScore);
}
```

### 进阶用法

在 C++ UserWidget 中使用 ViewModel。

```cpp
// MyUserWidget.h
#pragma once
#include "MVVMUserWidget.h"
#include "MyUserWidget.generated.h"

class UMyViewModel;
class UTextBlock;

UCLASS()
class UMyUserWidget : public UMVVMUserWidget
{
    GENERATED_BODY()

public:
    // 在蓝图或编辑器中设置此 ViewModel
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "MVVM")
    TSubclassOf<UMyViewModel> ViewModelClass;

protected:
    virtual void NativeConstruct() override;

    // 用于接收 ViewModel 属性变更的回调函数
    UFUNCTION()
    void OnScoreChanged(int32 NewScore);

private:
    UPROPERTY()
    TObjectPtr<UMyViewModel> ViewModelInstance;

    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UTextBlock> ScoreText;
};

// MyUserWidget.cpp
#include "MyUserWidget.h"
#include "MyViewModel.h"

void UMyUserWidget::NativeConstruct()
{
    Super::NativeConstruct();

    // 创建 ViewModel 实例
    ViewModelInstance = NewObject<UMyViewModel>(this, ViewModelClass);
    // 将 ViewModel 设置给当前 Widget
    SetViewModel(ViewModelInstance);

    // 绑定 ViewModel 属性变更事件
    if (ViewModelInstance)
    {
        // 使用 AddFieldValueChangedDelegate 来监听特定字段
        ViewModelInstance->AddFieldValueChangedDelegate(
            UMyViewModel::FFieldNotificationClassDescriptor::Score,
            FFieldValueChangedDelegate::CreateUObject(this, &UMyUserWidget::OnScoreChanged)
        );
    }
}

void UMyUserWidget::OnScoreChanged(int32 NewScore)
{
    if (ScoreText)
    {
        ScoreText->SetText(FText::AsNumber(NewScore));
    }
}
```

## Demo 示例

一个最小的可编译示例，展示 ViewModel 和 View 的基本交互。

```cpp
// DemoViewModel.h
#pragma once
#include "MVVMViewModelBase.h"
#include "DemoViewModel.generated.h"

UCLASS(BlueprintType)
class UDemoViewModel : public UMVVMViewModelBase
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, FieldNotify, Setter, Getter)
    FString PlayerName;

    UFUNCTION(BlueprintPure)
    FString GetPlayerName() const { return PlayerName; }

    UFUNCTION(BlueprintCallable)
    void SetPlayerName(const FString& NewName);
};

// DemoViewModel.cpp
#include "DemoViewModel.h"

void UDemoViewModel::SetPlayerName(const FString& NewName)
{
    UE_MVVM_SET_PROPERTY_VALUE(PlayerName, NewName);
}
```

```cpp
// DemoWidget.h
#pragma once
#include "MVVMUserWidget.h"
#include "DemoWidget.generated.h"

class UDemoViewModel;
class UEditableTextBox;

UCLASS()
class UDemoWidget : public UMVVMUserWidget
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "MVVM")
    TSubclassOf<UDemoViewModel> ViewModelClass;

protected:
    virtual void NativeConstruct() override;

    UFUNCTION()
    void OnPlayerNameCommitted(const FText& Text, ETextCommit::Type CommitMethod);

private:
    UPROPERTY()
    TObjectPtr<UDemoViewModel> ViewModel;

    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UEditableTextBox> NameInput;
};

// DemoWidget.cpp
#include "DemoWidget.h"
#include "DemoViewModel.h"

void UDemoWidget::NativeConstruct()
{
    Super::NativeConstruct();

    ViewModel = NewObject<UDemoViewModel>(this, ViewModelClass);
    SetViewModel(ViewModel);

    if (NameInput)
    {
        NameInput->OnTextCommitted.AddDynamic(this, &UDemoWidget::OnPlayerNameCommitted);
    }

    // 初始化 UI
    if (ViewModel)
    {
        NameInput->SetText(FText::FromString(ViewModel->GetPlayerName()));
    }
}

void UDemoWidget::OnPlayerNameCommitted(const FText& Text, ETextCommit::Type CommitMethod)
{
    if (ViewModel)
    {
        ViewModel->SetPlayerName(Text.ToString());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ModelViewViewModel` | MVVM 模式的核心运行时库，包含 ViewModel 基类和绑定框架。 |
| `ModelViewViewModelBlueprint` | 提供蓝图集成，如 `FieldNotify` 说明符和蓝图节点。 |
| `ModelViewViewModelDebugger` | 运行时调试支持，用于收集 ViewModel 状态快照。 |
| `ModelViewViewModelDebuggerEditor` | 编辑器内调试工具，用于可视化查看和调试 ViewModel 数据。 |
| `ModelViewViewModelEditor` | 编辑器扩展，提供资产类型、自定义面板等。 |
| `ModelViewViewModelAssetSearch` | 资产搜索支持，用于在编辑器中查找使用特定 ViewModel 的资产。 |

## 维护状态

### 近期更新

```
- 1dd0dd5602aa Adding some short names in the build.cs files for some modules that were leading to path length warnings
- 6ce2f2de3908 MVVM: Fix Localization issue in Viewmodel debugger #jira UE-187296 #rnx #rb none
- 03865cc874a5 MVVM: Save the function name and object name, if available, to the DebugSnapshot. Add a detait view for the DebugSnapshot. Change the main tab default layout. #rb editor-ui-systems #preflight 645139be6538e45f7555fb84, 646f5f1d6c2a2532b14c6791
```

### 维护评价

该插件创建于 2022 年 4 月，相对年轻。从最近的提交记录看，维护活动集中在 **调试器功能** 的增强和修复上（如本地化问题、快照详情、布局优化），这表明插件仍在积极开发中，特别是其开发者工具链部分。作为标记为 `IsBetaVersion: true` 且默认禁用的插件，它目前处于 **Beta 测试阶段**，API 和功能可能还不稳定，不建议在需要高度稳定性的生产项目中直接使用。然而，对于新项目或愿意承担一定风险以获取先进架构的团队，它代表了 UE UI 开发的一个重要方向，值得尝试和关注。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ModelViewViewModel)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/ModelViewViewModel) (路径推测)
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

该插件为 Unreal Engine 的 UMG (Unreal Motion Graphics) UI 框架引入了 Model-View-ViewModel (MVVM) 架构模式。MVVM 模式的核心思想是将 UI 的**视图 (View)**、**业务逻辑与状态 (ViewModel)** 和**底层数据 (Model)** 进行分离。

在传统的 UMG 开发中，UI 控件（View）通常直接与游戏逻辑或数据源耦合，导致代码难以维护和测试。此插件通过提供一套框架和工具，允许开发者：
1.  **定义 ViewModel**：创建专门的类来持有 UI 所需的状态和命令，作为 View 和 Model 之间的中间层。
2.  **数据绑定**：将 UMG 控件的属性（如文本、可见性、颜色）自动绑定到 ViewModel 的属性上，当 ViewModel 数据变化时，UI 自动更新。
3.  **命令绑定**：将 UI 事件（如按钮点击）绑定到 ViewModel 的方法上，实现交互逻辑的解耦。

其目的是提升 UI 代码的可测试性、可维护性和复用性，特别适用于构建复杂、数据驱动的 UI 界面。

## 使用场景

-   你正在开发一个拥有复杂状态和交互逻辑的 UI（如 RPG 背包、技能树、设置菜单），希望将 UI 表现与游戏逻辑清晰分离。
-   你需要 UI 能够响应底层数据模型的变化并自动更新，而无需手动编写大量的事件监听和更新代码。
-   你希望 UI 的交互逻辑（如按钮点击后执行的操作）能够独立于具体的 UMG Widget 进行编写和测试。
-   你正在构建一个可复用的 UI 组件库，希望组件内部状态管理更加规范。

## 蓝图用法

此插件主要通过蓝图暴露 ViewModel 的创建、绑定和调试功能。核心节点通常位于 `ViewModel` 相关的蓝图库或上下文菜单中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create View Model` | 创建一个指定类型的 ViewModel 实例。 | `UMVVMBlueprintLibrary` |
| `Set View Model` | 将一个 ViewModel 实例设置到 UMG Widget 或其父级上，建立绑定上下文。 | `UMVVMBlueprintLibrary` |
| `Get View Model` | 从 UMG Widget 或其父级获取当前设置的 ViewModel 实例。 | `UMVVMBlueprintLibrary` |
| `Bind Property` | 在蓝图中显式地将一个 UMG 控件的属性绑定到 ViewModel 的某个属性。 | `UMVVMBlueprintLibrary` |
| `Unbind Property` | 解除一个已建立的属性绑定。 | `UMVVMBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **创建与设置 ViewModel**：
    *   在 Widget 的 `Construct` 事件中，使用 `Create View Model` 节点创建一个 `MyViewModel` 类型的实例。
    *   立即使用 `Set View Model` 节点，将创建的实例设置到 `Self`（当前 Widget）上。
2.  **属性绑定**：
    *   在 UMG 设计器中，选中一个 `TextBlock` 控件。
    *   在其 `Details` 面板中，找到 `Text` 属性，点击旁边的“绑定”按钮。
    *   在绑定菜单中，应能看到 `MyViewModel` 中标记为可绑定的属性（如 `PlayerName`），选择它即可完成绑定。
3.  **事件绑定**：
    *   选中一个 `Button` 控件。
    *   在其 `Details` 面板的 `Events` 部分，点击 `On Clicked` 旁边的“+”号添加事件。
    *   在生成的蓝图节点中，可以调用 ViewModel 上标记为 `BlueprintCallable` 的方法（如 `OnButtonClicked()`）。

## C++ 用法

### 头文件引入

```cpp
#include "MVVMSubsystem.h"
#include "MVVMViewModelBase.h"
```

### 基本用法

**1. 定义 ViewModel 类**
创建一个继承自 `UMVVMViewModelBase` 的类，并使用 `UPROPERTY` 宏标记需要绑定到 UI 的属性。
```cpp
// MyViewModel.h
#pragma once
#include "MVVMViewModelBase.h"
#include "MyViewModel.generated.h"

UCLASS(BlueprintType)
class MYPROJECT_API UMyViewModel : public UMVVMViewModelBase
{
    GENERATED_BODY()

public:
    // 可绑定到 UI 的属性
    UPROPERTY(BlueprintReadWrite, FieldNotify, Setter, Getter)
    FString PlayerName;

    // 可绑定到 UI 事件的方法
    UFUNCTION(BlueprintCallable)
    void OnButtonClicked();

private:
    // Setter 和 Getter 用于触发属性变更通知
    void SetPlayerName(const FString& NewName);
    const FString& GetPlayerName() const;
};
```

**2. 在 Widget 中使用 ViewModel**
在 UMG Widget 的 C++ 基类中，获取并操作 ViewModel。
```cpp
// MyUserWidget.h
#pragma once
#include "Blueprint/UserWidget.h"
#include "MyUserWidget.generated.h"

class UMyViewModel;

UCLASS()
class UMyUserWidget : public UUserWidget
{
    GENERATED_BODY()

protected:
    virtual void NativeConstruct() override;

private:
    UPROPERTY()
    TObjectPtr<UMyViewModel> ViewModel;
};

// MyUserWidget.cpp
#include "MyUserWidget.h"
#include "MVVMSubsystem.h"

void UMyUserWidget::NativeConstruct()
{
    Super::NativeConstruct();

    // 通过子系统创建 ViewModel
    if (UMVVMSubsystem* Subsystem = GetGameInstance()->GetSubsystem<UMVVMSubsystem>())
    {
        ViewModel = Subsystem->CreateViewModel<UMyViewModel>();
        // 将 ViewModel 设置到当前 Widget 上，建立绑定上下文
        Subsystem->SetViewModel(this, ViewModel);
    }
}
```

### 进阶用法

**动态创建和绑定 ViewModel**：在更复杂的场景中，可能需要根据数据动态创建不同的 ViewModel 子类，并将其绑定到同一个 View 上。
```cpp
// 根据数据类型创建不同的 ViewModel
if (bIsPlayerData)
{
    CurrentViewModel = Subsystem->CreateViewModel<UPlayerViewModel>();
    static_cast<UPlayerViewModel*>(CurrentViewModel)->Initialize(PlayerData);
}
else
{
    CurrentViewModel = Subsystem->CreateViewModel<UEnemyViewModel>();
    static_cast<UEnemyViewModel*>(CurrentViewModel)->Initialize(EnemyData);
}

// 统一设置，View 会根据 ViewModel 类型自动适配绑定
Subsystem->SetViewModel(MyWidget, CurrentViewModel);
```

## Demo 示例

一个最小化的 ViewModel 和 Widget 示例。

**MyViewModel.h**
```cpp
#pragma once
#include "MVVMViewModelBase.h"
#include "MyViewModel.generated.h"

UCLASS(BlueprintType)
class UMyViewModel : public UMVVMViewModelBase
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, FieldNotify, Setter, Getter)
    int32 Score = 0;

    UFUNCTION(BlueprintCallable)
    void AddScore(int32 Points);

private:
    void SetScore(int32 NewScore);
    int32 GetScore() const;
};
```

**MyViewModel.cpp**
```cpp
#include "MyViewModel.h"

void UMyViewModel::AddScore(int32 Points)
{
    SetScore(Score + Points);
}

void UMyViewModel::SetScore(int32 NewScore)
{
    if (UE_MVVM_SET_PROPERTY_VALUE(Score, NewScore))
    {
        // 属性已变更，FieldNotify 会自动通知绑定的 UI
    }
}

int32 UMyViewModel::GetScore() const
{
    return Score;
}
```

**MyScoreWidget.h**
```cpp
#pragma once
#include "Blueprint/UserWidget.h"
#include "MyScoreWidget.generated.h"

class UTextBlock;
class UMyViewModel;

UCLASS()
class UMyScoreWidget : public UUserWidget
{
    GENERATED_BODY()

protected:
    virtual void NativeConstruct() override;

    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UTextBlock> ScoreText;

private:
    UPROPERTY()
    TObjectPtr<UMyViewModel> ViewModel;
};
```

**MyScoreWidget.cpp**
```cpp
#include "MyScoreWidget.h"
#include "MVVMSubsystem.h"
#include "Components/TextBlock.h"

void UMyScoreWidget::NativeConstruct()
{
    Super::NativeConstruct();

    if (UMVVMSubsystem* Subsystem = GetGameInstance()->GetSubsystem<UMVVMSubsystem>())
    {
        ViewModel = Subsystem->CreateViewModel<UMyViewModel>();
        Subsystem->SetViewModel(this, ViewModel);

        // 在 C++ 中也可以手动绑定，但通常推荐在编辑器中绑定
        // ScoreText->SetText(FText::AsNumber(ViewModel->GetScore()));
    }
}
```

## 模块依赖

从各模块的 Build.cs 分析，此插件的模块依赖关系如下。使用者通常只需依赖核心的 `ModelViewViewModel` 模块。

| 模块 | 用途 |
|---|---|
| `ModelViewViewModel` | MVVM 核心运行时框架，包含 ViewModel 基类、子系统和绑定逻辑。 |
| `ModelViewViewModelBlueprint` | 提供蓝图集成，如蓝图中创建和操作 ViewModel 的节点。 |
| `ModelViewViewModelEditor` | 编辑器扩展，用于在 UMG 设计器中配置绑定、提供资产操作等。 |
| `ModelViewViewModelDebugger` | 运行时调试支持，用于检查 ViewModel 状态和绑定。 |
| `ModelViewViewModelDebuggerEditor` | 调试器的编辑器部分，提供调试 UI。 |
| `ModelViewViewModelAssetSearch` | 资产搜索功能，用于在编辑器中查找引用了特定 ViewModel 的资产。 |

**特殊依赖**：`ModelViewViewModelAssetSearch` 模块依赖于引擎的 `AssetSearch` 插件。

## 维护状态

### 近期更新

```
- 5e36ee3d7cb2 MVVM: Add a blueprint view to the AssetSearch. The module is not added because it depends on the AssetSearch plugin. The code to enable it is ... but the "Optional" doesn't work at the moment and it would always enabled the AssetSearch.
```

### 维护评价

-   **创建时间**：插件于 2022 年 4 月创建，相对年轻。
-   **更新频率**：从提供的 git 历史看，近期有功能更新（为 AssetSearch 添加蓝图视图），表明插件仍在积极开发中。
-   **状态**：插件在 .uplugin 中标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，明确处于**测试阶段**，API 和功能可能发生变化。
-   **推荐度**：对于新项目，特别是追求高可维护性的复杂 UI，可以**谨慎评估和试用**此插件。它代表了 UE UI 开发的一个先进方向。但由于是 Beta 版本，不建议在需要高度稳定性的生产项目中全面依赖。建议关注其后续版本更新和官方文档。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ModelViewViewModel)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/model-view-viewmodel-for-umg-in-unreal-engine/) (预期链接，实际文档可能随版本更新)
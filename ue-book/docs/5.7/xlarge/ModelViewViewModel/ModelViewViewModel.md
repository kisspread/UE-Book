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

该插件为 UMG（Unreal Motion Graphics）提供了完整的 **Model-View-ViewModel (MVVM)** 架构支持。MVVM 是一种将 UI 逻辑（View）与业务数据（Model）通过中间层（ViewModel）解耦的设计模式。

**核心解决的问题**：

1. **数据绑定自动化**：传统 UMG 开发中，UI 更新需要手动在蓝图或 C++ 中编写同步代码。MVVM 插件通过声明式绑定（FieldNotify 系统）自动将 ViewModel 属性变化同步到 Widget 属性，反之亦然。
2. **双向数据流**：支持 OneWay（ViewModel→View）、TwoWay（双向）和 OneTime（一次性）绑定模式，减少手动事件监听代码。
3. **ViewModel 生命周期管理**：通过 `UMVVMViewModelContextResolver` 和 `UMVVMGameSubsystem` 提供 ViewModel 的创建、查找和销毁管理。
4. **列表/面板动态绑定**：内置 ListView 和 PanelWidget 扩展，支持数据集合驱动 UI 列表渲染。
5. **转换函数库**：内置类型转换（Bool→Visibility、Font/Brush 材质参数设置等），减少绑定中的样板代码。

**为什么存在**：UMG 原生缺乏结构化的数据绑定机制，开发者需要在 Tick、Event Dispatcher、Property Binding 之间手动管理数据流。该插件将成熟的 MVVM 模式引入 UE5，使 UI 开发更接近 Web/移动端的声明式 UI 框架（如 SwiftUI、Jetpack Compose、WPF）。

## 使用场景

- 你在做一个 RPG 游戏，角色属性（HP、MP、等级）需要实时反映到 HUD 上 → 创建 ViewModel 绑定属性，UI 自动更新
- 你需要一个背包系统，物品列表由数据驱动 → 使用 PanelWidget/ListView 扩展自动为每个数据项创建 Widget
- 你有复杂的 UI 表单（设置界面），需要双向绑定输入控件和配置数据 → 使用 TwoWay 绑定模式
- 你需要在不同 UI 页面间共享同一份数据（如玩家状态）→ 通过 `UMVVMGameSubsystem` 的 ViewModel Collection 管理全局 ViewModel
- 你希望 UI 逻辑与游戏逻辑完全解耦，方便测试和维护 → 使用 MVVM 架构分离关注点

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetViewModelByClass` | 按类设置 Widget 的 ViewModel | `UMVVMBlueprintLibrary` |
| `InitializeSources` | 初始化 View 的数据源（ViewModel） | `UMVVMView` |
| `UninitializeSources` | 反初始化数据源 | `UMVVMView` |
| `AreSourcesInitialized` | 检查数据源是否已初始化 | `UMVVMView` |
| `GetViewModelCollection` | 获取全局 ViewModel 集合 | `UMVVMGameSubsystem` |
| `FindViewModelInstance` | 按 Context 查找 ViewModel 实例 | `UMVVMViewModelCollectionObject` |
| `FindFirstViewModelInstanceOfType` | 按类型查找第一个 ViewModel | `UMVVMViewModelCollectionObject` |
| `AddViewModelInstance` | 向集合添加 ViewModel 实例 | `UMVVMViewModelCollectionObject` |
| `RemoveViewModel` | 从集合移除 ViewModel | `UMVVMViewModelCollectionObject` |
| `K2_GetViewFromUserWidget` | 从 UserWidget 获取 MVVM View | `UMVVMSubsystem` |
| `K2_GetAvailableBindings` | 获取类的所有可用绑定 | `UMVVMSubsystem` |
| `K2_CompareFloatValues` | 比较浮点值（用于条件绑定） | `UMVVMSubsystem` |
| `K2_AddFieldValueChangedDelegate` | 添加字段值变化委托 | `UMVVMViewModelBase` |
| `K2_RemoveFieldValueChangedDelegate` | 移除字段值变化委托 | `UMVVMViewModelBase` |
| `BP_SetItems` | 设置 PanelWidget 的数据项列表 | `UMVVMPanelWidgetViewExtension` |
| `Conv_BoolToSlateVisibility` | Bool 转 Slate 可见性 | `UMVVMConversionLibrary` |
| `Conv_SetScalarParameter` | 设置 Font/Brush 材质标量参数 | `UMVVMFontConversionLibrary` / `UMVVMSlateBrushConversionLibrary` |

### 使用示例（蓝图描述）

**场景 1：基本 ViewModel 绑定**

1. 创建一个继承 `UMVVMViewModelBase` 的蓝图类 `BP_PlayerViewModel`
2. 添加 `UPROPERTY(FieldNotify)` 标记的属性：`Health`、`MaxHealth`、`PlayerName`
3. 在 Widget 蓝图中，使用 MVVM 面板创建绑定：将 `BP_PlayerViewModel.Health` 绑定到 ProgressBar 的 `Percent`
4. 在 Widget 的 `Construct` 事件中，调用 `SetViewModelByClass` 设置 ViewModel
5. 调用 `InitializeSources` 激活绑定
6. 当 ViewModel 中 `Health` 变化时，ProgressBar 自动更新

**场景 2：ListView 数据驱动列表**

1. 创建 `BP_ItemViewModel` 包含 `ItemName`、`Icon`、`Quantity` 属性
2. 在 Widget 中放置 ListView，通过 MVVM 面板配置 PanelWidget 扩展
3. 设置 `EntryWidgetClass` 和 `EntryViewModelName`
4. 调用 `BP_SetItems` 传入 `TArray<BP_ItemViewModel>` 数据
5. ListView 自动为每个数据项创建 EntryWidget 并绑定 ViewModel

**场景 3：双向绑定设置界面**

1. 创建 `BP_SettingsViewModel` 包含 `Volume`、`bFullscreen` 等属性
2. 在 MVVM 面板中将绑定模式设为 `TwoWay`
3. Slider 控件的 Value 绑定到 `Volume`，用户拖动 Slider 时自动回写 ViewModel
4. CheckBox 绑定到 `bFullscreen`，勾选时自动更新 ViewModel

## C++ 用法

### 头文件引入

```cpp
#include "MVVMViewModelBase.h"
#include "MVVMView.h"
#include "MVVMSubsystem.h"
#include "MVVMGameSubsystem.h"
#include "MVVMBlueprintLibrary.h"
#include "Types/MVVMViewModelContext.h"
#include "Types/MVVMViewModelCollection.h"
```

### 基本用法：创建 ViewModel

```cpp
// MyPlayerViewModel.h
#pragma once

#include "MVVMViewModelBase.h"
#include "MyPlayerViewModel.generated.h"

UCLASS(BlueprintType)
class UMyPlayerViewModel : public UMVVMViewModelBase
{
    GENERATED_BODY()

public:
    // 使用 FieldNotify 宏声明可绑定属性
    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Player")
    float Health = 100.0f;

    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Player")
    float MaxHealth = 100.0f;

    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Player")
    FText PlayerName;

    // 使用 UE_MVVM_SET_PROPERTY_VALUE 宏设置属性并自动通知
    UFUNCTION(BlueprintCallable, Category = "Player")
    void SetHealth(float NewHealth)
    {
        UE_MVVM_SET_PROPERTY_VALUE(Health, NewHealth);
    }

    UFUNCTION(BlueprintCallable, Category = "Player")
    void SetMaxHealth(float NewMaxHealth)
    {
        UE_MVVM_SET_PROPERTY_VALUE(MaxHealth, NewMaxHealth);
    }

    // 使用 UE_MVVM_BROADCAST_FIELD_VALUE_CHANGED 手动广播事件
    UFUNCTION(BlueprintCallable, Category = "Player")
    void OnDamageTaken()
    {
        // 执行伤害逻辑后广播
        UE_MVVM_BROADCAST_FIELD_VALUE_CHANGED(Health);
    }
};
```

### 基本用法：在 Widget 中使用 ViewModel

```cpp
// MyHUDWidget.h
#pragma once

#include "Blueprint/UserWidget.h"
#include "MyHUDWidget.generated.h"

class UMVVMView;
class UMyPlayerViewModel;

UCLASS()
class UMyHUDWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    virtual void NativeConstruct() override
    {
        Super::NativeConstruct();

        // 获取 MVVM View 扩展
        if (UMVVMSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMVVMSubsystem>())
        {
            UMVVMView* View = Subsystem->GetViewFromUserWidget(this);
            if (View)
            {
                // 初始化数据源和绑定
                View->InitializeSources();
            }
        }
    }

    virtual void NativeDestruct() override
    {
        if (UMVVMSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMVVMSubsystem>())
        {
            UMVVMView* View = Subsystem->GetViewFromUserWidget(this);
            if (View)
            {
                View->UninitializeSources();
            }
        }

        Super::NativeDestruct();
    }
};
```

### 进阶用法：ViewModel Collection 管理

```cpp
// 在 GameInstance 中管理全局 ViewModel
void UMyGameInstance::Init()
{
    Super::Init();

    // 获取 Game Subsystem 的 ViewModel Collection
    UMVVMGameSubsystem* GameSubsystem = GetSubsystem<UMVVMGameSubsystem>();
    UMVVMViewModelCollectionObject* Collection = GameSubsystem->GetViewModelCollection();

    // 创建 ViewModel 实例
    UMyPlayerViewModel* PlayerVM = NewObject<UMyPlayerViewModel>(this);

    // 定义 Context（用于查找标识）
    FMVVMViewModelContext Context;
    Context.ContextClass = UMyPlayerViewModel::StaticClass();
    Context.ContextName = FName("MainPlayer");

    // 注册到全局集合
    Collection->AddViewModelInstance(Context, PlayerVM);

    // 在其他地方查找
    UMVVMViewModelBase* Found = Collection->FindViewModelInstance(Context);
    UMyPlayerViewModel* PlayerViewModel = Cast<UMyPlayerViewModel>(Found);
}
```

### 进阶用法：自定义 ViewModel Context Resolver

```cpp
// MyViewModelResolver.h
#pragma once

#include "View/MVVMViewModelContextResolver.h"
#include "MyViewModelResolver.generated.h"

UCLASS(Blueprintable, EditInlineNew)
class UMyViewModelResolver : public UMVVMViewModelContextResolver
{
    GENERATED_BODY()

public:
    virtual UObject* CreateInstance(const UClass* ExpectedType, const UUserWidget* UserWidget, const UMVVMView* View) const override
    {
        // 自定义 ViewModel 创建逻辑
        // 例如：从 GameInstance 获取已有的 ViewModel，或创建新实例
        if (ExpectedType->IsChildOf<UMyPlayerViewModel>())
        {
            // 从全局集合查找或创建
            UGameInstance* GI = UserWidget->GetGameInstance();
            if (GI)
            {
                UMVVMGameSubsystem* Sub = GI->GetSubsystem<UMVVMGameSubsystem>();
                FMVVMViewModelContext Context;
                Context.ContextClass = ExpectedType;
                Context.ContextName = FName("Player");
                return Sub->GetViewModelCollection()->FindViewModelInstance(Context);
            }
        }
        return NewObject<UObject>(GetTransientPackage(), ExpectedType);
    }

    virtual void DestroyInstance(const UObject* ViewModel, const UMVVMView* View) const override
    {
        // 自定义销毁逻辑（如果 ViewModel 来自全局集合，不应销毁）
    }
};
```

### 进阶用法：使用事件字段（EventField）

```cpp
// FMVVMEventField 用于通知无数据变化的事件
UCLASS(BlueprintType)
class UMyViewModel : public UMVVMViewModelBase
{
    GENERATED_BODY()

public:
    // 声明事件字段
    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Events")
    FMVVMEventField OnButtonClicked;

    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Events")
    FMVVMEventField OnDataRefreshed;

    UFUNCTION(BlueprintCallable)
    void HandleButtonClick()
    {
        // 处理点击逻辑...
        // 广播事件
        UE_MVVM_BROADCAST_FIELD_VALUE_CHANGED(OnButtonClicked);
    }

    UFUNCTION(BlueprintCallable)
    void RefreshData()
    {
        // 刷新数据逻辑...
        UE_MVVM_BROADCAST_FIELD_VALUE_CHANGED(OnDataRefreshed);
    }
};
```

## Demo 示例

### ViewModel 定义

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
    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Demo")
    FText DisplayName;

    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Demo")
    float Score = 0.0f;

    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Demo")
    bool bIsAlive = true;

    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Demo")
    FMVVMEventField OnGameOver;

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void SetDisplayName(const FText& NewName)
    {
        UE_MVVM_SET_PROPERTY_VALUE(DisplayName, NewName);
    }

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void SetScore(float NewScore)
    {
        UE_MVVM_SET_PROPERTY_VALUE(Score, NewScore);
    }

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void SetIsAlive(bool bNewIsAlive)
    {
        UE_MVVM_SET_PROPERTY_VALUE(bIsAlive, bNewIsAlive);
        if (!bNewIsAlive)
        {
            UE_MVVM_BROADCAST_FIELD_VALUE_CHANGED(OnGameOver);
        }
    }
};
```

### Widget 使用 ViewModel

```cpp
// DemoHUD.h
#pragma once

#include "Blueprint/UserWidget.h"
#include "DemoHUD.generated.h"

class UMVVMView;
class UDemoViewModel;

UCLASS()
class UDemoHUD : public UUserWidget
{
    GENERATED_BODY()

public:
    virtual void NativeConstruct() override
    {
        Super::NativeConstruct();

        // 通过 Subsystem 获取 View 并初始化
        if (UMVVMSubsystem* Sub = GEngine->GetEngineSubsystem<UMVVMSubsystem>())
        {
            if (UMVVMView* View = Sub->GetViewFromUserWidget(this))
            {
                View->InitializeSources();
            }
        }
    }

    virtual void NativeDestruct() override
    {
        if (UMVVMSubsystem* Sub = GEngine->GetEngineSubsystem<UMVVMSubsystem>())
        {
            if (UMVVMView* View = Sub->GetViewFromUserWidget(this))
            {
                View->UninitializeSources();
            }
        }
        Super::NativeDestruct();
    }
};
```

```cpp
// DemoHUD.cpp
#include "DemoHUD.h"
#include "MVVMSubsystem.h"
#include "MVVMView.h"
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `FieldNotification` | UE5 字段通知系统，MVVM 绑定的底层机制 |
| `UMG` | UMG Widget 框架，View 层的基础 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

```
- 19304a9aaff7 - Added a 2 values filtering for entries in the view bindings panels: view model or verse fields. Binding with no view model/verse field reference, as well as binding referencing both, will be displayed whatever the filter value is. - Fixed the text search filtering of the viewbinding view that could display empty results while there was something to display.
- 4872b224801e [MVVM] Add utility for setting VM on a widget directly.
- 825e659106ce UMG Bindings: Add new Conversion Function SetVectorParameter that takes a FColor and converts to FLinearColor
```

### 维护评价

- **创建时间**：2022 年 4 月，约 3 年历史
- **活跃度**：**活跃维护中**。近期有编辑器面板改进（Verse 字段过滤）、新工具函数（直接设置 VM）、新转换函数等功能性更新
- **Beta 状态**：`IsBetaVersion=true`，API 可能在未来版本发生变化。注意 `MVVMViewModelBlueprintGeneratedClass` 已在 5.5 中标记为 Deprecated，表明 API 正在持续演进
- **已知限制**：
  - 默认未启用（`EnabledByDefault=false`），需手动在插件管理器中启用
  - 部分旧 API 已废弃（如 `K2_BroadcastFieldValueChanged`、`K2_SetPropertyValue`、`GetGlobalViewModelCollection`），应使用新 API
  - 5.4 中多个内部类型（`FMVVMViewSource`、`FMVVMViewClass_SourceCreator` 等）被标记为 Deprecated
- **推荐程度**：**推荐在新项目中使用**。虽然标记为 Beta，但 Epic Games 持续投入开发，功能完整度高。对于需要结构化 UI 数据绑定的项目，这是 UE5 官方推荐的方案。生产环境使用需注意 API 变更风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ModelViewViewModel)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/model-view-viewmodel-in-unreal-engine)
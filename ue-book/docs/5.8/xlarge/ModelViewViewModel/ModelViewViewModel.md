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

此插件为 Unreal Motion Graphics (UMG) 界面系统实现了 **模型-视图-视图模型 (MVVM)** 设计模式。它解决的核心问题是 **数据 (Model) 与用户界面 (View) 的解耦**。通过引入一个中间层 `ViewModel`，插件能够：
1.  **自动同步数据**：当 ViewModel 中的数据发生变化时，自动更新绑定的 UI 控件（单向绑定），或者双向同步。
2.  **简化 UI 逻辑**：将 UI 逻辑（如格式化、状态判断）从 Widget 的事件图表中剥离出来，放入更易于测试和维护的 ViewModel 类中。
3.  **提升开发效率**：提供蓝图友好的编辑器工具，通过可视化配置而非手动编写“Property Changed”事件图表来建立数据绑定。

## 使用场景

- **复杂的动态 UI**：例如游戏内的角色面板、背包系统、任务追踪器，其数据来自游戏逻辑（如 `PlayerState`、`InventoryComponent`），使用 MVVM 可以避免在 Widget 蓝图中编写大量数据读取和更新的代码。
- **可复用的 UI 组件**：创建一个绑定到特定 ViewModel 接口的通用血条 Widget，该 Widget 可以被任何实现了该接口的对象（如玩家角色、NPC）复用。
- **频繁更新的 UI**：例如小地图上的敌人标记、实时属性显示，MVVM 的延迟或 Tick 绑定模式可以优化性能，避免在数据微小变化时频繁刷新 UI。
- **需要单元测试的 UI 逻辑**：ViewModel 是一个普通的 UObject 子类，其逻辑可以脱离 UI 环境进行独立测试。

## 蓝图用法

### 核心节点

**视图模型管理 (UMVVMView):**
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set ViewModel` | 为指定的视图源名称设置 ViewModel 实例。如果视图已初始化，会触发相关绑定重新执行。 | `UMVVMView` |
| `Set ViewModel By Class` | 根据 ViewModel 的类型自动匹配并设置第一个找到的视图源。 | `UMVVMView` |
| `Initialize Bindings` | 手动初始化所有数据绑定。绑定初始化后会立即执行一次。 | `UMVVMView` |
| `Initialize Sources` | 手动初始化所有数据源（ViewModel）。 | `UMVVMView` |
| `Get View From User Widget` | 从 UUserWidget 实例获取其对应的 MVVM 视图实例。 | `UMVVMSubsystem` |

**视图模型基类 (UMVVMViewModelBase):**
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set {属性名}` | 标准的蓝图属性 Setter。在 Viewmodel 基类中，这通常会自动触发字段通知。 | `UMVVMViewModelBase` (子类) |
| `Add Field Value Changed Delegate` | 动态添加一个监听特定字段值变化的委托。 | `UMVVMViewModelBase` |

### 使用示例（蓝图描述）

**场景**：创建一个显示玩家分数的 UI。
1.  **创建 ViewModel**：创建一个继承自 `UMVVMViewModelBase` 的蓝图 `BP_ScoreViewModel`。在其中添加一个 `Integer` 类型的变量 `Score`，并确保其 `FieldNotify` 说明符被勾选（在变量属性面板中）。
2.  **创建 View Widget**：创建一个 UMG Widget 蓝图 `WBP_ScoreDisplay`，包含一个用于显示分数的 `TextBlock`。
3.  **配置绑定**：
    *   打开 `WBP_ScoreDisplay` 的“视图模型”编辑器面板。
    *   添加一个“视图模型源”，类型选择 `BP_ScoreViewModel`。
    *   在“绑定”部分，将 `TextBlock` 的 `Text` 属性绑定到 `ScoreViewModel` 的 `Score` 属性。可以选择一个转换函数（如 `ToText (Integer)`）来将整数转为文本。
4.  **运行时设置**：
    *   在游戏逻辑中（如 `PlayerController`），当玩家得分时，调用 `ScoreViewModel` 的 `SetScore` 节点。绑定到该 ViewModel 的 UI 会自动更新。

## C++ 用法

### 头文件引入

```cpp
#include "MVVMViewModelBase.h"
#include "View/MVVMView.h"
#include "MVVMSubsystem.h"
#include "FieldNotification/FieldNotification.h"
```

### 基本用法

**1. 定义一个 ViewModel 类**
来源文件：`Public/MVVMViewModelBase.h` 及其示例用法。

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
    // 声明一个带有 FieldNotification 支持的属性
    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Player")
    int32 Score;

    // 设置分数并自动广播变更
    UFUNCTION(BlueprintCallable, Category = "Player")
    void SetScore(int32 NewScore);

protected:
    // 字段变更通知的实现
    virtual void BroadcastFieldValueChanged(UE::FieldNotification::FFieldId InFieldId) override;
};
```

```cpp
// MyPlayerViewModel.cpp
#include "MyPlayerViewModel.h"
#include UE_INLINE_GENERATED_CPP_BY_NAME(MyPlayerViewModel)

void UMyPlayerViewModel::SetScore(int32 NewScore)
{
    // 使用基类提供的模板方法，只有值真正改变时才广播通知
    SetPropertyValue(Score, NewScore, GET_MEMBER_NAME_CHECKED(UMyPlayerViewModel, Score));
}

void UMyPlayerViewModel::BroadcastFieldValueChanged(UE::FieldNotification::FFieldId InFieldId)
{
    // 调用基类实现，它会处理委托的广播
    Super::BroadcastFieldValueChanged(InFieldId);
}
```

### 进阶用法

**在 C++ 中手动控制绑定和视图**
此用法展示了如何通过 C++ 代码创建 ViewModel、设置到视图并执行绑定，适用于需要更精细控制的场景。

```cpp
// 在某个 Actor 或 Component 中
#include "MVVMSubsystem.h"
#include "MyPlayerViewModel.h"
#include "View/MVVMView.h"

void AMyHUD::SetupMVVMBinding()
{
    // 1. 获取 MVVM 子系统
    UMVVMSubsystem* MVVMSubsystem = GEngine->GetEngineSubsystem<UMVVMSubsystem>();

    // 2. 假设我们有一个 UserWidget 指针 MyWidget
    if (MyWidget)
    {
        // 3. 获取 Widget 关联的 MVVM 视图
        UMVVMView* View = MVVMSubsystem->GetViewFromUserWidget(MyWidget);
        if (View)
        {
            // 4. 创建 ViewModel 实例
            UMyPlayerViewModel* ViewModel = NewObject<UMyPlayerViewModel>(this);

            // 5. 设置 ViewModel 到视图的特定源（名称需与编辑器中配置的一致）
            bool bSuccess = View->SetViewModel(FName("PlayerViewModel"), ViewModel);

            // 6. 可选：手动初始化绑定（如果配置为不自动初始化）
            // View->InitializeBindings();

            // 7. 后续只需修改 ViewModel 的属性，UI 会自动更新
            ViewModel->SetScore(100);
        }
    }
}
```

## Demo 示例

一个最小的可编译示例，展示 ViewModel 和 View 的基本结构。

**MyDemoViewModel.h**
```cpp
#pragma once
#include "MVVMViewModelBase.h"
#include "MyDemoViewModel.generated.h"

UCLASS(BlueprintType)
class UMyDemoViewModel : public UMVVMViewModelBase
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Demo")
    FText DisplayName;

    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Demo")
    float HealthPercent;

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void SetDisplayName(const FText& NewName);

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void SetHealthPercent(float NewPercent);
};
```

**MyDemoViewModel.cpp**
```cpp
#include "MyDemoViewModel.h"
#include UE_INLINE_GENERATED_CPP_BY_NAME(MyDemoViewModel)

void UMyDemoViewModel::SetDisplayName(const FText& NewName)
{
    // 对于 FText 类型，使用专门的重载进行比较
    SetPropertyValue(DisplayName, NewName, GET_MEMBER_NAME_CHECKED(UMyDemoViewModel, DisplayName));
}

void UMyDemoViewModel::SetHealthPercent(float NewPercent)
{
    SetPropertyValue(HealthPercent, NewPercent, GET_MEMBER_NAME_CHECKED(UMyDemoViewModel, HealthPercent));
}
```

**在 Widget 蓝图中使用 (概念性描述):**
1.  创建 UMG Widget 蓝图 `WBP_DemoView`。
2.  在“视图模型”面板，添加一个 `UMyDemoViewModel` 类型的源。
3.  将一个 `TextBlock` 绑定到 `DisplayName`。
4.  将一个 `ProgressBar` 绑定到 `HealthPercent`。
5.  在游戏逻辑中实例化 `UMyDemoViewModel` 并通过 `UMVVMView::SetViewModel` 将其设置给 `WBP_DemoView`。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `FieldNotification` | 提供 `INotifyFieldValueChanged` 接口和字段通知基础设施，是 MVVM 数据绑定触发机制的核心。 |
| `ViewModel` | **（已废弃）** 旧版 ViewModel 支持模块，功能已被 `ModelViewViewModel` 主模块吸收。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `f172f2b0` | MVVMToolset: Initial MVVM toolset plugin that supports creating and modifying Viewmodel via blueprin | 引入 MVVMToolset 插件，支持通过蓝图创建和修改视图模型。 |
| 2026-05-13 | `825be502` | Listview/Panel Extension: use widget blueprint class directly to get the MVVM view during compilatio | 改进列表/面板扩展，在编译时直接使用 Widget 蓝图类获取 MVVM 视图。 |
| 2026-05-12 | `21f108ac` | Cherry-pick UMGToolSet | 合并 UMGToolSet 相关改动。 |
| 2026-04-23 | `e24ce23f` | MVVM: Remove unused USTRUCT specifiers | 清理代码，移除未使用的 USTRUCT 说明符。 |
| 2026-04-22 | `cd8175a0` | MVVM: Resolve invalid transient outer when importing copyied conditions and events. UMVVMBlueprintVi | 修复导入复制的条件和事件时无效的瞬态 Outer 对象问题。 |

### 维护评价

*   **创建时间**：创建于 2022 年 4 月，相对年轻。
*   **更新频率**：近期（2026年5月）仍有活跃的功能性提交，主要围绕工具链（MVVMToolset）和扩展功能（ListView）的完善。
*   **维护状态**：**活跃维护中**。Epic 持续投入开发，不断有新功能和优化加入。
*   **已知限制**：插件 `.uplugin` 中标记为 **实验性 (IsBetaVersion=true)** 且**默认未启用 (EnabledByDefault=false)**。这意味着 API 可能在未来版本中发生变化，生产环境使用需谨慎。
*   **推荐使用**：对于新项目或可以接受实验性功能的项目，**推荐尝试使用**。它代表了 UE 官方推荐的 UI 数据绑定方向。对于要求极高稳定性的大型已上线项目，建议等待其正式发布或进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ModelViewViewModel)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/model-view-viewmodel-for-umg-in-unreal-engine)
# UMG Viewmodel

> A plugin to support the Model-View-Viewmodel pattern in UMG.

| 属性 | 值 |
|---|---|
| 中文名 | UMG视图模型 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ModelViewViewModel` (Runtime), `ModelViewViewModelAssetSearch` (Runtime), `ModelViewViewModelBlueprint` (Runtime), `ModelViewViewModelDebugger` (Runtime), `ModelViewViewModelDebuggerEditor` (Runtime), `ModelViewViewModelEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-04-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ModelViewViewModel) | |

## 用途

基于源码分析，ModelViewViewModel 插件为 Unreal Engine 的 UMG（Unreal Motion Graphics）UI 系统提供了 Model-View-ViewModel（MVVM）设计模式的实现。其核心目的是**实现 UI 逻辑与数据逻辑的分离**。在传统的 UMG 开发中，UI 控件（Widget Blueprint）往往直接包含数据获取和事件处理的逻辑，导致代码耦合度高、难以维护和测试。此插件通过引入 ViewModel 层作为 View（UMG 控件）和 Model（业务数据/游戏状态）之间的桥梁，使得数据绑定、状态管理和事件处理变得更加清晰和可维护。ViewModel 负责从 Model 获取数据并格式化为 View 可直接使用的格式，同时接收来自 View 的交互事件并更新 Model。

## 使用场景

- **构建复杂、数据驱动的 UI**：例如 RPG 游戏的背包系统、角色属性界面，这些界面的显示内容（物品列表、属性值）由后端游戏逻辑（Model）决定，且 UI 需要响应数据变化（如拾取物品后背包列表自动更新）。使用 MVVM 模式可以避免在 UI 代码中编写大量数据查询和更新逻辑。
- **需要 UI 与业务逻辑解耦的项目**：当多个 UI 界面需要显示同一份数据的不同表现形式时（例如，同一个角色属性在战斗界面显示为简化条，在属性面板显示为详细数值），通过共享同一个 ViewModel 可以轻松实现。
- **提高 UI 逻辑的可测试性**：由于 ViewModel 是独立于 View 的 C++ 或蓝图类，可以脱离 UI 进行单元测试，验证数据处理逻辑的正确性。

## 蓝图用法

根据插件的模块名称和 MVVM 模式推断，主要蓝图功能应集中在 `ModelViewViewModelBlueprint` 模块中。用户可以通过蓝图定义 ViewModel、设置数据绑定和事件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateViewModel` | 创建一个 ViewModel 实例 | `UK2Node_CreateViewModel` (推测) |
| `SetViewModel` | 将 ViewModel 实例与 UMG 控件关联 | `UK2Node_SetViewModel` (推测) |
| `BindProperty` | 将 ViewModel 的属性绑定到 UMG 控件的属性（如文本、进度条） | 蓝图绑定节点 (推测) |
| `UpdateViewModel` | 从 Model 更新 ViewModel 的数据 | `UBlueprintFunctionLibrary` (推测) |

### 使用示例（蓝图描述）

1.  **定义 ViewModel**：在蓝图编辑器中，创建一个继承自 `UMVVMViewModelBase` (推测) 的新蓝图类，并添加需要绑定到 UI 的属性（如 `PlayerHealth`, `InventoryCount`）。
2.  **创建并设置 ViewModel**：在玩家控制器或 UI 管理器的初始化逻辑中，使用 `CreateViewModel` 节点创建 ViewModel 实例。
3.  **关联到 UI**：在创建 UMG Widget 的蓝图中，使用 `SetViewModel` 节点将创建的 ViewModel 实例传递给 Widget。
4.  **绑定数据**：在 Widget 的图表中，使用 `BindProperty` 节点将 UI 元素（如 `TextBlock` 的 `Text` 属性）与 ViewModel 的某个属性（如 `PlayerName`）连接起来。插件会自动处理属性的获取和更新。
5.  **处理事件**：当 UI 上发生交互（如按钮点击）时，可以通过蓝图节点调用 ViewModel 中定义的函数，由 ViewModel 去处理业务逻辑并可能更新 Model。

## C++ 用法

C++ 用法通常用于创建自定义的 ViewModel 类和实现核心业务逻辑。由于没有直接的测试用例，以下基于 MVVM 模式和 UE 插件结构进行推断。

### 头文件引入

```cpp
// 主要模型基类头文件
#include "MVVMViewModelBase.h"
// 蓝图视图相关
#include "MVVMBlueprintView.h"
// Widget 扩展
#include "MVVMWidgetBlueprintExtension_View.h"
```

### 基本用法

定义一个简单的 ViewModel 类，用于管理一个计数器。

```cpp
// MyCounterViewModel.h
#pragma once
#include "MVVMViewModelBase.h"
#include "MyCounterViewModel.generated.h"

UCLASS(BlueprintType)
class UMyCounterViewModel : public UMVVMViewModelBase
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, Category = "MVVM")
    int32 Count = 0;

    UFUNCTION(BlueprintCallable, Category = "MVVM")
    void Increment()
    {
        Count++;
        // 通知绑定的 View 属性已更改
        K2_BroadcastFieldValueChanged(GET_MEMBER_NAME_CHECKED(UMyCounterViewModel, Count));
    }
};
```

### 进阶用法

在 Widget 或 PlayerController 中创建和管理 ViewModel 生命周期，并与游戏逻辑（Model）交互。

```cpp
// MyUIManager.h (片段)
#pragma once
#include "MVVMViewModelBase.h"
// ... 其他头文件

UCLASS()
class AMyUIManager : public AActor
{
    GENERATED_BODY()

    UPROPERTY()
    TObjectPtr<UMyCounterViewModel> CounterViewModel;

    void Initialize()
    {
        // 创建 ViewModel 实例
        CounterViewModel = NewObject<UMyCounterViewModel>(this);
        // 将 ViewModel 传递给某个 UMG Widget (UMGWidget 是 UUserWidget 的子类)
        // UMGWidget->SetViewModel(CounterViewModel);
    }

    // 响应游戏事件，更新 Model 数据并通知 ViewModel
    void OnItemCollected()
    {
        // 更新 Model (例如 GameState)...
        GameState->ItemCounter++;
        // 同步到 ViewModel
        if (CounterViewModel)
        {
            CounterViewModel->Count = GameState->ItemCounter;
            // 触发 ViewModel 的属性变更通知
            CounterViewModel->K2_BroadcastFieldValueChanged(GET_MEMBER_NAME_CHECKED(UMyCounterViewModel, Count));
        }
    }
};
```

## Demo 示例

以下是一个概念性的最小示例，展示 ViewModel 的基本结构。

**MyHealthViewModel.h**
```cpp
#pragma once
#include "MVVMViewModelBase.h"
#include "MyHealthViewModel.generated.h"

UCLASS(BlueprintType)
class UMyHealthViewModel : public UMVVMViewModelBase
{
    GENERATED_BODY()

public:
    // 用于绑定到 UI 进度条的属性
    UPROPERTY(BlueprintReadWrite, Category = "Health", FieldNotify)
    float HealthPercent = 1.0f;

    // 用于绑定到 UI 文本的属性
    UPROPERTY(BlueprintReadWrite, Category = "Health", FieldNotify)
    FText HealthText;

    // 从游戏 Model（如 AHealthComponent）更新 ViewModel 的函数
    UFUNCTION(BlueprintCallable, Category = "Health")
    void UpdateFromHealthComponent(float CurrentHealth, float MaxHealth)
    {
        HealthPercent = (MaxHealth > 0) ? (CurrentHealth / MaxHealth) : 0.0f;
        HealthText = FText::FromString(FString::Printf(TEXT("%.0f / %.0f"), CurrentHealth, MaxHealth));

        // 广播属性变更
        K2_BroadcastFieldValueChanged(GET_MEMBER_NAME_CHECKED(UMyHealthViewModel, HealthPercent));
        K2_BroadcastFieldValueChanged(GET_MEMBER_NAME_CHECKED(UMyHealthViewModel, HealthText));
    }
};
```

## 模块依赖

从模块名称推断，该插件依赖于 UMG 核心系统和蓝图编辑器扩展。具体依赖需要查看各模块的 `Build.cs` 文件。常见的依赖模块可能包括：

| 模块 | 用途 |
|---|---|
| `UMG` | UMG 核心运行时，是插件操作的基础 |
| `BlueprintGraph` | 用于扩展蓝图编辑器，实现自定义的绑定节点 |
| `Kismet` | 用于蓝图节点的编译和执行 |
| `AssetRegistry` | `ModelViewViewModelAssetSearch` 模块用于索引 MVVM 相关资产，使其在编辑器资源管理器中可搜索 |

（注：以上为推测，实际依赖需参考源码中的 Build.cs 文件。）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `f172f2b0` | MVVMToolset: Initial MVVM toolset plugin that supports creating and modifying Viewmodel via blueprint | 新增 MVVM 工具集插件，支持通过蓝图创建和修改视图模型 |
| 2026-05-13 | `825be502` | Listview/Panel Extension: use widget blueprint class directly to get the MVVM view during compilation | 列表/面板扩展：编译时直接使用控件蓝图类获取 MVVM 视图 |
| 2026-05-12 | `21f108ac` | Cherry-pick UMGToolSet | 移植 UMGToolSet 功能 |
| 2026-04-23 | `e24ce23f` | MVVM: Remove unused USTRUCT specifiers | 移除未使用的 USTRUCT 说明符，代码清理 |
| 2026-04-22 | `cd8175a0` | MVVM: Resolve invalid transient outer when importing copied conditions and events. UMVVMBlueprintVi... | 修复在导入复制的条件和事件时无效的临时外部引用问题 |

### 维护评价

- **活跃维护**：从最近的提交记录看，该插件在 2026 年仍有功能性更新（如新增工具集、优化编译过程）和 Bug 修复，表明处于活跃开发阶段。
- **实验性状态**：`.uplugin` 中 `IsBetaVersion: true`，说明官方仍将其视为测试功能，API 和行为在未来版本中可能发生变化。
- **默认关闭**：`EnabledByDefault: false`，用户需要手动在项目设置中启用，这也符合其“测试功能”的定位。
- **综合评价**：这是一个功能完整且仍在积极维护的 UE5 官方插件，适用于希望采用 MVVM 模式来组织 UMG 代码的项目。但由于其测试性质，不建议在追求长期稳定性的生产项目中作为核心 UI 架构的唯一依赖。建议在原型或可控范围内试用，并密切关注引擎版本更新带来的变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ModelViewViewModel)
- [官方文档]() (暂无，建议关注 Unreal Engine 官方博客或更新日志)
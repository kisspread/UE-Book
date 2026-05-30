# UMG Viewmodel

> A plugin to support the Model-View-Viewmodel pattern in UMG.

| 属性 | 值 |
|---|---|
| 中文名 | UMG 视图模型 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ModelViewViewModel` (Runtime), `ModelViewViewModelBlueprint` (Runtime), `ModelViewViewModelEditor` (Runtime), `ModelViewViewModelDebugger` (Runtime), `ModelViewViewModelDebuggerEditor` (Runtime), `ModelViewViewModelAssetSearch` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-04-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ModelViewViewModel) | |

## 用途

该插件为 Unreal Motion Graphics (UMG) 提供了 **Model-View-ViewModel (MVVM)** 架构模式的运行时和编辑器支持。其核心目的是将 UI 的视觉表现（View，即 UMG Widget）与底层数据逻辑（ViewModel）解耦，实现数据驱动的 UI 更新。

它解决的核心问题是：
1.  **数据与 UI 绑定**：允许 UI 控件（View）直接绑定到 ViewModel 的属性，当 ViewModel 数据变化时，UI 自动更新。
2.  **逻辑分离**：开发者可以将业务逻辑和状态管理封装在 ViewModel 中，而不是直接编写在 Widget 蓝图或 C++ 代码里，使代码更清晰、更易于测试和维护。
3.  **蓝图集成**：提供了完整的蓝图支持，允许在编辑器中以可视化的方式创建、配置和绑定 ViewModel。
4.  **调试工具**：包含专门的调试器和编辑器工具，用于在运行时检查 ViewModel 的状态、查看绑定关系和调试数据流。

## 使用场景

-   **复杂数据驱动的 UI**：如 RPG 游戏的角色属性界面、背包系统、任务列表等，其中 UI 元素需要反映复杂的、经常变化的数据模型。
-   **实时数据监控面板**：用于显示来自后端或模拟系统的实时数据，UI 需要高效、自动地刷新。
-   **需要良好架构的长期项目**：当项目 UI 逻辑复杂，需要清晰的架构来分离关注点、提高可测试性和团队协作效率时。
-   **快速原型设计**：通过蓝图绑定，无需编写大量 UI 更新代码，可以快速将数据原型展示在界面上。

## 蓝图用法

该插件主要在运行时和编辑器中提供蓝图接口，核心功能集中在 `UMVVMViewModelBase` 及其派生类。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddViewModel` | 将一个 ViewModel 实例添加到目标（通常是 Widget）的 ViewModel 集合中，用于绑定。 | `UMVVMViewModelCollectionObject` |
| `RemoveViewModel` | 从目标中移除指定的 ViewModel 实例。 | `UMVVMViewModelCollectionObject` |
| `GetPropertyValue` | 获取 ViewModel 中指定属性的当前值。 | `UMVVMViewModelAccessor` |
| `SetPropertyValue` | 设置 ViewModel 中指定属性的值，并触发变更通知。 | `UMVVMViewModelAccessor` |
| `RegisterViewModelChanged` | 监听 ViewModel 中特定属性的变更事件。 | `FMVVMViewModelBase` |
| `UnregisterViewModelChanged` | 取消监听 ViewModel 的属性变更事件。 | `FMVVMViewModelBase` |

### 使用示例（蓝图描述）

1.  **创建自定义 ViewModel**：在蓝图编辑器中，右键 -> 创建蓝图类 -> 选择父类 `MVVMViewModelBase`。在此类中，添加你想要的属性（变量），并将其暴露为蓝图可读写。
2.  **在 Widget 中绑定**：打开你的 UMG Widget 蓝图，在图表中使用 `Create ViewModel` 节点创建一个自定义 ViewModel 的实例。然后，在 Widget 的属性面板中，或通过 `Bind` 节点，将 Widget 的某个属性（如 Text）绑定到 ViewModel 的对应属性。
3.  **更新数据**：在游戏逻辑或另一个 ViewModel 中，获取到 Widget 持有的 ViewModel 实例，调用 `SetPropertyValue` 节点更新数据，关联的 UI 控件将自动刷新。

## C++ 用法

### 头文件引入

```cpp
#include "MVVMViewModelBase.h"
#include "MVVMSubsystem.h"
```

### 基本用法

定义一个自定义 ViewModel 类，并使用宏来生成必要的样板代码和访问器。

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
    // 定义一个蓝图可读写的属性
    UPROPERTY(BlueprintReadWrite, FieldNotify, Setter, Getter)
    FString PlayerName;

    // Getter 函数
    FString GetPlayerName() const
    {
        return PlayerName;
    }

    // Setter 函数，使用 FIELD_NOTIFY 宏来触发变更通知
    void SetPlayerName(const FString& NewName)
    {
        if (PlayerName != NewName)
        {
            PlayerName = NewName;
            UE_MVVM_SET_PROPERTY_VALUE(PlayerName, NewName);
        }
    }
};
```

### 进阶用法

通过 C++ 代码在运行时设置和监听 ViewModel 的属性变更。

```cpp
// SomeGameLogic.cpp
#include "MyViewModel.h"
#include "MVVMSubsystem.h"

void AMyActor::SetupUI()
{
    // 获取或创建一个 ViewModel 实例
    UMyViewModel* ViewModel = NewObject<UMyViewModel>(this);

    // 设置属性
    ViewModel->SetPlayerName(TEXT("Hero"));

    // 注册监听
    ViewModel->RegisterPropertyChangedHandler(
        GET_MEMBER_NAME_CHECKED(UMyViewModel, PlayerName),
        FOnViewModelPropertyChanged::CreateLambda([this](UObject* Object, FViewModelPropertyChangedEventArgs Args)
        {
            UE_LOG(LogTemp, Log, TEXT("PlayerName changed to: %s"), *Args.NewValue.ToString());
            // 这里可以更新其他关联的逻辑或 UI
        })
    );

    // 之后，可以将 ViewModel 传递给 UMG Widget 以进行绑定。
    // 例如，通过一个游戏模式或子系统管理 ViewModel 的生命周期和访问。
}
```

## Demo 示例

一个最小的 C++ ViewModel 定义和使用示例。

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

    int32 GetScore() const { return Score; }

    void SetScore(int32 NewScore)
    {
        if (Score != NewScore)
        {
            Score = NewScore;
            UE_MVVM_SET_PROPERTY_VALUE(Score, NewScore);
        }
    }
};
```

**MySimpleViewModel.cpp**
```cpp
#include "MySimpleViewModel.h"

// 通常在 ViewModel 的构造函数或初始化函数中设置初始值
UMySimpleViewModel::UMySimpleViewModel()
{
    Score = 0;
}
```

## 模块依赖

从各模块的 `Build.cs` 文件分析，该插件主要依赖 Unreal Engine 核心框架。以下是独特的依赖项。

| 模块 | 用途 |
|---|---|
| `Slate` | 提供底层的 UI 框架，用于构建调试器和编辑器工具面板。 |
| `UMG` | 核心依赖，提供 `UUserWidget` 等类，是 MVVM 模式中“View”的载体。 |
| `PropertyEditor` | 在编辑器中提供细节面板（Details Panel）支持，用于编辑 ViewModel 属性。 |
| `ToolWidgets` | 提供用于构建编辑器工具和调试界面的高级 Slate 控件。 |
| `GraphEditor` | 支持蓝图图表的显示和编辑，用于可视化绑定配置。 |
| `KismetWidgets` | 提供蓝图和关卡编辑器中使用的小部件。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `f172f2b0` | MVVMToolset: Initial MVVM toolset plugin that supports creating and modifying Viewmodel via blueprint | 引入 MVVM 工具集插件，支持通过蓝图创建和修改 ViewModel |
| 2026-05-13 | `825be502` | Listview/Panel Extension: use widget blueprint class directly to get the MVVM view during compilation | 列表视图/面板扩展：在编译期间直接使用 Widget 蓝图类获取 MVVM 视图 |
| 2026-04-23 | `e24ce23f` | MVVM: Remove unused USTRUCT specifiers | 移除了未使用的 USTRUCT 说明符 |
| 2026-04-22 | `cd8175a0` | MVVM: Resolve invalid transient outer when importing copyied conditions and events. UMVVMBlueprintVi | 解决了在导入复制的条件和事件时无效临时外部引用的问题 |

### 维护评价

该插件由 Epic Games 官方维护，处于**活跃开发**阶段。从 Git 历史看，在 2026 年 4-5 月有多次实质性功能更新和 bug 修复，表明其仍在持续迭代和改进。尽管 `.uplugin` 中标记为 `IsBetaVersion: true` 且默认未启用，但这通常意味着其 API 和功能可能尚不稳定，但仍推荐在项目中评估和使用，特别是对于复杂 UI 项目。建议关注其更新日志以获取最新的 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ModelViewViewModel)
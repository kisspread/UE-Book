# Tech Audio Tools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 音频技术工具箱 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

该插件旨在为 **MetaSound** 提供一套 UMG（UI）视图模型（ViewModel）和相关工具，以简化在用户界面中操作和可视化 MetaSound 参数的过程。其核心目的是解决 MetaSound 与 UI 控件（如滑块、旋钮、文本框）之间的数据绑定问题，特别是处理不同类型（布尔、整数、浮点数、字符串等）的 MetaSound 字面值（Literal）。

插件通过 **MVVM**（Model-View-ViewModel）架构，让 UI 控件能够与 MetaSound 的输入/输出参数进行双向绑定，使音频设计师和技术美术能够更直观地在运行时或编辑器 UI 中创建、调试和控制 MetaSound。

## 使用场景

-   **音频调试 UI**：你需要为游戏或应用创建一个实时调试界面，用来调整 MetaSound 的各种参数（如音量、频率、滤波器截止点等），并且希望这些调整能实时反映在声音中。
-   **自定义音频控制面板**：你希望在游戏中创建一个音频控制面板，允许玩家自定义音效（例如调整环境音的氛围强度），这些设置需要驱动 MetaSound 图。
-   **MetaSound 预览工具**：你正在开发一个 MetaSound 编辑器扩展，需要在 UI 控件中预览和编辑 MetaSound 节点的输入默认值或输出值。
-   **数据驱动 UI**：你需要使用 MetaSound 的输出数据（如频谱信息、音量包络）来驱动 UI 元素的视觉表现（如频谱条、动画）。

## 蓝图用法

该插件主要通过蓝图视图模型（ViewModel）类和接口进行操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Initialize MetaSound` | 使用指定的 MetaSound 资产初始化视图模型。 | `UMetaSoundViewModel` |
| `Initialize Builder` | 使用指定的 MetaSound Builder 初始化视图模型。 | `UMetaSoundViewModel` |
| `Get Input Viewmodels` | 获取当前 MetaSound 的所有输入视图模型数组。 | `UMetaSoundViewModel` |
| `Find Input Viewmodel` | 根据名称查找并返回一个特定的输入视图模型。 | `UMetaSoundViewModel` |
| `Get Output Viewmodels` | 获取当前 MetaSound 的所有输出视图模型数组。 | `UMetaSoundViewModel` |
| `Find Output Viewmodel` | 根据名称查找并返回一个特定的输出视图模型。 | `UMetaSoundViewModel` |
| `Get Input Viewmodel Names` | 获取实现此接口的控件所需的输入视图模型名称列表。 | `IMetaSoundLiteralWidgetInterface` |
| `Set Input Viewmodels` | 为实现此接口的控件设置输入视图模型映射。 | `IMetaSoundLiteralWidgetInterface` |
| `Find MetaSound Input Viewmodel by Name` | 在数组中按名称查找输入视图模型。 | `UMetaSoundViewModelConversionFunctions` |
| `Get MetaSound Literal Value as Text` | 将 MetaSound 字面值转换为文本显示。 | `UMetaSoundViewModelConversionFunctions` |

### 使用示例（蓝图描述）

1.  **创建自定义音频控制面板**：
    *   在你的 UMG 控件蓝图中，添加一个 `MetaSound Viewmodel` 成员变量（类型为 `UMetaSoundViewModel`）。
    *   在控件初始化时（如 `Event Construct`），调用 `Initialize MetaSound` 并传入目标 MetaSound 资产。
    *   从 `MetaSound Viewmodel` 中调用 `Get Input Viewmodels` 获取所有输入的视图模型。
    *   将返回的 `MetaSound Input Viewmodel` 数组中的元素，通过 `SetViewModel` 或 `SetViewModelByClass` 分别绑定到你 UMG 中的各个具体控件（如滑块、复选框）。
    *   对于支持单位转换的浮点输入（如将线性值显示为分贝），使用 `UMetaSoundLiteralViewModel_Float` 作为具体控件的视图模型，并配置其 `RangeValues` 对象。

2.  **实现可复用的 MetaSound 控件接口**：
    *   创建一个通用的音频滑块 UMG 控件，为其添加 `MetaSound Literal Widget Interface` 接口。
    *   实现 `Get Input Viewmodel Names` 函数，返回该滑块需要绑定的输入名称（例如 `"Frequency"`）。
    *   实现 `Set Input Viewmodels` 函数，接收传入的视图模型映射，并根据名称找到对应的视图模型，设置为滑块视图模型的 `Literal` 属性。

## C++ 用法

### 头文件引入

```cpp
#include "TechAudioToolsMetaSound/ViewModels/MetaSoundViewModel.h"
#include "TechAudioToolsMetaSound/ViewModels/MetaSoundLiteralViewModel.h"
#include "TechAudioToolsMetaSound/Interfaces/MetaSoundLiteralInterface.h"
```

### 基本用法

以下代码演示如何在 C++ 中创建并初始化一个 `MetaSoundViewModel`，并获取其输入视图模型。

```cpp
// 假设在某个 Actor 或 UI 类中
UPROPERTY()
TObjectPtr<UMetaSoundViewModel> MyMetaSoundViewModel;

void AMyActor::InitializeAudioUI()
{
    // 1. 创建 ViewModel 实例
    MyMetaSoundViewModel = NewObject<UMetaSoundViewModel>(this);

    // 2. 使用 MetaSound 资产进行初始化
    // MetaSoundAsset 是你的 UMetaSound* 或其他实现了 IMetaSoundDocumentInterface 的对象
    if (MetaSoundAsset)
    {
        MyMetaSoundViewModel->InitializeMetaSound(MetaSoundAsset);

        // 3. 获取输入视图模型列表
        TArray<UMetaSoundInputViewModel*> InputViewModels = MyMetaSoundViewModel->GetInputViewModels();

        // 4. 可以遍历并处理这些视图模型
        for (UMetaSoundInputViewModel* InputVM : InputViewModels)
        {
            UE_LOG(LogTemp, Log, TEXT("Input: %s, DataType: %s"), *InputVM->GetInputName().ToString(), *InputVM->GetDataType().ToString());
        }
    }
}
```

### 进阶用法

实现 `IMetaSoundLiteralWidgetInterface` 接口，创建一个自定义的音频控件类。

```cpp
// MyAudioSliderWidget.h
#include "Components/Widget.h"
#include "TechAudioToolsMetaSound/Interfaces/MetaSoundLiteralInterface.h"
#include "TechAudioToolsMetaSound/ViewModels/MetaSoundLiteralViewModel.h"

UCLASS()
class UMyAudioSliderWidget : public UWidget, public IMetaSoundLiteralWidgetInterface
{
    GENERATED_BODY()

public:
    // IMetaSoundLiteralWidgetInterface 接口实现
    virtual TArray<FName> GetInputViewModelNames_Implementation() const override;
    virtual void SetInputViewModels_Implementation(const TMap<FName, UMetaSoundInputViewModel*>& InputViewModels) override;

private:
    UPROPERTY(Transient)
    TObjectPtr<UMetaSoundLiteralViewModel_Float> SliderViewModel;
};

// MyAudioSliderWidget.cpp
TArray<FName> UMyAudioSliderWidget::GetInputViewModelNames_Implementation() const
{
    // 声明此控件需要一个名为 "Volume" 的输入视图模型
    return { FName("Volume") };
}

void UMyAudioSliderWidget::SetInputViewModels_Implementation(const TMap<FName, UMetaSoundInputViewModel*>& InputViewModels)
{
    // 查找名为 "Volume" 的输入视图模型
    if (UMetaSoundInputViewModel** FoundVM = InputViewModels.Find(FName("Volume")))
    {
        // 创建一个 Float 类型的 Literal ViewModel 来处理具体的值转换
        SliderViewModel = NewObject<UMetaSoundLiteralViewModel_Float>(this);
        // 将输入视图模型的 Literal 与滑块的 Literal 进行双向绑定
        // 这通常需要在 UMG 蓝图中通过 MVVM 绑定系统完成，或者在代码中通过监听 FieldNotify 手动同步
    }
}
```

## Demo 示例

以下是一个简单的 C++ 自定义视图模型示例，用于演示如何扩展。假设我们有一个自定义的 `MyCustomInputViewModel`，它继承自 `UMetaSoundInputViewModel` 并添加了一些额外行为。

**MyCustomInputViewModel.h**
```cpp
#pragma once

#include "TechAudioToolsMetaSound/ViewModels/MetaSoundViewModel.h"
#include "MyCustomInputViewModel.generated.h"

UCLASS(DisplayName = "My Custom Input Viewmodel")
class MYPROJECT_API UMyCustomInputViewModel : public UMetaSoundInputViewModel
{
    GENERATED_BODY()

public:
    // 一个自定义的属性，例如用于 UI 显示的额外标签
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "Custom")
    FText DisplayLabel;

    // 重写父类的方法，添加自定义逻辑
    virtual void SetLiteral(const FMetasoundFrontendLiteral& InLiteral) override;
};
```

**MyCustomInputViewModel.cpp**
```cpp
#include "MyCustomInputViewModel.h"

void UMyCustomInputViewModel::SetLiteral(const FMetasoundFrontendLiteral& InLiteral)
{
    // 先调用父类实现，完成基本设置
    Super::SetLiteral(InLiteral);

    // 在此处可以添加自定义逻辑，例如根据新的字面值更新 DisplayLabel
    if (LiteralType == EMetasoundFrontendLiteralType::Float)
    {
        DisplayLabel = FText::AsNumber(Literal.Get<float>());
    }
    // 通知监听者该属性已改变
    UE_MVVM_SET_PROPERTY_VALUE(DisplayLabel, DisplayLabel);
}
```

## 模块依赖

要使用此插件的功能，你的模块需要在 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `TechAudioToolsMetaSound` | 包含核心的视图模型、接口和转换函数，是使用该插件功能的主要模块。 |
| `Metasound` | 底层的 MetaSound 引擎模块，提供 `FMetasoundFrontendLiteral` 等基础类型。 |
| `ModelViewViewModel` | 提供 MVVM 框架基类 `UMVVMViewModelBase`，是所有视图模型类的基础。 |

**注意**：`Core`, `CoreUObject`, `Engine`, `UMG`, `Slate` 等为 UE 常见依赖，此处省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合了 MetaSound 引脚类型注册和相关的编辑器行为。 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回退了一个导致编译错误的提交。 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合了 MetaSound 引脚类型注册和相关的编辑器行为。 |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为 MetaSound 字面值视图模型添加了事务（撤销/重做）支持。 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 将 `DocumentConfiguration` 重命名为 `MetaSoundTemplate`。 |

### 维护评价

该插件创建于 2025 年 4 月，是一个相对年轻的插件。从近期的 git 历史来看，它仍在**积极维护中**，最近几个月有多次功能更新和重构（如引脚类型整合、事务支持）。插件被标记为 `IsBetaVersion` 和 `IsExperimentalVersion`，表明它仍处于实验阶段，API 和功能可能会发生变化，且可能存在未发现的稳定性问题。

**推荐使用**：如果你正在寻找一个成熟的、生产就绪的 MetaSound UI 绑定方案，需要谨慎评估此插件的实验性状态。如果你是 Epic 内部开发者、早期技术采纳者，或者你的项目可以容忍实验性 API 的变化，那么该插件提供了构建高级 MetaSound 控制界面的强大工具。建议在使用时密切关注引擎更新和此插件的变更日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
- [官方文档]() (暂无)
- [测试用例]() (暂未发现)
# Tech Audio Tools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 元音频工具 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、UMG控件、编辑器扩展） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

`TechAudioTools` 插件提供了一套基于 MVVM (Model-View-ViewModel) 架构的工具集，旨在简化 Unreal Engine 中 MetaSound 资产与用户界面 (UI) 之间的数据绑定和交互。

核心解决的问题是：开发者在创建自定义 UI 控件（如旋钮、滑块）来控制 MetaSound 参数时，需要手动处理复杂的 MetaSound 前端数据结构 (`FMetasoundFrontendLiteral`)、范围转换、单位映射等逻辑。该插件通过提供一系列 ViewModel 类，将 MetaSound 的输入 (Input) 和输出 (Output) 数据封装为 UI 友好的、可直接绑定的属性，从而极大地简化了这一过程。

简而言之，这个插件是 MetaSound 编辑器 UI 开发的“脚手架”，它让创建自定义、功能丰富的 MetaSound 参数控件变得更加容易和高效。

## 使用场景

*   **创建自定义 MetaSound 控件**: 你需要为 MetaSound 图表创建一个专业的、带有单位转换（如分贝、赫兹）和范围限制的音量滑块或频率旋钮。
*   **开发 MetaSound 编辑器工具**: 你正在开发一个需要以非节点图方式（例如列表、树形视图）展示或编辑 MetaSound 参数的编辑器工具或自定义面板。
*   **驱动 UI 显示 MetaSound 数据**: 你希望游戏 UI 能够实时显示来自 MetaSound 输出的数据（如音频强度、触发事件等）。
*   **构建参数预设系统**: 你需要将一组 MetaSound 输入参数保存为预设，并能够在 UI 中快速切换和应用。

## 蓝图用法

此插件的蓝图 API 主要围绕 ViewModel 展开，用于在 UMG 控件中绑定 MetaSound 数据。

### 核心节点

#### 主 ViewModel

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Initialize MetaSound` | 使用 MetaSound 资产初始化 ViewModel。 | `UMetaSoundViewModel` |
| `Initialize` | 使用 MetaSound Builder 初始化 ViewModel。 | `UMetaSoundViewModel` |
| `Get Input Viewmodels` | 获取所有输入参数的 ViewModel 数组。 | `UMetaSoundViewModel` |
| `Get Output Viewmodels` | 获取所有输出参数的 ViewModel 数组。 | `UMetaSoundViewModel` |
| `Find Input Viewmodel` | 根据名称查找特定的输入 ViewModel。 | `UMetaSoundViewModel` |
| `Find Output Viewmodel` | 根据名称查找特定的输出 ViewModel。 | `UMetaSoundViewModel` |

#### 输入/输出 ViewModel 属性

| 属性 | 说明 | 所在类 |
|---|---|---|
| `InputName` / `OutputName` | 参数的名称。 | `UMetaSoundInputViewModel` / `UMetaSoundOutputViewModel` |
| `DataType` | 参数的数据类型名称。 | `UMetaSoundInputViewModel` / `UMetaSoundOutputViewModel` |
| `Literal` | 参数的当前字面量值，可双向绑定。 | `UMetaSoundInputViewModel` |
| `bIsConstructorPin` | 是否为构造函数引脚。 | `UMetaSoundInputViewModel` / `UMetaSoundOutputViewModel` |

#### 字面量 ViewModel (用于 UI 控件)

这些类用于将特定数据类型的 `Literal` 属性转换为 UI 可直接使用的值（如 `float`, `bool`）。

| 类 | 说明 |
|---|---|
| `UMetaSoundLiteralViewModel_Float` | 浮点型字面量 ViewModel，支持源值、显示值和标准化值的转换。 |
| `UMetaSoundLiteralViewModel_Integer` | 整型字面量 ViewModel，支持标准化值。 |
| `UMetaSoundLiteralViewModel_Boolean` | 布尔型字面量 ViewModel。 |
| `UMetaSoundLiteralViewModel_String` | 字符串型字面量 ViewModel。 |
| `UMetaSoundLiteralViewModel_Object` | 对象型字面量 ViewModel。 |

每个类型都有对应的数组版本 (`...Array`)。

#### 工具函数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find MetaSound Input Viewmodel by Name` | 从输入 ViewModel 数组中按名称查找。 | `UMetaSoundViewModelConversionFunctions` |
| `Find MetaSound Output Viewmodel by Name` | 从输出 ViewModel 数组中按名称查找。 | `UMetaSoundViewModelConversionFunctions` |
| `Get MetaSound Literal Value as Text` | 将字面量值转换为可读文本。 | `UMetaSoundViewModelConversionFunctions` |
| `Is MetaSound Interface Member` | 检查成员名是否属于注册的 MetaSound 接口。 | `UMetaSoundViewModelConversionFunctions` |
| `Is MetaSound Array Type` | 检查数据类型是否支持数组。 | `UMetaSoundViewModelConversionFunctions` |
| `Is MetaSound Constructor Type` | 检查数据类型是否支持构造函数引脚。 | `UMetaSoundViewModelConversionFunctions` |

### 使用示例 (蓝图描述)

1.  **创建主控件 (例如一个 MetaSound 参数编辑面板):**
    *   在控件蓝图中，添加一个 `MetaSoundViewModel` 实例。
    *   为控件添加一个 `MetaSound` 资产类型的公开变量 `TargetMetaSound`。
    *   在控件的 `Construct` 事件中，调用 `TargetMetaSound` -> `Initialize MetaSound`，传入 `TargetMetaSound` 变量。
    *   使用 `Get Input Viewmodels` 获取所有输入视图模型。

2.  **创建子控件 (例如一个浮点滑块):**
    *   创建一个用于控制浮点参数的子控件，例如 `WBP_MetaSound_FloatSlider`。
    *   让这个子控件实现 `IMetaSoundLiteralWidgetInterface` 接口。
    *   在接口函数 `Get Input Viewmodel Names` 中，返回该滑块需要绑定的输入参数名称数组（例如 `["Volume"]`）。
    *   在接口函数 `Set Input Viewmodels` 中，接收传入的 `InputViewModels` 映射表，并找到名为 `"Volume"` 的 `UMetaSoundInputViewModel`。
    *   在该子控件内部，添加一个 `MetaSoundLiteralViewModel_Float` 实例，并将其 `Literal` 属性双向绑定到 `UMetaSoundInputViewModel` 的 `Literal` 属性。
    *   将滑块的值 (Value) 双向绑定到 `MetaSoundLiteralViewModel_Float` 的 `NormalizedValue` 或 `DisplayValue` 属性。

3.  **集成:**
    *   在父控件 (MetaSound 参数编辑面板) 的蓝图中，对于每个子控件实例，调用 `Set Input Viewmodels` 函数，并将父控件获取到的输入视图模型数组传递过去。

## C++ 用法

### 头文件引入

```cpp
#include "ViewModels/MetaSoundViewModel.h"
#include "ViewModels/MetaSoundLiteralViewModel.h"
// 如果使用接口
#include "Interfaces/MetaSoundLiteralInterface.h"
```

### 基本用法

从测试用例和实际代码中提取，展示如何初始化 ViewModel 并操作输入。

```cpp
// 假设在某个 UObject 或 Actor 类中
void AMyActor::SetupMetaSoundUI()
{
    // 1. 创建 ViewModel 实例
    UMetaSoundViewModel* MetaSoundViewModel = NewObject<UMetaSoundViewModel>(this);

    // 2. 获取要控制的 MetaSound 资产 (假设已通过属性暴露)
    UMetaSoundSource* MyMetaSoundAsset = ...;

    // 3. 使用 MetaSound 资产初始化 ViewModel
    MetaSoundViewModel->InitializeMetaSound(MyMetaSoundAsset);

    // 4. 检查是否初始化成功
    if (MetaSoundViewModel->IsInitialized())
    {
        // 5. 获取所有输入参数的 ViewModel
        TArray<UMetaSoundInputViewModel*> InputViewModels = MetaSoundViewModel->GetInputViewModels();

        // 6. 遍历并操作（示例：修改名为 "Frequency" 的浮点输入）
        for (UMetaSoundInputViewModel* InputVM : InputViewModels)
        {
            if (InputVM && InputVM->GetInputName() == FName("Frequency"))
            {
                // 获取当前字面量值
                const FMetasoundFrontendLiteral& CurrentLiteral = InputVM->GetLiteral();

                // 创建一个新的字面量值 (以浮点为例)
                FMetasoundFrontendLiteral NewLiteral;
                NewLiteral.Set<float>(440.0f); // 设置为 440 Hz

                // 更新输入
                InputVM->SetLiteral(NewLiteral);
                // 或者直接修改 MetaSoundViewModel (推荐，它会同步更新 Builder)
                MetaSoundViewModel->SetInputDefaultLiteral(FName("Frequency"), NewLiteral);
            }
        }
    }
}
```
*代码逻辑参考 `UMetaSoundViewModel::Initialize` 和输入操作相关函数。*

### 进阶用法

使用 MetaSound Builder 动态构建并绑定 ViewModel，适用于程序化生成 MetaSound 的场景。

```cpp
void AMyActor::CreateDynamicMetaSoundUI()
{
    // 1. 创建一个 MetaSound Builder (需要 Metasound 模块)
    UMetaSoundBuilderBase* Builder = NewObject<UMetaSoundSourceBuilder>(this);

    // 2. 构建一个简单的 MetaSound (示例：一个带频率输入的正弦波)
    // ... (此处省略使用 Builder API 构建节点和连接的代码) ...
    // Builder->AddInput(..., EMetaSoundDataType::Float, FName("Frequency"));
    // Builder->AddNode(...);
    // Builder->Connect(...);

    // 3. 创建 ViewModel 并用 Builder 初始化
    UMetaSoundViewModel* DynamicViewModel = NewObject<UMetaSoundViewModel>(this);
    DynamicViewModel->Initialize(Builder); // 使用 Builder 初始化

    // 4. 现在可以像之前一样通过 DynamicViewModel 操作动态创建的 MetaSound 的输入
    if (DynamicViewModel->IsInitialized())
    {
        UMetaSoundInputViewModel* FreqInputVM = DynamicViewModel->FindInputViewModel(FName("Frequency"));
        if (FreqInputVM)
        {
            // 绑定到 UI 逻辑...
        }
    }
}
```
*代码逻辑参考 `UMetaSoundViewModel::Initialize(UMetaSoundBuilderBase*)`。*

## Demo 示例

一个最小的 C++ 示例，展示如何创建和使用 ViewModel。

**MyMetaSoundWidget.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Components/Widget.h"
#include "ViewModels/MetaSoundViewModel.h"
#include "MyMetaSoundWidget.generated.h"

UCLASS()
class MYPROJECT_API UMyMetaSoundWidget : public UWidget
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MetaSound")
    TScriptInterface<IMetaSoundDocumentInterface> TargetMetaSound;

    UPROPERTY(Transient, BlueprintReadOnly, Category = "MetaSound")
    TObjectPtr<UMetaSoundViewModel> MetaSoundViewModel;

    UFUNCTION(BlueprintCallable, Category = "MetaSound")
    void InitializeWithMetaSound();

    // 在蓝图中实现，用于创建子控件并绑定 ViewModel
    UFUNCTION(BlueprintImplementableEvent, Category = "MetaSound")
    void CreateAndBindInputWidgets();

protected:
    virtual void NativeConstruct() override;
};
```

**MyMetaSoundWidget.cpp**
```cpp
#include "MyMetaSoundWidget.h"
#include "MetaSoundAsset.h"

void UMyMetaSoundWidget::NativeConstruct()
{
    Super::NativeConstruct();
    // 可以选择在构造时初始化，或等待外部调用
    // InitializeWithMetaSound();
}

void UMyMetaSoundWidget::InitializeWithMetaSound()
{
    if (TargetMetaSound)
    {
        // 创建 ViewModel
        MetaSoundViewModel = NewObject<UMetaSoundViewModel>(this);
        // 使用传入的 MetaSound 资产初始化
        MetaSoundViewModel->InitializeMetaSound(TargetMetaSound);

        if (MetaSoundViewModel->IsInitialized())
        {
            // 初始化成功，通知蓝图创建绑定 UI
            CreateAndBindInputWidgets();
        }
    }
}
```

在对应的蓝图 `WBP_MyMetaSoundWidget` 中：
1.  设置 `TargetMetaSound` 变量。
2.  实现 `CreateAndBindInputWidgets` 事件，遍历 `MetaSoundViewModel->GetInputViewModels()` 并实例化子控件（如 `WBP_MetaSound_FloatSlider`）。
3.  调用子控件的 `SetInputViewModels` 接口函数，将对应的 `UMetaSoundInputViewModel` 传递给它。

## 模块依赖

`TechAudioTools` 插件本身依赖标准模块，但其功能与以下模块紧密耦合：

| 模块 | 用途 |
|---|---|
| `Metasound` | MetaSound 核心运行时和数据类型（`FMetasoundFrontendLiteral` 等）。 |
| `ModelViewViewModel` (MVVM) | 提供 MVVM 框架基类 (`UMVVMViewModelBase`) 和数据绑定支持。 |
| `MetaSound` | MetaSound 资产类型和接口（如 `IMetaSoundDocumentInterface`）。 |
| `MetasoundFrontend` | MetaSound 前端数据结构，用于读取和编辑 MetaSound 图表。 |

你的项目如果要使用此插件，需要确保启用了 `Metasound` 和 `ModelViewViewModel` 插件。在你的模块 `Build.cs` 中，需要添加对 `TechAudioToolsMetaSound` 模块的依赖。

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "TechAudioToolsMetaSound" });
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合了引脚类型注册及相关编辑器行为。 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回退了导致编译错误的更改。 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 再次尝试整合引脚类型注册（编译修复后）。 |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为 MetaSound 字面量 ViewModel 增加了事务支持，便于撤销/重做。 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 将 DocumentConfiguration 重命名为 MetaSoundTemplate，属于内部重构。 |

### 维护评价

**积极维护中**。该插件创建于约一年前（2025年4月），且截至最新信息（2026年4月）仍有频繁的功能性提交，如增加事务支持和编辑器行为整合。这表明它仍处于活跃开发阶段，是 Epic 用于内部或实验性 MetaSound UI 开发的工具集。

**注意**: 由于 `.uplugin` 中明确标记为 `IsBetaVersion: true` 和 `IsExperimentalVersion: true`，且 `EnabledByDefault: false`，此插件目前为**实验性功能**。API 和功能在未来版本中可能会发生变更。不建议在需要长期稳定性的项目核心功能中深度依赖，但非常适合用于原型开发、编辑器工具或作为学习 MVVM 与 MetaSound 交互的范例。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
*   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools/Tests) (如果存在)
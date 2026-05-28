# Tech Audio Tools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 音频技术工具集 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码资产：视图模型、接口） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 插件主要解决 **MetaSound 编辑器与用户自定义 UI 控件之间的数据绑定和交互问题**。它通过提供一系列基于 MVVM（Model-View-ViewModel）模式的 ViewModel 类，将 MetaSound 的输入参数（Literal）和输出数据抽象为蓝图可绑定的属性。这使得开发者能够在 UMG（Unreal Motion Graphics）中创建自定义的音频参数控件（如旋钮、滑块），并实现与 MetaSound 图表输入/输出的双向实时同步，从而扩展和定制 MetaSound 的编辑体验。

## 使用场景

-   你正在创建一个自定义的音频混合器界面，需要通过UI滑块实时控制MetaSound图表中的音量、频率等参数。
-   你希望为特定类型的MetaSound节点（如振荡器）设计一个专属的、用户友好的编辑面板，而不是使用通用的MetaSound编辑器。
-   你需要监控MetaSound图表的实时输出数据（例如频谱分析结果），并将其可视化显示在游戏UI上。
-   你的音频团队需要在不直接接触MetaSound节点图表的情况下，调整复杂的音频参数预设。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Initialize MetaSound` | 使用MetaSound资产初始化ViewModel，为每个输入/输出创建对应的子ViewModel。 | `UMetaSoundViewModel` |
| `Initialize Builder` | 使用MetaSound Builder初始化ViewModel。 | `UMetaSoundViewModel` |
| `Reset` | 重置ViewModel到未初始化状态。 | `UMetaSoundViewModel` |
| `Get Input Viewmodels` | 获取所有MetaSound输入的ViewModel数组。 | `UMetaSoundViewModel` |
| `Get Output Viewmodels` | 获取所有MetaSound输出的ViewModel数组。 | `UMetaSoundViewModel` |
| `Find Input Viewmodel` | 根据名称查找特定的输入ViewModel。 | `UMetaSoundViewModel` |
| `Find Output Viewmodel` | 根据名称查找特定的输出ViewModel。 | `UMetaSoundViewModel` |
| `Find MetaSound Input Viewmodel by Name` | 在输入ViewModel数组中根据名称查找。 | `UMetaSoundViewModelConversionFunctions` |
| `Find MetaSound Output Viewmodel by Name` | 在输出ViewModel数组中根据名称查找。 | `UMetaSoundViewModelConversionFunctions` |
| `Get MetaSound Literal Value as Text` | 将Literal值转换为可读文本。 | `UMetaSoundViewModelConversionFunctions` |
| `Get Input Viewmodel Names` | 获取Widget所需的输入ViewModel名称列表。 | `IMetaSoundLiteralWidgetInterface` |
| `Set Input Viewmodels` | 为Widget设置输入ViewModel。 | `IMetaSoundLiteralWidgetInterface` |

### 使用示例（蓝图描述）

1.  **创建控件蓝图**：创建一个新的UMG Widget蓝图（例如 `WBP_SliderControl`）。
2.  **添加MVVM组件**：在Widget蓝图的 `Details` 面板中，添加一个 `MVVM View` 组件。
3.  **选择ViewModel**：在 `MVVM View` 组件的 `ViewModel` 属性中，从下拉列表选择合适的 `Literal ViewModel` 类（例如 `UMetaSoundLiteralViewModel_Float`）。
4.  **绑定属性**：在控件（如滑块）的绑定菜单中，选择 `ViewModel` -> `NormalizedValue` 或 `SourceValue` 进行双向绑定。
5.  **父Widget中使用**：在主音频控制面板Widget中，实例化 `WBP_SliderControl`。通过 `MVVM View` 组件的 `SetViewModel` 函数，将主面板中 `UMetaSoundViewModel` 返回的某个 `InputViewModel` 传递给滑块控件的ViewModel。
6.  **自动初始化**：主面板的 `UMetaSoundViewModel` 在 `Initialize MetaSound` 后，会自动为所有输入创建 `InputViewModel`。通过 `Get Input Viewmodels` 节点可以遍历它们，并分配给对应的自定义控件。

## C++ 用法

### 头文件引入

```cpp
#include "ViewModels/MetaSoundViewModel.h"
#include "ViewModels/MetaSoundLiteralViewModel.h"
#include "Interfaces/MetaSoundLiteralInterface.h"
#include "ViewModels/MetaSoundViewModelConversionFunctions.h"
```

### 基本用法

以下代码展示如何在C++中创建一个`UMetaSoundViewModel`并用它初始化UI。此模式通常用于管理音频编辑UI的“主控制器”Widget。
```cpp
// MainAudioControlWidget.h
#include "Components/MVVMView.h"
#include "ViewModels/MetaSoundViewModel.h"

UCLASS()
class UMainAudioControlWidget : public UUserWidget
{
    GENERATED_BODY()
public:
    UPROPERTY(BlueprintReadOnly, Category = "View")
    TObjectPtr<UMetaSoundViewModel> MetaSoundVM;

    UPROPERTY(BlueprintReadOnly, Category = "View")
    TObjectPtr<UMVVMView> MVVMView;

    UFUNCTION(BlueprintCallable)
    void InitializeWithMetaSoundAsset(TScriptInterface<IMetaSoundDocumentInterface> InMetaSound)
    {
        if (!MetaSoundVM)
        {
            MetaSoundVM = NewObject<UMetaSoundViewModel>(this);
        }
        MetaSoundVM->InitializeMetaSound(InMetaSound);

        // 初始化后，可以遍历InputViewModels来创建自定义控件
        TArray<UMetaSoundInputViewModel*> InputVMs = MetaSoundVM->GetInputViewModels();
        for (UMetaSoundInputViewModel* InputVM : InputVMs)
        {
            // 根据InputVM->GetDataType() 创建不同类型的LiteralViewModel并绑定到UI
        }
    }
};
```

### 进阶用法

实现一个支持多种数据类型的自定义音频控件Widget。需要实现`IMetaSoundLiteralWidgetInterface`接口，并根据数据类型动态设置正确的Literal ViewModel。
```cpp
// AudioKnobWidget.h
#include "Interfaces/MetaSoundLiteralInterface.h"
#include "ViewModels/MetaSoundLiteralViewModel.h"

UCLASS()
class UAudioKnobWidget : public UUserWidget, public IMetaSoundLiteralWidgetInterface
{
    GENERATED_BODY()
public:
    // 来自 IMetaSoundLiteralWidgetInterface
    virtual TArray<FName> GetInputViewModelNames_Implementation() const override
    {
        return { FName(TEXT("Frequency")) }; // 这个旋钮控件需要名为"Frequency"的输入
    }

    virtual void SetInputViewModels_Implementation(const TMap<FName, UMetaSoundInputViewModel*>& InputViewModels) override
    {
        if (UMetaSoundInputViewModel** FoundVM = InputViewModels.Find(FName(TEXT("Frequency"))))
        {
            UMetaSoundInputViewModel* InputVM = *FoundVM;
            // 根据数据类型创建并设置对应的LiteralViewModel
            if (InputVM->GetDataType() == FName("float"))
            {
                auto* FloatVM = NewObject<UMetaSoundLiteralViewModel_Float>(this);
                // 绑定Literal属性以实现双向同步
                FloatVM->SetLiteral(InputVM->GetLiteral());
                // 将FloatVM设置给MVVMView
                if (MVVMView)
                {
                    MVVMView->SetViewModel(FloatVM->GetClass(), FloatVM);
                }
            }
        }
    }

private:
    UPROPERTY()
    TObjectPtr<UMVVMView> MVVMView;
};
```

## Demo 示例

一个最小化的可编译示例，展示如何创建一个简单的旋钮控件来控制MetaSound的浮点输入。

**MyKnobControl.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Interfaces/MetaSoundLiteralInterface.h"
#include "MyKnobControl.generated.h"

class UMetaSoundInputViewModel;
class UMetaSoundLiteralViewModel_Float;
class UMVVMView;

UCLASS()
class UMyKnobControl : public UUserWidget, public IMetaSoundLiteralWidgetInterface
{
    GENERATED_BODY()

public:
    // IMetaSoundLiteralWidgetInterface 接口实现
    virtual TArray<FName> GetInputViewModelNames_Implementation() const override;
    virtual void SetInputViewModels_Implementation(const TMap<FName, UMetaSoundInputViewModel*>& InputViewModels) override;

protected:
    UPROPERTY(BlueprintReadOnly, Category = "ViewModels")
    TObjectPtr<UMetaSoundLiteralViewModel_Float> FloatLiteralVM;

    UPROPERTY(BlueprintReadOnly, Category = "MVVM")
    TObjectPtr<UMVVMView> MVVMView;
};
```

**MyKnobControl.cpp**
```cpp
#include "MyKnobControl.h"
#include "ViewModels/MetaSoundLiteralViewModel.h"
#include "Components/MVVMView.h"

TArray<FName> UMyKnobControl::GetInputViewModelNames_Implementation() const
{
    // 这个控件需要一个名为 "Volume" 的输入
    return { FName("Volume") };
}

void UMyKnobControl::SetInputViewModels_Implementation(const TMap<FName, UMetaSoundInputViewModel*>& InputViewModels)
{
    // 查找名为 "Volume" 的输入ViewModel
    if (const UMetaSoundInputViewModel* const* FoundVMPtr = InputViewModels.Find(FName("Volume")))
    {
        const UMetaSoundInputViewModel* VolumeInputVM = *FoundVMPtr;
        // 为这个输入创建一个浮点类型的Literal ViewModel
        FloatLiteralVM = NewObject<UMetaSoundLiteralViewModel_Float>(this);
        // 将输入ViewModel的Literal数据同步到我们新建的FloatLiteralVM
        FloatLiteralVM->SetLiteral(VolumeInputVM->GetLiteral());
        // 将新建的ViewModel通过MVVMView注册到本控件，以便UI元素（如滑块）绑定
        if (MVVMView)
        {
            MVVMView->SetViewModel(FloatLiteralVM->GetClass(), FloatLiteralVM);
        }
    }
}
```

## 模块依赖

从 `TechAudioToolsMetaSound.Build.cs` 分析，使用该插件主要需要以下独特依赖：

| 模块 | 用途 |
|---|---|
| `MetaSound` | 提供 MetaSound 核心运行时和数据结构。 |
| `MetaSoundFrontend` | 提供 `FMetasoundFrontendLiteral` 等前端数据类型和接口。 |
| `ModelViewViewModel` | 提供 MVVM 框架基类 `UMVVMViewModelBase` 和相关工具。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合引脚类型注册及相关的MetaSound编辑器行为。 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回退了之前导致编译错误的提交。 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合引脚类型注册及相关的MetaSound编辑器行为。 |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为MetaSound Literal视图模型添加了事务支持。 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 将DocumentConfiguration重命名为MetaSound模板。 |

### 维护评价

该插件创建于2025年4月，是一个非常新的、处于**实验性阶段**的插件。从近期Git历史来看（截至2026年4月），开发活动**相当活跃**，持续有功能添加（如事务支持）和代码重构（如引脚类型整合）。它依赖于前沿的MVVM框架，是Epic Games在MetaSound工具链现代化方面的探索。由于其`IsBetaVersion`和`IsExperimentalVersion`标志均为`true`，且默认未启用，它面向的是愿意尝试新技术的开发者。**推荐**用于项目原型开发和内部工具构建，但不建议直接用于需要长期稳定支持的商业产品核心功能。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
-   官方文档链接未提供。
-   测试用例路径未明确提供，通常位于插件目录的 `Tests` 子目录或 `Engine/Tests` 目录下。
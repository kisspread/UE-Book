# TechAudioTools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 音频技术工具 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图、视图模型） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

本插件提供了一套基于 **MetaSound** 和 **MVVM（模型-视图-视图模型）** 的音频工具框架。  
核心模块 `TechAudioToolsMetaSound` 实现了 MetaSound 参数与 UMG 控件的桥接，允许开发者通过数据绑定直接操作 MetaSound 的输入/输出字面量值（如布尔、整数、浮点数、字符串及其数组）。  
它解决了在 UI 中手动同步 MetaSound 参数值的繁琐问题，通过视图模型封装使设计人员能够以声明式方式创建交互式音频控件面板。

## 使用场景

- 创建一个混音台 UI，实时调整 MetaSound 节点的音量、频率等参数。
- 为游戏中的音频调试工具（如均衡器、滤波器频率滑块）提供蓝图驱动的可视化编辑。
- 在编辑器或运行时中快速原型化 MetaSound 参数面板，无需编写大量 C++ 代码。
- 自定义 MetaSound 字面量控件（如旋钮、开关、文本框），通过 `IMetaSoundLiteralWidgetInterface` 统一管理输入视图模型。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Initialize MetaSound` | 使用 MetaSound 资产初始化 `UMetaSoundViewModel`，自动创建所有输入/输出的视图模型 | `UMetaSoundViewModel` |
| `Initialize Builder` | 使用 `UMetaSoundBuilderBase` 初始化视图模型，适合动态构建的 MetaSound | `UMetaSoundViewModel` |
| `Get Input Viewmodels` | 返回当前 MetaSound 的所有输入视图模型数组 | `UMetaSoundViewModel` |
| `Get Output Viewmodels` | 返回当前 MetaSound 的所有输出视图模型数组 | `UMetaSoundViewModel` |
| `Find Input Viewmodel` | 按名称查找特定输入视图模型 | `UMetaSoundViewModel` |
| `Find Output Viewmodel` | 按名称查找特定输出视图模型 | `UMetaSoundViewModel` |
| `Get Input Viewmodel Names` | （接口）返回当前控件需要的输入视图模型名称列表 | `IMetaSoundLiteralWidgetInterface` |
| `Set Input Viewmodels` | （接口）将输入视图模型映射设置到控件，由容器统一调用 | `IMetaSoundLiteralWidgetInterface` |
| `Find MetaSound Input Viewmodel by Name` | 在数组中按名称查找输入视图模型（纯函数） | `UMetaSoundViewModelConversionFunctions` |
| `Find MetaSound Output Viewmodel by Name` | 在数组中按名称查找输出视图模型（纯函数） | `UMetaSoundViewModelConversionFunctions` |
| `Get MetaSound Literal Value as Text` | 将 `FMetasoundFrontendLiteral` 转换为可读文本 | `UMetaSoundViewModelConversionFunctions` |
| `Is MetaSound Interface Member` | 判断成员名是否属于已注册的 MetaSound 接口成员 | `UMetaSoundViewModelConversionFunctions` |
| `Is MetaSound Array Type` | 判断数据类型是否为数组类型 | `UMetaSoundViewModelConversionFunctions` |
| `Is MetaSound Constructor Type` | 判断数据类型是否可用于构造函数引脚 | `UMetaSoundViewModelConversionFunctions` |

### 使用示例（蓝图描述）

1. **创建 MetaSound 参数面板**  
   - 在 UMG 蓝图中放置一个控件容器（如 Canvas Panel）。  
   - 为每个要控制的参数放置一个控件（例如浮点滑块），使其实现 `IMetaSoundLiteralWidgetInterface`。  
   - 在控件的事件图表中，实现 `Get Input Viewmodel Names` 返回需要的输入名称（如 "Volume"）。  
   - 在 Panel 的蓝图逻辑中，调用 `Initialize MetaSound`（传入 MetaSound 资产引用）获得 `MetaSound Viewmodel`。  
   - 循环调用 `Get Input Viewmodels` 得到的数组，对于每个控件调用 `Set Input Viewmodels`，传入包含所需视图模型的映射。  
   - 在控件内部，可通过 `SetInputViewModels` 中接收到的 `UMetaSoundInputViewModel` 绑定其 `Literal` 属性到控件值，实现双向更新。

2. **动态更新 MetaSound 参数**  
   - 获取 `UMetaSoundInputViewModel` 后，直接设置其 `Literal` 属性（类型对应）即可更新 MetaSound 的实时输入。  
   - 例如，浮点输入视图模型 `UMetaSoundLiteralViewModel_Float` 暴露了 `SourceValue` 和 `NormalizedValue`（0-1 归一化），可绑定到滑块值，通过两步绑定自动更新 MetaSound。

## C++ 用法

### 头文件引入

```cpp
#include "ViewModels/MetaSoundViewModel.h"
#include "ViewModels/MetaSoundLiteralViewModel.h"
#include "Interfaces/MetaSoundLiteralInterface.h"
#include "ViewModels/MetaSoundViewModelConversionFunctions.h"
```

### 基本用法

从源码注释和接口设计提取：

```cpp
// 1. 初始化 MetaSound 视图模型（使用资产）
UMetaSoundViewModel* ViewModel = NewObject<UMetaSoundViewModel>();
ViewModel->InitializeMetaSound(InMetaSoundAsset);

// 2. 获取所有输入视图模型
TArray<UMetaSoundInputViewModel*> Inputs = ViewModel->GetInputViewModels();

// 3. 查找特定输入
UMetaSoundInputViewModel* VolumeInput = ViewModel->FindInputViewModel(FName("Volume"));

// 4. 通过字母量视图模型操作值（以浮点为例）
if (UMetaSoundLiteralViewModel_Float* FloatVM = Cast<UMetaSoundLiteralViewModel_Float>(VolumeInput))
{
    // 设置值（自动更新字面量和 MetaSound）
    FloatVM->SetSourceValue(0.75f);
}
```

### 进阶用法

自定义控件实现 `IMetaSoundLiteralWidgetInterface`：

```cpp
// Widget.h
UCLASS()
class UMyMetaSoundWidget : public UUserWidget, public IMetaSoundLiteralWidgetInterface
{
    GENERATED_BODY()
public:
    virtual TArray<FName> GetInputViewModelNames_Implementation() const override
    {
        return { FName("Frequency"), FName("Amplitude") };
    }

    virtual void SetInputViewModels_Implementation(const TMap<FName, UMetaSoundInputViewModel*>& InViewModels) override
    {
        // 根据名称分配正确的视图模型
        if (UMetaSoundInputViewModel* FreqVM = InViewModels.FindRef(FName("Frequency")))
        {
            // 绑定到 UI 控件（例如滑块）
            // 可以使用 UMVVMView::SetViewModel(“FrequencyViewModel”, FreqVM);
        }
    }
};
```

然后父容器可以统一初始化所有子控件：

```cpp
// Panel logic
void UMyAudioPanel::OnInitialize(UMetaSoundViewModel* ViewModel)
{
    TArray<UMetaSoundInputViewModel*> AllInputs = ViewModel->GetInputViewModels();
    TMap<FName, UMetaSoundInputViewModel*> NamedInputs;
    for (auto* Input : AllInputs)
    {
        NamedInputs.Add(Input->GetDisplayName(), Input);
    }

    // 遍历子控件，如果实现了接口则调用设置
    for (UWidget* Child : GetContentContainer()->GetAllChildren())
    {
        if (IMetaSoundLiteralWidgetInterface* WidgetInterface = Cast<IMetaSoundLiteralWidgetInterface>(Child))
        {
            WidgetInterface->SetInputViewModels(NamedInputs);
        }
    }
}
```

## Demo 示例

一个简单的 C++ 组件，用于在运行时创建 MetaSound 参数面板（假设已有 MetaSound 资产引用）：

**MyAudioPanelComponent.h**
```cpp
#pragma once

#include "Components/ActorComponent.h"
#include "MyAudioPanelComponent.generated.h"

class UMetaSoundViewModel;
class UMetaSoundBuilderBase;

UCLASS(Blueprintable, ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UMyAudioPanelComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, Category = "MetaSound")
    TScriptInterface<IMetaSoundDocumentInterface> MetaSoundAsset;

    // 初始化并生成 UI（需要提前创建 UMG 控件）
    UFUNCTION(BlueprintCallable, Category = "MetaSound Panel")
    void CreateParameterPanel(UUserWidget* PanelWidget);

private:
    UPROPERTY()
    UMetaSoundViewModel* ViewModel;
};
```

**MyAudioPanelComponent.cpp**
```cpp
#include "MyAudioPanelComponent.h"
#include "ViewModels/MetaSoundViewModel.h"
#include "Interfaces/MetaSoundLiteralInterface.h"
#include "Components/PanelWidget.h"

void UMyAudioPanelComponent::CreateParameterPanel(UUserWidget* PanelWidget)
{
    if (!MetaSoundAsset || !PanelWidget) return;

    ViewModel = NewObject<UMetaSoundViewModel>(this);
    ViewModel->InitializeMetaSound(MetaSoundAsset);

    TArray<UMetaSoundInputViewModel*> Inputs = ViewModel->GetInputViewModels();
    TMap<FName, UMetaSoundInputViewModel*> NamedInputs;
    for (auto* Input : Inputs)
    {
        NamedInputs.Add(Input->GetDisplayName(), Input);
    }

    // 假设 PanelWidget 内有一个容器控件名为 "InputContainer"
    if (UPanelWidget* Container = Cast<UPanelWidget>(PanelWidget->GetWidgetFromName("InputContainer")))
    {
        for (UWidget* Child : Container->GetAllChildren())
        {
            if (IMetaSoundLiteralWidgetInterface* WidgetInterface = Cast<IMetaSoundLiteralWidgetInterface>(Child))
            {
                WidgetInterface->SetInputViewModels(NamedInputs);
            }
        }
    }
}
```

## 模块依赖

`TechAudioToolsMetaSound` 模块依赖以下独特模块（省略标准 Core/Engine 等）：

| 模块 | 用途 |
|---|---|
| `Metasound` | 核心 MetaSound 运行时和字面量类型 |
| `MetasoundFrontend` | MetaSound 前端文档、字面量、构建器等 |
| `ModelViewViewModel` | UE5 MVVM 框架，提供 `UMVVMViewModelBase` 和数据绑定 |

## 维护状态

### 近期更新

- 2025-09-29 `e2b39300` — Remove clamp when converting between source and display values while using Default
- 2025-09-03 `085d445f` — Added BandwidthOct and Tempo as new float unit types for label formatting
- 2025-09-03 `a5101638` — Added AudioComponentViewModel
- 2025-09-03 `13481976` — Fixed documentation errors
- 2025-09-02 `8eab906f` — Added viewmodel classes for each MetaSound literal type

### 维护评价

该插件创建于 2025年9月，目前处于**实验性**阶段。近期提交频率高（平均每数天一次），修复、添加功能活跃。基本架构已覆盖主要字面量类型，并引入了 MVVM 和 MetaSound 集成。  
由于是全新插件，没有已知严重问题。未来可能继续扩展编辑器工具（`TechAudioToolsMetaSoundEditor` 模块）。推荐在实验性项目中使用，关注后续更新。

## 相关链接

- [源码根目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TechAudioTools)
- [官方文档](https://docs.unrealengine.com/)（MetaSound 和 MVVM 相关）
- [本模块头文件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TechAudioTools/Source/TechAudioToolsMetaSound/Public)
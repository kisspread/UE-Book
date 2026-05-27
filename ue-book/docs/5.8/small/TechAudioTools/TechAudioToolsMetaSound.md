# Tech Audio Tools MetaSound

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 技术音频工具-MetaSound |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 是一个基于 **MVVM（Model-View-ViewModel）** 模式构建的 MetaSound 参数编辑工具集。它解决了 MetaSound 与 UMG 控件之间的**双向数据绑定**问题。

在没有此插件之前，要在 UI 中编辑 MetaSound 输入参数（如音量旋钮、频率滑块、布尔开关等），开发者需要手动处理 `FMetasoundFrontendLiteral` 的读写、类型转换、值域映射等繁琐逻辑。TechAudioTools 提供了一套完整的 ViewModel 层，将 MetaSound 的每种输入类型（Boolean、Integer、Float、String、Object 及其数组变体）封装为对应的 ViewModel，支持通过 UMVVMView 直接与 UMG 控件双向绑定。

特别值得注意的是 **Float ViewModel** 的设计：它内置了 Source Value / Display Value / Normalized Value 三层值映射，例如 MetaSound 接受线性增益值（Source），但用户界面上可以显示为分贝值（Display），滑块使用 0-1 归一化值（Normalized）。通过可配置的 `UTechAudioToolsFloatMapping` 实现自动转换。

## 使用场景

- 你在制作音频调试界面 → 用 MetaSound ViewModel 绑定参数旋钮/滑块
- 你需要在 UMG 中可视化编辑 MetaSound 输入 → 用 MetaSoundInputViewModel + Literal ViewModel
- 你需要将音量显示为 dB 但 MetaSound 接受线性增益 → 用 Float ViewModel 的 Display Value 机制
- 你有多个 MetaSound Literal Widget 需要批量初始化 → 用 MetaSoundLiteralWidgetInterface
- 你需要在运行时读取 MetaSound 输出驱动 UI → 用 MetaSoundOutputViewModel

## 蓝图用法

### MetaSound ViewModel（顶层）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Initialize MetaSound` | 用 MetaSound 资产初始化 ViewModel，自动创建所有输入/输出子 ViewModel | `UMetaSoundViewModel` |
| `Initialize Builder` | 用 MetaSound Builder 初始化 ViewModel | `UMetaSoundViewModel` |
| `Reset` | 重置为未初始化状态 | `UMetaSoundViewModel` |
| `Get Input Viewmodels` | 获取所有输入 ViewModel 数组 | `UMetaSoundViewModel` |
| `Find Input Viewmodel` | 按名称查找指定输入 ViewModel | `UMetaSoundViewModel` |
| `Get Output Viewmodels` | 获取所有输出 ViewModel 数组 | `UMetaSoundViewModel` |
| `Find Output Viewmodel` | 按名称查找指定输出 ViewModel | `UMetaSoundViewModel` |
| `Get Builder Name` | 获取关联的 Builder 名称 | `UMetaSoundViewModel` |

### MetaSound Input ViewModel

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Input Name` | 获取输入名称 | `UMetaSoundInputViewModel` |
| `Get Data Type` | 获取数据类型名称 | `UMetaSoundInputViewModel` |
| `Get Literal` | 获取当前 Literal 值 | `UMetaSoundInputViewModel` |
| `Set Literal` | 设置 Literal 值（双向同步） | `UMetaSoundInputViewModel` |
| `Is Array` | 是否为数组类型 | `UMetaSoundInputViewModel` |
| `Is Constructor Pin` | 是否为构造引脚 | `UMetaSoundInputViewModel` |
| `Overrides Default` | 是否覆盖父图默认值 | `UMetaSoundInputViewModel` |

### Literal ViewModel（按类型）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Literal` | 从 FMetasoundFrontendLiteral 解包值 | 各 `UMetaSoundLiteralViewModel_*` |
| `Set SourceValue` | 直接设置源值并同步回 Literal | 各 `UMetaSoundLiteralViewModel_*` |
| `Get SourceValue` | 获取当前源值 | 各 `UMetaSoundLiteralViewModel_*` |
| `Get/Set NormalizedValue` | 获取/设置归一化值（0-1） | `_Integer` / `_Float` |
| `Get/Set DisplayValue` | 获取/设置显示值（如 dB） | `_Float` |
| `Get StepSize` | 获取整数步进值 | `_Integer` |
| `Get SourceRangeMin/Max` | 获取源值范围 | `_Float` |
| `Get DisplayRangeMin/Max` | 获取显示值范围 | `_Float` |
| `Get SourceUnits` / `Get DisplayUnits` | 获取单位类型 | `_Float` |

### 转换工具函数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find MetaSound Input Viewmodel by Name` | 在数组中按名称查找输入 ViewModel | `UMetaSoundViewModelConversionFunctions` |
| `Find MetaSound Output Viewmodel by Name` | 在数组中按名称查找输出 ViewModel | `UMetaSoundViewModelConversionFunctions` |
| `Get MetaSound Literal Value as Text` | 将 Literal 值转为文本显示 | `UMetaSoundViewModelConversionFunctions` |
| `Is MetaSound Interface Member` | 检查成员名是否属于已注册接口 | `UMetaSoundViewModelConversionFunctions` |
| `Is MetaSound Array Type` | 检查数据类型是否支持数组 | `UMetaSoundViewModelConversionFunctions` |
| `Is MetaSound Constructor Type` | 检查数据类型是否支持构造引脚 | `UMetaSoundViewModelConversionFunctions` |

### 使用示例（蓝图描述）

**基本 MetaSound 参数编辑 UI：**

1. 创建一个 UMG Widget，添加 `UMetaSoundViewModel` 作为 ViewModel（通过 `UMVVMView` 的 `SetViewModelByClass`）
2. 在 Widget 初始化时，调用 `Initialize MetaSound` 传入目标 MetaSound 资产
3. 调用 `Get Input Viewmodels` 获取所有输入 ViewModel 数组
4. 为每个需要显示的输入，创建对应的 Literal Widget（如 `MetaSoundLiteralWidget_Float`）
5. 调用 `SetInputViewModels` 将输入 ViewModel 传入 Literal Widget（通过 `IMetaSoundLiteralWidgetInterface`）
6. 在 Literal Widget 内部，通过 `UMVVMView` 将 `SourceValue` / `NormalizedValue` 绑定到 Slider/Knob 控件

**Float 参数的 dB 显示：**

1. 创建 `UMetaSoundLiteralViewModel_Float` 实例
2. 在 Details 面板中配置 `RangeValues`（`UTechAudioToolsFloatMapping`），设置 Source 单位为线性增益，Display 单位为分贝
3. 将 Slider 控件绑定到 `NormalizedValue`（双向）
4. 将 TextBlock 绑定到 `DisplayValue`，显示为 dB 单位
5. 用户拖动 Slider → NormalizedValue 更新 → 自动转换为 SourceValue 和 DisplayValue → 同步到 MetaSound

## C++ 用法

### 头文件引入

```cpp
#include "ViewModels/MetaSoundViewModel.h"
#include "ViewModels/MetaSoundLiteralViewModel.h"
#include "ViewModels/MetaSoundViewModelConversionFunctions.h"
#include "Interfaces/MetaSoundLiteralInterface.h"
```

### 基本用法：初始化 MetaSound ViewModel

```cpp
// 创建 MetaSound ViewModel 并用资产初始化
UMetaSoundViewModel* ViewModel = NewObject<UMetaSoundViewModel>();
ViewModel->InitializeMetaSound(MetaSoundAsset);

// 获取所有输入并遍历
TArray<UMetaSoundInputViewModel*> Inputs = ViewModel->GetInputViewModels();
for (UMetaSoundInputViewModel* Input : Inputs)
{
    UE_LOG(LogTemp, Log, TEXT("Input: %s, Type: %s, LiteralType: %s"),
        *Input->GetInputName().ToString(),
        *Input->GetDataType().ToString(),
        *LexToString(Input->GetLiteralType()));
}

// 按名称查找特定输入
UMetaSoundInputViewModel* VolumeInput = ViewModel->FindInputViewModel(FName("Volume"));
```

*来源: `Public/ViewModels/MetaSoundViewModel.h`*

### 基本用法：使用 Float Literal ViewModel

```cpp
// 创建 Float Literal ViewModel
UMetaSoundLiteralViewModel_Float* FloatVM = NewObject<UMetaSoundLiteralViewModel_Float>();

// 设置源值（直接赋给 MetaSound 的值）
FloatVM->SetSourceValue(0.5f);

// 读取归一化值（用于滑块 UI 0-1 范围）
float Normalized = FloatVM->GetNormalizedValue();

// 读取显示值（如转换后的 dB 值）
float DisplayDB = FloatVM->GetDisplayValue();

// 从用户输入（归一化滑块）反向设置
FloatVM->SetNormalizedValue(0.75f);
// SourceValue 和 DisplayValue 会自动更新
```

*来源: `Public/ViewModels/MetaSoundLiteralViewModel.h`*

### 进阶用法：实现自定义 Literal Widget

```cpp
// 自定义 Widget 实现 MetaSoundLiteralWidgetInterface
UCLASS()
class UMyAudioKnobWidget : public UWidget, public IMetaSoundLiteralWidgetInterface
{
    GENERATED_BODY()

public:
    // 声明需要的输入名称
    virtual TArray<FName> GetInputViewModelNames_Implementation() const override
    {
        return { FName("Frequency"), FName("Volume") };
    }

    // 接收并绑定 ViewModel
    virtual void SetInputViewModels_Implementation(
        const TMap<FName, UMetaSoundInputViewModel*>& InputViewModels) override
    {
        if (UMetaSoundInputViewModel** Found = InputViewModels.Find(FName("Frequency")))
        {
            FrequencyInputVM = *Found;
        }
        if (UMetaSoundInputViewModel** Found = InputViewModels.Find(FName("Volume")))
        {
            VolumeInputVM = *Found;
        }
    }

private:
    UPROPERTY()
    TObjectPtr<UMetaSoundInputViewModel> FrequencyInputVM;

    UPROPERTY()
    TObjectPtr<UMetaSoundInputViewModel> VolumeInputVM;
};
```

*来源: `Public/Interfaces/MetaSoundLiteralInterface.h`*

### 进阶用法：监听 MetaSound 结构变化

```cpp
// MetaSoundViewModel 自动监听 Builder 的输入/输出变化并通知 UI
// 当添加新输入时触发：
void OnInputAdded(FName VertexName, FName DataType);
void OnInputRemoved(FName VertexName, FName DataType);
void OnInputNameChanged(FName OldName, FName NewName);
void OnInputDataTypeChanged(FName VertexName, FName DataType);
void OnInputDefaultChanged(FName VertexName, FMetasoundFrontendLiteral LiteralValue, 
                            FName PageName, EMetaSoundLiteralChangeType ChangeType);

// 输出同理：
void OnOutputAdded(FName VertexName, FName DataType);
void OnOutputRemoved(FName VertexName, FName DataType);
```

*来源: `Public/ViewModels/MetaSoundViewModel.h`*

## Demo 示例

### .h

```cpp
// MyMetaSoundParamEditor.h
#pragma once

#include "CoreMinimal.h"
#include "ViewModels/MetaSoundViewModel.h"
#include "ViewModels/MetaSoundLiteralViewModel.h"
#include "MyMetaSoundParamEditor.generated.h"

UCLASS(BlueprintType)
class MYGAME_API UMyMetaSoundParamEditor : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, Category = "Audio")
    TObjectPtr<UMetaSoundViewModel> MetaSoundVM;

    UPROPERTY(BlueprintReadWrite, Category = "Audio")
    TObjectPtr<UMetaSoundLiteralViewModel_Float> VolumeVM;

    UPROPERTY(BlueprintReadWrite, Category = "Audio")
    TObjectPtr<UMetaSoundLiteralViewModel_Float> FrequencyVM;

    UPROPERTY(BlueprintReadWrite, Category = "Audio")
    TObjectPtr<UMetaSoundLiteralViewModel_Boolean> EnabledVM;

    UFUNCTION(BlueprintCallable, Category = "Audio")
    void Initialize(const TScriptInterface<IMetaSoundDocumentInterface> InMetaSound);

    UFUNCTION(BlueprintCallable, Category = "Audio")
    void SetVolumeFromSlider(float NormalizedValue);

    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Audio")
    float GetVolumeDisplayValue() const;
};
```

### .cpp

```cpp
// MyMetaSoundParamEditor.cpp
#include "MyMetaSoundParamEditor.h"
#include "ViewModels/MetaSoundViewModelConversionFunctions.h"

void UMyMetaSoundParamEditor::Initialize(const TScriptInterface<IMetaSoundDocumentInterface> InMetaSound)
{
    // 创建并初始化 MetaSound ViewModel
    MetaSoundVM = NewObject<UMetaSoundViewModel>(this);
    MetaSoundVM->InitializeMetaSound(InMetaSound);

    // 查找 Volume 输入并创建对应的 Float Literal ViewModel
    UMetaSoundInputViewModel* VolumeInput = MetaSoundVM->FindInputViewModel(FName("Volume"));
    if (VolumeInput)
    {
        VolumeVM = NewObject<UMetaSoundLiteralViewModel_Float>(this);
        VolumeVM->SetLiteral(VolumeInput->GetLiteral());
    }

    // 查找 Frequency 输入
    UMetaSoundInputViewModel* FreqInput = MetaSoundVM->FindInputViewModel(FName("Frequency"));
    if (FreqInput)
    {
        FrequencyVM = NewObject<UMetaSoundLiteralViewModel_Float>(this);
        FrequencyVM->SetLiteral(FreqInput->GetLiteral());
    }

    // 查找 Enabled 输入
    UMetaSoundInputViewModel* EnabledInput = MetaSoundVM->FindInputViewModel(FName("Enabled"));
    if (EnabledInput)
    {
        EnabledVM = NewObject<UMetaSoundLiteralViewModel_Boolean>(this);
        EnabledVM->SetLiteral(EnabledInput->GetLiteral());
    }
}

void UMyMetaSoundParamEditor::SetVolumeFromSlider(float NormalizedValue)
{
    if (VolumeVM)
    {
        // 滑块的 0-1 值自动映射到 Source 和 Display 范围
        VolumeVM->SetNormalizedValue(NormalizedValue);
    }
}

float UMyMetaSoundParamEditor::GetVolumeDisplayValue() const
{
    return VolumeVM ? VolumeVM->GetDisplayValue() : 0.f;
}
```

## 模块依赖

以下依赖从 `TechAudioToolsMetaSound.Build.cs` 及 .uplugin 的插件依赖推断：

| 模块 | 用途 |
|---|---|
| `MetasoundFrontend` | MetaSound 前端数据结构（FMetasoundFrontendLiteral 等） |
| `ModelViewViewModel` | MVVM 框架基类 UMVVMViewModelBase |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合 MetaSound 引脚类型注册与编辑器行为 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回退导致编译错误的提交 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合引脚类型注册逻辑（首次提交后因编译错误回退） |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为 Literal ViewModel 添加撤销/重做事务支持 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 重命名 DocumentConfiguration 相关类型 |

### 维护评价

- **状态**：活跃开发中（2026 年 4 月仍有密集更新）
- **成熟度**：实验性/Beta 阶段，API 可能变动（近期有回退编译错误的记录）
- **风险**：`IsBetaVersion=true` + `IsExperimentalVersion=true` + `EnabledByDefault=false`，表明此插件尚未稳定，不应在生产环境依赖
- **推荐**：适合在音频工具开发、MetaSound 调试 UI 等**内部/实验性项目**中尝试使用。如用于生产，需自行承担 API 变更风险

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
- 官方文档（暂无）
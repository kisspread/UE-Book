# Tech Audio Tools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 技术音频工具集 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 为 MetaSound 系统提供 MVVM（Model-View-ViewModel）架构支持，解决 MetaSound 输入参数与 UMG 控件之间的双向绑定问题。

核心价值：
- 将 MetaSound 的各种字面量类型（Literal）封装为标准的 MVVM ViewModel，使 UMG 控件（旋钮、滑块、文本框等）可以零代码绑定 MetaSound 参数
- 提供 float 类型的源值（Source）、显示值（Display）和归一化值（Normalized）之间的自动转换（如线性增益 ↔ 分贝）
- 提供统一的接口模式，让包含多个 MetaSound 输入的控件能够批量初始化视图模型，无需逐一手动绑定
- 让 MetaSound 输出可以驱动 UI 视觉参数（如频谱可视化、电平表等）

简单来说：**这个插件让你用 UMG 做 MetaSound 参数编辑器**。

## 使用场景

- 你需要为 MetaSound 构建自定义的参数编辑 UI → 用此插件的 ViewModel 系统
- 你需要把 MetaSound 的 float 输入显示为分贝单位，但 MetaSound 内部用线性增益 → 用 `MetaSoundLiteralViewModel_Float` 的单位转换
- 你需要批量管理多个 MetaSound 输入的控件绑定 → 实现 `MetaSoundLiteralWidgetInterface`
- 你需要用 MetaSound 的输出驱动 UI 动画或可视化 → 绑定 `MetaSoundOutputViewModel`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Initialize MetaSound` | 用 MetaSound 资产初始化 ViewModel | `UMetaSoundViewModel` |
| `Initialize Builder` | 用 MetaSound Builder 初始化 ViewModel | `UMetaSoundViewModel` |
| `Get Input Viewmodels` | 获取所有输入的 ViewModel 数组 | `UMetaSoundViewModel` |
| `Find Input Viewmodel` | 按名称查找指定输入的 ViewModel | `UMetaSoundViewModel` |
| `Get Output Viewmodels` | 获取所有输出的 ViewModel 数组 | `UMetaSoundViewModel` |
| `Find Output Viewmodel` | 按名称查找指定输出的 ViewModel | `UMetaSoundViewModel` |
| `Reset` | 重置 ViewModel 到未初始化状态 | `UMetaSoundViewModel` |
| `Get Input Viewmodel Names` | 获取此控件所需的输入 ViewModel 名称列表 | `IMetaSoundLiteralWidgetInterface` |
| `Set Input Viewmodels` | 批量设置输入 ViewModel | `IMetaSoundLiteralWidgetInterface` |
| `Find MetaSound Input Viewmodel by Name` | 从数组中按名称查找输入 ViewModel | `UMetaSoundViewModelConversionFunctions` |
| `Find MetaSound Output Viewmodel by Name` | 从数组中按名称查找输出 ViewModel | `UMetaSoundViewModelConversionFunctions` |
| `Get MetaSound Literal Value as Text` | 将 Literal 值转为文本 | `UMetaSoundViewModelConversionFunctions` |
| `Is MetaSound Interface Member` | 检查成员名是否属于注册的 MetaSound 接口 | `UMetaSoundViewModelConversionFunctions` |
| `Is MetaSound Array Type` | 检查数据类型是否支持数组 | `UMetaSoundViewModelConversionFunctions` |
| `Is MetaSound Constructor Type` | 检查数据类型是否支持构造函数引脚 | `UMetaSoundViewModelConversionFunctions` |

### Float ViewModel 专用节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSourceRangeMin` | 获取源值范围最小值 | `UMetaSoundLiteralViewModel_Float` |
| `GetSourceRangeMax` | 获取源值范围最大值 | `UMetaSoundLiteralViewModel_Float` |
| `GetSourceUnits` | 获取源值单位 | `UMetaSoundLiteralViewModel_Float` |
| `GetDisplayRangeMin` | 获取显示范围最小值 | `UMetaSoundLiteralViewModel_Float` |
| `GetDisplayRangeMax` | 获取显示范围最大值 | `UMetaSoundLiteralViewModel_Float` |
| `GetDisplayUnits` | 获取显示值单位 | `UMetaSoundLiteralViewModel_Float` |
| `GetStepSize` | 获取整数 ViewModel 的步进值 | `UMetaSoundLiteralViewModel_Integer` |

### 使用示例（蓝图描述）

**基础用法：创建 MetaSound 参数滑块**

1. 在 UMG Widget 中创建 `MetaSound ViewModel` 实例（作为 Viewmodel）
2. 在 Event Construct 中调用 `Initialize MetaSound`，传入目标 MetaSound 资产
3. 调用 `Get Input Viewmodels` 获取所有输入 ViewModel
4. 用 `Find Input Viewmodel` 或 `Find MetaSound Input Viewmodel by Name` 定位目标输入
5. 将找到的 `MetaSound Input Viewmodel` 的 `Literal` 属性绑定到 Float Literal ViewModel
6. Float Literal ViewModel 的 `NormalizedValue` 绑定到 Slider 控件的值

**批量初始化用法：实现 MetaSoundLiteralWidgetInterface**

1. 创建一个包含多个输入控件的 Widget，实现 `MetaSoundLiteralWidgetInterface`
2. 在 `Get Input Viewmodel Names` 中返回需要的所有输入名称（如 `["Volume", "Pitch"]`）
3. 父级 Widget 初始化后，调用子 Widget 的 `Set Input Viewmodels` 批量注入 ViewModel
4. 子 Widget 在 `Set Input Viewmodels` 中将每个 ViewModel 绑定到对应的 UMG 控件

**Float 单位转换用法**

1. 创建 `MetaSound Literal Float Viewmodel` 实例，在 Details 面板配置：
   - `bShowDisplayValues = true`
   - `RangeValues` 设置为自定义的 Float Mapping（如 dB ↔ Linear）
2. 将 `DisplayValue` 绑定到文本显示控件
3. 将 `NormalizedValue` 绑定到 Slider
4. 用户拖动 Slider 时，`DisplayValue` 和 `SourceValue` 自动同步更新

## C++ 用法

### 头文件引入

```cpp
#include "ViewModels/MetaSoundViewModel.h"
#include "ViewModels/MetaSoundLiteralViewModel.h"
#include "Interfaces/MetaSoundLiteralInterface.h"
#include "ViewModels/MetaSoundViewModelConversionFunctions.h"
```

### 基本用法：初始化 MetaSound ViewModel

```cpp
// 创建 MetaSound ViewModel 并用 MetaSound 资产初始化
UMetaSoundViewModel* ViewModel = NewObject<UMetaSoundViewModel>(this);

// 方式一：用 MetaSound 资产初始化
ViewModel->InitializeMetaSound(MetaSoundAsset);

// 方式二：用 Builder 初始化
ViewModel->Initialize(MetaSoundBuilder);

// 获取所有输入 ViewModel
TArray<UMetaSoundInputViewModel*> Inputs = ViewModel->GetInputViewModels();

// 按名称查找特定输入
UMetaSoundInputViewModel* VolumeInput = ViewModel->FindInputViewModel(FName("Volume"));

// 读取输入的字面量值
FMetasoundFrontendLiteral Literal = VolumeInput->GetLiteral();
```

### 进阶用法：自定义 Float ViewModel 控件

```cpp
// 在自定义 Widget 中实现 MetaSound Literal Widget Interface
UCLASS()
class UMyMetaSoundSlider : public UUserWidget, public IMetaSoundLiteralWidgetInterface
{
    GENERATED_BODY()

public:
    // 声明需要的输入 ViewModel 名称
    virtual TArray<FName> GetInputViewModelNames_Implementation() const override
    {
        return { FName("Volume"), FName("Frequency") };
    }

    // 接收并绑定 ViewModel
    virtual void SetInputViewModels_Implementation(
        const TMap<FName, UMetaSoundInputViewModel*>& InputViewModels) override
    {
        if (UMetaSoundInputViewModel** VolumeVM = InputViewModels.Find(FName("Volume")))
        {
            // 绑定到内部的 Float Literal ViewModel
            FloatLiteralVM->SetLiteral((*VolumeVM)->GetLiteral());
        }
    }

private:
    UPROPERTY()
    TObjectPtr<UMetaSoundLiteralViewModel_Float> FloatLiteralVM;
};
```

### 进阶用法：使用转换函数库

```cpp
// 从数组中查找特定 ViewModel
TArray<UMetaSoundInputViewModel*> Inputs = ViewModel->GetInputViewModels();
UMetaSoundInputViewModel* Found = UMetaSoundViewModelConversionFunctions::FindInputViewModelByName(
    Inputs, FName("Volume"));

// 获取 Literal 的文本表示
FText LiteralText = UMetaSoundViewModelConversionFunctions::GetLiteralValueAsText(Literal);

// 检查数据类型是否支持数组
bool bSupportsArray = UMetaSoundViewModelConversionFunctions::IsArrayType(FName("float"));

// 检查是否为接口成员（支持取反）
bool bIsInterface = UMetaSoundViewModelConversionFunctions::IsInterfaceMember(FName("OnPlay"), false);
```

## Demo 示例

```cpp
// MyMetaSoundParamPanel.h
#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Interfaces/MetaSoundLiteralInterface.h"
#include "MyMetaSoundParamPanel.generated.h"

class UMetaSoundViewModel;
class UMetaSoundInputViewModel;

UCLASS()
class UMyMetaSoundParamPanel : public UUserWidget
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, Category = "MetaSound")
    TObjectPtr<UMetaSoundViewModel> MetaSoundViewModel;

    UFUNCTION(BlueprintCallable, Category = "MetaSound")
    void InitializeWithMetaSound(TScriptInterface<IMetaSoundDocumentInterface> InMetaSound);

    UFUNCTION(BlueprintCallable, Category = "MetaSound")
    UMetaSoundInputViewModel* GetInputViewModelByName(FName InputName) const;
};
```

```cpp
// MyMetaSoundParamPanel.cpp
#include "MyMetaSoundParamPanel.h"
#include "ViewModels/MetaSoundViewModel.h"
#include "ViewModels/MetaSoundViewModelConversionFunctions.h"

void UMyMetaSoundParamPanel::InitializeWithMetaSound(
    TScriptInterface<IMetaSoundDocumentInterface> InMetaSound)
{
    if (!MetaSoundViewModel)
    {
        MetaSoundViewModel = NewObject<UMetaSoundViewModel>(this);
    }

    MetaSoundViewModel->InitializeMetaSound(InMetaSound);

    // 列出所有输入供 UI 展示
    TArray<UMetaSoundInputViewModel*> Inputs = MetaSoundViewModel->GetInputViewModels();
    for (UMetaSoundInputViewModel* InputVM : Inputs)
    {
        UE_LOG(LogTemp, Log, TEXT("Input: %s, Type: %s"),
            *InputVM->GetInputName().ToString(),
            *InputVM->GetDataType().ToString());
    }
}

UMetaSoundInputViewModel* UMyMetaSoundParamPanel::GetInputViewModelByName(FName InputName) const
{
    if (!MetaSoundViewModel) return nullptr;
    return MetaSoundViewModel->FindInputViewModel(InputName);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetasoundFrontend` | MetaSound 前端数据结构（Literal、DocumentInterface） |
| `MetasoundEngine` | MetaSound Builder 基础设施 |
| `ModelViewViewModel` | MVVM 框架（ViewModel 基类、View 绑定） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合引脚类型注册及 MetaSound 编辑器相关行为 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回退导致 CIS 编译错误的提交 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合引脚类型注册（首次提交，后被回退重做） |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | MetaSound Literal ViewModel 支持事务操作（撤销/重做） |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 重命名 DocumentConfiguration 为 MetaSound Document Template |

### 维护评价

- **活跃维护**：最近 1 个月内有多次实质性更新，包括新功能（事务支持）和重构（引脚类型注册整合）
- **实验性插件**：`IsBetaVersion=true`、`IsExperimentalVersion=true`、`Installed=false`、位于 Experimental 目录，API 可能随时变动
- **年轻项目**：创建于 2025-04-22，约 1 年历史，仍在快速迭代中
- **风险提示**：作为实验性插件，不建议在生产环境中直接依赖，后续版本可能有 breaking changes
- **推荐程度**：如果你正在构建 MetaSound 的自定义 UI，且可以接受实验性 API 的稳定性风险，这是一个非常有价值的参考和基础框架

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
- [官方文档]()（暂无）
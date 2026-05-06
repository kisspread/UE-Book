# TechAudioTools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 技术音频工具 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器视图模型、蓝图内容） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 为 Unreal Engine 的音频系统（特别是 MetaSound）提供了一套 MVVM（Model-View-ViewModel）集成工具。它允许开发者以数据绑定方式在 UMG 界面中实时反映 MetaSound 编辑器中资产的元数据变化（如显示名称、描述、作者、关键词、分类层次等），并支持对 MetaSound 输入/输出端口的显示属性（名称、描述、排序、高级显示）进行编程式修改。

此外，该插件还包含类型转换辅助函数（如获取 MetaSound 数据类型的引脚颜色），以及音频组件视图模型等实用工具，便于在编辑器 UI 中创建定制化的音频控制面板。

## 使用场景

- **自定义 MetaSound 编辑器 UI**：当您需要创建一个展示当前选中 MetaSound 属性的 UMG 面板（如名称、描述、关键词）并使其在编辑器中实时更新时，可使用 `MetaSoundEditorViewModel`。
- **MetaSound 资产批处理**：通过代码批量设置 MetaSound 的元数据（如作者、弃用状态），无需手动操作编辑器。
- **音频数据类型可视化**：根据 MetaSound 引脚数据类型获取对应的颜色，用于自定义节点图绘制。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get MetaSound Data Type Pin Color` | 根据输入的数据类型名称（如 `"Float"`、`"Int"`）返回对应的引脚颜色 | `UMetaSoundEditorViewModelConversionFunctions` |
| `Set MetaSound Display Name` | 设置当前 MetaSound 的显示名称 | `UMetaSoundEditorViewModel` |
| `Set MetaSound Description` | 设置当前 MetaSound 的描述 | `UMetaSoundEditorViewModel` |
| `Set Author` | 设置当前 MetaSound 的作者 | `UMetaSoundEditorViewModel` |
| `Set Keywords` | 设置当前 MetaSound 的关键词列表 | `UMetaSoundEditorViewModel` |
| `Set Category Hierarchy` | 设置当前 MetaSound 的分类层次 | `UMetaSoundEditorViewModel` |
| `Set Is Deprecated` | 标记当前 MetaSound 为弃用状态 | `UMetaSoundEditorViewModel` |
| `Get Display Name` / `Get Description` / `Get Author` / `Get Keywords` / `Get Category Hierarchy` / `Is Deprecated` | 相应的 Getter 节点 | `UMetaSoundEditorViewModel` |

### 使用示例（蓝图描述）

1. **获取引脚颜色**：在事件图表中拖入 `Get MetaSound Data Type Pin Color` 节点，输入一个字符串（如 `"Float"`），输出 `LinearColor`，可直接用于设置节点的颜色。
2. **更新 MetaSound 元数据**：
   - 获取 `MetaSoundEditorViewModel` 对象引用（通常来自 MVVM 绑定或从 `GetViewModel` 节点获取）。
   - 调用 `Set MetaSound Display Name` 等节点，输入新值。
   - 资产立即在 MetaSound 编辑器中反映更新（因为视图模型通过 `MetaSoundEditorBuilderListener` 同步了更改）。

## C++ 用法

### 头文件引入

```cpp
#include "ViewModels/MetaSoundEditorViewModel.h"
#include "ViewModels/MetaSoundEditorViewModelConversionFunctions.h"
```

### 基本用法

从源码分析，您可以通过 `Initialize` 或 `InitializeMetaSound` 将一个 MetaSound 文档绑定到视图模型，然后获取/设置其属性。

```cpp
// 假设已有 MetaSound 文档接口
TScriptInterface<IMetaSoundDocumentInterface> MetaSoundInterface = ...;

// 创建视图模型实例（通常由 MVVM 系统自动创建，此处为演示）
UMetaSoundEditorViewModel* ViewModel = NewObject<UMetaSoundEditorViewModel>();
ViewModel->InitializeMetaSound(MetaSoundInterface);

// 读取元数据
FText DisplayName = ViewModel->GetDisplayName();
FText Description = ViewModel->GetDescription();
FString Author = ViewModel->GetAuthor();

// 修改元数据（更改会自动同步到编辑器）
ViewModel->SetMetaSoundDisplayName(FText::FromString(TEXT("My Custom MetaSound")));
ViewModel->SetMetaSoundDescription(FText::FromString(TEXT("A procedural wind sound")));
ViewModel->SetAuthor(FString("TechAudio Team"));

// 设置输入/输出端口的显示属性
ViewModel->SetInputDisplayName(TEXT("In_Amplitude"), FText::FromString(TEXT("Amplitude")));
ViewModel->SetInputDescription(TEXT("In_Amplitude"), FText::FromString(TEXT("Sound amplitude between 0 and 1")));
ViewModel->SetInputSortOrderIndex(TEXT("In_Amplitude"), 0);

// 获取数据类型引脚颜色
FLinearColor PinColor = UMetaSoundEditorViewModelConversionFunctions::GetMetaSoundDataTypePinColor(TEXT("Float"));
```

来源：基于 `Source/TechAudioToolsMetaSoundEditor/Public/ViewModels/MetaSoundEditorViewModel.h` 和 `...ConversionFunctions.h`。

### 进阶用法

结合 MVVM 系统，您可以将视图模型绑定到 UMG 中的字段通知（FieldNotify）属性，实现双向同步。例如，在 UMG 的 `OnTextChanged` 事件中调用 `SetMetaSoundDisplayName`，视图模型会通过 `OnDisplayNameChanged` 回调更新绑定的 UI 控件。

```cpp
// 假设有一个 UTextBlock 绑定到 ViewModel 的 DisplayName
// 在 ViewModel 中：
UFUNCTION()
void OnDisplayNameChanged(const FText NewDisplayName)
{
    UE_MVVM_SET_PROPERTY_VALUE(DisplayName, NewDisplayName);
    // 此函数由 MVVM 系统自动调用
}
```

您也可以通过 `Reset()` 方法清理视图模型的状态，用于重新绑定新的 MetaSound。

## Demo 示例

以下演示如何在 C++ 中创建一个 `UMetaSoundEditorViewModel` 并利用其功能。

**MyAudioTool.h**：

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "ViewModels/MetaSoundEditorViewModel.h"
#include "MyAudioTool.generated.h"

UCLASS()
class UMyAudioTool : public UObject
{
    GENERATED_BODY()

public:
    void ApplyMetaSoundSettings(TScriptInterface<IMetaSoundDocumentInterface> InMetaSound);
};
```

**MyAudioTool.cpp**：

```cpp
#include "MyAudioTool.h"
#include "ViewModels/MetaSoundEditorViewModelConversionFunctions.h"

void UMyAudioTool::ApplyMetaSoundSettings(TScriptInterface<IMetaSoundDocumentInterface> InMetaSound)
{
    UMetaSoundEditorViewModel* ViewModel = NewObject<UMetaSoundEditorViewModel>();
    ViewModel->InitializeMetaSound(InMetaSound);

    // 批量设置元数据
    ViewModel->SetMetaSoundDisplayName(FText::FromString(TEXT("Wind Sound")));
    ViewModel->SetMetaSoundDescription(FText::FromString(TEXT("Procedural wind generated by MetaSound")));
    ViewModel->SetAuthor(FString("Audio Team"));
    ViewModel->SetIsDeprecated(false);

    // 修改输入端口显示
    ViewModel->SetInputDisplayName(TEXT("In_Speed"), FText::FromString(TEXT("Wind Speed")));
    ViewModel->SetInputSortOrderIndex(TEXT("In_Speed"), 0);

    // 获取颜色示例
    FLinearColor Color = UMetaSoundEditorViewModelConversionFunctions::GetMetaSoundDataTypePinColor(TEXT("Float"));
    UE_LOG(LogTemp, Log, TEXT("Float pin color: %s"), *Color.ToString());
}
```

## 模块依赖

以下列出该插件独有的依赖（省略标准 Core/Engine/Slate 等公共依赖）。

| 模块 | 用途 |
|---|---|
| `Metasound` | MetaSound 运行时与编辑器基础模块，提供 `IMetaSoundDocumentInterface` 等核心接口 |
| `ModelViewViewModel` | UE 的 MVVM 框架，用于实现视图模型属性变化通知与 UMG 绑定 |
| `UMG` (非省略) | 提供 UUserWidget 等 UI 基础，但通常视为标准依赖，此处列出以便清晰 |

## 维护状态

### 近期更新

- 2025-09-29 `e2b3930` — 移除默认源值与显示值转换时的 clamp 限制
- 2025-09-03 `085d445` — 新增 `BandwidthOct` 和 `Tempo` 浮点单位类型用于标签格式化
- 2025-09-03 `a510163` — 新增 AudioComponentViewModel
- 2025-09-03 `1348197` — 修正文档错误
- 2025-09-02 `8eab906` — 新增每个 MetaSound 字面类型的视图模型类

### 维护评价

该插件为 2025 年 9 月新创建，处于实验阶段（`IsBetaVersion=true`、`IsExperimentalVersion=true`）。近期更新频繁，包含功能新增（单位类型、音频组件视图模型）和 bug 修复，开发活跃。当前无已知限制或废弃标记，推荐在项目开发早期进行试用，并关注后续更新以获取稳定版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TechAudioTools)
- [MetaSound 官方文档](https://dev.epicgames.com/documentation/unreal-engine/metasound-overview)
- [ModelViewViewModel 框架文档](https://dev.epicgames.com/documentation/unreal-engine/model-view-viewmodel-framework-in-unreal-engine)
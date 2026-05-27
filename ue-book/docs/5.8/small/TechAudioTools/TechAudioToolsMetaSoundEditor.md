# TechAudioTools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 技术音频工具 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、UMG 相关内容） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 是一个基于 **MVVM（Model-View-ViewModel）架构**的 MetaSound 编辑工具集。它为 MetaSound 编辑器提供 ViewModel 层，使得 MetaSound 资产的元数据（显示名称、描述、作者、关键词、分类层级等）以及输入/输出端口属性能够在 UMG Widget 中实时显示和编辑。

这个插件解决的核心问题是：将 MetaSound 编辑器中的数据变化（资产修改、端口属性调整）通过 MVVM 数据绑定机制桥接到 UMG 界面组件，实现编辑器 UI 的响应式更新。它依赖 UE5 的 ModelViewViewModel 框架，使用 `FieldNotify` 实现属性变更通知。

## 使用场景

- 你正在构建自定义的 MetaSound 编辑器界面 → 使用 `UMetaSoundEditorViewModel` 作为 UMG Widget 的数据源
- 你需要在 UMG 面板中展示和编辑 MetaSound 的元数据（名称、描述、作者、关键词）→ 通过 ViewModel 的属性绑定实现双向数据流
- 你需要自定义 MetaSound 输入/输出端口的显示顺序、是否为高级显示 → 使用 `UMetaSoundInputEditorViewModel` 和 `UMetaSoundOutputEditorViewModel`
- 你需要获取 MetaSound 数据类型对应的引脚颜色 → 使用 `GetMetaSoundDataTypePinColor` 工具函数

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMetaSoundDataTypePinColor` | 获取指定 MetaSound 数据类型对应的引脚颜色 | `UMetaSoundEditorViewModelConversionFunctions` |
| `SetMetaSoundDisplayName` | 设置 MetaSound 的显示名称 | `UMetaSoundEditorViewModel` |
| `SetMetaSoundDescription` | 设置 MetaSound 的描述 | `UMetaSoundEditorViewModel` |
| `SetAuthor` | 设置 MetaSound 的作者 | `UMetaSoundEditorViewModel` |
| `SetKeywords` | 设置 MetaSound 的关键词列表 | `UMetaSoundEditorViewModel` |
| `SetCategoryHierarchy` | 设置 MetaSound 的分类层级 | `UMetaSoundEditorViewModel` |
| `SetIsDeprecated` | 标记 MetaSound 为已废弃 | `UMetaSoundEditorViewModel` |
| `SetInputDisplayName` | 设置指定输入端口的显示名称 | `UMetaSoundEditorViewModel` |
| `SetInputDescription` | 设置指定输入端口的描述 | `UMetaSoundEditorViewModel` |
| `SetInputSortOrderIndex` | 设置指定输入端口的排序索引 | `UMetaSoundEditorViewModel` |
| `SetInputIsAdvancedDisplay` | 设置输入端口是否为高级显示 | `UMetaSoundEditorViewModel` |
| `SetOutputDisplayName` | 设置指定输出端口的显示名称 | `UMetaSoundEditorViewModel` |
| `SetOutputDescription` | 设置指定输出端口的描述 | `UMetaSoundEditorViewModel` |
| `SetOutputSortOrderIndex` | 设置指定输出端口的排序索引 | `UMetaSoundEditorViewModel` |
| `SetOutputIsAdvancedDisplay` | 设置输出端口是否为高级显示 | `UMetaSoundEditorViewModel` |

### 使用示例（蓝图描述）

**获取引脚颜色**：调用 `Get MetaSound Data Type Pin Color` 节点，传入数据类型名称（如 `Float`、`Audio`），返回对应的 `FLinearColor` 颜色值，可用于自定义绘制 MetaSound 节点引脚。

**编辑 MetaSound 元数据**：创建 `MetaSoundEditorViewModel` 的实例，调用 `InitializeMetaSound` 传入 MetaSound 资产引用，然后通过 `SetMetaSoundDisplayName`、`SetAuthor` 等节点修改元数据。由于属性带有 `FieldNotify`，UMG Widget 中绑定的 TextBlock 等组件会自动更新。

**自定义输入端口属性**：通过 `SetInputSortOrderIndex` 调整端口在编辑器面板中的显示顺序，通过 `SetInputIsAdvancedDisplay` 控制端口是否归入"高级显示"折叠区域。

## C++ 用法

### 头文件引入

```cpp
#include "ViewModels/MetaSoundEditorViewModel.h"
#include "ViewModels/MetaSoundEditorViewModelConversionFunctions.h"
```

### 基本用法

```cpp
// 创建 MetaSound Editor ViewModel 并初始化
// 来源: Public/ViewModels/MetaSoundEditorViewModel.h
UMetaSoundEditorViewModel* ViewModel = NewObject<UMetaSoundEditorViewModel>();

// 初始化 ViewModel，传入 MetaSound 资产
ViewModel->InitializeMetaSound(MetaSoundAsset);

// 修改元数据（带 FieldNotify，自动触发 UI 更新）
ViewModel->SetMetaSoundDisplayName(FText::FromString(TEXT("My Sound Effect")));
ViewModel->SetMetaSoundDescription(FText::FromString(TEXT("A custom sound effect")));
ViewModel->SetAuthor(TEXT("Epic Games"));
ViewModel->SetKeywords({ FText::FromString(TEXT("effect")), FText::FromString(TEXT("custom")) });
ViewModel->SetCategoryHierarchy({ FText::FromString(TEXT("Effects")), FText::FromString(TEXT("Custom")) });
ViewModel->SetIsDeprecated(false);

// 修改输入端口属性
ViewModel->SetInputDisplayName(FName("Frequency"), FText::FromString(TEXT("频率")));
ViewModel->SetInputDescription(FName("Frequency"), FText::FromString(TEXT("基础频率值")));
ViewModel->SetInputSortOrderIndex(FName("Frequency"), 0);
ViewModel->SetInputIsAdvancedDisplay(FName("Frequency"), false);
```

### 进阶用法

```cpp
// 使用 ViewModel 配合 MetaSound Builder
// 来源: Public/ViewModels/MetaSoundEditorViewModel.h
UMetaSoundEditorViewModel* EditorVM = NewObject<UMetaSoundEditorViewModel>();
UMetaSoundBuilderBase* Builder = /* 获取或创建 MetaSound Builder */;
EditorVM->Initialize(Builder);

// 获取引脚颜色（纯函数，无需实例化 ViewModel）
// 来源: Public/ViewModels/MetaSoundEditorViewModelConversionFunctions.h
FLinearColor FloatPinColor = UMetaSoundEditorViewModelConversionFunctions::GetMetaSoundDataTypePinColor(FName("Float"));
FLinearColor AudioPinColor = UMetaSoundEditorViewModelConversionFunctions::GetMetaSoundDataTypePinColor(FName("Audio"));

// 使用子 ViewModel 管理单个输入/输出端口
UMetaSoundInputEditorViewModel* InputVM = NewObject<UMetaSoundInputEditorViewModel>();
InputVM->SetInputDisplayName(FText::FromString(TEXT("Amplitude")));
InputVM->SetSortOrderIndex(1);
InputVM->SetIsAdvancedDisplay(false);
```

## Demo 示例

```cpp
// MetaSoundEditorWidget.h
#pragma once

#include "CoreMinimal.h"
#include "ViewModels/MetaSoundEditorViewModel.h"

UCLASS()
class UMetaSoundEditorWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    // 通过 UMG 数据绑定获取 ViewModel
    UPROPERTY(BlueprintReadWrite, Category = "MetaSound")
    TObjectPtr<UMetaSoundEditorViewModel> ViewModel;

    // 初始化 Widget 并绑定 MetaSound 资产
    UFUNCTION(BlueprintCallable, Category = "MetaSound")
    void SetupMetaSound(UMetaSoundAssetBase* MetaSound);

    // 获取引脚颜色供 UMG 绑定使用
    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "MetaSound")
    FLinearColor GetPinColor(const FName& DataType);
};
```

```cpp
// MetaSoundEditorWidget.cpp
#include "MetaSoundEditorWidget.h"
#include "ViewModels/MetaSoundEditorViewModelConversionFunctions.h"

void UMetaSoundEditorWidget::SetupMetaSound(UMetaSoundAssetBase* MetaSound)
{
    if (!ViewModel)
    {
        ViewModel = NewObject<UMetaSoundEditorViewModel>(this);
    }

    if (MetaSound)
    {
        TScriptInterface<IMetaSoundDocumentInterface> DocInterface;
        DocInterface.SetObject(MetaSound);
        DocInterface.SetInterface(Cast<IMetaSoundDocumentInterface>(MetaSound));
        ViewModel->InitializeMetaSound(DocInterface);
    }
    else
    {
        ViewModel->Reset();
    }
}

FLinearColor UMetaSoundEditorWidget::GetPinColor(const FName& DataType)
{
    return UMetaSoundEditorViewModelConversionFunctions::GetMetaSoundDataTypePinColor(DataType);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaSound` | MetaSound 核心运行时，提供 MetaSound 文档接口和 Builder 基类 |
| `MetaSoundEditor` | MetaSound 编辑器功能，提供 `UMetaSoundEditorBuilderListener` 监听器 |
| `ModelViewViewModel` | UE5 MVVM 框架，提供 `FieldNotify` 和 `UE_MVVM_SET_PROPERTY_VALUE` 等宏 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合 MetaSound 引脚类型注册和编辑器中引脚相关行为 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回退一次导致 CI 编译错误的提交 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合 MetaSound 引脚类型注册和编辑器引脚行为（首次尝试） |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为 MetaSound 字面量 ViewModel 添加撤销/重做事务支持 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 重命名 DocumentConfiguration 为 MetaSound 模板相关术语 |

### 维护评价

该插件创建于 2025 年 4 月，至今约 1 年，属于较新的插件。最近一个月内有多次实质性更新（引脚类型整合、事务支持），表明 Epic 正在**积极开发和迭代**此插件。

- **状态**：活跃开发中，频繁更新
- **风险**：作为 Experimental + Beta 插件，API 随时可能发生 breaking change（如最近的 `DocumentConfiguration` 重命名）
- **推荐度**：适合用于实验和原型开发，但不建议在生产项目中依赖此插件的核心 API

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
- [官方文档]()（暂无）
- [MetaSound 插件文档](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound)
- [ModelViewViewModel 框架](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ModelViewViewModel)
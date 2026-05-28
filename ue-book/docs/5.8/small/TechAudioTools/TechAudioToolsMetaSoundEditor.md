# Tech Audio Tools

> A collection of audio-related tools and utilities.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 技术音频工具 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 插件为 Unreal Engine 的 MetaSound 系统提供了一套基于 MVVM（Model-View-ViewModel）模式的编辑器工具链。其核心功能是创建和管理 MetaSound 编辑器的 ViewModel（视图模型），这些 ViewModel 充当了 MetaSound 资产数据与 UMG（UI 框架）控件之间的桥梁。它解决了在自定义编辑器或 UMG 界面中同步显示和编辑 MetaSound 资产元数据（如显示名称、描述、作者、输入/输出参数等）的复杂性问题，使得开发者能够轻松构建与 MetaSound 编辑器行为同步的自定义 UI。

## 使用场景

- 你需要创建一个自定义的 UMG 面板来批量编辑多个 MetaSound 资产的元数据（如作者、关键词、分类）。
- 你正在开发一个工具，需要在视口中实时预览和修改 MetaSound 节点的输入参数，并希望这些修改能实时反映到 MetaSound 编辑器和实际音频输出中。
- 你需要为 MetaSound 的输入和输出引脚构建一个高级的、可排序、可折叠的列表界面，用于展示和编辑其详细属性。

## 蓝图用法

插件主要暴露了 `UMetaSoundEditorViewModel` 及其相关的输入/输出 ViewModel 类供蓝图使用，它们继承自 `UMVVMViewModelBase`，支持 UE5 的 MVVM 框架。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Initialize` | 使用一个 MetaSound 构建器（Builder）初始化 ViewModel，建立数据绑定。 | `UMetaSoundEditorViewModel` |
| `Reset` | 重置 ViewModel，清除所有数据和监听器。 | `UMetaSoundEditorViewModel` |
| `SetMetaSoundDisplayName` | 设置当前 MetaSound 资产的显示名称。 | `UMetaSoundEditorViewModel` |
| `SetAuthor` | 设置当前 MetaSound 资产的作者。 | `UMetaSoundEditorViewModel` |
| `SetKeywords` | 设置当前 MetaSound 资产的关键词数组。 | `UMetaSoundEditorViewModel` |
| `SetInputDisplayName` | 通过输入名称设置特定输入的显示名称。 | `UMetaSoundEditorViewModel` |
| `SetOutputSortOrderIndex` | 通过输出名称设置特定输出的排序索引。 | `UMetaSoundEditorViewModel` |
| `GetMetaSoundDataTypePinColor` | 获取指定 MetaSound 数据类型对应的引脚颜色。 | `UMetaSoundEditorViewModelConversionFunctions` |

### 使用示例（蓝图描述）

1.  创建一个 `UMetaSoundEditorViewModel` 的实例（例如，在你的 UMG Widget 的成员变量中）。
2.  在 Widget 初始化时，获取要编辑的 MetaSound 资产的 `MetaSoundBuilderBase` 对象，然后调用 `Initialize` 节点绑定到该 ViewModel。
3.  在 UMG 的文本框（TextBox）上，使用 **Property Binding** 或 **ViewModel Binding** 功能，将其文本属性绑定到 ViewModel 的 `DisplayName`、`Author`、`Keywords` 等属性上。
4.  当用户在 UI 中修改文本框内容时，ViewModel 的对应属性会自动更新，并通过内部的 `BuilderListener` 将更改同步回 MetaSound 编辑器和资产。
5.  使用 `GetMetaSoundDataTypePinColor` 节点，根据节点引脚的类型名称，获取正确的颜色来绘制 UI。

## C++ 用法

### 头文件引入

```cpp
#include "ViewModels/MetaSoundEditorViewModel.h"
#include "ViewModels/MetaSoundEditorViewModelConversionFunctions.h" // 如需使用工具函数
```

### 基本用法

创建并初始化一个 MetaSound 编辑器 ViewModel，用于驱动 UI。

```cpp
// 来源文件: 概括自 Public/ViewModels/MetaSoundEditorViewModel.h
// 在你的 UI 管理器或 Widget 类中
UPROPERTY()
TObjectPtr<UMetaSoundEditorViewModel> MetaSoundEditorViewModel;

// 初始化过程
void UMyMetaSoundEditorPanel::InitializeWithMetaSoundBuilder(UMetaSoundBuilderBase* InBuilder)
{
    if (!MetaSoundEditorViewModel)
    {
        MetaSoundEditorViewModel = NewObject<UMetaSoundEditorViewModel>(this);
    }
    // 初始化 ViewModel 并绑定监听器，此后 ViewModel 的属性会同步资产变化
    MetaSoundEditorViewModel->Initialize(InBuilder);
    // 现在可以绑定到 UI，或读取 MetaSoundEditorViewModel->GetDisplayName() 等
}
```

### 进阶用法

监听 ViewModel 属性的变化，或直接设置特定输入/输出的属性。

```cpp
// 来源文件: 概括自 Public/ViewModels/MetaSoundEditorViewModel.h
// 1. 通过 ViewModel 修改 MetaSound 的元数据
MetaSoundEditorViewModel->SetAuthor(TEXT("Epic Games Audio Team"));
MetaSoundEditorViewModel->SetKeywords({ FText::FromString(TEXT("Ambient")), FText::FromString(TEXT("Forest")) });

// 2. 修改特定输入的显示信息
MetaSoundEditorViewModel->SetInputDisplayName(FName("Volume"), FText::FromString(TEXT("主音量")));
MetaSoundEditorViewModel->SetInputIsAdvancedDisplay(FName("Volume"), true); // 设为高级显示

// 3. 修改特定输出的排序索引
MetaSoundEditorViewModel->SetOutputSortOrderIndex(FName("OutMono"), 0);

// 4. 监听单个输入属性的变化（通常通过数据绑定自动处理，但也可手动绑定委托）
// 注意：更常见的做法是使用 FieldNotify 和 MVVM 框架自动绑定。
```

## Demo 示例

一个最小化的示例，展示如何创建一个自定义的编辑器面板 ViewModel。

```cpp
// MyMetaSoundEditorViewModel.h
#pragma once
#include "ViewModels/MetaSoundEditorViewModel.h"
#include "MyMetaSoundEditorViewModel.generated.h"

UCLASS()
class UMyMetaSoundEditorViewModel : public UMetaSoundEditorViewModel
{
    GENERATED_BODY()
public:
    // 自定义初始化逻辑，例如为 UI 添加额外的派生属性
    void InitializeForCustomPanel(UMetaSoundBuilderBase* InBuilder);
};

// MyMetaSoundEditorViewModel.cpp
#include "MyMetaSoundEditorViewModel.h"
#include "MetaSoundBuilderBase.h"

void UMyMetaSoundEditorViewModel::InitializeForCustomPanel(UMetaSoundBuilderBase* InBuilder)
{
    // 先调用父类的初始化，建立与 MetaSound 资产和编辑器的连接
    Initialize(InBuilder);
    
    // 此时，ViewModel 已经同步了资产的 DisplayName, Author, Inputs, Outputs 等。
    // 你可以在蓝图中绑定这个 ViewModel 的属性到 UMG 控件。
    // 也可以在 C++ 中进一步处理数据。
    UE_LOG(LogTemp, Log, TEXT("Editing MetaSound: %s"), *GetDisplayName().ToString());
}
```

## 模块依赖

从 `Build.cs` 文件分析，以下为本插件特有的依赖：

| 模块 | 用途 |
|---|---|
| `MetaSound` | 核心 MetaSound 框架，提供资产类型、构建器和文档接口。 |
| `ModelViewViewModel` | UE5 的 MVVM 框架，`UMVVMViewModelBase` 的基类在此模块中定义。 |
| `MetasoundFrontend` | MetaSound 前端数据模型，用于访问输入、输出引脚的详细类型信息。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合 MetaSound 引脚类型注册和相关编辑器行为。 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回滚了导致编译错误的更改。 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合 MetaSound 引脚类型注册和相关编辑器行为（首次尝试）。 |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为 MetaSound 字面量 ViewModel 添加了事务（Undo/Redo）支持。 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 将 `DocumentConfiguration` 重命名为 `MetaSoundTemplate`。 |

### 维护评价

TechAudioTools 插件创建于 2025 年 4 月，是一个相对年轻的实验性插件。从 Git 历史看，它在 2026 年 3 月至 4 月期间有过数次实质性更新，主要集中在 MetaSound 引脚系统和编辑器行为的整合与优化上，并修复了编译问题，表明它正处于**活跃开发**阶段。由于其 `IsBetaVersion` 和 `IsExperimentalVersion` 均为 true，且 `EnabledByDefault` 为 false，属于需要手动启用的实验性功能。其 API 可能会在未来版本中发生变化。

**推荐**：如果你正在开发依赖 MetaSound 编辑器自定义 UI 的高级工具或插件，可以尝试使用，但需注意其实验性状态和潜在的 API 变更。对于核心生产项目，建议等待其进入正式发布阶段。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
- [官方文档]() (无)
- [测试用例]() (此插件的测试用例可能位于引擎级测试目录中，未在本插件目录内发现)
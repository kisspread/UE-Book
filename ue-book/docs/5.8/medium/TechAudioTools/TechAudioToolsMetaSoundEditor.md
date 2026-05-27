# Tech Audio Tools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 技术音频工具 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 是一套基于 MVVM（Model-View-ViewModel）架构的 MetaSound 编辑器工具集。它为 MetaSound 编辑器提供了视图模型层，使 UMG 控件能够实时反映 MetaSound 资产中的变更。核心解决的问题是：在 MetaSound 编辑器中编辑节点图时，如何将资产元数据（显示名称、描述、作者、关键字等）和端口属性的变更同步到 UI 控件中。

该插件实现了三层 ViewModel 架构：
- **MetaSoundEditorViewModel**：管理 MetaSound 资产的整体元数据（名称、描述、作者、关键字、分类层级、废弃状态）
- **MetaSoundInputEditorViewModel / MetaSoundOutputEditorViewModel**：管理输入/输出端口的编辑器属性（显示名称、描述、排序顺序、是否高级显示）
- 通过 `MetaSoundEditorBuilderListener` 监听编辑器中的操作并自动同步到 ViewModel 属性

## 使用场景

- 你在构建自定义 MetaSound 编辑器面板/UMG Widget → 用此插件的 ViewModel 绑定数据
- 你需要在 UMG 中显示和编辑 MetaSound 资产的元数据（名称、描述、作者等）→ 用 `UMetaSoundEditorViewModel`
- 你需要自定义 MetaSound 输入/输出端口的展示方式（排序、高级显示）→ 用 `UMetaSoundInputEditorViewModel` / `UMetaSoundOutputEditorViewModel`
- 你需要获取 MetaSound 数据类型对应的引脚颜色 → 用 `GetMetaSoundDataTypePinColor` 蓝图函数

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMetaSoundDataTypePinColor` | 根据数据类型名称返回对应的引脚颜色（FLinearColor） | `UMetaSoundEditorViewModelConversionFunctions` |
| `SetMetaSoundDisplayName` | 设置 MetaSound 资产的显示名称 | `UMetaSoundEditorViewModel` |
| `SetMetaSoundDescription` | 设置 MetaSound 资产的描述 | `UMetaSoundEditorViewModel` |
| `SetAuthor` | 设置 MetaSound 资产的作者 | `UMetaSoundEditorViewModel` |
| `SetKeywords` | 设置 MetaSound 资产的关键字列表 | `UMetaSoundEditorViewModel` |
| `SetCategoryHierarchy` | 设置 MetaSound 资产的分类层级 | `UMetaSoundEditorViewModel` |
| `SetIsDeprecated` | 设置 MetaSound 资产的废弃状态 | `UMetaSoundEditorViewModel` |
| `SetInputDisplayName` | 设置指定输入端口的显示名称 | `UMetaSoundEditorViewModel` |
| `SetInputDescription` | 设置指定输入端口的描述 | `UMetaSoundEditorViewModel` |
| `SetInputSortOrderIndex` | 设置指定输入端口的排序索引 | `UMetaSoundEditorViewModel` |
| `SetInputIsAdvancedDisplay` | 设置指定输入端口是否为高级显示 | `UMetaSoundEditorViewModel` |
| `SetOutputDisplayName` | 设置指定输出端口的显示名称 | `UMetaSoundEditorViewModel` |
| `SetOutputDescription` | 设置指定输出端口的描述 | `UMetaSoundEditorViewModel` |
| `SetOutputSortOrderIndex` | 设置指定输出端口的排序索引 | `UMetaSoundEditorViewModel` |
| `SetOutputIsAdvancedDisplay` | 设置指定输出端口是否为高级显示 | `UMetaSoundEditorViewModel` |

### 使用示例（蓝图描述）

**获取数据类型引脚颜色：**
1. 创建 `Get MetaSound Data Type Pin Color` 节点
2. 将 DataType 引脚连接到包含目标类型名称（FName）的变量
3. 输出引脚为 FLinearColor，可直接用于设置 UI 控件颜色

**在 UMG Widget 中绑定 MetaSound 元数据：**
1. 在 Widget 中创建 `UMetaSoundEditorViewModel` 类型的属性（BlueprintReadWrite）
2. 调用 `InitializeMetaSound` 传入目标 MetaSound 资产的 `IMetaSoundDocumentInterface` 引用
3. 使用 MVVM FieldNotify 绑定（`DisplayName`、`Description`、`Author` 等属性都标记了 FieldNotify）
4. ViewModel 属性变更会自动触发绑定的 UMG 控件刷新

## C++ 用法

### 头文件引入

```cpp
#include "ViewModels/MetaSoundEditorViewModel.h"
#include "ViewModels/MetaSoundEditorViewModelConversionFunctions.h"
```

### 基本用法

```cpp
// 创建 MetaSound 编辑器 ViewModel 并初始化
UMetaSoundEditorViewModel* ViewModel = NewObject<UMetaSoundEditorViewModel>(this);
ViewModel->InitializeMetaSound(MetaSoundInterface);

// 读取和修改元数据
FText CurrentName = ViewModel->GetDisplayName();
ViewModel->SetMetaSoundDisplayName(FText::FromString(TEXT("My New Sound")));
ViewModel->SetAuthor(FText::FromString(TEXT("Audio Designer")));
ViewModel->SetKeywords({FText::FromString(TEXT("ambient")), FText::FromString(TEXT("loop"))});

// 设置输入端口属性
ViewModel->SetInputDisplayName(FName("Frequency"), FText::FromString(TEXT("Base Frequency")));
ViewModel->SetInputSortOrderIndex(FName("Frequency"), 0);
ViewModel->SetInputIsAdvancedDisplay(FName("Frequency"), true);

// 设置输出端口属性
ViewModel->SetOutputDisplayName(FName("AudioOut"), FText::FromString(TEXT("Audio Output")));
```

### 进阶用法

```cpp
// 获取 MetaSound 数据类型对应的引脚颜色
FLinearColor PinColor = UMetaSoundEditorViewModelConversionFunctions::GetMetaSoundDataTypePinColor(FName("Audio"));

// 使用独立的输入/输出 ViewModel
// ViewModel 在 Initialize 时会自动创建 UMetaSoundInputEditorViewModel 和 UMetaSoundOutputEditorViewModel 实例
// 通过 GetInputViewModelClass() / GetOutputViewModelClass() 可自定义子类

// ViewModel 内部通过 UMetaSoundEditorBuilderListener 监听编辑器操作
// 当资产在编辑器中被修改时，OnDisplayNameChanged、OnDescriptionChanged 等回调会自动同步到属性
// 属性变更通过 UE_MVVM_SET_PROPERTY_VALUE 宏触发 FieldNotify，自动更新绑定的 UI
```

## Demo 示例

```cpp
// MetaSoundEditorPanel.h
#pragma once

#include "CoreMinimal.h"
#include "Components/Widget.h"
#include "ViewModels/MetaSoundEditorViewModel.h"
#include "MetaSoundEditorPanel.generated.h"

UCLASS()
class UMetaSoundEditorPanel : public UWidget
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, Category = "MetaSound")
    TObjectPtr<UMetaSoundEditorViewModel> EditorViewModel;

    /** 初始化面板并绑定到指定 MetaSound 资产 */
    UFUNCTION(BlueprintCallable, Category = "MetaSound")
    void InitializeWithMetaSound(const TScriptInterface<IMetaSoundDocumentInterface>& InMetaSound);

    /** 应用显示名称变更 */
    UFUNCTION(BlueprintCallable, Category = "MetaSound")
    void ApplyDisplayName(const FText& NewDisplayName);
};
```

```cpp
// MetaSoundEditorPanel.cpp
#include "MetaSoundEditorPanel.h"
#include "ViewModels/MetaSoundEditorViewModel.h"

void UMetaSoundEditorPanel::InitializeWithMetaSound(const TScriptInterface<IMetaSoundDocumentInterface>& InMetaSound)
{
    if (!EditorViewModel)
    {
        EditorViewModel = NewObject<UMetaSoundEditorViewModel>(this);
    }
    EditorViewModel->InitializeMetaSound(InMetaSound);

    // 此后 EditorViewModel 的所有 FieldNotify 属性（DisplayName、Description 等）
    // 会自动响应编辑器中的变更并触发 UI 更新
}

void UMetaSoundEditorPanel::ApplyDisplayName(const FText& NewDisplayName)
{
    if (EditorViewModel)
    {
        EditorViewModel->SetMetaSoundDisplayName(NewDisplayName);
    }
}
```

## 模块依赖

从 .uplugin 的 Plugins 和源码中的类型引用推断：

| 模块 | 用途 |
|---|---|
| `MetaSound` | MetaSound 核心运行时模块，提供 `IMetaSoundDocumentInterface`、`UMetaSoundBuilderBase` 等基础类型 |
| `MetaSoundEditor` | MetaSound 编辑器模块，提供 `UMetaSoundEditorBuilderListener` 等编辑器监听器 |
| `ModelViewViewModel` | UE MVVM 框架，提供 `UE_MVVM_SET_PROPERTY_VALUE` 宏和 FieldNotify 支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合引脚类型注册及 MetaSound 编辑器引脚相关行为 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回退之前的提交，修复 CIS 编译错误 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合引脚类型注册及 MetaSound 编辑器引脚相关行为（首次提交后被回退） |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为 MetaSound Literal Viewmodel 添加撤销/重做事务支持 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 将 DocumentConfiguration 重命名为 MetaSound(Document)Template |

### 维护评价

- **创建时间**：2025-04-22，插件非常年轻（约 1 年）
- **更新频率**：近期活跃，2026 年 3-4 月有多次功能性提交
- **维护状态**：活跃维护中，持续进行功能增强和重构
- **实验性标记**：`IsBetaVersion=true` 且 `IsExperimentalVersion=true`，API 可能在后续版本中发生变更
- **已知限制**：作为实验性插件，接口不稳定；依赖 ModelViewViewModel 框架（该框架本身也在演进中）
- **推荐程度**：仅推荐在开发 MetaSound 编辑器扩展 UI 时使用，不建议在生产环境依赖此 API。适用于内部工具开发和原型验证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
- [官方文档](https://docs.unrealengine.com/)（暂无专门文档）
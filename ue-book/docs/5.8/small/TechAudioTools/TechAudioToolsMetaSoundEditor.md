# Tech Audio Tools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 音频工具集 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 是一个为 MetaSound 编辑器提供 MVVM（Model-View-ViewModel）架构支持的工具集。该插件的核心目的是将 MetaSound 资产的编辑操作与 UMG（Unreal Motion Graphics）UI 控件进行双向绑定，使得 MetaSound 编辑器中的属性变更能够实时反映到 UI 界面上。

具体来说，它解决了以下问题：
- **MetaSound 属性的编辑器绑定**：通过 ViewModel 模式，将 MetaSound 的元数据（名称、描述、作者、关键词等）暴露为可绑定的属性
- **输入/输出端口的独立管理**：为每个输入和输出端口提供单独的 ViewModel，支持自定义显示名、描述、排序顺序等
- **MVVM 架构支持**：利用 UE5 的 ModelViewViewModel 插件实现数据绑定，简化 MetaSound 编辑器的 UI 开发

该插件依赖 ModelViewViewModel 插件，表明它是为 MetaSound 编辑器的现代化 UI 重构而创建的基础设施。

## 使用场景

- 你在开发 MetaSound 编辑器的自定义 UI 面板 → 使用 MetaSoundEditorViewModel 绑定属性
- 你需要在 UMG Widget 中显示和编辑 MetaSound 的元数据 → 使用 ViewModel 的 FieldNotify 属性
- 你正在为 MetaSound 编辑器构建基于 MVVM 架构的新界面 → 使用该插件提供的 ViewModel 类
- 你需要获取 MetaSound 数据类型的引脚颜色 → 使用 GetMetaSoundDataTypePinColor 函数

## 蓝图用法

该插件的蓝图 API 主要面向编辑器扩展开发，提供了 ViewModel 属性的读写访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get MetaSound Data Type Pin Color` | 获取指定数据类型的引脚颜色 | `UMetaSoundEditorViewModelConversionFunctions` |
| `SetMetaSoundDisplayName` | 设置 MetaSound 的显示名称 | `UMetaSoundEditorViewModel` |
| `SetMetaSoundDescription` | 设置 MetaSound 的描述 | `UMetaSoundEditorViewModel` |
| `SetAuthor` | 设置 MetaSound 的作者 | `UMetaSoundEditorViewModel` |
| `SetKeywords` | 设置 MetaSound 的关键词列表 | `UMetaSoundEditorViewModel` |
| `SetCategoryHierarchy` | 设置 MetaSound 的分类层级 | `UMetaSoundEditorViewModel` |
| `SetIsDeprecated` | 设置 MetaSound 为已废弃状态 | `UMetaSoundEditorViewModel` |
| `SetInputDisplayName` | 设置指定输入的显示名称 | `UMetaSoundEditorViewModel` |
| `SetInputDescription` | 设置指定输入的描述 | `UMetaSoundEditorViewModel` |
| `SetInputSortOrderIndex` | 设置指定输入的排序索引 | `UMetaSoundEditorViewModel` |
| `SetInputIsAdvancedDisplay` | 设置指定输入是否为高级显示 | `UMetaSoundEditorViewModel` |
| `SetOutputDisplayName` | 设置指定输出的显示名称 | `UMetaSoundEditorViewModel` |
| `SetOutputDescription` | 设置指定输出的描述 | `UMetaSoundEditorViewModel` |
| `SetOutputSortOrderIndex` | 设置指定输出的排序索引 | `UMetaSoundEditorViewModel` |
| `SetOutputIsAdvancedDisplay` | 设置指定输出是否为高级显示 | `UMetaSoundEditorViewModel` |

### 可绑定属性（FieldNotify）

**MetaSound 元数据属性**（`UMetaSoundEditorViewModel`）：
- `DisplayName` - MetaSound 显示名称
- `Description` - MetaSound 描述
- `Author` - 作者
- `Keywords` - 关键词数组
- `CategoryHierarchy` - 分类层级数组
- `bIsDeprecated` - 是否已废弃

**输入属性**（`UMetaSoundInputEditorViewModel`）：
- `InputDisplayName` - 输入显示名称
- `InputDescription` - 输入描述
- `SortOrderIndex` - 排序索引
- `bIsAdvancedDisplay` - 是否高级显示

**输出属性**（`UMetaSoundOutputEditorViewModel`）：
- `OutputDisplayName` - 输出显示名称
- `OutputDescription` - 输出描述
- `SortOrderIndex` - 排序索引
- `bIsAdvancedDisplay` - 是否高级显示

### 使用示例（蓝图描述）

1. **创建 ViewModel 并绑定到 MetaSound**：
   - 创建 `MetaSoundEditorViewModel` 实例
   - 调用 `InitializeMetaSound` 传入目标 MetaSound 资产
   - ViewModel 会自动创建 `MetaSoundEditorBuilderListener` 监听资产变更

2. **在 UMG Widget 中绑定属性**：
   - 将 ViewModel 设置为 Widget 的数据源
   - 在 Widget 的属性绑定中选择 ViewModel 的 `DisplayName`、`Description` 等属性
   - 使用 FieldNotify 机制实现实时更新

3. **编辑 MetaSound 输入属性**：
   - 获取输入的 ViewModel 实例（通过 `CreateInputViewModel` 自动创建）
   - 调用 `SetInputDisplayName`、`SetInputDescription` 等函数修改属性
   - 变更会自动同步到 MetaSound 资产

## C++ 用法

### 头文件引入

```cpp
#include "ViewModels/MetaSoundEditorViewModel.h"
#include "ViewModels/MetaSoundEditorViewModelConversionFunctions.h"
```

### 基本用法

```cpp
// 来源: MetaSoundEditorViewModel.h

// 创建 MetaSound Editor ViewModel
UMetaSoundEditorViewModel* EditorViewModel = NewObject<UMetaSoundEditorViewModel>();

// 初始化 ViewModel，绑定到 MetaSound 资产
EditorViewModel->InitializeMetaSound(MetaSoundAsset);

// 设置 MetaSound 元数据
EditorViewModel->SetMetaSoundDisplayName(FText::FromString(TEXT("My Ambient Sound")));
EditorViewModel->SetMetaSoundDescription(FText::FromString(TEXT("An ambient sound effect")));
EditorViewModel->SetAuthor(TEXT("Audio Team"));
EditorViewModel->SetKeywords({FText::FromString(TEXT("ambient")), FText::FromString(TEXT("environment"))});

// 获取输入端口并修改其属性
EditorViewModel->SetInputDisplayName(FName("Volume"), FText::FromString(TEXT("Volume Control")));
EditorViewModel->SetInputDescription(FName("Volume"), FText::FromString(TEXT("Controls the output volume")));
EditorViewModel->SetInputSortOrderIndex(FName("Volume"), 0);
EditorViewModel->SetInputIsAdvancedDisplay(FName("Volume"), false);

// 修改输出端口属性
EditorViewModel->SetOutputDisplayName(FName("AudioOut"), FText::FromString(TEXT("Audio Output")));
EditorViewModel->SetOutputSortOrderIndex(FName("AudioOut"), 0);
```

### 进阶用法

```cpp
// 来源: MetaSoundEditorViewModel.h + MetaSoundEditorViewModelConversionFunctions.h

// 获取 MetaSound 数据类型的引脚颜色
FLinearColor PinColor = UMetaSoundEditorViewModelConversionFunctions::GetMetaSoundDataTypePinColor(FName("Audio"));
FLinearColor FloatColor = UMetaSoundEditorViewModelConversionFunctions::GetMetaSoundDataTypePinColor(FName("Float"));
FLinearColor BoolColor = UMetaSoundEditorViewModelConversionFunctions::GetMetaSoundDataTypePinColor(FName("Bool"));

// 监听 ViewModel 属性变更（需要在 UMG Widget 或其他绑定类中实现）
// ViewModel 使用 FieldNotify 机制，可以通过 UE_MVVM_SET_PROPERTY_VALUE 宏触发通知
// 变更会自动通过 MetaSoundEditorBuilderListener 同步到资产

// 重置 ViewModel 状态
EditorViewModel->Reset();

// 标记 MetaSound 为已废弃
EditorViewModel->SetIsDeprecated(true);

// 设置分类层级
EditorViewModel->SetCategoryHierarchy({
    FText::FromString(TEXT("Audio")),
    FText::FromString(TEXT("Ambient")),
    FText::FromString(TEXT("Environment"))
});
```

## Demo 示例

```cpp
// MetaSoundEditorPanel.h
#pragma once

#include "CoreMinimal.h"
#include "ViewModels/MetaSoundEditorViewModel.h"
#include "MetaSoundEditorPanel.generated.h"

UCLASS()
class UMetaSoundEditorPanel : public UObject
{
    GENERATED_BODY()

public:
    // 初始化面板并绑定 MetaSound
    UFUNCTION(BlueprintCallable, Category = "MetaSound Editor")
    void InitializePanel(UMetaSoundViewModel* InViewModel);

    // 更新显示名称
    UFUNCTION(BlueprintCallable, Category = "MetaSound Editor")
    void UpdateDisplayName(const FText& NewDisplayName);

    // 获取当前 ViewModel
    UFUNCTION(BlueprintCallable, Category = "MetaSound Editor")
    UMetaSoundEditorViewModel* GetViewModel() const { return EditorViewModel; }

private:
    UPROPERTY()
    TObjectPtr<UMetaSoundEditorViewModel> EditorViewModel;
};
```

```cpp
// MetaSoundEditorPanel.cpp
#include "MetaSoundEditorPanel.h"

void UMetaSoundEditorPanel::InitializePanel(UMetaSoundViewModel* InViewModel)
{
    if (UMetaSoundEditorViewModel* ViewModel = Cast<UMetaSoundEditorViewModel>(InViewModel))
    {
        EditorViewModel = ViewModel;
        
        // 设置默认值
        EditorViewModel->SetMetaSoundDisplayName(FText::FromString(TEXT("New MetaSound")));
        EditorViewModel->SetMetaSoundDescription(FText::FromString(TEXT("")));
    }
}

void UMetaSoundEditorPanel::UpdateDisplayName(const FText& NewDisplayName)
{
    if (EditorViewModel)
    {
        EditorViewModel->SetMetaSoundDisplayName(NewDisplayName);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Metasound` | MetaSound 核心模块，提供 MetaSound 资产和前端接口 |
| `ModelViewViewModel` | UE5 MVVM 框架，提供属性绑定和通知机制 |
| `MetaSoundEditor` | MetaSound 编辑器模块，提供编辑器特定功能 |
| `UMG` | Unreal Motion Graphics，用于 UI Widget 绑定 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合引脚类型注册和相关编辑器行为 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回退编译错误修复 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合引脚类型注册和相关编辑器行为 |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 添加 MetaSound 字面量 ViewModel 的事务支持 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 重命名文档配置为 MetaSound 模板 |

### 维护评价

**活跃维护中** 🟢

该插件创建于 2025 年 4 月，虽然历史较短，但维护非常活跃：
- 最近一个月内有多次实质性更新
- 2026 年 4 月密集更新，主要围绕引脚类型注册和编辑器行为整合
- 2026 年 4 月添加了事务支持，表明功能在持续完善
- 2026 年 3 月进行了命名重构，说明架构在优化中

**注意事项**：
- 该插件标记为实验性（`IsExperimentalVersion=true`）和 Beta 版本（`IsBetaVersion=true`）
- 默认未启用（`Installed=false`），需要手动启用
- API 可能在未来版本中发生变化
- 建议在生产环境中谨慎使用，适合早期采用者和内部开发

**推荐使用**：适合正在开发 MetaSound 编辑器扩展的团队，特别是需要 MVVM 架构支持的场景。不建议在生产环境中使用，但可以用于原型开发和内部工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
- [ModelViewViewModel 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ModelViewViewModel)
- [MetaSound 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound)
# Tech Audio Tools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 音频工具集 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 是 Epic 官方的实验性音频工具插件，核心功能是为 MetaSound 编辑器提供基于 **MVVM（Model-View-ViewModel）** 架构的编辑器 ViewModel 层。

该插件解决的核心问题是：**MetaSound 资产在编辑器中的 UI 绑定**。通过 `MetaSoundViewModel` 系列类，它将 MetaSound 的元数据（显示名称、描述、作者、关键字、分类层级、废弃标记等）以及输入/输出端口配置（显示名称、描述、排序索引、是否高级显示）暴露为可观察属性（`FieldNotify`），使 UMG Widget 能够通过 UE5 的 MVVM 框架自动响应 MetaSound 编辑器中资产的变化。

简单来说：这个插件让 MetaSound 编辑器的 UI 面板能实时绑定和编辑 MetaSound 资产的各种属性，而不需要手动编写属性变更通知逻辑。

**注意**：此插件默认未启用（`Installed: false`），且标记为实验性（`IsBetaVersion: true`, `IsExperimentalVersion: true`），依赖 MetaSound 和 ModelViewViewModel 插件。

## 使用场景

- 你正在开发或扩展 **MetaSound 编辑器**的自定义 UI 面板 → 使用 `UMetaSoundEditorViewModel` 绑定资产元数据
- 你需要在 UMG Widget 中实时显示和编辑 MetaSound 输入/输出端口的元数据 → 使用 `UMetaSoundInputEditorViewModel` / `UMetaSoundOutputEditorViewModel`
- 你需要在蓝图中获取 MetaSound 数据类型的引脚颜色 → 使用 `GetMetaSoundDataTypePinColor` 转换函数

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get MetaSound Data Type Pin Color` | 根据数据类型名称获取对应的 MetaSound 引脚颜色 | `UMetaSoundEditorViewModelConversionFunctions` |

### ViewModel 蓝图属性（通过 FieldNotify 绑定）

`UMetaSoundEditorViewModel` 暴露以下可绑定属性，可在 UMG Widget 中通过 MVVM 绑定使用：

**资产级元数据：**
- `DisplayName` (FText) — MetaSound 显示名称
- `Description` (FText) — MetaSound 描述
- `Author` (FString) — 作者
- `Keywords` (TArray&lt;FText&gt;) — 关键字列表
- `CategoryHierarchy` (TArray&lt;FText&gt;) — 分类层级
- `bIsDeprecated` (bool) — 是否标记为废弃

`UMetaSoundInputEditorViewModel` 和 `UMetaSoundOutputEditorViewModel` 各自暴露：
- `InputDisplayName` / `OutputDisplayName` (FText) — 端口显示名称
- `InputDescription` / `OutputDescription` (FText) — 端口描述
- `SortOrderIndex` (int32) — 排序索引
- `bIsAdvancedDisplay` (bool) — 是否在高级显示分类中

### 使用示例（蓝图描述）

1. 在 UMG Widget 中创建一个 `UMetaSoundEditorViewModel` 实例
2. 调用 `InitializeMetaSound` 或 `Initialize` 绑定目标 MetaSound 资产
3. 将 Widget 的文本框绑定到 ViewModel 的 `DisplayName`、`Description` 等属性（通过 MVVM FieldNotify 机制）
4. 编辑器中 MetaSound 资产变更时，ViewModel 会自动通过 `OnDisplayNameChanged`、`OnDescriptionChanged` 等回调更新属性，UI 自动刷新
5. 用户在 UI 中修改属性时，ViewModel 的 Setter 会将变更写回 MetaSound 资产

## C++ 用法

### 头文件引入

```cpp
#include "ViewModels/MetaSoundEditorViewModel.h"
#include "ViewModels/MetaSoundEditorViewModelConversionFunctions.h"
```

### 基本用法：获取 MetaSound 数据类型引脚颜色

```cpp
// 获取 MetaSound 某个数据类型的引脚颜色
FLinearColor PinColor = UMetaSoundEditorViewModelConversionFunctions::GetMetaSoundDataTypePinColor(FName("Float"));
```

> 来源：`Public/ViewModels/MetaSoundEditorViewModelConversionFunctions.h`

### 进阶用法：编辑器 ViewModel 的完整生命周期

```cpp
// 1. 创建编辑器 ViewModel
UMetaSoundEditorViewModel* ViewModel = NewObject<UMetaSoundEditorViewModel>();

// 2. 初始化并绑定 MetaSound 资产（这会自动创建 BuilderListener 并注册委托）
TScriptInterface<IMetaSoundDocumentInterface> MetaSoundDoc = MyMetaSoundAsset;
ViewModel->InitializeMetaSound(MetaSoundDoc);

// 3. 通过 ViewModel 读取/修改元数据
FText Name = ViewModel->GetDisplayName();
ViewModel->SetMetaSoundDisplayName(FText::FromString(TEXT("My New Name")));
ViewModel->SetAuthor(TEXT("Epic Games"));

// 4. 修改输入/输出端口元数据
ViewModel->SetInputDisplayName(FName("Frequency"), FText::FromString(TEXT("频率")));
ViewModel->SetInputDescription(FName("Frequency"), FText::FromString(TEXT("控制频率参数")));
ViewModel->SetInputSortOrderIndex(FName("Frequency"), 0);
ViewModel->SetInputIsAdvancedDisplay(FName("Frequency"), false);

ViewModel->SetOutputDisplayName(FName("OutLeft"), FText::FromString(TEXT("左声道")));
ViewModel->SetOutputSortOrderIndex(FName("OutLeft"), 0);

// 5. 重置 ViewModel（解绑所有委托）
ViewModel->Reset();
```

## Demo 示例

```cpp
// MyMetaSoundPanel.h
#pragma once

#include "CoreMinimal.h"
#include "Components/Widget.h"
#include "ViewModels/MetaSoundEditorViewModel.h"
#include "MyMetaSoundPanel.generated.h"

UCLASS()
class UMyMetaSoundPanel : public UWidget
{
    GENERATED_BODY()

public:
    /** 初始化面板并绑定 MetaSound */
    UFUNCTION(BlueprintCallable, Category = "MetaSound")
    void BindMetaSound(const TScriptInterface<IMetaSoundDocumentInterface>& InMetaSound);

    /** 获取当前 ViewModel */
    UFUNCTION(BlueprintCallable, Category = "MetaSound")
    UMetaSoundEditorViewModel* GetViewModel() const { return ViewModel; }

protected:
    UPROPERTY(Transient)
    TObjectPtr<UMetaSoundEditorViewModel> ViewModel;

    // ... Widget 实现省略
};
```

```cpp
// MyMetaSoundPanel.cpp
#include "MyMetaSoundPanel.h"

void UMyMetaSoundPanel::BindMetaSound(const TScriptInterface<IMetaSoundDocumentInterface>& InMetaSound)
{
    if (!ViewModel)
    {
        ViewModel = NewObject<UMetaSoundEditorViewModel>(this);
    }
    
    ViewModel->InitializeMetaSound(InMetaSound);
    
    // 此时 ViewModel 的所有 FieldNotify 属性已绑定
    // 可通过 MVVM 框架将 UI 元素绑定到 ViewModel 属性
    UE_LOG(LogTemp, Log, TEXT("Bound MetaSound: %s"), *ViewModel->GetDisplayName().ToString());
    UE_LOG(LogTemp, Log, TEXT("Author: %s"), *ViewModel->GetAuthor());
}
```

## 模块依赖

从 `.uplugin` 的 Plugins 字段和模块类型推断：

| 模块 | 用途 |
|---|---|
| `Metasound` | MetaSound 运行时和前端框架，提供 `IMetaSoundDocumentInterface`、`UMetaSoundBuilderBase` 等基础类型 |
| `ModelViewViewModel` | UE5 MVVM 框架，提供 `FieldNotify`、`UE_MVVM_SET_PROPERTY_VALUE` 等 ViewModel 基础设施 |

**注意**：`TechAudioToolsMetaSoundEditor` 模块类型声明为 Runtime，但其中的 ViewModel 类（如 `UMetaSoundEditorViewModel`）实现了 `IsEditorOnly() const override { return true; }`，表明实际仅在编辑器环境下使用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合 MetaSound 引脚类型注册及编辑器引脚相关行为 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回退编译错误的改动 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合 MetaSound 引脚类型注册及编辑器引脚行为（首次提交后回退） |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为 MetaSound 字面量 ViewModel 添加事务支持（撤销/重做） |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 将 DocumentConfiguration 重命名为 MetaSound 模板相关命名 |

### 维护评价

- **创建时间**：2025-04-22，约 1 年前
- **最近更新**：2026-04-16，非常活跃，最近一个月有多次功能性更新
- **维护状态**：**活跃维护中**。作为 Epic 官方的 MetaSound 编辑器 MVVM 基础设施，持续在进行重构和功能增强
- **已知限制**：
  - 标记为实验性（`IsBetaVersion: true`, `IsExperimentalVersion: true`），API 可能发生破坏性变更
  - 默认未启用（`Installed: false`），需要手动在项目中启用
  - 依赖 ModelViewViewModel 插件，该框架本身也在演进中
- **推荐程度**：如果你在开发 MetaSound 相关的编辑器扩展并希望使用 MVVM 模式，这是官方推荐的 ViewModel 层实现。但由于是实验性插件，**不建议在生产环境中深度依赖**，随时可能因上游重构而需要适配

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
- 官方文档（暂无）
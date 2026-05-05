# Motion Design (AvalancheEditorCore 模块)

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche) | |

---

## 用途

Motion Design（内部代号 Avalanche）是 Epic 为虚拟制片打造的**运动图形设计与广播合成工具**。它在 UE 编辑器中提供了一套类似 After Effects / Motion 的时间线驱动设计工作流，让设计师可以直接在引擎内完成：

- **2D/3D 运动图形设计**：形状、文字、SVG 导入、材质动画
- **时间线编排与过渡逻辑**：基于 Sequencer 的多序列切换与过渡（Transition Logic）
- **实时合成与广播输出**：媒体合成、远程控制、MRQ 渲染队列集成
- **场景管理**：场景树、场景装备（Scene Rig）、遮罩系统、修改器堆栈

**AvalancheEditorCore** 是整个 Motion Design 编辑器框架的**核心基础设施模块**，定义了编辑器扩展体系（Editor + Extension）、标签页管理、选择系统、边界计算、用户输入对话框等所有上层模块共用的抽象层。

## 使用场景

- 你在做虚拟制片的**实时运动图形**（节目包装、虚拟背景动画） → 用 Motion Design
- 你需要在 UE 编辑器中**扩展自定义编辑器模式**，添加工具栏按钮、标签页、快捷键 → 用 AvalancheEditorCore 的 `IAvaEditor` / `IAvaEditorExtension` 体系
- 你需要**缓存和查询 Actor/Component 的包围盒**（含有向包围盒） → 用 `UAvaBoundsProviderSubsystem`
- 你需要**统一管理编辑器选择状态**并获取选中对象 → 用 `UAvaSelectionProviderSubsystem`
- 你需要弹出**模态输入对话框**（文本、数值、结构体） → 用 `SAvaUserInputDialog`

## 蓝图用法

AvalancheEditorCore 主要是 C++ 框架层，公开的蓝图 API 较少。以下是从子系统中提取的可蓝图访问接口：

### 核心子系统

| 子系统 | 说明 | 获取方式 |
|---|---|---|
| `UAvaEditorSubsystem` | 管理当前活跃的 Motion Design 编辑器实例，提供扩展查找 | `GetWorld()->GetSubsystem<UAvaEditorSubsystem>()` |
| `UAvaSelectionProviderSubsystem` | 缓存编辑器选择状态，提供选中 Actor/Component 列表和变换 | `GetWorld()->GetSubsystem<UAvaSelectionProviderSubsystem>()` |
| `UAvaBoundsProviderSubsystem` | 缓存并查询 Actor/Component 的本地和有向包围盒 | `GetWorld()->GetSubsystem<UAvaBoundsProviderSubsystem>()` |

### 使用示例（蓝图描述）

1. **获取选中 Actor 列表**：在蓝图中通过 `Get Game World` → `Get Subsystem (UAvaSelectionProviderSubsystem)` → `Get Selected Actors` 获取当前 Motion Design 编辑器选中的所有 Actor。
2. **获取选择包围盒**：通过 `UAvaBoundsProviderSubsystem` → `Get Selection Bounds`（传入 `bIncludeChildren`）获取选中对象的整体包围盒，用于对齐和布局计算。

## C++ 用法

### 头文件引入

```cpp
#include "IAvaEditor.h"
#include "IAvaEditorExtension.h"
#include "AvaEditorBuilder.h"
#include "AvaEditorSubsystem.h"
#include "Selection/AvaSelectionProviderSubsystem.h"
#include "Bounds/AvaBoundsProviderSubsystem.h"
```

### 基本用法 — 创建编辑器实例

通过 `FAvaEditorBuilder` 构建一个 Motion Design 编辑器实例，设置 Provider 并添加扩展：

```cpp
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheEditorCore/Public/AvaEditorBuilder.h

// 使用 Builder 模式创建编辑器
TSharedRef<IAvaEditor> Editor = FAvaEditorBuilder()
    .SetIdentifier(FName("MyMotionDesignEditor"))
    .SetProvider<FMySceneProvider>(/* 构造参数 */)
    .AddExtension<FAvaToolbarExtension>()
    .AddExtension<FAvaSelectionExtension>()
    .Build();

// 激活编辑器
Editor->Activate();
```

### 基本用法 — 自定义编辑器扩展

```cpp
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheEditorCore/Public/IAvaEditorExtension.h

class FMyCustomExtension : public IAvaEditorExtension
{
public:
    // 编辑器激活时调用
    virtual void Activate() override
    {
        // 初始化扩展功能
    }

    // 扩展工具栏菜单
    virtual void ExtendToolbarMenu(UToolMenu& InMenu) override
    {
        // 向工具栏添加自定义按钮
    }

    // 响应选择变化
    virtual void NotifyOnSelectionChanged(const FAvaEditorSelection& InSelection) override
    {
        TArray<AActor*> SelectedActors = InSelection.GetSelectedObjects<AActor>();
        // 处理选择变化...
    }

    // 处理复制粘贴
    virtual void OnCopyActors(FString& OutCopyData, TConstArrayView<AActor*> InActorsToCopy) override
    {
        // 向复制数据中追加自定义信息
    }

    virtual void PostPasteActors(TConstArrayView<FAvaEditorPastedActor> InPastedActors) override
    {
        // 粘贴后处理，例如重建引用关系
    }

    virtual void Cleanup() override
    {
        // 清理资源
    }
};
```

### 进阶用法 — 查询选择与包围盒

```cpp
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheEditorCore/Public/Selection/AvaSelectionProviderSubsystem.h
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheEditorCore/Public/Bounds/AvaBoundsProviderSubsystem.h

UWorld* World = GetWorld();

// 获取选择子系统
UAvaSelectionProviderSubsystem* SelectionSubsystem = World->GetSubsystem<UAvaSelectionProviderSubsystem>();
TConstArrayView<TWeakObjectPtr<AActor>> SelectedActors = SelectionSubsystem->GetSelectedActors();
FTransform SelectionTransform = SelectionSubsystem->GetSelectionTransform();

// 获取包围盒子系统
UAvaBoundsProviderSubsystem* BoundsSubsystem = World->GetSubsystem<UAvaBoundsProviderSubsystem>();

// 缓存并查询单个 Actor 的有向包围盒
BoundsSubsystem->CacheActorOrientedBounds(MyActor);
FOrientedBox OrientedBounds;
if (BoundsSubsystem->GetActorOrientedBounds(MyActor, OrientedBounds))
{
    // 使用有向包围盒进行布局计算
}

// 获取整个选择的包围盒（包含子 Actor）
FBox SelectionBounds = BoundsSubsystem->GetSelectionBounds(true /* bIncludeChildren */);
```

### 进阶用法 — 注册自定义标签页

```cpp
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheEditorCore/Public/AvaTabSpawner.h

class FMyCustomTabSpawner : public FAvaTabSpawner
{
public:
    FMyCustomTabSpawner(const TSharedRef<IAvaEditor>& InEditor)
        : FAvaTabSpawner(InEditor, FName("MyCustomTab"))
    {
        TabLabel = NSLOCTEXT("MyPlugin", "CustomTab", "My Custom Tab");
        TabTooltipText = NSLOCTEXT("MyPlugin", "CustomTabTooltip", "Opens the custom panel");
    }

    virtual TSharedRef<SWidget> CreateTabBody() override
    {
        return SNew(SVerticalBox)
            + SVerticalBox::Slot()
            [
                SNew(STextBlock).Text(FText::FromString(TEXT("Hello from custom tab!")))
            ];
    }
};

// 在扩展中注册
virtual void RegisterTabSpawners(const TSharedRef<IAvaEditor>& InEditor) const override
{
    InEditor->RegisterTabSpawner(MakeShared<FMyCustomTabSpawner>(InEditor));
}
```

### 进阶用法 — 用户输入对话框

```cpp
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheEditorCore/Public/Widgets/SAvaUserInputDialog.h
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheEditorCore/Public/Widgets/DataTypes/AvaUserInputDialogDataTypeText.h

// 弹出文本输入对话框
FAvaUserInputDialogTextData::FParams TextParams;
TextParams.InitialValue = FText::FromString(TEXT("Default Name"));
TextParams.bAllowMultiline = false;
TextParams.MaxLength = 64;

auto TextData = MakeShared<FAvaUserInputDialogTextData>(TextParams);

if (SAvaUserInputDialog::CreateModalDialog(TextData, nullptr,
    FText::FromString(TEXT("请输入名称：")),
    FText::FromString(TEXT("重命名"))))
{
    FText UserValue = TextData->GetValue();
    // 使用用户输入的值...
}
```

```cpp
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheEditorCore/Public/Widgets/DataTypes/AvaUserInputDialogDataTypeNumeric.h

// 弹出数值输入对话框
FAvaUserInputDialogNumericData<float>::FParams NumParams;
NumParams.InitialValue = 1.0f;
NumParams.MinValue = 0.0f;
NumParams.MaxValue = 100.0f;

auto NumericData = MakeShared<FAvaUserInputDialogNumericData<float>>(NumParams);

if (SAvaUserInputDialog::CreateModalDialog(NumericData))
{
    float Value = NumericData->GetValue();
    // 使用数值...
}
```

## Demo 示例

一个最小的自定义编辑器扩展，注册一个工具栏按钮和一个自定义标签页：

```cpp
// MyMotionDesignExtension.h
#pragma once

#include "IAvaEditorExtension.h"

class FMyMotionDesignExtension : public IAvaEditorExtension
{
public:
    virtual void Construct(const TSharedRef<IAvaEditor>& InEditor) override;
    virtual void Activate() override;
    virtual void Deactivate() override;
    virtual void ExtendToolbarMenu(UToolMenu& InMenu) override;
    virtual void RegisterTabSpawners(const TSharedRef<IAvaEditor>& InEditor) const override;
    virtual void NotifyOnSelectionChanged(const FAvaEditorSelection& InSelection) override;

private:
    TWeakPtr<IAvaEditor> EditorWeak;
};
```

```cpp
// MyMotionDesignExtension.cpp
#include "MyMotionDesignExtension.h"
#include "IAvaEditor.h"
#include "AvaTabSpawner.h"
#include "ToolMenus.h"
#include "Widgets/Text/STextBlock.h"

class FMyInfoTabSpawner : public FAvaTabSpawner
{
public:
    FMyInfoTabSpawner(const TSharedRef<IAvaEditor>& InEditor)
        : FAvaTabSpawner(InEditor, FName("MyInfoTab"))
    {
        TabLabel = NSLOCTEXT("MyMD", "InfoTab", "Info");
    }

    virtual TSharedRef<SWidget> CreateTabBody() override
    {
        return SNew(STextBlock).Text(FText::FromString(TEXT("My Motion Design Info Panel")));
    }
};

void FMyMotionDesignExtension::Construct(const TSharedRef<IAvaEditor>& InEditor)
{
    EditorWeak = InEditor;
}

void FMyMotionDesignExtension::Activate()
{
    UE_LOG(LogTemp, Log, TEXT("MyMotionDesignExtension activated"));
}

void FMyMotionDesignExtension::Deactivate()
{
    UE_LOG(LogTemp, Log, TEXT("MyMotionDesignExtension deactivated"));
}

void FMyMotionDesignExtension::ExtendToolbarMenu(UToolMenu& InMenu)
{
    FToolMenuSection& Section = InMenu.FindOrAddSection(
        IAvaEditorExtension::DefaultSectionName);
    Section.AddMenuEntry(
        FName("MyCustomAction"),
        FText::FromString(TEXT("My Action")),
        FText::FromString(TEXT("Performs a custom action")),
        FSlateIcon(),
        FUIAction(FExecuteAction::CreateLambda([]()
        {
            UE_LOG(LogTemp, Log, TEXT("Custom action executed!"));
        }))
    );
}

void FMyMotionDesignExtension::RegisterTabSpawners(const TSharedRef<IAvaEditor>& InEditor) const
{
    InEditor->RegisterTabSpawner(MakeShared<FMyInfoTabSpawner>(InEditor));
}

void FMyMotionDesignExtension::NotifyOnSelectionChanged(const FAvaEditorSelection& InSelection)
{
    TArray<AActor*> Selected = InSelection.GetSelectedObjects<AActor>();
    UE_LOG(LogTemp, Log, TEXT("Selection changed: %d actors"), Selected.Num());
}
```

## 模块依赖

AvalancheEditorCore 的 Build.cs 依赖（仅列出非常见依赖）：

| 模块 | 用途 |
|---|---|
| `AvalancheCore` | Motion Design 核心运行时类型系统（AvaType、AvaTypeId） |
| `ToolWidgets` | 编辑器工具控件 |
| `ToolMenus` | 工具栏/菜单扩展框架 |
| `WorkspaceMenuStructure` | 标签页工作区菜单结构 |
| `EditorFramework` | 编辑器框架（Toolkit、ToolkitHost） |

## 维护状态

### 近期更新

```
- 752af0d30748 Motion Design: fixed typo
- 46f74ef30651 Motion Design: added create default TL scene option to automatically set up a new motion design level with an empty transition logic set up. This option enables TL, sets it to reuse, and creates 4 sequences (In, Out, Layer1 Change In, Layer 1 Change Out). Additionally, a "layer 1 content" null actor is spawned in with sub layer modifier set to the layer 1 change in/out sequences set.
- 3e1bf2b58a66 Motion Design: Repurposed 'add' button in md sequence to now give additional options for presets for faster creation of sequences. In addition to that, new motion design levels auto-create 4 sequences for TL.
```

### 维护评价

- **创建时间**：2024 年 1 月，约 1 年历史，属于较新的插件
- **更新频率**：活跃开发中，近期 commit 包含功能增强（Transition Logic 场景创建、序列预设）和 bug 修复
- **维护状态**：**活跃维护** — 由 Epic Games 虚拟制片团队持续开发
- **规模**：xlarge 级别（2991 个源文件，41 个模块），架构成熟但仍在快速迭代
- **推荐度**：✅ **推荐使用** — 这是 Epic 官方的 Motion Design 工具，是虚拟制片工作流的核心组件。如果你的项目涉及实时运动图形、节目包装或广播合成，这是首选方案。注意它依赖多个其他插件（Remote Control、Text3D、SVG Importer 等），启用前需确保依赖可用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/motion-design-in-unreal-engine/)
# Guided Tutorials

> Adds classes and content that support running guided tutorials within the editor UI.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 引导教程 |
| 分类 | Learning |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（教程内容资产） |
| 模块 | `IntroTutorials` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-02-09 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/GuidedTutorials) | |

## 用途

Guided Tutorials 是一个编辑器插件，为 Unreal Editor 提供了一套构建交互式、分步骤教程的框架。它不是一个运行时功能，而是面向内容创作者和工具开发者的工具集，旨在解决“如何在编辑器内部提供结构化学习体验”的问题。通过它，你可以：
*   创建多阶段的教程，引导用户逐步操作。
*   将教程内容（文本、富文本）与具体的编辑器 UI 控件（例如按钮、菜单项、资产）精确关联，并高亮显示这些控件。
*   管理用户的教程进度、完成状态和配置。
*   在编辑器内提供一个统一的“教程浏览器”，让用户可以发现、启动和管理所有可用教程。

## 使用场景

*   你正在开发一个 UE5 编辑器扩展或新功能，希望提供内置的教学指南帮助用户上手 → 使用此插件创建功能专属教程。
*   你希望为你的游戏项目创建一套编辑器使用指南（如“蓝图入门”、“关卡编辑基础”）→ 使用此插件构建可交互的引导课程。
*   你需要管理多个教程的分类、排序和显示策略（例如在哪个编辑器上下文中显示哪个教程）→ 使用 `UEditorTutorialSettings` 和 `UTutorialStateSettings` 进行配置。

## 蓝图用法

该插件的核心类 `UEditorTutorial` 是 `Blueprintable` 的，因此可以通过创建蓝图子类来定义教程。以下是用于控制教程流程和行为的核心节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BeginTutorial` | 启动一个指定的教程。如果已有教程在进行，会先结束它。 | `UEditorTutorial` (静态) |
| `GoToNextTutorialStage` | 跳转到当前教程的下一阶段。 | `UEditorTutorial` (静态) |
| `GoToPreviousTutorialStage` | 跳转到当前教程的上一阶段。 | `UEditorTutorial` (静态) |
| `OpenAsset` | 在编辑器中打开一个指定的资产（常用于在教程中引导用户查看特定资产）。 | `UEditorTutorial` (静态) |
| `SetEngineFolderVisibilty` | 设置内容浏览器中“引擎”文件夹的可见性（用于教学演示）。 | `UEditorTutorial` (静态) |
| `GetActorReference` | 根据路径字符串在当前关卡中获取一个 Actor 的引用。 | `UEditorTutorial` (实例) |

此外，`UEditorTutorial` 还提供了一系列 `BlueprintImplementableEvent`，允许你在教程生命周期的关键点添加自定义逻辑：
*   `OnTutorialStageStarted`：教程阶段开始时触发。
*   `OnTutorialStageEnded`：教程阶段结束时触发。
*   `OnTutorialLaunched`：教程启动时触发。
*   `OnTutorialClosed`：教程关闭时触发。

### 使用示例（蓝图描述）

1.  **创建教程资产**：在内容浏览器右键 -> `Blueprint Class` -> 选择父类为 `EditorTutorial`。
2.  **定义教程阶段**：在蓝图编辑器中，编辑 `Stages` 数组。为每个 `FTutorialStage` 添加一个 `Name`，并在 `Content` 或 `WidgetContent` 中设置要显示的文本和 UI 锚点。
3.  **配置教程属性**：设置教程的 `Title`、`Category`、`Icon`、`SortOrder` 等元数据。
4.  **启动教程**：在另一个蓝图或编辑器工具中，调用 `BeginTutorial` 节点，传入你创建的教程蓝图类。
5.  **控制流程**：在教程蓝图内部，可以重写 `OnTutorialStageEnded` 等事件，并在其中调用 `GoToNextTutorialStage` 来自动推进流程，或根据条件判断是否跳转。
6.  **关联 UI**：在 `FTutorialWidgetContent` 的 `WidgetAnchor` 中，通过 `NamedWidget` 或 `Asset` 类型指定要高亮和提示的具体编辑器控件。

## C++ 用法

### 头文件引入

```cpp
#include "IntroTutorials.h"
```

### 基本用法

创建一个 `UEditorTutorial` 的子类来定义教程。这通常在编辑器模块中完成。

```cpp
// MyTutorial.h
#pragma once

#include "CoreMinimal.h"
#include "EditorTutorial.h" // 来自 IntroTutorials 模块
#include "MyTutorial.generated.h"

UCLASS()
class UMyFirstTutorial : public UEditorTutorial
{
    GENERATED_UCLASS_BODY()

public:
    UMyFirstTutorial();
};
```

```cpp
// MyTutorial.cpp
#include "MyTutorial.h"

UMyFirstTutorial::UMyFirstTutorial()
{
    Title = FText::FromString(TEXT("我的第一个教程"));
    Category = TEXT("Custom");
    bIsStandalone = false;

    // 定义第一个阶段
    FTutorialStage& WelcomeStage = Stages.AddDefaulted_GetRef();
    WelcomeStage.Name = FName(TEXT("Welcome"));
    WelcomeStage.Content.Type = ETutorialContent::RichText;
    WelcomeStage.Content.Text = FText::FromString(TEXT("欢迎来到本教程！请点击下一步继续。"));
    WelcomeStage.NextButtonText = FText::FromString(TEXT("开始学习"));
    WelcomeStage.BackButtonText = FText::FromString(TEXT("返回"));

    // 定义第二个阶段，关联一个具体的 UI 控件
    FTutorialStage& ClickButtonStage = Stages.AddDefaulted_GetRef();
    ClickButtonStage.Name = FName(TEXT("ClickButton"));
    ClickButtonStage.Content.Text = FText::FromString(TEXT("现在，请点击下面高亮的按钮。"));

    FTutorialWidgetContent& WidgetContent = ClickButtonStage.WidgetContent.AddDefaulted_GetRef();
    WidgetContent.Content.Text = FText::FromString(TEXT("点击此按钮"));
    WidgetContent.WidgetAnchor.Type = ETutorialAnchorIdentifier::NamedWidget;
    WidgetContent.WidgetAnchor.WrapperIdentifier = FName(TEXT("TargetButtonName")); // 需与编辑器中实际控件名匹配
    WidgetContent.bAutoFocus = true;
}
```

### 进阶用法

可以通过 `IIntroTutorials` 接口以编程方式启动和管理教程。

```cpp
// 获取 IIntroTutorials 模块接口
if (IIntroTutorials::IsAvailable())
{
    IIntroTutorials& TutorialModule = IIntroTutorials::Get();

    // 方式1：通过资产路径字符串启动
    TutorialModule.LaunchTutorial(TEXT("/Game/Tutorials/BP_MyTutorial.BP_MyTutorial"));

    // 方式2：通过 UEditorTutorial* 指针启动，并指定启动类型
    UEditorTutorial* MyTutorial = LoadObject<UEditorTutorial>(nullptr, TEXT("/Game/Tutorials/BP_MyTutorial.BP_MyTutorial_C"));
    if (MyTutorial)
    {
        TutorialModule.LaunchTutorial(MyTutorial, IIntroTutorials::TST_RESTART);
    }

    // 注册一个新的教程分类（通常由插件完成）
    FTutorialCategory NewCategory;
    NewCategory.Identifier = TEXT("MyPlugin.Features");
    NewCategory.Title = FText::FromString(TEXT("我的插件功能"));
    NewCategory.Description = FText::FromString(TEXT("学习使用我的插件提供的高级功能。"));
    TutorialModule.RegisterCategory(NewCategory);
}
```

## Demo 示例

以下是一个最小的可编译教程类示例。

```cpp
// MinimalTutorial.h
#pragma once

#include "CoreMinimal.h"
#include "EditorTutorial.h"
#include "MinimalTutorial.generated.h"

UCLASS()
class UMinimalTutorial : public UEditorTutorial
{
    GENERATED_BODY()

public:
    UMinimalTutorial();
};
```

```cpp
// MinimalTutorial.cpp
#include "MinimalTutorial.h"

UMinimalTutorial::UMinimalTutorial()
{
    Title = FText::FromString(TEXT("最小化教程示例"));
    SortOrder = 100;
    bIsStandalone = true;

    // 阶段 1: 纯文本介绍
    FTutorialStage& IntroStage = Stages.AddDefaulted_GetRef();
    IntroStage.Name = TEXT("Intro");
    IntroStage.Content.Text = FText::FromString(TEXT("这是一个最简单的引导教程演示。"));
    IntroStage.NextButtonText = FText::FromString(TEXT("下一步"));

    // 阶段 2: 高亮一个编辑器控件
    FTutorialStage& HighlightStage = Stages.AddDefaulted_GetRef();
    HighlightStage.Name = TEXT("Highlight");
    HighlightStage.Content.Text = FText::FromString(TEXT("注意下方高亮的“保存”按钮。"));

    FTutorialWidgetContent& SaveButtonHint = HighlightStage.WidgetContent.AddDefaulted_GetRef();
    SaveButtonHint.Content.Text = FText::FromString(TEXT("点击这里保存您的作品。"));
    SaveButtonHint.WidgetAnchor.Type = ETutorialAnchorIdentifier::NamedWidget;
    SaveButtonHint.WidgetAnchor.WrapperIdentifier = FName(TEXT("SaveButton")); // 这个名称需要与编辑器工具栏中按钮的Widget名匹配
    SaveButtonHint.Offset = FVector2D(0.f, -20.f); // 微调提示位置
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | 该插件主要依赖 Unreal Editor 的基础模块，如 `Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore`, `InputCore`, `UnrealEd`，以及用于资产浏览和发现的 `ContentBrowser` 和 `AssetRegistry`。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从旧的 UE_LOG 迁移到新的 UE_LOGF 格式。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 重命名配置文件从 BaseGuidedTutorials.ini 为 DefaultGuidedTutorials.ini，符合 UE 新规范。 |
| 2025-05-21 | `269aeb1b` | Replaced bool arguments with EFindObjectFlags. | 替换了 FindObject 函数中的布尔参数，使用枚举标志以提高代码可读性。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复了代码中的一些琐碎的、不可达代码警告。 |
| 2024-06-27 | `a890c0ce` | Fixed some 'deprecated' FString usage. | 修复了一些已弃用的 FString 用法。 |

### 维护评价

Guided Tutorials 插件自 2022 年创建以来，功能上已经稳定。从 git 历史看，最近一年仍有维护性更新，主要集中在代码风格统一、API 适配和编译警告修复，而非功能性新增。这表明插件处于**维护中**状态，核心功能完善，能够随着 UE 版本迭代而保持兼容。它仍然是在编辑器内创建正式教学内容的官方推荐方案，适合用于项目或插件开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/GuidedTutorials)
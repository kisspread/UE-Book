# Code Editor

> [EXPERIMENTAL] Allows editing of code from within the Unreal editor

| 属性 | 值 |
|---|---|
| 中文名 | 代码编辑器 |
| 分类 | Programming |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CodeEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2015-03-17 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CodeEditor) | |

## 用途

Code Editor 插件是一个实验性的、集成在 Unreal 编辑器内部的源代码编辑器。它的核心目的是让开发者能够在不离开编辑器环境的情况下，直接查看、编辑、保存和编译项目的 C++ 或其他源代码文件。该插件通过创建一个专门的资产（`UCodeProject`）来表示一个代码项目，并为其提供一个完整的编辑器界面，包括项目文件浏览器、带语法高亮的代码编辑区以及工具栏。它旨在简化开发流程，避免开发者在编辑器和外部 IDE 之间频繁切换。

## 使用场景

- **快速代码修复**：当你在编辑器内发现一个小 bug 或需要进行一个小的代码修改（例如调整一个变量的值或添加一个简单的日志语句），不想中断当前工作流去启动完整的 IDE 时，可以使用这个内置编辑器进行修改和编译。
- **代码浏览与导航**：在编辑器内快速浏览项目文件结构，查看源代码，而无需打开外部工具。
- **原型开发与内部测试**：由于其“实验性”状态，它可能主要用于 Epic 内部测试或特定原型开发流程，而不推荐在生产环境中作为主力编辑器。

## 蓝图用法

此插件主要为编辑器扩展和 Slate UI 提供功能，直接暴露给蓝图的节点非常有限。其主要用途是通过 C++ 创建和管理编辑器实例。

### 核心属性

| 属性 | 说明 | 所在类 |
|---|---|---|
| `Controls` | 一个数组，用于定义编辑器控件（如滚动条）的颜色自定义。 | `UCodeEditorCustomization` |
| `Text` | 一个数组，用于定义不同语法元素（关键字、注释等）的字体和颜色样式。 | `UCodeEditorCustomization` |

### 使用示例（蓝图描述）

由于此插件主要是编辑器框架，没有提供直接在运行时游戏蓝图中使用的节点。其自定义设置 `UCodeEditorCustomization` 是一个配置类，通常通过编辑器首选项或配置文件进行修改，而不是在蓝图图表中动态设置。

## C++ 用法

### 头文件引入

要使用此插件提供的类，需要包含相应的头文件。

```cpp
#include "CodeProjectEditor.h"      // 主编辑器类
#include "CodeProject.h"            // 代码项目资产
#include "CodeProjectItem.h"        // 项目内的文件/文件夹项
```

### 基本用法

以下代码演示了如何以编程方式初始化代码编辑器并打开一个 `UCodeProject` 资产进行编辑。

```cpp
// 假设你已经有一个有效的 UCodeProject 资产指针 InCodeProjectToEdit
UCodeProject* InCodeProjectToEdit = ...;

// 获取或创建编辑器实例
TSharedPtr<FCodeProjectEditor> CodeEditor = FCodeProjectEditor::Get();
if (!CodeEditor.IsValid())
{
    CodeEditor = MakeShareable(new FCodeProjectEditor());
}

// 初始化编辑器并打开项目
// EToolkitMode::Standalone 表示独立窗口模式
CodeEditor->InitCodeEditor(EToolkitMode::Standalone, TSharedPtr<IToolkitHost>(), InCodeProjectToEdit);

// 打开项目中的特定文件进行编辑
// 假设你已经遍历了 InCodeProjectToEdit 的子项，并找到了代表目标文件的 UCodeProjectItem
UCodeProjectItem* TargetFileItem = ...;
CodeEditor->OpenFileForEditing(TargetFileItem);
```

**来源**: 从 `FCodeProjectEditor::InitCodeEditor` 和 `OpenFileForEditing` 方法的功能推断。

### 进阶用法

可以进一步控制编辑器的行为，例如处理文件保存和利用语法高亮器。

```cpp
// 1. 保存当前打开的文件
bool bSaveSuccess = CodeEditor->Save();

// 2. 保存项目中的所有已修改文件
bool bSaveAllSuccess = CodeEditor->SaveAll();

// 3. 使用语法高亮器（内部实现，通常不直接调用）
// 代码编辑器内部使用 FCPPRichTextSyntaxHighlighterTextLayoutMarshaller 来处理 C++ 语法高亮。
// 它通过 FSyntaxHighlighterTextLayoutMarshaller 基类和自定义的 ISyntaxTokenizer 来解析源代码文本，
// 并为其应用不同的 FTextBlockStyle（对应关键字、注释、字符串等）。
// 你可以在创建自定义编辑器组件时参考其内部逻辑。
```

## Demo 示例

一个展示如何创建并显示一个简单代码编辑器窗口的最小示例。

```cpp
// CodeEditorDemo.h
#pragma once
#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class SCodeEditorDemo : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SCodeEditorDemo) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<class SCodeProjectEditor> ProjectEditorWidget;
};
```

```cpp
// CodeEditorDemo.cpp
#include "CodeEditorDemo.h"
#include "SCodeProjectEditor.h"
#include "CodeProject.h"
#include "Engine/AssetManager.h"

void SCodeEditorDemo::Construct(const FArguments& InArgs)
{
    // 尝试从内容浏览器加载或创建一个 UCodeProject 资产
    // 注意：在实际使用中，你可能需要先通过工厂创建或从磁盘加载
    UCodeProject* DemoProject = NewObject<UCodeProject>(GetTransientPackage(), TEXT("DemoCodeProject"));

    // 创建项目编辑器 Slate 控件
    ProjectEditorWidget = SNew(SCodeProjectEditor, DemoProject);

    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Embedded Code Editor Demo")))
        ]
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        [
            ProjectEditorWidget.ToSharedRef()
        ]
    ];
}
```

**说明**：此示例创建了一个包含代码项目编辑器控件的 Slate 窗口。要看到实际效果，你需要在编辑器工具或单独的窗口中实例化 `SCodeEditorDemo`。由于 `UCodeProject` 的初始化依赖于磁盘上的文件扫描，实际使用中可能需要更复杂的设置。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `WorkspaceMenuStructure` | 提供编辑器工作区菜单结构的基础类，用于注册编辑器标签页。 |
| `DirectoryWatcher` | 监控项目文件所在目录的变化，以更新项目视图树。 |

**说明**：此插件依赖于 `UnrealEd` 等标准编辑器模块（未在表格中列出）。`DirectoryWatcher` 用于实时监控文件系统变动，是其文件树动态更新功能的基础。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了上一次提交中错误的查找替换后重新提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了变更列表 CL51314860 的修改。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 将引擎初始化委托的获取方式从静态成员改为静态方法调用，以修复注册问题。 |
| 2025-12-09 | `0ce72078` | HarmonixNiagaraEditor | 提交信息不明确，可能与 Niagara 编辑器相关（非直接功能更新）。 |
| 2025-12-08 | `0a66df2d` | [Backout] - CL49053845 | 回退了变更列表 CL49053845 的修改。 |

### 维护评价

- **创建时间**：2015年3月，距今超过11年。
- **最近更新**：最近几次更新（2026年）均涉及编译修复和回退，没有实质性新功能添加。
- **活跃度**：更新非常不频繁，且内容与核心功能无关。
- **状态判断**：此插件自首次提交以来，其功能列表中的 TODO 项（如 Clang 语法高亮、源代码管理集成等）从未完成。它始终保持 `IsExperimentalVersion: true` 和 `EnabledByDefault: false` 状态。虽然最近有代码提交，但这很可能只是为了维护编译兼容性，而非积极开发新功能。
- **推荐使用**：**不推荐在生产项目中使用**。它是一个陈旧的实验性插件，功能不完整，缺乏维护，且未集成现代 UE 开发所需的关键特性。建议使用外部 IDE（如 Visual Studio, Rider）或 Epic 官方后续推出的、更成熟的代码编辑解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CodeEditor)
- [官方文档]()（无）
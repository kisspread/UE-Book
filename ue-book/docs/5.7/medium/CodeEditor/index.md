```markdown
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
| 创建时间 | 2022-10-21 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CodeEditor) | |

## 用途

Code Editor 插件提供了一个轻量级的 C++ 源代码编辑器，可以直接在 Unreal Editor 内部浏览和编辑代码文件。它解决了在开发过程中需要在编辑器与外部 IDE 之间频繁切换的痛点，让你能够快速查看、修改和调试代码，而无需离开 UE 编辑器环境。

该插件通过自定义资产类型 `UCodeProject` 来管理项目文件结构，支持目录树浏览、多文件编辑、C++ 语法高亮（包括关键字、字符串、注释、数字、预处理器指令等）、智能缩进（Tab 转空格）等基本编辑功能。虽然功能远不及 Visual Studio 等专业 IDE，但对于快速修复、浏览或小范围修改代码非常实用。

## 使用场景

- **快速代码浏览与修复**：在编辑器中发现错误或需要调整逻辑，直接双击 `.h`/`.cpp` 文件或打开 Code Project 资产即可编辑，修改后立即在编辑器内编译，无需切换到外部 IDE。
- **多文件项目管理**：通过将源码目录组织为 `UCodeProject` 资产，你可以在编辑器中以树形结构查看整个项目，并同时打开多个文件进行对比或修改。
- **教学与演示**：在培训或演示过程中，可以直观地向观众展示 UE 源码的修改位置和效果，而不必切换窗口。
- **嵌入式开发快速迭代**：当使用 Hot Reload 或 Live Coding 时，很小的改动可以在编辑器内快速完成并应用。

## 蓝图用法

此插件为纯编辑器工具，**不暴露任何蓝图书节点**。所有功能均在编辑器 UI 和 C++ 层面实现。

## C++ 用法

要在 C++ 代码中使用 Code Editor 插件，主要操作包括：创建/打开 `UCodeProject` 资产，并通过标准的资产编辑器系统打开编辑界面。

### 头文件引入

```cpp
#include "CodeProject.h"
#include "CodeProjectItem.h"
#include "CodeProjectEditor.h"
#include "CodeProjectFactory.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "FileHelpers.h"
#include "Toolkits/AssetEditorManager.h"
```

### 基本用法

#### 1. 通过 Content 资产路径打开已有的 CodeProject

```cpp
// 来源：插件测试或典型用例
void OpenExistingCodeProject()
{
    // 从内容浏览器中加载已创建的 CodeProject 资产
    UCodeProject* MyProject = LoadObject<UCodeProject>(nullptr, TEXT("/Game/MyCodeProject.MyCodeProject"));
    if (MyProject)
    {
        // 使用标准资产编辑器框架打开
        FAssetEditorManager::Get().OpenEditorForAsset(MyProject);
    }
}
```

#### 2. 以编程方式创建一个新的 CodeProject 资产并立即打开

```cpp
// 来源：UCodeProjectFactory 实现
void CreateAndOpenNewCodeProject(const FString& ProjectPath, const FString& ProjectName)
{
    // 确保内容浏览器路径存在
    UPackage* Package = CreatePackage(*(ProjectPath + "/" + ProjectName));
    UCodeProject* NewProject = NewObject<UCodeProject>(Package, *ProjectName, RF_Public | RF_Standalone);

    // 保存资产到磁盘
    FString PackageFileName = FPackageName::LongPackageNameToFilename(ProjectPath + "/" + ProjectName, FPackageName::GetAssetPackageExtension());
    UPackage::SavePackage(Package, NewProject, RF_Public | RF_Standalone, *PackageFileName, GError, nullptr, false, true, SAVE_NoError);

    // 通知资产注册表刷新
    FAssetRegistryModule::AssetCreated(NewProject);
    NewProject->MarkPackageDirty();

    // 打开编辑器
    FAssetEditorManager::Get().OpenEditorForAsset(NewProject);
}
```

### 进阶用法

#### 手动控制编辑器窗口

你可以在自己的 Editor Module 中直接实例化 `FCodeProjectEditor` 并调用 `InitCodeEditor`，以完全控制编辑器的创建过程。以下示例展示如何在一个自定义的工具栏按钮点击时打开代码编辑器：

```cpp
// 假设你已经有一个有效的 UCodeProject 指针
void MyCustomTool::OpenCodeEditorForProject(UCodeProject* InProject)
{
    // 创建编辑器实例（需要以 Editor Toolkit 模式运行）
    TSharedPtr<FCodeProjectEditor> NewEditor = MakeShareable(new FCodeProjectEditor());
    NewEditor->InitCodeEditor(
        EToolkitMode::Standalone,
        TSharedPtr<IToolkitHost>(),
        InProject
    );

    // 编辑器实例会在内部维护，通常不需要手动释放
}
```

> **注意**：`FCodeProjectEditor` 是基于 `FWorkflowCentricApplication` 的，使用时需要确保在有效的编辑器模块生命周期内。

## Demo 示例

以下是一个最小化的完整 C++ 示例，展示了如何在你的 Editor Module 中添加一个控制台命令，以打开一个指定的 CodeProject 资产。

### MyTestCommands.h

```cpp
#pragma once

#include "CoreMinimal.h"

class FMyTestCommands
{
public:
    static void RegisterCommands();
    static void ExecuteOpenCodeProject();
};
```

### MyTestCommands.cpp

```cpp
#include "MyTestCommands.h"
#include "CodeProject.h"
#include "CodeProjectEditor.h"
#include "Framework/Commands/Commands.h"
#include "Framework/Commands/UICommandList.h"
#include "LevelEditor.h"
#include "Toolkits/AssetEditorManager.h"

#define LOCTEXT_NAMESPACE "MyTestCommands"

class FMyTestCommandImpl : public TCommands<FMyTestCommandImpl>
{
public:
    FMyTestCommandImpl()
        : TCommands<FMyTestCommandImpl>(TEXT("MyTestCommand"), LOCTEXT("MyTestCommand", "My Test Commands"), NAME_None, FName(TEXT("MyTestStyle")))
    {}

    virtual void RegisterCommands() override
    {
        UI_COMMAND(OpenCodeProject, "Open Code Project", "Open a CodeProject asset by path", EUserInterfaceActionType::Button, FInputChord());
    }

    TSharedPtr<FUICommandInfo> OpenCodeProject;
};

void FMyTestCommands::RegisterCommands()
{
    FMyTestCommandImpl::Register();
}

void FMyTestCommands::ExecuteOpenCodeProject()
{
    // 需要替换为项目中实际存在的 CodeProject 资产路径
    const FString AssetPath = TEXT("/Game/MyCodeProject.MyCodeProject");

    UCodeProject* Project = LoadObject<UCodeProject>(nullptr, *AssetPath);
    if (Project)
    {
        FAssetEditorManager::Get().OpenEditorForAsset(Project);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("CodeProject asset not found: %s"), *AssetPath);
    }
}
```

### 模块启动时注册命令（放在你模块的 StartupModule 中）

```cpp
#include "MyTestCommands.h"

void FMyModule::StartupModule()
{
    FMyTestCommands::RegisterCommands();

    // 注册到 Level Editor 菜单栏（示例）
    FLevelEditorModule& LevelEditorModule = FModuleManager::LoadModuleChecked<FLevelEditorModule>("LevelEditor");
    TSharedPtr<FExtender> Extender = MakeShareable(new FExtender());
    Extender->AddMenuExtension(
        "FileOpen",
        EExtensionHook::After,
        nullptr,
        FMenuExtensionDelegate::CreateLambda([](FMenuBuilder& Builder) {
            Builder.AddMenuEntry(FMyTestCommandImpl::Get().OpenCodeProject);
        })
    );
    LevelEditorModule.GetMenuExtensibilityManager()->AddExtender(Extender);
}
```

> 此示例假设你有一个包含模块 `MyModule` 的插件，并已在 Build.cs 中添加了对 `CodeEditor`、`UnrealEd`、`LevelEditor` 等模块的依赖。

## 模块依赖

要使用 Code Editor 插件的功能，你的模块需要在 `Build.cs` 中添加对以下模块的依赖。

| 模块 | 用途 |
|---|---|
| `WorkflowOrientedApp` | 提供 `FWorkflowCentricApplication` 基石，支持多文档编辑器框架 |
| `DesktopPlatform` | 用于文件系统操作（如扫描目录） |
| `AssetRegistry` | 管理 CodeProject 资产的注册和查找 |

其他常见依赖（Core、CoreUObject、Engine、Slate、SlateCore、UnrealEd、EditorStyle、InputCore、Projects 等）无需额外声明。

## 维护状态

### 近期更新

- 2024-11-15 a2c3875d — Cleanup of FSlateFontInfo constructor across the solution that uses font paths. It will be deprecate
- 2023-05-16 de8db5ff — Converting ARO-facing raw pointers to TObjectPtr ahead of raw pointer ARO API deprecation.
- 2023-01-27 f9121212 — Added generated.h includes and updated enums to have underlying types.
- 2023-01-16 bbc37aa2 — [Engine/Plugins] (批量编译修复)
- 2022-10-21 610c4676 — Update vendor links for built-in plugins to use secure protocol.

### 维护评价

- **创建时间**：2022-10-21（约 3 年）
- **最近更新频率**：最近一次实质性更新在 2024-11（字体构造清理），其他更新多为结构体属性调整或批量修复。
- **活跃度**：**维护不活跃**。近两年内没有新增功能或 bug 修复，仅有少量 API 兼容性更新。插件仍标记为实验性（Beta），未正式发布。
- **已知限制**：
  - 功能较为基础，不支持代码补全、编译、调试等功能。
  - 文件监视（Directory Watcher）可能存在性能问题（参见 `FDirectoryScanner` 实现）。
  - 依赖的 Slate 富文本组件渲染较慢，不适合超大型文件。
- **推荐使用**：如果你需要快速在编辑器中修改少量代码，或想要在纯编辑器环境中浏览源码，这个插件可以满足需求。但对于日常开发，**强烈建议使用专业 IDE**（Visual Studio、Rider）。该插件未来可能被废弃或整合到其他工具中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CodeEditor)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/code-editor-in-unreal-engine/)（可能需要手动搜索）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CodeEditor/Tests)（该插件未提供独立测试目录）
```
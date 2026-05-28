# AutomatedPerfTestTools

> Tools for Automated Perf Testing framework

| 属性 | 值 |
|---|---|
| 中文名 | 自动化性能测试工具 |
| 分类 | Testing |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AutomatedPerfTestLaunchExtension` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-06 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTestTools) | |

## 用途

该插件为 Unreal Frontend (UFE) 提供了一个 `Launch Extension`，用于在无编辑器环境下配置和运行自动化性能测试。它将性能测试配置从 Unreal Editor 的依赖中解耦，使得通过 UFE 或命令行启动的自动化测试流程也能使用完整的性能测试框架（如 Sequence, Replay, ProfileGo 等）。其核心是扩展 `ProjectLauncher` 插件的功能，为自动化测试配置界面添加专门的选项和参数。

## 使用场景

- **持续集成 (CI)**：在自动化构建流水线中，通过 Unreal Frontend 调起性能测试，无需启动完整的编辑器。
- **远程/服务器测试**：在只有 UFE 的无头 (headless) 环境中配置和启动游戏项目的性能回归测试。
- **需要快速配置多种测试模式**：为 Sequence、Replay、ProfileGo、静态相机等不同性能测试场景提供统一的配置入口。

## 蓝图用法

该插件主要为编辑器/工具链功能，不提供运行时蓝图节点。其功能通过 UFE 的扩展菜单集成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CustomizeTree` | 在 UFE 的启动配置界面中，根据当前选择的测试类型，动态显示/隐藏相关的配置选项树节点。 | `FAutomatedPerfTestLaunchExtensionInstance` |
| `CustomizeUATCommandLine` | 在 UFE 生成最终的 UAT (Unreal Automation Tool) 命令行时，将插件特定的配置参数（如测试类型、LLM、GPU分析等）附加到命令行中。 | `FAutomatedPerfTestLaunchExtensionInstance` |
| `OnTestAdded` | 当用户在 UFE 界面添加一个新的自动化测试条目时被调用，用于进行初始化设置。 | `FAutomatedPerfTestLaunchExtensionInstance` |
| `OnTestTypeSelectionChanged` | 当用户在 UI 上切换测试类型（如从 Sequence 切到 Replay）时被调用，用于更新内部状态和界面。 | `FAutomatedPerfTestLaunchExtensionInstance` |

### 使用示例（蓝图描述）

此插件的“蓝图”主要指 UFE 中的图形化配置。使用流程如下：
1. 在 Unreal Frontend 中创建一个新的“启动配置文件 (Launch Profile)”。
2. 在左侧菜单栏找到并点击“自动化性能测试 (Automated Perf Test)”扩展入口。
3. 在右侧出现的配置面板中，通过下拉菜单选择测试类型（如 `Sequence`, `Replay`）。
4. 根据所选类型，面板会动态显示对应的配置项（如序列名称、回放文件、ProfileGo 场景文件等）。
5. 勾选额外的性能分析选项，如启用 LLM 或 GPU 性能统计。
6. 保存配置后，UFE 即可使用此配置启动应用程序并执行自动化测试。

## C++ 用法

### 头文件引入

```cpp
#include "AutomatedPerfTestLaunchExtensionModule.h"
```

### 基本用法

该插件作为模块在 `UnrealFrontend` 启动时自动加载并注册其扩展。通常，用户代码无需直接交互。主要交互是通过 `ProjectLauncher` 的接口。

```cpp
// 在 UFE 启动时，模块会自动注册扩展。以下是其内部注册逻辑的示例。
void FAutomatedPerfTestLaunchExtensionModule::StartupModule()
{
    // 创建一个 AutomatedPerfTestLaunchExtension 实例并添加到扩展列表
    Extensions.Add(MakeShared<FAutomatedPerfTestLaunchExtension>());
    // 将扩展注册到 ProjectLauncher 系统
    for (const auto& Extension : Extensions)
    {
        ProjectLauncher::Get().AddExtension(Extension);
    }
}
```

### 进阶用法

插件通过 `FAutomatedPerfTestLaunchExtensionInstance` 与 `ProjectLauncher` 的配置文件树深度集成。它根据 `EAutomatedPerfTestType` 枚举来管理不同测试类型的 UI 和参数。

```cpp
// 示例：为特定的测试类型（如 Sequence）添加配置节点
void FAutomatedPerfTestLaunchExtensionInstance::AddSequenceTestNodeOptions(ProjectLauncher::FLaunchProfileTreeNode& TreeNode)
{
    // 创建一个文本输入框节点，用于指定 Sequence 名称
    TreeNode.AddChild(ProjectLauncher::SNew(ProjectLauncher::SWidgetNode)
        .DisplayName(LOCTEXT("SequenceName", "Sequence Name"))
        [
            SNew(SEditableTextBox)
            .Text(this, &FAutomatedPerfTestLaunchExtensionInstance::GetSequenceName)
            .OnTextChanged(this, &FAutomatedPerfTestLaunchExtensionInstance::OnSequenceNameChanged)
        ]
    );
    // 使用回调来控制此节点的可见性和启用状态，仅当测试类型为 Sequence 时显示
    .Callbacks(GetTestTypeCallbacks<EAutomatedPerfTestType::Sequence>());
}
```

## Demo 示例

由于该插件是 UFE 的扩展，其“Demo”是集成在 UFE 中的 UI。以下是一个极简的自定义 Launch Extension 的示例，用于说明插件扩展机制。

**`MyCustomLaunchExtension.h`**
```cpp
#pragma once
#include "LaunchExtension.h" // 来自 ProjectLauncher 插件

// 定义一个自定义的 Launch Extension 实例
class FMyCustomLaunchExtensionInstance : public ProjectLauncher::FLaunchExtensionInstance
{
public:
    using FLaunchExtensionInstance::FLaunchExtensionInstance;

    // 当配置文件的属性变化时调用
    virtual void OnPropertyChanged() override
    {
        UE_LOG(LogTemp, Log, TEXT("Custom property changed!"));
    }

    // 自定义 UFE 界面树
    virtual void CustomizeTree(ProjectLauncher::FLaunchProfileTreeData& ProfileTreeData) override
    {
        // 添加一个简单的文本说明
        ProfileTreeData.TreeRoot.AddChild(
            ProjectLauncher::SNew(ProjectLauncher::SWidgetNode)
            .DisplayName(LOCTEXT("MyExtension", "My Extension"))
            [
                SNew(STextBlock)
                .Text(LOCTEXT("Info", "This is a custom extension"))
            ]
        );
    }
};

// 定义 Launch Extension 的工厂类
class FMyCustomLaunchExtension : public ProjectLauncher::FLaunchExtension
{
public:
    virtual TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> CreateInstanceForProfile(ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs) override
    {
        return MakeShared<FMyCustomLaunchExtensionInstance>(InArgs);
    }
    virtual const TCHAR* GetInternalName() const override { return TEXT("MyCustom"); }
    virtual FText GetDisplayName() const override { return LOCTEXT("Name", "My Custom Extension"); }
};
```

**`MyLaunchExtensionModule.cpp`** (模块实现)
```cpp
#include "MyCustomLaunchExtension.h"
#include "Modules/ModuleManager.h"
#include "ProjectLauncher.h" // ProjectLauncher 模块接口

class FMyLaunchExtensionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        // 注册自定义扩展
        TSharedRef<FMyCustomLaunchExtension> Extension = MakeShared<FMyCustomLaunchExtension>();
        ProjectLauncher::Get().AddExtension(Extension);
        Extensions.Add(Extension);
    }

    virtual void ShutdownModule() override
    {
        // 注销扩展
        for (const auto& Extension : Extensions)
        {
            ProjectLauncher::Get().RemoveExtension(Extension);
        }
        Extensions.Empty();
    }

private:
    TArray<TSharedRef<ProjectLauncher::FLaunchExtension>> Extensions;
};

IMPLEMENT_MODULE(FMyLaunchExtensionModule, MyLaunchExtension)
```

## 模块依赖

从模块定义和源码分析，该插件依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `ProjectLauncher` | 核心依赖。提供 `FLaunchExtension`, `FLaunchExtensionInstance`, `FLaunchProfileTreeData` 等基础架构，用于向 Unreal Frontend 添加自定义的启动配置扩展。 |
| `Slate` | 用于构建扩展在 UFE 中的用户界面 (UI)。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `f2e0adf8` | Fixed AutomatedPerfTestTools plugin having the installed flag set to true | 修复了插件元数据中 `Installed` 标志被错误设置为 `true` 的问题，使其行为与描述一致。 |
| 2026-03-18 | `bb23bd67` | APT Launcher Extension Minor improvements and updates | 对 APT 启动扩展进行了小幅改进和更新。 |
| 2026-02-06 | `600e17a2` | APT: Remove Editor and Engine dependencies from APT Launcher Extension | 初始提交。将启动扩展从编辑器和引擎依赖中剥离，成为一个独立的 UFE 专用插件。 |

### 维护评价

该插件创建于 2026 年初，是一个相对较新的**实验性**项目。根据 Git 历史，它在创建后的几个月内进行了后续的维护和问题修复。最近的更新（2026年5月）修正了一个配置错误，表明该插件仍在**活跃开发**中。作为实验性功能，其 API 和实现未来可能会有变动。目前，它是 UE5 自动化性能测试工具链中一个针对 UFE 环境的专用组件，推荐需要在无编辑器环境中集成性能测试工作流的团队关注和试用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTestTools)
- [官方文档]() (暂无)
- [测试用例]() (源码中未包含独立的测试文件)
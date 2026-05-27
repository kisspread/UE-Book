# Automated Perf Test Tools

> Tools for Automated Perf Testing framework（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 自动化性能测试工具 |
| 分类 | Testing |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AutomatedPerfTestLaunchExtension` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-06 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTestTools) | |

## 用途

该插件扩展了 Unreal Frontend (UFE) 中的 **Project Launcher** 工具，为自动化性能测试 (APT) 框架提供了一个图形化配置界面。它解决的核心问题是：**允许测试人员在 Unreal Frontend 中方便地配置和启动各种类型的自动化性能测试**，而无需依赖完整的 Unreal Editor。通过将 APT 的启动器扩展独立出来，实现了轻量化和对 Engine/Editor 模块的零依赖，使其能够在独立的 Unreal Frontend 程序中运行，非常适合集成到 CI/CD 自动化流程中。

## 使用场景

- 你需要在 CI/CD 管道中自动化运行游戏性能基准测试，且希望使用 Unreal Frontend 而非完整的编辑器。
- 测试人员需要在一个简洁的界面中，配置并启动针对不同性能测试类型（如场景序列、Replay、ProfileGo 等）的自动化测试。
- 你想在不同的目标平台（Win64, Linux, Mac）上通过 Project Launcher 统一管理自动化性能测试的配置和执行。

## 蓝图用法

该插件主要通过 C++ 扩展 Unreal Frontend 的编辑器界面，不直接暴露节点给游戏逻辑蓝图。其核心功能是通过 Project Launcher 的扩展点实现的。

## C++ 用法

### 头文件引入

```cpp
#include "AutomatedPerfTestLaunchExtensionModule.h"
```

### 基本用法

该插件作为 Project Launcher 的扩展而存在，其核心类 `FAutomatedPerfTestLaunchExtension` 是 `ProjectLauncher::FAutomatedTestLaunchExtension` 的实现。通常不需要直接实例化，模块启动时会自动注册。

若需了解或扩展其内部行为，可以查看其子类：

```cpp
// 获取插件内部定义的测试类型枚举，用于区分不同的性能测试场景
enum class EAutomatedPerfTestType : uint8
{
    Sequence,    // 场景序列测试
    Replay,      // Replay 文件回放测试
    ProfileGo,   // ProfileGo 场景测试
    StaticCamera,// 静态相机测试
    Material,    // 材质测试
    MAX
};
```

### 进阶用法

该插件通过自定义 `FAutomatedPerfTestLaunchExtensionInstance` 来动态构建 Project Launcher 中的 UI 树 (`FLaunchProfileTreeData`) 并附加命令行参数。其核心机制是：
1.  **`CustomizeTree`**: 根据用户选择的测试类型 (`EAutomatedPerfTestType`)，动态显示/隐藏对应的配置选项节点。
2.  **`CustomizeUATCommandLine`**: 将 UI 上配置的测试参数（从 INI 配置文件读取）序列化为命令行字符串，传递给 UAT (Unreal Automation Tool)。

## Demo 示例

以下示例演示了如何在自己的模块中，参考 `AutomatedPerfTestLaunchExtension` 的模式，创建一个自定义的、更简单的 Launcher 扩展。

### MyCustomTestExtension.h
```cpp
// MyCustomTestExtension.h
#pragma once
#include "LaunchExtension.h"

// 自定义的 Launcher 扩展实例，代表一个可配置的测试会话
class FMyCustomTestLaunchExtensionInstance : public ProjectLauncher::FLaunchExtensionInstance
{
    using Super = ProjectLauncher::FLaunchExtensionInstance;
public:
    FMyCustomTestLaunchExtensionInstance(FArgs& InArgs) : Super(InArgs) {};
    virtual ~FMyCustomTestLaunchExtensionInstance() = default;

    // 当用户点击“运行”时，调用此方法来生成最终的命令行参数
    virtual void CustomizeUATCommandLine(FString& InOutCommandLine) override;

    // 自定义 Project Launcher 界面中的测试设置树
    virtual void CustomizeTree(ProjectLauncher::FLaunchProfileTreeData& ProfileTreeData) override;

private:
    bool bIsMyCustomTestEnabled = true;
};

// 自定义的 Launcher 扩展，负责创建上面的实例
class FMyCustomTestLaunchExtension : public ProjectLauncher::FLaunchExtension
{
public:
    virtual TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> CreateInstanceForProfile(ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs) override;
    virtual const TCHAR* GetInternalName() const override;
    virtual FText GetDisplayName() const override;
};
```

### MyCustomTestExtension.cpp
```cpp
// MyCustomTestExtension.cpp
#include "MyCustomTestExtension.h"
#include "Widgets/Input/SCheckBox.h"

void FMyCustomTestLaunchExtensionInstance::CustomizeUATCommandLine(FString& InOutCommandLine)
{
    if (bIsMyCustomTestEnabled)
    {
        // 将自定义参数附加到 UAT 命令行
        InOutCommandLine += TEXT(" -MyCustomTestFlag");
    }
}

void FMyCustomTestLaunchExtensionInstance::CustomizeTree(ProjectLauncher::FLaunchProfileTreeData& ProfileTreeData)
{
    // 在树中添加一个简单的复选框选项
    auto OnCheckChanged = [this](ECheckBoxState NewState)
    {
        bIsMyCustomTestEnabled = (NewState == ECheckBoxState::Checked);
    };
    auto IsChecked = [this]() -> ECheckBoxState
    {
        return bIsMyCustomTestEnabled ? ECheckBoxState::Checked : ECheckBoxState::Unchecked;
    };

    // 创建一个带有复选框的树节点
    ProfileTreeData.Tree->AddChildNode(
        ProjectLauncher::FLaunchProfileTreeNode::CreateLeaf(
            SNew(SHorizontalBox)
            + SHorizontalBox::Slot()
            .AutoWidth()
            [
                SNew(SCheckBox)
                .IsChecked_Lambda(IsChecked)
                .OnCheckStateChanged_Lambda(OnCheckChanged)
            ]
            + SHorizontalBox::Slot()
            .Padding(4, 0, 0, 0)
            .AutoWidth()
            [
                SNew(STextBlock)
                .Text(FText::FromString(TEXT("启用我的自定义测试")))
            ]
        )
    );
}

TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> FMyCustomTestLaunchExtension::CreateInstanceForProfile(ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs)
{
    return MakeShared<FMyCustomTestLaunchExtensionInstance>(InArgs);
}

const TCHAR* FMyCustomTestLaunchExtension::GetInternalName() const
{
    return TEXT("MyCustomTest");
}

FText FMyCustomTestLaunchExtension::GetDisplayName() const
{
    return FText::FromString(TEXT("我的自定义测试"));
}
```
*注意：此示例需在 Editor 模块的 `StartupModule` 中，通过 `ProjectLauncher::Get()` 注册 `FMyCustomTestLaunchExtension`。*

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ProjectLauncher` | 提供 Launcher 扩展点 (`FLaunchExtension`, `FLaunchProfileTreeData`) 的基础框架 |
| `DesktopPlatform` | (推测) 可能用于文件对话框（如 `ExportProfileGoScenarios` 功能） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `f2e0adf8` | Fixed AutomatedPerfTestTools plugin having the installed flag set to true | 修复了插件 `Installed` 标志错误为 true 的问题 |
| 2026-03-18 | `bb23bd67` | APT Launcher Extension Minor improvements and updates | 对 Launcher 扩展进行了小幅改进和更新 |
| 2026-02-06 | `600e17a2` | APT: Remove Editor and Engine dependencies from APT Launcher Extension | 移除对 Engine/Editor 的依赖，使扩展可在 Unreal Frontend 中独立运行 |

### 维护评价

这是一个非常新的插件（约 0 年），创建于 2026 年 2 月。从 git 历史看，它在创建后的几个月内持续有更新，包括一次重要的功能修复（Installed 标志）和一次改进。这表明该插件目前**处于活跃维护状态**。

其 `.uplugin` 标记为 `IsExperimentalVersion: true`，这意味着它仍处于**实验阶段**，API 和功能可能会发生变化。它专门为 Unreal Frontend (`SupportedPrograms: UnrealFrontend`) 设计，使用场景明确且受限，但对于其目标场景（CI/CD 中的自动化性能测试）来说，它是一个有价值的新工具。

**推荐程度**：如果你正在为 Unreal Frontend 构建自动化性能测试流程，可以尝试使用。但对于生产环境，需关注其“实验性”状态并做好应对未来变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTestTools)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTestTools/Tests) (路径基于典型结构推测，可能不存在或位置不同)
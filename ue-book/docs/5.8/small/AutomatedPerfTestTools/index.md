# AutomatedPerfTestTools

> Tools for Automated Perf Testing framework

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AutomatedPerfTestLaunchExtension` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-06 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTestTools) | |

## 用途

该插件是 **UnrealFrontend (UFE)** 的一个扩展，用于在项目启动器（Project Launcher）中集成和配置自动化性能测试。它解决了在 UFE 中配置各种性能测试场景（如序列、回放、ProfileGo、静态相机、材质测试）的复杂性问题，为测试人员提供了一个统一的图形化界面来设置和管理这些测试的参数，最终生成正确的 UAT 命令行参数。

## 使用场景

- 你是 QA 工程师或性能优化团队成员，需要在 UnrealFrontend 中配置和运行一系列标准化的性能测试。
- 你需要测试游戏在不同场景（如特定序列、回放文件、ProfileGo 路径）下的帧率、内存等性能指标。
- 你希望简化性能测试的启动配置流程，避免手动编写复杂的 UAT 命令行。

## 蓝图用法

此插件为编辑器扩展，不提供蓝图可调用的函数或属性。

## C++ 用法

此插件主要通过继承和扩展 `ProjectLauncher` 模块的接口来工作。

### 头文件引入

```cpp
#include "AutomatedPerfTestLaunchExtension.h"
```

### 基本用法

该插件的核心是 `FAutomatedPerfTestLaunchExtension` 类，它负责创建扩展实例并注册到项目启动器。

```cpp
// 来自 Source/AutomatedPerfTestLaunchExtension/Private/AutomatedPerfTestLaunchExtension.h
// 这是插件提供的扩展类，通常不需要直接使用，而是由模块在启动时自动注册。
class FAutomatedPerfTestLaunchExtension : public ProjectLauncher::FAutomatedTestLaunchExtension
{
public:
    // 为每个启动配置文件创建扩展实例
    virtual TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> CreateInstanceForProfile(ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs) override;
    // 返回内部名称
    virtual const TCHAR* GetInternalName() const override;
    // 返回显示名称
    virtual FText GetDisplayName() const override;
    // 定义在扩展菜单中的条目
    virtual void GetExtensionsMenuEntry(FExtensionsMenuEntry& MenuEntry) const override;
};
```

### 进阶用法

扩展实例 `FAutomatedPerfTestLaunchExtensionInstance` 包含了所有测试类型的配置逻辑。它通过 `CustomizeTree` 方法向启动配置文件的 UI 树中添加控件，并通过 `CustomizeUATCommandLine` 方法将配置转换为 UAT 命令行参数。

```cpp
// 来自 Source/AutomatedPerfTestLaunchExtension/Private/AutomatedPerfTestLaunchExtension.h
// 这是每个启动配置文件对应的扩展实例，管理具体的测试配置。
class FAutomatedPerfTestLaunchExtensionInstance : public ProjectLauncher::FAutomatedTestLaunchExtensionInstance
{
public:
    // 当属性发生变化时调用
    virtual void OnPropertyChanged() override;
    // 当添加一个新的自动化测试时调用
    virtual void OnTestAdded(ILauncherProfileAutomatedTestRef AutomatedTest) override;
    // 自定义启动配置文件的 UI 树
    virtual void CustomizeTree(ProjectLauncher::FLaunchProfileTreeData& ProfileTreeData) override;
    // 自定义最终生成的 UAT 命令行
    virtual void CustomizeUATCommandLine(FString& InOutCommandLine) override;

private:
    // 根据当前选择的测试类型，向UI树节点添加对应的选项
    void AddTestNodeOptions(ProjectLauncher::FLaunchProfileTreeNode& TreeNode);
    // ... 其他针对特定测试类型的添加方法 (AddSequenceTestNodeOptions, AddReplayTestNodeOptions 等)
};
```

## Demo 示例

以下示例展示了如何创建一个自定义的启动扩展，其结构与 `AutomatedPerfTestTools` 插件类似。

**MyCustomLaunchExtension.h**
```cpp
#pragma once

#include "Extension/AutomatedTestLaunchExtension.h"
#include "Model/ProjectLauncherModel.h"

class FMyCustomLaunchExtensionInstance : public ProjectLauncher::FAutomatedTestLaunchExtensionInstance
{
public:
    using Super = ProjectLauncher::FAutomatedTestLaunchExtensionInstance;
    FMyCustomLaunchExtensionInstance(FArgs& InArgs) : Super(InArgs) {}

    virtual void CustomizeTree(ProjectLauncher::FLaunchProfileTreeData& ProfileTreeData) override
    {
        // 在这里向 ProfileTreeData 添加自定义的 UI 控件
        // 例如，添加一个复选框来启用/禁用你的自定义测试
    }

    virtual void CustomizeUATCommandLine(FString& InOutCommandLine) override
    {
        // 在这里根据 UI 控件的状态，向 InOutCommandLine 追加参数
        // 例如: InOutCommandLine += TEXT(" -MyCustomTestFlag");
    }
};

class FMyCustomLaunchExtension : public ProjectLauncher::FAutomatedTestLaunchExtension
{
public:
    virtual TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> CreateInstanceForProfile(ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs) override
    {
        return MakeShared<FMyCustomLaunchExtensionInstance>(InArgs);
    }

    virtual const TCHAR* GetInternalName() const override { return TEXT("MyCustomExtension"); }
    virtual FText GetDisplayName() const override { return NSLOCTEXT("MyCustom", "DisplayName", "My Custom Test"); }
    virtual void GetExtensionsMenuEntry(FExtensionsMenuEntry& MenuEntry) const override
    {
        MenuEntry.Name = GetInternalName();
        MenuEntry.DisplayName = GetDisplayName();
    }
};
```

**MyCustomLaunchExtensionModule.cpp** (模块启动部分)
```cpp
#include "Modules/ModuleManager.h"
#include "ProjectLauncherModule.h"
#include "MyCustomLaunchExtension.h"

class FMyCustomLaunchExtensionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        if (FModuleManager::Get().IsModuleLoaded(TEXT("ProjectLauncher")))
        {
            IProjectLauncherModule& ProjectLauncherModule = FModuleManager::GetModuleChecked<IProjectLauncherModule>(TEXT("ProjectLauncher"));
            // 注册你的自定义扩展
            ProjectLauncherModule.RegisterLaunchExtension(MakeShared<FMyCustomLaunchExtension>());
        }
    }

    virtual void ShutdownModule() override
    {
        // 可选：在模块关闭时注销扩展
    }
};

IMPLEMENT_MODULE(FMyCustomLaunchExtensionModule, MyCustomLaunchExtension);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ProjectLauncher` | 提供项目启动器的框架、UI 树模型和扩展接口，是本插件的核心依赖。 |

## 维护状态

### 近期更新

- 2026-03-18 `bb23bd67` APT Launcher Extension Minor improvements and updates
- 2026-02-06 `600e17a2` APT: Remove Editor and Engine dependencies from APT Launcher Extension

### 维护评价

该插件创建于 **2026年2月**，是一个非常新的插件。从最近的提交记录看，它在创建后一个月内就有后续的改进和优化（移除不必要的依赖），表明其处于**活跃开发**阶段。由于其标记为 `IsExperimentalVersion=true`，说明 Epic 可能还在对其进行功能验证和接口调整，不建议在生产环境中作为稳定依赖使用，但非常适合用于内部测试和工具链开发。推荐关注其后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTestTools)
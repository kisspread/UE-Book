# Automated Perf Test Tools

> Tools for Automated Perf Testing framework

| 属性 | 值 |
|---|---|
| 中文名 | 自动化性能测试工具 |
| 分类 | Testing |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AutomatedPerfTestLaunchExtension` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2026-02-06 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTestTools) | |

## 用途

此插件的核心功能是将“自动化性能测试（Automated Perf Testing， APT）框架”的**启动配置与扩展**功能，从主引擎和编辑器依赖中解耦出来。它允许测试人员在独立的 **Unreal Frontend (UFE)** 程序中配置和启动各种自动化性能测试（如序列测试、回放测试、静态摄像机测试等），而无需加载整个编辑器。

简而言之，它解决了“如何在不依赖编辑器的情况下，通过专用工具（UFE）配置和启动复杂的自动化性能测试”这一问题。

## 使用场景

- 你是一个QA或性能测试工程师，需要使用 Unreal Frontend 工具来批量、自动化地运行针对特定场景（如 Lyra 示例项目）的性能测试。
- 你需要配置不同的测试类型（如回放、序列、ProfileGo 等）及其特定参数（如 LLM 跟踪、GPU 性能分析），并希望通过 UI 界面管理这些配置，而不是手动编辑命令行。
- 你的测试流程需要与 Epic 的 `ProjectLauncher` 框架集成，以便利用其构建、部署和启动能力。

## 蓝图用法

此插件不包含任何蓝图接口。所有功能都通过 C++ 实现，并集成到 Unreal Frontend 的 `ProjectLauncher` 用户界面中。

## C++ 用法

此插件的核心是提供 `ProjectLauncher` 框架的扩展实例，用于自定义性能测试的配置界面和命令行参数。

### 头文件引入

```cpp
#include "AutomatedPerfTestLaunchExtensionModule.h" // 模块接口
// 核心功能头文件为 Private，通常不直接包含。使用者应通过模块获取扩展实例。
```

### 基本用法

该插件通过模块自动注册扩展，无需用户手动创建实例。其核心逻辑体现在 `FAutomatedPerfTestLaunchExtensionInstance` 类中。以下是从源码中提取的关键方法及其作用：

```cpp
// 来自 Source/AutomatedPerfTestLaunchExtension/Private/AutomatedPerfTestLaunchExtension.h

// 1. 当添加一个新的自动化测试配置时被调用
virtual void OnTestAdded(ILauncherProfileAutomatedTestRef AutomatedTest) override;

// 2. 用于自定义“项目启动器”中的配置树（UI 部分）
virtual void CustomizeTree(ProjectLauncher::FLaunchProfileTreeData& ProfileTreeData) override;

// 3. 用于向 UAT（Unreal Automation Tool）命令行追加性能测试特有的参数
virtual void CustomizeUATCommandLine(FString& InOutCommandLine) override;
```

**关键枚举类型**用于区分不同的测试模式：

```cpp
enum class EAutomatedPerfTestType : uint8
{
    Sequence,   // 序列测试
    Replay,     // 回放测试
    ProfileGo,  // ProfileGo 测试
    StaticCamera, // 静态摄像机测试
    Material,     // 材质测试
    MAX
};
```

### 进阶用法

插件支持通过 `.ini` 配置文件（而非 Developer Settings UObject）来配置详细的测试选项。`GetConfigSection` 和 `ExportProfileGoScenarios` 等私有方法表明，它可以从配置文件中读取设置，并能导出 ProfileGo 的场景数据。

`GetTestTypeCallbacks` 模板函数是一个设计亮点，它利用 Lambda 表达式根据当前选择的测试类型动态生成 UI 元素的可见性和启用状态回调，实现了高效的 UI 状态管理。

## Demo 示例

由于此插件是 Editor 工具扩展，没有直接的运行时 API。一个典型的使用场景是在 UFE 中通过其自定义的 UI 来选择和配置测试，然后点击启动。其核心交互发生在 `ProjectLauncher` 的界面中。

若要以 C++ 方式扩展类似功能（例如创建一个新的测试类型），你需要创建一个继承自 `ProjectLauncher::FAutomatedTestLaunchExtension` 的类，并实现 `CreateInstanceForProfile` 等虚函数。可参考 `FAutomatedPerfTestLaunchExtension` 类的实现。

```cpp
// 假设要创建一个新的测试类型扩展（示例代码，非原插件代码）
// MyCustomPerfTestExtension.h
#pragma once

#include "ProjectLauncher/LaunchExtension.h"

class FMyCustomPerfTestLaunchExtensionInstance : public ProjectLauncher::FAutomatedTestLaunchExtensionInstance
{
public:
    using Super = ProjectLauncher::FAutomatedTestLaunchExtensionInstance;
    FMyCustomPerfTestLaunchExtensionInstance(FArgs& InArgs) : Super(InArgs) {}
    virtual ~FMyCustomPerfTestLaunchExtensionInstance() = default;

    // 实现界面自定义和命令行定制
    virtual void CustomizeTree(ProjectLauncher::FLaunchProfileTreeData& ProfileTreeData) override
    {
        // 在此添加自定义的UI树节点
    }
    virtual void CustomizeUATCommandLine(FString& InOutCommandLine) override
    {
        // 在此追加自定义的命令行参数
        InOutCommandLine += TEXT(" -MyCustomFlag");
    }
};

class FMyCustomPerfTestLaunchExtension : public ProjectLauncher::FAutomatedTestLaunchExtension
{
public:
    virtual TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> CreateInstanceForProfile(ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs) override
    {
        return MakeShared<FMyCustomPerfTestLaunchExtensionInstance>(InArgs);
    }
    virtual const TCHAR* GetInternalName() const override { return TEXT("MyCustomPerfTest"); }
    virtual FText GetDisplayName() const override { return NSLOCTEXT("MyCustom", "DisplayName", "My Custom Perf Test"); }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ProjectLauncher` | 提供启动配置框架、UI 扩展接口和基类 |
| `LauncherInterface` | 为启动器提供基础接口定义 |
| `UnrealFrontendProgram` (Program) | 插件被限定在 UnrealFrontend 程序中加载和运行 |

（注：依赖列表基于 `.uplugin` 中的 `Plugins` 配置和代码中的 `#include` 推断。）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `f2e0adf8` | Fixed AutomatedPerfTestTools plugin having the installed flag set to true | 修复插件 `Installed` 标志被错误设为 `true` 的问题 |
| 2026-03-18 | `bb23bd67` | APT Launcher Extension Minor improvements and updates | APT启动器扩展的小幅改进和更新 |
| 2026-02-06 | `600e17a2` | APT: Remove Editor and Engine dependencies from APT Launcher Extension | 从APT启动器扩展中移除编辑器和引擎依赖 |

### 维护评价

- **创建时间**：2026年2月创建，是一个非常新的插件（约1年）。
- **近期更新**：最近一次更新在2026年5月，修复了一个配置问题，表明插件仍在被使用和维护。
- **维护状态**：**活跃维护中**。作为性能测试工具链的一部分，预计会随着引擎版本和测试框架的迭代而持续更新。
- **已知限制**：此插件仅在 **Unreal Frontend** 程序中可用，不能在独立编辑器会话或运行时使用。它是实验性的（`IsExperimentalVersion: true`）。
- **推荐使用**：如果你需要在 Unreal Frontend 中进行自动化的性能测试配置，**推荐使用**此插件。它是 Epic 官方测试工具链的一部分，功能稳定且专门为此场景设计。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTestTools)
- 官方文档：未提供
- 测试用例：未在插件目录中发现测试文件
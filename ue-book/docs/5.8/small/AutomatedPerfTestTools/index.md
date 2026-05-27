# AutomatedPerfTestTools

> Tools for Automated Perf Testing framework

| 属性 | 值 |
|---|---|
| 中文名 | 自动性能测试启动器 |
| 分类 | Testing |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AutomatedPerfTestLaunchExtension` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-06 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTestTools) | |

## 用途

该插件是**自动化性能测试（APT）框架**的**启动器扩展**。它的核心目的是**将 APT 测试的配置和启动逻辑从 Unreal Editor 和引擎中剥离出来**，使其能够作为独立的模块，在 **UnrealFrontend（Unreal 编辑器工具）** 中运行。这样，测试团队可以配置并启动各种性能测试（如序列、重放、ProfileGo 等），而无需依赖完整的编辑器环境。

## 使用场景

- 你是测试工程师，需要在 **UnrealFrontend** 中为项目（如 Lyra）配置并批量运行自动化性能测试。
- 你希望测试配置（如 LLM、GPU 性能选项）能够从 `.ini` 配置文件中读取，而不是依赖编辑器中的设置对象。
- 你需要在不启动完整游戏或编辑器的情况下，通过启动器扩展来触发和管理性能测试会话。

## 蓝图用法

此插件主要面向 C++ 和编辑器工具开发，**没有直接暴露给蓝图的核心节点**。其功能主要通过在 UnrealFrontend 的启动器扩展界面中操作实现。

## C++ 用法

### 头文件引入

```cpp
#include "AutomatedPerfTestLaunchExtensionModule.h"
```

### 基本用法

此插件通常作为 `ProjectLauncher` 插件的一个扩展被加载和使用。它通过 `FAutomatedPerfTestLaunchExtension` 类注册到启动器系统。开发者主要关注如何实现或集成自己的测试扩展逻辑。

```cpp
// 引用自: Source/AutomatedPerfTestLaunchExtension/Private/AutomatedPerfTestLaunchExtension.h
// 自定义一个性能测试启动器扩展实例类
class FMyCustomTestLaunchExtensionInstance : public FAutomatedPerfTestLaunchExtensionInstance
{
public:
    FMyCustomTestLaunchExtensionInstance(FArgs& InArgs) : FAutomatedPerfTestLaunchExtensionInstance(InArgs) {}

    virtual void CustomizeUATCommandLine(FString& InOutCommandLine) override
    {
        // 根据当前测试类型，向 UAT 命令行追加自定义参数
        if (GetTestType() == EAutomatedPerfTestType::Sequence)
        {
            InOutCommandLine += TEXT(" -CustomSequenceFlag");
        }
    }

    // 重写其他虚函数以实现自定义逻辑...
};
```

### 进阶用法

了解插件定义的测试类型枚举和扩展点，可以用于创建更复杂的测试配置流程。

```cpp
// 引用自: Source/AutomatedPerfTestLaunchExtension/Private/AutomatedPerfTestLaunchExtension.h
// 测试类型枚举
enum class EAutomatedPerfTestType : uint8
{
    Sequence,   // 序列测试
    Replay,     // 重放测试
    ProfileGo,  // ProfileGo 场景测试
    StaticCamera, // 静态相机测试
    Material,   // 材质测试
    MAX
};

// 在扩展实例中，可以根据测试类型动态调整 UI 或命令行参数
void FAutomatedPerfTestLaunchExtensionInstance::CustomizeTree(ProjectLauncher::FLaunchProfileTreeData& ProfileTreeData)
{
    // 根据当前选择的测试类型，向树状控件添加不同的配置选项节点
    switch (GetTestType())
    {
    case EAutomatedPerfTestType::Sequence:
        AddSequenceTestNodeOptions(ProfileTreeData.GetRootNode());
        break;
    case EAutomatedPerfTestType::Replay:
        AddReplayTestNodeOptions(ProfileTreeData.GetRootNode());
        break;
    // ... 其他类型
    }
}
```

## Demo 示例

一个最小化的自定义性能测试扩展实现。

**MyCustomPerfTestExtension.h**
```cpp
#pragma once
#include "AutomatedPerfTestLaunchExtension.h" // 包含插件的主要头文件

class FMyCustomPerfTestExtension : public FAutomatedPerfTestLaunchExtension
{
public:
    virtual TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> CreateInstanceForProfile(
        ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs) override
    {
        // 创建我们自定义的扩展实例
        return MakeShareable(new FAutomatedPerfTestLaunchExtensionInstance(InArgs));
    }

    virtual const TCHAR* GetInternalName() const override
    {
        return TEXT("MyCustomPerfTest");
    }

    virtual FText GetDisplayName() const override
    {
        return NSLOCTEXT("MyCustomTest", "DisplayName", "My Custom Performance Test");
    }

    virtual void GetExtensionsMenuEntry(FExtensionsMenuEntry& MenuEntry) const override
    {
        MenuEntry.MenuPath = TEXT("Performance");
        MenuEntry.SortOrder = 100;
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ProjectLauncher` | 核心依赖，提供启动器扩展的基类和框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `f2e0adf8` | Fixed AutomatedPerfTestTools plugin having the installed flag set to true | 修复了插件“已安装”标志被错误设置为 true 的问题。 |
| 2026-03-18 | `bb23bd67` | APT Launcher Extension Minor improvements and updates | APT 启动器扩展的小改进和更新。 |
| 2026-02-06 | `600e17a2` | APT: Remove Editor and Engine dependencies from APT Launcher Extension | 将启动器扩展从主插件中分离，移除对编辑器和引擎的依赖，使其能在 UnrealFrontend 中运行。 |

### 维护评价

该插件**创建时间很新**（约 1 年），但**标记为实验性**。从提交记录看，创建后有过小规模的功能更新和 bug 修复，表明它仍处于**早期积极开发阶段**。最近一次提交（2026年5月）是一个配置修复，说明其基本框架已稳定，但功能集和 API 可能仍有变动。由于它是实验性的且专门服务于 UnrealFrontend 的测试工作流，**在确定的测试流程中可以谨慎使用**，但需关注其后续更新和可能的不兼容变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTestTools)
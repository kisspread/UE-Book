# AutomatedPerfTestTools

> Tools for Automated Perf Testing framework

| 属性 | 值 |
|---|---|
| 中文名 | 自动化性能测试工具 |
| 分类 | Testing |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器UI与配置） |
| 模块 | `AutomatedPerfTestLaunchExtension` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-06 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTestTools) | |

## 用途

此插件是**自动化性能测试框架**的一个组成部分，专为在 **Unreal Frontend (UFE)** 环境中运行而设计。它的核心作用是**扩展 Unreal Frontend 的“项目启动器”界面**，为用户提供一个统一的图形化配置界面，用于设置和启动各种类型的自动化性能测试（如序列测试、回放测试等）。它解决了将自动化测试工具与引擎/编辑器核心代码解耦的问题，使其能独立于编辑器运行，从而更轻量、更专注于测试流程配置。

## 使用场景

- 你是 QA 工程师或性能测试人员，需要在 **Unreal Frontend** 中批量、自动化地运行游戏或项目的性能测试，而无需打开完整的编辑器。
- 你需要为不同的测试场景（如 `Sequence` 序列测试、`Replay` 回放测试、`ProfileGo` 性能分析等）提供图形化的配置选项，例如设置 LLM（低层内存）追踪、GPU 性能分析等参数。
- 你希望将测试配置（如测试类型、特定参数）导出为配置文件，以便复用或集成到自动化流水线中。

## 蓝图用法

此插件未暴露蓝图节点。其主要功能通过编辑器（Unreal Frontend）的图形界面和 C++ 接口提供。

## C++ 用法

### 头文件引入

```cpp
#include "AutomatedPerfTestLaunchExtensionModule.h"
```

### 基本用法

此插件主要作为 Unreal Frontend 的扩展模块运行。在 C++ 层面，其模块接口遵循标准的 `IModuleInterface` 模式。

```cpp
// 模块启动和关闭由引擎自动管理，无需用户代码干预。
// 此插件的核心在于向 ProjectLauncher 系统注册一个扩展。
// 参考：AutomatedPerfTestLaunchExtensionModule.cpp
```

### 进阶用法

核心扩展逻辑在 `FAutomatedPerfTestLaunchExtensionInstance` 和 `FAutomatedPerfTestLaunchExtension` 类中。它们通过继承 `ProjectLauncher` 插件的基类来实现。开发者通常**不会直接实例化或使用这些类**，而是通过该插件提供的 UI 进行配置。其内部定义了测试类型枚举：

```cpp
// 测试类型定义 (来自 Private/AutomatedPerfTestLaunchExtension.h)
enum class EAutomatedPerfTestType : uint8
{
    Sequence,    // 序列测试
    Replay,      // 回放测试
    ProfileGo,   // 性能分析测试
    StaticCamera,// 静态摄像机测试
    Material,    // 材质测试
    MAX
};
```

插件通过 `GetProjectSettings` 和 `GetConfigSection` 从 `.ini` 配置文件读取特定测试类型的参数。

## Demo 示例

由于此插件是编辑器扩展，不提供可独立运行的最小示例。其使用方式体现在 Unreal Frontend 的界面操作中。核心的模块注册逻辑如下：

```cpp
// AutomatedPerfTestLaunchExtensionModule.h
class FAutomatedPerfTestLaunchExtensionModule : public IModuleInterface
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

private:
	// 存储注册的启动器扩展
	TArray<TSharedRef<ProjectLauncher::FLaunchExtension>> Extensions;
};

// .cpp 实现中，StartupModule 会创建并注册 FAutomatedPerfTestLaunchExtension 扩展。
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ProjectLauncher` | 提供基础的启动器扩展框架，本插件依赖并扩展其功能。 |
| `AutomationController` | 可能用于自动化测试的执行控制（隐式依赖）。 |
| `TargetPlatform` | 用于平台相关的性能测试配置。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `f2e0adf8` | Fixed AutomatedPerfTestTools plugin having the installed flag set to true | 修正插件默认安装标志为真，使其默认启用行为符合预期。 |
| 2026-03-18 | `bb23bd67` | APT Launcher Extension Minor improvements and updates | 对启动器扩展进行了细微改进和更新。 |
| 2026-02-06 | `600e17a2` | APT: Remove Editor and Engine dependencies from APT Launcher Extension | 将启动器扩展独立为插件，移除对编辑器和引擎的依赖，使其能在 Unreal Frontend 中运行。 |

### 维护评价

- **年龄**: 插件于2026年2月创建，非常年轻。
- **活动性**: 自创建以来有两次后续提交，最近一次在2026年5月，表明在积极开发和修正中。
- **状态**: 插件被标记为 `IsExperimentalVersion: true`，表明其处于实验阶段，API 和功能可能在未来发生变化。
- **推荐**: 作为**实验性插件**，推荐给希望在 Unreal Frontend 中使用标准化自动化性能测试框架的团队试用。由于其默认启用，可以开箱即用进行评估。需注意其可能存在的不稳定性和接口变更风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTestTools)
- 官方文档 (无)
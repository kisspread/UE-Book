# Automation Utilities

> Tools and Utilities for Automation purposes（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 自动化工具 |
| 分类 | Testing |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AutomationUtils` (Runtime), `AutomationUtilsEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-03-26 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AutomationUtils) | |

## 用途

这个插件为自动化测试提供辅助工具和函数库，其主要功能是简化和扩展虚幻引擎内置的自动化测试框架。它解决了两个核心问题：
1. 允许在非正式测试（`FTest`）运行的**游戏玩法过程中**捕获自动化截图。
2. 提供了一个**离线命令行工具（Commandlet）**，用于批量比较截图差异，从而实现跨平台截图捕获与后期图像比对的工作流。

它降低了编写复杂视觉回归测试的门槛，并支持更灵活的测试流程。

## 使用场景

- 你需要在游戏运行时（非编辑器PIE模式）捕获截图用于自动化回归测试 → 使用 `TakeAutomationScreenshot` 蓝图函数。
- 你在多个平台（如不同移动设备）运行游戏并截图，希望后期统一进行图像比较以验证UI或渲染一致性 → 使用 `ScreenshotComparisonCommandlet` 进行批量比对。
- 你正在构建自定义的自动化测试框架，并需要扩展屏幕截图相关的功能。

## 蓝图用法

根据提供的 `AutomationUtilsEditor` 模块文件，该模块主要提供编辑器及命令行功能，不直接包含蓝图可调用节点。蓝图功能位于 `AutomationUtils` (Runtime) 模块中（未在当前提供文件中列出）。根据首次提交信息，该Runtime模块应包含一个 `UBlueprintFunctionLibrary`，提供了核心的截图函数。

### 核心节点

*（基于插件初始功能描述推断）*
| 节点 | 说明 | 所在类 |
|---|---|---|
| `TakeAutomationScreenshot` | 在游戏运行时捕获一张用于自动化比较的截图，无需在正式的 `FTest` 环境中。 | `UAutomationUtilsBlueprintFunctionLibrary` (假设) |

### 使用示例（蓝图描述）

1.  在任意蓝图（例如角色蓝图或游戏模式蓝图）中，添加一个事件（如按键输入或游戏逻辑触发）。
2.  搜索并拖入 `TakeAutomationScreenshot` 节点。
3.  连接事件执行线到该节点的输入执行引脚。
4.  （可选）提供截图名称等参数。
5.  当游戏运行到该逻辑时，将自动保存一张截图到指定目录。

## C++ 用法

### 头文件引入

要使用 `AutomationUtilsEditor` 模块提供的功能，例如命令行工具，你需要在你的 `.cpp` 文件中包含相关头文件。

```cpp
// 包含命令行工具类定义
#include "ScreenshotComparisonCommandlet.h"
```

### 基本用法

该插件的核心C++用法体现在其提供的命令行工具 `ScreenshotComparisonCommandlet` 上，通常不直接在游戏代码中调用，而是通过引擎的命令行参数使用。

（基于类定义推断的调用方式）通过引擎可执行文件调用该Commandlet进行截图比较：
```bash
UnrealEditor-Cmd.exe -run=ScreenshotComparisonCommandlet -ComparisonDir="Path/To/ComparedImages" -BaseDir="Path/To/BaseImages"
```

### 进阶用法

结合其初始提交描述，一个典型的自动化测试流程是：
1.  在目标平台客户端（如Android设备）运行游戏，通过蓝图或C++调用 `TakeAutomationScreenshot` 函数捕获截图。
2.  将不同平台/构建版本捕获的截图文件收集到指定目录。
3.  使用 `ScreenshotComparisonCommandlet` 对这些截图目录进行批量差异分析，生成测试报告。

## Demo 示例

```cpp
// ExampleAutomationCommandlet.h
#pragma once
#include "Commandlets/Commandlet.h"
#include "ExampleAutomationCommandlet.generated.h"

UCLASS()
class UExampleAutomationCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    virtual int32 Main(const FString& Params) override;
};
```

```cpp
// ExampleAutomationCommandlet.cpp
#include "ExampleAutomationCommandlet.h"
#include "ScreenshotComparisonCommandlet.h" // 引用AutomationUtilsEditor提供的类

int32 UExampleAutomationCommandlet::Main(const FString& Params)
{
    UE_LOG(LogTemp, Log, TEXT("Running Example Automation Commandlet..."));
    
    // 示例：此处可以调用其他自动化逻辑
    // 注意：ScreenshotComparisonCommandlet 本身是独立的，这里仅为演示模块引用
    
    UE_LOG(LogTemp, Log, TEXT("Automation process finished."));
    return 0;
}
```

## 模块依赖

`AutomationUtilsEditor` 模块的构建配置（Build.cs）未在提供的文件内容中完全展示。但根据其功能（提供Commandlet）和编辑器模块的常规依赖，它很可能依赖于以下模块：

| 模块 | 用途 |
|---|---|
| `AutomationUtils` | 引用运行时模块提供的蓝图函数库等基础功能 |
| `AutomationController` 或 `AutomationTest` | 与引擎核心自动化测试框架集成 |
| `ImageCore`, `ImageWrapper` | 用于图像文件的读取、处理和比较（截图比对功能核心） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `ec6539e3` | Add FinishAllAssetCompilation to fix material instance test crash | 修复材质实例测试崩溃问题，添加资产编译完成等待函数 |
| 2026-05-12 | `52ac5ba2` | Add support for registering an automation mount point to the AutomationUtils BPFL. This allows thing | 为自动化工具蓝图函数库添加挂载点注册支持，扩展测试环境配置能力 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移至UE_LOGF，可能是日志系统更新 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 解决动态链接库导出符号问题，确保跨模块调用 |
| 2024-11-25 | `af0eb101` | Removed pure virtual requirement for scene extension methods to reduce noise when searching for vali | 移除场景扩展方法的纯虚函数要求，降低代码干扰 |

### 维护评价

- **创建时间**: 2019年，属于较老的插件。
- **近期活跃度**: **非常活跃**。从2024年底到2026年5月有多次实质性更新，涉及功能新增（挂载点）、崩溃修复和代码质量改进。
- **实验状态**: 插件在 `.uplugin` 中明确标记为 `IsBetaVersion: true`，表明它仍处于实验阶段，API和行为可能发生变更。
- **推荐度**: 对于需要**扩展自动化截图功能**和**进行离线图像比对**的测试场景，该插件仍然是官方提供的有效工具。由于其持续维护，可以谨慎使用。但需注意其“实验性”标签，并在关键项目中做好备份和版本管理。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AutomationUtils)
- [官方文档]() （无）
- [测试用例]() （未在提供路径中找到）
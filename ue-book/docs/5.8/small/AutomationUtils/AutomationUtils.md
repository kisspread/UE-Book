# Automation Utilities

> Tools and Utilities for Automation purposes

| 属性 | 值 |
|---|---|
| 中文名 | 自动化工具 |
| 分类 | Testing |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AutomationUtils` (Runtime), `AutomationUtilsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-03-26 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AutomationUtils) | |

## 用途

该插件旨在为游戏玩法自动化测试提供核心工具。它主要解决两个问题：
1.  **自动化截图对比**：允许在正常游戏运行期间（而非严格的自动化测试会话中）捕获屏幕截图，并将其与基准图像进行比较。这对于持续集成（CI）中的视觉回归测试至关重要。
2.  **简化测试环境准备**：通过提供管理虚拟文件系统挂载点的函数，简化了测试期间对资产路径的管理，避免了硬编码路径带来的维护问题。同时，它提供了确保资产（如材质）完全编译完毕的同步函数，防止因异步编译导致的测试崩溃。

## 使用场景

-   你的游戏需要在每次提交后进行自动化视觉回归测试，以检查UI、场景渲染或角色外观是否意外改变。
-   你在编写测试用例时，需要为测试资产创建一个临时的、隔离的目录结构，避免与项目资产混淆。
-   你的测试需要在删除某些资产前，确保其相关的着色器编译任务已全部完成，以避免引擎崩溃。

## 蓝图用法

所有函数均通过 `UAutomationUtilsBlueprintLibrary` 暴露，在蓝图中以静态节点形式调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Take Gameplay Automation Screenshot` | 捕获当前游戏画面截图，用于后续的自动化对比。可设置误差容限。 | `UAutomationUtilsBlueprintLibrary` |
| `Add Automation Mount Point` | 注册一个虚拟文件系统挂载点，指向引擎的自动化临时目录。 | `UAutomationUtilsBlueprintLibrary` |
| `Remove Automation Mount Point` | 注销一个由 `Add Automation Mount Point` 创建的虚拟挂载点。 | `UAutomationUtilsBlueprintLibrary` |
| `Finish All Asset Compilation` | 阻塞游戏线程，直到所有进行中的资产（如材质）编译任务完成。 | `UAutomationUtilsBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **自动化截图**：在一个游戏逻辑的`Event Tick`或特定事件中，连接一个`Take Gameplay Automation Screenshot`节点。`ScreenshotName`参数指定保存的文件名（不含后缀）。
2.  **管理测试资源路径**：
    *   在测试开始时，调用`Add Automation Mount Point`，默认挂载到`/Automation/`。之后在代码中就可以使用`/Automation/MyAsset`这样的路径来访问`FPaths::AutomationTransientDir()`下的实际文件。
    *   在测试结束时，调用`Remove Automation Mount Point`进行清理。
3.  **安全删除测试资产**：在测试的清理（Teardown）阶段，调用`Finish All Asset Compilation`节点，等待所有资源编译完成，然后再执行删除测试中创建的资产（如临时材质）的操作，避免引擎崩溃。

## C++ 用法

### 头文件引入

```cpp
#include "AutomationUtilsBlueprintLibrary.h"
```

### 基本用法

在 C++ 中，这些函数同样作为静态函数直接调用。

```cpp
// 在游戏逻辑或测试代码中截屏
UAutomationUtilsBlueprintLibrary::TakeGameplayAutomationScreenshot(TEXT("MainMenuState"));

// 设置虚拟挂载点
UAutomationUtilsBlueprintLibrary::AddAutomationMountPoint(TEXT("/TestAssets/"));

// 现在可以使用 "/TestAssets/SomeFile" 的路径
// ...

// 测试结束后移除挂载点
UAutomationUtilsBlueprintLibrary::RemoveAutomationMountPoint(TEXT("/TestAssets/"));
```

### 进阶用法

在自定义的自动化测试或命令中组合使用这些功能，构建完整的测试流程。

```cpp
void FMyAutomationTest::RunTest()
{
    // 1. 准备测试环境：创建虚拟目录
    const FString MountPoint = TEXT("/AutomationTest/");
    UAutomationUtilsBlueprintLibrary::AddAutomationMountPoint(MountPoint);

    // 2. 执行需要测试的游戏逻辑或UI操作
    // ... (例如：加载一个UI，点击一个按钮)

    // 3. 捕获截图，用于后续比较
    const FString ScreenshotName = FString::Printf(TEXT("TestStep_%s"), *FDateTime::Now().ToString());
    UAutomationUtilsBlueprintLibrary::TakeGameplayAutomationScreenshot(ScreenshotName);

    // 4. 清理：等待所有资源操作完成，然后移除挂载点
    UAutomationUtilsBlueprintLibrary::FinishAllAssetCompilation();
    UAutomationUtilsBlueprintLibrary::RemoveAutomationMountPoint(MountPoint);
}
```
*示例来源：基于 `AutomationUtilsBlueprintLibrary.h` 中的函数接口推断。*

## Demo 示例

以下是一个最小的 C++ 示例，展示如何在一个自定义的编辑器命令中调用这些工具函数。

```cpp
// MyAutomationCommand.h
#pragma once

#include "CoreMinimal.h"

class FMyAutomationCommand
{
public:
    static void Execute();
};
```

```cpp
// MyAutomationCommand.cpp
#include "MyAutomationCommand.h"
#include "AutomationUtilsBlueprintLibrary.h"

void FMyAutomationCommand::Execute()
{
    // 设置一个临时的虚拟目录用于本次测试
    UAutomationUtilsBlueprintLibrary::AddAutomationMountPoint();

    // 模拟一些操作...
    UE_LOG(LogTemp, Log, TEXT("正在执行自动化测试..."));

    // 执行屏幕截图
    UAutomationUtilsBlueprintLibrary::TakeGameplayAutomationScreenshot(TEXT("DemoCapture"));

    // 确保所有资源编译完成（如果测试涉及创建资源）
    UAutomationUtilsBlueprintLibrary::FinishAllAssetCompilation();

    // 清理虚拟目录
    UAutomationUtilsBlueprintLibrary::RemoveAutomationMountPoint();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AutomationUtils` | 提供核心的 Runtime 自动化工具函数。 |
| `AutomationUtilsEditor` | (可能) 提供仅在编辑器中可用的自动化工具扩展。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `ec6539e3` | Add FinishAllAssetCompilation to fix material instance test crash | 新增`FinishAllAssetCompilation`函数，修复材质实例测试中的崩溃问题。 |
| 2026-05-12 | `52ac5ba2` | Add support for registering an automation mount point to the AutomationUtils BPFL. This allows thing | 为自动化工具蓝图函数库添加了虚拟挂载点注册功能，方便管理测试资源路径。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG日志调用迁移到新的UE_LOGF宏。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 为所有方法和静态变量添加了正确的DLL导出标记。 |
| 2024-11-25 | `af0eb101` | Removed pure virtual requirement for scene extension methods to reduce noise when searching for vali | 移除场景扩展方法的纯虚函数要求，减少代码搜索噪音。 |

### 维护评价

-   **状态**：**活跃维护中**。尽管插件被标记为实验性且自2019年创建，但近期（2025-2026年）有连续的实质性功能更新和问题修复。
-   **建议**：**推荐在需要游戏玩法自动化截图或复杂测试环境搭建的场景中使用**。该插件解决了自动化测试中的常见痛点，且仍在积极迭代。注意其“实验性”标签，意味着API未来可能发生变化。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AutomationUtils)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Editor/AutomationUtils) (推断路径，可能存在)
# GPU Reshape Plugin

> GPU Reshape editor integration

| 属性 | 值 |
|---|---|
| 中文名 | GPU调试工具 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GPUReshape` (DeveloperTool) |
| 实验性 | 否 |
| 创建时间 | 2025-05-19 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/GPUReshape) | |

## 用途

GPUReshape 插件为 Unreal Engine 编辑器集成了 GPU Reshape 调试/分析应用程序。它解决的核心问题是：**为开发者提供一种在编辑器内一键启动并自动附加 GPU Reshape 工具的工作流**，从而简化 GPU 性能分析和调试过程。

此插件并非一个纯运行时或渲染插件，而是一个开发者工具，负责管理外部 GPU Reshape 应用的生命周期、进程注入和工作区附加。它抽象了查找安装器、注入当前进程并缓存认证令牌的复杂步骤，使开发者能专注于使用工具进行 GPU 调试。

## 使用场景

- 你正在开发一个对 GPU 性能要求较高的项目，需要使用外部的 GPU Reshape 工具来分析着色器执行、资源使用或捕获帧时，可通过编辑器中的按钮一键启动并附加调试器。
- 你希望将 GPU Reshape 集成到你的开发管线中，并希望通过编辑器命令或按钮方便地访问它。

## 蓝图用法

该插件未暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 的蓝图 API。其功能主要通过**编辑器 UI 按钮**和**控制台命令**提供。

### 核心控制台命令

| 命令 | 说明 | 执行方式 |
|---|---|---|
| `GPUReshape.OpenApp` | 启动或切换到 GPU Reshape 应用程序 | 在编辑器控制台输入 |

### 使用示例（编辑器操作）

1.  在 Unreal Editor 的工具栏或菜单栏中，找到由插件添加的“GPU Reshape”按钮（样式类似 PIX/RD 的按钮）。
2.  点击该按钮，将自动执行 `OpenOrSwitchToApp` 操作。
3.  如果 GPU Reshape 应用未运行，插件会查找并启动它，然后自动将当前工作区附加到正在运行的 UE 编辑器进程。
4.  如果应用已在运行，点击按钮会将焦点切换到该应用窗口。

## C++ 用法

### 头文件引入

```cpp
#include "GPUReshapeModule.h"
```

### 基本用法

通过模块接口访问插件的核心功能。以下示例展示了如何检查插件状态并启动应用。

```cpp
// 来源: 基于 Source/GPUReshape/Private/GPUReshapeModule.h 的 API 推断
void ExampleUsage()
{
    // 获取模块实例
    FGPUReshapeModule* GPUReshapeModule = FModuleManager::GetModulePtr<FGPUReshapeModule>(TEXT("GPUReshape"));
    if (GPUReshapeModule && GPUReshapeModule->IsInitialized())
    {
        // 插件已初始化，尝试打开或切换到 GPU Reshape 应用
        GPUReshapeModule->OpenOrSwitchToApp();
        
        // 获取已启动应用的进程 ID (用于后续调试或日志记录)
        uint32 AppPID = GPUReshapeModule->GetAppGetProcessID();
        UE_LOG(LogGPUReshape, Log, TEXT("GPU Reshape process ID: %u"), AppPID);
    }
}
```

### 进阶用法

更精细地控制应用窗口的切换。

```cpp
void FocusGPUReshapeWindow()
{
    if (FGPUReshapeModule* Module = FModuleManager::GetModulePtr<FGPUReshapeModule>(TEXT("GPUReshape")))
    {
        // 仅当应用已经打开时才尝试切换，避免意外启动
        if (Module->GetAppGetProcessID() != 0)
        {
            Module->SwitchToApp();
        }
        else
        {
            UE_LOG(LogGPUReshape, Warning, TEXT("GPU Reshape app is not currently running."));
        }
    }
}
```

## Demo 示例

一个最小的示例，展示如何从其他模块调用 GPUReshape 的功能。

**MyClass.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyClass
{
public:
    void LaunchGPUDebugTool();
};
```

**MyClass.cpp**
```cpp
#include "MyClass.h"
#include "GPUReshapeModule.h"

void FMyClass::LaunchGPUDebugTool()
{
    // 安全地获取模块并调用
    if (FGPUReshapeModule* GPUReshapeModule = FModuleManager::GetModulePtr<FGPUReshapeModule>(TEXT("GPUReshape")))
    {
        GPUReshapeModule->OpenOrSwitchToApp();
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("GPUReshape module is not loaded."));
    }
}
```

## 模块依赖

你的模块需要链接 `GPUReshape` 模块才能使用其 C++ API。此外，由于插件包含编辑器扩展，它隐含依赖了以下模块（仅需在插件或编辑器模块内使用）：

| 模块 | 用途 |
|---|---|
| `Slate`, `SlateCore` | 构建编辑器工具栏按钮和UI |
| `EditorStyle` | 获取编辑器默认样式集，用于按钮图标等 |

**使用说明**：若你仅通过编辑器按钮或控制台命令使用此插件，则无需在你的 Build.cs 中添加任何依赖。若需在 C++ 中直接调用 `FGPUReshapeModule`，则需在你模块的 `Build.cs` 中添加 `GPUReshape` 到 `PublicDependencyModuleNames`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-03-09 | `5d05ec9a` | GPU Reshape [addressing feedback], automatically set symbol and source paths | 根据反馈改进，自动设置符号和源代码路径。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了错误的查找替换后的第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了某个更改。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复引擎初始化委托注册问题。 |

### 维护评价

- **活跃维护**：插件创建于 2025 年 5 月，距今约 1 年。从提交历史看，在 2026 年初仍有积极的更新和 bug 修复，表明处于活跃开发阶段。
- **实验性/平台限制**：目前仅支持 Win64 平台，且作为开发者工具默认启用，这限制了其应用场景。
- **推荐使用**：**推荐**。对于需要在 Windows 平台上进行 GPU 深度性能分析和调试的开发者，此插件提供了高效的集成方案。其维护状态良好，功能明确。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/GPUReshape)
- [官方文档]() （暂无）
- [测试用例]() （未在提供的信息中发现标准测试用例文件）
# GPU Reshape Plugin

> GPU Reshape editor integration

| 属性 | 值 |
|---|---|
| 中文名 | GPU Reshape 编辑器集成 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GPUReshape` (DeveloperTool) |
| 实验性 | 否 |
| 创建时间 | 2025-05-19 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/GPUReshape) | |

## 用途

GPUReshape 插件是一个**开发者工具**，用于在虚幻编辑器中集成外部 GPU 调试与性能分析工具 "GPU Reshape"。它的核心作用是：
1. **自动启动和管理 GPU Reshape 应用程序**：插件会在本地环境中自动寻找、安装并启动 GPU Reshape 的进程。
2. **提供编辑器内一键访问**：为开发者提供一个类似 PIX/RD 的编辑器按钮，可以快速打开 GPU Reshape 应用程序。
3. **自动附加工作空间**：启动 GPU Reshape 后，自动将当前编辑器工程作为工作空间附加，省去手动配置的步骤。

它解决了开发者在进行 GPU 性能分析、调试和优化时，需要频繁切换窗口和手动配置工具环境的繁琐流程问题。

## 使用场景

- 你在开发一个图形密集型游戏，需要频繁使用 GPU 分析工具（如 PIX、RenderDoc）来检查渲染性能和调试着色器。
- 你希望在虚幻编辑器内部就能一键启动 GPU 调试工具，并自动关联当前项目，提高工作效率。
- 你正在 Windows 平台上进行开发，因为此插件仅支持 Win64。

## 蓝图用法

此插件作为开发者工具，主要通过编辑器界面和 C++ API 提供功能。源码中没有暴露任何 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 接口，因此**不适用于蓝图编程**。其功能通过编辑器工具栏按钮和控制台命令触发。

### 编辑器集成

插件会在编辑器中添加一个工具栏按钮（类似 PIX 或 RenderDoc 的图标）。点击该按钮会执行 `OpenOrSwitchToApp` 逻辑：
1. 如果 GPU Reshape 应用程序尚未启动，则启动它。
2. 如果已启动，则将焦点切换到该应用程序窗口。

## C++ 用法

### 头文件引入

```cpp
#include "GPUReshapeModule.h"
```

### 基本用法

该插件的模块 `FGPUReshapeModule` 暴露了几个关键函数，可用于以编程方式控制 GPU Reshape 应用程序。

```cpp
// 获取 GPUReshape 模块实例
FGPUReshapeModule& GPUReshapeModule = FModuleManager::GetModuleChecked<FGPUReshapeModule>(TEXT("GPUReshape"));

// 检查模块是否已正确初始化（即是否成功找到并安装了加载器）
if (GPUReshapeModule.IsInitialized())
{
    // 打开或切换到 GPU Reshape 应用程序窗口
    GPUReshapeModule.OpenOrSwitchToApp();

    // 获取已启动的 GPU Reshape 应用程序的进程 ID (PID)
    uint32 ProcessID = GPUReshapeModule.GetAppGetProcessID();
    UE_LOG(LogGPUReshape, Log, TEXT("GPU Reshape App PID: %u"), ProcessID);
}
else
{
    UE_LOG(LogGPUReshape, Warning, TEXT("GPU Reshape backend is not initialized. Cannot launch app."));
}
```
*来源：基于 `GPUReshapeModule.h` 中的公共接口设计。*

### 进阶用法

该插件还注册了控制台命令，可以在编辑器的控制台窗口中直接调用：

```bash
# 控制台命令
gpureshape.open
```
此命令会触发与点击编辑器按钮相同的逻辑。这在自动化测试或脚本中可能有用。

## Demo 示例

此插件是一个编辑器扩展，本身不提供运行时组件。以下是一个示例，展示如何在你的自定义编辑器工具中，使用 GPUReshape 模块来检查其状态并触发操作。

**MyCustomTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyCustomEditorTool
{
public:
    void CheckGPUReshapeStatus();
    void LaunchGPUReshapeForCurrentProject();
};
```

**MyCustomTool.cpp**
```cpp
#include "MyCustomTool.h"
#include "GPUReshapeModule.h"

void FMyCustomEditorTool::CheckGPUReshapeStatus()
{
    if (FModuleManager::Get().IsModuleLoaded(TEXT("GPUReshape")))
    {
        FGPUReshapeModule& Module = FModuleManager::GetModuleChecked<FGPUReshapeModule>(TEXT("GPUReshape"));
        bool bReady = Module.IsInitialized();
        UE_LOG(LogTemp, Log, TEXT("GPU Reshape Plugin Initialized: %s"), bReady ? TEXT("Yes") : TEXT("No"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("GPU Reshape Plugin is not loaded."));
    }
}

void FMyCustomEditorTool::LaunchGPUReshapeForCurrentProject()
{
    if (FModuleManager::Get().IsModuleLoaded(TEXT("GPUReshape")))
    {
        FGPUReshapeModule& Module = FModuleManager::GetModuleChecked<FGPUReshapeModule>(TEXT("GPUReshape"));
        if (Module.IsInitialized())
        {
            // 调用模块函数来打开或切换应用
            Module.OpenOrSwitchToApp();
            UE_LOG(LogTemp, Log, TEXT("Requested to open or switch to GPU Reshape."));
        }
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。作为 `DeveloperTool` 类型的模块，它主要依赖引擎核心模块来实现编辑器集成。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到 `UE_LOGF` 格式，可能是为了遵循新的日志标准。 |
| 2026-03-09 | `5d05ec9a` | GPU Reshape [addressing feedback], automatically set symbol and source paths | 根据反馈改进，自动设置符号和源代码路径，简化用户配置。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了错误的“查找与替换”操作后的第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了某个提交（CL51314860）。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist... | 修复引擎初始化委托注册问题，将 `FCoreDelegates::OnPostEngineInit` 改为通过 `GetOnPostEngineInit()` 方法获取，以解决缺失注册的问题。 |

### 维护评价

- **活跃维护**：创建时间（2025年5月）至今不足两年，最近几个月有持续的功能更新和问题修复（如2026年2月和3月的多次提交）。
- **状态**：从更新日志看，插件正在根据用户反馈进行改进（如自动设置路径），并修复底层引擎兼容性问题。这表明它仍在积极维护中。
- **推荐度**：**推荐使用**，特别是对于需要在 Windows 平台频繁使用 GPU 调试工具的开发者。它是一个能有效提升工作流效率的工具插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/GPUReshape)
- 官方文档：无
- 测试用例：无（插件目录下未发现测试文件）
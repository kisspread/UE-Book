# LiveCodingToolset

> Live Coding compile toolset.

| 属性 | 值 |
|---|---|
| 中文名 | 实时编码编译工具集 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveCodingToolset` (Editor), `LiveCodingToolsetTests` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 -1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/LiveCodingToolset) | |

## 用途

此插件将用于**AI代理（AI Agent）**的“实时编码（Live Coding）”编译功能，从其他模块（如 `UAF`）迁移到了一个独立的引擎插件中。它通过一个工具集子系统，将 `CompileLiveCoding` 函数暴露为 `AICallable`（即可供 AI 调用的）蓝图函数，使得外部 AI 工具（如 MCP）能够以编程方式触发热重载编译，并获取编译输出与结果状态。其主要目的是为高级自动化或 AI 驱动的开发工作流提供标准化的编译接口。

## 使用场景

- 你正在开发或集成基于 AI 的自动化构建流水线，需要让 AI 能够安全地触发和监控 C++ 代码的实时编译。
- 你需要一个独立的、可控的接口来执行 Live Coding 编译，以便集成到自定义的编辑器工具或菜单中。

## 模块列表

- **LiveCodingToolset**: 核心运行时模块，包含工具集定义、编译功能实现及子系统管理。
- **LiveCodingToolsetTests**: 编辑器测试模块，验证子系统的注册和核心编译函数的可用性。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CompileLiveCoding` | 调用实时编码编译并返回执行结果与日志。 | `ULiveCodingToolset` |

### 使用示例（蓝图描述）

在蓝图中，你可以通过 `ULiveCodingToolsetSubsystem` 获取该工具集的实例，然后调用 `CompileLiveCoding` 节点。节点执行后，返回一个结构体，包含是否成功、是否有错误以及详细的输出日志字符串。

## C++ 用法

### 头文件引入

```cpp
#include "LiveCodingToolsetSubsystem.h"
```

### 基本用法

```cpp
// 获取编辑器子系统实例
ULiveCodingToolsetSubsystem* Subsystem = GEditor->GetEditorSubsystem<ULiveCodingToolsetSubsystem>();
if (Subsystem && Subsystem->IsToolAvailable())
{
    // 调用编译函数
    FLiveCodingResult Result = Subsystem->CompileLiveCoding();
    
    if (Result.bSuccess)
    {
        UE_LOG(LogLiveCodingToolset, Log, TEXT("编译成功: %s"), *Result.Output);
    }
    else
    {
        UE_LOG(LogLiveCodingToolset, Error, TEXT("编译失败: %s"), *Result.Output);
    }
}
```

## Demo 示例

以下示例展示了一个最小化的编辑器模块，用于通过子系统触发一次 Live Coding 编译。

**MyToolModule.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyToolModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void TriggerLiveCodingCompile();
};
```

**MyToolModule.cpp**
```cpp
#include "MyToolModule.h"
#include "LiveCodingToolsetSubsystem.h"
#include "Toolkits/AssetEditorManager.h" // 用于演示

#define LOCTEXT_NAMESPACE "FMyToolModule"

void FMyToolModule::StartupModule()
{
    // 此处可绑定菜单或快捷键触发 TriggerLiveCodingCompile
}

void FMyToolModule::ShutdownModule()
{
}

void FMyToolModule::TriggerLiveCodingCompile()
{
    if (ULiveCodingToolsetSubsystem* Subsystem = GEditor->GetEditorSubsystem<ULiveCodingToolsetSubsystem>())
    {
        if (Subsystem->IsToolAvailable())
        {
            FLiveCodingResult Result = Subsystem->CompileLiveCoding();
            // 使用结果，例如显示通知
            FNotificationInfo Info(Result.bSuccess ? LOCTEXT("CompileSuccess", "Live Coding 成功") : LOCTEXT("CompileFail", "Live Coding 失败"));
            Info.SubText = FText::FromString(Result.Output.Left(200)); // 显示部分输出
            FSlateNotificationManager::Get().AddNotification(Info);
        }
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyToolModule, MyToolModule)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveCoding` | 提供底层的实时编译（Live Coding）功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `0d1e3ace` | [LiveCodingToolset] Move the *Live Coding* *MCP* tool into a dedicated Engine plugin... | 初始创建插件，将实时编码的MCP工具独立为新插件，暴露AICallable编译函数并添加测试。 |

### 维护评价

- **实验性**：插件标记为 `IsExperimentalVersion` 且 `EnabledByDefault` 为 false，属于实验阶段功能。
- **活跃状态**：插件于 2026 年 4 月创建，目前仅有初始提交。属于全新插件，未来活跃度有待观察。
- **使用建议**：适用于希望尝试或集成 AI 驱动编译工作流的开发者。由于是实验性功能，生产环境使用需谨慎，需关注后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/LiveCodingToolset)
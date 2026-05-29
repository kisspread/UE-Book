# Command Link Server

> Listens to and runs console commands from CmdLink

| 属性 | 值 |
|---|---|
| 中文名 | 命令链接服务 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `CmdLinkServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-06-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/CmdLinkServer) | |

## 用途

CmdLinkServer 是一个**Windows 命名管道（Named Pipe）服务器**，用于监听来自外部工具 `CmdLink.exe` 的连接，接收字符串形式的控制台命令并在 UE 进程中执行，然后将执行结果回传。

它解决的核心问题是：**让外部进程能够实时控制运行中的 Unreal Engine 实例**。与 HTTP 远程控制不同，命名管道提供低延迟的本地 IPC 通道，适合需要在同一台机器上对 UE 进程进行自动化操作的场景（如 QA 自动化测试、构建流水线控制、远程调试等）。

插件通过 `BeginAsyncCommand` / `EndAsyncCommand` 机制支持异步命令——当某个命令需要跨帧执行时，可以标记为异步状态，防止 CmdLink 在命令完成前断开连接。

## 使用场景

- 你在做自动化 QA 测试，需要从测试脚本向运行中的编辑器发送控制台命令
- 你在 CI/CD 流水线中需要通过 `CmdLink.exe` 驱动 UE 编辑器执行批量操作
- 你需要从外部工具实时查询或控制 UE 进程状态，且要求低延迟的本地通信
- 你在开发跨进程的自定义工具链，需要向 UE 注入命令并获取执行结果

## 蓝图用法

此插件**不暴露任何蓝图接口**。所有 API 均为 C++ 模块级接口，供其他 C++ 模块或通过控制台命令间接使用。外部交互通过 `CmdLink.exe` 命令行工具完成，不经过蓝图系统。

## C++ 用法

### 头文件引入

```cpp
#include "CmdLinkServer.h"
```

### 基本用法

获取模块实例并控制其启用/禁用状态：

```cpp
// 获取 CmdLinkServer 模块单例
FCmdLinkServerModule* CmdLink = FCmdLinkServerModule::Get();
if (CmdLink)
{
    // 启用管道监听
    CmdLink->Enable();

    // 禁用管道监听
    CmdLink->Disable();

    // 当安全密钥变更时更新（用于连接认证）
    CmdLink->OnKeyChanged(TEXT("NewSecurityKey"));
}
```

### 进阶用法：异步命令支持

当你实现一个需要跨帧完成的自定义控制台命令时，需要使用异步命令机制来通知 CmdLinkServer 等待命令完成：

```cpp
// 在一个自定义控制台命令的处理函数中
void UMySubsystem::HandleLongRunningCommand(const TArray<FString>& Params)
{
    FCmdLinkServerModule* CmdLink = FCmdLinkServerModule::Get();
    if (!CmdLink) return;

    // 标记异步命令开始，CmdLink 管道将等待此命令完成
    CmdLink->BeginAsyncCommand(TEXT("MyLongCommand"), Params);

    // 启动异步操作（如加载资产、网络请求等）
    DoSomethingAsync([CmdLink, Params]()
    {
        // 异步操作完成后通知 CmdLinkServer
        CmdLink->EndAsyncCommand(TEXT("MyLongCommand"), Params);
    });
}
```

> **注意**：`BeginAsyncCommand` 会让 CmdLink 服务端在该命令执行期间保持连接不断开，直到对应的 `EndAsyncCommand` 被调用。如果不使用异步命令机制，命令返回后 CmdLink 会立即关闭连接。

## Demo 示例

以下示例展示如何在你自己的模块中与 CmdLinkServer 交互：

### MyTool.h

```cpp
// Copyright My Company. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

class FMyToolModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OnCmdLinkReady();
};
```

### MyTool.cpp

```cpp
// Copyright My Company. All Rights Reserved.

#include "MyToolModule.h"
#include "CmdLinkServer.h"

void FMyToolModule::StartupModule()
{
    // 确保 CmdLinkServer 已加载并启用
    FCmdLinkServerModule* CmdLink = FCmdLinkServerModule::Get();
    if (CmdLink)
    {
        CmdLink->Enable();
        UE_LOG(LogTemp, Log, TEXT("CmdLinkServer is active and listening."));
    }
}

void FMyToolModule::ShutdownModule()
{
    // 无需特殊清理，CmdLinkServer 会自行管理管道生命周期
}
```

### Build.cs

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "CmdLinkServer"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine 等） | 插件内部使用 `Windows/WindowsPlatformNamedPipe.h`，属于平台层 API |

> **平台限制**：此插件依赖 Windows 命名管道 API（`FPlatformNamedPipe`），仅在 **Windows** 平台可用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue f | 修复 nodiscard 返回值被忽略的编译警告 |
| 2025-05-29 | `1a832d69` | Move the StringOutputDevice into a separate header. | 将 StringOutputDevice 提取到独立头文件 |
| 2023-09-21 | `bd8e4ec4` | [BugFix] Silenced noisy error in CmdLinkServer plugin | 修复插件中烦人的错误日志输出 |
| 2023-09-15 | `0ca75e7c` | Disable cmdlink on build machines unless -cmdlink is passed on the command line to avoid conflicts o | 构建机器上默认禁用 cmdlink，需通过 -cmdlink 参数显式启用 |

### 维护评价

CmdLinkServer 是一个功能单一、代码量极小（仅 2 个源文件）的工具型插件，自 2023 年创建以来处于**低频维护**状态。近期更新主要是编译警告修复和日志系统迁移等基础设施调整，无功能性变更。

- ✅ 持续有编译兼容性修复，说明未被废弃
- ✅ 默认启用，Epic 内部仍在使用
- ⚠️ 仅支持 Windows 平台（依赖命名管道 API）
- ⚠️ 无公开测试用例，无蓝图接口
- 代码成熟稳定，适合作为 IPC 通道使用，但功能边界明确，不建议超出其设计用途使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/CmdLinkServer)
- 官方文档：无
- 测试用例：未找到公开测试用例
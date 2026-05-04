# Command Link Server

> Listens to and runs console commands from CmdLink

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | 是 |
| 包含内容 | 否 |
| 模块 | CmdLinkServer (Editor) |
| 创建时间 | 2023-06-30 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/CmdLinkServer) | |

## 用途

CmdLinkServer 是一个 **仅限 Windows** 的编辑器插件，通过 Windows Named Pipe（命名管道）监听来自外部工具 **CmdLink.exe** 的连接。当 CmdLink.exe 连接后，可以通过管道发送控制台命令（console command），插件会在编辑器中执行这些命令并将结果返回。

简单来说：它让外部程序能够远程向 UE Editor 发送并执行控制台命令。

核心机制：
- 使用 `FPlatformNamedPipe` 创建 Named Pipe `\\.\pipe\UnrealEngine-CLI`（可通过 key 自定义）
- 内部用 `FTickStateMachine` 状态机驱动异步 I/O：连接 → 读取 → 执行 → 回复 → 循环
- 命令通过 `IConsoleCommandExecutor` 的 Modular Feature 执行，支持引擎内置命令和 Python 命令
- 连接断开后自动重连（5 秒延迟）
- 构建机器（`GIsBuildMachine`）上默认禁用，避免管道名称冲突

## 使用场景

- **自动化流水线**：CI/CD 中通过 CmdLink.exe 向运行中的 Editor 发送命令（如加载关卡、截图、运行测试）
- **外部工具集成**：自定义的批处理工具或 IDE 插件需要与 UE Editor 交互
- **远程调试**：通过命令行远程查询编辑器状态或触发操作

## 控制台变量

插件注册了两个控制台变量来控制运行时行为：

| CVar | 类型 | 说明 |
|---|---|---|
| `console.CmdLink.enable` | bool | 启用/禁用管道监听。启动时可通过 `-cmdlink` 命令行参数强制启用 |
| `console.CmdLink.key` | string | 设置管道名称后缀。默认 `None` 时管道名为 `UnrealEngine-CLI`，设为 `Foo` 则变为 `UnrealEngine-CLI-Foo` |

### 启用方式

**方式一**：命令行参数（推荐用于自动化场景）

```
UnrealEditor.exe MyProject.uproject -cmdlink
```

**方式二**：运行时控制台命令

```
console.CmdLink.enable 1
console.CmdLink.key MyBuildMachine
```

## 蓝图用法

本插件没有暴露任何蓝图节点。它完全通过 Named Pipe 和控制台变量交互，不适用于蓝图工作流。

## C++ 用法

### 头文件引入

```cpp
#include "CmdLinkServer.h"
```

### 基本用法：获取模块实例

```cpp
// 获取模块单例
FCmdLinkServerModule* Server = FCmdLinkServerModule::Get();
if (Server)
{
    Server->Enable();   // 启动管道监听
    Server->Disable();  // 停止管道监听
}
```

### 进阶用法：异步命令

如果执行的命令需要跨多帧完成（如加载大关卡、批量操作），需要使用异步命令 API 让 CmdLinkServer 等待完成后再回复客户端：

```cpp
#include "CmdLinkServer.h"

// 在命令开始时调用，CmdLinkServer 会等待 EndAsyncCommand 再回复
FCmdLinkServerModule* Server = FCmdLinkServerModule::Get();
Server->BeginAsyncCommand(TEXT("MyLongCommand"), {TEXT("arg1"), TEXT("arg2")});

// ... 跨帧执行逻辑 ...

// 命令完成后调用
Server->EndAsyncCommand(TEXT("MyLongCommand"), {TEXT("arg1"), TEXT("arg2")});
```

`BeginAsyncCommand` 和 `EndAsyncCommand` 的 CommandName 和 Params 必须与管道收到的命令完全匹配，否则调用会被忽略。这确保了只有真正对应的异步命令才能解除等待状态。

源码中通过 `UE::CmdLink::GBeginAsyncCommand` / `UE::CmdLink::GEndAsyncCommand` 全局函数指针将这两个 API 暴露给 UnrealEd 模块（见 `extern UNREALED_API` 声明）。

## 管道通信协议

了解协议有助于编写自己的 CmdLink 客户端或调试工具：

**客户端 → 服务器（请求）**：
1. `int32`: 参数数量 `ArgC`
2. 重复 `ArgC` 次：
   - `int32`: 字符串长度（含 null 终止符）
   - `char[长度]`: 参数字符串

**服务器 → 客户端（响应）**：
1. `int32`: 响应字符串长度（含 null 终止符）
2. `char[长度]`: 响应内容

`ArgV[0]` 是文件路径，`ArgV[1]` 是命令名，`ArgV[2+]` 是命令参数。它们会被拼接成一条空格分隔的命令字符串交给 `IConsoleCommandExecutor` 执行。

## 模块依赖

从 Build.cs 的 `PublicDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心基础模块 |

私有依赖（使用者不需要额外引用）：`CoreUObject`, `Engine`, `UnrealEd`

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 | 解读 |
|---|---|---|---|
| 2025-09-12 | `ce6ff39` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue for FTSTicker::RemoveTicker usage. | 修复编译警告：`FTSTicker::RemoveTicker` 返回值被标记为 `[[nodiscard]]` 后的适配 |
| 2025-05-29 | `1a832d6` | Move the StringOutputDevice into a separate header. | 重构：将 `FStringOutputDevice` 移到独立头文件，非功能性改动 |
| 2023-09-21 | `bd8e4ec` | [BugFix] Silenced noisy error in CmdLinkServer plugin | 修复：消除管道断连时的冗余错误日志 |

### 维护评价

- 创建于 2023-06-30，约 2.8 年历史，🆕 标签
- 功能稳定，近期更新均为编译适配和小幅重构，无重大功能变更
- 仅限 Win64，使用 Windows Named Pipe API，跨平台不可用
- 作为 Epic 内部工具链的一部分（配合 CmdLink.exe），持续维护但更新频率低
- **推荐使用**：如果你的自动化流程需要从外部向 UE Editor 发送命令，这是官方推荐的方式

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/CmdLinkServer)
- [CmdLinkServer.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/CmdLinkServer/Source/CmdLinkServer/Public/CmdLinkServer.h)
- [CmdLinkServer.cpp](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/CmdLinkServer/Source/CmdLinkServer/Private/CmdLinkServer.cpp)

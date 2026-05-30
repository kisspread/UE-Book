# MsQuic Runtime Plugin

> Runtime plugin for the MsQuic library.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MsQuic 运行时模块 |
| 分类 | Runtime |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MsQuicRuntime` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2023-05-10 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MsQuic) | |

## 用途

本插件的核心功能是提供一个统一的运行时入口，用于在支持的程序中加载 MsQuic 的动态链接库（DLL 或 .so）。它本身不实现任何 QUIC 协议逻辑，而是作为 MsQuic 库的运行时加载器，确保 MsQuic 二进制文件能够被正确加载到进程内存中。其他依赖 MsQuic 进行网络通信的插件（例如用于多用户编辑的插件）可以依赖此模块，而无需各自实现复杂的库加载逻辑。

## 使用场景

- 你需要在 UnrealFrontend、UnrealMultiUserServer 或 CrashReportClientEditor 等编辑器或服务器程序中使用基于 MsQuic 的网络功能。
- 你正在开发一个自定义的、基于 QUIC 协议的 Unreal 程序，并且需要一个标准化的方式来加载 MsQuic 运行时。
- **注意**：此插件**不适用于**常规的游戏（Game）项目，它仅被限制用于特定的编辑器程序和工具（参见 `SupportedPrograms`）。

## 蓝图用法

本插件**没有提供任何蓝图接口**。源码中未发现任何 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 标记。其所有功能均通过 C++ 模块接口提供。

## C++ 用法

### 头文件引入

```cpp
#include "MsQuicRuntimeModule.h"
```

### 基本用法

从 `MsQuicRuntimeModule.h` 头文件可知，本模块的核心是提供一个静态函数 `InitRuntime`，用于加载 MsQuic 库。在依赖此模块的插件启动时，应调用此函数。

```cpp
// 在你自己的模块（例如 MultiUserServer 模块）的启动过程中调用
void FMyMultiUserModule::StartupModule()
{
    // 尝试初始化 MsQuic 运行时环境
    if (!FMsQuicRuntimeModule::InitRuntime())
    {
        UE_LOG(LogMyModule, Error, TEXT("Failed to initialize MsQuic runtime. Multi-user features may be unavailable."));
        return;
    }

    // ... 继续初始化依赖 MsQuic 的网络逻辑
}
```
*来源：根据 `MsQuicRuntimeModule.h` 中 `InitRuntime` 函数的声明推断用法。*

### 进阶用法

插件内部根据目标平台加载特定的库文件。以 `LoadMsQuicDll` 函数为例，它展示了平台相关的加载逻辑：

```cpp
// 以下为简化示意，展示了插件内部如何根据平台加载库
bool FMsQuicRuntimeModule::LoadMsQuicDll()
{
    FString LibraryPath;
    // 根据平台构建库文件路径，例如：Binaries/ThirdParty/MsQuic/v220/Win64/msquic.dll
    // ... 路径构建代码 ...

    MsQuicLibraryHandle = FPlatformProcess::GetDllHandle(*LibraryPath);
    if (!MsQuicLibraryHandle)
    {
        UE_LOG(LogMsQuicRuntime, Error, TEXT("Failed to load MsQuic library from: %s"), *LibraryPath);
        return false;
    }
    return true;
}
```
*来源：`MsQuicRuntimeModule.h` 中 `LoadMsQuicDll` 函数的声明和 `MSQUIC_BINARIES_PATH` 常量定义。*

## Demo 示例

以下是一个最小示例，演示如何创建一个依赖 MsQuicRuntime 的自定义运行时模块。

**MyQuicModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyQuicModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    bool bMsQuicInitialized = false;
};
```

**MyQuicModule.cpp**
```cpp
#include "MyQuicModule.h"
#include "MsQuicRuntimeModule.h" // 包含 MsQuic 运行时模块头文件

void FMyQuicModule::StartupModule()
{
    // 在模块启动时初始化 MsQuic 运行时
    bMsQuicInitialized = FMsQuicRuntimeModule::InitRuntime();
    if (!bMsQuicInitialized)
    {
        UE_LOG(LogTemp, Warning, TEXT("MsQuic runtime failed to initialize."));
    }
}

void FMyQuicModule::ShutdownModule()
{
    // MsQuic 运行时会在其自身模块关闭时自动清理（FreeMsQuicDll），
    // 因此此处通常无需额外操作。
    bMsQuicInitialized = false;
}

IMPLEMENT_MODULE(FMyQuicModule, MyQuic)
```

## 模块依赖

根据 `MsQuicRuntime.Build.cs` 文件分析，该模块仅依赖引擎的核心模块，无特殊依赖。

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，属于代码风格统一调整。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 为所有方法和静态变量添加 `DLLexport`/`DLLimport` 宏，以支持动态库导出，改进跨模块兼容性。 |
| 2023-05-16 | `e2056a61` | [MsQuic] Fixing MsQuic linux build and runtime load of .so | 修复了在 Linux 平台上 MsQuic 的构建和运行时加载 .so 文件的问题。 |
| 2023-05-12 | `d463abe6` | [MsQuic] Restructuring MsQuicRuntime module to have a static InitRuntime function | 重构 MsQuicRuntime 模块，将库加载逻辑封装成静态的 `InitRuntime` 函数，简化调用方式。 |
| 2023-05-10 | `65e6543e` | [MsQuic] Adding MsQuic plugin with MsQuicRuntime module | 创建 MsQuic 插件及 MsQuicRuntime 模块，实现基础的 MsQuic 库加载功能。 |

### 维护评价

- **创建时间**：插件创建于 2023 年 5 月，相对年轻。
- **更新频率**：最近一次实质性功能相关更新（添加 DLL 导出宏）发生在 2025 年 4 月，之后为风格调整。插件核心功能（加载 MsQuic 库）自 2023 年 5 月后未发生变化，表明其功能已稳定。
- **活跃状态**：处于**维护中**状态，偶有编译或兼容性修复，但无新功能开发。
- **已知限制**：
    1. 仅支持特定的编辑器/服务器程序，**不能用于游戏（Game）目标**。
    2. 依赖于特定版本 (`v220`) 的 MsQuic 二进制文件，这些文件需要预先放置在项目的 `Binaries/ThirdParty/MsQuic/` 目录下。
- **推荐使用**：如果你正在为支持的程序（如 MultiUserServer）开发依赖 MsQuic 的功能，推荐使用此模块作为标准加载入口。对于自定义项目，需确保目标平台和程序符合限制条件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MsQuic)
- [官方文档]()（无）
- [测试用例]()（无）
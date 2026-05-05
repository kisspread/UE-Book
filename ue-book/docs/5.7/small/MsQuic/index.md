# MsQuic Runtime Plugin

> Runtime plugin for the MsQuic library.

| 属性 | 值 |
|---|---|
| 分类 | Runtime |
| 默认启用 | ✅ 是 |
| 包含内容 | 否 |
| 模块 | MsQuicRuntime (Runtime, LoadingPhase: PreDefault) |
| 创建时间 | 2023-05-10 |
| 年龄标签 | 🆕 (~3年) |
| 支持平台 | Win64, Linux, Mac |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MsQuic) | |

## 用途

MsQuic Runtime Plugin 是 UE5 对 [Microsoft MsQuic](https://github.com/microsoft/msquic) 库的运行时封装。MsQuic 实现了基于 UDP 的 QUIC 协议，提供快速、加密的网络通信能力。

这个 plugin 本身**非常薄**——它只有一个模块 `MsQuicRuntime`，做的事情就是一件事：**在 PreDefault 阶段加载 MsQuic 的平台原生动态库**（DLL / .so / .dylib）。它不直接提供任何 QUIC 网络功能，而是作为底层依赖，让 UE5 的其他组件（如 SwitchboardListener、UnrealBuildAccelerator）能够使用 MsQuic C API。

核心架构关系：

```
你的程序
  ├── MsQuicRuntime Plugin    ← 加载 DLL，确保 MsQuic 可用
  │     └── MsQuic (ThirdParty)  ← 提供 msquic.h 头文件和链接库
  └── 你的 QUIC 网络代码       ← 直接调用 MsQuic C API (MsQuicOpen2, etc.)
```

### 为什么需要这个 Plugin？

MsQuic 的原生库（msquic.dll / libmsquic.so.2）以预编译二进制形式存放在 `Engine/Binaries/ThirdParty/MsQuic/v220/` 目录下。由于 MsQuic 使用 C API 并通过函数指针表（`QUIC_API_TABLE`）调用，运行时必须先加载 DLL 才能使用。MsQuicRuntime Plugin 就是负责这个加载过程的桥梁。

## 使用场景

- **Switchboard Listener**：UE5 的多用户编辑系统通过 QUIC 协议进行安全通信，依赖此 plugin 加载 MsQuic
- **Unreal Build Accelerator (UBA)**：构建加速工具使用 QUIC 作为网络传输后端
- **自定义 QUIC 网络应用**：你需要在 UE5 程序中使用 QUIC 协议进行低延迟、加密的 UDP 网络通信
- **虚拟制片 / nDisplay**：Switchboard 工具通过 QUIC 与远程设备通信

## 蓝图用法

此 plugin **没有暴露任何蓝图接口**。它是一个纯 C++ 运行时模块，仅提供 DLL 加载功能。所有 QUIC 相关操作都需要通过 C++ 直接调用 MsQuic C API。

## C++ 用法

### 头文件引入

```cpp
#include "MsQuicRuntimeModule.h"   // MsQuicRuntime Plugin 的模块头文件
#include "msquic.h"                 // MsQuic C API（来自 ThirdParty/MsQuic 模块）
```

### 基本用法：初始化 MsQuic 运行时

在使用任何 MsQuic API 之前，必须先调用 `InitRuntime()` 加载 DLL。

```cpp
#include "MsQuicRuntimeModule.h"

bool bSuccess = FMsQuicRuntimeModule::InitRuntime();
if (!bSuccess)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to initialize MsQuic runtime"));
    return;
}

// MsQuic DLL 已加载，现在可以使用 MsQuic C API
```

> 来源：`Engine/Source/Programs/SwitchboardListener/SblCore/Private/SwitchboardMainCommon.cpp:213`

`InitRuntime()` 内部会根据平台自动选择正确的动态库：
- Windows: `Engine/Binaries/ThirdParty/MsQuic/v220/win64/msquic.dll`
- Linux: `Engine/Binaries/ThirdParty/MsQuic/v220/linux/libmsquic.so.2`
- macOS: `Engine/Binaries/ThirdParty/MsQuic/v220/macos/libmsquic.dylib`

调用多次是安全的——如果 DLL 已加载，会直接返回 `true`。

### 进阶用法：完整的 QUIC 服务端

以下示例展示如何使用 MsQuic C API 创建一个完整的 QUIC 监听服务，代码来自 SwitchboardListener 的实际实现模式。

```cpp
#include "MsQuicRuntimeModule.h"
#include "msquic.h"

// 1. 初始化运行时（加载 DLL）
FMsQuicRuntimeModule::InitRuntime();

// 2. 打开 MsQuic API 表
const QUIC_API_TABLE* QuicApi = nullptr;
QUIC_STATUS Status = MsQuicOpen2(&QuicApi);
if (QUIC_FAILED(Status))
{
    UE_LOG(LogTemp, Error, TEXT("MsQuicOpen2 failed"));
    return;
}

// 3. 创建 Registration（应用级注册）
const QUIC_REGISTRATION_CONFIG RegConfig = {
    "my-app", QUIC_EXECUTION_PROFILE_LOW_LATENCY
};
HQUIC QuicRegistration = nullptr;
Status = QuicApi->RegistrationOpen(&RegConfig, &QuicRegistration);

// 4. 配置 TLS 证书
QUIC_CERTIFICATE_FILE CertFile = {};
CertFile.PrivateKeyFile = "/path/to/key.pem";
CertFile.CertificateFile = "/path/to/cert.pem";

QUIC_CREDENTIAL_CONFIG CredConfig = {};
CredConfig.Type = QUIC_CREDENTIAL_TYPE_CERTIFICATE_FILE;
CredConfig.CertificateFile = &CertFile;

// 5. 配置 QUIC 设置
QUIC_SETTINGS Settings = {};
Settings.IdleTimeoutMs = 30000;
Settings.IsSet.IdleTimeoutMs = 1;
Settings.PeerBidiStreamCount = 1;
Settings.IsSet.PeerBidiStreamCount = 1;

// 6. 创建 Configuration（ALPN 协商）
const char AlpnStr[] = "my-protocol";
const QUIC_BUFFER Alpn = { sizeof(AlpnStr) - 1, (uint8_t*)AlpnStr };
HQUIC QuicConfiguration = nullptr;
Status = QuicApi->ConfigurationOpen(
    QuicRegistration, &Alpn, 1,
    &Settings, sizeof(Settings), nullptr, &QuicConfiguration);

// 7. 加载证书凭证
Status = QuicApi->ConfigurationLoadCredential(QuicConfiguration, &CredConfig);

// 8. 定义回调函数
auto ListenerCallback = [](
    HQUIC Listener, void* Context, QUIC_LISTENER_EVENT* Event) -> QUIC_STATUS
{
    switch (Event->Type)
    {
    case QUIC_LISTENER_EVENT_NEW_CONNECTION:
        // 处理新连接...
        return QUIC_STATUS_SUCCESS;
    default:
        break;
    }
    return QUIC_STATUS_NOT_SUPPORTED;
};

// 9. 打开并启动 Listener
HQUIC QuicListener = nullptr;
Status = QuicApi->ListenerOpen(
    QuicRegistration, ListenerCallback, nullptr, &QuicListener);

QUIC_ADDR Addr = {};
QuicAddrSetFamily(&Addr, QUIC_ADDRESS_FAMILY_INET);
QuicAddrSetPort(&Addr, 4433);
Status = QuicApi->ListenerStart(QuicListener, &Alpn, 1, &Addr);

// ... 使用完毕后清理 ...
QuicApi->ListenerClose(QuicListener);
QuicApi->ConfigurationClose(QuicConfiguration);
QuicApi->RegistrationClose(QuicRegistration);
MsQuicClose(QuicApi);
```

> 来源：`Engine/Source/Programs/SwitchboardListener/SblCore/Private/SwitchboardListener.cpp:482-576`

### 流（Stream）发送与接收

```cpp
// 发送数据到流
QUIC_BUFFER SendBuffer;
SendBuffer.Buffer = (uint8_t*)DataPtr;
SendBuffer.Length = DataSize;
QuicApi->StreamSend(Stream, &SendBuffer, 1, QUIC_SEND_FLAG_NONE, Context);

// 启用流接收
QuicApi->StreamReceiveSetEnabled(Stream, true);
```

> 来源：`Engine/Source/Programs/SwitchboardListener/SblCore/Private/SwitchboardListener.cpp:2881,629`

## Demo 示例

### 最小 MsQuic 初始化示例

```cpp
// MyQuicGameSubsystem.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "msquic.h"
#include "MyQuicGameSubsystem.generated.h"

UCLASS()
class UMyQuicGameSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    bool IsQuicAvailable() const { return QuicApi != nullptr; }

private:
    const QUIC_API_TABLE* QuicApi = nullptr;
    HQUIC QuicRegistration = nullptr;
};
```

```cpp
// MyQuicGameSubsystem.cpp
#include "MyQuicGameSubsystem.h"
#include "MsQuicRuntimeModule.h"

void UMyQuicGameSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 1. 加载 MsQuic DLL
    if (!FMsQuicRuntimeModule::InitRuntime())
    {
        UE_LOG(LogTemp, Error, TEXT("MsQuic DLL not available"));
        return;
    }

    // 2. 打开 MsQuic
    if (QUIC_FAILED(MsQuicOpen2(&QuicApi)))
    {
        UE_LOG(LogTemp, Error, TEXT("MsQuicOpen2 failed"));
        QuicApi = nullptr;
        return;
    }

    // 3. 创建 Registration
    const QUIC_REGISTRATION_CONFIG RegConfig = {
        "my-ue5-app", QUIC_EXECUTION_PROFILE_LOW_LATENCY
    };
    if (QUIC_FAILED(QuicApi->RegistrationOpen(&RegConfig, &QuicRegistration)))
    {
        UE_LOG(LogTemp, Error, TEXT("RegistrationOpen failed"));
        MsQuicClose(QuicApi);
        QuicApi = nullptr;
        return;
    }

    UE_LOG(LogTemp, Display, TEXT("MsQuic initialized successfully"));
}

void UMyQuicGameSubsystem::Deinitialize()
{
    if (QuicApi)
    {
        if (QuicRegistration)
        {
            QuicApi->RegistrationClose(QuicRegistration);
            QuicRegistration = nullptr;
        }
        MsQuicClose(QuicApi);
        QuicApi = nullptr;
    }

    Super::Deinitialize();
}
```

**Build.cs 依赖配置**（在你的模块 `.Build.cs` 中）：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "MsQuicRuntime",   // 运行时 DLL 加载
    "MsQuic"           // MsQuic C API 头文件和链接库
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE5 核心模块 |
| `MsQuic` | ThirdParty 外部模块，提供 msquic.h 头文件和平台原生链接库（msquic.lib / libmsquic.so） |

### 使用此 Plugin 时你的模块需要依赖

| 模块 | 用途 |
|---|---|
| `MsQuicRuntime` | 调用 `FMsQuicRuntimeModule::InitRuntime()` 加载 DLL |
| `MsQuic` | 使用 MsQuic C API（`msquic.h`、`MsQuicOpen2()` 等） |

### 平台宏定义

MsQuic ThirdParty 模块在链接时自动定义以下宏：

| 宏 | 平台 | 用途 |
|---|---|---|
| `MSQUIC_WIN=1` | Windows | 标识 Windows 平台 |
| `MSQUIC_LINUX=1` | Linux | 标识 Linux 平台 |
| `MSQUIC_POSIX=1` | Linux / macOS | 标识 POSIX 兼容平台 |

### 支持的目标程序

此 Plugin 仅对以下 UE 程序启用（非通用游戏运行时）：

| 程序 | 用途 |
|---|---|
| `UnrealFrontend` | UE 前端工具（编辑器相关） |
| `UnrealMultiUserServer` | 多用户编辑服务器 |
| `UnrealMultiUserSlateServer` | 多用户 Slate 服务器 |
| `CrashReportClientEditor` | 崩溃报告客户端 |
| `CoopMultiUserServer` | 协作多用户服务器 |

> **注意**：这意味着此 Plugin 默认**不会**在独立游戏构建中加载。如果你的游戏需要 QUIC 功能，需要自行处理 DLL 加载或修改 Plugin 配置。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-04-23 | `89df8c170d23` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types. | 全局性构建重构，将 DLL 导出标记从类型级别改为方法/静态变量级别。非 MsQuic 特定改动。 |
| 2023-05-16 | `e2056a616f78` | [MsQuic] Fixing MsQuic linux build and runtime load of .so | 修复 Linux 平台的 MsQuic 构建和运行时 .so 加载问题。 |
| 2023-05-12 | `d463abe686f8` | [MsQuic] Restructuring MsQuicRuntime module to have a static InitRuntime function | 重构模块，添加静态 `InitRuntime()` 函数，使 DLL 加载可由外部程序按需触发。 |

### 维护评价

- **创建时间**：2023-05-10，约 3 年前，UE5 新增
- **最近更新**：2025-04 有一次全局性构建修复，但自 2023-05 以来没有 MsQuic 功能性更新
- **MsQuic 版本**：固定在 v2.2.0（2023-04-18 发布），尚未升级
- **维护状态**：**稳定/低活跃** — 代码极简（3 个源文件），功能明确，无需频繁更新
- **已知限制**：
  - 仅支持特定 UE 程序（非通用游戏运行时）
  - Mac 平台在 ThirdParty Build.cs 中被排除（`bShouldUseMsQuic = false`），但 Plugin 声明支持 Mac
  - MsQuic v2.2.0 已有新版本可用，但未更新
- **推荐使用**：如果你需要在 UE5 工具链中使用 QUIC 协议，此 Plugin 是官方推荐的入口点

## 相关链接

- [源码 - Plugin](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MsQuic)
- [源码 - MsQuic ThirdParty](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/ThirdParty/MsQuic)
- [Microsoft MsQuic 官方仓库](https://github.com/microsoft/msquic)
- [MsQuic API 文档](https://learn.microsoft.com/en-us/windows/win32/wininet/quic-start)
- 主要使用者：SwitchboardListener (`Engine/Source/Programs/SwitchboardListener/`)
- 主要使用者：UBA NetworkBackendQuic (`Engine/Source/Programs/UnrealBuildAccelerator/Common/Private/UbaNetworkBackendQuic.cpp`)

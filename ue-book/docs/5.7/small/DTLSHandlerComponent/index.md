# DTLS Network Packet Handler

> Provides a packet handler component to do DTLS encryption and decryption.

| 属性 | 值 |
|---|---|
| 分类 | Runtime (PacketHandlers) |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 否 |
| 模块 | DTLSHandlerComponent (Runtime) |
| 创建时间 | 2019-10-01 |
| 年龄标签 | 👴 老古董(>5年) |
| 实验性 | ⚠️ `IsExperimentalVersion = true` |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/PacketHandlers/DTLSHandlerComponent) | |

## 用途

DTLSHandlerComponent 是 UE5 网络 **PacketHandler** 框架中的一个加密组件，基于 OpenSSL 实现 **DTLS (Datagram Transport Layer Security)** 协议，为 UDP 网络通信提供传输层加密。

它解决的核心问题是：**如何在不可靠的 UDP 传输上实现安全的加密通信**。标准 TLS 面向 TCP 流式传输，而 DTLS 是 TLS 的 UDP 适配版本，专门处理数据包丢失、乱序、重放等 UDP 特有问题。

该组件作为 `FEncryptionComponent` 的子类，嵌入 UE 的 PacketHandler 管道中，在网络数据包发送/接收时自动进行加密/解密，对上层游戏逻辑透明。

### 两种认证模式

该插件支持两种 DTLS 认证方式：

1. **Pre-Shared Key (PSK)** — 默认模式（`DTLS.PreSharedKeys=1`）。客户端和服务端共享密钥，使用 `PSK-AES256-GCM-SHA384` 密码套件。握手更快，适合游戏场景。
2. **自签名证书** — 当 `DTLS.PreSharedKeys=0` 时使用。自动生成 RSA 2048 位自签名 X509 证书，客户端通过 SHA256 指纹验证服务端证书身份。密码套件为 `HIGH`。

## 使用场景

- 你在做一个多人在线游戏，需要对 UDP 网络流量加密 → 使用此插件
- 你需要为 Dedicated Server 和客户端之间的通信提供安全性 → 配合 PacketHandler 使用
- 你希望避免中间人攻击，需要验证服务端证书 → 使用证书模式并交换指纹
- 你追求低延迟握手，信任共享密钥分发机制 → 使用 PSK 模式（默认）

## 蓝图用法

此插件没有暴露任何蓝图接口。它是一个纯 C++ 网络层组件，通过 UE 的 PacketHandler 框架自动集成到网络栈中，不需要（也无法在）蓝图中直接操作。

配置通过控制台变量（CVar）完成，可以在 DefaultEngine.ini 或运行时控制台中设置。

## C++ 用法

### 头文件引入

```cpp
#include "DTLSHandlerComponent.h"
#include "DTLSCertStore.h"
#include "DTLSCertificate.h"
```

### 启用插件

由于 `EnabledByDefault = false`，需要在项目的 `.uproject` 文件中手动启用：

```json
{
    "Plugins": [
        {
            "Name": "DTLSHandlerComponent",
            "Enabled": true
        }
    ]
}
```

### 控制台变量

| CVar | 默认值 | 说明 |
|---|---|---|
| `DTLS.PreSharedKeys` | `1` | 非零时使用 PSK 模式，否则使用自签名证书 |
| `DTLS.CertLifetime` | `14400` (4小时) | 生成证书的有效期（秒） |
| `DTLS.HandshakeRetry` | `500` | 握手重试间隔（毫秒） |
| `DTLS.DebugFingerprints` | `0` | 非零时将证书指纹导出到日志目录（仅非 Shipping 构建） |

### 证书管理

通过 `FDTLSCertStore` 单例管理证书：

```cpp
#include "DTLSCertStore.h"

// 创建一个有效期 1 小时的证书
FDTLSCertStore& CertStore = FDTLSCertStore::Get();
TSharedPtr<FDTLSCertificate> Cert = CertStore.CreateCert(
    FTimespan::FromHours(1),
    TEXT("MyServerCert")
);

// 获取证书指纹（32 字节 SHA256）
TArrayView<const uint8> Fingerprint = Cert->GetFingerprint();

// 从 PEM 文件导入已有证书
TSharedPtr<FDTLSCertificate> ImportedCert = CertStore.ImportCert(
    TEXT("/path/to/cert.pem"),
    TEXT("ImportedCert")
);

// 导出证书到 PEM 文件
if (Cert.IsValid())
{
    Cert->ExportCertificate(TEXT("/path/to/export.pem"));
}

// 移除证书
CertStore.RemoveCert(TEXT("MyServerCert"));
```

### PacketHandler 集成

DTLSHandlerComponent 通过 UE 的 PacketHandler 框架自动工作。它会在模块启动时注册为 `FPacketHandlerComponentModuleInterface`，当网络连接需要加密时，由 `FEncryptionComponent` 接口驱动：

```cpp
// FDTLSHandlerComponent 的生命周期（由引擎自动调用）：

// 1. 初始化
FDTLSHandlerComponent::Initialize();

// 2. 设置加密数据（PSK 或证书标识）
FDTLSHandlerComponent::SetEncryptionData(EncryptionData);

// 3. 启用加密 — 客户端立即开始握手，服务端等待客户端发起
FDTLSHandlerComponent::EnableEncryption();

// 4. 握手完成后，所有数据包自动加密/解密
// Incoming() — 接收时解密
// Outgoing() — 发送时加密

// 5. 禁用加密
FDTLSHandlerComponent::DisableEncryption();
```

### DTLS 握手状态机

组件内部维护三个状态：

```
Unencrypted → Handshaking → Encrypted
```

- **Unencrypted**: 初始状态，数据包明文传输
- **Handshaking**: 正在进行 DTLS 握手，此时：
  - 非握手数据包会被丢弃
  - 客户端主动发起握手
  - 服务端在收到首个握手包后进入此状态
- **Encrypted**: 握手完成，所有数据包通过 SSL 加密/解密

### 自定义 PacketHandler 组件

如果你需要扩展或替换默认行为，可以继承 `FDTLSHandlerComponentModule`：

```cpp
// 在你的模块中重写 CreateComponentInstance
TSharedPtr<HandlerComponent> FMyDTLSModule::CreateComponentInstance(FString& Options)
{
    // 可以在此处注入自定义逻辑
    return MakeShared<FDTLSHandlerComponent>();
}
```

## Demo 示例

### 最小使用示例 — 手动创建和管理证书

```cpp
// DTLSMinimalExample.h
#pragma once

#include "CoreMinimal.h"

class FDTLSMinimalExample
{
public:
    static void RunExample();
};
```

```cpp
// DTLSMinimalExample.cpp
#include "DTLSMinimalExample.h"
#include "DTLSCertStore.h"
#include "DTLSCertificate.h"
#include "DTLSHandlerTypes.h"

void FDTLSMinimalExample::RunExample()
{
    // 获取证书存储单例
    FDTLSCertStore& CertStore = FDTLSCertStore::Get();

    // 创建一个有效期 2 小时的自签名证书
    FTimespan Lifetime = FTimespan::FromHours(2);
    TSharedPtr<FDTLSCertificate> ServerCert = CertStore.CreateCert(
        Lifetime,
        TEXT("GameServer")
    );

    if (ServerCert.IsValid())
    {
        // 获取证书的 SHA256 指纹（用于客户端验证）
        TArrayView<const uint8> Fingerprint = ServerCert->GetFingerprint();
        
        UE_LOG(LogTemp, Log, TEXT("Certificate fingerprint (%d bytes):"), Fingerprint.Num());
        for (int32 i = 0; i < Fingerprint.Num(); i++)
        {
            UE_LOG(LogTemp, Log, TEXT("  [%02d] = 0x%02X"), i, Fingerprint[i]);
        }

        // 导出证书到文件（可选）
        ServerCert->ExportCertificate(TEXT("ServerCert.pem"));
    }

    // 清理
    CertStore.RemoveCert(TEXT("GameServer"));
}
```

### Build.cs 依赖

```csharp
// 注意：DTLSHandlerComponent 自身不暴露 PublicDependencyModuleNames
// 它的依赖都是 Private 的：Core, CoreUObject, NetCore, PacketHandler, Engine
// 如果你需要直接使用 DTLS 相关类，需要在你的模块中添加：
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "SSL",           // OpenSSL 模块
    "PacketHandler", // 如果你要扩展 PacketHandler
});
```

### 平台支持

DTLS 功能需要 OpenSSL 支持（`bPlatformSupportsOpenSSL`）。支持的平台：

| 平台 | 支持 |
|---|---|
| Windows (Win64) | ✅ |
| macOS | ✅ |
| Linux | ✅ |
| iOS | ✅ |
| Android | ✅ |
| 其他平台 | ❌ `UE_WITH_DTLS=0`，功能被编译排除 |

## 模块依赖

从 `DTLSHandlerComponent.Build.cs` 的 `PrivateDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `NetCore` | 网络核心 |
| `PacketHandler` | PacketHandler 框架（加密组件基类所在） |
| `Engine` | 引擎核心 |
| `SSL` | UE 的 OpenSSL 封装模块（条件依赖，仅支持 OpenSSL 的平台） |
| `OpenSSL` | OpenSSL 第三方库（条件依赖） |

> **注意**: 这些都是 `PrivateDependencyModuleNames`。使用者通常不需要直接依赖此插件模块，它通过 PacketHandler 框架自动加载。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-04-23 | `736bd5e2` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types. | API 导出宏重构，将 `DTLSHANDLERCOMPONENT_API` 从类型声明移到方法/静态变量上，适配 DLL 导出规范变更 |
| 2024-06-26 | `c5c17658` | Fixed incorrect FString constructor. | 修复 `FString::ConstructFromPtrSize` 的误用，可能是编译兼容性修复 |
| 2023-03-17 | `c341d7fc` | Added [[nodiscard]] to relevant TUniquePtr functions. Fixed up misuses. | 编译器警告清理，非功能性变更 |

### 维护评价

- **创建时间**: 2019 年 10 月，至今约 6.5 年
- **实验性标记**: `.uplugin` 中 `IsExperimentalVersion = true`，从未摘除
- **默认未启用**: `EnabledByDefault = false`，需要手动开启
- **更新频率**: 近 3 次更新跨越约 2 年，且均为非功能性维护（编译修复、宏清理）
- **核心逻辑未变**: 自 2019 年创建以来，核心 DTLS 握手和加解密逻辑未见实质性更新
- **无测试用例**: 在 `Engine/Tests/` 下未找到相关自动化测试

**综合评价**: ⚠️ **维护不活跃 / 实验性**

此插件功能完整但处于实验状态已超过 5 年，Epic 从未将其升级为正式功能。代码质量尚可，核心 OpenSSL 集成逻辑稳定，但缺乏活跃维护和测试覆盖。

**建议**: 如果你需要 DTLS 加密且了解其局限性，可以使用。但需注意：
- 它始终标记为实验性，未来可能被移除或重写
- 没有官方文档或技术支持
- 建议在生产环境中充分测试握手流程和边界情况

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/PacketHandlers/DTLSHandlerComponent)
- [PacketHandler 框架源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/PacketHandler)
- [SSL 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/SSL)

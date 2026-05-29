# DTLS network packet handler

> Provides a packet handler component to do DTLS encryption and decryption.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | DTLS网络数据包处理组件 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DTLSHandlerComponent` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-03 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PacketHandlers/DTLSHandlerComponent) | |

## 用途

DTLSHandlerComponent 为 UE5 的网络数据包处理栈提供了一个组件，用于对基于 UDP 的网络数据包进行 DTLS (Datagram Transport Layer Security) 协议的加密和解密。它基于 OpenSSL 实现，主要解决游戏服务器与客户端之间建立安全 UDP 通信的需求，是自定义网络栈加密能力的一部分。与 TLS 类似，但专门针对数据报（UDP）设计。

## 使用场景

- 你正在开发一个多人在线游戏，需要为游戏逻辑的 UDP 流量提供加密和身份验证。
- 你的项目需要使用 UE 的 `PacketHandler` 网络栈扩展机制，并希望集成基于证书或预共享密钥 (PSK) 的 DTLS 加密。
- 你需要一个可编程的网络加密层，支持自定义证书管理（生成、导入、导出）和握手流程控制。

## 蓝图用法

此插件主要面向 C++ 开发者，通过 UE 的 `PacketHandler` 接口集成，没有提供直接的蓝图可调用节点。其核心类（如 `FDTLSHandlerComponent`）并非 `UObject`，因此不暴露给蓝图反射系统。

## C++ 用法

### 头文件引入

```cpp
#include "DTLSHandlerComponent.h"
// 根据需求可能还需要引入：
#include "DTLSCertStore.h"
#include "DTLSCertificate.h"
#include "DTLSContext.h"
```

### 基本用法

首先需要通过 `FDTLSCertStore` 创建或导入证书，然后在建立网络连接时，将 `DTLSHandlerComponent` 作为 PacketHandler 进行配置。

```cpp
// 示例：在服务器或客户端的网络初始化代码中（来源：DTLSHandlerComponent.cpp 及相关类接口推断）
#include "DTLSHandlerComponent.h"
#include "DTLSCertStore.h"

// 1. 获取证书存储单例
FDTLSCertStore& CertStore = FDTLSCertStore::Get();

// 2. 创建一个自签名证书（有效期为1天）
FTimespan Lifetime = FTimespan::FromDays(1.0);
TSharedPtr<FDTLSCertificate> ServerCert = CertStore.CreateCert(Lifetime, TEXT("MyGameServerCert"));

if (ServerCert.IsValid())
{
    // 可以将证书导出到文件用于持久化或分发
    ServerCert->ExportCertificate(TEXT("ServerCert.pem"));
}

// 3. 当创建网络连接或处理数据包时，会实例化 FDTLSHandlerComponent。
// 它通过 FPacketHandlerComponentModuleInterface::CreateComponentInstance 创建。
// 后续，通过 SetEncryptionData 传入连接所需的加密配置（如证书指纹、PSK等）。
```

### 进阶用法

使用预共享密钥 (PSK) 替代证书进行身份验证，并配置 DTLS 上下文。

```cpp
// 示例：使用 PSK 模式（来源：FDTLSHandlerComponent.h, FDTLSContext.h 接口推断）
#include "DTLSHandlerComponent.h"
#include "DTLSContext.h"

// 假设我们已经得到了一个 FDTLSHandlerComponent 的共享指针 HandlerComponent
TSharedPtr<FDTLSHandlerComponent> HandlerComponent = /* ... */;

// 1. 创建并设置预共享密钥
TUniquePtr<FDTLSPreSharedKey> PSK = MakeUnique<FDTLSPreSharedKey>();
TArray<uint8> KeyData = {0x01, 0x02, 0x03, 0x04}; // 示例密钥数据
PSK->SetPreSharedKey(KeyData);
PSK->SetIdentity(TEXT("ClientPSKIdentity"));

// 2. 将 PSK 信息传递给 HandlerComponent
// 实际传递机制可能通过 FEncryptionData 或内部接口，这里展示概念。
// HandlerComponent 内部会使用 PSK 来初始化 FDTLSContext。

// 3. 启用加密
HandlerComponent->EnableEncryption();

// 4. 在 Tick 中，HandlerComponent 会处理 DTLS 握手（通过 TickHandshake），
//    握手完成后，所有经过此组件的 Incoming/Outgoing 数据包都会自动加解密。
```

## Demo 示例

一个最小的、用于生成和管理 DTLS 证书的 C++ 示例。

```cpp
// DTLSMinimalExample.h
#pragma once

#include "CoreMinimal.h"

class FDTLSCertificate;

class FDTLSMinimalExample
{
public:
    /** 演示基本的证书生成和存储流程 */
    static void DemonstrateCertManagement();
};
```

```cpp
// DTLSMinimalExample.cpp
#include "DTLSMinimalExample.h"
#include "DTLSCertStore.h"
#include "DTLSCertificate.h"

void FDTLSMinimalExample::DemonstrateCertManagement()
{
    // 获取证书存储单例
    FDTLSCertStore& CertStore = FDTLSCertStore::Get();

    // 生成一个有效期为1小时的证书，并以“MyTempCert”为名存储
    FTimespan HourLife = FTimespan::FromHours(1.0);
    TSharedPtr<FDTLSCertificate> NewCert = CertStore.CreateCert(HourLife, TEXT("MyTempCert"));

    if (NewCert.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("成功创建证书，指纹长度: %d"), NewCert->GetFingerprint().Num());

        // 从存储中按名称获取证书
        TSharedPtr<FDTLSCertificate> RetrievedCert = CertStore.GetCert(TEXT("MyTempCert"));
        if (RetrievedCert.IsValid() && RetrievedCert == NewCert)
        {
            UE_LOG(LogTemp, Log, TEXT("按名称成功检索证书"));
        }

        // 将证书导出到文件
        NewCert->ExportCertificate(TEXT("TempCert.pem"));

        // 移除存储中的证书
        CertStore.RemoveCert(TEXT("MyTempCert"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SSL` | 提供底层 OpenSSL 加密库的支持，是 DTLS 功能实现的基石 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复32位与64位格式化说明符匹配问题，提升日志兼容性 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，属于日志系统更新 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 为方法添加 DLL 导出标记，属于编译兼容性修复 |
| 2024-06-26 | `c5c17658` | Fixed incorrect FString constructor. | 修复错误的 FString 构造函数使用 |
| 2023-03-17 | `c341d7fc` | Added [[nodiscard]] to relevant TUniquePtr functions. | 为 TUniquePtr 的相关函数添加 [[nodiscard]] 属性，属于代码规范改进 |

### 维护评价

**中性**。该插件创建于 2019 年，属于实验性功能 (`IsExperimentalVersion: true`)，且默认未启用 (`EnabledByDefault: false`)。从提交历史看，过去几年有零星的维护更新，但主要集中在日志、编译警告和代码规范等非功能性修复上，没有看到核心功能的增加或重大问题的修复。这表明该插件功能可能已基本稳定，或处于低优先级维护状态。

由于是实验性插件，且长期无重大功能性更新，**建议在决定深度依赖前进行充分评估**。它适合需要 DTLS 加密且愿意承担实验性功能潜在风险的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PacketHandlers/DTLSHandlerComponent)
- [官方文档]() (无)
- [测试用例]() (未在源码中发现对应测试文件)
# Platform Cryptography Plugin

> Exposes a unified API for cryptography functionality provided by the platform, if available. Otherwise, interfaces with OpenSSL.

| 属性 | 值 |
|---|---|
| 中文名 | 平台加密插件 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PlatformCrypto` (Runtime), `PlatformCryptoContext` (Runtime), `PlatformCryptoOpenSSL` (External), `PlatformCryptoTypes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-11-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlatformCrypto) | |

## 用途

**PlatformCrypto** 为 Unreal Engine 提供了一套统一的、跨平台的加密算法接口。它封装了底层平台原生加密能力（如 Apple 的 Security Framework）和开源库 OpenSSL 的实现，开发者无需关心平台差异即可使用 AES-256 加密/解密、RSA 签名/验证、SHA-256 哈希等常见密码学功能。该插件主要解决以下问题：

- **消除平台差异**：不同操作系统（Windows、macOS、iOS、Android、Linux）对加密 API 的支持各不相同，插件提供一致的 C++ API。
- **简化集成**：通过 `IPlatformCryptoEncryptor` / `IPlatformCryptoDecryptor` 流式接口，支持渐进式加密/解密，无需一次性加载全部数据。
- **安全性**：底层使用 OpenSSL（或平台原生实现），避免开发者自行实现加密算法带来的安全风险。

`PlatformCryptoContext` 模块是该插件的核心运行时模块，提供了 `FEncryptionContextOpenSSL` 类作为主要的加密操作入口，以及 `FSHA256Hasher` 用于哈希计算。

## 使用场景

- 你需要在游戏或应用中加密网络通信数据（如自定义协议、包体加密）。
- 你需要对玩家存档、配置文件进行加密存储。
- 你需要实现数字签名（RS256）验证更新包或消息的合法性。
- 你需要计算数据的 SHA-256 摘要用于校验完整性。
- 你正在开发一个需要多平台部署的严肃/企业级应用，且依赖 OpenSSL 的加密算法。

## 蓝图用法

本模块未暴露任何 `BlueprintCallable` 函数。加密操作需要较高的参数控制（如密钥、初始化向量、认证标签），不适合从蓝图直接调用。请使用 C++ 实现加密逻辑，或通过封装成 BlueprintFunctionLibrary 暴露给蓝图。

## C++ 用法

### 头文件引入

使用核心加密功能引入以下头文件：

```cpp
#include "EncryptionContextOpenSSL.h"
#include "PlatformCryptoTypes.h"
```

若需使用流式加密/解密接口，还需包含相应工厂函数所在的头文件（它们已通过 `EncryptionContextOpenSSL.h` 间接暴露）。

### 基本用法

#### 1. 一次性加密/解密（AES-256-GCM）

```cpp
#include "EncryptionContextOpenSSL.h"
#include "PlatformCryptoTypes.h"

void Example_AES_GCM_EncryptDecrypt()
{
    FEncryptionContextOpenSSL Context;

    // 准备数据
    const TArray<uint8> Plaintext = {0x01, 0x02, 0x03, 0x04, 0x05};
    const TArray<uint8> Key(32);          // 256 位密钥，由您安全生成/分发
    const TArray<uint8> Nonce(12);        // 96 位 Nonce（IV）
    TArray<uint8> AuthTag;               // 认证标签（输出）

    // 加密
    EPlatformCryptoResult Result;
    TArray<uint8> Ciphertext = Context.Encrypt_AES_256_GCM(Plaintext, Key, Nonce, AuthTag, Result);
    check(Result == EPlatformCryptoResult::Success);

    // 解密（需要相同的 Key、Nonce 和 AuthTag）
    TArray<uint8> RecoveredPlaintext = Context.Decrypt_AES_256_GCM(Ciphertext, Key, Nonce, AuthTag, Result);
    check(Result == EPlatformCryptoResult::Success);
    // RecoveredPlaintext 应与原始 Plaintext 相同
}
```

*（示例来自 `EncryptionContextOpenSSL.h` 中的 `Encrypt_AES_256_GCM` / `Decrypt_AES_256_GCM` 函数声明）*

#### 2. 流式加密（适用于大文件）

```cpp
#include "EncryptionContextOpenSSL.h"
#include "IPlatformCryptoEncryptor.h"
#include "IPlatformCryptoDecryptor.h"

void Example_StreamingEncrypt()
{
    FEncryptionContextOpenSSL Context;

    // 创建 AES-256-CBC 加密器（需要密钥和 IV）
    const TArray<uint8> Key(32);
    const TArray<uint8> IV(16);          // CBC 需要 16 字节 IV
    TUniquePtr<IPlatformCryptoEncryptor> Encryptor = Context.CreateEncryptor_AES_256_CBC(Key, IV);

    if (!Encryptor.IsValid()) return;

    // 准备分片数据
    const TArray<uint8> Data = {0x10, 0x20, 0x30}; // 实际数据可能很大
    TArray<uint8> Output;
    Output.AddUninitialized(Encryptor->GetUpdateBufferSizeBytes(Data));

    int32 BytesWritten = 0;
    EPlatformCryptoResult Result = Encryptor->Update(Data, Output, BytesWritten);
    check(Result == EPlatformCryptoResult::Success);

    // 完成加密
    TArray<uint8> FinalBlock;
    FinalBlock.AddUninitialized(Encryptor->GetFinalizeBufferSizeBytes());
    int32 FinalBytes = 0;
    Result = Encryptor->Finalize(FinalBlock, FinalBytes);
    check(Result == EPlatformCryptoResult::Success);

    // 最终密文 = Output[0..BytesWritten-1] + FinalBlock[0..FinalBytes-1]
}
```

*（API 来源于 `IPlatformCryptoEncryptor` 接口及 `FEncryptionContextOpenSSL::CreateEncryptor_AES_256_CBC`）*

#### 3. 计算 SHA-256 哈希

```cpp
#include "EncryptionContextOpenSSL.h"

void Example_SHA256()
{
    FSHA256Hasher Hasher;

    // 初始化（可在构造后首次调用 Init，也可跳过，Update 时会自动初始化）
    Hasher.Init();

    // 输入数据（可分多次）
    const TArray<uint8> Data1 = {0x11, 0x22};
    const TArray<uint8> Data2 = {0x33, 0x44};
    Hasher.Update(Data1);
    Hasher.Update(Data2);

    // 获取摘要（32 字节）
    TArray<uint8> Digest;
    Digest.AddUninitialized(FSHA256Hasher::OutputByteLength); // = 32
    Hasher.Finalize(Digest);

    // Digest 即为 SHA-256 哈希值
}
```

*（API 来自 `FSHA256HasherOpenSSL`，定义于 `EncryptionContextOpenSSL.h`）*

#### 4. RSA 签名（RS256）

```cpp
#include "EncryptionContextOpenSSL.h"

void Example_RS256SignVerify()
{
    FEncryptionContextOpenSSL Context;

    // 假设已有 RSA 密钥对（通过 FRSAKeyHandle 管理）
    FRSAKeyHandle PrivateKey = /* 从文件或内存加载 */;
    FRSAKeyHandle PublicKey  = /* 对应的公钥 */;

    const TArray<uint8> Message = {0x41, 0x42, 0x43};

    // 签名
    TArray<uint8> Signature;
    bool bSignOK = Context.DigestSign_RS256(Message, Signature, PrivateKey);
    check(bSignOK);

    // 验证
    bool bVerifyOK = Context.DigestVerify_RS256(Message, Signature, PublicKey);
    check(bVerifyOK);
}
```

*（函数声明见 `EncryptionContextOpenSSL.h` 中的 `DigestSign_RS256` / `DigestVerify_RS256`）*

### 进阶用法

结合流式加密与自定义键值管理，可用于网络包加密。例如在 PacketHandler 中创建加密器/解密器实例，逐步处理数据包，并在每轮加密后重置 IV。

## Demo 示例

以下是一个完整的可编译 C++ 文件，演示 AES-256-GCM 加密解密流程。假设您的模块已正确引用 `PlatformCryptoContext` 和 `PlatformCryptoTypes`。

**MyEncryptionDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"

class FMyEncryptionDemo
{
public:
    static void RunDemo();
};
```

**MyEncryptionDemo.cpp**

```cpp
#include "MyEncryptionDemo.h"
#include "EncryptionContextOpenSSL.h"
#include "PlatformCryptoTypes.h"

void FMyEncryptionDemo::RunDemo()
{
    FEncryptionContextOpenSSL Context;

    // 1. 准备数据
    const uint8 PlaintextData[] = "Hello, PlatformCrypto!";
    TArray<uint8> Plaintext;
    Plaintext.Append(PlaintextData, sizeof(PlaintextData));

    // 2. 生成随机密钥和 Nonce（仅演示，实际应安全生成）
    TArray<uint8> Key;
    TArray<uint8> Nonce;
    Key.AddUninitialized(32);
    Nonce.AddUninitialized(12);
    FMemory::Memset(Key.GetData(), 0xAB, 32);
    FMemory::Memset(Nonce.GetData(), 0xCD, 12);

    // 3. 加密
    TArray<uint8> AuthTag;
    EPlatformCryptoResult Result;
    TArray<uint8> Ciphertext = Context.Encrypt_AES_256_GCM(Plaintext, Key, Nonce, AuthTag, Result);
    if (Result != EPlatformCryptoResult::Success)
    {
        UE_LOG(LogTemp, Error, TEXT("Encryption failed"));
        return;
    }

    // 4. 解密
    TArray<uint8> Decrypted = Context.Decrypt_AES_256_GCM(Ciphertext, Key, Nonce, AuthTag, Result);
    if (Result != EPlatformCryptoResult::Success)
    {
        UE_LOG(LogTemp, Error, TEXT("Decryption failed"));
        return;
    }

    // 5. 验证
    if (Decrypted == Plaintext)
    {
        UE_LOG(LogTemp, Log, TEXT("Encryption/Decryption successful!"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Data mismatch"));
    }
}
```

在您的 `GameInstance` 或启动逻辑中调用 `FMyEncryptionDemo::RunDemo()` 即可测试。

## 模块依赖

要使用 `PlatformCryptoContext` 模块提供的功能，您的模块的 `Build.cs` 应添加以下依赖（省略常见核心模块）：

| 模块 | 用途 |
|---|---|
| `PlatformCryptoTypes` | 提供加密结果枚举、接口基类（`IPlatformCryptoEncryptor` 等） |
| `PlatformCryptoOpenSSL` | 提供 OpenSSL 加密实现（作为外部依赖链接） |

实际依赖关系请参考 `PlatformCryptoContext.Build.cs` 的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames`。通常编译器会自动处理 `PlatformCryptoOpenSSL` 的符号链接。若使用静态链接，可能还需添加 `OpenSSL` 库自身的依赖。

## 维护状态

### 近期更新

- 2025-06-18 `082c27ae` — Clean up AES GCM PacketHandler code to have buffers with exactly MAX_PACKET_SIZE size.
- 2025-05-16 `97c9876a` — Add deprecated PlatformCryptoOpenSSL module to warn licensees of the module's replacement.
- 2025-04-23 `cea122ce` — Used UnrealPak build target to find and convert all files to have dllstorage on methods/staticvar in
- 2025-04-04 `49c9e5de` — Cleanup PlatformCrypto context build complexity. This fixes some incorrect explicit dependencies on
- 2024-11-10 `66e9bb39` — Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base

### 维护评价

- **创建时间**：2024 年 11 月（约 1 年）。
- **近期更新**：最近几个月仍有多项功能性提交（修复、优化、清理），无废弃标记。
- **活跃度**：活跃维护中。Epic Games 持续投入资源完善该插件。
- **已知问题**：目前无公开严重问题。部分平台可能缺乏原生加密实现而退回到 OpenSSL，但接口保持一致。
- **推荐度**：★★★★☆（推荐使用）。对于需要跨平台加密的 UE 项目，这是官方推荐方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlatformCrypto)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/platform-cryptography-in-unreal-engine/)（链接为推断，具体请参考 UE5 官方文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlatformCrypto/Source/PlatformCryptoContext/Private)（私人头文件多数位于 Private 目录，测试可能位于 `Engine/Tests/` 下）
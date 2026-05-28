# Platform Cryptography Plugin

> Exposes a unified API for cryptography functionality provided by the platform, if available. Otherwise, interfaces with OpenSSL.

| 属性 | 值 |
|---|---|
| 中文名 | 平台加密接口 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PlatformCrypto` (Runtime), `PlatformCryptoContext` (Runtime), `PlatformCryptoOpenSSL` (External), `PlatformCryptoTypes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-18 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlatformCrypto) | |

## 用途

PlatformCrypto 插件的核心目的是为 Unreal Engine 游戏提供一个跨平台、统一的加密功能抽象层。它解决了在不同操作系统（如 Windows、Xbox、PlayStation 等）上使用原生加密库带来的复杂性问题。开发者无需为每个平台编写特定的加密代码，只需通过 PlatformCrypto 提供的统一接口进行调用。插件会优先尝试使用平台原生的、经过安全认证的加密实现（例如 Xbox One 上的 BCrypt/CNG），如果该平台没有提供，则会回退到通用的 OpenSSL 库。

简而言之，这个插件让你专注于“加密”和“解密”这一业务逻辑，而不用关心“在哪里加密”和“用什么库加密”这种平台适配问题。

## 使用场景

-   **网络游戏流量加密**：你需要为你的多人游戏会话加密网络数据包，以防止数据被篡改或窥探。`PlatformCrypto` 与 `PacketHandler` 系统集成，可以方便地为网络流量添加 AES 加密层。
-   **安全数据存储**：你的游戏需要安全地存储或传输敏感信息（如玩家存档、内购凭证、本地配置等），可以使用此插件提供的对称加密（如 AES）功能对数据进行加解密。
-   **构建跨平台游戏**：当你的项目需要同时部署到 PC (Windows/Linux)、主机 (Xbox, PlayStation) 和移动平台，并且这些平台对加密库有不同的要求时，`PlatformCrypto` 提供了统一的接口来避免编写大量平台条件编译代码。

## 蓝图用法

本插件主要为 C++ 设计，但也通过 `PlatformCryptoTypes` 模块暴露了一些枚举和结构体给蓝图，以便进行基础的配置。核心的加解密函数并未直接暴露为蓝图节点。

### 核心类型

| 类型 | 说明 | 所在模块 |
|---|---|---|
| `EPlatformCryptoResult` | 枚举，表示加密操作的结果（成功、失败等）。 | `PlatformCryptoTypes` |
| `FEncryptionContext` | 结构体，代表一个加密会话的上下文，包含密钥等信息。 | `PlatformCryptoTypes` |

**注意**：具体的加密操作（如 AES 加密、解密）通常在 C++ 层面通过 `IPlatformCrypto` 接口和 `FEncryptionContext` 来完成。

## C++ 用法

### 头文件引入

要使用平台加密的核心功能，通常需要引入以下头文件：

```cpp
#include "PlatformCryptoTypes.h" // 包含 FEncryptionContext 等基础类型
#include "PlatformCrypto.h" // 包含 IPlatformCrypto 接口
```

### 基本用法

以下代码演示了如何获取平台加密接口并进行一次简单的 AES-ECB 模式加密。

```cpp
// 来源：推断自模块接口和常见加密流程
#include "PlatformCrypto.h"
#include "PlatformCryptoTypes.h"

void EncryptData()
{
    // 1. 获取平台加密接口单例
    IPlatformCrypto* PlatformCrypto = IPlatformCrypto::Get();

    // 2. 准备密钥和待加密数据
    TArray<uint8> Key = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10 }; // 示例 128 位 AES 密钥
    TArray<uint8> PlainData = { 0xAA, 0xBB, 0xCC, 0xDD };

    // 3. 创建加密上下文
    FEncryptionContext Context = PlatformCrypto->CreateEncryptionContext();

    // 4. 执行加密 (以 AES-ECB 为例)
    EPlatformCryptoResult Result;
    TArray<uint8> EncryptedData;
    Context.AES_Encrypt(Key, PlainData, EncryptedData, Result);

    if (Result == EPlatformCryptoResult::Success)
    {
        // 加密成功，使用 EncryptedData
        UE_LOG(LogTemp, Log, TEXT("加密成功，密文长度: %d"), EncryptedData.Num());
    }
}
```

### 进阶用法：AES-GCM 模式

对于需要认证加密的场景，可以使用 AES-GCM 模式。这通常需要处理初始化向量（IV）和附加认证数据（AAD）。

```cpp
void EncryptWithAESGCM()
{
    IPlatformCrypto* PlatformCrypto = IPlatformCrypto::Get();
    FEncryptionContext Context = PlatformCrypto->CreateEncryptionContext();

    TArray<uint8> Key; // 需填充为有效的 AES-256 密钥
    TArray<uint8> Nonce; // GCM 模式通常使用 12 字节的 Nonce (IV)
    TArray<uint8> AdditionalData; // 附加认证数据，可为空
    TArray<uint8> PlainText;

    // ... 填充 Key, Nonce, PlainText 数据 ...

    EPlatformCryptoResult Result;
    TArray<uint8> CipherText;
    TArray<uint8> AuthenticationTag; // GCM 会生成用于验证的 Tag

    // 执行 AES-GCM 加密
    Result = Context.AES_GCM_EncryptWithAdditionalData(Key, Nonce, PlainText, AdditionalData, CipherText, AuthenticationTag);

    if (Result == EPlatformCryptoResult::Success)
    {
        // 成功，现在可以将 CipherText 和 AuthenticationTag 一起传输
        // 解密时，需要提供相同的 Key, Nonce, CipherText, AdditionalData 和 AuthenticationTag 来验证数据完整性
    }
}
```

## Demo 示例

一个简单的加密解密演示：

**PlatformCryptoDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class PLATFORMCRYPTODEMO_API FPlatformCryptoDemo
{
public:
    static void RunDemo();
};
```

**PlatformCryptoDemo.cpp**
```cpp
#include "PlatformCryptoDemo.h"
#include "PlatformCrypto.h"
#include "PlatformCryptoTypes.h"

void FPlatformCryptoDemo::RunDemo()
{
    IPlatformCrypto* Crypto = IPlatformCrypto::Get();
    if (!Crypto)
    {
        UE_LOG(LogTemp, Error, TEXT("无法获取平台加密接口！"));
        return;
    }

    // 准备数据
    TArray<uint8> Key(16); // 128-bit key
    for (int i = 0; i < 16; ++i) Key[i] = i + 1;
    FString OriginalText = TEXT("Hello, PlatformCrypto!");
    TArray<uint8> OriginalData;
    OriginalData.Append((uint8*)*OriginalText, OriginalText.Len());

    // 加密
    FEncryptionContext EncCtx = Crypto->CreateEncryptionContext();
    EPlatformCryptoResult Result;
    TArray<uint8> EncryptedData;
    EncCtx.AES_Encrypt(Key, OriginalData, EncryptedData, Result);

    if (Result != EPlatformCryptoResult::Success)
    {
        UE_LOG(LogTemp, Error, TEXT("加密失败。"));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("原始数据长度: %d, 加密后长度: %d"), OriginalData.Num(), EncryptedData.Num());

    // 解密
    FEncryptionContext DecCtx = Crypto->CreateEncryptionContext();
    TArray<uint8> DecryptedData;
    DecCtx.AES_Decrypt(Key, EncryptedData, DecryptedData, Result);

    if (Result == EPlatformCryptoResult::Success && DecryptedData == OriginalData)
    {
        FString DecryptedString((const TCHAR*)*DecryptedData, DecryptedData.Num());
        UE_LOG(LogTemp, Log, TEXT("解密成功，数据一致。解密内容: %s"), *DecryptedString);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("解密失败或数据不一致。"));
    }
}
```

## 模块依赖

根据 `PlatformCryptoOpenSSL` 模块的 `Build.cs` 文件分析，该插件的独特依赖如下：

| 模块 | 用途 |
|---|---|
| `OpenSSL` | 作为 `PlatformCryptoOpenSSL` 模块的后端加密库，提供具体的加密算法实现。这是该插件回退到跨平台加密的核心依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了日志输出中32位和64位格式说明符混用的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将传统的 `UE_LOG` 宏迁移为更现代的 `UE_LOGF` 宏。 |
| 2026-02-26 | `37eb983a` | Add ED25519 key pair generation and sign/verify support to Engine/PlatformCrypto | 在平台加密模块中增加了对 ED25519 椭圆曲线签名算法的支持（生成密钥对、签名、验签）。 |
| 2025-06-18 | `082c27ae` | Clean up AES GCM PacketHandler code to have buffers with exactly MAX_PACKET_SIZE size. | 清理了用于处理 AES-GCM 加密网络包的代码，使其缓冲区大小精确匹配 `MAX_PACKET_SIZE`。 |
| 2025-05-16 | `97c9876a` | Add deprecated PlatformCryptoOpenSSL module to warn licensees of the module's replacement. | **关键更新**：将 `PlatformCryptoOpenSSL` 模块标记为弃用，并添加警告信息，提示用户该模块已被新模块取代。 |

### 维护评价

PlatformCrypto 插件**仍处于活跃维护状态**。从提交记录看，它在2026年仍有功能性更新（如新增 ED25519 算法支持）和代码现代化工作（日志宏迁移）。然而，**一个重要的注意事项是**：其核心的 OpenSSL 后端模块 `PlatformCryptoOpenSSL` 已于2025年被官方明确标记为**弃用（Deprecated）**。这意味着新项目不应再依赖 `PlatformCryptoOpenSSL`，而应使用 Epic 推荐的新替代模块（可能是其他平台原生加密模块）。

**推荐使用指南**：
1.  如果你需要使用 `PlatformCrypto` 提供的**统一接口和抽象层**，这仍然是官方推荐的做法，该接口本身是稳定的。
2.  **避免**在新建模块或项目中显式依赖 `PlatformCryptoOpenSSL` 模块。应依赖更上层的 `PlatformCrypto` 模块，让插件根据平台自动选择后端。
3.  请注意查阅 Epic 的最新文档或更新日志，以获取关于加密后端迁移的具体指引。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlatformCrypto)
-   官方文档（无提供链接）
-   测试用例（路径推测为 `Engine/Tests/PlatformCrypto/`）
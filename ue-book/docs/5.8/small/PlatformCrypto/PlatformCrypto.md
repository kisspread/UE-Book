# Platform Cryptography Plugin

> Exposes a unified API for cryptography functionality provided by the platform, if available. Otherwise, interfaces with OpenSSL.

| 属性 | 值 |
|---|---|
| 中文名 | 平台加密插件 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PlatformCrypto` (Runtime), `PlatformCryptoContext` (Runtime), `PlatformCryptoTypes` (Runtime), `PlatformCryptoOpenSSL` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-08-18 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlatformCrypto) | |

## 用途

PlatformCrypto 是 UE5 网络加密体系的底层基础设施。它解决的核心问题是：**不同平台提供了不同的加密原生实现**（例如 Xbox One 使用 BCrypt/CNG，PC 使用 OpenSSL），游戏代码不应该关心这些差异。

该插件提供了一个统一的 `FEncryptionContext` 接口，封装了以下加密能力：
- **对称加密**：AES-ECB、AES-CBC、AES-GCM
- **哈希算法**：SHA-1、SHA-256
- **数字签名**：RSA、Ed25519（2026 年新增）

UE5 的网络加密管线（`PacketHandler` 中的 `AESHandlerComponent`）直接依赖此插件来实现游戏流量加密。如果你需要在自己的游戏逻辑中进行平台无关的加密操作，也应使用此插件而非直接调用 OpenSSL 等第三方库。

## 使用场景

- 你需要为网络流量加密提供平台适配层 → 用 PlatformCrypto
- 你需要在多平台游戏中实现统一的 AES 加密/解密 → 用 PlatformCrypto
- 你需要生成 Ed25519 密钥对并进行签名/验签 → 用 PlatformCrypto
- 你需要平台无关的 SHA-256 哈希计算 → 用 PlatformCrypto
- 你是引擎网络层开发者，需要对接 `PacketHandler` 加密组件 → 用 PlatformCrypto

## 蓝图用法

PlatformCrypto 不暴露蓝图接口。它是一个纯 C++ 运行时模块，面向引擎和底层网络代码，不设计为蓝图可调用。

如果你需要在蓝图中使用加密功能，需要自行编写 C++ 包装层并通过 `UFUNCTION(BlueprintCallable)` 暴露。

## C++ 用法

### 头文件引入

```cpp
#include "PlatformCrypto.h"
```

### 基本用法

获取加密上下文并执行基础操作（基于模块接口推断）：

```cpp
#include "PlatformCrypto.h"
#include "PlatformCryptoContextIncludes.h"

// 检查平台加密模块是否可用
if (IPlatformCrypto::IsAvailable())
{
    // 获取平台对应的加密上下文
    TUniquePtr<FEncryptionContext> Context = IPlatformCrypto::Get().CreateContext();

    if (Context.IsValid())
    {
        // 后续可使用 Context 进行 AES 加密/解密、哈希计算等操作
    }
}
```

### 进阶用法

结合网络加密场景，通过 `FEncryptionContext` 进行 AES-GCM 加密：

```cpp
#include "PlatformCrypto.h"
#include "PlatformCryptoContextIncludes.h"

void EncryptPayload(const TArray<uint8>& Plaintext, const TArray<uint8>& Key, const TArray<uint8>& IV)
{
    if (!IPlatformCrypto::IsAvailable())
    {
        UE_LOG(LogNet, Warning, TEXT("PlatformCrypto not available"));
        return;
    }

    TUniquePtr<FEncryptionContext> Context = IPlatformCrypto::Get().CreateContext();

    // 使用 AES-GCM 模式加密（提供认证加密，兼具机密性和完整性）
    TArray<uint8> Ciphertext;
    Context->Encrypt_AES_GCM(Plaintext, Key, IV, Ciphertext);

    // Ciphertext 现在包含加密后的数据
}
```

## Demo 示例

一个完整的最小加密示例，展示如何使用 PlatformCrypto 进行 AES 加密：

**PlatformCryptoDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "PlatformCrypto.h"
#include "PlatformCryptoContextIncludes.h"

class FPlatformCryptoDemo
{
public:
    /** 加密一段数据，返回密文。失败时返回空数组 */
    static TArray<uint8> EncryptData(const TArray<uint8>& InData, const TArray<uint8>& InKey);

    /** 解密一段密文，返回明文。失败时返回空数组 */
    static TArray<uint8> DecryptData(const TArray<uint8>& InCiphertext, const TArray<uint8>& InKey);

    /** 计算数据的 SHA-256 哈希 */
    static TArray<uint8> ComputeSHA256(const TArray<uint8>& InData);
};
```

**PlatformCryptoDemo.cpp**
```cpp
#include "PlatformCryptoDemo.h"

TArray<uint8> FPlatformCryptoDemo::EncryptData(const TArray<uint8>& InData, const TArray<uint8>& InKey)
{
    if (!IPlatformCrypto::IsAvailable())
    {
        return {};
    }

    TUniquePtr<FEncryptionContext> Context = IPlatformCrypto::Get().CreateContext();
    if (!Context.IsValid())
    {
        return {};
    }

    TArray<uint8> OutCiphertext;
    Context->Encrypt_AES_ECB(InData, InKey, OutCiphertext);
    return OutCiphertext;
}

TArray<uint8> FPlatformCryptoDemo::DecryptData(const TArray<uint8>& InCiphertext, const TArray<uint8>& InKey)
{
    if (!IPlatformCrypto::IsAvailable())
    {
        return {};
    }

    TUniquePtr<FEncryptionContext> Context = IPlatformCrypto::Get().CreateContext();
    if (!Context.IsValid())
    {
        return {};
    }

    TArray<uint8> OutPlaintext;
    Context->Decrypt_AES_ECB(InCiphertext, InKey, OutPlaintext);
    return OutPlaintext;
}

TArray<uint8> FPlatformCryptoDemo::ComputeSHA256(const TArray<uint8>& InData)
{
    if (!IPlatformCrypto::IsAvailable())
    {
        return {};
    }

    TUniquePtr<FEncryptionContext> Context = IPlatformCrypto::Get().CreateContext();
    if (!Context.IsValid())
    {
        return {};
    }

    TArray<uint8> OutHash;
    Context->ComputeSHA256(InData, OutHash);
    return OutHash;
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 模块）。

此插件的内部模块依赖关系为：
- `PlatformCrypto` → `PlatformCryptoContext`
- `PlatformCryptoContext` → `PlatformCryptoTypes`
- `PlatformCryptoOpenSSL`（External）→ OpenSSL 第三方库

你的项目模块如果需要直接使用 `FEncryptionContext`，需在 Build.cs 中添加 `PlatformCrypto` 依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF 新格式 |
| 2026-02-26 | `37eb983a` | Add ED25519 key pair generation and sign/verify support to Engine/PlatformCrypto | 新增 Ed25519 密钥对生成和签名验证支持 |
| 2025-06-18 | `082c27ae` | Clean up AES GCM PacketHandler code to have buffers with exactly MAX_PACKET_SIZE size. | 清理 AES GCM 缓冲区大小使其精确匹配最大包尺寸 |
| 2025-05-16 | `97c9876a` | Add deprecated PlatformCryptoOpenSSL module to warn licensees of the module's replacement. | 将 PlatformCryptoOpenSSL 标记为已废弃，警告许可证持有者迁移 |

### 维护评价

**维护中，但有风险信号。**

- **活跃度**：2026 年 4 月仍有功能性更新（Ed25519 支持），属于活跃维护状态。
- **实验性**：插件仍位于 `Experimental` 目录下，未正式毕业到稳定类别。
- **废弃警告**：`PlatformCryptoOpenSSL` 模块已于 2025 年 5 月标记为废弃，表明 Epic 正在推进平台原生加密替代 OpenSSL 的策略。
- **长期存在**：创建于 2017 年，已有 8 年历史，是网络加密管线的核心依赖，不太可能被完全移除。
- **建议**：可以用于引擎级加密需求，但关注 `Experimental` 状态和 OpenSSL 模块的废弃迁移。如果你的项目直接引用了 `PlatformCryptoOpenSSL`，应尽早迁移到平台原生实现。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlatformCrypto)
- 官方文档（无）
- 测试用例（无公开测试文件）
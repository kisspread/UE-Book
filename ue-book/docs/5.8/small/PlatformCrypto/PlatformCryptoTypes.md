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
| 创建时间 | 2017-08-18 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlatformCrypto) | |

## 用途

PlatformCrypto 插件旨在为 UE 应用程序提供一套**跨平台、统一的加密与解密 API**。它的核心价值在于：
1.  **平台抽象**：插件会尝试利用目标平台提供的原生加密功能（例如 Xbox One 的 BCrypt/CNG）。如果平台没有提供或不可用，它将回退到一个通用的 OpenSSL 实现。
2.  **流式处理**：提供了 `IPlatformCryptoEncryptor` 和 `IPlatformCryptoDecryptor` 接口，允许开发者以分块（chunks）的方式进行加解密，这对于处理大数据流（如网络数据包）非常高效，无需一次性将所有数据加载到内存。
3.  **网络集成**：从其创建历史可知，该插件与引擎的网络层（如 PacketHandler、AESHandlerComponent）深度集成，旨在为游戏网络通信提供透明的加密支持。

## 使用场景

-   你正在开发一个**多人在线游戏**，需要为客户端与服务器之间的网络流量提供加密保护 → 使用此插件的 `AESHandlerComponent` 等组件。
-   你的游戏需要在不同主机平台（如 PC、Xbox）上运行，并希望**优先使用各平台的硬件加速或安全加密功能**，同时保持代码统一。
-   你需要加密/解密大型文件或数据流，希望避免单次内存分配过大 → 使用其流式（Progressive）加密/解密接口。

## 蓝图用法

当前分析的 `PlatformCryptoTypes` 模块主要定义了 C++ 接口和数据类型，**没有直接暴露 `BlueprintCallable` 节点**。加密功能通常由引擎网络层（如 PacketHandler）内部使用，或通过其他更高级的系统（如 Online Subsystem）间接暴露给蓝图。游戏逻辑蓝图一般不直接操作底层加密流。

## C++ 用法

### 头文件引入

```cpp
#include "PlatformCryptoTypes.h"
```

### 基本用法：创建加密器和解密器

`IPlatformCryptoEncryptor` 和 `IPlatformCryptoDecryptor` 是核心接口，其具体实现（如基于 OpenSSL 或 BCrypt）由插件内部创建。通常通过插件提供的工厂函数或上下文对象来获取实例。

```cpp
// （概念性示例，具体获取方式需参考 PlatformCryptoContext 模块的 API）
TUniquePtr<IPlatformCryptoEncryptor> Encryptor = PlatformCryptoContext->CreateAESGCM128Encryptor(Key, IV);
if (Encryptor)
{
    // ... 使用加密器
}
```

### 进阶用法：流式加密/解密数据块

```cpp
// 假设已获得一个 IPlatformCryptoEncryptor 实例
TArray<uint8> PlaintextData = ... // 待加密数据
TArray<uint8> CiphertextBuffer;
int32 BytesWritten = 0;

// 1. 计算输出缓冲区所需大小
const int32 RequiredBufferSize = Encryptor->GetUpdateBufferSizeBytes(PlaintextData);
CiphertextBuffer.SetNumUninitialized(RequiredBufferSize);

// 2. 分块加密（一次或多次调用 Update）
EPlatformCryptoResult Result = Encryptor->Update(
    MakeArrayView(PlaintextData.GetData(), PlaintextData.Num()),
    MakeArrayView(CiphertextBuffer.GetData(), CiphertextBuffer.Num()),
    BytesWritten
);

if (Result == EPlatformCryptoResult::Success)
{
    // 处理加密后的数据 (CiphertextBuffer[0..BytesWritten-1])

    // 3. 最终确定加密（处理最后可能不足一个块的数据和填充）
    TArray<uint8> FinalizeBuffer;
    FinalizeBuffer.SetNumUninitialized(Encryptor->GetFinalizeBufferSizeBytes());
    int32 FinalBytesWritten = 0;
    Result = Encryptor->Finalize(
        MakeArrayView(FinalizeBuffer.GetData(), FinalizeBuffer.Num()),
        FinalBytesWritten
    );

    if (Result == EPlatformCryptoResult::Success)
    {
        // 处理最后输出的数据 (FinalizeBuffer[0..FinalBytesWritten-1])
        // 对于支持 AuthTag 的模式（如 GCM），此时可调用 Encryptor->GenerateAuthTag(...)。
    }
}
```

### 使用辅助类 `FAESBlockEncryptionHelper`

该类帮助管理缓冲区，确保传递给底层加密函数的数据始终是块大小的整数倍。

```cpp
// 假设我们有一个执行 AES-CBC 加密的 Lambda
auto EncryptBlock = [](const TArrayView<const uint8> InData, const TArrayView<uint8> OutData, int32& OutWritten) -> EPlatformCryptoResult
{
    // 调用底层平台加密API（如 AES_cbc_encrypt）
    // ...
    OutWritten = InData.Num(); // 示例
    return EPlatformCryptoResult::Success;
};

FAESBlockEncryptionHelper AESHelper(16); // AES 块大小通常为 16 字节
TArray<uint8> OutputBuffer;
int32 TotalBytesWritten = 0;

// 流式处理输入数据
for (const auto& DataChunk : InputStream)
{
    OutputBuffer.SetNumUninitialized(DataChunk.Num() + AESHelper.GetBlockSize()); // 预分配足够空间
    int32 BytesWritten = 0;
    EPlatformCryptoResult Res = AESHelper.Update(
        MakeArrayView(DataChunk.GetData(), DataChunk.Num()),
        EncryptBlock,
        MakeArrayView(OutputBuffer.GetData(), OutputBuffer.Num()),
        BytesWritten
    );
    // 使用 OutputBuffer[0..BytesWritten-1] ...
}

// 最终确定
OutputBuffer.SetNumUninitialized(AESHelper.GetBlockSize());
int32 FinalBytes = 0;
EPlatformCryptoResult FinalRes = AESHelper.Finalize(EncryptBlock, MakeArrayView(OutputBuffer.GetData(), OutputBuffer.Num()), FinalBytes);
// 使用最后的数据 ...
```

## Demo 示例

一个模拟使用 `IPlatformCryptoEncryptor` 接口进行 AES 加密的最小示例。

**CryptoDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "PlatformCryptoTypes.h"

class FCryptoDemo
{
public:
    void RunDemo();
private:
    // 模拟一个平台加密器（实际应从插件获取）
    TUniquePtr<IPlatformCryptoEncryptor> CreateMockEncryptor();
};
```

**CryptoDemo.cpp**
```cpp
#include "CryptoDemo.h"
#include "Misc/SecureHash.h" // 用于演示，非加密必需

// 模拟一个简单的 XOR “加密器”用于演示接口使用
class FXOREncryptor : public IPlatformCryptoEncryptor
{
public:
    FXOREncryptor() : Key(0x5A) {}
    virtual FName GetCipherName() const override { return TEXT("XORDemo"); }
    virtual int32 GetCipherBlockSizeBytes() const override { return 1; }
    virtual int32 GetCipherInitializationVectorSizeBytes() const override { return 0; }
    virtual int32 GetCipherAuthTagSizeBytes() const override { return 0; }
    virtual EPlatformCryptoResult GenerateAuthTag(const TArrayView<uint8>, int32&) const override { return EPlatformCryptoResult::Failure; }
    virtual int32 GetUpdateBufferSizeBytes(const TArrayView<const uint8> Plaintext) const override { return Plaintext.Num(); }
    virtual EPlatformCryptoResult Update(const TArrayView<const uint8> Plaintext, const TArrayView<uint8> OutCiphertext, int32& OutCiphertextBytesWritten) override
    {
        if (OutCiphertext.Num() < Plaintext.Num()) return EPlatformCryptoResult::Failure;
        for (int32 i = 0; i < Plaintext.Num(); ++i)
        {
            OutCiphertext[i] = Plaintext[i] ^ Key;
        }
        OutCiphertextBytesWritten = Plaintext.Num();
        return EPlatformCryptoResult::Success;
    }
    virtual int32 GetFinalizeBufferSizeBytes() const override { return 0; }
    virtual EPlatformCryptoResult Finalize(const TArrayView<uint8>, int32& OutCiphertextBytesWritten) override { OutCiphertextBytesWritten = 0; return EPlatformCryptoResult::Success; }
    virtual EPlatformCryptoResult Reset(const TArrayView<const uint8>) override { return EPlatformCryptoResult::Success; }
private:
    uint8 Key;
};

TUniquePtr<IPlatformCryptoEncryptor> FCryptoDemo::CreateMockEncryptor()
{
    return MakeUnique<FXOREncryptor>();
}

void FCryptoDemo::RunDemo()
{
    // 1. 获取加密器实例
    TUniquePtr<IPlatformCryptoEncryptor> Encryptor = CreateMockEncryptor();
    if (!Encryptor)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create encryptor"));
        return;
    }

    // 2. 准备数据
    FString OriginalMessage = TEXT("Hello Platform Crypto!");
    FTCHARToUTF8 Converter(*OriginalMessage);
    TArray<uint8> Plaintext;
    Plaintext.Append((uint8*)Converter.Get(), Converter.Length());

    TArray<uint8> Ciphertext;
    int32 BytesWritten = 0;

    // 3. 计算所需缓冲区大小并分配
    const int32 BufferSize = Encryptor->GetUpdateBufferSizeBytes(Plaintext);
    Ciphertext.SetNumUninitialized(BufferSize);

    // 4. 执行加密
    EPlatformCryptoResult Result = Encryptor->Update(
        MakeArrayView(Plaintext.GetData(), Plaintext.Num()),
        MakeArrayView(Ciphertext.GetData(), Ciphertext.Num()),
        BytesWritten
    );

    if (Result == EPlatformCryptoResult::Success)
    {
        // 5. 结束加密流
        TArray<uint8> FinalizeBuffer;
        FinalizeBuffer.SetNumUninitialized(Encryptor->GetFinalizeBufferSizeBytes());
        int32 FinalBytes = 0;
        Result = Encryptor->Finalize(MakeArrayView(FinalizeBuffer), FinalBytes);

        if (Result == EPlatformCryptoResult::Success)
        {
            // 6. 输出结果（XOR示例中，Ciphertext就是结果）
            UE_LOG(LogTemp, Log, TEXT("Original: %s"), *OriginalMessage);
            UE_LOG(LogTemp, Log, TEXT("Encrypted (%d bytes): %s"), BytesWritten, *FString::FromHexBlob(Ciphertext.GetData(), BytesWritten));
        }
    }

    // 注意：此示例中的 XOR 加密器只是一个演示用的 Mock。
    // 在真实应用中，应使用 PlatformCrypto 插件提供的安全加密实现。
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine 等） | `PlatformCryptoTypes` 模块仅定义接口和类型，无复杂依赖。其他模块（如 `PlatformCrypto`、`PlatformCryptoOpenSSL`）会依赖具体的加密库。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了64位参数使用的32位格式说明符，确保类型匹配 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移到新的UE_LOGF |
| 2026-02-26 | `37eb983a` | Add ED25519 key pair generation and sign/verify support to Engine/PlatformCrypto | 为平台加密模块添加了ED25519密钥对生成和签名/验证支持 |
| 2025-06-18 | `082c27ae` | Clean up AES GCM PacketHandler code to have buffers with exactly MAX_PACKET_SIZE size. | 清理了AES GCM PacketHandler代码，使缓冲区大小恰好为MAX_PACKET_SIZE |
| 2025-05-16 | `97c9876a` | Add deprecated PlatformCryptoOpenSSL module to warn licensees of the module's replacement. | 添加了已废弃的PlatformCryptoOpenSSL模块，以警告用户该模块已被替换 |

### 维护评价

-   **创建时间**：插件于2017年8月创建，至今已有约9年历史。
-   **近期活跃度**：从Git历史看，插件在2025年和2026年仍有实质性更新（如添加ED25519支持、重构日志），表明它仍处于**活跃维护**中。
-   **状态**：虽然位于 `Experimental` 目录下，但 `EnabledByDefault` 为 true，且长期有更新，是引擎网络加密功能的重要基础。
-   **已知限制**：作为底层加密接口，其具体实现（如OpenSSL版本）可能随引擎版本升级而变化。
-   **推荐**：**推荐使用**。该插件为需要跨平台加密功能的项目（尤其是网络通信）提供了稳定、抽象的接口。虽然名称带有“Experimental”，但其长期维护和默认启用的状态表明它是引擎的可靠组成部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlatformCrypto)
- [官方文档]  （该插件在.uplugin中未提供DocsURL）
- [测试用例] （未在提供的信息中明确指定路径，测试可能位于 `Engine/Tests` 下或插件内部）
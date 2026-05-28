# Platform Cryptography Plugin

> Exposes a unified API for cryptography functionality provided by the platform, if available. Otherwise, interfaces with OpenSSL.

| 属性 | 值 |
|---|---|
| 中文名 | 平台加密插件 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PlatformCryptoContext` (Runtime), `PlatformCrypto` (Runtime), `PlatformCryptoOpenSSL` (External), `PlatformCryptoTypes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-18 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlatformCrypto) | |

## 用途

PlatformCrypto 插件为 Unreal Engine 提供了底层的、平台抽象的加密原语库。它并非直接面向游戏玩法逻辑，而是为引擎和高级系统（如网络通信）提供安全基础设施。其核心价值在于：

1.  **统一加密接口**：抽象了不同操作系统（如 Windows 的 BCrypt/CNG，其他平台的 OpenSSL）的加密库差异，为上层代码提供一致的 `IPlatformCryptoContext` 接口。
2.  **提供核心密码学操作**：包含对称加密（AES-256-ECB/CBC/GCM）、非对称加密（RSA）、哈希（SHA-256）、数字签名（RS256, Ed25519）、密钥生成和安全随机数生成等核心功能。
3.  **支持网络流量加密**：插件的创建与网络数据包加密组件（`AESHandlerComponent`）和网络握手流程的加密令牌（`EncryptionToken`）紧密相关，旨在为游戏网络通信提供端到端加密能力。

## 使用场景

- **游戏网络通信安全**：你需要为你的多人游戏实现数据包级别的加密，以防止数据在传输过程中被窃听或篡改。
- **数据完整性验证**：你需要对游戏存档、配置文件或关键数据进行 SHA-256 哈希计算，以验证其是否被意外损坏或恶意修改。
- **数字签名与验证**：你需要生成或验证数字签名，以确保收到的数据（如游戏资源、服务器指令）确实来自可信方。
- **安全的随机数生成**：你需要为游戏中的关键系统（如随机任务生成、抽奖系统）生成密码学安全的随机数。
- **构建跨平台安全功能**：你希望在 Windows, Xbox, PlayStation 等多个平台上使用同一套加密代码，而无需关心底层平台库的差异。

## 蓝图用法

**无。** 此插件主要提供 C++ 层面的底层加密接口，未暴露任何 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。加密操作通常性能敏感且涉及二进制数据，因此更适合在 C++ 中使用。

## C++ 用法

### 头文件引入

```cpp
#include "PlatformCryptoContext.h" // 获取模块单例
#include "EncryptionContextOpenSSL.h" // 使用加密功能（注意：当前所有平台都使用此实现）
```

### 基本用法

**1. AES-256-CBC 加密与解密**

```cpp
// 从 EncryptionContextOpenSSL.h
void EncryptAndDecryptData()
{
    // 确保加密上下文模块可用
    if (!IPlatformCryptoContext::IsAvailable())
    {
        return;
    }
    
    // 获取加密上下文（通常在平台层配置好，此处使用 OpenSSL 实现）
    FEncryptionContextOpenSSL EncryptionContext;
    EPlatformCryptoResult Result;
    
    // 生成一个 32 字节的 AES-256 密钥（实际项目中应安全存储和交换）
    TArray<uint8> Key;
    Key.SetNumZeroed(32); // 示例，应使用安全随机数生成
    
    // 生成一个 16 字节的初始化向量 (IV)
    TArray<uint8> IV;
    IV.SetNumZeroed(16);
    
    // 要加密的明文
    TArray<uint8> Plaintext = { 0x48, 0x65, 0x6c, 0x6c, 0x6f }; // “Hello”
    
    // 加密
    TArray<uint8> Ciphertext = EncryptionContext.Encrypt_AES_256_CBC(
        Plaintext,
        Key,
        IV,
        Result
    );
    
    if (Result == EPlatformCryptoResult::Success)
    {
        UE_LOG(LogTemp, Log, TEXT("Encryption successful. Ciphertext size: %d"), Ciphertext.Num());
        
        // 解密
        TArray<uint8> DecryptedText = EncryptionContext.Decrypt_AES_256_CBC(
            Ciphertext,
            Key,
            IV,
            Result
        );
        
        if (Result == EPlatformCryptoResult::Success)
        {
            // 验证解密结果
            ensure(DecryptedText == Plaintext);
            UE_LOG(LogTemp, Log, TEXT("Decryption successful. Data matches."));
        }
    }
}
```

**2. 使用 SHA-256 计算哈希**

```cpp
// 从 EncryptionContextOpenSSL.h
void ComputeHash()
{
    FEncryptionContextOpenSSL EncryptionContext;
    TArray<uint8> SourceData = { /* ... your data ... */ };
    TArray<uint8> Hash;
    
    // 方法一：一步计算
    bool bSuccess = EncryptionContext.CalcSHA256(SourceData, Hash);
    if (bSuccess)
    {
        // Hash 现在包含 32 字节的 SHA-256 摘要
    }
    
    // 方法二：使用流式哈希器（适用于大文件）
    FSHA256Hasher Hasher = EncryptionContext.CreateSHA256Hasher();
    TArray<uint8> Chunk1 = { /* ... chunk 1 ... */ };
    TArray<uint8> Chunk2 = { /* ... chunk 2 ... */ };
    
    Hasher.Update(Chunk1);
    Hasher.Update(Chunk2);
    
    TArray<uint8> FinalHash;
    FinalHash.SetNumZeroed(FSHA256Hasher::OutputByteLength);
    EPlatformCryptoResult FinalResult = Hasher.Finalize(FinalHash);
}
```

**3. RSA 操作（签名与验证）**

```cpp
// 从 EncryptionContextOpenSSL.h
void RSAOperations()
{
    FEncryptionContextOpenSSL EncryptionContext;
    
    // 生成 RSA 密钥对
    TArray<uint8> PublicExponent, PrivateExponent, Modulus;
    bool bGenSuccess = EncryptionContext.GenerateKey_RSA(2048, PublicExponent, PrivateExponent, Modulus);
    if (bGenSuccess)
    {
        // 从分量创建 RSA 密钥句柄
        FRSAKeyHandle PrivateKey = EncryptionContext.CreateKey_RSA(PublicExponent, PrivateExponent, Modulus);
        
        // 使用私钥进行签名
        TArray<uint8> Message = { /* ... message to sign ... */ };
        TArray<uint8> Signature;
        bool bSignSuccess = EncryptionContext.DigestSign_RS256(Message, Signature, PrivateKey);
        
        // 从 PEM 格式字符串加载公钥（典型使用场景）
        FString PEM_PublicKey = TEXT("-----BEGIN PUBLIC KEY-----\nMIIBIjANBg...\n-----END PUBLIC KEY-----");
        FRSAKeyHandle PublicKey = EncryptionContext.GetPublicKey_RSA(PEM_PublicKey);
        
        // 使用公钥验证签名
        bool bVerifySuccess = EncryptionContext.DigestVerify_RS256(Message, Signature, PublicKey);
        
        // 释放密钥句柄
        EncryptionContext.DestroyKey_RSA(PrivateKey);
        EncryptionContext.DestroyKey_RSA(PublicKey);
    }
}
```

### 进阶用法

**使用流式加密器 (Encryptor/Decryptor) 处理大数据**

对于大型数据，一次性加载到内存进行加密可能不可行。应使用 `CreateEncryptor` 和 `CreateDecryptor` 系列函数创建流式处理器。

```cpp
// 来自 PlatformCryptoAesEncryptorsOpenSSL.h / PlatformCryptoAesDecryptorsOpenSSL.h 的接口
void StreamEncryption()
{
    FEncryptionContextOpenSSL EncryptionContext;
    TArray<uint8> Key, IV;
    // ... 初始化 Key 和 IV ...
    
    // 创建 AES-256-GCM 加密器（带认证标签）
    TUniquePtr<IPlatformCryptoEncryptor> Encryptor = EncryptionContext.CreateEncryptor_AES_256_GCM(Key, IV);
    
    if (Encryptor.IsValid())
    {
        TArray<uint8> Plaintext = { /* ... large data ... */ };
        TArray<uint8> Ciphertext;
        int32 BytesWritten = 0;
        EPlatformCryptoResult Result;
        
        // 分块加密
        for (int32 Offset = 0; Offset < Plaintext.Num(); Offset += 1024)
        {
            int32 ChunkSize = FMath::Min(1024, Plaintext.Num() - Offset);
            TArrayView<const uint8> ChunkView(&Plaintext[Offset], ChunkSize);
            TArray<uint8> ChunkOut;
            ChunkOut.SetNum(Encryptor->GetUpdateBufferSizeBytes(ChunkView));
            
            Result = Encryptor->Update(ChunkView, ChunkOut, BytesWritten);
            Ciphertext.Append(ChunkOut.GetData(), BytesWritten);
        }
        
        // 完成加密，获取认证标签（GCM 特性）
        TArray<uint8> FinalChunk;
        FinalChunk.SetNum(Encryptor->GetFinalizeBufferSizeBytes());
        Result = Encryptor->Finalize(FinalChunk, BytesWritten);
        Ciphertext.Append(FinalChunk.GetData(), BytesWritten);
        
        TArray<uint8> AuthTag;
        AuthTag.SetNum(Encryptor->GetCipherAuthTagSizeBytes());
        Result = Encryptor->GenerateAuthTag(AuthTag, BytesWritten);
        
        // 现在，Ciphertext 和 AuthTag 可以安全传输或存储
    }
}
```

## Demo 示例

一个最小的、可运行的 C++ 示例，演示如何使用 `FEncryptionContextOpenSSL` 进行基本的 AES-256-CBC 加密和 SHA-256 哈希。

**CryptoDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CryptoDemoActor.generated.h"

UCLASS()
class ACryptoDemoActor : public AActor
{
	GENERATED_BODY()
	
public:	
	ACryptoDemoActor();

protected:
	virtual void BeginPlay() override;
	
private:
	void DemonstrateAES256CBC();
	void DemonstrateSHA256();
};
```

**CryptoDemoActor.cpp**
```cpp
#include "CryptoDemoActor.h"
#include "PlatformCryptoContext.h" // 模块头文件
#include "EncryptionContextOpenSSL.h" // 加密功能实现

ACryptoDemoActor::ACryptoDemoActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void ACryptoDemoActor::BeginPlay()
{
	Super::BeginPlay();
	
	// 检查平台加密模块是否可用
	if (IPlatformCryptoContext::IsAvailable())
	{
		UE_LOG(LogTemp, Log, TEXT("PlatformCrypto module is available. Starting crypto demos."));
		DemonstrateAES256CBC();
		DemonstrateSHA256();
	}
	else
	{
		UE_LOG(LogTemp, Warning, TEXT("PlatformCrypto module is not available on this platform."));
	}
}

void ACryptoDemoActor::DemonstrateAES256CBC()
{
	FEncryptionContextOpenSSL EncryptionContext;
	EPlatformCryptoResult Result;
	
	// 硬编码密钥和 IV 仅用于演示，切勿在实际产品中使用！
	TArray<uint8> Key;
	Key.SetNumZeroed(32); // 256-bit key
	Key[0] = 0x2B; Key[1] = 0x7E; Key[2] = 0x15; Key[3] = 0x16; // 示例填充
	
	TArray<uint8> IV;
	IV.SetNumZeroed(16); // 128-bit IV
	IV[0] = 0x00; IV[1] = 0x01; IV[2] = 0x02; IV[3] = 0x03; // 示例填充
	
	// 明文数据
	FString PlaintextString = TEXT("Hello, PlatformCrypto!");
	TArray<uint8> Plaintext;
	Plaintext.Append((uint8*)TCHAR_TO_UTF8(*PlaintextString), PlaintextString.Len());
	
	// 加密
	TArray<uint8> Ciphertext = EncryptionContext.Encrypt_AES_256_CBC(Plaintext, Key, IV, Result);
	
	if (Result == EPlatformCryptoResult::Success)
	{
		UE_LOG(LogTemp, Log, TEXT("AES-256-CBC Encrypt: Success. Input: %d bytes, Output: %d bytes"),
			Plaintext.Num(), Ciphertext.Num());
		
		// 解密
		TArray<uint8> DecryptedData = EncryptionContext.Decrypt_AES_256_CBC(Ciphertext, Key, IV, Result);
		
		if (Result == EPlatformCryptoResult::Success && DecryptedData == Plaintext)
		{
			FString DecryptedString = UTF8_TO_TCHAR(DecryptedData.GetData());
			UE_LOG(LogTemp, Log, TEXT("AES-256-CBC Decrypt: Success. Recovered: %s"), *DecryptedString);
		}
		else
		{
			UE_LOG(LogTemp, Error, TEXT("AES-256-CBC Decrypt: Failed!"));
		}
	}
}

void ACryptoDemoActor::DemonstrateSHA256()
{
	FEncryptionContextOpenSSL EncryptionContext;
	
	// 计算字符串的 SHA-256 哈希
	FString TestString = TEXT("Unreal Engine Crypto");
	TArray<uint8> SourceData;
	SourceData.Append((uint8*)TCHAR_TO_UTF8(*TestString), TestString.Len());
	
	TArray<uint8> Hash;
	bool bSuccess = EncryptionContext.CalcSHA256(SourceData, Hash);
	
	if (bSuccess && Hash.Num() == 32)
	{
		// 将哈希转换为十六进制字符串以便显示
		FString HashHex;
		for (uint8 Byte : Hash)
		{
			HashHex += FString::Printf(TEXT("%02x"), Byte);
		}
		UE_LOG(LogTemp, Log, TEXT("SHA-256 of \"%s\": %s"), *TestString, *HashHex);
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("SHA-256 calculation failed!"));
	}
}
```

## 模块依赖

使用此插件的功能，你的模块需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `PlatformCrypto` | 核心加密接口和类型定义。 |
| `PlatformCryptoContext` | 提供 `IPlatformCryptoContext` 模块接口。 |
| `PlatformCryptoOpenSSL` | **必须**。 提供基于 OpenSSL 的加密算法实现（`FEncryptionContextOpenSSL`）。即使在其他平台，当前也依赖此模块。 |

**示例 Build.cs 片段:**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    // 你的其他依赖...
    "PlatformCrypto",
    "PlatformCryptoContext",
    "PlatformCryptoOpenSSL"
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式说明符与参数位宽不匹配的潜在问题，提升代码健壮性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，属于引擎全局的日志系统更新。 |
| 2026-02-26 | `37eb983a` | Add ED25519 key pair generation and sign/verify support to Engine/PlatformCrypto | **功能更新**：为平台加密添加了 Ed25519 签名算法支持，增加了密钥生成、签名和验证功能。 |
| 2025-06-18 | `082c27ae` | Clean up AES GCM PacketHandler code to have buffers with exactly MAX_PACKET_SIZE size. | 优化了 AES GCM 数据包处理器的缓冲区大小，使其精确匹配最大包尺寸。 |
| 2025-05-16 | `97c9876a` | Add deprecated PlatformCryptoOpenSSL module to warn licensees of the module's replacement. | 添加了已废弃的 `PlatformCryptoOpenSSL` 模块警告，提示授权用户该模块已被替代。 |

### 维护评价

- **活跃维护**：插件在 **2026 年 4 月** 仍有实质性功能更新和代码维护，表明它并非废弃项目。
- **长期存在**：自 **2017 年** 创建以来，已存在约 **8 年**，是一个相对成熟和底层的基础设施模块。
- **功能持续增强**：最近的提交显示仍在添加新的密码学算法（如 Ed25519），并进行代码清理和优化。
- **已知限制**：虽然标注为 “Experimental”，但代码历史较长，且在引擎关键网络功能中被使用，其稳定性应高于典型的实验性功能。主要限制是其 API 为 C++ 专用，且使用较为底层。
- **推荐使用**：**推荐**用于需要底层加密原语的场景，特别是为引擎或工具链开发网络加密、数据验证等系统。对于游戏玩法层面的简单加密需求，建议封装或寻找更高级的抽象层。需要注意的是，其使用涉及密钥管理、模式选择等安全敏感决策，应由熟悉密码学的开发者负责集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlatformCrypto)
- [官方文档] 暂无
- [测试用例] 插件目录内未发现标准测试文件，测试可能集成在网络加密相关的单元测试中。
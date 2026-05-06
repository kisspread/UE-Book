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

该插件提供一套统一的加密 API，屏蔽底层实现差异。在支持硬件加密的平台（如 iOS 的 Security Framework、Android 的 KeyStore）上优先使用平台原生能力，否则回退到 OpenSSL 加密库。`PlatformCryptoOpenSSL` 是 OpenSSL 实现的封装模块，但**已被官方标记为弃用（deprecated）**，后续版本将由新的替代模块接管。插件主要用于网络通信加密、数据完整性校验、数字签名等需要跨平台一致加密行为的场景。

## 使用场景

- **多人游戏加密**：对客户端与服务器之间的网络包进行 AES-GCM 加密，防止篡改和窃听。
- **本地存储加密**：加密玩家存档、配置文件等敏感数据。
- **验证对抗**：生成 HMAC 签名验证更新包或 DLC 的完整性。
- **证书与密钥处理**：在自定义认证流程中解析 X.509 证书或生成 RSA 签名。

## 蓝图用法

本插件主要面向 C++ 开发者，蓝图暴露接口非常有限。目前没有发现可直接调用的蓝图节点。如果需要从蓝图执行加密操作，建议编写 C++ 函数库并将其暴露为蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "PlatformCrypto.h"           // 主模块头文件
#include "PlatformCryptoTypes.h"      // 加密类型定义
#include "EncryptionContext.h"        // 加密上下文接口
```

### 基本用法

以下示例演示如何获取加密上下文并对数据进行 AES-256-GCM 加密/解密。代码基于官方测试文件 `PlatformCryptoTest.cpp` 和通用 API 编写。

```cpp
// 获取加密上下文（单例）
TSharedPtr<FEncryptionContext> CryptoContext = FPlatformCrypto::GetEncryptionContext();

// 准备数据
const FString PlaintextString = TEXT("Hello, PlatformCrypto!");
const TArray<uint8> Plaintext = FTCHARToUTF8(PlaintextString).GetBytes();

// 生成随机密钥与 IV（生产环境应从安全随机源生成）
TArray<uint8> Key(32);  // AES-256 需要 32 字节密钥
TArray<uint8> IV(12);   // GCM 推荐 12 字节随机数
CryptoContext->GenerateRandomBytes(Key.GetData(), Key.Num());
CryptoContext->GenerateRandomBytes(IV.GetData(), IV.Num());

// 加密（返回加密结果和认证标签）
TArray<uint8> Ciphertext;
TArray<uint8> AuthTag;
bool bEncrypted = CryptoContext->Encrypt_AES_256_GCM(
    Plaintext,
    Key,
    IV,
    Ciphertext,
    AuthTag
);
check(bEncrypted);

// 解密
TArray<uint8> Decrypted;
bool bDecrypted = CryptoContext->Decrypt_AES_256_GCM(
    Ciphertext,
    Key,
    IV,
    AuthTag,
    Decrypted
);
check(bDecrypted);
check(Decrypted == Plaintext);
```

**来源**：[Engine/Plugins/Experimental/PlatformCrypto/Source/PlatformCrypto/Private/Tests/PlatformCryptoTest.cpp](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/PlatformCrypto/Source/PlatformCrypto/Private/Tests/PlatformCryptoTest.cpp)

### 进阶用法

**使用 PacketHandler 集成**  
在网络子系统中，可以通过 `UE::Net::PacketHandler` 的加密组件自动对发送的包进行加密。具体实现参考 `Clean up AES GCM PacketHandler code` 提交相关代码。

**自定义密钥提供器**  
如果需要从外部密钥管理系统获取密钥，可以实现 `IKeyProvider` 接口并注入加密上下文。

## Demo 示例

以下是一个最小 C++ 类，在 Actor 的 `BeginPlay` 中加密一个固定字符串并打印结果。

### PlatformCryptoDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PlatformCryptoDemo.generated.h"

UCLASS()
class APLATFORMCRYPTODEMO_API APlatformCryptoDemo : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
};
```

### PlatformCryptoDemo.cpp

```cpp
#include "PlatformCryptoDemo.h"
#include "PlatformCrypto.h"
#include "EncryptionContext.h"
#include "Containers/Array.h"
#include "Internationalization/Text.h"

void APlatformCryptoDemo::BeginPlay()
{
    Super::BeginPlay();

    TSharedPtr<FEncryptionContext> Context = FPlatformCrypto::GetEncryptionContext();
    if (!Context.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get encryption context"));
        return;
    }

    // 明文
    const FString Secret = TEXT("This is a secret message.");
    const TArray<uint8> Plaintext = FTCHARToUTF8(Secret).GetBytes();

    // 生成密钥与 IV（仅演示）
    TArray<uint8> Key(32), IV(12);
    Context->GenerateRandomBytes(Key.GetData(), Key.Num());
    Context->GenerateRandomBytes(IV.GetData(), IV.Num());

    // 加密
    TArray<uint8> Ciphertext, AuthTag;
    if (!Context->Encrypt_AES_256_GCM(Plaintext, Key, IV, Ciphertext, AuthTag))
    {
        UE_LOG(LogTemp, Error, TEXT("Encryption failed"));
        return;
    }

    // 解密
    TArray<uint8> Decrypted;
    if (!Context->Decrypt_AES_256_GCM(Ciphertext, Key, IV, AuthTag, Decrypted))
    {
        UE_LOG(LogTemp, Error, TEXT("Decryption failed"));
        return;
    }

    // 验证
    const FString DecryptedStr = UTF8ToString(Decrypted);
    check(DecryptedStr == Secret);
    UE_LOG(LogTemp, Log, TEXT("PlatformCrypto Demo: Encryption & Decryption succeeded. Original: %s"), *Secret);
}
```

## 模块依赖

使用时只需在 `Build.cs` 的 `PublicDependencyModuleNames` 中添加 `"PlatformCrypto"` 即可自动包含所有子模块。以下列出该插件特有的依赖（已省略标准模块）：

| 模块 | 用途 |
|---|---|
| `PlatformCryptoTypes` | 加密算法枚举、密钥结构等类型定义 |
| `OpenSSL`（第三方） | 实现 AES、RSA、SHA 等算法（通过 `PlatformCryptoOpenSSL` 链接） |

**注意**：`PlatformCryptoOpenSSL` 作为外部模块将被标记弃用，未来版本可能移除。如果直接引用该模块需谨慎。

## 维护状态

### 近期更新

- 2025-06-18 `082c27ae` Clean up AES GCM PacketHandler code to have buffers with exactly MAX_PACKET_SIZE size.
- 2025-05-16 `97c9876a` Add deprecated PlatformCryptoOpenSSL module to warn licensees of the module's replacement.
- 2025-04-23 `cea122ce` Used UnrealPak build target to find and convert all files to have dllstorage on methods/staticvar in
- 2025-04-04 `49c9e5de` Cleanup PlatformCrypto context build complexity. This fixes some incorrect explicit dependencies on 
- 2024-11-10 `66e9bb39` Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base

### 维护评价

插件自 2024 年 11 月创建以来持续更新，近期仍有功能性清理和 PacketHandler 集成改进。但 `PlatformCryptoOpenSSL` 模块已被官方标记为弃用，计划被新实现替换。这意味着直接依赖 `PlatformCryptoOpenSSL` 的代码在未来版本可能失效。整体而言，插件仍处于**积极开发阶段**，但底层实现正在迁移。推荐在新项目中使用 `PlatformCrypto` 主模块，避免直接引用 `PlatformCryptoOpenSSL`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlatformCrypto)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/PlatformCrypto/Source/PlatformCrypto/Private/Tests/PlatformCryptoTest.cpp)
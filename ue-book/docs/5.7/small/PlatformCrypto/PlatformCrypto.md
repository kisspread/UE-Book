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

本插件为跨平台加密操作提供统一的抽象层。不同操作系统（如 iOS、Android、Windows）对加密功能的原生支持各不相同（例如 iOS 有 Keychain Services，Windows 有 CNG），而大多数桌面端则依赖 OpenSSL。Platform Cryptography Plugin 封装了这些差异，使得游戏或应用开发者无需关心底层实现，只需通过统一的接口即可完成加解密、哈希、签名等操作。当平台不提供原生加密时，自动回退到 OpenSSL 实现。该插件是 UE 网络层加密（如 PacketHandler 的 AES GCM 加密）的基础依赖。

## 使用场景

- 你需要对网络传输数据包进行加密，防止中间人攻击或篡改（如使用 AES-GCM 加密）
- 需要存储敏感数据（如用户凭据、许可证密钥）到本地，确保数据在磁盘上安全
- 需要在不同平台上使用一致的加密算法（如 RSA 签名验证）
- 希望在 UObject 序列化后对字节流进行加密，或对存档文件进行完整性校验

## 蓝图用法

当前版本**未提供蓝图可调用函数**。所有加密操作均设计为 C++ 接口，以确保性能和线程安全。如果您需要在蓝图中使用加密功能，可以通过继承 C++ 类并暴露自定义蓝图节点来实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无） | 本插件无蓝图暴露函数 | - |

## C++ 用法

### 头文件引入

```cpp
#include "IPlatformCrypto.h"
#include "PlatformCryptoTypes.h"   // 包含加密上下文类型定义
```

### 基本用法

通过 `IPlatformCrypto::Get()` 获取模块单例，然后调用 `CreateContext()` 获取适用于当前平台的加密上下文。该上下文可用于执行对称/非对称加密、哈希操作等。

```cpp
// 获取平台加密模块实例（自动加载模块）
IPlatformCrypto& CryptoModule = IPlatformCrypto::Get();

// 创建加密上下文（具体类型由平台决定，通常是 FEncryptionContext 的子类）
TUniquePtr<FEncryptionContext> Context = CryptoModule.CreateContext();

// 使用上下文进行 AES-GCM 加密（假设上下文提供了 Encrypt 方法）
// 注意：实际接口请参考 FEncryptionContext 的公开方法
TArray<uint8> Plaintext = { /* ... */ };
TArray<uint8> Key = { /* ... */ };
TArray<uint8> IV = { /* ... */ };
TArray<uint8> Ciphertext;
Context->Encrypt(Plaintext, Key, IV, Ciphertext);  // 伪代码，具体函数名以源码为准
```

### 进阶用法

利用平台加密上下文实现批量数据包的加密/解密（PacketHandler 场景，参考 `EncryptionComponent` 实现）：

```cpp
#include "PlatformCryptoContext.h"

// 在 FEncryptionComponent 初始化时创建上下文
void MyEncryptionComponent::Initialize()
{
    FEncryptionContext& Context = *(IPlatformCrypto::Get().CreateContext());
    // 配置密钥和 IV（从安全来源获取）
    Context.SetKey(MyKey);
    Context.SetIV(MyIV);
}

// 加密输出包
void MyEncryptionComponent::EncryptPacket(const TArray<uint8>& InData, TArray<uint8>& OutData)
{
    Context.Encrypt(InData, OutData);
}
```

（完整示例可参考 Plugin `PlatformCrypto` 源码中的 `Source/PlatformCrypto/Private/PlatformCrypto.cpp` 以及相关测试用例）

## Demo 示例

以下是一个独立的 C++ 模块示例，展示了如何获取加密上下文并执行一次简单的 AES-256 加密（假设 FEncryptionContext 公开了 `Encrypt` 方法）。实际接口请参考最新源码。

**MyEncryptionHelper.h**

```cpp
#pragma once
#include "CoreMinimal.h"
#include "IPlatformCrypto.h"

class FMyEncryptionHelper
{
public:
    static TArray<uint8> EncryptData(const TArray<uint8>& Data, const TArray<uint8>& Key, const TArray<uint8>& IV);
};
```

**MyEncryptionHelper.cpp**

```cpp
#include "MyEncryptionHelper.h"

TArray<uint8> FMyEncryptionHelper::EncryptData(const TArray<uint8>& Data, const TArray<uint8>& Key, const TArray<uint8>& IV)
{
    IPlaftformCrypto& Crypto = IPlatformCrypto::Get();
    TUniquePtr<FEncryptionContext> Context = Crypto.CreateContext();
    // 假设上下文存在 Encrypt 方法，返回加密后的数据
    TArray<uint8> Encrypted;
    Context->Encrypt(Data, Key, IV, Encrypted);
    return Encrypted;
}
```

使用时只需要包含头文件并调用 `FMyEncryptionHelper::EncryptData` 即可。请注意，以上代码中的 `Encrypt` 方法名和参数签名需根据实际 API 调整。

## 模块依赖

本插件依赖于 `PlatformCryptoTypes` 和 `PlatformCryptoContext` 两个内部模块。公共依赖仅有标准 `Core` 模块，无其他特殊依赖。

| 模块 | 用途 |
|---|---|
| `PlatformCryptoTypes` | 定义加密算法枚举、密钥类型、加密上下文基类等类型 |
| `PlatformCryptoContext` | 提供 `FEncryptionContext` 的具体实现（平台或 OpenSSL） |
| `PlatformCryptoOpenSSL` | OpenSSL 后端实现（外部模块） |

## 维护状态

### 近期更新

- 2025-06-18 `082c27ae` Clean up AES GCM PacketHandler code to have buffers with exactly MAX_PACKET_SIZE size.
- 2025-05-16 `97c9876a` Add deprecated PlatformCryptoOpenSSL module to warn licensees of the module's replacement.
- 2025-04-23 `cea122ce` Used UnrealPak build target to find and convert all files to have dllstorage on methods/staticvar in
- 2025-04-04 `49c9e5de` Cleanup PlatformCrypto context build complexity. This fixes some incorrect explicit dependencies on
- 2024-11-10 `66e9bb39` Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base

### 维护评价

- **创建时间**：2024-11-10，距今约 1 年，属于较新插件。
- **更新频率**：近半年内（2025-04 至 2025-06）有多次功能性更新和优化，包括 AES GCM 相关修复、依赖清理、OpenSSL 模块弃用提示等，表明开发团队仍在积极维护。
- **状态**：活跃维护。该插件已被用于 UE 网络层加密（PacketHandler），是引擎核心加密基础设施的一部分。
- **推荐**：推荐使用。作为官方提供的平台加密抽象，它减少了跨平台加密适配工作量，并且随着引擎更新持续获得改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlatformCrypto)
- [官方文档](https://dev.epicgames.com/documentation/unreal-engine/platform-cryptography-in-unreal-engine)（通用加密文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlatformCrypto/Source)（位于模块源码目录内，未独立分离）
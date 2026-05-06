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

本插件为 UE5 提供统一的加密 API 抽象层。它首先尝试使用平台原生的加密实现（如 Windows BCrypt、Apple 的 CommonCrypto 等），若平台未提供则回退到 OpenSSL。这使得开发者无需关心底层加密库的差异，即可在多个平台（Windows、Mac、Linux、iOS、Android、Console 等）上安全地执行对称加密、非对称加密、哈希、数字签名等操作。

`PlatformCryptoTypes` 模块定义了所有加密操作共用的基础类型和抽象接口（如 `IPlatformCryptoEncryptor` 类），是整个插件的数据契约层。其他模块（`PlatformCrypto`、`PlatformCryptoContext`、`PlatformCryptoOpenSSL`）依赖它提供具体的实现和上下文管理。

## 使用场景

- 需要加密网络通信（如 WebSocket、自定义游戏协议）的即时对战游戏
- 需要加密保存本地存档或配置文件的单机/联机游戏
- 需要实现玩家自定义内容（UGC）签名验证的社区创作平台
- 需要符合安全合规要求（如 PCI DSS、GDPR）的应用

## 蓝图用法

该模块 (`PlatformCryptoTypes`) 仅提供 C++ 抽象基类和枚举，**没有暴露任何蓝图中可调用的函数或可读写的属性**。蓝图中如需使用加密功能，必须通过 C++ 包装成 `UObject` 派生的 `BlueprintCallable` 函数，例如在 `PlatformCrypto` 模块中提供的 UBlueprintFunctionLibrary 类（需参考该模块文档）。因此，建议通过 C++ 编码使用该插件。

## C++ 用法

### 头文件引入

```cpp
#include "PlatformCryptoTypes.h"
```

### 基本用法

以下代码展示了如何使用加密器接口进行流式加密（来自测试用例 `PlatformCryptoTypesTest.cpp` 的典型模式）：

```cpp
#include "PlatformCryptoTypes.h"
#include "PlatformCrypto.h"   // 需包含具体实现模块的头文件

// 获取加密器实例（需通过具体实现模块创建，此处仅作示意）
TUniquePtr<IPlatformCryptoEncryptor> Encryptor = FPlatformCrypto::CreateEncryptor(NAME_AES_256_GCM);

// 准备明文和输出缓冲区
const TArray<uint8> Plaintext = { 0x01, 0x02, 0x03, 0x04 };
TArray<uint8> Ciphertext;
Ciphertext.SetNum(Encryptor->GetUpdateBufferSizeBytes(Plaintext) + Encryptor->GetFinalizeBufferSizeBytes());

// 逐步加密
int32 BytesWritten = 0;
EPlatformCryptoResult Result = Encryptor->Update(Plaintext, Ciphertext, BytesWritten);
ensure(Result == EPlatformCryptoResult::Success);

// 完成加密
int32 FinalBytes = 0;
Result = Encryptor->Finalize(TArrayView<uint8>(Ciphertext.GetData() + BytesWritten, Ciphertext.Num() - BytesWritten), FinalBytes);
ensure(Result == EPlatformCryptoResult::Success);

// 获取认证标签（GCM 模式）
TArray<uint8> AuthTag;
AuthTag.SetNum(Encryptor->GetCipherAuthTagSizeBytes());
int32 AuthTagWritten = 0;
ensure(Encryptor->GenerateAuthTag(AuthTag, AuthTagWritten) == EPlatformCryptoResult::Success);
```

*来源：`Engine/Plugins/Experimental/PlatformCrypto/Source/PlatformCryptoTypes/Private/Tests/PlatformCryptoTypesTest.cpp`*

### 进阶用法

结合 `FPlatformCryptoContext` 进行密钥管理，支持多个加密器实例并发工作：

```cpp
// 创建加密上下文（每个上下文可持有自己的密钥和 IV）
TUniquePtr<IPlatformCryptoContext> Context = FPlatformCrypto::CreateContext(NAME_AES_256_GCM);
Context->SetKey(MyKeyArray);      // 设置 32 字节密钥
Context->SetIV(MyIVArray);        // 设置 12 字节随机初始向量

// 创建加密器（从上下文衍生）
TUniquePtr<IPlatformCryptoEncryptor> Encryptor = Context->CreateEncryptor();
// ... 加密操作同上
```

## Demo 示例

以下是一个完整的、可编译的最小示例，演示如何使用 `PlatformCryptoTypes` 接口进行 AES-GCM 加密（使用 `PlatformCryptoOpenSSL` 实现）。确保项目中已添加对 `PlatformCryptoTypes` 和 `PlatformCrypto` 模块的依赖。

```cpp
// MyEncryptionDemo.h
#pragma once
#include "CoreMinimal.h"
#include "PlatformCryptoTypes.h"

class FMyEncryptionDemo
{
public:
    static void RunDemo();
};
```

```cpp
// MyEncryptionDemo.cpp
#include "MyEncryptionDemo.h"
#include "PlatformCrypto.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMyEncryptionDemoTest, "Plugins.PlatformCrypto.Demo", 
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::EngineFilter)

bool FMyEncryptionDemoTest::RunTest(const FString& Parameters)
{
    // 1. 准备明文
    const TArray<uint8> Plaintext = { 'H', 'e', 'l', 'l', 'o', ' ', 'W', 'o', 'r', 'l', 'd' };

    // 2. 创建加密器（使用 AES-256-GCM）
    TUniquePtr<IPlatformCryptoEncryptor> Encryptor = FPlatformCrypto::CreateEncryptor(NAME_AES_256_GCM);
    if (!Encryptor)
    {
        AddError(TEXT("Failed to create encryptor"));
        return false;
    }

    // 3. 计算输出缓冲区大小
    const int32 UpdateBufferSize = Encryptor->GetUpdateBufferSizeBytes(Plaintext);
    const int32 FinalizeBufferSize = Encryptor->GetFinalizeBufferSizeBytes();
    TArray<uint8> Ciphertext;
    Ciphertext.SetNum(UpdateBufferSize + FinalizeBufferSize);

    // 4. 加密
    int32 TotalWritten = 0;
    int32 TempWritten = 0;
    TestTrue("Update succeeded", Encryptor->Update(Plaintext, Ciphertext, TempWritten) == EPlatformCryptoResult::Success);
    TotalWritten += TempWritten;

    TestTrue("Finalize succeeded", Encryptor->Finalize(TArrayView<uint8>(Ciphertext.GetData() + TotalWritten, Ciphertext.Num() - TotalWritten), TempWritten) == EPlatformCryptoResult::Success);
    TotalWritten += TempWritten;

    // 5. 获取认证标签
    TArray<uint8> AuthTag;
    AuthTag.SetNum(Encryptor->GetCipherAuthTagSizeBytes());
    int32 AuthTagWritten = 0;
    TestTrue("GenerateAuthTag succeeded", Encryptor->GenerateAuthTag(AuthTag, AuthTagWritten) == EPlatformCryptoResult::Success);

    // 6. 验证非空
    TestTrue("Ciphertext not empty", TotalWritten > 0);

    return !HasAnyErrors();
}
```

## 模块依赖

使用当前模块 (`PlatformCryptoTypes`) 时，你的 `Build.cs` 需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `PlatformCryptoTypes` | 提供加密基础类型和抽象接口（必须） |
| `PlatformCrypto` | 提供工厂函数和平台实现（通常需要） |
| `PlatformCryptoOpenSSL` | 自动链接 OpenSSL（如果你的构建配置需要回退实现） |

**注意**：`PlatformCryptoTypes` 自身不依赖任何其他插件模块，它只包含轻量的 C++ 头文件和枚举。实际使用中几乎总是与 `PlatformCrypto` 一起引用。

## 维护状态

### 近期更新

- 2025-06-18 `082c27ae` Clean up AES GCM PacketHandler code to have buffers with exactly MAX_PACKET_SIZE size.
- 2025-05-16 `97c9876a` Add deprecated PlatformCryptoOpenSSL module to warn licensees of the module's replacement.
- 2025-04-23 `cea122ce` Used UnrealPak build target to find and convert all files to have dllstorage on methods/staticvar in
- 2025-04-04 `49c9e5de` Cleanup PlatformCrypto context build complexity. This fixes some incorrect explicit dependencies on 
- 2024-11-10 `66e9bb39` Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base

### 维护评价

- **创建时间**：2024-11-10，距今约 0.5 年，属于较新的插件。
- **更新频率**：近 6 个月内有多次功能性更新（如清理缓冲区大小、构建系统改进、废弃旧模块等），说明团队仍在积极维护。
- **活跃度**：2025 年 6 月仍有提交，反应迅速，符合 UE 5.7 后续版本的更新节奏。
- **质量**：代码经过重构成 dllstorage，修复了依赖问题，API 设计成熟。
- **推荐度**：**强烈推荐使用**。对于需要跨平台安全通信的项目，这是官方提供的标准加密方案。注意旧版 `PlatformCryptoOpenSSL` 已标记为 deprecated，应使用新的 `PlatformCrypto` + `PlatformCryptoTypes`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlatformCrypto)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/platform-cryptography-in-unreal-engine/)（5.7 版暂未更新，可参考 5.6 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/PlatformCrypto/Source/PlatformCryptoTypes/Private/Tests/PlatformCryptoTypesTest.cpp)
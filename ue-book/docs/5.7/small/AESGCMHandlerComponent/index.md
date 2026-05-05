# AES GCM Network Packet Handler

> Provides a packet handler component to do AES GCM encryption and decryption.

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | AESGCMHandlerComponent (Runtime) |
| 创建时间 | 2019-05-31 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/PacketHandlers/AESGCMHandlerComponent) | |

## 用途

AESGCMHandlerComponent 是 UE5 网络加密框架中的一个 PacketHandler 组件，用于对 UDP 网络数据包进行 **AES-256-GCM**（Galois/Counter Mode）加密和解密。

它解决的核心问题是：**防止游戏网络流量被窃听或篡改**。AES-GCM 是一种认证加密（Authenticated Encryption）模式，同时提供：

- **机密性**（Confidentiality）：数据被加密，第三方无法读取
- **完整性**（Integrity）：通过 Auth Tag 验证数据未被篡改
- **认证性**（Authenticity）：确认数据来自持有密钥的发送方

这个组件不是独立使用的加密工具——它是 UE5 **PacketHandler 链** 中的一个环节，需要通过网络子系统（NetDriver/NetConnection）集成，而非直接在游戏逻辑中调用。

> **注意**：此插件默认未启用（`EnabledByDefault: false`），需要手动在项目设置或 .uproject 中启用，或通过命令行参数 `-EncryptionToken` 触发。

## 使用场景

- 你的游戏需要对网络通信进行加密，防止玩家使用抓包工具窥探游戏协议 → 用 AESGCMHandlerComponent
- 你的游戏有反作弊需求，需要确保网络数据包未被中间人篡改 → AES-GCM 的认证标签（Auth Tag）提供完整性校验
- 你在开发竞技类游戏（如 MOBA、FPS、格斗游戏），需要保护网络数据的机密性和完整性 → 启用此插件作为 PacketHandler 链的一部分

### 典型架构位置

```
Game NetDriver
  └── PacketHandler 链
        ├── CompressionHandler（如 OodleNetworkHandler）← 压缩
        └── AESGCMHandlerComponent ← 加密（本插件）
```

加密包的二进制格式：
```
加密包: [IV:12字节] [AuthTag:16字节] [密文:N字节]
未加密包: [0x00] [明文:N字节]
```

## 蓝图用法

此插件 **没有暴露任何蓝图接口**。`FAESGCMHandlerComponent` 是纯 C++ 类，不继承 `UObject`，因此没有 `BlueprintCallable` 或 `BlueprintReadWrite` 属性。

加密功能通过 UE5 的网络子系统自动管理，游戏逻辑层通常不需要直接交互。

## C++ 用法

### 头文件引入

```cpp
#include "AESGCMHandlerComponent.h"
```

### 核心类

| 类 | 说明 |
|---|---|
| `FAESGCMHandlerComponent` | 主组件类，继承 `FEncryptionComponent`，实现 AES-256-GCM 加解密 |
| `FAESGCMHandlerComponentModule` | 模块工厂类，通过 PacketHandler 框架创建组件实例 |
| `FAESGCMFaultHandler` | 故障处理器，将 AES-GCM 解密错误上报给 NetConnection 故障恢复系统 |
| `EAESGCMNetResult` | AES-GCM 网络错误枚举，用于故障恢复计数 |

### 关键常量

```cpp
// 来自 AESGCMHandlerComponent.h
static const int32 KeySizeInBytes = 32;       // AES-256 密钥长度
static const int32 BlockSizeInBytes = 16;      // AES 块大小
static const int32 IVSizeInBytes = 12;         // GCM 模式 IV 长度
static const int32 AuthTagSizeInBytes = 16;    // 认证标签长度
```

### 基本用法

从测试用例提取的核心使用流程（来源：`Source/Tests/AESGCMHandlerComponentTest.cpp`）：

```cpp
#include "AESGCMHandlerComponent.h"
#include "PlatformCryptoTypes.h"

// 1. 创建组件实例
FAESGCMHandlerComponent Component;

// 2. 准备 32 字节的 AES-256 密钥
TArray<uint8> Key;
Key.SetNumUninitialized(FAESGCMHandlerComponent::KeySizeInBytes);
// ... 填充密钥数据（通常由服务端协商生成）

// 3. 设置加密数据
FEncryptionData EncryptionData = { Key };
Component.SetEncryptionData(EncryptionData);

// 4. 启用加密
Component.EnableEncryption();
```

设置密钥后，组件内部会：
- 生成随机 IV（首字节保证非零，用于区分加密/未加密包）
- 创建平台加密器（`IPlatformCryptoEncryptor`）和解密器（`IPlatformCryptoDecryptor`）

### 发送加密包（Outgoing）

```cpp
FBitWriter Packet(8 * MAX_PACKET_SIZE, false);

// 将明文数据写入 Packet
FMemory::Memcpy(Packet.GetData(), PlainTextData, PlainTextSize);
Packet.SetNumBits(8 * PlainTextSize);

// Outgoing 会自动：
// 1. 递增 IV（64位计数器模式）
// 2. 加密载荷
// 3. 生成 AuthTag
// 4. 将 [IV][AuthTag][密文] 写回 Packet
FOutPacketTraits Traits;
Component.Outgoing(Packet, Traits);
```

### 接收解密包（Incoming）

```cpp
FBitReader Packet(Bytes.GetData(), 8 * Bytes.Num());
TSharedPtr<const FInternetAddr> Address;
FInPacketTraits Traits;
FIncomingPacketRef PacketRef = { Packet, Address, Traits };

// Incoming 会自动：
// 1. 检查首字节（非零 = 加密包）
// 2. 提取 IV (12字节) 和 AuthTag (16字节)
// 3. 验证 AuthTag 并解密载荷
// 4. 将明文写回 Packet
Component.Incoming(PacketRef);
```

### 进阶：直接调用加解密

测试用例展示了直接调用底层 `Encrypt`/`Decrypt`（这些是 private 方法，仅通过 `friend class` 在测试中访问）：

```cpp
// 直接加密（测试用）
uint8 CipherText[MAX_PACKET_SIZE];
uint8 AuthTag[FAESGCMHandlerComponent::AuthTagSizeInBytes];
EPlatformCryptoResult Result = Component.Encrypt(
    CipherText, TestPlainText, TestIV, AuthTag
);

// 直接解密（测试用）
uint8 PlainText[MAX_PACKET_SIZE];
EPlatformCryptoResult Result = Component.Decrypt(
    PlainText, TestCipherText, TestIV, TestAuthTag
);
```

> ⚠️ 注意：`Encrypt` 和 `Decrypt` 是 private 方法。在实际使用中，应通过 `Incoming`/`Outgoing` 接口操作。

### 故障处理（Fault Handler）

AES-GCM 解密错误会通过 `FAESGCMFaultHandler` 上报给 NetConnection 的故障恢复系统：

```cpp
// EAESGCMNetResult 错误类型
enum class EAESGCMNetResult : uint8
{
    Unknown,
    Success,
    AESMissingIV,          // 包缺少 IV
    AESMissingAuthTag,     // 包缺少 AuthTag
    AESMissingPayload,     // 包缺少密文
    AESDecryptionFailed,   // 解密失败（密钥错误或数据损坏）
    AESZeroLastByte        // 最后字节为零
};
```

这些错误会被累加到 `NetConnectionFaultRecovery` 的计数器中（归类为 `NetworkCorruption`），如果错误频率过高，可能导致连接被关闭。

## Demo 示例

### 最小加解密示例

```cpp
// AESGCMExample.h
#pragma once
#include "CoreMinimal.h"

// AESGCM 最小使用示例
class FAESGCMExample
{
public:
    static void RunExample();
};
```

```cpp
// AESGCMExample.cpp
#include "AESGCMExample.h"
#include "AESGCMHandlerComponent.h"
#include "PlatformCryptoTypes.h"

void FAESGCMExample::RunExample()
{
    // 创建组件
    FAESGCMHandlerComponent Component;

    // 设置密钥（实际项目中由服务端安全分发）
    TArray<uint8> Key;
    Key.SetNumUninitialized(32);
    FMemory::Memset(Key.GetData(), 0xAB, 32);  // 示例密钥

    FEncryptionData EncryptionData = { Key };
    Component.SetEncryptionData(EncryptionData);
    Component.EnableEncryption();

    // 发送方：加密一个包
    FBitWriter Writer(8 * 1024, false);
    const char* Message = "Hello, encrypted world!";
    FMemory::Memcpy(Writer.GetData(), Message, strlen(Message));
    Writer.SetNumBits(8 * strlen(Message));

    FOutPacketTraits OutTraits;
    Component.Outgoing(Writer, OutTraits);

    // 接收方：解密同一个包
    FBitReader Reader(Writer.GetData(), Writer.GetNumBits());
    TSharedPtr<const FInternetAddr> Address;
    FInPacketTraits InTraits;
    FIncomingPacketRef PacketRef = { Reader, Address, InTraits };

    Component.Incoming(PacketRef);

    // Reader 现在包含解密后的明文
    FString Result((const ANSICHAR*)Reader.GetData(), Reader.GetNumBytes());
    UE_LOG(LogTemp, Log, TEXT("Decrypted: %s"), *Result);
}
```

### Build.cs 依赖

```csharp
// 如果你的模块需要引用 AESGCM 功能
PublicDependencyModuleNames.AddRange(new string[]
{
    "AESGCMHandlerComponent",
    "PacketHandler",
    "PlatformCrypto"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE5 核心库 |
| `CoreUObject` | UObject 系统基础 |
| `PacketHandler` | PacketHandler 框架（提供 `FEncryptionComponent` 基类） |
| `PlatformCrypto` | 平台加密接口（`IPlatformCrypto`、加密器/解密器抽象） |
| `PlatformCryptoContext` | 平台加密上下文实现 |
| `NetCore` | 网络核心（`NetConnectionFaultRecovery` 故障恢复） |

插件级依赖：
- **PlatformCrypto** 插件必须启用（在 .uplugin 中声明）

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-09-23 | `0bba868` | Handle packet bit-lengths that are not multiple of eight in AESGCMHandlerComponent | 修复了包长度非 8 位对齐时的处理问题，这是网络协议边缘情况的 bug fix |
| 2025-06-18 | `082c27a` | Clean up AES GCM PacketHandler code to have buffers with exactly MAX_PACKET_SIZE size. Update PlatformCrypto implementation to process exact amount of bytes for GCM mode, no padding block(s) necessary. Add AESGCMHandlerComponent test. | 重大清理：精确化缓冲区大小、移除 GCM 模式不必要的填充块、新增测试用例 |
| 2025-06-10 | `0babb55` | Update change for previous fix - correctly increase buffer for outgoing packets in AES GCM packet handler | 修复出站包缓冲区增长逻辑的后续修正 |

### 维护评价

- **创建时间**：2019-05-31，约 7 年前
- **最近活跃度**：2025 年 6-9 月有 3 次实质性更新，属于**活跃维护**
- **测试覆盖**：有完整的单元测试（`AESGCMHandlerComponentTest.cpp`），覆盖 Encrypt/Decrypt/Incoming/Outgoing 四个核心场景
- **近期更新内容**：主要是底层优化和 bug 修复（缓冲区大小精确化、非对齐包处理），说明仍在被实际使用和打磨
- **平台支持**：Android、iOS、Mac、Win64、Linux、LinuxArm64 全平台覆盖
- **推荐程度**：✅ 推荐使用。作为 Epic 官方维护的网络加密组件，且有持续更新和测试保障，是 UE5 网络加密的标准方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/PacketHandlers/AESGCMHandlerComponent)
- [PacketHandler 框架](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/PacketHandlers/PacketHandler)
- [PlatformCrypto 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlatformCrypto)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/PacketHandlers/AESGCMHandlerComponent/Source/Tests/AESGCMHandlerComponentTest.cpp)

# AES Network Packet Handler

> Provides a packet handler component to do AES encryption and decryption.

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | AESHandlerComponent (Runtime) |
| 创建时间 | 2017-08-18 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/PacketHandlers/AESHandlerComponent) | |

## ⚠️ 废弃警告

**此插件自 UE 5.1 起已被标记为 `UE_DEPRECATED`。** Epic 官方推荐使用替代方案 `FAESGCMHandlerComponent`（位于 `AESGCMHandlerComponent` 插件中）。AES-GCM 模式同时提供加密和认证（AEAD），比本插件使用的 AES-256 ECB 模式安全性更高。

**ECB 模式的问题**：ECB（Electronic Codebook）对每个 16 字节块独立加密，相同的明文块会产生相同的密文块，无法隐藏数据模式。在网络加密场景中，这不是理想选择。GCM 模式通过认证标签（Authentication Tag）同时保证机密性和完整性。

## 用途

本插件实现了 UE5 网络层（`PacketHandler` 框架）中的一个加密组件，使用 AES-256 ECB 算法对网络数据包进行加密和解密。它在网络数据包的发送（Outgoing）和接收（Incoming）路径上拦截数据，自动对有效载荷进行加解密处理。

核心机制：
- **发送方向**：在数据包前写入 1 bit 加密标志位 + 终止位（用于精确恢复 bit 长度），然后用 AES-256 ECB 加密整个载荷
- **接收方向**：读取加密标志位，如已加密则提取密文并用密钥解密，通过终止位恢复原始 bit 长度
- 通过 `IPlatformCrypto` 接口委托实际的加解密操作，支持平台原生加密实现

## 使用场景

- 你需要在网络数据包层面添加基本加密保护（但注意已废弃，建议用 AESGCM）
- 你维护的是 UE 5.0 或更早版本的项目，需要网络加密能力
- 你在研究 UE 网络加密架构的历史实现

> **新项目请使用 `AESGCMHandlerComponent` 插件。**

## 蓝图用法

本插件没有暴露任何蓝图接口。`FAESHandlerComponent` 是纯 C++ 类，不继承自 `UObject`，无法在蓝图中使用。它通过 `PacketHandler` 框架在网络层自动工作，无需蓝图参与。

## C++ 用法

本插件作为 `PacketHandler` 框架的组件运行，通常由引擎网络层自动加载和管理，不需要手动编写代码。以下是其内部工作原理和可编程接口：

### 头文件引入

```cpp
#include "AESHandlerComponent.h"
```

> 注意：该头文件中的类已标记 `UE_DEPRECATED(5.1, ...)`，编译时会产生弃用警告。

### 核心类

```cpp
// AES-256 ECB 加密组件（已废弃，使用 FAESGCMHandlerComponent 替代）
class FAESHandlerComponent : public FEncryptionComponent
{
public:
    static const int32 KeySizeInBytes = 32;   // AES-256 密钥长度
    static const int32 BlockSizeInBytes = 16;  // AES 块大小

    // 设置加密密钥（必须恰好 32 字节）
    virtual void SetEncryptionData(const FEncryptionData& EncryptionData) override;

    // 启用/禁用加密
    virtual void EnableEncryption() override;
    virtual void DisableEncryption() override;
    virtual bool IsEncryptionEnabled() const override;
};
```

### 基本用法

密钥设置和加密启用流程（参考 `AESHandlerComponent.cpp`）：

```cpp
// 1. 创建实例（通常由 PacketHandler 框架自动完成）
TSharedPtr<FAESHandlerComponent> Handler = MakeShared<FAESHandlerComponent>();
Handler->Initialize();

// 2. 设置 32 字节密钥
FEncryptionData EncData;
EncData.Key.SetNum(32);
// ... 填充密钥数据 ...
Handler->SetEncryptionData(EncData);

// 3. 启用加密
Handler->EnableEncryption();

// 此后所有经过此 Handler 的出站数据包将自动加密
// 所有入站数据包将自动尝试解密
```

### 数据包处理流程

**出站（Outgoing）**：
1. 写入 1 bit 标志位（`bEncryptionEnabled ? 1 : 0`）
2. 如加密启用：追加终止位 → AES-256 ECB 加密 → 写入新数据包
3. 如加密未启用：直接复制原始数据

**入站（Incoming）**：
1. 读取 1 bit 加密标志位
2. 如已加密且密钥已设置：提取密文 → AES-256 ECB 解密 → 通过终止位恢复原始 bit 长度
3. 如密钥未设置：丢弃该数据包（可能是乱序到达）

### 预留空间

```cpp
int32 FAESHandlerComponent::GetReservedPacketBits() const
{
    // 最坏情况：加密标志位(1) + 终止位(1) + 字节对齐(最多7) + 一个加密块(128 bits)
    return 2 + 7 + (BlockSizeInBytes * 8);  // = 137 bits
}
```

## Demo 示例

本插件不提供独立的使用 Demo，因为它完全由引擎网络层通过 `PacketHandler` 框架自动管理。如果你想在自定义网络层中使用类似功能，参考实现：

```cpp
// MyCustomEncryption.h
#pragma once
#include "CoreMinimal.h"
#include "EncryptionComponent.h"

class FMyEncryptionComponent : public FEncryptionComponent
{
public:
    FMyEncryptionComponent() : FEncryptionComponent(FName(TEXT("MyEncryption"))), bEnabled(false) {}

    virtual void SetEncryptionData(const FEncryptionData& EncData) override { Key = EncData.Key; }
    virtual void EnableEncryption() override { bEnabled = true; }
    virtual void DisableEncryption() override { bEnabled = false; }
    virtual bool IsEncryptionEnabled() const override { return bEnabled; }

    // 实现 Incoming/Outgoing 中的加解密逻辑...

private:
    TArray<uint8> Key;
    bool bEnabled;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `PacketHandler` | UE 网络数据包处理器框架，提供 `HandlerComponent` 基类 |
| `PlatformCrypto` | 平台加密接口（`IPlatformCrypto`），提供跨平台 AES 加密能力 |
| `PlatformCryptoContext` | 平台加密上下文实现，执行实际的加解密运算 |

插件依赖：
| 插件 | 用途 |
|---|---|
| `PlatformCrypto` | 提供 `FEncryptionContext` 和平台加密实现 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-04-04 | `49c9e5d` | Cleanup PlatformCrypto context build complexity | 构建系统清理，将 PlatformCrypto context 模块从独立模块改为基础模块+平台扩展模式。非功能性更新。 |
| 2023-03-08 | `4ee049a` | Move Handler in to UE namespace | 命名空间重构，将 Handler 移入 `UE` 命名空间以避免第三方代码冲突。 |
| 2023-01-16 | `bbc37aa` | IWYU updates to reduce includes | 编译优化，减少头文件包含数量。 |

### 维护评价

- **创建时间**：2017 年，至今约 8.7 年，属于老古董级别
- **废弃状态**：自 UE 5.1（2022）起标记为 `UE_DEPRECATED`，类和模块均带有弃用警告
- **最近更新**：2025 年的更新仅涉及构建系统清理，非功能性改动
- **推荐使用**：❌ **不推荐**。已被 `AESGCMHandlerComponent` 完全替代。GCM 模式提供认证加密（AEAD），安全性显著优于 ECB 模式
- **注意**：虽然默认未启用（`EnabledByDefault: false`），但仍保留在引擎中以保持向后兼容

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/PacketHandlers/AESHandlerComponent)
- [替代方案: AESGCMHandlerComponent](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/PacketHandlers/AESGCMHandlerComponent)

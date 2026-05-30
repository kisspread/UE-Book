# AES Handler Component

> Provides a packet handler component to do AES encryption and decryption.

| 属性 | 值 |
|---|---|
| 中文名 | AES网络数据包处理器 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AESHandlerComponent` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-18 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PacketHandlers/AESHandlerComponent) | |

## 用途

AESHandlerComponent 是一个网络数据包处理组件（Packet Handler Component），其主要功能是对游戏网络流量进行 AES 加密和解密。它通常与 `PlatformCrypto` 插件和引擎内置的网络加密握手流程配合使用。通过网络连接时的 `NMT_Hello` 消息交换 `EncryptionToken` 来协商加密密钥，然后使用 AES-256 算法加密后续所有收发的数据包，以保障网络通信安全，防止数据被窃听或篡改。

**重要提示**：根据源码中的 `UE_DEPRECATED` 标记，此组件在 UE 5.1 版本后已被标记为废弃（Deprecated），官方建议使用其后续版本 `FAESGCMHandlerComponent`。

## 使用场景

- 你需要在多人在线游戏中对客户端与服务器之间的网络数据包进行加密。
- 你的游戏类型是FPS、MOBA等竞技类游戏，对网络安全性有较高要求，需要防止简单的抓包作弊。
- 你希望使用引擎内置的、经过验证的加密方案来保护游戏网络通信。

## 蓝图用法

该插件主要为引擎底层网络系统提供加密组件，**没有直接暴露给蓝图的接口**。加密功能的启用和配置需要在 C++ 层通过引擎的网络管理类（如 `UNetDriver`）和配置控制台变量（CVar）来完成。

## C++ 用法

### 头文件引入

```cpp
#include "AESHandlerComponent.h"
```

### 基本用法

以下示例展示了如何在自定义网络模块中创建并配置一个 AES 加密处理器。该代码展示了组件的核心生命周期：创建实例、设置密钥、启用加密。

```cpp
// 基于 Public/AESHandlerComponent.h 中的类定义
// 通常由引擎内部的 PacketHandler 系统管理，但以下代码展示了手动使用的逻辑

// 1. 创建加密处理器实例
FAESHandlerComponent* AESHandler = new FAESHandlerComponent();

// 2. 准备32字节的AES-256密钥（示例，实际应通过安全握手获取）
TArray<uint8> SharedSecretKey;
SharedSecretKey.SetNumZeroed(FAESHandlerComponent::KeySizeInBytes); // 32字节
// ... 从 EncryptionToken 等来源填充实际密钥数据 ...

// 3. 设置加密密钥
FEncryptionData EncryptionData;
EncryptionData.EncryptionKey = SharedSecretKey;
AESHandler->SetEncryptionData(EncryptionData);

// 4. 启用加密（开始加密 outgoing 数据包）
if (AESHandler->IsValid())
{
    AESHandler->EnableEncryption();
}

// 5. 将处理器注册到网络连接或数据包处理链中（具体步骤取决于引擎版本和上下文）
// 此过程通常由引擎的 FPacketHandler 在连接建立时自动完成。
```

### 进阶用法：自定义网络加密流程

在更复杂的场景中，你可能需要参与加密握手过程。以下代码片段展示了如何监听 `NMT_Hello` 消息以获取 `EncryptionToken`，并使用它来配置加密组件。

```cpp
// 在自定义的 UNetConnection 或相关网络逻辑中
void UMyNetConnection::HandleHelloMessage(FBunch& Bunch)
{
    // 读取消息类型
    uint8 MessageType;
    Bunch << MessageType;

    if (MessageType == NMT_Hello)
    {
        // 尝试读取加密令牌
        bool bHasEncryptionToken = false;
        Bunch.SerializeBits(&bHasEncryptionToken, 1);

        if (bHasEncryptionToken)
        {
            FEncryptionToken Token;
            Bunch << Token;

            // 使用令牌派生出共享密钥（派生逻辑需自定义实现）
            TArray<uint8> DerivedKey = DeriveKeyFromToken(Token);

            // 创建并配置加密组件
            FAESHandlerComponent* EncryptionComp = new FAESHandlerComponent();
            FEncryptionData EncData;
            EncData.EncryptionKey = DerivedKey;
            EncryptionComp->SetEncryptionData(EncData);

            // 将组件设置到当前连接的 PacketHandler 中
            // (PacketHandler 具体访问方式需参考引擎版本)
            GetPacketHandler()->SetEncryptionComponent(TSharedPtr<FEncryptionComponent>(EncryptionComp));
            EncryptionComp->EnableEncryption();
        }
    }
}
```

**注意**：`DeriveKeyFromToken` 函数需要根据游戏的具体安全协议实现，通常涉及密钥交换算法（如 ECDH）。

## Demo 示例

一个可编译的、展示如何从零开始集成 `FAESHandlerComponent` 的最小化模块示例。

### MyNetSecurityModule.h

```cpp
// MyNetSecurityModule.h
#pragma once

#include "Modules/ModuleManager.h"
#include "AESHandlerComponent.h"

class FMyNetSecurityModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    /** 创建一个配置好的 AES 加密处理器 */
    static TSharedPtr<FAESHandlerComponent> CreateConfiguredAESHandler(const TArray<uint8>& SharedKey);

private:
    // 可以持有对当前活跃加密组件的引用
    TSharedPtr<FAESHandlerComponent> ActiveEncryptionComponent;
};
```

### MyNetSecurityModule.cpp

```cpp
// MyNetSecurityModule.cpp
#include "MyNetSecurityModule.h"
#include "HAL/PlatformProcess.h"

#define LOCTEXT_NAMESPACE "FMyNetSecurityModule"

void FMyNetSecurityModule::StartupModule()
{
    UE_LOG(LogTemp, Log, TEXT("MyNetSecurityModule 启动。"));
}

void FMyNetSecurityModule::ShutdownModule()
{
    ActiveEncryptionComponent.Reset();
    UE_LOG(LogTemp, Log, TEXT("MyNetSecurityModule 关闭。"));
}

TSharedPtr<FAESHandlerComponent> FMyNetSecurityModule::CreateConfiguredAESHandler(const TArray<uint8>& SharedKey)
{
    // 检查密钥长度是否符合 AES-256 要求
    if (SharedKey.Num() != FAESHandlerComponent::KeySizeInBytes)
    {
        UE_LOG(LogTemp, Error, TEXT("创建 AES Handler 失败：密钥长度必须为 %d 字节。"), FAESHandlerComponent::KeySizeInBytes);
        return nullptr;
    }

    // 创建实例
    TSharedPtr<FAESHandlerComponent> Handler = MakeShareable(new FAESHandlerComponent());

    // 配置密钥
    FEncryptionData EncData;
    EncData.EncryptionKey = SharedKey;
    Handler->SetEncryptionData(EncData);

    // 检查组件是否有效（例如，底层加密上下文是否初始化成功）
    if (!Handler->IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("AES Handler 创建后验证失败。"));
        return nullptr;
    }

    // 启用加密
    Handler->EnableEncryption();
    UE_LOG(LogTemp, Log, TEXT("成功创建并启用 AES 加密处理器。"));

    return Handler;
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyNetSecurityModule, MyNetSecurity)
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了日志输出中64位整数的格式说明符错误。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2025-04-04 | `49c9e5de` | Cleanup PlatformCrypto context build complexity. This fixes some incorrect explicit dependencies on... | 清理了 PlatformCrypto 上下文构建的复杂性，修复了一些错误的显式依赖。 |
| 2023-03-08 | `4ee049a2` | Move Handler in to UE namespace to avoid name collisions with third party code | 将处理器移入 UE 命名空间以避免与第三方代码冲突。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 插件目录下的通用提交，具体信息不明。 |

### 维护评价

⚠️ **不推荐使用（已废弃）**

该插件在 UE 5.1 版本中被官方标记为 `UE_DEPRECATED`，明确提示应使用 `FAESGCMHandlerComponent` 替代。最近的几次提交（如2026年）主要是编译修复和代码迁移（如命名空间调整、日志宏迁移），并非功能性更新或安全增强。最后一次与加密逻辑本身相关的实质性更新可能在2023年之前。

**结论**：这是一个处于“维护状态”但功能上已被取代的遗留组件。对于新项目，应直接研究和使用 `AESGCMHandlerComponent`。在维护旧项目时，如果遇到加密相关问题，可以参考此组件的代码，但迁移到新组件是更安全、更未来的选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PacketHandlers/AESHandlerComponent)
- [官方文档]（无）
- [测试用例]（引擎内部网络测试中可能包含，路径通常位于 `Engine/Tests/` 下）
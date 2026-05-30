# AES GCM network packet handler

> Provides a packet handler component to do AES GCM encryption and decryption.

| 属性 | 值 |
|---|---|
| 中文名 | AES GCM 网络数据包处理器 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AESGCMHandlerComponent` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-05-31 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PacketHandlers/AESGCMHandlerComponent) | |

## 用途

该插件是一个用于 Unreal 网络子系统的**数据包处理器组件**，其核心功能是为网络数据包提供 **AES 256 GCM (Galois/Counter Mode)** 加密和解密能力。它并非独立运行的插件，而是被集成到 UE 的 **Packet Handler** 管线中，在数据包发送和接收时自动执行加密操作，从而保障客户端与服务器之间网络通信的安全性，防止数据被窃听或篡改。它主要解决多人在线游戏或任何需要安全网络连接的场景中，对网络流量进行加密的需求。

## 使用场景

- 你正在开发一款多人在线竞技游戏（如射击、MOBA），需要防止玩家通过抓包工具窃取或分析网络通信内容以实施作弊。
- 你的游戏涉及敏感数据传输（如玩家账户信息、游戏内交易），需要在客户端和服务器之间建立安全的通信通道。
- 你需要遵循特定的网络安全协议，该协议要求使用 AES-GCM 这种认证加密算法。

## 蓝图用法

此插件主要作为底层的网络组件运行，**没有直接暴露给蓝图的节点**。其加密行为由引擎的网络系统在后台管理，蓝图开发者通常通过配置 `NetDriver` 或连接选项来启用它，而不是直接在蓝图图表中操作其加密/解密函数。具体的启用方式属于引擎网络配置范畴，超出了此插件自身的蓝图 API。

## C++ 用法

该插件的核心用法是通过 C++ 代码设置加密密钥并将其作为数据包处理器集成到网络连接中。

### 头文件引入

```cpp
#include "AESGCMHandlerComponent.h"
```

### 基本用法

以下代码展示了如何实例化并配置 AES GCM 处理器组件。关键步骤是设置符合长度的加密密钥。

```cpp
// 假设你已经获取了一个 TSharedPtr<FAESGCMHandlerComponent> 实例
// 实例通常由引擎的 PacketHandler 系统管理，或通过模块接口创建。

// 1. 设置加密数据（密钥）
FEncryptionData EncryptionData;
EncryptionData.Key.SetNum(FAESGCMHandlerComponent::KeySizeInBytes); // 密钥必须是32字节
// 从安全来源（如服务器握手）填充密钥数据到 EncryptionData.Key
// ... 填充密钥逻辑 ...
HandlerComponent->SetEncryptionData(EncryptionData);

// 2. 启用加密
HandlerComponent->EnableEncryption();

// 此后，通过此连接发出的所有数据包都将被自动加密。
```

*来源文件: `AESGCMHandlerComponent.h`*

### 进阶用法：错误处理

该插件定义了详细的错误类型 (`EAESGCMNetResult`) 用于诊断加密/解密失败的原因。在网络连接出现故障时，可以检查这些结果。

```cpp
// EAESGCMNetResult 定义了诸如以下可能的错误：
// - AESMissingIV: 收到的数据包缺少初始化向量 (IV)
// - AESMissingAuthTag: 缺少认证标签
// - AESDecryptionFailed: 解密失败（密钥错误、数据损坏等）
// - AESZeroLastByte: 数据包结构异常
```

*来源文件: `AESGCMFaultHandler.h`*

## Demo 示例

此插件并非独立使用，而是作为 UE 网络栈的一部分。一个完整的“使用示例”涉及设置一个使用此加密处理器的网络连接，这通常在游戏的网络初始化代码中完成，而非一个独立的、可编译的 .cpp 文件。核心操作如上方“C++ 用法”所示。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PlatformCrypto` | 提供跨平台的加密/解密原语实现（AES、GCM 等）。 |
| `CommonUI` | （在 Build.cs 中可见）可能用于某些依赖链，但非核心加密功能所需。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了日志格式说明符在不同位宽下的匹配问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至新的 `UE_LOGF` 格式。 |
| 2025-11-21 | `f97662ab` | Iris Parallelization - Added API for network HandlerComponents to indicate support for being run in | 为支持并行化网络处理添加了API接口声明。 |
| 2025-11-20 | `bb770c94` | [Backout] - CL48503168 - CIS Compile Warning | 回退了之前可能导致编译警告的更改。 |
| 2025-11-20 | `14c2335d` | Iris Parallelization - Added API for network HandlerComponents to indicate support for being run in | 同上，为网络数据包处理器添加并行化支持API。 |

### 维护评价

该插件创建于 2019 年，是一个相对成熟的组件。从近期提交记录看，其主要改动集中在 2025 年底至 2026 年初，内容以**维护性更新**为主（日志格式迁移、编译警告修复）以及对引擎新特性（Iris 网络并行化）的适配支持，**并未发现近期有功能性的重大增强或安全算法的更新**。它作为网络基础设施的一部分，仍被引擎维护以确保兼容性，但开发活跃度较低。考虑到 AES-GCM 本身是成熟的算法，且插件功能明确，目前状态属于**维护不活跃但功能稳定**，适用于需要此特定加密方式的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PacketHandlers/AESGCMHandlerComponent)
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

PlatformCrypto 插件为 Unreal Engine 提供了一层**平台无关的加密抽象接口**。其核心目标是：让游戏代码无需关心底层加密库的实现细节，统一使用相同的 API 进行加解密操作。

插件优先使用**平台原生加密库**（如 Xbox One 的 BCrypt/CNG），在没有原生支持时自动回退到 **OpenSSL**。这在多人游戏中尤为重要——网络数据包可以通过 AES 加密保护传输安全，同时支持网络握手阶段的加密密钥交换（EncryptionToken）。近期版本还新增了 ED25519 密钥对生成及签名验证功能。

## 模块总览

| 模块 | 类型 | 说明 |
|---|---|---|
| `PlatformCrypto` | Runtime | 核心 API 层，定义加解密的抽象接口（如加密组件、对称/非对称加密接口） |
| `PlatformCryptoTypes` | Runtime | 加密相关类型定义，包括密钥、向量、签名等数据结构 |
| `PlatformCryptoContext` | Runtime | 加密上下文管理，封装加解密操作的状态和生命周期 |
| `PlatformCryptoOpenSSL` | External | OpenSSL 后端实现，已被标记为 deprecated，建议迁移到新的统一接口 |

## 使用场景

- 你正在开发多人在线游戏，需要加密网络流量 → 使用 `AESHandlerComponent` 通过 PacketHandler 自动加密数据包
- 你需要在网络握手阶段协商加密密钥 → 利用 `EncryptionToken` 机制在 NMT_Hello 中交换密钥信息
- 你需要进行非对称加密操作（如密钥对生成、签名验证） → 使用 `PlatformCrypto` 的 ED25519/密钥交换接口
- 你需要在不同平台（PC / Xbox / 主机）上使用统一的加密 API → PlatformCrypto 会自动选择平台最优实现
- 你需要测试加密功能但不想复杂配置 → 使用 `net.AllowEncryption` CVar 启用，或在 ShooterGame 中设置 `ShooterGame.TestEncryption=1`

## 模块文档

- [PlatformCrypto](PlatformCrypto.md) — 核心加密接口与组件
- [PlatformCryptoContext](PlatformCryptoContext.md) — 加密上下文管理
- [PlatformCryptoOpenSSL](PlatformCryptoOpenSSL.md) — OpenSSL 后端（已废弃）
- [PlatformCryptoTypes](PlatformCryptoTypes.md) — 加密类型定义

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlatformCrypto)
- 官方文档：无
- [PlatformCrypto 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlatformCrypto/Source/PlatformCrypto)
- [PlatformCryptoTypes 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlatformCrypto/Source/PlatformCryptoTypes)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式化说明符匹配问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 日志宏迁移到新的 UE_LOGF 格式 |
| 2026-02-26 | `37eb983a` | Add ED25519 key pair generation and sign/verify support to Engine/PlatformCrypto | 新增 ED25519 密钥对生成及签名验证功能 |
| 2025-06-18 | `082c27ae` | Clean up AES GCM PacketHandler code to have buffers with exactly MAX_PACKET_SIZE size | 清理 AES GCM 缓冲区大小使其精确匹配 MAX_PACKET_SIZE |
| 2025-05-16 | `97c9876a` | Add deprecated PlatformCryptoOpenSSL module to warn licensees of the module's replacement | 为 OpenSSL 模块添加废弃警告提示授权用户迁移到新接口 |

### 维护评价

**活跃维护中。** 插件创建于 2017 年，至今约 9 年历史，但近期（2025-2026）仍有持续功能性更新：新增了 ED25519 非对称加密支持，标记了旧的 OpenSSL 模块为 deprecated 并引导迁移到统一接口，还有编译修复和代码清理。

需要注意：
- `PlatformCryptoOpenSSL` 模块已被标记为 **deprecated**，不再推荐使用，新的加密后端已整合到核心模块中
- 插件路径仍在 `Experimental/` 下，但实际已被引擎核心网络加密功能依赖，属于"名为实验、实际必不可少"的状态
- **推荐使用**：对于需要平台加密能力的多人游戏项目，这是引擎官方推荐的加密抽象层
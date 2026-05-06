# Platform Cryptography Plugin

> Exposes a unified API for cryptography functionality provided by the platform, if available. Otherwise, interfaces with OpenSSL.

| 属性 | 值 |
|---|---|
| 中文名 | 平台加密 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PlatformCrypto` (Runtime), `PlatformCryptoContext` (Runtime), `PlatformCryptoOpenSSL` (External), `PlatformCryptoTypes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-11-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlatformCrypto) | |

## 总体用途

PlatformCrypto 提供了一套统一的密码学接口，允许上层代码以平台无关的方式使用加密功能。当目标平台提供了原生加密 API（如 iOS/macOS 的 CommonCrypto、Windows 的 BCrypt 等）时，插件会优先调用平台实现；否则自动回退到 OpenSSL。该插件解决了跨平台加密方案的碎片化问题，开发者无需为每个平台编写条件化加密代码。

## 模块列表

每个模块的详细 API 请参见对应子文档。

- **[PlatformCrypto](PlatformCrypto.md)** (Runtime)：插件入口与工厂类，负责创建加密上下文和选择底层实现（平台原生或 OpenSSL）。
- **[PlatformCryptoContext](PlatformCryptoContext.md)** (Runtime)：加密上下文，提供对称加密（AES）、哈希（SHA256）、HMAC 等操作的具体执行环境。
- **[PlatformCryptoOpenSSL](PlatformCryptoOpenSSL.md)** (External)：OpenSSL 后端实现，当平台无原生加密时自动启用，已标记为 deprecated，新代码应使用 `PlatformCrypto` 模块。
- **[PlatformCryptoTypes](PlatformCryptoTypes.md)** (Runtime)：公共类型定义，包括加密枚举（如加密算法、填充模式）、结果结构体、错误码等，被其他模块共享。

## 使用场景

- 你需要对网络数据包进行对称加密（AES-GCM / AES-CBC），且希望代码在 Windows、Mac、iOS、Android 上一致工作。
- 你需要计算文件或消息的哈希值（SHA-256 / SHA-1），并避免手动链接 OpenSSL 库。
- 你正在实现自定义 PacketHandler 或网络传输层加密，需要可互换的后端（平台原生 / OpenSSL）。
- 你希望未来平台新增原生加密时，代码无需修改即可受益。

## 相关链接

- [源码主目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlatformCrypto)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlatformCrypto/Tests)（如有）
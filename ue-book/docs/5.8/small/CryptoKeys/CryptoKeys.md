# CryptoKeys

> 

| 属性 | 值 |
|---|---|
| 中文名 | 加密密钥 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `CryptoKeys` (Editor), `CryptoKeysOpenSSL` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-12-12 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/CryptoKeys) | |

## 用途

CryptoKeys 是一个**打包安全工具插件**，用于在 Unreal 项目打包阶段对 `.pak` 文件进行 AES 加密和 RSA 签名保护。

它解决的核心问题是：**防止玩家通过解包工具（如 UnrealPak）直接提取游戏资产内容，以及防止 pak 文件被篡改后分发**。插件提供了完整的密钥管理流程——生成、存储、配置加密/签名策略——全部通过编辑器设置面板和命令行工具完成。

与引擎内置的 `Crypto.json` 配置系统不同，CryptoKeys 将密钥管理集中到一个可编辑的 Settings 对象中（存储在 `Crypto.ini`），并支持：

- **AES 对称加密**：可选择加密 ini 文件、pak 索引、uasset 文件头或所有资产
- **RSA 非对称签名**：对 pak 文件进行数字签名，在加载时验证完整性
- **多密钥体系**：主密钥 + 可命名的次级加密密钥，用于按资产粒度选择不同密钥

## 使用场景

- 你在打包单机游戏，希望防止资源被逆向提取 → 使用 AES 加密 ini/索引/资产
- 你在做多人在线游戏，需要确保客户端 pak 文件未被篡改 → 启用 RSA 签名
- 你有多个子项目需要使用不同的加密密钥 → 配置多个次级加密密钥并按名称引用
- 你使用 CI/CD 流水线打包，需要命令行管理密钥 → 使用 `CryptoKeysCommandlet`

## 蓝图用法

此插件**没有暴露任何蓝图接口**。所有功能通过编辑器设置面板和命令行工具使用。

### 配置入口

在编辑器中通过以下路径访问：

**Project Settings → Crypto**（或直接编辑 `Crypto.ini`）

### 设置面板功能

| 设置项 | 说明 |
|---|---|
| EncryptionKey | 主 AES 加密密钥（Base64 编码的 32 字节密钥） |
| SecondaryEncryptionKeys | 次级加密密钥数组，每项包含 GUID、名称和密钥 |
| bEncryptPakIniFiles | 加密 pak 内的 ini 文件 |
| bEncryptPakIndex | 加密 pak 索引，阻止 UnrealPak 无密钥访问 |
| bEncryptUAssetFiles | 加密 uasset 文件头（包含包头和字符串数据） |
| bEncryptAllAssetFiles | 加密 pak 内所有文件（安全但影响运行时 IO 性能和补丁效率） |
| bEnablePakSigning | 启用 pak 文件 RSA 签名 |
| SigningPublicExponent | RSA 公钥指数 |
| SigningModulus | RSA 模数 |
| SigningPrivateExponent | RSA 私钥指数 |

### 设置面板自定义按钮

通过 `FCryptoKeysSettingsDetails` 自定义详情面板，提供以下操作按钮：

- **Generate Encryption Key** — 生成新的 AES 加密密钥
- **Generate Signing Keys** — 生成新的 RSA 4096 位签名密钥对
- **Cycle Key** — 为当前密钥生成新值（用于密钥轮换）

## C++ 用法

### 头文件引入

```cpp
#include "CryptoKeys.h"
```

### 基本用法 — 生成 AES 加密密钥

使用公共 API 生成加密密钥：

```cpp
// 来源: Public/CryptoKeys.h
FString OutBase64Key;
CryptoKeys::GenerateEncryptionKey(OutBase64Key);

// OutBase64Key 现在包含 Base64 编码的 32 字节 AES 密钥
// 可用于注入到 CryptoKeysSettings 或 Crypto.json
```

### 进阶用法 — 使用 OpenSSL 辅助函数生成 RSA 签名密钥

如果链接了 `CryptoKeysOpenSSL` 模块，可以使用底层辅助函数：

```cpp
// 来源: Private/CryptoKeysHelpers.h
#include "CryptoKeysHelpers.h"

FString PublicExponent, PrivateExponent, Modulus;

// 生成 4096 位 RSA 密钥对
bool bSuccess = CryptoKeysHelpers::GenerateSigningKey(
    PublicExponent,     // Base64 编码的 RSA 公钥指数
    PrivateExponent,    // Base64 编码的 RSA 私钥指数
    Modulus,            // Base64 编码的 RSA 模数
    4096                // 密钥位数（默认 4096）
);
```

### 进阶用法 — 读取和修改加密设置

```cpp
// 来源: Classes/CryptoKeysSettings.h
#include "CryptoKeysSettings.h"

// 获取 Settings 对象
const UCryptoKeysSettings* Settings = GetDefault<UCryptoKeysSettings>();

// 检查加密和签名状态
bool bEncryptionEnabled = Settings->IsEncryptionEnabled();
bool bSigningEnabled = Settings->IsSigningEnabled();

// 检查具体加密粒度
bool bIniEncrypted = Settings->bEncryptPakIniFiles;
bool bAllEncrypted = Settings->bEncryptAllAssetFiles;
```

### 命令行用法

通过 Commandlet 在 CI/CD 中管理密钥：

```bash
# 运行 CryptoKeys 命令行工具
UnrealEditor-Cmd.exe YourProject -run=CryptoKeys
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OpenSSL` | RSA 密钥生成和签名操作（通过 `CryptoKeysOpenSSL` 模块间接依赖） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式 |
| 2025-05-31 | `8396b185` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 修复 DLL 导出符号声明 |
| 2024-10-22 | `98a8e0e0` | Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 清理 5.2 版本弃用的头文件包含顺序宏 |
| 2024-09-24 | `0136afdc` | Fixed another instance of the bad saving method for Defaults | 修复设置保存方式的又一个问题 |
| 2024-09-24 | `77b27f1c` | Fixed an issue with Clearing Encryption Key wasn't saving, as it was using a hacky way to save to | 修复清除加密密钥后不保存的 Bug |

### 维护评价

CryptoKeys 自 2017 年随 UE4 4.18 引入以来一直保持默认启用状态，是引擎打包安全基础设施的一部分。近年来的更新主要集中在：

1. **代码现代化**（日志宏迁移、头文件清理、DLL 导出修复），属于维护性改动
2. **Bug 修复**（设置保存问题），说明该功能仍在被实际使用

虽然最近没有功能性的大更新，但核心逻辑稳定，不需要频繁修改。作为 Epic 官方维护的编辑器基础设施插件，**推荐使用**。如果你需要保护打包资产免受逆向提取或篡改，CryptoKeys 是官方唯一推荐的解决方案。

⚠️ 注意：此插件仅在编辑器中运行（模块类型为 Editor），不会增加最终打包体积。加密和签名逻辑在打包阶段由 UnrealPak 和引擎运行时的 pak 文件系统处理。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/CryptoKeys)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/CryptoKeys)（如果存在）
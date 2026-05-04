# CryptoKeys

> 为 Pak 文件提供加密（AES）和签名（RSA）密钥的生成与管理界面。

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | CryptoKeys (Editor), CryptoKeysOpenSSL (Editor) |
| 创建时间 | 2017-12-12 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/CryptoKeys) | |

## 用途

CryptoKeys 是一个纯编辑器插件，解决 Pak 文件的安全问题。它提供两层保护：

1. **加密（Encryption）**：使用 AES-256 对 Pak 中的资产进行加密，防止数据被直接提取。支持四种粒度——加密 INI 配置文件、Pak 索引、uasset 文件头、或全部文件。
2. **签名（Signing）**：使用 RSA-4096 对 Pak 文件进行签名，防止数据被篡改。运行时引擎会验证签名完整性。

插件本身不执行打包时的加密操作——那是 UnrealPak 和引擎打包管线的工作。CryptoKeys 的职责是**管理密钥配置**并提供**密钥生成能力**，这些密钥会被写入项目的 `Crypto.json` 配置文件，供打包和运行时流程使用。

## 使用场景

- 你需要防止玩家通过解包工具提取游戏资产 → 启用 Pak 加密
- 你需要防止 Pak 文件被第三方篡改（防作弊/防修改） → 启用 Pak 签名
- 你需要为不同资产使用不同的加密密钥（如 DLC 分包） → 配置 Secondary Encryption Keys
- 你需要在 CI/CD 流水线中自动轮换加密密钥 → 使用 CryptoKeys Commandlet

## 编辑器用法

### 设置面板

在编辑器中通过 **Project Settings → Project → Encryption** 访问。面板分为两个区域：

#### Encryption 区域

| 设置 | 说明 |
|---|---|
| Encryption Key | 主加密密钥（Base64 编码），通过按钮生成或清除 |
| Secondary Encryption Keys | 辅助密钥列表，每个条目包含 GUID、名称和密钥。添加新条目时自动生成密钥 |
| Encrypt Pak Ini Files | 加密 Pak 中的 INI 文件（低性能开销，保护常见配置泄露） |
| Encrypt Pak Index | 加密 Pak 索引，使 UnrealPak 无法在无密钥情况下操作 Pak |
| Encrypt UAsset Files | 加密 uasset 文件头（保护包头信息和字符串数据） |
| Encrypt All Asset Files | 加密 Pak 中所有文件（最安全，但影响 IO 性能和增量更新效率） |

#### Signing 区域

| 设置 | 说明 |
|---|---|
| Generate New Signing Keys | 按钮，生成 RSA-4096 签名密钥对（公钥指数、私钥指数、模数） |
| Enable Pak Signing | 启用后，打包时会对 Pak 进行签名 |

## C++ 用法

### 头文件引入

```cpp
#include "CryptoKeys/Public/CryptoKeys.h"       // 公共 API
#include "CryptoKeys/Private/CryptoKeysHelpers.h" // 内部辅助（仅限模块内部使用）
```

### 基本用法 — 生成加密密钥

```cpp
#include "CryptoKeys/Public/CryptoKeys.h"

FString Base64Key;
CryptoKeys::GenerateEncryptionKey(Base64Key);
// Base64Key 现在包含一个 Base64 编码的 AES-256 密钥
```

来源：`Source/CryptoKeys/Public/CryptoKeys.h`、`Source/CryptoKeys/Private/CryptoKeys.cpp`

### 使用 CryptoKeysHelpers（模块内部）

```cpp
#include "CryptoKeysHelpers.h"

// 生成 AES 加密密钥
FString EncryptionKey;
bool bSuccess = CryptoKeysHelpers::GenerateEncryptionKey(EncryptionKey);

// 生成 RSA 签名密钥对（默认 4096 位）
FString PublicExponent, PrivateExponent, Modulus;
bool bSigned = CryptoKeysHelpers::GenerateSigningKey(
    PublicExponent, PrivateExponent, Modulus, 4096
);
// 所有输出均为 Base64 编码
```

来源：`Source/CryptoKeys/Private/CryptoKeysHelpers.h`

### 使用 OpenSSL 底层 API

```cpp
#include "CryptoKeysOpenSSL/Public/CryptoKeysOpenSSL.h"

// 生成原始字节格式的 AES 密钥（32 字节）
TArray<uint8> RawKey;
CryptoKeysOpenSSL::GenerateNewEncryptionKey(RawKey);

// 生成原始字节格式的 RSA 签名密钥
TArray<uint8> PubExp, PrivExp, Modulus;
CryptoKeysOpenSSL::GenerateNewSigningKey(PubExp, PrivExp, Modulus, 2048);
```

来源：`Source/CryptoKeysOpenSSL/Public/CryptoKeysOpenSSL.h`

### Commandlet 用法（CI/CD）

通过命令行调用 `CryptoKeys` Commandlet 自动化密钥管理：

```bash
# 更新加密密钥
UnrealEditor-Cmd.exe ProjectName -run=CryptoKeys -updateencryptionkey

# 更新签名密钥
UnrealEditor-Cmd.exe ProjectName -run=CryptoKeys -updatesigningkey

# 同时更新所有密钥
UnrealEditor-Cmd.exe ProjectName -run=CryptoKeys -updateallkeys

# 测试签名密钥生成的唯一性（压力测试）
UnrealEditor-Cmd.exe ProjectName -run=CryptoKeys -testsigningkeygen
```

来源：`Source/CryptoKeys/Private/CryptoKeysCommandlet.cpp`

## Demo 示例

### 最小集成：在自定义编辑器工具中生成加密密钥

```cpp
// MyCryptoTool.h
#pragma once
#include "CoreMinimal.h"

class FMyCryptoTool
{
public:
    static void GenerateAndSaveKey()
    {
        FString Key;
        CryptoKeys::GenerateEncryptionKey(Key);
        
        // 保存到项目配置
        GConfig->SetString(
            TEXT("/Script/CryptoKeys.CryptoKeysSettings"),
            TEXT("EncryptionKey"),
            *Key,
            GGameIni
        );
        GConfig->Flush(false, GGameIni);
        
        UE_LOG(LogTemp, Display, TEXT("Generated encryption key: %s"), *Key);
    }
};
```

依赖：在 `Build.cs` 中添加 `CryptoKeys` 到 `PrivateDependencyModuleNames`。

> **注意**：CryptoKeys 模块类型为 `Editor`，只能在编辑器环境下使用，不能在运行时（Runtime）调用。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、Base64 编码 |
| `CoreUObject` | UObject 系统（设置类继承） |
| `Engine` | 引擎核心 |
| `UnrealEd` | 编辑器框架、Settings 注册 |
| `Slate` / `SlateCore` | UI 按钮（Generate/Clear） |
| `CryptoKeysOpenSSL` | OpenSSL 封装，实际密钥生成 |
| `GameProjectGeneration` | 项目构建相关 |
| `DeveloperToolSettings` | 开发者工具设置 |
| `OpenSSL`（第三方） | RSA/AES 密码学运算 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-05-30 | `8396b18` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 2/n | 编译器兼容性修复，将 DLL export 标记从类型移到方法/静态变量上。纯维护性改动。 |
| 2024-10-22 | `98a8e0e` | Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 清理 UE 5.2 弃用的 include 顺序兼容宏。代码清理。 |
| 2024-09-24 | `0136afd` | Fixed another instance of the bad saving method for Defaults | 修复设置保存方法的一个 bug。功能性修复。 |

### 维护评价

- **年龄**：创建于 2017-12-12，已存在约 8 年
- **最近更新**：最近一次实质性功能修复在 2024-09-24，其余为编译兼容性维护
- **维护频率**：低频维护，但仍在持续跟随引擎大版本更新
- **稳定性**：功能已经非常成熟，无需频繁改动。密钥生成、配置管理、UI 交互均已稳定
- **已知限制**：
  - 仅支持 Mac、Win64、Linux 平台
  - Editor 模块，不能在运行时使用
  - `SecondaryEncryptionKeys` 中的密钥需要在运行时由游戏代码手动提供给 Pak 平台文件层
  - 加密所有文件会显著影响 IO 性能和增量更新（patching）效率
- **推荐**：✅ 推荐使用。这是 Epic 官方的加密密钥管理方案，功能稳定，适合所有需要 Pak 安全保护的项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/CryptoKeys)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/CryptoKeys)（未发现独立测试文件）

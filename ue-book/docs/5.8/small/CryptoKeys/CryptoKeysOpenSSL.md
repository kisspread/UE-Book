# CryptoKeys

> （描述字段为空，基于源码分析）

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

`CryptoKeys` 是一个**编辑器插件**，主要解决游戏资产和Pak文件在打包、分发和运行时过程中的**安全保护**问题。它提供了统一的图形化界面来管理AES加密密钥和RSA签名密钥，并将这些密钥的设置与引擎的打包流程深度集成。

**它为什么存在？** 在没有此插件前，开发者需要手动修改加密配置文件（如 `Crypto.json` 和 `CryptoKeys.ini`）来设置加密和签名，这个过程繁琐且容易出错。`CryptoKeys` 插件将这些操作封装为易于使用的编辑器工具，并能自动将设置应用于打包流程（如通过 `UnrealPak`），确保了密钥管理的正确性和便捷性。其核心目的是在项目发布前，为游戏资产（`.uasset`）和最终的Pak文件提供可靠的加密和签名支持。

## 使用场景

-   你正在开发一款需要发布到商业平台（如Epic Games Store， Steam）的游戏，需要防止资源文件被直接提取和查看。
-   你为游戏开发了DLC或在线内容，需要确保资源包（.pak）的完整性和来源可信，防止被篡改。
-   你需要在团队中安全地管理和传递项目加密密钥，避免密钥硬编码在源码或配置文件中。
-   你在打包过程中希望自动应用统一的加密策略，而不是手动编辑多个配置文件。

## 蓝图用法

此插件主要提供编辑器工具界面，其核心功能通过编辑器菜单（Project Settings -> Crypto Keys）暴露。可编程的API相对有限，主要用于密钥生成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GenerateNewEncryptionKey` | 生成一个新的随机 AES 加密密钥（32字节）。 | `CryptoKeysOpenSSL` (命名空间) |
| `GenerateNewSigningKey` | 生成一对新的 RSA 签名密钥（公钥、私钥、模数），默认为2048位。 | `CryptoKeysOpenSSL` (命名空间) |

### 使用示例（蓝图描述）

这些函数通常在编辑器工具蓝图或编辑器工具插件中被调用，用于自动化生成密钥，而非在游戏运行时蓝图中调用。一个可能的用法是在一个“生成项目密钥”的编辑器工具按钮点击事件中，调用这两个函数，并将返回的密钥数据（`TArray<uint8>`）保存到项目的 `Crypto.json` 文件中。

## C++ 用法

插件的核心API由 `CryptoKeysOpenSSL` 模块提供，主要用于生成密钥。

### 头文件引入

```cpp
#include “CryptoKeysOpenSSL/CryptoKeysOpenSSL.h“
```

### 基本用法

**生成加密和签名密钥**（来源：`CryptoKeysOpenSSL.h`）

```cpp
#include “CryptoKeysOpenSSL/CryptoKeysOpenSSL.h”

void GenerateProjectKeys()
{
    // 1. 生成AES加密密钥
    TArray<uint8> EncryptionKey;
    if (CryptoKeysOpenSSL::GenerateNewEncryptionKey(EncryptionKey))
    {
        // 可以将 EncryptionKey 保存到配置文件
        UE_LOG(LogTemp, Log, TEXT(“Successfully generated a new AES encryption key.”));
    }

    // 2. 生成RSA签名密钥对
    TArray<uint8> PublicExponent, PrivateExponent, Modulus;
    if (CryptoKeysOpenSSL::GenerateNewSigningKey(PublicExponent, PrivateExponent, Modulus))
    {
        // 可以将签名密钥的三个部分分别保存到配置文件
        UE_LOG(LogTemp, Log, TEXT(“Successfully generated a new RSA signing key pair.”));
    }
}
```

### 进阶用法

此插件的运行时逻辑（如何将这些密钥应用于打包）由引擎内部的 `UnrealPak` 和打包流程调用。开发者通常不需要直接在C++运行时代码中使用这些密钥进行加密解密，因为这部分工作在引擎底层通过 `IPlatformCrypto` 接口完成了。插件的主要价值在于提供**编辑器时**的密钥管理工具。

## Demo 示例

一个最小的编辑器工具模块，用于在编辑器中添加一个菜单按钮来生成密钥。

```cpp
// MyCryptoKeyGeneratorTool.h
#pragma once

#include “CoreMinimal.h“
#include “Modules/ModuleManager.h“

class FMyCryptoKeyGeneratorToolModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void GenerateAndLogKeys();
    void RegisterMenus();

    TSharedPtr<FUICommandList> PluginCommands;
};
```

```cpp
// MyCryptoKeyGeneratorTool.cpp
#include “MyCryptoKeyGeneratorTool.h“
#include “CryptoKeysOpenSSL/CryptoKeysOpenSSL.h“
#include “LevelEditor.h“
#include “Framework/MultiBox/MultiBoxBuilder.h“
#include “Misc/MessageDialog.h“

#define LOCTEXT_NAMESPACE “FMyCryptoKeyGeneratorToolModule“

void FMyCryptoKeyGeneratorToolModule::StartupModule()
{
    PluginCommands = MakeShareable(new FUICommandList);
    // 这里省略了菜单扩展的注册代码，通常通过 `FLevelEditorModule` 或 `FToolMenus` 实现
    // 假设我们添加了一个按钮，其执行函数绑定到 GenerateAndLogKeys
}

void FMyCryptoKeyGeneratorModule::ShutdownModule()
{
}

void FMyCryptoKeyGeneratorToolModule::GenerateAndLogKeys()
{
    TArray<uint8> EncKey;
    TArray<uint8> PubExp, PrivExp, Modulus;

    bool bSuccess = CryptoKeysOpenSSL::GenerateNewEncryptionKey(EncKey) &&
                    CryptoKeysOpenSSL::GenerateNewSigningKey(PubExp, PrivExp, Modulus);

    if (bSuccess)
    {
        FMessageDialog::Open(EAppMsgType::Ok, LOCTEXT(“KeyGenSuccess“, “New crypto and signing keys generated successfully. Check the log for details.“));
        UE_LOG(LogTemp, Warning, TEXT(“New AES Key Length: %d bytes“), EncKey.Num());
        // 实际应用中，应将密钥序列化并保存到文件
    }
    else
    {
        FMessageDialog::Open(EAppMsgType::Ok, LOCTEXT(“KeyGenFail“, “Failed to generate new keys.“));
    }
}

void FMyCryptoKeyGeneratorToolModule::RegisterMenus()
{
    // 菜单注册逻辑
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyCryptoKeyGeneratorToolModule, MyCryptoKeyGeneratorTool)
```

## 模块依赖

从模块名称和功能推断，`CryptoKeysOpenSSL` 模块依赖于 OpenSSL 的第三方库。

| 模块 | 用途 |
|---|---|
| `OpenSSL` | 提供底层的加密算法实现（如 AES， RSA） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式。 |
| 2025-05-31 | `8396b185` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 更新头文件，确保 DLL 导出属性作用于正确的方法和静态变量。 |
| 2024-10-22 | `98a8e0e0` | Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 移除了大量用于 5.2 版本头文件包含顺序兼容性的宏。 |
| 2024-09-24 | `0136afdc` | Fixed another instance of the bad saving method for Defaults | 修复了默认设置保存方法的另一个错误实例。 |
| 2024-09-24 | `77b27f1c` | Fixed an issue with Clearing Encryption Key wasn't saving, as it was using a hacky way to save to | 修复了清除加密密钥后无法保存的问题，原保存方法不规范。 |

### 维护评价

该插件**维护不活跃**。创建于2017年，最后一次重要的功能性更新（修复密钥保存逻辑）发生在2024年9月。此后的提交主要是为了适应引擎宏和日志系统的变更，属于维护性更新。插件本身功能已稳定成熟，对于绝大多数需要加密功能的项目来说，现有功能足够且可靠。由于它是Epic官方维护的核心功能插件，可以放心使用。但需注意，如果未来有更高级的加密需求，可能需要自行扩展或寻找替代方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/CryptoKeys)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/CryptoKeys/Tests)（如果存在，通常在 `Tests` 子目录）
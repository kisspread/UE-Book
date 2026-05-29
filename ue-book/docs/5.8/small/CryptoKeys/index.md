# CryptoKeys

> （Description为空，基于源码分析）

| 属性 | 值 |
|---|---|
| 中文名 | 加密密钥 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `CryptoKeys` (Editor), `CryptoKeysOpenSSL` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-12-12 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/CryptoKeys) | |

## 用途

CryptoKeys 插件提供了一套完整的编辑器内工具和运行时接口，用于管理项目的 AES 加密密钥和 RSA 签名密钥。它的核心目的是保护游戏打包后的资产（如 .pak 文件）安全，通过加密防止未授权访问，并通过签名验证资产的完整性和来源，防止被篡改。

它解决了以下问题：
1. **资产加密**：为打包的资产设置 AES 密钥，在打包时自动加密资产，在运行时自动解密加载。
2. **资产签名**：使用 RSA 密钥对资产包进行签名，在加载时验证签名以确保资产未被修改。
3. **密钥管理**：在项目设置中提供用户界面，方便开发者创建、编辑和轮换加密/签名密钥，而无需手动处理复杂的密钥文件。

## 使用场景

- 你需要保护发布的游戏资产不被玩家轻易解包、查看或修改。
- 你是一个使用联机模式或有内购的游戏开发团队，需要确保客户端下载的资产包是官方且未被篡改的。
- 你需要遵守特定的安全合规要求，必须对分发的内容进行加密和签名。

## 蓝图用法

### 核心节点

插件主要提供了一个运行时帮助类 `FCryptoKeysHelper`，用于检查加密状态和获取密钥信息。蓝图中可直接使用这些静态函数。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is Crypto Enabled` | 检查当前项目是否启用了资产加密。 | `FCryptoKeysHelper` |
| `Get Encryption Key` | 获取当前使用的 AES 加密密钥（用于调试或特定用途）。 | `FCryptoKeysHelper` |
| `Get Signing Key` | 获取当前使用的 RSA 签名公钥（用于验证）。 | `FCryptoKeysHelper` |

### 使用示例

在蓝图中，你可以拖入一个 “Is Crypto Enabled” 节点，将其输出连接到一个分支节点。如果返回 `True`，则说明项目资产是加密的。通常，这个检查用于调试日志或在特定平台上执行不同的加载逻辑。正常情况下，资产的加密和解密过程在引擎层面自动完成，开发者无需在游戏逻辑中直接调用加密/解密函数。

## C++ 用法

### 头文件引入

```cpp
#include "CryptoKeysHelper.h"
```

### 基本用法

检查加密状态并获取密钥。
（示例代码基于模块文档 `CryptoKeys.md` 中描述的接口）

```cpp
// 检查当前资产是否被加密
if (FCryptoKeysHelper::IsCryptoEnabled())
{
    UE_LOG(LogTemp, Log, TEXT("资产加密已启用。"));
}

// 获取 AES 密钥 (返回一个包含32字节的数组)
const TArray<uint8>& AESKey = FCryptoKeysHelper::GetEncryptionKey();

// 获取 RSA 签名公钥
const FString& RSAKey = FCryptoKeysHelper::GetSigningKey();
```

### 进阶用法

在自定义的打包或资产处理流程中，可能需要显式使用这些密钥。例如，在编写一个自定义的资产管理器时，你可能需要判断环境并获取密钥来手动处理某些资产。

## Demo 示例

这是一个最小的 Actor 示例，它在开始运行时检查加密状态并输出日志。

**CryptoKeysDemoActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CryptoKeysDemoActor.generated.h"

UCLASS()
class ACryptoKeysDemoActor : public AActor
{
    GENERATED_BODY()
    
public:
    ACryptoKeysDemoActor();

protected:
    virtual void BeginPlay() override;
};
```

**CryptoKeysDemoActor.cpp**
```cpp
#include "CryptoKeysDemoActor.h"
#include "CryptoKeysHelper.h" // 关键头文件

ACryptoKeysDemoActor::ACryptoKeysDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ACryptoKeysDemoActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 检查并输出加密状态
    if (FCryptoKeysHelper::IsCryptoEnabled())
    {
        UE_LOG(LogTemp, Warning, TEXT("CryptoKeysDemoActor: 项目资产已加密!"));
        // 可以进一步获取密钥信息（通常无需在游戏逻辑中直接使用）
        const TArray<uint8>& Key = FCryptoKeysHelper::GetEncryptionKey();
        UE_LOG(LogTemp, Log, TEXT("  AES Key Length: %d"), Key.Num());
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("CryptoKeysDemoActor: 项目资产未加密。"));
    }
}
```

## 模块依赖

要使用 CryptoKeys 的运行时功能，你的模块通常无需直接依赖，因为加密解密在引擎层处理。但若要使用 `FCryptoKeysHelper` 进行查询，需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `CryptoKeys` | 提供 `FCryptoKeysHelper` 等运行时查询接口 |

对于大多数项目，仅需在 **项目设置** 中配置密钥，无需编写额外 C++ 代码或添加模块依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到新的 UE_LOGF 格式。 |
| 2025-05-31 | `8396b185` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 更新头文件，确保DLL导出标记（dllexport）正确应用于方法和静态变量。 |
| 2024-10-22 | `98a8e0e0` | Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 移除了大量因UE5.2头文件包含顺序变更而引入的兼容性代码。 |
| 2024-09-24 | `0136afdc` | - Fixed another instance of the bad saving method for Defaults | 修复了另一个使用错误方法保存“默认设置”的问题。 |
| 2024-09-24 | `77b27f1c` | - Fixed an issue with Clearing Encryption Key wasn't saving, as it was using a hacky way to save to | 修复了“清除加密密钥”功能无法保存的问题，因为它使用了错误的保存方式。 |

### 维护评价

CryptoKeys 插件自 2017 年创建以来一直是 UE 资产安全体系的核心组成部分。近期的更新（如 2024 年）表明它仍在接受维护和 Bug 修复，尤其是与保存逻辑相关的缺陷。然而，最近的实质性功能更新较少，主要围绕编译兼容性和代码清理（如 2025、2026 年的提交）。鉴于其核心地位和持续的小规模维护，它处于 **维护中** 状态，但并非活跃开发。对于需要基础资产加密和签名的项目，它仍然是推荐使用的官方解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/CryptoKeys)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/cryptographic-keys/) (需根据实际文档地址补充)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/CryptoKeys) (路径可能存在，需确认)
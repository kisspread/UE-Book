# JSON Web Token Plugin

> An API for working with JSON Web Token (JWT) data.

| 属性 | 值 |
|---|---|
| 中文名 | JWT 插件 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `JWT` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-08-21 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/JWT) | |

## 用途

该插件提供对 **JSON Web Token (JWT)** 的编码、解码与签名验证能力。JWT 是一种轻量级的身份令牌格式，常用于 API 认证、单点登录（SSO）等场景。

插件主要解决以下问题：
- 解析 Base64URL 编码的 JWT 令牌，提取 header 和 payload（JSON 对象）
- 通过内置的 RS256 算法验证令牌的数字签名
- 为 C++ 项目提供一套自包含的 JWT 处理工具，无需额外引入第三方库（利用 Unreal 的 PlatformCrypto 模块）

## 使用场景

- **对接第三方 REST API**：当你的游戏需要调用外部服务（如玩家认证、排行榜更新）且该服务要求携带 JWT 时，可用此插件解析并验证返回的令牌。
- **本地令牌缓存与校验**：从服务端获取 JWT 后，在客户端缓存并定期验证签名，确保令牌未被篡改。
- **自定义认证流程**：如需实现客户端内部生成签名并发送给服务端，可借助 `FJwtAlgorithm_RS256` 对消息进行签名（目前仅提供签名验证，未提供生成签名的接口，可通过 `PlatformCrypto` 自行扩展）。

## 蓝图用法

该插件当前**未暴露任何蓝图节点**。所有功能均通过 C++ 类提供，仅可在 C++ 项目或蓝图函数库中调用。

## C++ 用法

### 头文件引入

```cpp
#include "JsonWebToken.h"
#include "JwtAlgorithms.h"
```

### 基本用法：解析 JWT 字符串

```cpp
#include "JsonWebToken.h"
#include "Dom/JsonObject.h"

void ParseAndInspectJWT()
{
    // 示例 JWT（格式：header.payload.signature）
    FString EncodedJWT = TEXT("eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c");

    // 方式一：返回 TOptional
    TOptional<FJsonWebToken> OptionalToken = UE::JWT::FromString(EncodedJWT);
    if (OptionalToken.IsSet())
    {
        FJsonWebToken Token = OptionalToken.GetValue();

        // 获取标准声明
        FString Issuer;
        Token.GetIssuer(Issuer);

        int64 IssuedAt;
        Token.GetIssuedAt(IssuedAt);

        // 获取自定义 payload 字段（通过原始 JSON）
        const TSharedRef<FJsonObject>& Payload = Token.GetPayload();
        TSharedPtr<FJsonValue> SubValue = Payload->TryGetField(TEXT("sub"));
        if (SubValue.IsValid())
        {
            FString Subject = SubValue->AsString();
        }
    }

    // 方式二：输出参数
    FJsonWebToken TokenOut;
    if (UE::JWT::FromString(EncodedJWT, TokenOut))
    {
        FString Algorithm;
        TokenOut.GetAlgorithm(Algorithm); // "RS256"
    }
}
```

### 进阶用法：验证 RS256 签名

```cpp
#include "JwtAlgorithms.h"
#include "JwtUtils.h"

bool VerifyJWTSignature(const FString& EncodedJWT, const FString& PublicKeyPEM)
{
    // 1. 解析 JWT 获得 header 和 payload
    FStringView Header, Payload, Signature;
    if (!FJwtUtils::SplitEncodedJsonWebTokenString(EncodedJWT, Header, Payload, Signature))
    {
        return false;
    }

    // 2. 解码签名部分（Base64URL → 字节数组）
    TArray<uint8> DecodedSignature;
    if (!FJwtUtils::Base64UrlDecode(Signature, DecodedSignature))
    {
        return false;
    }

    // 3. 构造签名的消息： "header.payload"
    FString EncodedMessage = FString(Header) + TEXT(".") + FString(Payload);
    TArray<uint8> EncodedMessageBytes;
    FJwtUtils::StringViewToBytes(EncodedMessage, EncodedMessageBytes);

    // 4. 使用 RS256 算法验证
    FJwtAlgorithm_RS256 Algorithm;
    if (!Algorithm.SetPublicKey(PublicKeyPEM))
    {
        return false;
    }

    return Algorithm.VerifySignature(EncodedMessageBytes, DecodedSignature);
}
```

### 辅助函数

`FJwtUtils` 提供以下工具方法：

| 函数 | 说明 |
|---|---|
| `Base64UrlDecode(const FStringView, FString&)` | 将 Base64URL 字符串解码为普通字符串 |
| `Base64UrlDecode(const FStringView, TArray<uint8>&)` | 解码为字节数组（用于签名） |
| `SplitEncodedJsonWebTokenString(...)` | 将 JWT 字符串拆分为 header / payload / signature 三部分 |
| `StringViewToBytes(const FStringView, TArray<uint8>&)` | 将 FStringView 转为 UTF-8 字节（用于构造待签名消息） |

## Demo 示例

以下是一个控制台命令测试，展示完整的解析与验证流程：

**JwtDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "JwtDemo.generated.h"

UCLASS()
class UJwtDemo : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    // 测试入口，可在控制台或 C++ 中调用
    UFUNCTION(Exec)
    static void TestJwt();
};
```

**JwtDemo.cpp**
```cpp
#include "JwtDemo.h"
#include "JsonWebToken.h"
#include "JwtAlgorithms.h"
#include "JwtUtils.h"
#include "Dom/JsonObject.h"

void UJwtDemo::TestJwt()
{
    // 1. 解析一个简单的 JWT（无签名验证）
    FString TestToken = TEXT("eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c");
    FJsonWebToken Token;
    if (UE::JWT::FromString(TestToken, Token))
    {
        FString Issuer, Subject;
        Token.GetIssuer(Issuer);
        // payload 中自定义字段
        const TSharedRef<FJsonObject>& Payload = Token.GetPayload();
        if (Payload->TryGetStringField("sub", Subject))
        {
            UE_LOG(LogTemp, Log, TEXT("Subject: %s"), *Subject);
        }
    }

    // 2. 验证 RS256 签名（使用公钥）
    // 注意：公钥需为 PEM 格式（如 "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"）
    // 此处仅为示例，实际公钥由服务端提供
    const FString PublicKeyPEM = TEXT("-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA7...\n-----END PUBLIC KEY-----");
    FJwtAlgorithm_RS256 Verifier;
    if (Verifier.SetPublicKey(PublicKeyPEM))
    {
        FStringView Header, PayloadPart, SignaturePart;
        FJwtUtils::SplitEncodedJsonWebTokenString(TestToken, Header, PayloadPart, SignaturePart);
        TArray<uint8> DecodedSig;
        if (FJwtUtils::Base64UrlDecode(SignaturePart, DecodedSig))
        {
            FString EncodedMessage = FString(Header) + TEXT(".") + FString(PayloadPart);
            TArray<uint8> MessageBytes;
            FJwtUtils::StringViewToBytes(EncodedMessage, MessageBytes);
            bool bValid = Verifier.VerifySignature(MessageBytes, DecodedSig);
            UE_LOG(LogTemp, Log, TEXT("Signature valid: %s"), bValid ? TEXT("Yes") : TEXT("No"));
        }
    }
}
```

## 模块依赖

在您的 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "JWT",
    // PlatformCrypto 是 JWT 的内部依赖，若您直接使用 JwtAlgorithm 无需额外添加
});
```

| 模块 | 用途 |
|---|---|
| `PlatformCrypto` | 提供跨平台的加密功能（OpenSSL / SwitchSSL），用于 RS256 签名验证 |

## 维护状态

### 近期更新

- 2025-04-23 `939cc6e5` Used FortniteClient build target to find and convert all files to have dllstorage on methods/static variables (编译调整)
- 2025-04-04 `49c9e5de` Cleanup PlatformCrypto context build complexity. Fixes some incorrect explicit dependencies on ... (依赖重构)
- 2024-11-10 `66e9bb39` Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base (代码清理)
- 2024-06-12 `e7a04268` Replaced EAutomationTestFlags::ApplicationContextMask with EAutomationTestFlags_ApplicationContextMa (测试更新)
- 2023-08-21 `1d54f305` Add JWT option to get raw JSON payload (初始功能提交)

### 维护评价

该插件自 2023 年创建以来持续得到维护，最近一年内仍有功能性调整和清理更新。当前主要用于 UE5.4+，且作为实验性插件默认未启用，但从更新频率判断仍在活跃维护中。功能较为单一（仅解析和 RS256 验证），适合需要 JWT 基本操作的 C++ 项目。如果需要的算法（如 HS256、ES256）未提供，则需要自行扩展 `IJwtAlgorithm` 接口。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/JWT)
- [官方文档](https://docs.unrealengine.com/5.4/en-US/)（暂未提供专门文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/JWT/Tests)
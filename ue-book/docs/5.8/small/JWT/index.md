# JSON Web Token Plugin

> An API for working with JSON Web Token (JWT) data.

| 属性 | 值 |
|---|---|
| 中文名 | JWT插件 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `JWT` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-08-15 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/JWT) | |

## 用途

此插件提供了一套用于**解析、提取声明（Claims）和验证签名**的 JSON Web Token (JWT) API。它解决的核心问题是：如何在虚幻引擎项目中安全、便捷地处理来自外部服务（如身份验证提供商、Web API）的 JWT 字符串。插件专注于客户端验证，特别提供了 RS256 算法的签名验证支持，并与 `FOnlineIdentityMcp` 等身份系统集成。

## 使用场景

- 你的游戏需要集成一个在线身份验证系统，该系统使用 JWT 作为访问令牌 → 用此插件解析和验证用户令牌。
- 你需要在客户端安全地验证从服务器收到的 JWT 令牌的签名和有效性（例如，确认发行者、检查是否过期）。
- 你需要从 JWT 的载荷（Payload）中提取自定义声明（Claims）用于业务逻辑。

## 蓝图用法

此插件主要提供 C++ API，未暴露原生蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "JWT.h"
#include "JsonWebToken.h"
#include "JwtAlgorithms.h"
```

### 基本用法

解析一个 JWT 字符串并提取标准声明。

```cpp
// 来源：源码分析基于 Source/JWT/Public/JsonWebToken.h
const FString JWTString = TEXT("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE3MTYyMzkwMjIsImlzcyI6Im15X2FwcCJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c");

// 1. 解析JWT字符串
UE::JWT::FromString(JWTString).BindLambda([](const FJsonWebToken& Token)
{
    // 2. 检查令牌是否过期
    if (Token.HasExpired())
    {
        UE_LOG(LogTemp, Warning, TEXT("JWT has expired."));
        return;
    }

    // 3. 提取标准声明
    FString Issuer;
    if (Token.GetIssuer(Issuer))
    {
        UE_LOG(LogTemp, Log, TEXT("Issuer: %s"), *Issuer);
    }

    int64 ExpirationTime;
    if (Token.GetExpiration(ExpirationTime))
    {
        UE_LOG(LogTemp, Log, TEXT("Expires at: %lld"), ExpirationTime);
    }

    // 4. 提取自定义声明
    FString CustomClaim;
    if (Token.GetStringClaim(TEXT("name"), CustomClaim))
    {
        UE_LOG(LogTemp, Log, TEXT("Custom 'name' claim: %s"), *CustomClaim);
    }

    // 5. 或者直接访问原始JSON对象
    const TSharedRef<FJsonObject>& Payload = Token.GetPayload();
    // 使用 Payload 进行自定义解析...
});
```

### 进阶用法

使用 RS256 算法验证 JWT 的签名，并验证发行者。

```cpp
// 来源：源码分析基于 Source/JWT/Public/JwtAlgorithms.h
// 假设你从某个配置或服务获取了公钥（PEM格式）和预期的发行者
const FString PEMPublicKey = TEXT("-----BEGIN PUBLIC KEY-----\nMIIBI...IDAQAB\n-----END PUBLIC KEY-----");
const FString ExpectedIssuer = TEXT("my_auth_server");
const FString JWTString = TEXT("...一个RS256签名的JWT...");

// 1. 创建RS256算法实例并设置公钥
FJwtAlgorithm_RS256 RS256Algorithm;
if (!RS256Algorithm.SetPublicKey(PEMPublicKey))
{
    UE_LOG(LogTemp, Error, TEXT("Failed to set public key for RS256 verification."));
    return;
}

// 2. 解析JWT
FJsonWebToken Token;
if (!UE::JWT::FromString(JWTString, Token))
{
    UE_LOG(LogTemp, Error, TEXT("Failed to parse JWT string."));
    return;
}

// 3. 使用算法和预期发行者进行综合验证（签名+基本声明+发行者匹配）
bool bIsVerified = Token.Verify(RS256Algorithm, ExpectedIssuer);

if (bIsVerified)
{
    UE_LOG(LogTemp, Log, TEXT("JWT signature and claims verified successfully."));
    // ... 继续安全地使用令牌 ...
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("JWT verification failed."));
}
```

## Demo 示例

一个完整的可编译最小示例，演示解析、过期检查和签名验证。

**MyJWTUser.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyJWTUser.generated.h"

class FJsonWebToken;

UCLASS()
class UMyJWTUserSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    void DemonstrateJWTParsing();
    bool VerifyJWTWithRS256(const FString& InJWTString, const FString& InPEMPublicKey, const FString& InExpectedIssuer);
};
```

**MyJWTUser.cpp**
```cpp
#include "MyJWTUser.h"
#include "JWT.h"
#include "JsonWebToken.h"
#include "JwtAlgorithms.h"
#include "JwtGlobals.h" // For LogJwt category

void UMyJWTUserSubsystem::DemonstrateJWTParsing()
{
    // 示例JWT (HS256，仅用于演示解析结构)
    const FString ExampleJWT = TEXT("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJhYmMxMjMiLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE3MDAwMDAwMDAsImV4cCI6MTcwMDAwMDAwMCwiaXNzIjoiZ2FtZV9zZXJ2ZXIifQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c");

    UE::JWT::FromString(ExampleJWT).Bind([this](const FJsonWebToken& Token)
    {
        UE_LOG(LogJwt, Log, TEXT("--- JWT Parsing Demo ---"));

        // 过期检查
        UE_LOG(LogJwt, Log, TEXT("Token has expired: %s"), Token.HasExpired() ? TEXT("Yes") : TEXT("No"));

        // 提取标准声明
        FString Issuer;
        if (Token.GetIssuer(Issuer))
        {
            UE_LOG(LogJwt, Log, TEXT("Issuer: %s"), *Issuer);
        }

        // 提取自定义声明
        FString UserId;
        if (Token.GetStringClaim(TEXT("userId"), UserId))
        {
            UE_LOG(LogJwt, Log, TEXT("Custom Claim 'userId': %s"), *UserId);
        }

        FString UserRole;
        if (Token.GetStringClaim(TEXT("role"), UserRole))
        {
            UE_LOG(LogJwt, Log, TEXT("Custom Claim 'role': %s"), *UserRole);
        }
    });
}

bool UMyJWTUserSubsystem::VerifyJWTWithRS256(const FString& InJWTString, const FString& InPEMPublicKey, const FString& InExpectedIssuer)
{
    FJwtAlgorithm_RS256 Algorithm;
    if (!Algorithm.SetPublicKey(InPEMPublicKey))
    {
        UE_LOG(LogJwt, Error, TEXT("Failed to initialize RS256 algorithm with provided PEM key."));
        return false;
    }

    FJsonWebToken Token;
    if (!UE::JWT::FromString(InJWTString, Token))
    {
        UE_LOG(LogJwt, Error, TEXT("Failed to parse the provided JWT string."));
        return false;
    }

    const bool bVerified = Token.Verify(Algorithm, InExpectedIssuer);
    UE_LOG(LogJwt, Log, TEXT("JWT verification result: %s"), bVerified ? TEXT("SUCCESS") : TEXT("FAILURE"));
    return bVerified;
}
```

## 模块依赖

除标准 Core/Engine 等模块外，使用此插件需要依赖以下内容：

| 模块 | 用途 |
|---|---|
| `PlatformCrypto` | 提供底层的加密上下文（如 OpenSSL），用于签名验证。 |
| `Json` | 用于解析 JWT 的头部和载荷 JSON 对象。 |

你的模块 `Build.cs` 中应包含：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "JWT",
    "Json"
});
// 如果需要直接使用平台加密功能
PrivateDependencyModuleNames.Add("PlatformCrypto");
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 FSharedString，优化字符串处理。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移至 UE_LOGF，更新日志记录方式。 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复以释放内存，优化内存使用。 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 回退了某个变更。 |
| 2026-02-25 | `af0dfacf` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 同 9758fa58，为修复内存问题所做的更改。 |

### 维护评价

- **创建时间**：约 3 年前（2022年）。
- **更新频率**：在 2026 年初仍有活跃的维护活动，主要涉及性能优化（内存管理）和代码迁移。
- **状态**：**活跃维护**。尽管处于 `Experimental` 目录且默认禁用，但近期有持续的改进，表明 Epic 可能仍在内部使用或开发中。
- **已知限制**：标记为 `Experimental`，未来 API 可能发生变化。目前仅支持 RS256 算法。
- **推荐使用**：如果你需要处理 JWT，这是一个功能完整且专注于核心需求的插件。鉴于其维护状态和清晰的源码，对于需要 JWT 功能的项目是**值得使用的**，但需注意其“实验性”状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/JWT)
- [官方文档]() (无)
- [测试用例]() (插件目录内未发现标准测试文件，可能在 `Engine/Tests/` 下，需进一步确认)
# Electra Player Content Decryption Module

> Content Decryption Module for Electra Player Media Playback

| 属性 | 值 |
|---|---|
| 中文名 | Electra 内容解密模块 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraCDM` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-05-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraCDM) | |

## 用途

ElectraCDM 是为 Electra 媒体播放器提供的**内容解密框架（CDM，Content Decryption Module）**。它解决的是受 DRM 保护的媒体流（如加密的 DASH/HLS 视频）在播放时的解密问题。

该插件的核心设计是一个**可扩展的 DRM 系统注册框架**：

- **`IMediaCDM`** 作为全局单例管理器，负责注册和调度不同的 CDM 系统
- **`IMediaCDMSystem`** 是 CDM 提供者需要实现的接口（如 ClearKey、HLS AES-128）
- **`IMediaCDMClient`** 是播放器会话使用的客户端接口，负责许可证获取和解密器创建
- **`IMediaCDMDecrypter`** 是实际执行解密操作的实例

插件内置了两个 CDM 实现：
1. **ClearKey**：W3C EME 规范中的明文密钥方案，用于测试和基本保护场景
2. **HLS AES-128**：HLS 流中使用 AES-128 加密的方案

## 使用场景

- 你正在集成 Electra 媒体播放器，需要播放 DRM 保护的 DASH/HLS 内容 → 启用此插件
- 你需要为 Electra 播放器添加自定义 DRM 系统（如 Widevine、PlayReady）→ 实现 `IMediaCDMSystem` 接口并注册
- 你需要在 HLS 流中解密使用 AES-128-CBC 或 AES-128-CTR 加密的媒体段 → 使用内置的解密器
- 你使用 ClearKey 方案进行开发测试 → 直接使用内置的 ClearKey CDM

## 蓝图用法

该插件**不包含任何蓝图可调用接口**。所有 API 均为纯 C++ 接口，面向媒体播放器底层开发者，不暴露给蓝图。

## C++ 用法

### 头文件引入

```cpp
#include "ElectraCDM.h"
#include "ElectraCDMClient.h"
#include "ElectraCDMSystem.h"
#include "ElectraCDMError.h"
#include "ElectraEncryptedSampleInfo.h"
```

### 基本用法：查询 CDM 能力并创建客户端

查询某个 DRM scheme 是否支持指定的媒体类型，然后创建解密客户端。

```cpp
// 来源: Source/ElectraCDM/Public/ElectraCDM.h

// 获取 CDM 管理器单例
ElectraCDM::IMediaCDM& CDMManager = ElectraCDM::IMediaCDM::Get();

// 查询某个 scheme 的能力
FString SchemeId = TEXT("urn:uuid:e2719d58-a985-b3c9-781a-b030af78d30e");
TSharedPtr<ElectraCDM::IMediaCDMCapabilities, ESPMode::ThreadSafe> Capabilities =
    CDMManager.GetCDMCapabilitiesForScheme(SchemeId, TEXT("ClearKey1.0"), TEXT("{}"));

if (Capabilities.IsValid())
{
    // 检查是否支持指定的加密方式
    auto CipherResult = Capabilities->SupportsCipher(TEXT("cenc"));
    // 检查是否支持指定的媒体类型
    auto TypeResult = Capabilities->SupportsType(TEXT("video/mp4; codecs=\"avc1.640028\""));

    // 检查是否需要安全解码器
    auto SecureResult = Capabilities->RequiresSecureDecoder(TEXT("video/mp4"));
}
```

### 基本用法：创建播放会话和 DRM 客户端

```cpp
// 来源: Source/ElectraCDM/Public/ElectraCDM.h

ElectraCDM::IMediaCDM& CDMManager = ElectraCDM::IMediaCDM::Get();

// 创建播放器会话（每个播放器实例一个）
ElectraCDM::IMediaCDM::IPlayerSession* PlayerSession = CDMManager.CreatePlayerSessionID();

// 准备候选 CDM 列表（来自 DASH/HLS 解析的 ContentProtection 元素）
TArray<ElectraCDM::IMediaCDM::FCDMCandidate> Candidates;
ElectraCDM::IMediaCDM::FCDMCandidate Candidate;
Candidate.SchemeId = TEXT("urn:uuid:e2719d58-a985-b3c9-781a-b030af78d30e");
Candidate.Value = TEXT("ClearKey1.0");
Candidate.AdditionalElements = TEXT("{\"laurl\":\"https://example.com/license\"}");
Candidates.Add(Candidate);

// 创建 DRM 客户端
TSharedPtr<ElectraCDM::IMediaCDMClient, ESPMode::ThreadSafe> DRMClient;
ElectraCDM::ECDMError Error = CDMManager.CreateDRMClient(DRMClient, PlayerSession, Candidates);

if (Error == ElectraCDM::ECDMError::Success && DRMClient.IsValid())
{
    // 开始许可证获取流程
    DRMClient->PrepareLicenses();
}
```

### 进阶用法：实现事件监听器处理许可证获取

```cpp
// 来源: Source/ElectraCDM/Public/ElectraCDMClient.h

// 应用程序需要实现事件监听器来响应 CDM 事件
class FMyCDMEventListener : public ElectraCDM::IMediaCDMEventListener
{
public:
    virtual void OnCDMEvent(
        ECDMEventType InEventType,
        TSharedPtr<ElectraCDM::IMediaCDMClient, ESPMode::ThreadSafe> InDrmClient,
        void* InEventId,
        const TArray<uint8>& InCustomData) override
    {
        switch (InEventType)
        {
        case ECDMEventType::KeyRequired:
        {
            // 获取许可证请求数据
            TArray<uint8> KeyRequestData;
            FString HttpMethod;
            TArray<FString> HttpHeaders;
            uint32 Flags;
            FString LicenseURL;
            InDrmClient->GetLicenseKeyURL(LicenseURL);
            InDrmClient->GetLicenseKeyRequestData(KeyRequestData, HttpMethod, HttpHeaders, Flags);

            // 异步发送到许可证服务器（此处省略网络请求细节）
            // ... 发送请求并获取响应 ...

            // 将服务器响应设置回 CDM 客户端
            TArray<uint8> ResponseData; // 从服务器获取的响应
            int32 HttpResponseCode = 200;
            InDrmClient->SetLicenseKeyResponseData(InEventId, HttpResponseCode, ResponseData);
            break;
        }
        case ECDMEventType::KeyExpired:
            // 处理密钥过期，可能需要重新获取许可证
            break;
        case ECDMEventType::ProvisionRequired:
            // 处理设备配置需求
            break;
        }
    }
};

// 注册监听器
TSharedPtr<FMyCDMEventListener> Listener = MakeShared<FMyCDMEventListener>();
DRMClient->RegisterEventListener(Listener);
```

### 进阶用法：使用解密器解密媒体数据

```cpp
// 来源: Source/ElectraCDM/Public/ElectraCDMClient.h, ElectraEncryptedSampleInfo.h

// 为指定 MIME 类型创建解密器
TSharedPtr<ElectraCDM::IMediaCDMDecrypter, ESPMode::ThreadSafe> Decrypter;
ElectraCDM::ECDMError Error = DRMClient->CreateDecrypter(Decrypter, TEXT("video/mp4"));

if (Error == ElectraCDM::ECDMError::Success && Decrypter.IsValid())
{
    // 从 PSSH box 更新初始化数据
    TArray<uint8> PSSHData; // 从媒体流中解析得到
    Decrypter->UpdateInitDataFromPSSH(PSSHData);

    // 准备加密样本信息
    ElectraCDM::FMediaCDMSampleInfo SampleInfo;
    SampleInfo.IV = { /* 16 字节 IV */ };
    SampleInfo.DefaultKID = { /* 16 字节 KID */ };
    SampleInfo.Scheme4CC = 'cenc'; // 或 'cbcs'

    // 根据加密模式选择解密方式
    if (!Decrypter->IsBlockStreamDecrypter())
    {
        // CTR 模式：就地解密（非块流模式）
        TArray<uint8> EncryptedData = { /* 加密数据 */ };
        Decrypter->DecryptInPlace(EncryptedData.GetData(), EncryptedData.Num(), SampleInfo);
    }
    else
    {
        // CBC 模式：块流解密
        ElectraCDM::IMediaCDMDecrypter::IStreamDecryptHandle* Handle = nullptr;
        Decrypter->BlockStreamDecryptStart(Handle, SampleInfo);

        int32 BytesDecrypted = 0;
        TArray<uint8> Data = { /* 加密数据 */ };
        Decrypter->BlockStreamDecryptInPlace(Handle, BytesDecrypted,
            Data.GetData(), Data.Num(), true /* bIsLastBlock */);

        Decrypter->BlockStreamDecryptEnd(Handle);
    }
}
```

### 进阶用法：直接使用 AES-128 加密工具类

```cpp
// 来源: Source/ElectraCDM/Public/Crypto/StreamCryptoAES128.h

#include "Crypto/StreamCryptoAES128.h"

// 创建 AES-128 解密器
TSharedPtr<ElectraCDM::IStreamDecrypterAES128, ESPMode::ThreadSafe> AESDecrypter =
    ElectraCDM::IStreamDecrypterAES128::Create();

TArray<uint8> Key; // 16 字节 AES 密钥
TArray<uint8> IV;  // 16 字节初始化向量

// CBC 模式解密
auto Result = AESDecrypter->CBCInit(Key, &IV);
if (Result == ElectraCDM::IStreamDecrypterAES128::EResult::Ok)
{
    TArray<uint8> EncryptedData; // 必须是 16 字节的倍数
    int32 BytesDecrypted = 0;
    AESDecrypter->CBCDecryptInPlace(BytesDecrypted, EncryptedData.GetData(),
        EncryptedData.Num(), true /* bIsFinalBlock */);
}

// CTR 模式解密
Result = AESDecrypter->CTRInit(Key);
if (Result == ElectraCDM::IStreamDecrypterAES128::EResult::Ok)
{
    AESDecrypter->CTRSetIV(IV);
    TArray<uint8> Data; // 任意长度
    AESDecrypter->CTRDecryptInPlace(Data.GetData(), Data.Num());
}
```

## Demo 示例

一个完整的自定义 CDM 系统实现示例（最小可运行骨架）：

### MyCDMSystem.h

```cpp
#pragma once

#include "ElectraCDM.h"
#include "ElectraCDMSystem.h"
#include "ElectraCDMClient.h"

// 自定义 CDM 系统实现
class FMyCustomCDMSystem : public ElectraCDM::IMediaCDMSystem
{
public:
    static void RegisterWith(ElectraCDM::IMediaCDM& InDRMManager);

    virtual FString GetLastErrorMessage() override { return ErrorMessage; }
    virtual const TArray<FString>& GetSchemeIDs() override { return SchemeIDs; }

    virtual void GetCDMCustomJSONPrefixes(
        FString& OutAttributePrefix,
        FString& OutTextPropertyName,
        bool& bOutNoNamespaces) override;

    virtual TSharedPtr<ElectraCDM::IMediaCDMCapabilities, ESPMode::ThreadSafe>
        GetCDMCapabilities(const FString& InValue, const FString& InAdditionalElements) override;

    virtual ElectraCDM::ECDMError CreateDRMClient(
        TSharedPtr<ElectraCDM::IMediaCDMClient, ESPMode::ThreadSafe>& OutClient,
        ElectraCDM::IMediaCDM::IPlayerSession* InForPlayerSession,
        const TArray<ElectraCDM::IMediaCDM::FCDMCandidate>& InCandidates) override;

    virtual ElectraCDM::ECDMError ReleasePlayerSessionKeys(
        ElectraCDM::IMediaCDM::IPlayerSession* PlayerSession) override;

private:
    FString ErrorMessage;
    TArray<FString> SchemeIDs = { TEXT("urn:uuid:your-custom-scheme-id") };
};
```

### MyCDMSystem.cpp

```cpp
#include "MyCDMSystem.h"

void FMyCustomCDMSystem::RegisterWith(ElectraCDM::IMediaCDM& InDRMManager)
{
    // 创建 CDM 系统实例并注册到全局管理器
    TSharedPtr<FMyCustomCDMSystem, ESPMode::ThreadSafe> CDMSystem =
        MakeShared<FMyCustomCDMSystem>();
    InDRMManager.RegisterCDM(CDMSystem);
}

void FMyCustomCDMSystem::GetCDMCustomJSONPrefixes(
    FString& OutAttributePrefix,
    FString& OutTextPropertyName,
    bool& bOutNoNamespaces)
{
    OutAttributePrefix = TEXT("@");
    OutTextPropertyName = TEXT("#text");
    bOutNoNamespaces = true;
}

TSharedPtr<ElectraCDM::IMediaCDMCapabilities, ESPMode::ThreadSafe>
FMyCustomCDMSystem::GetCDMCapabilities(
    const FString& InValue,
    const FString& InAdditionalElements)
{
    // 返回此 CDM 系统的能力查询接口
    // 实际实现中应根据 InValue 和 InAdditionalElements 判断支持情况
    return nullptr;
}

ElectraCDM::ECDMError FMyCustomCDMSystem::CreateDRMClient(
    TSharedPtr<ElectraCDM::IMediaCDMClient, ESPMode::ThreadSafe>& OutClient,
    ElectraCDM::IMediaCDM::IPlayerSession* InForPlayerSession,
    const TArray<ElectraCDM::IMediaCDM::FCDMCandidate>& InCandidates)
{
    // 创建自定义的 DRM 客户端实例
    // OutClient = MakeShared<FMyCustomCDMClient>(InForPlayerSession, InCandidates);
    return ElectraCDM::ECDMError::Success;
}

ElectraCDM::ECDMError FMyCustomCDMSystem::ReleasePlayerSessionKeys(
    ElectraCDM::IMediaCDM::IPlayerSession* PlayerSession)
{
    // 释放与播放会话关联的所有许可证密钥
    return ElectraCDM::ECDMError::Success;
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等基础模块）。该插件使用了内置的 `3rdParty/tiny-AES-c` 库实现 AES-128 加密算法，无外部模块依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 全局代码修复：将析构函数体改为空默认 |
| 2025-04-23 | `939cc6e5` | Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv | 添加 DLL 导出标记以支持 Fortnite 构建 |
| 2024-06-25 | `4a6d973b` | Fixed some 'deprecated' FString usage. | 修复已废弃的 FString 用法 |
| 2024-06-24 | `babbc1e7` | ElectraCDM: Added decryption methods for HLS (for keyformat == identity) | 新增 HLS 身份密钥格式的解密方法 |

### 维护评价

ElectraCDM 创建于 2021 年 5 月，是一个相对较新的插件（约 4 年）。该插件的近期更新主要是**全局代码维护性修复**（日志宏迁移、析构函数规范化、DLL 导出标记等），而非功能迭代。唯一一次实质性功能更新是 2024 年 6 月添加的 HLS AES-128 解密支持。

该插件**默认未启用**（`EnabledByDefault: false`），且标记为未包含内容。这意味着它作为 Electra 媒体播放器生态的一部分存在，仅在需要 DRM 保护媒体播放时手动启用。

**评价**：维护状态为**维护中**，但活跃度较低。插件功能相对稳定，作为基础 DRM 框架已经足够成熟。如果你的项目需要播放加密媒体流并通过 Electra 播放器解密，可以放心使用。但如果你需要集成商业级 DRM（如 Widevine、PlayReady），需要基于此框架自行实现 `IMediaCDMSystem`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraCDM)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraCDM)（未发现独立测试文件）
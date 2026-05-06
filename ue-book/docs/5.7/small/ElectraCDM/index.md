# Electra Player Content Decryption Module

> Content Decryption Module for Electra Player Media Playback

| 属性 | 值 |
|---|---|
| 中文名 | Electra 解密模块 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraCDM` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-04-03 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraCDM) | |

## 用途

ElectraCDM 是 Electra 媒体播放器的**内容解密模块**。它提供了一套统一的 DRM（数字版权管理）框架，允许注册不同的解密系统（CDM）来处理加密媒体内容的解密。该模块内置了两种常用解密方案：

- **ClearKey CDM**：用于 MPEG-DASH 等流媒体协议中的 ClearKey 加密（基于 ISO/IEC 23009-1 标准）。
- **HLS AES-128 CDM**：用于 HLS 流媒体协议中以 `keyformat=identity` 标识的 AES-128 加密。

此外，模块还提供了纯 AES-128 CBC/CTR 模式的流解密器（`IStreamDecrypterAES128`），可单独用于低级加密操作。

该插件的存在使得 Electra 播放器能够直接支持加密内容播放，同时允许开发者扩展自定义的 CDM 系统（如 Widevine、PlayReady 等），而无需修改播放器核心。

## 使用场景

- 需要播放受 DRM 保护的 DASH 流（如使用 ClearKey 加密的媒体）。
- 需要播放使用 AES-128 加密的 HLS 流。
- 希望为 Electra 播放器集成第三方 DRM 系统（通过实现 `IMediaCDMSystem` 接口）。
- 需要在运行时对媒体样本进行低级别 AES 解密（使用 `IStreamDecrypterAES128`）。

## 蓝图用法

该插件未暴露任何蓝图可调用功能，所有 API 均为 C++ 接口。

## C++ 用法

### 头文件引入

```cpp
#include "ElectraCDM.h"
```

若需使用流解密器：

```cpp
#include "Crypto/StreamCryptoAES128.h"
```

### 基本用法

#### 1. 获取全局 CDM 管理器并注册内置系统

```cpp
using namespace ElectraCDM;

// 获取 CDM 管理器单例
IMediaCDM& CDMManager = IMediaCDM::Get();

// 注册内置的 ClearKey CDM 系统
IClearKeyCDM::RegisterWith(CDMManager);

// 注册内置的 HLS AES-128 CDM 系统
IHLS_AES128_CDM::RegisterWith(CDMManager);
```

#### 2. 创建 DRM 客户端并监听事件

```cpp
// 假设已有 PlayerSession（由播放器创建）
IMediaCDM::IPlayerSession* PlayerSession = ...;

// 构造 CDM 候选列表
TArray<IMediaCDM::FCDMCandidate> Candidates;
IMediaCDM::FCDMCandidate Candidate;
Candidate.SchemeIdUri = TEXT("urn:uuid:e2719d58-a985-b3c9-781a-b030af78d30e"); // ClearKey UUID
Candidate.Value = TEXT("ClearKey1.0");
Candidate.AdditionalElements = ...; // JSON 格式的附加元素（如许可证URL）
Candidates.Add(Candidate);

// 创建 DRM 客户端
TSharedPtr<IMediaCDMClient, ESPMode::ThreadSafe> Client;
ECDMError Result = CDMManager.CreateDRMClient(Client, PlayerSession, Candidates);
if (Result == ECDMError::Success)
{
    // 注册事件监听器（用于许可证获取等）
    TSharedPtr<IMediaCDMEventListener, ESPMode::ThreadSafe> Listener = ...;
    Client->RegisterEventListener(Listener);

    // 准备许可证获取
    Client->PrepareForLicenseAcquisition();

    // 在收到 OnCDMEvent(KeyRequired, ...) 后，通过 SetLicenseKeyResponseData() 提供密钥
    TArray<uint8> KeyResponse;
    Client->SetLicenseKeyResponseData(EventId, ECDMError::Success, KeyResponse, 0);
}
```

#### 3. 使用流解密器（AES-128 CBC/CTR）

```cpp
// 创建解密器实例
TSharedPtr<IStreamDecrypterAES128, ESPMode::ThreadSafe> Decrypter = IStreamDecrypterAES128::Create();

// 准备密钥和 IV
TArray<uint8> Key = {0x00, 0x01, ...}; // 16字节
TArray<uint8> IV = {0x00, 0x01, ...};  // 16字节

// 初始化 CBC 模式
ECDMError Err = Decrypter->CBCInit(Key, &IV);

// 解密数据（16字节对齐）
int32 OutBytes = 0;
uint8 Buffer[512]; // 假设已填充加密数据
Err = Decrypter->CBCDecryptInPlace(OutBytes, Buffer, 256, true); // 最后一块
if (Err == ECDMError::Success)
{
    // 解密后的数据在 Buffer 中，有效长度为 OutBytes
}
```

### 进阶用法

#### 实现自定义 CDM 系统

1. 继承 `IMediaCDMSystem` 和 `IMediaCDMClient` 接口。
2. 实现 `GetSchemeIDs()`、`CreateDRMClient()`、`GetCDMCapabilities()` 等方法。
3. 注册到全局管理器：

```cpp
class FMyCDMSystem : public IMediaCDMSystem
{
    // ... 实现所有纯虚函数
};

// 注册函数
void FMyCDMSystem::RegisterWith(IMediaCDM& InDRMManager)
{
    TSharedPtr<FMyCDMSystem, ESPMode::ThreadSafe> CDM(new FMyCDMSystem);
    InDRMManager.RegisterCDM(CDM);
}
```

#### 处理许可证获取事件

实现 `IMediaCDMEventListener` 接口，在 `OnCDMEvent` 中根据事件类型执行网络请求、用户界面交互等操作，并通过 `SetLicenseKeyResponseData()` 返回结果。

## Demo 示例

以下是一个最小化的 C++ 模块，演示如何使用 ElectraCDM 的流解密器对 AES-128 CBC 加密数据进行解密。

**MyDecryptor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Crypto/StreamCryptoAES128.h"

class FMyDecryptor
{
public:
    static bool DecryptBuffer(const TArray<uint8>& Key, const TArray<uint8>& IV, TArray<uint8>& Data);
};
```

**MyDecryptor.cpp**

```cpp
#include "MyDecryptor.h"
#include "ElectraCDMError.h"

bool FMyDecryptor::DecryptBuffer(const TArray<uint8>& Key, const TArray<uint8>& IV, TArray<uint8>& Data)
{
    using namespace ElectraCDM;

    TSharedPtr<IStreamDecrypterAES128, ESPMode::ThreadSafe> Decrypter = IStreamDecrypterAES128::Create();
    if (!Decrypter.IsValid())
        return false;

    ECDMError Err = Decrypter->CBCInit(Key, &IV);
    if (Err != ECDMError::Success)
        return false;

    // CBCDecryptInPlace 要求输入大小为16的倍数
    int32 NumBlocks = Data.Num() / 16;
    if (Data.Num() % 16 != 0)
    {
        // 添加 PKCS7 填充扩展（简化，实际应使用正确的填充方式）
        int32 PadLen = 16 - (Data.Num() % 16);
        Data.AddZeroed(PadLen);
        NumBlocks = Data.Num() / 16;
    }

    int32 OutBytes = 0;
    Err = Decrypter->CBCDecryptInPlace(OutBytes, Data.GetData(), NumBlocks * 16, true);
    if (Err != ECDMError::Success)
        return false;

    // 根据实际填充情况裁剪数据（此处省略）
    Data.SetNum(OutBytes);
    return true;
}
```

## 模块依赖

在您的模块 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(
    new string[] {
        "ElectraCDM"
    }
);
```

该插件无特殊外部依赖（仅标准 `Core`、`CoreUObject`、`Engine` 等）。

| 模块 | 用途 |
|---|---|
| 无特殊依赖 | 仅依赖 UE 核心模块 |

## 维护状态

### 近期更新

- 2025-04-23 `939cc6e5` — Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv
- 2024-06-25 `4a6d973b` — Fixed some 'deprecated' FString usage.
- 2024-06-24 `babbc1e7` — ElectraCDM: Added decryption methods for HLS (for keyformat == identity)
- 2023-10-12 `ffb133e7` — Update more code using FJsonObject to use TCHAR strings instead of ANSI strings.
- 2023-04-03 `ebabab67` — Electra: Copy-up from codec refactor task stream

### 维护评价

该插件创建于 2023 年 4 月，至今约 2 年。近期更新活跃，2024 年 6 月添加了 HLS 解密支持并修复了 API 弃用问题，2025 年 4 月仍有构建相关的转换提交。目前官方仍在积极维护。

**该插件推荐使用**，特别适用于需要处理加密媒体的 Electra 播放器集成场景。但请注意插件默认未启用，需在项目中手动开启（.uplugin 中 `EnabledByDefault = false`）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraCDM)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [Electra 播放器文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/ElectraPlayer)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraCDM/Source/ElectraCDM/Private)（无公开测试用例）
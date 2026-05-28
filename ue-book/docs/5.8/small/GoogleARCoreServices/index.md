# Google ARCore Services

> Provide functionality in Google cross-platform ARCore services.

| 属性 | 值 |
|---|---|
| 中文名 | AR 云锚点服务 |
| 分类 | Augmented Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GoogleARCoreServices` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-28 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/Google/GoogleARCoreServices) | |

## 用途

这个插件提供 Google ARCore 的**云锚点（Cloud Anchor）**功能，解决多人共享 AR 体验的核心问题。

具体来说，它允许你：
1. **托管（Host）**：将本地 ARPin 上传到 Google 云端服务器，获取一个 CloudID
2. **解析（Resolve）**：通过 CloudID 在另一台设备上恢复同一位置的 ARPin

典型场景：两台手机对着同一个物理空间，通过云锚点可以实现**多人协作 AR**，例如一起在同一张桌子上放置虚拟物体。

**注意**：此插件默认禁用（`EnabledByDefault=false`），需要手动在插件管理器中启用。同时需要在项目设置中配置 Google ARCore API Key。

## 使用场景

- 你需要实现多人共享 AR 体验 → 用 CloudARPin 托管/解析锚点
- 你需要在不同设备间持久化 AR 空间标记 → 用 CloudARPin
- 你在开发 AR 协作应用（如多人 AR 游戏、AR 远程指导）→ 此插件提供底层支持
- 你需要在 Android/iOS 上使用 Google 的云服务 → 配置对应平台的 API Key

## 蓝图用法

所有核心功能都通过 `UGoogleARCoreServicesFunctionLibrary` 静态节点暴露，以及 `UCloudARPin` 实例的查询节点。

### 配置节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Config Google ARCore Services` | 配置云锚点模式（启用/禁用） | `UGoogleARCoreServicesFunctionLibrary` |

### 托管锚点（Host）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create And Host Cloud ARPin Latent Action` | 托管 ARPin 到云端（Latent，等待完成后触发） | `UGoogleARCoreServicesFunctionLibrary` |
| `Create And Host Cloud ARPin` | 托管 ARPin 到云端（立即返回，需轮询状态） | `UGoogleARCoreServicesFunctionLibrary` |

### 解析锚点（Resolve）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create And Resolve Cloud ARPin Latent Action` | 通过 CloudID 解析云端锚点（Latent） | `UGoogleARCoreServicesFunctionLibrary` |
| `Create And Resolve Cloud ARPin` | 通过 CloudID 解析云端锚点（立即返回） | `UGoogleARCoreServicesFunctionLibrary` |

### 管理节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Remove Cloud ARPin` | 从当前 ARSession 移除云锚点 | `UGoogleARCoreServicesFunctionLibrary` |
| `Get All Cloud ARPin` | 获取当前 ARSession 中所有云锚点 | `UGoogleARCoreServicesFunctionLibrary` |

### CloudARPin 查询节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cloud ID` | 获取云锚点的 CloudID 字符串 | `UCloudARPin` |
| `Get ARPin Cloud State` | 获取云锚点当前状态（成功/失败/进行中等） | `UCloudARPin` |

### 使用示例（蓝图描述）

**托管本地锚点到云端（Latent 方式）：**

```
[事件触发] → [Config Google ARCore Services]
    └─ ServiceConfig: ARPinCloudMode = Enabled
    
[ARPin 来自 AR 框架] → [Create And Host Cloud ARPin Latent Action]
    ├─ ARPinToHost: 你的本地 ARPin
    ├─ LifetimeInDays: 1
    ├─ OutHostingResult → [Branch] → 成功路径 / 失败路径
    └─ OutCloudARPin → [Get Cloud ID] → 打印/存储 CloudID
```

**解析云端锚点（Latent 方式）：**

```
[接收到 CloudID 字符串] → [Create And Resolve Cloud ARPin Latent Action]
    ├─ CloudId: "abc123..."
    ├─ OutAcquiringResult → [Branch]
    └─ OutCloudARPin → [Get AR Pin Cloud State] → [Switch on ECloudARPinCloudState]
        ├─ Success: 使用锚点放置虚拟物体
        └─ 其他错误状态: 显示错误信息
```

**非 Latent 方式（需要轮询）：**

```
[每帧 Tick] → [Create And Host Cloud ARPin]
    ├─ ARPinToHost: 你的本地 ARPin
    ├─ LifetimeInDays: 1
    ├─ OutTaskResult: Started（表示已开始）
    └─ OutCloudARPin → [Get ARPin Cloud State]
        └─ 如果 == Success: 读取 CloudID 并停止轮询
```

## C++ 用法

### 头文件引入

```cpp
#include "GoogleARCoreServicesTypes.h"
#include "GoogleARCoreServicesFunctionLibrary.h"
```

### 基本用法

**配置云锚点模式并托管 ARPin（Latent 方式）**

来源：`Source/GoogleARCoreServices/Public/GoogleARCoreServicesFunctionLibrary.h`

```cpp
// 1. 配置 ARCore Services，启用云锚点
FGoogleARCoreServicesConfig Config;
Config.ARPinCloudMode = EARPinCloudMode::Enabled;
UGoogleARCoreServicesFunctionLibrary::ConfigGoogleARCoreServices(Config);

// 2. 托管一个本地 ARPin 到云端（需要在蓝图中使用 Latent Action）
// C++ 中需要手动管理 FLatentActionInfo 或使用非 Latent 版本
EARPinCloudTaskResult TaskResult;
UCloudARPin* CloudPin = UGoogleARCoreServicesFunctionLibrary::CreateAndHostCloudARPin(
    LocalARPin,    // UARPin* - 本地追踪到的锚点
    1,             // int32 - 云锚点存活天数
    TaskResult     // OUT - 任务结果
);

// 3. 检查任务是否成功启动
if (TaskResult == EARPinCloudTaskResult::Started)
{
    // CloudPin 已创建，托管任务在后台进行
    // 需要后续轮询 GetARPinCloudState() 检查完成状态
}
```

### 进阶用法

**轮询云锚点状态并获取 CloudID**

来源：`Source/GoogleARCoreServices/Public/GoogleARCoreServicesTypes.h`

```cpp
// 假设 CloudPin 已通过 CreateAndHostCloudARPin 获取
void CheckCloudPinStatus(UCloudARPin* CloudPin)
{
    if (!CloudPin) return;

    // 获取当前云状态（每帧更新一次）
    ECloudARPinCloudState CloudState = CloudPin->GetARPinCloudState();

    switch (CloudState)
    {
    case ECloudARPinCloudState::Success:
    {
        // 托管成功，获取 CloudID 分享给其他设备
        FString CloudID = CloudPin->GetCloudID();
        UE_LOG(LogTemp, Log, TEXT("Cloud ARPin hosted! CloudID: %s"), *CloudID);
        break;
    }
    case ECloudARPinCloudState::InProgress:
        // 仍在处理中，下一帧再检查
        UE_LOG(LogTemp, Log, TEXT("Cloud ARPin hosting in progress..."));
        break;
    case ECloudARPinCloudState::ErrorNotAuthorized:
        // API Key 错误
        UE_LOG(LogTemp, Error, TEXT("Not authorized. Check your API key."));
        break;
    case ECloudARPinCloudState::ErrorResourceExhausted:
        // 配额用尽
        UE_LOG(LogTemp, Error, TEXT("API quota exhausted."));
        break;
    case ECloudARPinCloudState::ErrorHostingDatasetProcessingFailed:
        // 数据不足，需更多环境数据
        UE_LOG(LogTemp, Error, TEXT("Dataset processing failed. Gather more environment data."));
        break;
    default:
        // 其他错误状态
        UE_LOG(LogTemp, Warning, TEXT("Cloud state: %d"), (int)CloudState);
        break;
    }
}
```

**通过 CloudID 解析远程锚点**

来源：`Source/GoogleARCoreServices/Public/GoogleARCoreServicesFunctionLibrary.h`

```cpp
// 在另一台设备上，使用收到的 CloudID 解析锚点
FString ReceivedCloudID = TEXT("收到的 CloudID");
EARPinCloudTaskResult ResolveResult;

UCloudARPin* ResolvedPin = UGoogleARCoreServicesFunctionLibrary::CreateAndResolveCloudARPin(
    ReceivedCloudID,
    ResolveResult
);

if (ResolveResult == EARPinCloudTaskResult::Started)
{
    // 解析任务已启动
    // 后续轮询 ResolvedPin->GetARPinCloudState()
}

// 清理：移除不再需要的云锚点
// UGoogleARCoreServicesFunctionLibrary::RemoveCloudARPin(ResolvedPin);
```

**获取所有云锚点**

```cpp
TArray<UCloudARPin*> AllCloudPins = UGoogleARCoreServicesFunctionLibrary::GetAllCloudARPin();

for (UCloudARPin* Pin : AllCloudPins)
{
    UE_LOG(LogTemp, Log, TEXT("CloudPin - ID: %s, State: %d"),
        *Pin->GetCloudID(), (int)Pin->GetARPinCloudState());
}
```

## Demo 示例

一个完整的最小示例，演示如何配置、托管和轮询云锚点状态。

### MyCloudARComponent.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "GoogleARCoreServicesTypes.h"
#include "MyCloudARComponent.generated.h"

class UCloudARPin;

UCLASS(ClassGroup=(AR), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UMyCloudARComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyCloudARComponent();

    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;

    /** 托管本地 ARPin 到云端 */
    UFUNCTION(BlueprintCallable)
    void HostLocalPin(UARPin* LocalPin);

    /** 通过 CloudID 解析远程锚点 */
    UFUNCTION(BlueprintCallable)
    void ResolveRemotePin(const FString& CloudID);

    /** 云锚点状态变化时广播 */
    DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnCloudStateChanged, FString, CloudID,
        ECloudARPinCloudState, NewState);

    UPROPERTY(BlueprintAssignable)
    FOnCloudStateChanged OnCloudStateChanged;

private:
    void ConfigureServices();

    /** 需要轮询状态的云锚点 */
    UPROPERTY()
    TArray<UCloudARPin*> PendingPins;

    bool bConfigured = false;
};
```

### MyCloudARComponent.cpp

```cpp
#include "MyCloudARComponent.h"
#include "GoogleARCoreServicesFunctionLibrary.h"
#include "GoogleARCoreServicesTypes.h"

UMyCloudARComponent::UMyCloudARComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyCloudARComponent::BeginPlay()
{
    Super::BeginPlay();
    ConfigureServices();
}

void UMyCloudARComponent::ConfigureServices()
{
    FGoogleARCoreServicesConfig Config;
    Config.ARPinCloudMode = EARPinCloudMode::Enabled;
    
    if (UGoogleARCoreServicesFunctionLibrary::ConfigGoogleARCoreServices(Config))
    {
        bConfigured = true;
        UE_LOG(LogTemp, Log, TEXT("ARCore Services configured successfully."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to configure ARCore Services."));
    }
}

void UMyCloudARComponent::HostLocalPin(UARPin* LocalPin)
{
    if (!bConfigured || !LocalPin)
    {
        return;
    }

    EARPinCloudTaskResult TaskResult;
    UCloudARPin* CloudPin = UGoogleARCoreServicesFunctionLibrary::CreateAndHostCloudARPin(
        LocalPin, 1, TaskResult);

    if (TaskResult == EARPinCloudTaskResult::Started && CloudPin)
    {
        PendingPins.Add(CloudPin);
        UE_LOG(LogTemp, Log, TEXT("Cloud ARPin hosting started."));
    }
}

void UMyCloudARComponent::ResolveRemotePin(const FString& CloudID)
{
    if (!bConfigured || CloudID.IsEmpty())
    {
        return;
    }

    EARPinCloudTaskResult TaskResult;
    UCloudARPin* CloudPin = UGoogleARCoreServicesFunctionLibrary::CreateAndResolveCloudARPin(
        CloudID, TaskResult);

    if (TaskResult == EARPinCloudTaskResult::Started && CloudPin)
    {
        PendingPins.Add(CloudPin);
        UE_LOG(LogTemp, Log, TEXT("Cloud ARPin resolving started for: %s"), *CloudID);
    }
}

void UMyCloudARComponent::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    // 轮询所有待处理的云锚点状态
    for (int32 i = PendingPins.Num() - 1; i >= 0; --i)
    {
        UCloudARPin* Pin = PendingPins[i];
        if (!Pin)
        {
            PendingPins.RemoveAt(i);
            continue;
        }

        ECloudARPinCloudState State = Pin->GetARPinCloudState();

        // 广播状态变化
        OnCloudStateChanged.Broadcast(Pin->GetCloudID(), State);

        // 如果不再是进行中状态，移除出轮询列表
        if (State != ECloudARPinCloudState::NotHosted &&
            State != ECloudARPinCloudState::InProgress)
        {
            PendingPins.RemoveAt(i);

            if (State == ECloudARPinCloudState::Success)
            {
                UE_LOG(LogTemp, Log, TEXT("Cloud ARPin ready! ID: %s"), *Pin->GetCloudID());
            }
            else
            {
                UE_LOG(LogTemp, Warning, TEXT("Cloud ARPin failed with state: %d"), (int)State);
            }
        }
    }
}
```

## 模块依赖

根据插件的功能（ARCore 云服务集成），需要依赖 AR 相关模块。

| 模块 | 用途 |
|---|---|
| `GoogleARCoreBase` | Google ARCore 基础模块，提供 AR 会话和锚点底层接口 |
| `AugmentedReality` | UE5 AR 框架，提供 UARPin、UARSession 等核心类 |

## 编辑器设置

启用插件后，需要在 **项目设置 > Plugins > ARCore Services** 中配置 API Key：

| 设置项 | 说明 |
|---|---|
| `AndroidAPIKey` | Android 平台的 Google ARCore Cloud 服务 API Key |
| `IOSAPIKey` | iOS 平台的 Google ARCore Cloud 服务 API Key |

API Key 需要在 [Google Cloud Console](https://console.cloud.google.com/) 中创建并启用 ARCore Cloud Anchor API。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 |
| 2026-04-13 | `b905d146` | Fix/Silence unreachable code warnings | 修复不可达代码警告 |
| 2026-04-08 | `86879cf0` | Fix unreachable code warnings | 修复不可达代码警告 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复 printf 格式说明符 |
| 2025-03-27 | `7a3b70c6` | ARCoreServices breaks ARCore with vulkan | 修复 Vulkan 渲染下 ARCore 异常 |

### 维护评价

- **创建时间**：2019 年，已运行约 7 年
- **近期活动**：2026 年仍有更新，但均为**代码质量修复**（日志迁移、警告消除、格式修复），无功能性新增
- **维护状态**：**维护不活跃** — 最近 5 次提交全部是编译警告修复和基础设施迁移，无新功能开发
- **已知限制**：
  - 需要有效的 Google ARCore API Key 和 Cloud Anchor 配额
  - Cloud Anchor 功能依赖 Google 云服务，存在网络延迟
  - `UCloudARPin` 标记为 `Experimental`
  - 仅支持 Android 和 iOS，不支持桌面平台
- **推荐**：如果你需要多人共享 AR 体验且目标平台是移动端，仍然推荐使用。但需注意 Google Cloud Anchor API 可能有配额限制和费用。

⚠️ **注意**：该插件长期无功能性更新，依赖 Google 的 Cloud Anchor API 可能已更新。建议确认与最新 ARCore SDK 版本的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/Google/GoogleARCoreServices)
- [Google ARCore Cloud Anchor 文档](https://developers.google.com/ar/develop/cloud-anchors)
- [Google Cloud Console](https://console.cloud.google.com/)
# GooglePAD

> Google Play Asset Delivery for Android.

| 属性 | 值 |
|---|---|
| 中文名 | 谷歌资产交付 |
| 分类 | Android |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GooglePAD` (Runtime), `GooglePADEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-04-21 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GooglePAD) | |

## 用途

该插件封装了 Google Play Asset Delivery API，允许 UE 项目在 Android 平台上实现按需下载游戏资产（如关卡、模型、纹理包）。通过将大型资产从初始安装包（APK）中分离，可以显著减小应用首次下载的大小，并让玩家在需要时再下载所需内容。

## 使用场景

- 你的 Android 游戏体积过大，希望分包发布，减小初始下载大小。
- 你需要在游戏运行时动态下载新的可选内容（DLC、扩展包）。
- 你希望将大型资源（如4K贴图、额外音效包）与主程序分离，实现按需加载。

## 蓝图用法

`GooglePAD` 模块在蓝图中暴露了用于管理资产包的核心节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Check Asset Pack State` | 查询指定资产包的当前状态（已安装、已下载、需要下载等）。 | `UGooglePAD` |
| `Show Asset Pack Confirmation` | （如果适用）向用户显示系统级别的下载确认对话框。 | `UGooglePAD` |
| `Download Asset Pack` | 发起一个或多个资产包的后台下载请求。 | `UGooglePAD` |
| `Get Asset Pack Download Status` | 获取资产包的下载进度和大小信息。 | `UGooglePAD` |
| `Cancel Asset Pack Download` | 取消正在进行中的资产包下载。 | `UGooglePAD` |

### 使用示例（蓝图描述）

1.  使用“`Check Asset Pack State`”节点检查名为“`LargeTextures`”的资产包是否已就绪。
2.  如果状态为“需要下载”，则调用“`Download Asset Pack`”节点。
3.  同时，使用一个计时器或循环节点定期调用“`Get Asset Pack Download Status`”，获取下载进度并更新UI进度条。
4.  当状态变为“已安装”后，加载对应的资产。

## C++ 用法

### 头文件引入

```cpp
#include "GooglePAD.h"
```

### 基本用法

启动一个资产包的下载并轮询其状态。

```cpp
// 启动下载
const FString AssetPackName = TEXT(“MyLevelPack”);
UGooglePAD::CheckAssetPackState(AssetPackName, [&AssetPackName](const EGooglePADAssetPackState State) {
    if (State == EGooglePADAssetPackState::NotInstalled || State == EGooglePADAssetPackState::RequiresCellularDownloadPermission)
    {
        UGooglePAD::DownloadAssetPack(AssetPackName);
    }
});

// 在 Tick 或某个回调中查询进度
FString Name;
EGooglePADAssetPackStatus Status;
int64 BytesDownloaded;
int64 TotalBytesToDownload;
float DownloadProgress;

if (UGooglePAD::GetAssetPackDownloadStatus(AssetPackName, Status, BytesDownloaded, TotalBytesToDownload, DownloadProgress) == EGooglePADLocation::AssetPack)
{
    UE_LOG(LogTemp, Log, TEXT(“%s: Status=%d, Progress=%f”), *AssetPackName, static_cast<int32>(Status), DownloadProgress);
    if (Status == EGooglePADAssetPackStatus::Completed)
    {
        // 下载完成，可以安全加载资产
        UGooglePAD::GetAssetsPath(AssetPackName, /*...*/);
    }
}
```

### 进阶用法

结合 `GooglePADEditor` 模块，在打包时配置资产包映射，将特定资产（如整个文件夹或资产列表）分配到命名的资产包中。

## Demo 示例

以下是一个最小的 C++ Actor 示例，演示了检查并下载一个资产包。

```cpp
// GooglePADDemoActor.h
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “GooglePAD.h” // 关键头文件
#include “GooglePADDemoActor.generated.h”

UCLASS()
class AGooglePADDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AGooglePADDemoActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY(EditAnywhere, Category = “GooglePAD”)
    FString TargetAssetPackName = “MyAssetPack”;

    void CheckAndDownloadPack();
    void PollDownloadStatus();

    bool bDownloadInitiated = false;
};
```

```cpp
// GooglePADDemoActor.cpp
#include “GooglePADDemoActor.h”
#include “GooglePAD.h” // 关键头文件

AGooglePADDemoActor::AGooglePADDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AGooglePADDemoActor::BeginPlay()
{
    Super::BeginPlay();
    CheckAndDownloadPack();
}

void AGooglePADDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (bDownloadInitiated)
    {
        PollDownloadStatus();
    }
}

void AGooglePADDemoActor::CheckAndDownloadPack()
{
    UGooglePAD::CheckAssetPackState(TargetAssetPackName, [this](const EGooglePADAssetPackState State)
    {
        UE_LOG(LogTemp, Log, TEXT(“%s Current State: %d”), *TargetAssetPackName, static_cast<int32>(State));

        if (State == EGooglePADAssetPackState::NotInstalled ||
            State == EGooglePADAssetPackState::RequiresCellularDownloadPermission)
        {
            EGooglePADRequestAccess Result = UGooglePAD::DownloadAssetPack(TargetAssetPackName);
            if (Result == EGooglePADRequestAccess::Granted)
            {
                UE_LOG(LogTemp, Log, TEXT(“Download requested for: %s”), *TargetAssetPackName);
                bDownloadInitiated = true;
            }
        }
        else if (State == EGooglePADAssetPackState::Installed)
        {
            UE_LOG(LogTemp, Log, TEXT(“%s is already installed.”), *TargetAssetPackName);
        }
    });
}

void AGooglePADDemoActor::PollDownloadStatus()
{
    EGooglePADAssetPackStatus Status;
    int64 BytesDownloaded;
    int64 TotalBytes;
    float Progress;

    EGooglePADLocation Location = UGooglePAD::GetAssetPackDownloadStatus(
        TargetAssetPackName, Status, BytesDownloaded, TotalBytes, Progress);

    if (Location == EGooglePADLocation::AssetPack)
    {
        UE_LOG(LogTemp, Log, TEXT(“%s: Status=%d, Progress=%f%% (%lld/%lld bytes)”),
            *TargetAssetPackName, static_cast<int32>(Status), Progress * 100.f,
            BytesDownloaded, TotalBytes);

        if (Status == EGooglePADAssetPackStatus::Completed)
        {
            UE_LOG(LogTemp, Log, TEXT(“%s download completed.”), *TargetAssetPackName);
            bDownloadInitiated = false;
            // 可以在这里获取资产路径并加载
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Android` | Android 平台核心支持。 |
| `Launch` | 包含 Android JNI 交互和启动逻辑。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的日志宏UE_LOG迁移到新的UE_LOGF宏。 |
| 2025-09-17 | `2e280ccd` | Update GooglePAD to 1.15.4 / 2.3.0 | 更新了内置的GooglePAD SDK版本到1.15.4。 |
| 2025-09-02 | `7d7255e0` | Registered JNI functions. Made JNI classes for Java classes. Added thread_local Ue::Jni::Env global. | 重构了底层JNI交互，改进了线程安全性。 |
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 代码生成宏更新，符合UE最新规范。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 构建系统相关修复，确保符号正确导出。 |

### 维护评价

**活跃维护**。该插件创建于2020年，作为Google Play Asset Delivery的官方集成，一直是Epic维护的Android平台关键组件。从git历史看，它在2025-2026年仍有持续、实质性的更新，包括SDK版本升级、底层重构和构建系统优化。这表明插件与Google服务的版本保持同步，且代码库在持续改进中。推荐在面向Android平台且需要按需下载功能的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GooglePAD)
- [Google Play Asset Delivery 官方文档](https://developer.android.com/guide/playcore/asset-delivery)
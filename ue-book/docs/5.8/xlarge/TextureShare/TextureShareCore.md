# Texture Share

> Share textures and data between processes

| 属性 | 值 |
|---|---|
| 中文名 | 纹理共享 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、示例场景） |
| 模块 | `TextureShareCore` (Runtime), `TextureShare` (Runtime), `TextureShareDisplayCluster` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-06-25 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TextureShare) | |

## 用途

TextureShare 插件提供了一套完整的**跨进程纹理与数据共享框架**，通过操作系统级别的共享内存（IPC Shared Memory）和同步原语（Mutex/Event），在多个独立进程之间实时传输 GPU 纹理资源和自定义数据。

它解决的核心问题是：在虚拟制片（Virtual Production）场景中，多个应用程序（如 Unreal Engine 节点、外部 SDK 程序、nDisplay 集群节点）需要**零拷贝或低延迟地共享渲染结果和场景数据**。传统的做法是通过网络或磁盘文件传输纹理，延迟高且带宽受限；TextureShare 则利用 Windows 的命名共享内存（Named Shared Memory）、跨进程 Mutex 和 NT Handle 共享机制，实现了 GPU 级别的直接资源传递。

该插件的主要设计目标：
- **进程间纹理共享**：支持 D3D11、D3D12、Vulkan 三种图形 API 的纹理共享，包括跨 GPU 适配器（Cross-Adapter）共享
- **帧级同步**：提供精细的帧同步屏障（Barrier）机制，支持游戏线程和渲染线程各自的同步步骤
- **nDisplay 集成**：作为 DisplayCluster 模块的底层传输层，为多节点渲染集群提供纹理同步能力
- **SDK 兼容**：通过二进制兼容的序列化结构体，允许外部 C++ SDK 程序直接参与纹理共享

## 使用场景

- 你在使用 **nDisplay** 进行多显示器/多节点虚拟制片渲染 → 用 TextureShare 作为底层纹理同步通道
- 你需要在 **UE 和外部应用程序**（如媒体服务器、合成工具）之间实时共享渲染输出 → 用 TextureShare 的 SDK 模式
- 你有 **多 GPU 系统**（如 NVLink/SLI），需要在不同 GPU 之间传输渲染纹理 → 用 TextureShare 的 Cross-Adapter 资源支持
- 你需要在 **多个 UE 实例之间**同步场景数据和纹理（如集群渲染的从节点）→ 用 TextureShare 的 UE2UE 连接模式

## 蓝图用法

> ⚠️ 注意：TextureShare 的大部分核心逻辑运行在 C++ 层，蓝图接口主要通过 `TextureShare` 模块暴露。以下节点基于源码中的 BlueprintCallable 标注提取。

### 核心节点

TextureShare 模块（非 Core 模块）封装了蓝图友好的 Actor/Component 接口。基于 Core 模块的接口设计，蓝图可用的核心操作包括：

| 功能 | 说明 | 所在模块 |
|---|---|---|
| 创建纹理共享对象 | 通过唯一的 ShareName 创建可共享对象 | `TextureShare` |
| 开始/结束会话 | 管理 IPC 会话生命周期 | `TextureShare` |
| 帧同步 | BeginFrameSync → FrameSync → EndFrameSync 三阶段同步 | `TextureShare` |
| 读取/写入纹理 | 在同步步骤中声明纹理的读写操作 | `TextureShare` |

### 使用示例（蓝图描述）

典型的蓝图工作流：

1. **创建 TextureShare Actor**：放置到场景中，设置唯一的 ShareName
2. **配置同步设置**：在细节面板设置进程类型、允许/禁止连接的进程名列表
3. **声明资源**：在事件图表中，调用节点声明要共享的纹理（资源名、读写方向、视图ID）
4. **帧同步流程**：
   - 在 Tick 或 BeginPlay 中调用 `BeginSession`
   - 在 Tick 中调用 `BeginFrameSync` → `FrameSync(指定步骤)` → `EndFrameSync`
   - 渲染线程同步通过代理数据完成

## C++ 用法

### 头文件引入

```cpp
#include "ITextureShareCoreAPI.h"
#include "ITextureShareCoreObject.h"
```

### 基本用法

以下代码展示了如何创建纹理共享对象、配置同步设置并执行帧同步：

```cpp
// 来源: ITextureShareCoreAPI.h + ITextureShareCoreObject.h

// 1. 获取 TextureShareCore API 实例
ITextureShareCoreAPI& TextureShareAPI = ITextureShareCoreAPI::Get();

// 2. 设置本地进程名称
TextureShareAPI.SetProcessName(TEXT("MyExternalApp"));

// 3. 创建纹理共享对象（相同 ShareName 的对象会尝试连接）
TSharedPtr<ITextureShareCoreObject, ESPMode::ThreadSafe> ShareObject =
    TextureShareAPI.GetOrCreateCoreObject(
        TEXT("MyShareSession"),
        ETextureShareProcessType::SDK  // 外部 SDK 进程
    );

if (ShareObject.IsValid())
{
    // 4. 配置同步设置
    FTextureShareCoreSyncSettings SyncSettings;
    SyncSettings.FrameConnectionSettings.MinValue = 1;  // 至少需要1个连接进程
    SyncSettings.TimeoutSettings.FrameSyncTimeOut = 2000; // 2秒超时
    ShareObject->SetSyncSettings(SyncSettings);

    // 5. 开始会话
    if (ShareObject->BeginSession())
    {
        // 6. 帧同步循环
        if (ShareObject->BeginFrameSync())
        {
            // 在各个同步步骤执行数据传输
            ShareObject->FrameSync(ETextureShareSyncStep::FrameSetupBegin);

            // 获取已连接的远程进程列表
            auto ConnectedObjects = ShareObject->GetConnectedInterprocessObjects();

            ShareObject->FrameSync(ETextureShareSyncStep::FrameEnd);
            ShareObject->EndFrameSync();
        }
    }
}
```

### 帧同步步骤详解

TextureShare 提供了精细的帧同步步骤，分为游戏线程和渲染线程两组：

```cpp
// 来源: TextureShareCoreEnums.h

// === 游戏线程同步步骤 ===
// ETextureShareSyncStep::FrameBegin       — 帧开始
// ETextureShareSyncStep::FrameSetupBegin  — 帧设置开始
// ETextureShareSyncStep::FrameSetupEnd    — 帧设置结束
// ETextureShareSyncStep::FrameEnd         — 帧结束

// === 渲染线程同步步骤 ===
// ETextureShareSyncStep::FrameProxyBegin              — 渲染线程帧开始
// ETextureShareSyncStep::FrameSceneFinalColorBegin     — 场景最终颜色开始
// ETextureShareSyncStep::FrameProxyRenderBegin         — 渲染开始
// ETextureShareSyncStep::FrameProxyPostRenderBegin     — 后处理开始
// ETextureShareSyncStep::FrameProxyEnd                 — 渲染线程帧结束
```

### 进阶用法

#### 声明和使用纹理资源

```cpp
// 来源: TextureShareCoreContainers_ResourceDesc.h, TextureShareCoreContainers_ResourceRequest.h

// 声明要写入的纹理资源
FTextureShareCoreViewDesc ViewDesc(TEXT("MainView"), ETextureShareEyeType::Default);
FTextureShareCoreResourceDesc ResourceDesc(
    TEXT("SceneColor"),                    // 资源名称
    ViewDesc,                              // 视图描述
    ETextureShareTextureOp::Write,         // 写入操作
    ETextureShareSyncStep::FrameSceneFinalColorBegin  // 同步步骤
);

// 在帧同步时，获取本地数据容器并添加资源请求
FTextureShareCoreData& Data = ShareObject->GetData();
FTextureShareCoreResourceRequest ResourceRequest(ResourceDesc);
Data.ResourceRequests.Add(ResourceRequest);

// 执行同步（资源句柄将在渲染线程中通过 ProxyData 交换）
ShareObject->FrameSync(ETextureShareSyncStep::FrameSceneFinalColorBegin);

// 在渲染线程中，获取代理数据
FTextureShareCoreProxyData& ProxyData = ShareObject->GetProxyData_RenderThread();
for (const FTextureShareCoreResourceHandle& Handle : ProxyData.ResourceHandles)
{
    // 使用资源句柄进行 GPU 资源共享
    // D3D11: ITextureShareCoreD3D11ResourcesCache::OpenSharedResource()
    // D3D12: ITextureShareCoreD3D12ResourcesCache::OpenSharedResource()
    // Vulkan: ITextureShareCoreVulkanResourcesCache::OpenSharedResource()
}
```

#### 线程安全互斥锁

```cpp
// 来源: ITextureShareCoreObject.h

// 在多线程场景中保护共享数据
ShareObject->LockThreadMutex(ETextureShareThreadMutex::GameThread);
// ... 访问共享数据 ...
ShareObject->UnlockThreadMutex(ETextureShareThreadMutex::GameThread);
```

#### 场景数据共享

```cpp
// 来源: TextureShareCoreContainers_SceneData.h

// 在渲染线程中设置场景视图数据
FTextureShareCoreSceneViewData SceneViewData(TEXT("MainView"), ETextureShareEyeType::Default);

// 填充视图矩阵
SceneViewData.View.ViewMatrices.ViewMatrix = ViewInfo.ViewMatrix;
SceneViewData.View.ViewMatrices.ProjectionMatrix = ViewInfo.ProjectionMatrix;
SceneViewData.View.ViewLocation = ViewInfo.ViewLocation;
SceneViewData.View.FOV = ViewInfo.FOV;

// 填充视图族信息
SceneViewData.ViewFamily.GameTime.RealTimeSeconds = GetWorld()->GetRealTimeSeconds();
SceneViewData.ViewFamily.FrameNumber = GFrameNumber;

FTextureShareCoreProxyData& ProxyData = ShareObject->GetProxyData_RenderThread();
ProxyData.SceneData.Add(SceneViewData);
```

#### 回调事件监听

```cpp
// 来源: ITextureShareCoreCallbacks.h

ITextureShareCoreCallbacks& Callbacks = TextureShareAPI.GetCallbacks();

// 监听帧同步事件
Callbacks.OnTextureShareCoreBeginFrameSync().AddLambda(
    [](ITextureShareCoreObject& Object)
    {
        UE_LOG(LogTextureShare, Log, TEXT("BeginFrameSync: %s"), *Object.GetName());
    }
);

// 监听渲染线程帧同步
Callbacks.OnTextureShareCoreFrameSync_RenderThread().AddLambda(
    [](ITextureShareCoreObject& Object, const ETextureShareSyncStep Step)
    {
        UE_LOG(LogTextureShare, Log, TEXT("RenderThread SyncStep: %d"), (int32)Step);
    }
);
```

## Demo 示例

### 最小完整示例：跨进程纹理共享

```cpp
// TextureShareExample.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ITextureShareCoreAPI.h"
#include "ITextureShareCoreObject.h"
#include "TextureShareExample.generated.h"

UCLASS()
class ATextureShareExample : public AActor
{
    GENERATED_BODY()

public:
    ATextureShareExample();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // 共享名称（两个进程必须使用相同名称才能连接）
    UPROPERTY(EditAnywhere, Category = "TextureShare")
    FString ShareName = TEXT("MySharedTexture");

    // 进程名称
    UPROPERTY(EditAnywhere, Category = "TextureShare")
    FString ProcessName = TEXT("UE_Process");

private:
    TSharedPtr<ITextureShareCoreObject, ESPMode::ThreadSafe> SharedObject;
    bool bSessionActive = false;
};
```

```cpp
// TextureShareExample.cpp
#include "TextureShareExample.h"
#include "ITextureShareCoreAPI.h"

ATextureShareExample::ATextureShareExample()
{
    PrimaryActorTick.bCanEverTick = true;
}

void ATextureShareExample::BeginPlay()
{
    Super::BeginPlay();

    // 获取 TextureShareCore API
    ITextureShareCoreAPI& API = ITextureShareCoreAPI::Get();

    // 设置进程名
    API.SetProcessName(ProcessName);

    // 创建共享对象
    SharedObject = API.GetOrCreateCoreObject(
        ShareName,
        ETextureShareProcessType::UE2UE
    );

    if (SharedObject.IsValid())
    {
        // 配置同步设置
        FTextureShareCoreSyncSettings Settings;
        Settings.FrameConnectionSettings.MinValue = 1;
        Settings.TimeoutSettings.FrameBeginTimeOut = 5000;
        Settings.TimeoutSettings.FrameSyncTimeOut = 2000;
        SharedObject->SetSyncSettings(Settings);

        // 启动会话
        bSessionActive = SharedObject->BeginSession();
    }
}

void ATextureShareExample::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!bSessionActive || !SharedObject.IsValid())
    {
        return;
    }

    // 帧同步流程
    if (SharedObject->BeginFrameSync())
    {
        // 声明要写入的场景颜色
        FTextureShareCoreData& Data = SharedObject->GetData();

        FTextureShareCoreViewDesc ViewDesc(TEXT("SceneView"));
        FTextureShareCoreResourceDesc ResDesc(
            TEXT("SceneColor"),
            ViewDesc,
            ETextureShareTextureOp::Write,
            ETextureShareSyncStep::FrameSceneFinalColorBegin
        );
        Data.ResourceRequests.Add(FTextureShareCoreResourceRequest(ResDesc));

        // 在游戏线程同步步骤执行同步
        SharedObject->FrameSync(ETextureShareSyncStep::FrameSetupBegin);
        SharedObject->FrameSync(ETextureShareSyncStep::FrameEnd);

        SharedObject->EndFrameSync();

        // 检查已连接的远程进程
        auto Connected = SharedObject->GetConnectedInterprocessObjects();
        if (Connected.Num() > 0)
        {
            UE_LOG(LogTemp, Log, TEXT("Connected to %d remote processes"), Connected.Num());
        }
    }
}

void ATextureShareExample::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (SharedObject.IsValid())
    {
        SharedObject->EndSession();
        SharedObject->RemoveObject();
        SharedObject.Reset();
    }

    bSessionActive = false;
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `nDisplay` | DisplayCluster 集成（TextureShareDisplayCluster 模块依赖） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

> **平台限制**：仅支持 Win64 平台，依赖 Windows 的命名共享内存（Named Shared Memory）、跨进程 Mutex 和 NT Handle 机制。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复函数类型转换警告，兼容 MSVC 和 Clang 编译器 |
| 2026-04-16 | `270dc64a` | Fix unreachable code warnings | 修复不可达代码警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到新的 UE_LOGF 宏 |
| 2026-03-18 | `c8d86942` | Deprecate more unused includes from public rendering headers. | 清理公共渲染头文件中未使用的 include |
| 2026-03-02 | `c3f81430` | VulkanRHI: Remove extensions that don't need to be manually loaded anymore from plugin startup: | 移除 VulkanRHI 中不再需要手动加载的扩展 |

### 维护评价

- **维护状态**：**维护中** — 最近 3 个月内持续有更新，但以编译警告修复和代码清理为主，无功能性新增
- **实验性标记**：`.uplugin` 中 `IsBetaVersion=true`，`EnabledByDefault=false`，表明此插件仍处于实验阶段
- **代码规模**：172 个源文件，架构完整且层次分明（Core → IPC → Object → DisplayCluster），代码质量较高
- **活跃度**：自 2022 年创建以来持续维护，近期更新主要是编译器兼容性修复，非功能性变更
- **已知限制**：
  - 仅支持 Win64 平台
  - 共享内存对象数量上限为 256（`MaxNumberOfInterprocessObject`）
  - 单个对象数据序列化区域上限为 32KB（`MaxInterprocessObjectDataSize`）
  - 进程类型连接规则严格：UE 实例之间默认不可见，需使用 `UE2UE` 类型
- **推荐程度**：⭐⭐⭐ 如果你在做 nDisplay 虚拟制片项目，此插件是必经之路；如果是独立使用，需注意其实验性质和 Win64 限制

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TextureShare)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TextureShare/Source/TextureShareCore/Private/Tests)（如有）
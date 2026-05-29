# Texture Share

> Share textures and data between processes（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 纹理共享 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例、测试资源） |
| 模块 | `TextureShareCore` (Runtime), `TextureShare` (Runtime), `TextureShareDisplayCluster` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-06-25 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TextureShare) | |

## 用途

TextureShare 插件提供了一套在多个进程（包括多个 Unreal Engine 实例、外部应用程序或 nDisplay 集群节点）之间实时共享 GPU 纹理资源和自定义数据的完整框架。它解决的核心问题是：如何在虚拟制片、多机渲染、实时合成等复杂工作流中，实现不同软件或硬件之间的像素级和数据级同步。

该插件不仅封装了底层的进程间通信（IPC）和跨 GPU 传输机制，还通过与 UE 渲染管线的深度集成（场景视图扩展、帧同步回调等），允许在渲染线程的特定阶段精确控制纹理的读取和写入，从而实现了高效的、低延迟的实时数据交换。它特别适用于需要多路视频输出、实时光效合成或与外部控制软件（如 TouchDesigner、Notch）交互的场景。

## 使用场景

- **虚拟制片 (Virtual Production)**：在 nDisplay 多机多屏渲染系统中，同步不同节点间的场景纹理、深度图或最终合成画面。
- **实时合成 (Real-time Compositing)**：将 UE 的渲染结果实时发送到外部合成软件（如 After Effects, Nuke 的实时预览），或接收外部视频信号进行实时抠像合成。
- **交互式媒体艺术**：控制多个 UE 实例或与 Processing、TouchDesigner 等工具同步视觉内容。
- **硬件集成**：与支持共享内存或特定 IPC 机制的专用硬件（如 LED 墙控制器、信号处理器）交换渲染数据。

## 蓝图用法

插件提供了基于 UObject 的蓝图友好封装，主要通过 `UTextureShareWorldSubsystem` 和 `UTextureShareObject` 来操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get TextureShare` | 获取当前世界的纹理共享系统接口 | `UTextureShareWorldSubsystem` |
| `Get or Create TextureShare Object` | 通过唯一名称获取或创建一个纹理共享对象 | `UTextureShare` |
| `Remove TextureShare Object` | 移除一个指定的纹理共享对象 | `UTextureShare` |
| `Send Custom Data` | 向远程进程发送键值对形式的自定义数据 | `UTextureShareObject` |

### 使用示例（蓝图描述）

1.  **初始化**：在 Actor 的 `BeginPlay` 中，通过 `Get TextureShare` 节点获取 `UTextureShare` 对象，然后调用 `Get or Create TextureShare Object` 创建一个名为 “MyShare” 的共享对象。将返回的对象引用保存到变量中。
2.  **配置对象**：在创建的对象上，设置 `Desc` 属性中的 `ShareName` 和同步超时。将需要发送的本地纹理（如 `SceneCaptureComponent` 的输出）和接收用的渲染目标（`RenderTarget`）分别添加到 `Textures.SendTextures` 和 `Textures.ReceiveTextures` 数组中。
3.  **发送数据**：在每一帧的 Tick 中，可以调用 `Send Custom Data` 节点，传入一个 `TMap<String, String>`，用于传递时间码、元数据等信息。
4.  **接收数据**：在 Tick 中，可以读取对象 `CustomData` 属性中的 `ReceivedParameters`，以获取远程进程发来的自定义数据。
5.  **同步与清理**：插件内部通过 `UTextureShareWorldSubsystem` 的 Tick 自动管理帧同步和资源传输。在 `EndPlay` 中调用 `Remove TextureShare Object` 清理资源。

## C++ 用法

### 头文件引入

```cpp
// 核心模块接口
#include "ITextureShare.h"
#include "ITextureShareAPI.h"

// 对象与数据类型
#include "ITextureShareObject.h"
#include "ITextureShareObjectProxy.h"
#include "TextureShareBlueprintContainersBase.h" // 用于蓝图结构体

// 用于游戏对象配置
#include "TextureShareObject.h" // 若直接操作C++对象
```

### 基本用法

以下是一个在游戏 Actor 中创建和使用纹理共享对象的基本模式。

```cpp
// MyActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "ITextureShareObject.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()
public:
    AMyActor();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void Tick(float DeltaTime) override;

private:
    // 持有纹理共享对象的指针
    TSharedPtr<ITextureShareObject> TextureShareObject;
};
```

```cpp
// MyActor.cpp
#include "MyActor.h"
#include "ITextureShareAPI.h"
#include "ITextureShareModule.h"
#include "TextureShareBlueprintContainersBase.h"

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 获取API
    if (ITextureShareModule* Module = FModuleManager::GetModulePtr<ITextureShareModule>("TextureShare"))
    {
        ITextureShareAPI& API = Module->GetTextureShareAPI();

        // 2. 创建或获取共享对象 (名称不区分大小写)
        TextureShareObject = API.GetOrCreateObject(TEXT("MyActorShare"));
        if (TextureShareObject)
        {
            // 3. 配置同步设置
            FTextureShareCoreSyncSettings SyncSettings;
            SyncSettings.ConnectionSettings.ConnectTimeout = 5000;
            SyncSettings.FrameSyncSettings.SyncStep = ETextureShareSyncStep::FrameProxyPreRender;
            TextureShareObject->SetSyncSetting(SyncSettings);

            // 4. 开始会话 (可指定视口，通常为nullptr)
            TextureShareObject->BeginSession(nullptr);
        }
    }
}

void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (TextureShareObject && TextureShareObject->IsSessionActive())
    {
        // 5. 帧同步: 这会触发远程进程的数据交换
        TextureShareObject->BeginFrameSync();

        // 在此处可以访问和修改共享数据
        FTextureShareCoreData& CoreData = TextureShareObject->GetCoreData();
        // ... 例如，写入一些元数据

        // 进行具体的同步步骤
        TextureShareObject->FrameSync(ETextureShareSyncStep::FrameProxyPreRender);

        // 6. 获取接收到的数据
        TArray<FTextureShareCoreObjectData> ReceivedData = TextureShareObject->GetReceivedCoreObjectData();
        for (const FTextureShareCoreObjectData& ObjectData : ReceivedData)
        {
            // 处理从其他进程接收的数据
            // ...
        }

        TextureShareObject->EndFrameSync();
    }
}

void AMyActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (TextureShareObject)
    {
        // 7. 结束会话并清理
        TextureShareObject->EndSession();
        TextureShareObject.Reset();
    }
    Super::EndPlay(EndPlayReason);
}
```

### 进阶用法

进阶用法涉及渲染线程的资源操作和自定义上下文，通常用于实现自定义的纹理共享逻辑。

1.  **渲染线程纹理共享**：在渲染线程（如通过场景视图扩展或渲染线程回调）中，使用 `ITextureShareObjectProxy` 接口共享 RHI 纹理。
    ```cpp
    // 在某个渲染线程回调中
    void MyRenderCallback(FRHICommandListImmediate& RHICmdList, const ITextureShareObjectProxy& ObjectProxy)
    {
        if (ObjectProxy.IsActive_RenderThread() && ObjectProxy.IsFrameSyncActive_RenderThread())
        {
            // 共享一个 RHITexture
            FRHITexture* MyTexture = ...; // 获取要共享的纹理
            FTextureShareCoreResourceDesc ResourceDesc;
            ResourceDesc.TextureDesc.Name = TEXT("SharedSceneColor");
            ResourceDesc.SynchronizeResource = true;

            FTextureShareColorDesc ColorDesc(2.2f); // 指定 gamma

            // 发送纹理
            ObjectProxy.ShareResource_RenderThread(
                RHICmdList,
                ResourceDesc,
                MyTexture,
                ColorDesc,
                0 /*GPU Index*/,
                nullptr /*共享整个纹理，或指定区域*/
            );
        }
    }
    ```

2.  **使用自定义上下文 (`ITextureShareContext`)**：通过继承 `ITextureShareContext`，你可以为你的纹理共享对象创建自定义的生命周期和回调处理逻辑，避免与全局回调冲突。
    ```cpp
    class FMyCustomContext : public ITextureShareContext
    {
    public:
        // 注册你的自定义游戏线程回调
        virtual void RegisterTextureShareContextCallbacks() override
        {
            // 在此订阅需要的全局回调
            // 例如: ITextureShareCallbacks::Get().OnTextureShareBeginFrameSync().AddRaw(this, &FMyCustomContext::OnBeginSync);
        }

        virtual void UnregisterTextureShareContextCallbacks() override
        {
            // 取消订阅
        }

        virtual FName GetRTTI() const override { return TEXT("MyCustomContext"); }

    private:
        void OnBeginSync(ITextureShareObject& Object)
        {
            // 检查这个对象是否属于“我”的实现
            if (Object.GetTextureShareContext() && Object.GetTextureShareContext()->IsA(FMyCustomContext()))
            {
                // 执行你的自定义逻辑
            }
        }
    };

    // 在创建对象时设置上下文
    TSharedPtr<ITextureShareObject> MyObject = API.GetOrCreateObject(TEXT("MyObj"));
    TSharedPtr<FMyCustomContext> MyContext = MakeShared<FMyCustomContext>();
    MyObject->SetTextureShareContext(MyContext);
    ```

## Demo 示例

一个最小的、可运行的纹理共享对象创建和数据收发示例。

```cpp
// TextureShareDemoActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "ITextureShareObject.h"
#include "TextureShareDemoActor.generated.h"

UCLASS()
class ATextureShareDemoActor : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(EditAnywhere, Category = "TextureShare")
    FString ShareName = TEXT("DemoShare");

private:
    TSharedPtr<ITextureShareObject> ShareObject;
};
```

```cpp
// TextureShareDemoActor.cpp
#include "TextureShareDemoActor.h"
#include "ITextureShareAPI.h"
#include "ITextureShareModule.h"

void ATextureShareDemoActor::BeginPlay()
{
    Super::BeginPlay();
    ITextureShareAPI& API = ITextureShareModule::Get().GetTextureShareAPI();
    ShareObject = API.GetOrCreateObject(ShareName);
    if (ShareObject)
    {
        ShareObject->BeginSession();
    }
}

void ATextureShareDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (!ShareObject) return;

    ShareObject->BeginFrameSync();

    // 发送自定义数据
    FTextureShareCoreData& CoreData = ShareObject->GetCoreData();
    // 假设我们发送当前时间
    FString TimeKey = TEXT("CurrentTime");
    FString TimeValue = FString::Printf(TEXT("%f"), GetWorld()->GetTimeSeconds());
    CoreData.CustomData.Add(TimeKey, TimeValue);

    // 执行主要同步
    ShareObject->FrameSync(ETextureShareSyncStep::FrameProxyPreRender);

    // 接收来自其他进程的数据
    TArray<FTextureShareCoreObjectData> Received = ShareObject->GetReceivedCoreObjectData();
    for (const auto& ObjData : Received)
    {
        for (const auto& Pair : ObjData.Data.CustomData)
        {
            if (Pair.Key == TimeKey)
            {
                UE_LOG(LogTemp, Log, TEXT("Received remote time: %s"), *Pair.Value);
            }
        }
    }

    ShareObject->EndFrameSync();
}

void ATextureShareDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (ShareObject)
    {
        ShareObject->EndSession();
        ShareObject.Reset();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

从 `Build.cs` 的依赖关系推断，使用此插件时，你的模块通常需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `TextureShareCore` | 底层进程间通信和纹理共享的核心库 |
| `TextureShare` | UE 集成层，提供游戏线程/渲染线程 API、蓝图封装和世界子系统 |
| `RenderCore` | 访问 `FRHICommandListImmediate`, `FRDGBuilder` 等渲染核心类型 |
| `RHI` | 访问 `FRHITexture` 等 RHI 资源类型 |
| `Renderer` | 若需要通过场景视图扩展 (`FSceneViewExtensionBase`) 集成 |

*注意：标准依赖如 Core, CoreUObject, Engine 等已省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复跨编译器（MSVC/Clang）的函数类型转换警告。 |
| 2026-04-16 | `270dc64a` | Fix unreachable code warnings | 修复“不可达代码”的编译器警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移到新的 UE_LOGF 格式。 |
| 2026-03-18 | `c8d86942` | Deprecate more unused includes from public rendering headers. | 从公共渲染头文件中移除更多未使用的包含。 |
| 2026-03-02 | `c3f81430` | VulkanRHI: Remove extensions that don't need to be manually loaded anymore from plugin startup: | VulkanRHI：从插件启动中移除不再需要手动加载的扩展。 |

### 维护评价

- **创建时间**：2022年6月，属于较新的虚拟制片基础设施。
- **近期活动**：最近一次提交在2026年5月，但全部内容均为代码质量提升、警告修复和头文件清理，**没有新的功能更新或重大重构**。
- **维护状态**：**不活跃**。自创建以来的近一年内，没有实质性的功能增强或API演进。
- **已知问题**：插件处于实验性（Beta）阶段，默认未启用。其复杂的多线程架构（游戏线程/渲染线程交互）和底层RHI操作可能带来调试困难。
- **推荐使用**：如果你正在搭建 **虚拟制片或多机渲染** 管线，并且需要稳定的进程间纹理共享功能，此插件是官方提供的基础方案，值得一试。但应意识到其“实验性”标签，且近期无活跃开发。对于新的项目，建议评估其是否满足长期维护需求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TextureShare)
- [官方文档]() （无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TextureShare/Source/TextureShare/Private/Tests) （示例路径，需验证）
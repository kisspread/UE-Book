# Texture Share

> Share textures and data between processes

| 属性 | 值 |
|---|---|
| 中文名 | 纹理共享 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例资产） |
| 模块 | `TextureShareCore` (Runtime), `TextureShare` (Runtime), `TextureShareDisplayCluster` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-06-25 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TextureShare) | |

## 用途

TextureShare 是一个为虚拟制作（Virtual Production）场景设计的插件，旨在解决跨进程的实时纹理和数据共享问题。其核心目标是让不同的应用程序（如多个 Unreal Engine 实例、外部渲染器、合成软件等）能够高效、同步地共享纹理资源和自定义数据。

该插件的存在解决了虚拟制作中多设备协同渲染、多应用同步（例如 nDisplay 多节点渲染）以及与外部工具（如 DaVinci Resolve、Nuke 等）进行数据交换的需求。

## 使用场景

- **多机位/多应用渲染**：你需要在不同的显示器或应用中同步显示相同的纹理或视频源（如虚拟摄像机画面）。
- **nDisplay 集成**：你正在使用 nDisplay 进行多屏幕或 CAVE 环境渲染，需要在不同渲染节点间共享纹理和数据。
- **外部合成**：你需要将 Unreal Engine 中的渲染结果实时输出到外部合成软件进行后期处理，或反之。
- **自定义数据通道**：你需要在进程间传递自定义的数据（如变换矩阵、控制信号等），而不仅仅是纹理。

## 模块概览

| 模块 | 类型 | 简述 |
|---|---|---|
| `TextureShareCore` | Runtime | 核心共享库，提供平台无关的进程间通信（IPC）、共享纹理管理和同步机制。 |
| `TextureShare` | Runtime | Unreal Engine 运行时模块，封装核心功能为 UE 内容，提供易于使用的组件和蓝图 API。 |
| `TextureShareDisplayCluster` | Runtime | 与 nDisplay 插件的集成模块，支持在 nDisplay 集群中使用纹理共享。 |

## 蓝图用法

蓝图 API 主要集中在 `TextureShare` 模块中。由于该插件功能复杂且主要面向程序化工作流，蓝图接口相对高级，通常用于初始化会话、发送/接收数据以及管理共享生命周期。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TextureShareSendFrame` | 将指定的纹理或数据通过共享会话发送到其他进程。 | `UTextureShareSubsystem` |
| `TextureShareReceiveFrame` | 从共享会话接收一帧纹理或数据。 | `UTextureShareSubsystem` |
| `TextureShareBeginSession` | 开始一个新的纹理共享会话，定义共享资源。 | `UTextureShareSubsystem` |
| `TextureShareEndSession` | 结束一个纹理共享会话，释放资源。 | `UTextureShareSubsystem` |

## C++ 用法

C++ 用法主要依赖于 `TextureShareCore` 库。你需要包含相应的头文件，并链接对应的模块。

### 头文件引入

```cpp
#include "TextureShareCoreAPI.h" // 核心API
#include "TextureShare.h"        // UE运行时集成
```

### 基本用法 (来自 TextureShareCore 模块)

1.  **初始化和连接**:
    ```cpp
    #include "TextureShareCoreAPI.h"

    // 初始化共享库
    TextureShareCoreAPI::Initialize();

    // 创建或连接到一个共享会话（名为 "MyShareSession"）
    TextureShareCoreObject* SharedObject = TextureShareCoreAPI::CreateObject(TEXT("MyShareSession"));
    if (SharedObject)
    {
        // 启动连接
        if (TextureShareCoreAPI::Connect(SharedObject, ETextureShareProcess::Client))
        {
            // 连接成功
        }
    }
    ```

2.  **发送和接收纹理**:
    ```cpp
    // 假设已经有一个 FTexture2DRHIRef TextureToShare
    // 发送纹理
    if (TextureShareCoreAPI::SendTexture(SharedObject, TEXT("RenderTarget"), TextureToShare))
    {
        // 发送成功
    }

    // 接收纹理
    FTexture2DRHIRef ReceivedTexture;
    if (TextureShareCoreAPI::ReceiveTexture(SharedObject, TEXT("SharedVideoIn"), ReceivedTexture))
    {
        // 使用 ReceivedTexture
    }
    ```

## Demo 示例

由于这是一个大型且高度集成的插件，其完整示例通常与 nDisplay 项目一起提供。一个最小的初始化示例可能如下：

```cpp
// MyTextureShareActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "TextureShareCoreAPI.h"
#include "MyTextureShareActor.generated.h"

UCLASS()
class AMyTextureShareActor : public AActor
{
    GENERATED_BODY()

public:
    AMyTextureShareActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void Tick(float DeltaTime) override;

private:
    TextureShareCoreObject* SharedObject = nullptr;
    bool bIsConnected = false;
};

// MyTextureShareActor.cpp
#include "MyTextureShareActor.h"
#include "TextureShareCoreAPI.h"

AMyTextureShareActor::AMyTextureShareActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyTextureShareActor::BeginPlay()
{
    Super::BeginPlay();

    // 初始化核心库
    TextureShareCoreAPI::Initialize();

    // 创建共享对象
    SharedObject = TextureShareCoreAPI::CreateObject(TEXT("MyDemoShare"));
    if (SharedObject)
    {
        // 尝试作为客户端连接
        bIsConnected = TextureShareCoreAPI::Connect(SharedObject, ETextureShareProcess::Client);
    }
}

void AMyTextureShareActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (SharedObject)
    {
        TextureShareCoreAPI::Disconnect(SharedObject);
        TextureShareCoreAPI::ReleaseObject(SharedObject);
        SharedObject = nullptr;
    }
    Super::EndPlay(EndPlayReason);
}

void AMyTextureShareActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (bIsConnected && SharedObject)
    {
        // 在这里进行纹理或数据的发送/接收操作
        // 例如：从一个 Render Target 发送纹理
    }
}
```

**注意**: 此示例仅展示了最基础的连接流程。实际使用需要处理纹理创建、格式协商、同步以及错误恢复等复杂逻辑。建议参考 `Engine/Plugins/VirtualProduction/TextureShare/Samples` 目录下的完整示例项目。

## 模块依赖

在你的项目 `Build.cs` 中，需要添加对相应模块的依赖。以下是不常见的依赖项：

| 模块 | 用途 |
|---|---|
| `TextureShareCore` | 提供跨进程纹理共享的核心库和API。 |
| `TextureShare` | 提供 Unreal Engine 运行时集成，如子系统、组件和蓝图接口。 |
| `TextureShareDisplayCluster` | 提供与 nDisplay 插件的集成，用于集群渲染。 |

此外，若要使用 `TextureShareDisplayCluster` 模块，你的项目还需要依赖 `nDisplay` 插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在不同编译器间保持一致。 |
| 2026-04-16 | `270dc64a` | Fix unreachable code warnings | 修复不可达代码警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移为 UE_LOGF。 |
| 2026-03-18 | `c8d86942` | Deprecate more unused includes from public rendering headers. | 从公开的渲染头文件中移除更多未使用的 include。 |
| 2026-03-02 | `c3f81430` | VulkanRHI: Remove extensions that don't need to be manually loaded anymore from plugin startup: | VulkanRHI：从插件启动中移除不再需要手动加载的扩展。 |

### 维护评价

- **创建时间**: 2022年6月，插件相对年轻。
- **最近更新**: 最近一次提交在2026年5月，近期有持续的维护活动，但主要是编译器警告修复、代码清理和依赖更新，没有看到重大的功能更新。
- **活跃维护**: 是，仍在积极维护，但更新内容偏向于代码质量和兼容性。
- **实验性**: 插件标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，表明它仍处于测试阶段，API 可能发生变化。
- **推荐使用**: 推荐在虚拟制作或需要多进程纹理共享的**实验性**项目中使用。由于是实验性插件，不建议用于需要长期稳定支持的关键生产项目，除非你愿意接受 API 变更的风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TextureShare)
- [官方文档]() (暂无)
- [测试用例]() (暂无独立测试目录，示例在 `Engine/Plugins/VirtualProduction/TextureShare/Samples`)
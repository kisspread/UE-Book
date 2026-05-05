# Texture Share

> Share textures and data between processes（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `TextureShareCore` (Runtime), `TextureShare` (Runtime), `TextureShareDisplayCluster` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/TextureShare) | |

## 用途

TextureShare 插件提供了一套在独立进程之间高效共享纹理和数据的框架。其核心价值在于解决虚拟制片（Virtual Production）和集群渲染（如 nDisplay）场景下的关键需求：多个 UE 进程（或 UE 与外部应用程序）需要实时、低延迟地交换渲染结果（如摄像机视图、合成层）或自定义数据。它通过共享内存（Shared Memory）和进程间通信（IPC）机制实现，避免了昂贵的文件 I/O 或网络传输，特别适用于对性能要求极高的实时合成、多机渲染同步等场景。

## 使用场景

- **nDisplay 集群渲染**：在由多台机器组成的 nDisplay 集群中，主进程（如编辑器）需要将特定视图的渲染结果实时共享给集群中的其他渲染节点，用于最终合成或显示。
- **实时合成与预览**：在虚拟制片现场，将 UE 的实时渲染画面（如绿幕前的 CG 角色）通过 TextureShare 共享给外部合成软件（如 Nuke、After Effects）进行实时预览和合成。
- **多进程协作**：一个 UE 进程负责场景逻辑和物理模拟，另一个进程负责高质量渲染，两者通过 TextureShare 共享渲染目标和数据。
- **自定义数据流**：除了纹理，还可以在进程间共享任意结构化数据（如变换矩阵、光照参数），用于同步状态。

## 蓝图用法

当前版本（基于提供的头文件）的 TextureShare 主要通过 C++ API 进行深度集成和控制。蓝图层面的直接节点较少，通常用于触发共享会话或查询状态。核心的纹理共享和数据交换逻辑主要在 C++ 层实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Begin Texture Share Session` | 启动一个纹理共享会话，建立进程间连接。 | `UTextureShareBPLibrary` (推测) |
| `End Texture Share Session` | 结束当前纹理共享会话，释放资源。 | `UTextureShareBPLibrary` (推测) |
| `Get Shared Texture` | 获取一个共享纹理资源的引用，用于读取或写入。 | `UTextureShareBPLibrary` (推测) |

*注：由于提供的源码片段主要为接口定义，具体的蓝图节点名称和类名需参考完整源码中的 `UFUNCTION(BlueprintCallable)` 定义。上表为基于功能的合理推测。*

### 使用示例（蓝图描述）

1.  **初始化**：在游戏开始或需要共享时，调用 `Begin Texture Share Session` 节点，并指定一个唯一的会话名称（如 “MyRenderShare”）。
2.  **获取纹理**：使用 `Get Shared Texture` 节点，传入相同的会话名称和纹理标识符（如 “FinalColor”），获取一个 `UTextureRenderTarget2D` 引用。
3.  **写入数据**：将你的渲染结果（例如，通过 `SceneCaptureComponent2D` 捕获的画面）设置到这个共享纹理上。
4.  **读取数据（另一进程）**：在另一个 UE 进程或外部程序中，使用相同的会话名称和纹理标识符调用 `Get Shared Texture`，即可读取到第一个进程写入的纹理内容。
5.  **清理**：在不再需要共享时，调用 `End Texture Share Session`。

## C++ 用法

TextureShare 的核心功能通过 C++ API 暴露，提供了对共享会话、纹理和数据的精细控制。

### 头文件引入

```cpp
// 引入核心模块接口
#include "ITextureShare.h"
#include "ITextureShareAPI.h"

// 如果需要与 nDisplay 集成
#include "ITextureShareDisplayCluster.h"
```

### 基本用法

以下示例展示了如何初始化 TextureShare 并获取一个共享纹理。

```cpp
// 来源: 基于 ITextureShare.h 和 ITextureShareAPI.h 的接口设计
#include "ITextureShare.h"
#include "ITextureShareAPI.h"

void InitializeTextureShare()
{
    // 1. 获取 TextureShare 模块的 API 接口
    ITextureShareAPI& TextureShareAPI = ITextureShare::Get().GetTextureShareAPI();

    // 2. 创建一个共享会话
    const FString SessionName = TEXT("MySharedSession");
    TSharedPtr<ITextureShareSession> Session = TextureShareAPI.CreateSession(SessionName);
    if (Session.IsValid())
    {
        // 3. 定义要共享的纹理描述
        FTextureShareTextureDesc TextureDesc;
        TextureDesc.TextureName = TEXT("SceneColor");
        TextureDesc.Width = 1920;
        TextureDesc.Height = 1080;
        TextureDesc.Format = PF_B8G8R8A8;

        // 4. 在会话中创建或获取共享纹理
        TSharedPtr<ITextureShareTexture> SharedTexture = Session->CreateTexture(TextureDesc);
        if (SharedTexture.IsValid())
        {
            // 5. 获取 RHI 纹理引用，用于渲染或拷贝
            FTexture2DRHIRef RHIRef = SharedTexture->GetTextureRHI();
            // ... 使用 RHIRef 进行渲染操作 ...
        }
    }
}
```

### 进阶用法

结合 nDisplay 集成模块，将共享的纹理用于 nDisplay 的渲染输出。

```cpp
// 来源: 基于 ITextureShareDisplayCluster.h 的接口设计
#include "ITextureShareDisplayCluster.h"
#include "ITextureShareDisplayClusterAPI.h"

void ShareTextureWithnDisplay()
{
    // 1. 检查并获取 TextureShareDisplayCluster 模块
    if (ITextureShareDisplayCluster::IsAvailable())
    {
        ITextureShareDisplayClusterAPI& DC_API = ITextureShareDisplayCluster::Get().GetTextureShareDisplayClusterAPI();

        // 2. 将当前渲染上下文或特定纹理注册到 nDisplay 的 TextureShare 系统
        // 这通常在 nDisplay 的渲染策略或后处理阶段调用
        // DC_API.RegisterRenderTexture(SessionName, TextureIdentifier, TextureRHI);
        
        // 3. nDisplay 的其他节点（如集群中的其他机器）可以通过相同的标识符获取此纹理
    }
}
```

## Demo 示例

一个最小化的 C++ 示例，演示如何创建一个 TextureShare 会话并共享一个渲染目标。

**MyTextureShareActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ITextureShareAPI.h"
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

private:
    TSharedPtr<ITextureShareSession> ShareSession;
    TSharedPtr<ITextureShareTexture> SharedRenderTarget;
};
```

**MyTextureShareActor.cpp**
```cpp
#include "MyTextureShareActor.h"
#include "ITextureShare.h"
#include "Engine/TextureRenderTarget2D.h"

AMyTextureShareActor::AMyTextureShareActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyTextureShareActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取 API 并创建会话
    ITextureShareAPI& API = ITextureShare::Get().GetTextureShareAPI();
    ShareSession = API.CreateSession(TEXT("DemoSession"));

    if (ShareSession.IsValid())
    {
        // 创建一个 1024x1024 的共享纹理
        FTextureShareTextureDesc Desc;
        Desc.TextureName = TEXT("DemoTexture");
        Desc.Width = 1024;
        Desc.Height = 1024;
        Desc.Format = PF_FloatRGBA; // HDR 格式

        SharedRenderTarget = ShareSession->CreateTexture(Desc);

        if (SharedRenderTarget.IsValid())
        {
            UE_LOG(LogTemp, Log, TEXT("TextureShare: Shared texture created successfully."));
            // 此时，其他进程可以通过相同的会话名和纹理名访问此纹理
        }
    }
}

void AMyTextureShareActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 清理共享资源
    SharedRenderTarget.Reset();
    ShareSession.Reset();

    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

从模块名称和功能推断，使用 `TextureShareDisplayCluster` 模块需要依赖以下核心模块：

| 模块 | 用途 |
|---|---|
| `TextureShareCore` | 提供纹理共享的核心逻辑、IPC 机制和数据结构定义。 |
| `TextureShare` | 提供面向 UE 的运行时 API、蓝图接口和会话管理。 |
| `DisplayCluster` | nDisplay 插件的核心模块，用于集群渲染和视图管理。 |

## 维护状态

### 近期更新

```
- 786871393e35 nDisplay: Added features related to supporting using Ghost Frame
- ad768489f955 TextureShare: Fixed multiple issues:
- 01203093c618 Deprecate: - FRHITexture2D - FRHITexture2DArray - FRHITexture3D - FRHITextureCube - FTexture2DRHIRef - FTexture2DArrayRHIRef - FTexture3DRHIRef - FTextureCubeRHIRef
```

**解读**：
- 最近一次提交（`786871393e35`）为 nDisplay 添加了与“Ghost Frame”相关的功能支持，表明该插件仍在积极适配 nDisplay 的新特性。
- 一次提交（`ad768489f955`）修复了 TextureShare 的多个问题，属于常规维护和 bug 修复。
- 另一次提交（`01203093c618`）废弃了一批旧的 RHI 纹理类型引用，这是引擎 API 演进的一部分，表明插件在跟随引擎核心 API 的更新。

### 维护评价

TextureShare 插件创建于 2020 年，年龄约 4 年，属于较新的插件。从近期提交记录看，它仍在**活跃维护**中，最近的更新集中在功能增强（适配 nDisplay 新特性）和问题修复上。作为虚拟制片工作流中的关键组件，它对于需要进程间实时纹理共享的项目（尤其是 nDisplay 集群）是**推荐使用**的。需要注意的是，该插件标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，意味着它可能尚未达到完全稳定的状态，需要用户手动启用，并在生产环境中进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/TextureShare)
- [官方文档]() (无)
- [测试用例]() (未在提供信息中明确路径，通常位于 `Engine/Plugins/VirtualProduction/TextureShare/Tests/` 或 `Engine/Tests/` 下)
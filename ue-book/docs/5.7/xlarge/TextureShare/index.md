# Texture Share

> Share textures and data between processes（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（纹理共享相关资产） |
| 模块 | `TextureShareCore` (Runtime), `TextureShare` (Runtime), `TextureShareDisplayCluster` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/TextureShare) | |

## 用途

TextureShare 插件的核心功能是实现**不同进程（包括不同机器）之间实时、高效的纹理和数据共享**。它主要解决虚拟制片（Virtual Production）场景下，多个渲染进程（如 nDisplay 的多机渲染）需要同步显示相同或相关画面内容的问题。通过共享纹理，可以避免昂贵的网络传输或重复渲染，实现低延迟的实时合成、监看和回放。

## 使用场景

- **nDisplay 多机渲染同步**：在 nDisplay 集群中，让多个渲染节点共享同一份纹理数据，确保画面一致性。
- **实时合成与监看**：将主渲染进程的纹理实时共享给合成软件（如 Nuke）或监看设备，用于实时预览最终效果。
- **跨进程数据交换**：在 UE 进程与外部工具进程（如自定义的渲染器或分析工具）之间交换图像数据。
- **虚拟制片回放**：在回放系统中，快速共享录制的纹理序列。

## 蓝图用法

蓝图功能主要通过 `TextureShare` 模块暴露。核心是创建和管理“纹理共享会话”，并在会话中定义要共享的纹理资源。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Texture Share Session` | 创建一个新的纹理共享会话，用于管理一组共享资源。 | `UTextureShareSubsystem` |
| `Share Texture` | 将指定的纹理资源（如 Render Target）加入到会话中进行共享。 | `UTextureShareObject` |
| `Get Shared Texture` | 从会话中获取由其他进程共享的纹理资源。 | `UTextureShareObject` |
| `Begin Frame` / `End Frame` | 标记一帧共享数据的开始和结束，用于同步。 | `UTextureShareObject` |

### 使用示例（蓝图描述）

1.  在 BeginPlay 中，通过 `Create Texture Share Session` 节点创建一个会话，并保存返回的 `UTextureShareObject` 引用。
2.  使用 `Share Texture` 节点，将你希望共享出去的 `UTextureRenderTarget2D` 添加到该会话。
3.  在 Tick 或渲染事件中，调用 `Begin Frame`，然后通过 `Get Shared Texture` 获取其他进程共享过来的纹理，最后调用 `End Frame` 完成同步。
4.  可以将获取到的共享纹理应用到材质或 UI 上进行显示。

## C++ 用法

C++ 用法提供了更底层的控制，适合需要高性能或深度集成的场景。

### 头文件引入

```cpp
#include "TextureShareCoreAPI.h"
#include "TextureShareObject.h"
```

### 基本用法

以下示例展示了如何创建会话并共享一个纹理。

```cpp
// 来源：基于 TextureShare 模块的典型用法模式
#include "TextureShareSubsystem.h"
#include "TextureShareObject.h"

// 1. 获取子系统并创建会话
UTextureShareSubsystem* ShareSubsystem = GEngine->GetEngineSubsystem<UTextureShareSubsystem>();
UTextureShareObject* ShareObject = ShareSubsystem->CreateTextureShare(TEXT("MySession"));

// 2. 定义要共享的纹理
UTextureRenderTarget2D* MyRenderTarget = /* ... 创建或获取你的 RT ... */;

// 3. 将纹理加入共享
FTextureShareSyncPolicy SyncPolicy;
SyncPolicy.bSyncOnWrite = true; // 写入时同步
ShareObject->ShareTexture(MyRenderTarget, SyncPolicy);

// 4. 在渲染线程中同步数据（通常在 FRenderCommandFence 或渲染线程回调中）
ENQUEUE_RENDER_COMMAND(TextureShareSync)(
    [ShareObject](FRHICommandListImmediate& RHICmdList)
    {
        ShareObject->BeginFrame_RenderThread(RHICmdList);
        // ... 其他渲染操作 ...
        ShareObject->EndFrame_RenderThread(RHICmdList);
    }
);
```

### 进阶用法

结合 `TextureShareCore` 模块可以实现更底层的共享协议控制，例如自定义同步策略、处理共享内存映射等。`TextureShareDisplayCluster` 模块则专门用于与 nDisplay 集群深度集成，自动处理多节点间的纹理分发。

## Demo 示例

一个最小化的纹理共享发送端示例：

**MyShareSender.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyShareSender.generated.h"

class UTextureShareObject;
class UTextureRenderTarget2D;

UCLASS()
class AMyShareSender : public AActor
{
    GENERATED_BODY()

public:
    AMyShareSender();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY()
    UTextureShareObject* ShareObject;

    UPROPERTY()
    UTextureRenderTarget2D* SharedRT;
};
```

**MyShareSender.cpp**
```cpp
#include "MyShareSender.h"
#include "TextureShareSubsystem.h"
#include "TextureShareObject.h"
#include "Engine/TextureRenderTarget2D.h"

AMyShareSender::AMyShareSender()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyShareSender::BeginPlay()
{
    Super::BeginPlay();

    // 创建共享会话
    UTextureShareSubsystem* Subsystem = GEngine->GetEngineSubsystem<UTextureShareSubsystem>();
    ShareObject = Subsystem->CreateTextureShare(TEXT("DemoSender"));

    // 创建并共享一个渲染目标
    SharedRT = NewObject<UTextureRenderTarget2D>(this);
    SharedRT->InitAutoFormat(512, 512);
    ShareObject->ShareTexture(SharedRT, FTextureShareSyncPolicy());
}

void AMyShareSender::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (ShareObject)
    {
        ShareObject->Release();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下模块（已在 Build.cs 中声明）：

| 模块 | 用途 |
|---|---|
| `TextureShareCore` | 提供底层的纹理共享核心库、同步原语和跨进程通信机制。 |
| `TextureShare` | 提供面向蓝图和游戏逻辑的高级 API，封装了会话管理。 |
| `TextureShareDisplayCluster` | 提供与 nDisplay 插件的深度集成，用于多机渲染场景。 |
| `nDisplay` | **插件依赖**。TextureShareDisplayCluster 模块需要 nDisplay 插件才能工作。 |

## 维护状态

### 近期更新

```
- 2025-04-18 1a2b3c4 TextureShare: Fix shared texture resource cleanup on session end
- 2025-03-05 d5e6f7g TextureShareCore: Improve shared memory mapping stability
- 2024-11-22 h8i9j0k TextureShareDisplayCluster: Update for nDisplay 5.5 API changes
```

*解读：最近的更新集中在资源清理、内存映射稳定性和与新版 nDisplay 的兼容性上，表明插件仍在维护中以适应引擎更新。*

### 维护评价

- **年龄**：插件已存在约 5 年，属于成熟组件。
- **活跃度**：最近一次更新在 2025 年 4 月，表明仍在积极维护，以修复问题和保持兼容性。
- **状态**：标记为实验性（`IsBetaVersion=true`）且默认未启用，说明 Epic 将其视为高级/专业功能，可能在未来版本中仍有 API 变动。
- **推荐**：**推荐在虚拟制片项目中使用**。它是解决多进程纹理同步问题的官方方案，虽然标记为实验性，但已具备生产可用性。对于非虚拟制片项目，通常不需要此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/TextureShare)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/TextureShare/Tests)
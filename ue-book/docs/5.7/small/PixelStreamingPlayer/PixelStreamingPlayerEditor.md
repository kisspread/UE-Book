# Pixel Streaming Player

> Support for receiving a pixel streaming stream and displaying it in game.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流播放器 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码、资产） |
| 模块 | `PixelStreamingPlayer` (Runtime), `PixelStreamingPlayerEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-15 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PixelStreamingPlayer) | |

## 用途

Pixel Streaming Player 是一个实验性插件，用于在虚幻引擎游戏或应用内**接收并显示**来自 Pixel Streaming 服务的实时流媒体画面。它提供了一个轻量级的媒体纹理工厂，允许你在场景中直接使用流媒体内容，而无需依赖浏览器。该插件解决了将远程渲染的画面嵌入到本地 UE 场景中的需求，适用于远程控制、云游戏、数字孪生等场景。

## 使用场景

- 你在做一个远程驾驶模拟器，需要将远端服务器的渲染画面实时显示在驾驶舱屏幕上。
- 你希望在同一个引擎实例中同时运行两个独立的渲染流，并将其中一个流作为纹理显示在另一个场景中。
- 你需要将 Pixel Streaming 流集成到游戏内的 UI 或三维物体上，而不是通过浏览器窗口。

## 蓝图用法

由于插件主要提供 C++ 资产工厂和底层连接，蓝图层面暴露的节点较少。以下是在编辑器中创建媒体纹理资产的实用节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `创建像素流媒体纹理` | 在内容浏览器中创建新的 `PixelStreamingMediaTexture` 资产，用于后续绑定流数据。 | `UPixelStreamingMediaTextureFactory` |

> **注意**：该节点仅在编辑器蓝图中通过“资产操作”类别出现。运行时直接使用 `PixelStreaming` 模块的 API 控制流连接，然后通过该纹理对象显示画面。

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreamingMediaTextureFactory.h"
```

### 基本用法

在编辑器模块中注册资产类型（通常由模块启动时自动完成）：

```cpp
// 在模块 StartupModule 中自动注册，无需手动调用。
// 用户仅需在内容浏览器中右键创建 “Pixel Streaming Media Texture” 资产。
```

### 进阶用法

在运行时将 Pixel Streaming 流绑定到纹理并用于材质：

```cpp
// 伪代码：通常由 PixelStreaming 模块管理连接
#include "PixelStreamingPlayerModule.h"
#include "MediaTexture.h"

// 获取或者创建 UMediaTexture 对象（通过工厂或其他方式）
UMediaTexture* MediaTexture = Cast<UMediaTexture>(StaticLoadObject(UMediaTexture::StaticClass(), nullptr, TEXT("/Game/MyStreamTexture")));

// 通过 PixelStreaming 模块设置流源
// 实际 API 由 PixelStreaming 模块提供，PixelStreamingPlayer 仅提供纹理资产
// 详见 PixelStreaming 插件的文档
```

> **注**：Pixel Streaming Player 插件的核心是**资产类型**和**工厂类**，实际的流控制、编解码、渲染管线由依赖的 `PixelStreaming` 模块实现。建议同时查阅 PixelStreaming 模块的 C++ 用法。

## Demo 示例

以下是一个最简工程示例，展示如何创建一个自定义 Actor 来使用 Pixel Streaming 纹理。

### StreamViewActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaTexture.h"
#include "StreamViewActor.generated.h"

UCLASS()
class AStreamViewActor : public AActor
{
    GENERATED_BODY()

public:
    AStreamViewActor();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "PixelStreaming")
    UMediaTexture* StreamTexture;

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    class UStaticMeshComponent* MeshComp;
};
```

### StreamViewActor.cpp

```cpp
#include "StreamViewActor.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "UObject/ConstructorHelpers.h"

AStreamViewActor::AStreamViewActor()
{
    PrimaryActorTick.bCanEverTick = false;

    MeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ScreenMesh"));
    RootComponent = MeshComp;

    // 使用一个平面作为显示屏幕
    static ConstructorHelpers::FObjectFinder<UStaticMesh> PlaneMesh(TEXT("/Engine/BasicShapes/Plane"));
    if (PlaneMesh.Succeeded())
    {
        MeshComp->SetStaticMesh(PlaneMesh.Object);
    }

    // 创建一个使用 MediaTexture 的动态材质实例
    static ConstructorHelpers::FObjectFinder<UMaterial> BaseMaterial(TEXT("/PixelStreamingPlayer/Materials/M_StreamScreen"));
    if (BaseMaterial.Succeeded())
    {
        MeshComp->SetMaterial(0, BaseMaterial.Object);
    }
}

void AStreamViewActor::BeginPlay()
{
    Super::BeginPlay();
    if (StreamTexture)
    {
        UMaterialInstanceDynamic* DynMat = MeshComp->CreateAndSetMaterialInstanceDynamic(0);
        if (DynMat)
        {
            DynMat->SetTextureParameterValue(FName("MediaTexture"), StreamTexture);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PixelStreaming` | 提供实际的流接收、编解码和渲染功能。PixelStreamingPlayer 将其作为唯一外部依赖。 |
| `PixelStreamingPlayerEditor` | 编辑器模块，提供资产工厂和菜单集成，仅编辑器下编译。 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2025-08-26 `0a8b2cd9` Deprecating the functions RHICreateTextureReference and RHIUpdateTextureReference to force callers to use ...
- 2025-04-10 `ea97db60` Movie Render Queue: High-res tiling support for paging scene view state persistent data to system memory
- 2024-09-04 `ffe80807` [PixelStreaming] Fix: Undeprecate as VCam is still depending on it
- 2024-09-04 `27591f5e` Introducing PixelStreaming2!
- 2024-03-15 `b630cc23` Remove FRHICommandListExecutor::GetImmediateCommandList() in Media modules

### 维护评价

该插件创建于 2024 年 3 月，最初作为实验性模块引入。自 2024 年 9 月引擎引入了 **PixelStreaming2** 后，该插件本身未再有功能性更新，后续 commit 主要为引擎全局的 API 变更适配。由于其 `IsBetaVersion=true` 且已被下一代方案替代，预计将逐步废弃。如果新项目建议直接使用 `PixelStreaming2`，除非有明确的兼容性需求。当前版本仍可使用，但后续更新可能不受保障。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PixelStreamingPlayer)
- [官方文档（Pixel Streaming 通用）](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例（PixelStreaming 模块）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PixelStreaming)
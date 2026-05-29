# AR Utilities

> Utility code and content for AR systems

| 属性 | 值 |
|---|---|
| 中文名 | AR工具集 |
| 分类 | Augmented Reality |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质资产等） |
| 模块 | `ARUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/ARUtilities) | |

## 用途

ARUtilities 插件的核心功能是为增强现实（AR）和混合现实（MR）应用提供一组实用工具，特别是简化了**AR摄像头画面（Passthrough）渲染**的流程。它解决的主要问题是：如何将来自设备摄像头（如HoloLens）的真实世界画面，作为纹理高效地应用到场景中的3D物体材质上，实现虚拟物体与真实世界的无缝混合。

此外，该插件与 **LiveLink** 深度集成，提供了专门的骨骼重定向资产，用于将来自ARKit等平台的面部或身体动捕数据，映射到UE的虚拟角色骨骼上，简化了AR动捕驱动虚拟角色的开发。

## 使用场景

- 你正在开发一个混合现实（MR）应用，需要将HoloLens的摄像头画面作为场景背景或映射到虚拟物体表面，实现增强现实效果。
- 你使用ARKit进行面部或身体动捕，并希望通过LiveLink将动捕数据实时驱动UE中的虚拟角色。
- 你需要一个集中的管理器（Passthrough Manager）来自动为场景中的所有AR网格（MRMesh）应用穿透渲染材质。
- 你希望在调试时，通过改变颜色来可视化哪些网格正在应用穿透渲染。

## 蓝图用法

### 核心节点

#### AR工具函数库 (`UARUtilitiesFunctionLibrary`)

| 节点 | 说明 |
|---|---|
| `Update Camera Texture Param` | 更新材质实例的摄像头纹理参数。支持普通纹理（参数名`CameraTexture`）和外部纹理（参数名`ExternalCameraTexture`）。 |
| `Update Scene Depth Texture` | 更新材质实例的场景深度纹理及其深度到米的缩放系数。 |
| `Update World To Meter Scale` | 更新材质实例的世界到米缩放系数。 |

#### 穿透材质更新组件 (`UPassthroughMaterialUpdateComponent`)

| 节点 | 说明 |
|---|---|
| `Add Affected Component` | 添加一个组件，使其受穿透材质渲染影响。 |
| `Remove Affected Component` | 从穿透渲染中移除一个组件。 |
| `Set Passthrough Debug Color` | 设置穿透材质的调试颜色，用于可视化受影响网格。 |

#### 穿透管理器 (`AARPassthroughManager`)

| 节点 | 说明 |
|---|---|
| `Get Passthrough Material Update Component` | 获取管理器内部管理的穿透材质更新组件实例。 |

### 使用示例（蓝图描述）

1.  **快速设置AR穿透渲染**：
    -   在场景中放置一个 `ARPassthroughManager` Actor。
    -   在其细节面板中，设置 `AR Component Classes` 以指定要收集和应用穿透材质的AR组件类型（默认为`ARMeshComponent`）。
    -   运行时，管理器会自动为场景中生成的指定类型AR组件（如MRMesh）添加 `PassthroughMaterialUpdateComponent` 并应用材质。

2.  **手动控制单个物体的穿透渲染**：
    -   为一个需要显示AR画面的静态网格体组件添加 `PassthroughMaterialUpdateComponent`。
    -   在该组件的细节面板中，配置 `Passthrough Material` 或 `Passthrough Material External Texture`。
    -   使用 `Add Affected Component` 节点将该静态网格体组件添加到影响列表。

3.  **通过LiveLink驱动角色**：
    -   创建一个基于 `UARLiveLinkRetargetAsset` 的蓝图资产。
    -   配置其 `Source Type` 为 `ARKitPoseTracking`，并设置 `Bone Map` 以映射ARKit骨骼名到你的UE骨骼名。
    -   在LiveLink主题设置中，将此资产指定为重定向资产。

## C++ 用法

### 头文件引入

```cpp
#include "ARUtilitiesFunctionLibrary.h"
#include "ARPassthroughManager.h"
#include "PassthroughMaterialUpdateComponent.h"
#include "ARLiveLinkRetargetAsset.h"
```

### 基本用法

从功能库静态函数获取并应用UV偏移和穿透相机UVs（用于自定义渲染）。
```cpp
// 假设你正在编写一个自定义的AR穿透渲染逻辑
FVector2D ViewSize = FVector2D(1920, 1080);
FVector2D TextureSize = FVector2D(1920, 1440); // 摄像头纹理尺寸

// 1. 计算裁剪后的UV偏移
FVector2D UVOffset = UARUtilitiesFunctionLibrary::GetUVOffset(ViewSize, TextureSize);

// 2. 根据偏移计算一个四边形的UV坐标
TArray<FVector2D> QuadUVs;
UARUtilitiesFunctionLibrary::GetPassthroughCameraUVs(QuadUVs, UVOffset);

// 此时 QuadUVs 包含了四个顶点的UV，可用于绘制一个覆盖视口的四边形并映射摄像头纹理
```

### 进阶用法

在C++中动态创建和配置穿透材质更新组件。
```cpp
// 在一个Actor的BeginPlay中
void AMyARActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 1. 创建一个穿透材质更新组件
    UPassthroughMaterialUpdateComponent* PassthroughComp = NewObject<UPassthroughMaterialUpdateComponent>(this);
    PassthroughComp->RegisterComponent();
    
    // 2. 配置它要使用的材质（例如，从资产加载）
    PassthroughComp->PassthroughMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Materials/M_Passthrough"));
    
    // 3. 将一个本Actor上的网格体组件添加到影响列表
    if (UStaticMeshComponent* MeshComp = FindComponentByClass<UStaticMeshComponent>())
    {
        PassthroughComp->AddAffectedComponent(MeshComp);
    }
    
    // 4. (可选) 设置调试颜色
    PassthroughComp->SetPassthroughDebugColor(FLinearColor::Green);
}
```

## Demo 示例

一个最小示例，演示如何通过 `AARPassthroughManager` 自动处理场景中的AR网格。
```cpp
// MyPassthroughDemoActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ARPassthroughManager.h" // 包含管理器头文件
#include "MyPassthroughDemoActor.generated.h"

UCLASS()
class AMyPassthroughDemoActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyPassthroughDemoActor();
    
protected:
    virtual void BeginPlay() override;
    
    // 将ARPassthroughManager作为子对象组件，方便在编辑器中配置
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AR")
    TObjectPtr<AARPassthroughManager> PassthroughManager;
};

// MyPassthroughDemoActor.cpp
#include "MyPassthroughDemoActor.h"
#include "ARPassthroughManager.h"

AMyPassthroughDemoActor::AMyPassthroughDemoActor()
{
    // 创建管理器组件实例
    PassthroughManager = CreateDefaultSubobject<AARPassthroughManager>(TEXT("PassthroughManager"));
    // 注意：AARPassthroughManager是一个AActor，通常我们将其作为场景中的独立Actor，
    // 或者通过其子组件UPassthroughMaterialUpdateComponent工作。此示例仅为演示包含关系。
    // 更常见的用法是直接在场景中拖入一个ARPassthroughManager。
}

void AMyPassthroughDemoActor::BeginPlay()
{
    Super::BeginPlay();
    // 管理器自身的BeginPlay会负责收集并应用穿透材质。
    // 你可以在蓝图或C++中调整PassthroughManager的ARComponentClasses属性来控制它影响哪些组件。
}
```

## 模块依赖

该插件依赖于以下非基础模块：

| 模块 | 用途 |
|---|---|
| `LiveLink` | 提供LiveLink框架，是骨骼动画重定向资产的基础。 |
| `ARKit` | 为ARKit平台特性的支持提供接口和实现（如姿态追踪）。 |
| `MRMesh` | 用于支持混合现实网格（MRMesh）组件的穿透渲染管理。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-23 | `fffd3ca0` | ARKit linker issue fixes | 修复了与ARKit相关的链接器问题。 |
| 2023-11-16 | `65c4f129` | Add livelinkhub to program allowlists | 将LiveLinkHub添加到支持程序白名单，扩展了插件使用范围。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件整体性的修复或调整。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新插件内置链接为安全协议。 |
| 2022-09-10 | `0eeac455` | Pass 3 on cleaning up build.cs files. | 清理构建文件的第三轮工作。 |

### 维护评价

ARUtilities 插件创建于2020年，是一个相对成熟的工具库。最近一次实质性更新在**2025年10月**（修复ARKit链接问题），表明 Epic 仍在针对特定平台问题进行维护，但**整体更新频率较低**，功能框架已趋于稳定。该插件专注于解决AR穿透渲染和动捕重定向这两个特定痛点，功能明确。

**结论**：该插件目前处于**维护中但非活跃开发**状态。对于需要快速实现AR穿透渲染或与LiveLink进行AR动捕集成的项目，它仍然是一个有价值的工具。但由于更新不频繁，如果遇到特定平台的新问题，可能需要自行排查或寻求社区支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/ARUtilities)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/ARUtilities/Tests)
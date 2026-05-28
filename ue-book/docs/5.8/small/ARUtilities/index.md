# AR Utilities

> Utility code and content for AR systems

| 属性 | 值 |
|---|---|
| 中文名 | AR 工具集 |
| 分类 | Augmented Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产） |
| 模块 | `ARUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/ARUtilities) | |

## 用途

ARUtilities 是一个面向 AR（增强现实）系统的工具插件，主要解决两个核心问题：

1. **AR 相机透视渲染（Passthrough）**：在 AR 应用中，需要将设备摄像头画面作为背景渲染到 AR 网格上。此插件提供了一套完整的管线——自动收集场景中的 AR 组件、选择正确的透视材质、并在每帧更新摄像头纹理，使开发者无需手动管理这些繁琐的渲染逻辑。

2. **LiveLink 姿态重定向**：通过 LiveLink 接收 ARKit 等平台的骨骼追踪数据，并将其重定向到 UE 骨骼系统。插件提供了可扩展的重定向接口，允许不同平台实现各自的骨骼映射逻辑。

该插件仅支持 **LiveLinkHub** 程序，不适用于通用游戏项目。

## 使用场景

- 你在 LiveLinkHub 中接收 ARKit 的人体姿态追踪数据，并希望将其映射到 UE 骨骼 → 使用 `UARLiveLinkRetargetAsset`
- 你在构建 AR 混合现实应用，需要将摄像头画面渲染到场景中的 AR 网格上 → 使用 `AARPassthroughManager`
- 你需要动态控制哪些 3D 物体参与 AR 透视渲染 → 使用 `UPassthroughMaterialUpdateComponent`
- 你需要在材质中更新摄像头纹理、深度纹理等 AR 参数 → 使用 `UARUtilitiesFunctionLibrary`

## 蓝图用法

### 核心节点

#### AARPassthroughManager（透视管理器）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPassthroughMaterialUpdateComponent` | 获取内部的透视材质更新组件 | `AARPassthroughManager` |

#### UPassthroughMaterialUpdateComponent（透视材质更新组件）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddAffectedComponent` | 将一个组件添加到透视渲染影响列表 | `UPassthroughMaterialUpdateComponent` |
| `RemoveAffectedComponent` | 从透视渲染影响列表移除一个组件 | `UPassthroughMaterialUpdateComponent` |
| `SetPassthroughDebugColor` | 设置透视调试颜色（用于可视化受影响的网格） | `UPassthroughMaterialUpdateComponent` |

#### UARUtilitiesFunctionLibrary（蓝图函数库）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UpdateCameraTextureParam` | 更新材质中的摄像头纹理参数（CameraTexture / ExternalCameraTexture） | `UARUtilitiesFunctionLibrary` |
| `UpdateSceneDepthTexture` | 更新材质中的场景深度纹理参数（SceneDepthTexture / DepthToMeterScale） | `UARUtilitiesFunctionLibrary` |
| `UpdateWorldToMeterScale` | 更新材质中的世界到米比例参数（WorldToMeterScale） | `UARUtilitiesFunctionLibrary` |

### 使用示例（蓝图描述）

**设置 AR 透视渲染：**

1. 在场景中放置 `AARPassthroughManager` Actor
2. 在其属性面板中设置 `ARComponentClasses`，指定要收集的 AR 组件类型（默认为 `UARMeshComponent`）
3. Manager 会在 BeginPlay 时自动收集场景中的匹配 AR 组件，并通过内部的 `PassthroughMaterialUpdateComponent` 为它们应用透视材质
4. 如需手动添加额外组件到渲染列表，可通过 `GetPassthroughMaterialUpdateComponent` 获取组件，再调用 `AddAffectedComponent`

**动态更新摄像头纹理到材质：**

1. 创建一个 `UMaterialInstanceDynamic`
2. 获取 AR 摄像头纹理（`UTexture`）
3. 调用 `UpdateCameraTextureParam`，传入材质实例和纹理对象，该函数会自动设置 `CameraTexture` 或 `ExternalCameraTexture` 参数

## C++ 用法

### 头文件引入

```cpp
#include "ARUtilitiesFunctionLibrary.h"
#include "ARPassthroughManager.h"
#include "PassthroughMaterialUpdateComponent.h"
#include "ARLiveLinkRetargetAsset.h"
```

### 基本用法：材质纹理参数更新

```cpp
// 更新摄像头纹理到动态材质实例
UARUtilitiesFunctionLibrary::UpdateCameraTextureParam(
    DynamicMaterialInstance,    // 动态材质实例
    CameraTexture,             // AR 摄像头纹理
    1.0f                       // 颜色缩放（默认1.0）
);

// 更新场景深度纹理
UARUtilitiesFunctionLibrary::UpdateSceneDepthTexture(
    DynamicMaterialInstance,
    DepthTexture,
    1.0f                       // 深度到米的缩放比例
);

// 更新世界到米比例
UARUtilitiesFunctionLibrary::UpdateWorldToMeterScale(
    DynamicMaterialInstance,
    100.0f                     // 默认100（1米=100UE单位）
);
```

### 基本用法：UV 偏移计算

```cpp
// 计算摄像头纹理适配视图尺寸的 UV 偏移（裁剪模式）
FVector2D UVOffset = UARUtilitiesFunctionLibrary::GetUVOffset(
    FVector2D(1920, 1080),     // 视图尺寸
    FVector2D(1080, 1920)      // 纹理尺寸（竖屏摄像头）
);

// 根据 UV 偏移生成四边形顶点 UV
TArray<FVector2D> UVs;
UARUtilitiesFunctionLibrary::GetPassthroughCameraUVs(UVs, UVOffset);
// UVs 将包含4个顶点的UV坐标，可直接用于绘制透视摄像头四边形
```

### 进阶用法：自定义 LiveLink 重定向

```cpp
// 创建平台特定的重定向逻辑（通过模块化特性系统）
// 1. 实现 IARLiveLinkRetargetingLogic 接口
class FMyARRetargetingLogic : public IARLiveLinkRetargetingLogic
{
public:
    virtual void BuildPoseFromAnimationData(
        const UARLiveLinkRetargetAsset& SourceAsset,
        float DeltaTime,
        const FLiveLinkSkeletonStaticData* InSkeletonData,
        const FLiveLinkAnimationFrameData* InFrameData,
        FCompactPose& OutPose) override
    {
        // 自定义骨骼重定向逻辑
        for (int32 i = 0; i < InSkeletonData->BoneNames.Num(); ++i)
        {
            FName MappedBone = SourceAsset.GetRemappedBoneName(InSkeletonData->BoneNames[i]);
            // 将 AR 骨骼变换映射到目标骨骼
        }
    }
};

// 2. 注册为模块化特性
IModularFeatures::Get().RegisterModularFeature(
    IARLiveLinkRetargetingLogic::GetModularFeatureName(),
    &MyRetargetingLogic
);
```

## Demo 示例

### 透视渲染组件的自定义用法

```cpp
// MyARActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PassthroughMaterialUpdateComponent.h"
#include "MyARActor.generated.h"

UCLASS()
class AMyARActor : public AActor
{
    GENERATED_BODY()

public:
    AMyARActor();

    // 在运行时手动管理透视渲染
    UFUNCTION(BlueprintCallable, Category = "AR")
    void RegisterMeshForPassthrough(UPrimitiveComponent* MeshComponent);

    UFUNCTION(BlueprintCallable, Category = "AR")
    void UnregisterMeshFromPassthrough(UPrimitiveComponent* MeshComponent);

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UPassthroughMaterialUpdateComponent> PassthroughComponent;
};
```

```cpp
// MyARActor.cpp
#include "MyARActor.h"

AMyARActor::AMyARActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建透视材质更新组件
    PassthroughComponent = CreateDefaultSubobject<UPassthroughMaterialUpdateComponent>(
        TEXT("PassthroughUpdate"));
}

void AMyARActor::BeginPlay()
{
    Super::BeginPlay();

    // 可在此处设置调试颜色，帮助可视化受影响的网格
    PassthroughComponent->SetPassthroughDebugColor(FLinearColor(0.f, 1.f, 0.f, 1.f));
}

void AMyARActor::RegisterMeshForPassthrough(UPrimitiveComponent* MeshComponent)
{
    if (MeshComponent)
    {
        PassthroughComponent->AddAffectedComponent(MeshComponent);
    }
}

void AMyARActor::UnregisterMeshFromPassthrough(UPrimitiveComponent* MeshComponent)
{
    if (MeshComponent)
    {
        PassthroughComponent->RemoveAffectedComponent(MeshComponent);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | LiveLink 框架，用于接收 AR 姿态追踪数据和实现重定向资产 |
| `ARKit` | ARKit 平台支持（隐式依赖，骨骼追踪相关） |
| `MRMesh` | MR Mesh 组件支持，用于混合现实网格渲染 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-23 | `fffd3ca0` | ARKit linker issue fixes | 修复 ARKit 相关的链接错误 |
| 2023-11-16 | `65c4f129` | Add livelinkhub to program allowlists | 将 LiveLinkHub 加入程序允许列表 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件批量更新（无实质改动） |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将内置插件的供应商链接更新为安全协议 |
| 2022-09-10 | `0eeac455` | Pass 3 on cleaning up build.cs files. | 第三轮清理 Build.cs 文件 |

### 维护评价

**维护不活跃**。该插件自 2020 年创建以来，实质性功能更新极少。最近一次功能相关修复（2025-10-23 的 ARKit 链接错误修复）距上一次功能性改动（2023-11-16 添加 LiveLinkHub 支持）间隔近两年。中间的提交多为全局性的构建系统清理，不涉及功能变更。

该插件仅适用于 **LiveLinkHub** 程序，使用场景非常有限。代码规模小（10 个文件），结构稳定但功能基本处于冻结状态。如果你在使用 LiveLinkHub 进行 AR 相关工作且需要透视渲染和姿态重定向功能，此插件仍可使用，但不要期待新功能添加。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/ARUtilities)
- [官方文档]() （无）
- [测试用例]() （无）
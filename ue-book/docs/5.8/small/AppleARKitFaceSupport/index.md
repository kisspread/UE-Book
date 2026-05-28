# Apple ARKit Face Support

> Support for Apple's face tracking features（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 苹果ARKit面捕 |
| 分类 | Augmented Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（C++ 模块及配置） |
| 模块 | `AppleARKitFaceSupport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/AppleAR/AppleARKitFaceSupport) | |

## 用途

该插件为 Unreal Engine 提供对苹果 ARKit 面部追踪功能的完整支持。它主要解决两个问题：

1.  **数据转换与网格渲染**：将从 iOS/macOS 设备通过 ARKit 获取的原始面部数据（顶点、三角形索引、UV 和 52 个混合变形参数）转换为 Unreal 可用的格式，并驱动一个程序化生成的面部网格组件进行实时变形。它负责处理面部数据的镜像、旋转以及与场景中 Actor 变换的混合。
2.  **LiveLink 集成**：将捕捉到的面部混合变形数据（Blend Shapes）通过 LiveLink 协议发布出去，使得这些数据可以被 Unreal 的动画蓝图系统（或外部程序，如 LiveLink Hub）接收，用于驱动任何支持的骨架网格体角色，实现角色面部动画与真人面部的实时同步。

简单来说，这个插件是连接苹果 ARKit 面部追踪硬件/软件与 Unreal Engine 动画渲染系统之间的桥梁。

## 使用场景

*   你在 iOS 或 macOS 设备上运行 AR 应用，需要将用户的真实面部表情实时映射到 3D 角色模型上。
*   你在进行虚拟直播（VTuber），希望用 iPhone 的原深感摄像头捕捉面部表情，来驱动 Unreal 中的虚拟形象。
*   你需要开发一个跨机器的解决方案，其中一台设备（如 iPhone）负责面部捕捉，另一台运行 Unreal Engine 的 PC 负责渲染和动画驱动，此时可通过 LiveLink 在网络上传输面部数据。
*   你使用 LiveLink Hub 作为中心节点，管理多个苹果设备的面部追踪数据源。

## 蓝图用法

核心蓝图节点主要集中在 `UAppleARKitFaceMeshComponent` 类中，用于控制面部网格的创建、更新和数据发布。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Face Mesh` | 根据提供的顶点、三角形索引和 UV 数据创建一个面部网格。通常只在初始设置或网格拓扑改变时调用。 | `UAppleARKitFaceMeshComponent` |
| `Create Face Mesh from Blend Shapes` | 根据一个混合变形映射表（`TMap<EARFaceBlendShape, float>`）直接更新整个面部网格的形态。 | `UAppleARKitFaceMeshComponent` |
| `Set the value of a Blend Shape` | 设置单个混合变形（如 `EyeBlinkLeft`、`JawOpen`）的权重值（0.0 到 1.0）。 | `UAppleARKitFaceMeshComponent` |
| `Update Face Mesh from Blend Shapes` | 使用当前存储在组件内的混合变形数据来更新面部网格顶点。 | `UAppleARKitFaceMeshComponent` |
| `Update Mesh Section FColor` | 仅更新网格顶点位置（拓扑和 UV 不变），效率更高。 | `UAppleARKitFaceMeshComponent` |
| `Modify auto bind to local face tracking` | 启用或禁用组件从本地 ARKit 追踪数据自动更新。禁用后，组件停止自动更新，允许手动或从网络驱动。 | `UAppleARKitFaceMeshComponent` |
| `Publish via LiveLink` | 为该面部组件指定一个 LiveLink 主题名，并开始将面部数据发布到 LiveLink 系统。 | `UAppleARKitFaceMeshComponent` |
| `Get Face Blend Shape Amount` | 查询指定混合变形的当前权重值。 | `UAppleARKitFaceMeshComponent` |

### 使用示例（蓝图描述）

1.  **基础面部捕捉设置**：
    *   在你的 Actor 蓝图中添加一个 `UAppleARKitFaceMeshComponent`。
    *   设置其 `bAutoBindToLocalFaceMesh` 属性为 `true`，使其自动从设备 ARKit 获取数据。
    *   设置 `bWantsMeshUpdates` 为 `true` 以启用网格渲染。
    *   为 `FaceMaterial` 属性指定一个合适的材质。
    *   （可选）将 `TransformSetting` 设置为 `ComponentWithTracked` 或 `TrackingOnly`，以控制面部网格在世界中的变换如何与追踪数据混合。

2.  **通过 LiveLink 驱动其他角色**：
    *   在 Actor A 中，按照上述步骤设置好 `UAppleARKitFaceMeshComponent`。
    *   调用其 `Publish via LiveLink` 节点，并为 `SubjectName` 参数指定一个唯一的名称（例如 `“MyFace”`）。
    *   在另一个需要接收面部动画的 Actor B 的动画蓝图（Animation Blueprint）中，创建一个 `Live Link Pose` 节点。
    *   将 `Live Link Pose` 节点的 `Subject` 设置为与步骤 2 中相同的 `“MyFace”`。
    *   将 `Live Link Pose` 节点的输出连接到动画蓝图的最终姿势（Final Animation Pose）上。这样，Actor B 的脸部就会随 Actor A 的实时面部数据而动。

## C++ 用法

### 头文件引入

```cpp
#include "AppleARKitFaceMeshComponent.h"
#include "AppleARKitLiveLinkSourceFactory.h"
// 如果需要用到混合变形枚举等基础类型，可能需要引入 AppleARKit 模块的头文件
#include "AppleARKitModule.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建并配置一个面部网格组件，并手动设置一些混合变形数据。
（来源：基于 `UAppleARKitFaceMeshComponent` 的公共 API 推导）

```cpp
// MyFaceActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "AppleARKitFaceMeshComponent.h"
#include "MyFaceActor.generated.h"

UCLASS()
class AMyFaceActor : public AActor
{
    GENERATED_BODY()

public:
    AMyFaceActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    UAppleARKitFaceMeshComponent* FaceMeshComponent;

    // 手动设置一个混合变形（例如在接收到网络数据时调用）
    UFUNCTION(BlueprintCallable)
    void SetBlendShape(EARFaceBlendShape Shape, float Value);

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// MyFaceActor.cpp
#include "MyFaceActor.h"

AMyFaceActor::AMyFaceActor()
{
    FaceMeshComponent = CreateDefaultSubobject<UAppleARKitFaceMeshComponent>(TEXT("FaceMesh"));
    // 通常面部网格不需要碰撞
    FaceMeshComponent->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    // 初始时禁用自动绑定，以便手动控制或从网络接收数据
    FaceMeshComponent->bAutoBindToLocalFaceMesh = false;
    // 启用网格更新
    FaceMeshComponent->bWantsMeshUpdates = true;
    // 设置一个默认材质
    static ConstructorHelpers::FObjectFinder<UMaterial> DefaultMaterial(TEXT("/Game/Materials/FaceMaterial"));
    if (DefaultMaterial.Succeeded())
    {
        FaceMeshComponent->FaceMaterial = DefaultMaterial.Object;
    }
    // 设置为仅使用追踪到的变换（假设 Actor 位于世界原点）
    FaceMeshComponent->TransformSetting = EARFaceComponentTransformMixing::TrackingOnly;
}

void AMyFaceActor::BeginPlay()
{
    Super::BeginPlay();
    // 在游戏开始时，可以选择开启自动绑定以获取实时面部数据
    // FaceMeshComponent->SetAutoBind(true);
    // 或者启动 LiveLink 发布
    // FaceMeshComponent->PublishViaLiveLink(FName("MyActorFace"));
}

void AMyFaceActor::SetBlendShape(EARFaceBlendShape Shape, float Value)
{
    if (FaceMeshComponent)
    {
        FaceMeshComponent->SetBlendShapeAmount(Shape, Value);
        // 设置后需要调用此函数来更新网格
        FaceMeshComponent->UpdateMeshFromBlendShapes();
    }
}
```

### 进阶用法

结合 LiveLink 发布和混合变形列表的完整更新：
（来源：基于 `SetBlendShapes` 和 `PublishViaLiveLink` API）

```cpp
// 假设你有一个 TMap<EARFaceBlendShape, float> NewBlendShapes 包含了从某处获取的全部混合变形数据
void UpdateFaceFromNetworkData(const TMap<EARFaceBlendShape, float>& NewBlendShapes)
{
    if (FaceMeshComponent && FaceMeshComponent->bAutoBindToLocalFaceMesh == false)
    {
        // 使用接收到的完整数据集更新组件内部的混合变形
        FaceMeshComponent->SetBlendShapes(NewBlendShapes);
        // 更新网格
        FaceMeshComponent->UpdateMeshFromBlendShapes();
        // 这些数据也会通过之前启动的 LiveLink 发布出去
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例 Actor，用于接收并显示来自 ARKit 的面部数据。

```cpp
// ARFaceDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AppleARKitFaceMeshComponent.h"
#include "ARFaceDemoActor.generated.h"

UCLASS()
class AARFaceDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AARFaceDemoActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    UAppleARKitFaceMeshComponent* FaceMesh;
};
```

```cpp
// ARFaceDemoActor.cpp
#include "ARFaceDemoActor.h"
#include "UObject/ConstructorHelpers.h"

AARFaceDemoActor::AARFaceDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    FaceMesh = CreateDefaultSubobject<UAppleARKitFaceMeshComponent>(TEXT("FaceMesh"));
    RootComponent = FaceMesh;

    // 配置
    FaceMesh->bWantsMeshUpdates = true;
    FaceMesh->bAutoBindToLocalFaceMesh = true; // 自动从设备获取数据
    FaceMesh->TransformSetting = EARFaceComponentTransformMixing::TrackingOnly;
    FaceMesh->bFlipTrackedRotation = true; // 根据设备方向调整

    // 尝试加载一个基础材质
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> MaterialFinder(TEXT("/Game/Materials/M_FaceDefault"));
    if (MaterialFinder.Succeeded())
    {
        FaceMesh->FaceMaterial = MaterialFinder.Object;
    }
}

void AARFaceDemoActor::BeginPlay()
{
    Super::BeginPlay();
    // 确保自动绑定已启用（尽管在构造函数中设置了）
    if (!FaceMesh->bAutoBindToLocalFaceMesh)
    {
        FaceMesh->SetAutoBind(true);
    }
    // 开始通过 LiveLink 发布数据，主题名为 “ARFaceDemo”
    FaceMesh->PublishViaLiveLink(FName(“ARFaceDemo”));
}
```

**使用说明**：
1.  将此类放入你的项目并编译。
2.  在关卡中放置一个 `AARFaceDemoActor` 实例。
3.  确保项目已启用 `AppleARKit` 和 `AppleARKitFaceSupport` 插件。
4.  在 iOS 或 macOS 设备上运行，该 Actor 的面部网格应会实时反映你的面部动作。
5.  你可以在任何其他角色的动画蓝图中，通过 LiveLink 主题 `“ARFaceDemo”` 来接收并使用这些面部数据。

## 模块依赖

要使用此插件的功能，你的模块（例如包含上述 Actor 的游戏模块）需要在 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `AppleARKitFaceSupport` | 核心 API，提供 `UAppleARKitFaceMeshComponent` 等类。 |
| `AppleARKit` | 底层 ARKit 封装，提供基础的 AR 会话和数据类型。是运行此插件的前提。 |

```cpp
// YourModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "AppleARKitFaceSupport", // 添加此行
    "AppleARKit"             // 添加此行
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，属于内部代码规范统一。 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复了对非便携式工具链的支持问题，提高了跨平台编译兼容性。 |
| 2025-06-11 | `8406cd44` | Replace some usages of FORCEINLINE with inline in AR modules. | 将部分 FORCEINLINE 替换为 inline，属于代码风格和编译优化调整。 |
| 2024-10-07 | `a8971688` | Set a min / max value for ARKit connection settings | 为 LiveLink 连接端口设置了最小和最大值限制（1-32765）。 |
| 2024-04-17 | `a1d5ecfc` | Fix ios compile error | 修复了一个 iOS 平台的编译错误。 |

### 维护评价

该插件创建于 2020 年，已有约 6 年历史，属于**老古董**级别。从 git 历史看，它处于**低度维护**状态。最近两年的更新主要是平台兼容性修复、编译错误修正和代码规范调整，没有引入新的功能特性。这表明插件功能已经相对稳定和成熟，但 Epic 可能没有投入大量资源进行新功能开发。

对于需要苹果设备面部追踪功能的项目，此插件仍然是**官方支持且可用的解决方案**。由于它依赖于 `AppleARKit` 底层插件，且 API 相对稳定，可以放心使用。但要注意，`EnabledByDefault` 为 `false`，你必须在项目设置中手动启用它。

**建议**：如果你的项目确实需要此功能，可以放心集成。但不要期待短期内会有重大功能更新。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/AppleAR/AppleARKitFaceSupport)
*   [官方文档](https://docs.unrealengine.com/) (需在官方文档中搜索 “Apple ARKit” 或 “Face Tracking” 相关内容)
*   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/AppleAR/AppleARKitFaceSupport) (在插件目录内未发现独立的测试文件，功能可能包含在 ARKit 主插件或 LiveLink 模块的测试中)
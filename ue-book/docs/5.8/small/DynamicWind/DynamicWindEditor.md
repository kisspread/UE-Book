# Dynamic Wind

> Extremely experimental dynamic wind support for Nanite foliage.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 动态风效 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `DynamicWind` (Runtime), `DynamicWindEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DynamicWind) | |

## 用途

该插件为 Nanite 植被提供动态风效支持。从源码分析，它并非一个独立的渲染系统，而是一套**资产转换工具链**。其核心功能是帮助将使用 Pivot Painter 工作流制作的静态网格树资产（Static Mesh Tree），转换为可用于模拟动态骨骼动画（风吹效果）的骨骼网格（Skeletal Mesh）。转换后的数据（关节、模拟组等）以资产用户数据（Asset User Data）的形式附加到骨骼网格上，供运行时动态风系统读取和使用。

因此，该插件解决的是 **Nanite 渲染的静态植被如何获得动态摇曳效果**的问题。Nanite 要求网格静态，但传统的风动效果依赖顶点动画或骨骼动画。该插件提供了一条路径，将静态树的结构信息（通过 Pivot Painter 纹理编码）提取并转化为骨骼动画所需的骨骼数据和权重，从而让 Nanite 植被“动”起来。

## 使用场景

- 你正在开发一个使用 Nanite 技术的大规模开放世界游戏，场景中包含大量树木、草地等植被。
- 你的美术使用 Pivot Painter 工作流（在 3ds Max、Blender 等 DCC 工具中）制作了树木资产，并希望为它们添加逼真的风吹摇曳动画。
- 你需要将这些静态的树木资产转换为引擎运行时可以播放动态风效动画的骨骼网格资产。

## 蓝图用法

该插件的蓝图功能主要集中在 `UDynamicWindBlueprintLibrary` 类中，提供了两个核心转换/导入节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConvertPivotPainterTreeToSkeletalMesh` | 将一个使用 Pivot Painter 纹理的静态网格树资产，转换并合并到目标骨骼网格资产中。 | `UDynamicWindBlueprintLibrary` |
| `ImportDynamicWindSkeletalDataFromFile` | 从文件（可能是自定义格式）中导入动态风骨骼数据，并设置到目标骨骼网格资产中。 | `UDynamicWindBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **资产转换流程**：
    - 在蓝图中，获取你的原始树木静态网格（`TreeStaticMesh`）和对应的 Pivot Painter 位置纹理（`TreePivotPosTexture`）。
    - 创建或指定一个目标骨骼网格（`TargetSkeletalMesh`）和一个骨骼（`TargetSkeleton`）。
    - 调用 `ConvertPivotPainterTreeToSkeletalMesh` 节点，将原始静态网格的拓扑和动画信息“烘焙”到目标骨骼网格中。这个节点内部会处理顶点权重、创建骨骼层级等。

2.  **数据导入流程**：
    - 如果已经有准备好的 `.uasset` 文件包含动态风数据，可以调用 `ImportDynamicWindSkeletalDataFromFile` 节点，将数据直接加载并应用到目标骨骼网格。

## C++ 用法

### 头文件引入

```cpp
// 使用蓝图库函数
#include "DynamicWindBlueprintLibrary.h"
// 使用导入数据结构和函数
#include "DynamicWindImportData.h"
```

### 基本用法

基于代码分析，展示如何通过 C++ 调用蓝图库函数进行资产转换。
*(来源文件：`Private/DynamicWindBlueprintLibrary.h`)*

```cpp
#include "DynamicWindBlueprintLibrary.h"
#include "Engine/StaticMesh.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/Texture2D.h"
#include "Engine/Skeleton.h"

void ConvertTreeAsset()
{
    // 假设这些资产指针已经加载或获取
    UStaticMesh* TreeStaticMesh = ...;
    UTexture2D* PivotPosTexture = ...;
    USkeletalMesh* TargetSkelMesh = NewObject<USkeletalMesh>();
    USkeleton* TargetSkeleton = NewObject<USkeleton>();

    // 调用蓝图库中的静态函数
    bool bSuccess = UDynamicWindBlueprintLibrary::ConvertPivotPainterTreeToSkeletalMesh(
        TreeStaticMesh,
        PivotPosTexture,
        0, // UV索引
        TargetSkelMesh,
        TargetSkeleton
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully converted static mesh tree to skeletal mesh with wind data."));
        // 保存或使用 TargetSkelMesh ...
    }
}
```

### 进阶用法

使用导入数据结构，在代码中构建复杂的风模拟参数，并将其导入到骨骼网格。
*(来源文件：`Public/DynamicWindImportData.h`)*

```cpp
#include "DynamicWindImportData.h"
#include "SkeletalMesh.h"

void ImportCustomWindData()
{
    USkeletalMesh* SkelMesh = ...; // 获取目标骨骼网格

    // 1. 构建导入数据
    FDynamicWindSkeletalImportData ImportData;
    ImportData.bIsGroundCover = false; // 是树，不是草
    ImportData.GustAttenuation = 0.7f; // 设置阵风衰减系数

    // 2. 添加关节数据（模拟树的枝干结构）
    FDynamicWindJointImportData RootJoint;
    RootJoint.JointName = TEXT("Trunk");
    RootJoint.SimulationGroupIndex = 0;
    ImportData.Joints.Add(RootJoint);

    FDynamicWindJointImportData BranchJoint;
    BranchJoint.JointName = TEXT("Branch_01");
    BranchJoint.SimulationGroupIndex = 1; // 属于不同的模拟组，可以有不同的风力影响
    ImportData.Joints.Add(BranchJoint);

    // 3. 添加模拟组数据（可选，用于更精细的控制）
    FDynamicWindSimulationGroupData TrunkGroup;
    TrunkGroup.GroupIndex = 0;
    // ... 设置组参数如硬度、阻尼等
    ImportData.SimulationGroups.Add(TrunkGroup);

    // 4. 执行导入
    UDynamicWindSkeletalData* ImportedData = DynamicWind::ImportSkeletalData(*SkelMesh, ImportData);
    if (ImportedData)
    {
        UE_LOG(LogTemp, Log, TEXT("Custom wind data imported successfully."));
        // ImportedData 现在作为 Asset User Data 挂在 SkelMesh 上
    }
}
```

## Demo 示例

一个最小的可编译示例，演示如何在一个 Actor 中使用该插件的核心转换功能。

### WindTreeConverterActor.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WindTreeConverterActor.generated.h"

class UStaticMeshComponent;
class USkeletalMeshComponent;

UCLASS()
class AWindTreeConverterActor : public AActor
{
    GENERATED_BODY()

public:
    AWindTreeConverterActor();

    UPROPERTY(EditAnywhere, Category="Wind Conversion")
    UStaticMesh* SourceTreeStaticMesh;

    UPROPERTY(EditAnywhere, Category="Wind Conversion")
    UTexture2D* PivotPainterTexture;

    UPROPERTY(VisibleAnywhere, Category="Wind Conversion")
    USkeletalMeshComponent* ConvertedSkeletalMeshComponent;

    UFUNCTION(BlueprintCallable, CallInEditor, Category="Wind Conversion")
    void ExecuteConversion();
};
```

### WindTreeConverterActor.cpp
```cpp
#include "WindTreeConverterActor.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "DynamicWindBlueprintLibrary.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/Skeleton.h"

AWindTreeConverterActor::AWindTreeConverterActor()
{
    PrimaryActorTick.bCanEverTick = false;

    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    ConvertedSkeletalMeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("SkelMeshComp"));
    ConvertedSkeletalMeshComponent->SetupAttachment(RootComponent);
}

void AWindTreeConverterActor::ExecuteConversion()
{
    if (!SourceTreeStaticMesh || !PivotPainterTexture)
    {
        UE_LOG(LogTemp, Warning, TEXT("Source assets not set."));
        return;
    }

    // 在运行时或编辑器中动态创建资产（示例，实际可能需要资产保存逻辑）
    USkeletalMesh* NewSkelMesh = NewObject<USkeletalMesh>(GetTransientPackage(), NAME_None, RF_Public | RF_Standalone);
    USkeleton* NewSkeleton = NewObject<USkeleton>(GetTransientPackage(), NAME_None, RF_Public | RF_Standalone);

    // 调用插件的核心转换函数
    bool bSuccess = UDynamicWindBlueprintLibrary::ConvertPivotPainterTreeToSkeletalMesh(
        SourceTreeStaticMesh,
        PivotPainterTexture,
        0,
        NewSkelMesh,
        NewSkeleton
    );

    if (bSuccess)
    {
        // 将转换后的网格应用到组件
        ConvertedSkeletalMeshComponent->SetSkeletalMesh(NewSkelMesh);
        UE_LOG(LogTemp, Log, TEXT("Wind tree conversion succeeded!"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Wind tree conversion failed."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RenderCore`, `Renderer` | DynamicWind Runtime 模块依赖的渲染核心模块，用于处理与风效相关的着色器和数据。 |
| `AssetTools`, `ContentBrowser` | DynamicWindEditor 模块依赖的编辑器工具模块，用于创建资产工厂和集成到编辑器右键菜单（尽管 `ShouldShowInNewMenu` 返回 false）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `8b5eabf3` | FastGeo: Support GPU animated instanced skinned meshes. | 支持 FastGeo 中 GPU 动画的实例化骨骼网格。 |
| 2026-04-14 | `b1c9fc96` | Fixed dynamic wind ES31 compilation error not supporting bit fields in structured buffers. | 修复了在 ES31 上，结构缓冲区不支持位域导致的编译错误。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到 UE_LOGF 格式。 |
| 2026-04-09 | `39e82b40` | Refactored ASTP to support layers and blend spaces. Rather than use a parent / child hierarchy, ther | 重构了 ASTP 以支持层和混合空间。 |
| 2026-04-02 | `ac7816b3` | Implement dynamic wind for GPU skin and unified bone indices which both use a bone map. | 实现了对 GPU 蒙皮和统一骨骼索引（均使用骨骼映射）的动态风支持。 |

### 维护评价

- **创建时间**：插件创建于 2025 年 8 月，非常年轻，处于早期开发阶段。
- **更新频率**：从 git 历史看，在 2026 年 4-5 月有多次实质性更新，涉及功能扩展（GPU 蒙皮支持）、错误修复和重构，表明**维护活跃**。
- **内容相关性**：更新内容与插件核心功能（风效、骨骼、GPU 皮肤）直接相关，并非简单的编译适配。
- **实验性状态**：插件明确标记为 `IsExperimentalVersion: true` 且默认禁用，说明其 API 和功能尚不稳定，可能在未来的引擎版本中发生重大变化。
- **综合评价**：这是一个**活跃维护中的实验性插件**。它专注于解决一个具体且前沿的技术问题（Nanite植被动画），近期有持续的功能迭代。**推荐用于学习和技术预研**，但不建议在需要长期稳定性的商业项目中作为核心依赖使用。由于是实验性功能，使用时应准备好应对潜在的破坏性更改。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DynamicWind)
- [官方文档]() (暂无)
- [测试用例]() (暂未在插件目录内发现)
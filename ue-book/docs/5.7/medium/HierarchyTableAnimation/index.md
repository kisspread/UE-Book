# Hierarchy Table Animation

> Animation-specific type definitions for Hierarchy Tables

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画节点蓝图资产） |
| 模块 | `HierarchyTableAnimationRuntime` (Runtime), `HierarchyTableAnimationEditor` (Editor), `HierarchyTableAnimationUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/HierarchyTableAnimation) | |

## 用途

HierarchyTableAnimation 是 UE5 动画系统中用于**基于骨骼层级的分层混合**的插件。它建立在通用的 [HierarchyTable](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/HierarchyTable) 插件之上，为其扩展了骨骼动画专用的类型定义和工具。

核心解决的问题：在动画蓝图中实现**精确的逐骨骼、逐曲线、逐属性的混合权重控制**。传统的 Layered Blend Per Bone 节点只能按骨骼层级设置混合权重，而 HierarchyTableAnimation 通过独立的 Blend Profile 资产，允许你：

- 为每根骨骼设置独立的混合权重（0.0 ~ 1.0）
- 为动画曲线（Curve）设置独立的混合权重
- 为自定义动画属性（Attribute，如 RootMotionDelta）设置独立的混合权重
- 将这些配置保存为可复用的独立资产（`UBlendProfileStandalone`），而非嵌入在动画蓝图中

简而言之，这是 UE5 对传统 Blend Profile 机制的升级版——从"嵌入在 Skeleton 中的配置"变为"独立的资产化配置"，并支持 Mask 类型的更精细控制。

## 使用场景

- **上半身/下半身分层动画**：你在做第三人称射击游戏，角色下半身播放跑步动画，上半身播放射击动画 → 使用 Blend Profile 设置上半身骨骼权重为 1.0，下半身为 0.0
- **精细的面部动画混合**：你需要同时混合多个面部 Morph Target 曲线，不同曲线需要不同的混合权重 → 使用 Mask 类型的 Blend Profile 为每条曲线单独设置权重
- **Root Motion 精确控制**：你在做动画混合时需要精确控制哪些属性参与 Root Motion 混合 → 在 Blend Profile 中为 RootMotionDelta 属性单独设置权重
- **可复用的混合配置**：你的多个动画蓝图或多个角色需要相同的混合配置 → 将 Blend Profile 保存为独立资产，在多处引用

## 蓝图用法

此插件主要通过动画蓝图中的 AnimGraph 节点使用，不暴露 BlueprintCallable 函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| **Profile Blend** | 基于 Blend Profile 资产的分层混合节点，支持逐骨骼/逐曲线/逐属性混合权重 | `UAnimGraphNode_BlendProfileLayeredBlend` |

### AnimGraph 节点属性

在动画蓝图的 AnimGraph 中添加 "Profile Blend" 节点（位于 `Animation > Blends` 分类下）：

| 属性 | 类型 | 说明 |
|---|---|---|
| `BasePose` | FPoseLink | 基础姿势（底层动画） |
| `BlendPose` | FPoseLink | 混合姿势（上层动画） |
| `BlendProfileAsset` | UBlendProfileStandalone* | 控制逐骨骼/曲线/属性混合权重的 Blend Profile 资产 |
| `BlendWeight` | float | 整体混合权重（0.0 ~ 1.0），默认 1.0 |
| `bMeshSpaceRotationBlend` | bool | 是否在 Mesh 空间而非本地空间混合骨骼旋转 |
| `bCustomCurveBlending` | bool | 是否使用自定义曲线混合模式 |
| `CurveBlendingOption` | ECurveBlendOption | 自定义曲线混合方式（Override/Normalize/Weighted 等） |
| `bBlendRootMotionBasedOnRootBone` | bool | 是否根据根骨骼的混合权重来混合 Root Motion，默认 true |

### 使用示例（蓝图描述）

1. **创建 Blend Profile 资产**：在 Content Browser 右键 → Animation → Blend Profile，选择类型（WeightFactor / TimeFactor / BlendMask），然后选择关联的 Skeleton
2. **编辑 Blend Profile**：双击打开 Blend Profile 编辑器，在层级表中为每根骨骼/曲线/属性设置 0.0 ~ 1.0 的权重值
3. **在 AnimGraph 中使用**：在动画蓝图中添加 "Profile Blend" 节点，将 BasePose 连接基础动画（如 Idle），BlendPose 连接上层动画（如 Aim Offset），然后将 Blend Profile 资产拖到 `BlendProfileAsset` 属性上

## C++ 用法

### 头文件引入

```cpp
// Runtime 层 - 动画节点和 Blend Profile 核心类型
#include "AnimNode_BlendProfileLayeredBlend.h"
#include "BlendProfileStandalone.h"
#include "HierarchyTableBlendProfile.h"
#include "SkeletonHierarchyTableType.h"

// Mask 类型
#include "MaskProfile/HierarchyTableTypeMask.h"
```

### 基本用法 - 创建 HierarchyTableBlendProfile

从 HierarchyTable（层级表）数据构建 Blend Profile，用于逐骨骼混合权重计算。

```cpp
// 来源: Source/Runtime/Private/HierarchyTableBlendProfile.cpp

// 假设已有一个包含骨骼权重的 UHierarchyTable
TObjectPtr<UHierarchyTable> HierarchyTable = /* ... */;

// 从 HierarchyTable 构建 Blend Profile（WeightFactor 模式）
FHierarchyTableBlendProfile BlendProfile(HierarchyTable, EBlendProfileMode::WeightFactor);

// 获取特定骨骼的混合权重
float BoneWeight = BlendProfile.GetBoneBlendScale(BoneIndex);

// 获取曲线混合权重
const auto& CurveWeights = BlendProfile.GetCurveBlendWeights();

// 获取属性混合权重
const auto& AttributeWeights = BlendProfile.GetAttributeBlendWeights();

// 将 BlendProfile 数据写入引擎原生 UBlendProfile 对象
TObjectPtr<UBlendProfile> NativeBlendProfile = NewObject<UBlendProfile>();
BlendProfile.ConstructBlendProfile(NativeBlendProfile);
```

### 基本用法 - 使用 UBlendProfileStandalone 资产

`UBlendProfileStandalone` 是可序列化的独立资产，内部包含一个 UHierarchyTable 用于存储混合权重。

```cpp
// 来源: Source/Runtime/Public/BlendProfileStandalone.h

// 获取 Blend Profile 资产的类型
TObjectPtr<UBlendProfileStandalone> BlendProfileAsset = /* ... */;
EBlendProfileStandaloneType Type = BlendProfileAsset->Type;
// 可选值: WeightFactor, TimeFactor, BlendMask

// 获取关联的 Skeleton
TObjectPtr<USkeleton> Skeleton = BlendProfileAsset->GetSkeleton();

// 获取运行时缓存的混合数据（扁平化，高效访问）
const FBlendProfileStandaloneCachedData& CachedData = BlendProfileAsset->CachedBlendProfileData;

// 骨骼权重数组（按骨骼索引）
const TArray<float>& BoneWeights = CachedData.GetBoneBlendWeights();

// 曲线权重
const auto& CurveWeights = CachedData.GetCurveBlendWeights();

// 属性权重
const auto& AttributeWeights = CachedData.GetAttributeBlendWeights();
```

### 进阶用法 - AnimNode 混合流程

`FAnimNode_BlendProfileLayeredBlend` 的评估流程展示了 Blend Profile 在动画节点中的完整工作方式：

```cpp
// 来源: Source/Runtime/Private/AnimNode_BlendProfileLayeredBlend.cpp

// 1. 验证 Blend Profile 有效性
const bool bBlendProfileValid = Skeleton
    && BlendProfileAsset
    && BlendProfileAsset->Type == EBlendProfileStandaloneType::BlendMask
    && BlendProfileAsset->GetSkeleton() == Skeleton;

// 2. 获取缓存的骨骼权重（在 CacheBones 阶段已计算）
// CurrentBoneBlendWeights 数组大小 = RequiredBones 数量
// 每个权重 = BlendWeight * DesiredBoneBlendWeights[BoneIndex]

// 3. 逐骨骼混合两个姿势
FAnimationRuntime::BlendTwoPosesTogetherPerBone(
    BasePoseData.GetPose(),
    BlendPoseData.GetPose(),
    CurrentBoneBlendWeights,  // 每根骨骼的独立权重
    Output.Pose
);

// 4. 曲线混合 - 使用 Mask 权重过滤
// 曲线权重为 0 的曲线会被从 BlendPose 中移除
// 曲线权重为 1 的曲线会完全覆盖 BasePose 中的对应曲线
// 曲线权重在 (0,1) 之间会进行 Lerp 插值

// 5. 属性混合 - 两阶段处理
// 第一阶段: 按骨骼权重混合（属性继承其附着骨骼的权重）
UE::Anim::Attributes::BlendAttributesPerBone(
    BasePoseData.GetAttributes(),
    BlendPoseData.GetAttributes(),
    CurrentBoneBlendWeights,
    OutputAttributes
);
// 第二阶段: 对有自定义权重的属性进行修正（覆盖骨骼继承的权重）
```

### 进阶用法 - Skeleton 层级表类型

`FHierarchyTable_TableType_Skeleton` 定义了与骨骼绑定的层级表结构：

```cpp
// 来源: Source/Runtime/Public/SkeletonHierarchyTableType.h

// 层级表的元数据类型 - 指定关联的 Skeleton
FHierarchyTable_TableType_Skeleton TableMetadata;
TableMetadata.Skeleton = MySkeleton;

// 层级表中每个条目的 Payload 类型
// 用于区分条目是骨骼、曲线还是属性
FHierarchyTable_TablePayloadType_Skeleton EntryPayload;

EntryPayload.EntryType = ESkeletonHierarchyTable_TablePayloadEntryType::Bone;     // 骨骼
EntryPayload.EntryType = ESkeletonHierarchyTable_TablePayloadEntryType::Curve;    // 曲线
EntryPayload.EntryType = ESkeletonHierarchyTable_TablePayloadEntryType::Attribute; // 属性
```

### 进阶用法 - Mask 元素类型

```cpp
// 来源: Source/Runtime/Public/MaskProfile/HierarchyTableTypeMask.h

// Mask 类型的层级表元素，Value 范围 [0.0, 1.0]
FHierarchyTable_ElementType_Mask MaskElement;
MaskElement.Value = 0.75f;  // 75% 混合权重
```

## Demo 示例

### 最小混合 Profile 使用示例

以下示例展示如何在 C++ 中创建和使用 HierarchyTableBlendProfile。

**Build.cs 依赖**:

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "HierarchyTableRuntime",
    "HierarchyTableAnimationRuntime"
});
```

**BlendProfileExample.h**:

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "BlendProfileExample.generated.h"

class UBlendProfileStandalone;
class USkeleton;

UCLASS(ClassGroup=(Animation), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UBlendProfileExample : public UActorComponent
{
    GENERATED_BODY()

public:
    // 混合 Profile 资产引用（可在编辑器中指定）
    UPROPERTY(EditAnywhere, Category = "Blend Profile")
    TObjectPtr<UBlendProfileStandalone> BlendProfileAsset;

    // 打印 Blend Profile 中所有骨骼的混合权重
    UFUNCTION(BlueprintCallable, Category = "Blend Profile")
    void PrintBlendProfileWeights() const;

    // 构建原生 BlendProfile 对象
    UFUNCTION(BlueprintCallable, Category = "Blend Profile")
    UBlendProfile* BuildNativeBlendProfile() const;
};
```

**BlendProfileExample.cpp**:

```cpp
#include "BlendProfileExample.h"
#include "BlendProfileStandalone.h"
#include "HierarchyTableBlendProfile.h"
#include "Animation/BlendProfile.h"
#include "Animation/Skeleton.h"

void UBlendProfileExample::PrintBlendProfileWeights() const
{
    if (!BlendProfileAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("BlendProfileAsset is null"));
        return;
    }

    const FBlendProfileStandaloneCachedData& CachedData =
        BlendProfileAsset->CachedBlendProfileData;

    const TArray<float>& BoneWeights = CachedData.GetBoneBlendWeights();

    TObjectPtr<USkeleton> Skeleton = BlendProfileAsset->GetSkeleton();
    if (!Skeleton)
    {
        return;
    }

    const FReferenceSkeleton& RefSkeleton = Skeleton->GetReferenceSkeleton();

    UE_LOG(LogTemp, Log, TEXT("=== Blend Profile: %s ==="),
        *BlendProfileAsset->GetName());
    UE_LOG(LogTemp, Log, TEXT("Type: %d, Bone Count: %d"),
        static_cast<int32>(BlendProfileAsset->Type), BoneWeights.Num());

    for (int32 i = 0; i < BoneWeights.Num(); ++i)
    {
        if (BoneWeights[i] != 1.0f) // 只打印非默认值
        {
            UE_LOG(LogTemp, Log, TEXT("  Bone[%d] %s: %.3f"),
                i, *RefSkeleton.GetBoneName(i).ToString(), BoneWeights[i]);
        }
    }

    // 打印曲线权重
    const auto& CurveWeights = CachedData.GetCurveBlendWeights();
    for (const auto& Curve : CurveWeights)
    {
        UE_LOG(LogTemp, Log, TEXT("  Curve %s: %.3f"),
            *Curve.Name.ToString(), Curve.Value);
    }

    // 打印属性权重
    const auto& AttrWeights = CachedData.GetAttributeBlendWeights();
    for (const auto& Attr : AttrWeights)
    {
        UE_LOG(LogTemp, Log, TEXT("  Attribute: Weight %.3f"), Attr.Weight);
    }
}

UBlendProfile* UBlendProfileExample::BuildNativeBlendProfile() const
{
    if (!BlendProfileAsset)
    {
        return nullptr;
    }

    UBlendProfile* NativeProfile = NewObject<UBlendProfile>();
    BlendProfileAsset->CachedBlendProfileData.ConstructBlendProfile(NativeProfile);
    return NativeProfile;
}
```

## 模块依赖

### Runtime 模块 (HierarchyTableAnimationRuntime)

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Skeleton、AnimInstance 等） |
| `HierarchyTableRuntime` | 层级表运行时核心（UHierarchyTable、FHierarchyTableEntryData 等） |

### Editor 模块 (HierarchyTableAnimationEditor)

| 模块 | 用途 |
|---|---|
| `AssetDefinition` | 资产定义系统（Content Browser 中的资产类型注册） |
| `HierarchyTableEditor` | 层级表编辑器 UI（SHierarchyTable 组件等） |
| `HierarchyTableAnimationRuntime` | 运行时模块依赖 |
| `Persona` | 动画编辑器框架（BlendProfile Picker 扩展、Curve Picker 等） |
| `PropertyEditor` | 属性面板自定义（Skeleton 表类型的 Details Customization） |
| `ToolMenus` | 工具栏和菜单扩展 |

### UncookedOnly 模块 (HierarchyTableAnimationUncookedOnly)

| 模块 | 用途 |
|---|---|
| `AnimGraph` | 动画蓝图图节点基类（UAnimGraphNode_BlendListBase） |
| `AnimGraphRuntime` | AnimGraph 运行时支持 |
| `AnimationBlueprintLibrary` | 动画蓝图工具库 |
| `AnimationCore` | 动画核心类型 |
| `Kismet` | 蓝图编译支持（仅编辑器） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-09-08 | `1479428` | **功能更新**: Profile Blend 节点支持编辑器内实时更新混合权重。编辑 Blend Profile 资产后立即反映到 AnimGraph 节点，无需重新编译动画蓝图。同时添加了编辑器撤销支持。 |
| 2025-07-17 | `110a586` | **优化**: 移除不必要的默认分配器内存分配，提升性能 |
| 2025-07-10 | `9803c44` | **构建维护**: 添加 UE_INLINE_GENERATED_CPP_BY_NAME 宏到源文件 |

### 维护评价

- **创建时间**: 2024-11-21，约 1 年历史，属于较新的插件
- **维护状态**: **活跃维护** — 2025 年 9 月有功能性更新（实时权重预览），说明 Epic 仍在积极开发
- **实验性状态**: `IsExperimentalVersion=true`，`EnabledByDefault=false` — 需手动启用，API 可能在未来版本发生变化
- **历史背景**: 从 `.ini` 中的 CoreRedirects 可以看到，此插件从 `HierarchyTableBuiltin` 重命名而来，说明经历了架构调整
- **已知限制**:
  - `AnimGraphNode_BlendProfileLayeredBlend` 编译时只验证 `BlendMask` 类型的资产，不支持 `WeightFactor` 和 `TimeFactor`
  - 层级表的条目修改后需要调用 `RegenerateEntriesGuid()` 来标记数据变更
  - 曲线和属性必须有父条目（`check(TableEntry.HasParent())`），不能作为顶层条目存在
- **推荐使用**: 适合需要精确逐骨骼/逐曲线混合控制的项目。由于是实验性插件，建议在生产环境中做好升级兼容准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/HierarchyTableAnimation)
- [HierarchyTable 基础插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/HierarchyTable)
- [HierarchyTableBuiltin 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/HierarchyTableBuiltin)
- 官方文档: 无（DocsURL 为空）
- 测试用例: 未发现独立测试文件

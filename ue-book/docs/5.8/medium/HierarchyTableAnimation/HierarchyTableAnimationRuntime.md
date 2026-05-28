# Hierarchy Table Animation

> Animation-specific type definitions for Hierarchy Tables

| 属性 | 值 |
|---|---|
| 中文名 | 层级表动画 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、骨架混合配置） |
| 模块 | `HierarchyTableAnimationRuntime` (Runtime), `HierarchyTableAnimationEditor` (Editor), `HierarchyTableAnimationUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/HierarchyTableAnimation) | |

## 用途

本插件是 [HierarchyTable](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HierarchyTable) 插件在动画领域的扩展。它解决了**按骨骼、曲线、属性分别控制混合权重**的问题。

核心功能：

- **基于层级表的混合配置文件（Blend Profile）**：将骨架的骨骼层级与混合权重绑定，每个骨骼、动画曲线、属性都可以有独立的混合权重值
- **分层混合动画节点**：提供 `BlendProfileLayeredBlend` 动画图节点，支持将基础姿态和混合姿态按自定义骨骼权重进行分层混合
- **独立混合配置资产**：`UBlendProfileStandalone` 将层级表数据展平为运行时可用的缓存格式，避免运行时遍历树结构的性能开销

典型场景：角色上半身播放射击动画、下半身播放跑步动画时，需要对每根骨骼指定不同的混合权重——本插件就是为此而生。

## 使用场景

- 你需要角色上半身和下半身分别播放不同动画，并用**逐骨骼权重**控制混合区域
- 你需要同时混合动画曲线（如面部表情）和骨骼变换，且权重各不相同
- 你需要在根骨骼运动（Root Motion）混合时，根据根骨骼权重决定是否融合
- 你需要将混合配置保存为独立资产，在多个动画蓝图间复用

## 蓝图用法

本插件的蓝图功能主要通过**动画图（AnimGraph）系统**暴露。`FAnimNode_BlendProfileLayeredBlend` 标记为 `BlueprintInternalUseOnly`，由动画蓝图编译器自动创建，用户通过动画图编辑器操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BlendProfileLayeredBlend` | 基于混合配置文件的分层混合节点 | `UAnimGraphNode_BlendProfileLayeredBlend`（Editor 模块） |

### 节点属性

在动画图编辑器中放置 `BlendProfileLayeredBlend` 节点后，可在细节面板中配置：

| 属性 | 类型 | 说明 |
|---|---|---|
| `BasePose` | Pose Link | 基础姿态输入 |
| `BlendPose` | Pose Link | 混合目标姿态输入 |
| `BlendProfileAsset` | `UBlendProfileStandalone` | 混合配置资产，控制逐骨骼/曲线/属性的混合权重 |
| `RotationBlendSpace` | `EBlendProfileRotationBlendSpace` | 旋转混合空间：Local（局部）、Mesh（网格体）、Root（根骨骼相对） |
| `bCustomCurveBlending` | bool | 是否启用自定义曲线混合 |
| `CurveBlendingOption` | `ECurveBlendOption` | 曲线混合模式（Override、DoNotOverride 等） |
| `BlendWeight` | float | 混合目标姿态的权重（0~1） |
| `bBlendRootMotionBasedOnRootBone` | bool | 是否根据根骨骼混合权重融合根骨骼运动 |

### 使用示例（动画图描述）

1. 在动画蓝图的 AnimGraph 中添加 `BlendProfileLayeredBlend` 节点
2. 将基础动画（如跑步）连接到 `BasePose`
3. 将叠加动画（如射击上半身）连接到 `BlendPose`
4. 创建一个 `BlendProfileStandalone` 资产，关联角色骨架，在编辑器中设置各骨骼权重（如上半身骨骼权重 1.0，下半身 0.0）
5. 将该资产指定给 `BlendProfileAsset` 属性
6. 通过 `BlendWeight` 引脚（支持 Pin 动态连接）控制混合强度

## C++ 用法

### 头文件引入

```cpp
#include "AnimNode_BlendProfileLayeredBlend.h"
#include "BlendProfileStandalone.h"
#include "HierarchyTableBlendProfile.h"
```

### 基本用法：创建独立混合配置资产

```cpp
// 创建一个 UBlendProfileStandalone 资产（通常在编辑器工具或导入流程中）
UBlendProfileStandalone* BlendProfile = NewObject<UBlendProfileStandalone>(GetTransientPackage(), FName("MyBlendProfile"));
BlendProfile->Type = EBlendProfileStandaloneType::WeightFactor;

#if WITH_EDITOR
// 关联骨架并构建层级
BlendProfile->UpdateHierarchy();
BlendProfile->UpdateCachedData();
#endif

// 通过缓存数据获取骨骼混合权重
const FBlendProfileStandaloneCachedData& CachedData = BlendProfile->CachedBlendProfileData;
const TArray<float>& BoneWeights = CachedData.GetBoneBlendWeights();
const auto& CurveWeights = CachedData.GetCurveBlendWeights();
const auto& AttributeWeights = CachedData.GetAttributeBlendWeights();
```

### 进阶用法：直接使用 FHierarchyTableBlendProfile

```cpp
// 从骨架创建混合配置文件（不依赖 UBlendProfileStandalone 资产）
USkeleton* MySkeleton = /* 获取骨架 */;
FHierarchyTableBlendProfile BlendProfile(MySkeleton, EBlendProfileMode::WeightFactor);

// 查询骨骼混合权重
float HeadBoneBlend = BlendProfile.GetBoneBlendScale(HeadBoneIndex);

// 查询曲线混合权重
const auto& CurveWeights = BlendProfile.GetCurveBlendWeights();
for (const auto& Curve : CurveWeights)
{
    // Curve 包含曲线名和权重值
}

// 查询属性混合权重
const auto& AttributeWeights = BlendProfile.GetAttributeBlendWeights();
for (const auto& Attr : AttributeWeights)
{
    // Attr.Attribute 包含属性标识，Attr.Weight 是权重
}

// 转换为引擎标准 UBlendProfile 对象
UBlendProfile* EngineBlendProfile = NewObject<UBlendProfile>(GetTransientPackage());
BlendProfile.ConstructBlendProfile(EngineBlendProfile);
```

### 进阶用法：配置动画节点参数

```cpp
// 在自定义动画节点或 AnimInstance 中配置 BlendProfileLayeredBlend 节点
FAnimNode_BlendProfileLayeredBlend BlendNode;
BlendNode.BlendProfileAsset = MyBlendProfileStandaloneAsset;
BlendNode.BlendWeight = 0.7f;
BlendNode.RotationBlendSpace = EBlendProfileRotationBlendSpace::RootSpace;
BlendNode.bCustomCurveBlending = true;
BlendNode.CurveBlendingOption = ECurveBlendOption::NormalizeByCombinedWeight;
BlendNode.bBlendRootMotionBasedOnRootBone = true;
```

## Demo 示例

以下示例展示如何在 C++ 中创建一个混合配置文件并查询权重数据：

```cpp
// BlendProfileExample.h
#pragma once

#include "CoreMinimal.h"
#include "BlendProfileStandalone.h"
#include "HierarchyTableBlendProfile.h"

class FBlendProfileExample
{
public:
    /** 从骨架创建混合配置并查询骨骼权重 */
    static void QueryBlendProfile(USkeleton* Skeleton)
    {
        if (!Skeleton)
        {
            return;
        }

        // 创建基于层级表的混合配置文件
        FHierarchyTableBlendProfile Profile(Skeleton, EBlendProfileMode::WeightFactor);

        // 验证骨骼索引有效性
        const int32 BoneCount = Profile.GetNumBlendEntries();
        UE_LOG(LogTemp, Log, TEXT("Blend profile has %d entries"), BoneCount);

        // 遍历所有骨骼权重
        for (int32 BoneIdx = 0; BoneIdx < BoneCount; ++BoneIdx)
        {
            if (Profile.IsValidBoneIndex(BoneIdx))
            {
                const float Scale = Profile.GetBoneBlendScale(BoneIdx);
                UE_LOG(LogTemp, Log, TEXT("Bone %d: BlendScale = %.2f"), BoneIdx, Scale);
            }
        }

        // 查询曲线权重
        const auto& Curves = Profile.GetCurveBlendWeights();
        UE_LOG(LogTemp, Log, TEXT("Curve weights count: %d"), Curves.Num());

        // 查询属性权重
        const auto& Attributes = Profile.GetAttributeBlendWeights();
        UE_LOG(LogTemp, Log, TEXT("Attribute weights count: %d"), Attributes.Num());
    }

    /** 创建独立混合配置资产 */
    static UBlendProfileStandalone* CreateStandaloneProfile(USkeleton* Skeleton)
    {
        UBlendProfileStandalone* Profile = NewObject<UBlendProfileStandalone>(
            GetTransientPackage(), FName("DemoBlendProfile"));
        Profile->Type = EBlendProfileStandaloneType::WeightFactor;

#if WITH_EDITOR
        // 更新层级结构和缓存数据
        Profile->UpdateHierarchy();
        Profile->UpdateCachedData();
#endif

        return Profile;
    }
};
```

## 模块依赖

从 `.uplugin` 声明的插件依赖及源码推断：

| 模块 | 用途 |
|---|---|
| `HierarchyTable` | 提供通用层级表数据结构，本插件在此基础上扩展动画类型定义 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

> **注意**：本插件通过 `.uplugin` 的 `Plugins` 字段声明对 `HierarchyTable` 插件的硬依赖，启用本插件前需确保 `HierarchyTable` 已启用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `711fdc2f` | Add root space support to profile blend | 为混合配置添加根骨骼空间旋转混合支持 |
| 2026-03-04 | `d9a06590` | Update UAF blend profiles | 更新动画混合配置文件 |
| 2025-10-20 | `beb220c7` | Fix loaded blend profile assets not updating the hierarchy when its skeleton's hierarchy has changed | 修复骨架层级变更后已加载混合配置资产不更新的问题 |
| 2025-10-09 | `71d54d3d` | Fix profile blend node crash due to cached data not being generated in some cases | 修复混合节点因缓存数据未生成导致的崩溃 |
| 2025-10-07 | `96352708` | Renaming Base<Plugin>.ini to Default<Plugin>.ini | 配置文件命名规范化 |

### 维护评价

- **创建时间**：2024-11-21，从 `HierarchyTableBuiltin` 重命名而来（commit `0838d5b`）
- **更新频率**：活跃维护中，2025-2026 年持续有功能增强和 bug 修复
- **活跃度**：最近一次更新（2026-05-12）距离现在较近，仍在积极开发
- **状态**：实验性插件（`IsExperimentalVersion=true`，`EnabledByDefault=false`），API 可能发生变化
- **已知问题**：2025-10 修复了两个稳定性问题（缓存数据缺失崩溃、骨架层级变更不更新），表明该阶段仍在打磨中

**推荐使用**：✅ 适合实验性项目或需要精细骨骼混合控制的场景。作为实验性插件，生产环境使用前需充分测试，关注后续 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/HierarchyTableAnimation)
- [HierarchyTable 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HierarchyTable)（上游依赖）
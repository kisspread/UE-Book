# Groom

> Rendering and simulation of grooms

| 属性 | 值 |
|---|---|
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、纹理、蓝图资产） |
| 模块 | `HairCardGeneratorFramework` (Runtime), `HairStrandsCore` (Runtime), `HairStrandsDataflow` (Runtime), `HairStrandsDeformer` (Runtime), `HairStrandsEditor` (Runtime), `HairStrandsRuntime` (Runtime), `HairStrandsSolver` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-08-02 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands) | |

## 用途

HairStrands（Groom）插件是 UE5 中完整的毛发/头发渲染与模拟系统。它解决的核心问题是：**如何在实时渲染中高效地呈现数万到数十万根头发曲线，并使其随角色骨骼动画正确变形**。

该插件提供三种几何体表示方式来适应不同 LOD 需求：
- **Strands（发丝）**：逐根渲染的高精度曲线，适用于近景特写
- **Cards（发片）**：将多根发丝烘焙到带纹理的卡片网格上，适用于中距离
- **Meshes（网格）**：将整体发型烘焙为单一网格，适用于远景

核心能力包括：
- 从 Alembic/USD 等格式导入毛发资产（GroomAsset）
- 将毛发绑定到骨骼网格体（GroomBindingAsset），实现蒙皮跟随
- 支持 GroomCache 动画缓存，用于预烘焙的毛发动画
- 通过 RBF（径向基函数）插值实现高质量的发丝-引导线插值
- 与 Niagara 粒子系统集成，支持基于速度场/压力场的物理模拟
- 与 Sequencer 集成，支持在时间轴上控制毛发动画播放
- 支持光线追踪阴影、稳定光栅化、场景光照散射等高级渲染特性

**为什么需要手动启用**：该插件 `EnabledByDefault=false`，因为毛发渲染对 GPU 性能有显著影响，且需要特定的资产工作流，不适合所有项目默认开启。

## 使用场景

- 你在制作写实角色，需要高质量的头发/毛发渲染 → 启用 HairStrands 插件，导入 Groom 资产
- 你需要头发随角色骨骼动画正确变形 → 使用 GroomBindingAsset 将毛发绑定到骨骼网格体
- 你有预烘焙的毛发动画（如从 Houdini 导出）→ 使用 GroomCache 导入动画数据
- 你需要在不同距离下优化毛发性能 → 配置 LOD 设置，在 Strands/Cards/Meshes 之间切换
- 你需要毛发与风场、碰撞等物理交互 → 结合 Niagara 的 VelocityGrid/PressureGrid 数据接口
- 你需要在 Sequencer 中精确控制毛发动画时间线 → 使用 MovieSceneGroomCacheTrack

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateNewGroomBindingAsset` | 创建毛发绑定资产（自动生成包名） | `UGroomBlueprintLibrary` |
| `CreateNewGroomBindingAssetWithPath` | 在指定路径创建毛发绑定资产 | `UGroomBlueprintLibrary` |
| `CreateNewGeometryCacheGroomBindingAsset` | 创建绑定到 GeometryCache 的毛发绑定资产 | `UGroomBlueprintLibrary` |
| `CreateNewGeometryCacheGroomBindingAssetWithPath` | 在指定路径创建绑定到 GeometryCache 的毛发绑定资产 | `UGroomBlueprintLibrary` |
| `IsHairStrandsSupportedInWorld` | 检查当前世界是否支持毛发渲染 | `UGroomBlueprintLibrary` |

### 使用示例

**创建毛发绑定资产（蓝图描述）**：

1. 获取对 `GroomAsset` 和 `SkeletalMesh` 的引用
2. 调用 `CreateNewGroomBindingAsset` 节点
3. 将 `GroomAsset` 引脚连接到你的毛发资产
4. 将 `InSkeletalMesh` 引脚连接到目标骨骼网格体
5. `InNumInterpolationPoints` 默认 100，值越大绑定质量越高但构建越慢
6. 返回的 `UGroomBindingAsset` 可设置到 `UGroomComponent` 的 Binding 属性

**检查毛发支持（蓝图描述）**：

1. 调用 `IsHairStrandsSupportedInWorld` 节点
2. 将 `WorldContextObject` 连接到任意 Actor 或 self
3. 返回 `true` 表示当前渲染设置支持毛发（需要开启 `r.HairStrands` 相关控制台变量）

## C++ 用法

### 头文件引入

```cpp
#include "HairStrandsCore.h"
#include "GroomBlueprintLibrary.h"
#include "GroomBuilder.h"
#include "GroomBindingBuilder.h"
#include "GroomAsset.h"
#include "GroomBindingAsset.h"
```

### 基本用法：创建毛发绑定资产

从 `GroomBlueprintLibrary.h` 提取的 API 用法：

```cpp
#include "HairStrandsCore.h"
#include "GroomAsset.h"
#include "GroomBindingAsset.h"
#include "GroomBindingBuilder.h"

// 创建毛发绑定资产，将 Groom 绑定到骨骼网格体
void CreateBindingExample(UGroomAsset* GroomAsset, USkeletalMesh* TargetMesh)
{
    // 方法一：通过模块静态函数（编辑器环境）
    UGroomBindingAsset* BindingAsset = FHairStrandsCore::CreateGroomBindingAsset(
        EGroomBindingMeshType::SkeletalMesh,  // 绑定类型
        GroomAsset,                            // 毛发资产
        nullptr,                               // 源网格（nullptr 表示使用目标网格的静止姿态）
        TargetMesh,                            // 目标骨骼网格体
        100,                                   // RBF 插值采样点数
        0                                      // 匹配的 Section 索引
    );

    // 方法二：指定包路径
    UGroomBindingAsset* BindingAsset2 = FHairStrandsCore::CreateGroomBindingAsset(
        EGroomBindingMeshType::SkeletalMesh,
        TEXT("/Game/MyGroom/MyBinding"),        // 包路径
        GroomAsset->GetOuter(),                // 父包
        GroomAsset,
        nullptr,
        TargetMesh,
        100,
        0
    );
}
```

### 基本用法：构建毛发数据

从 `GroomBuilder.h` 提取的构建流程：

```cpp
#include "GroomBuilder.h"
#include "HairDescription.h"
#include "HairStrandsDatas.h"

// 毛发数据构建流程（编辑器/导入时使用）
void BuildGroomDataExample(const FHairDescription& HairDescription)
{
    // 步骤 1：从 HairDescription 构建分组描述
    FHairDescriptionGroups DescriptionGroups;
    FGroomBuilder::BuildHairDescriptionGroups(HairDescription, DescriptionGroups);

    // 步骤 2：从分组描述构建发丝数据和引导线数据
    for (int32 GroupIndex = 0; GroupIndex < DescriptionGroups.Groups.Num(); ++GroupIndex)
    {
        const FHairDescriptionGroup& Group = DescriptionGroups.Groups[GroupIndex];
        FHairGroupsInterpolation InterpolationSettings; // 使用默认设置

        FHairGroupInfo GroupInfo;
        FHairStrandsDatas StrandsData;
        FHairStrandsDatas GuidesData;

        FGroomBuilder::BuildData(
            Group,
            InterpolationSettings,
            GroupInfo,
            StrandsData,
            GuidesData
        );

        // 步骤 3：构建运行时 BulkData
        FHairStrandsBulkData StrandsBulkData;
        FGroomBuilder::BuildBulkData(GroupInfo, StrandsData, StrandsBulkData, true);
    }
}
```

### 进阶用法：GroomCache 流式加载

从 `GroomCacheStreamingManager.h` 和 `GroomCache.h` 提取：

```cpp
#include "GroomCacheStreamingManager.h"
#include "GroomCache.h"
#include "GroomComponent.h"

// 注册组件到流式管理器并获取动画数据
void StreamGroomCacheExample(UGroomComponent* GroomComp, UGroomCache* GroomCache)
{
    // 获取流式管理器单例
    IGroomCacheStreamingManager& StreamingManager = IGroomCacheStreamingManager::Get();

    // 注册组件（自动预取数据）
    StreamingManager.RegisterComponent(GroomComp);

    // 手动预取（例如 seek 后）
    StreamingManager.PrefetchData(GroomComp);

    // 映射动画数据（获取 CPU 端数据指针）
    const FGroomCacheAnimationData* AnimData = 
        StreamingManager.MapAnimationData(GroomCache, /*ChunkIndex=*/0);

    if (AnimData)
    {
        // 使用动画数据...
        
        // 用完后必须释放
        StreamingManager.UnmapAnimationData(GroomCache, 0);
    }

    // 清理时注销
    StreamingManager.UnregisterComponent(GroomComp);
}
```

### 进阶用法：构建绑定数据（底层 API）

从 `GroomBindingBuilder.h` 提取：

```cpp
#include "GroomBindingBuilder.h"
#include "GroomBindingAsset.h"

// 使用底层构建器创建绑定数据
void BuildBindingDirectly(UGroomAsset* Groom, USkeletalMesh* TargetMesh)
{
    // 创建绑定资产
    UGroomBindingAsset* BindingAsset = NewObject<UGroomBindingAsset>();

    // 准备输入参数
    FGroomBindingBuilder::FInput Input;
    Input.BindingType = EGroomBindingMeshType::SkeletalMesh;
    Input.NumInterpolationPoints = 100;
    Input.MatchingSection = 0;
    Input.GroomAsset = Groom;
    Input.TargetSkeletalMesh = TargetMesh;
    Input.SourceMeshLOD = 0;
    Input.TargetMeshMinLOD = 0;
    Input.bHasValidTarget = true;

    // 为每个毛发组构建绑定数据
    for (uint32 GroupIndex = 0; GroupIndex < Groom->GetNumHairGroups(); ++GroupIndex)
    {
        UGroomBindingAsset::FHairGroupPlatformData PlatformData;
        FGroomBindingBuilder::BuildBinding(Input, GroupIndex, nullptr, PlatformData);
        // 将 PlatformData 存入 BindingAsset...
    }
}
```

## Demo 示例

以下是一个最小可编译示例，展示如何在 C++ 中创建毛发绑定资产并将其应用到 GroomComponent：

```cpp
// MyGroomHelper.h
#pragma once

#include "CoreMinimal.h"

class UGroomAsset;
class USkeletalMesh;
class UGroomBindingAsset;
class UGroomComponent;

class FMyGroomHelper
{
public:
    /** 创建毛发绑定并应用到组件 */
    static UGroomBindingAsset* CreateAndApplyBinding(
        UGroomAsset* GroomAsset,
        USkeletalMesh* TargetSkeletalMesh,
        UGroomComponent* GroomComponent,
        int32 NumInterpolationPoints = 100);
};
```

```cpp
// MyGroomHelper.cpp
#include "MyGroomHelper.h"
#include "HairStrandsCore.h"
#include "GroomAsset.h"
#include "GroomBindingAsset.h"
#include "GroomComponent.h"
#include "GroomBindingBuilder.h"

UGroomBindingAsset* FMyGroomHelper::CreateAndApplyBinding(
    UGroomAsset* GroomAsset,
    USkeletalMesh* TargetSkeletalMesh,
    UGroomComponent* GroomComponent,
    int32 NumInterpolationPoints)
{
    if (!GroomAsset || !TargetSkeletalMesh)
    {
        UE_LOG(LogTemp, Warning, TEXT("CreateAndApplyBinding: Invalid GroomAsset or TargetSkeletalMesh"));
        return nullptr;
    }

    // 通过 HairStrandsCore 模块创建绑定资产
    UGroomBindingAsset* BindingAsset = FHairStrandsCore::CreateGroomBindingAsset(
        EGroomBindingMeshType::SkeletalMesh,
        GroomAsset,
        nullptr,           // Source mesh（使用目标网格的静止姿态）
        TargetSkeletalMesh,
        NumInterpolationPoints,
        0                  // Matching section
    );

    if (BindingAsset && GroomComponent)
    {
        // 将绑定资产应用到 GroomComponent
        GroomComponent->SetGroomBinding(BindingAsset);
    }

    return BindingAsset;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Niagara` | Niagara 粒子系统集成（VelocityGrid/PressureGrid 数据接口） |
| `MovieScene` | Sequencer 时间轴集成（GroomCache 动画轨道） |
| `GeometryCache` | 支持将毛发绑定到 GeometryCache 资产 |
| `Chaos` | GroomCache 实现 IChaosCacheData 接口 |
| `Dataflow` | Dataflow 图编辑器集成 |
| `MeshDescription` | HairDescription 底层数据结构依赖 |

## 维护状态

### 近期更新

```
- 0cb144950255 Added logging to catch null bone buffer from groom skin cache system and log information about it.
- a7f4750c98b0 Fix dataflow crash when the binding asset is changed while dataflow editor is opened #rb Charles.deRousiers #jira UE-351290
- 3acf88a0a189 Fix haircards causing crash during vulkan pso precompile
```

三条 commit 均为 Bug 修复：修复骨骼缓存空指针、Dataflow 编辑器崩溃、Vulkan PSO 预编译崩溃。

### 维护评价

- **创建时间**：2019 年 8 月，已有约 6 年历史
- **维护状态**：**活跃维护中**。近期 commit 集中在稳定性修复，说明 Epic 持续关注该插件的可靠性
- **代码规模**：390 个源文件，属于超大型插件，涵盖渲染、模拟、编辑器工具、Niagara 集成等多个子系统
- **已知限制**：
  - `EnabledByDefault=false`，需要手动在项目设置中启用
  - 毛发渲染对 GPU 性能有显著影响，需要合理配置 LOD
  - 高质量插值数据构建可能需要数十分钟
  - 部分功能标记为实验性（如 Procedural Cards Source Type）
- **推荐程度**：**推荐使用**。这是 UE5 官方的毛发渲染解决方案，功能完整且持续维护。对于需要写实毛发效果的项目（如角色展示、影视级渲染），这是首选方案。对于性能敏感的项目，建议充分利用 Cards/Meshes LOD 优化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands)
- 官方文档：无（.uplugin 中 DocsURL 为空）
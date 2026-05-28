# MetaHuman Creator

> MetaHuman Character Asset Creator and Editor.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 角色创建器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、纹理图表资产） |
| 模块 | `MetaHumanCharacter` (Runtime), `MetaHumanCharacterEditor` (Runtime), `MetaHumanCharacterMigrationEditor` (Runtime), `MetaHumanCharacterPalette` (Runtime), `MetaHumanCharacterPaletteEditor` (Runtime), `MetaHumanDefaultEditorPipeline` (Runtime), `MetaHumanDefaultPipeline` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter) | |

## 用途

本插件是 UE5 中 MetaHuman 角色的**资产创建与编辑管线**系统。它解决的核心问题是：如何将 MetaHuman Creator 生成的高精度数字人数据（面部、身体、毛发、服装）转换为可在游戏引擎中使用的优化资产。

具体而言，本插件（以 `MetaHumanDefaultEditorPipeline` 模块为核心）负责：

1. **角色组装**：将面部网格、身体网格、毛发（Groom）、服装组合为完整的 MetaHuman 角色
2. **材质烘焙**：通过 Texture Graph 系统将高分辨率材质参数烘焙为优化纹理，支持虚拟纹理（Virtual Texture）输出
3. **LOD 管理**：配置各组件的 LOD 级别、LOD 设置覆盖，以及仅烘焙 LOD 相关法线
4. **骨骼优化**：移除未使用权重的冗余骨骼，减少运行时计算开销
5. **RigLogic 解包**：将 RigLogic 的 RBF Solver 和 Swing/Twist 数据解包为标准 UE 动画资产（PoseAsset、AnimSequence、ControlRig）
6. **几何体裁剪**：通过 Hidden Face Map 纹理移除或缩小被服装遮挡的头部/身体几何体，防止穿模
7. **UEFN 导出**：支持将 MetaHuman 资产导出到 Unreal Editor for Fortnite 项目
8. **预烘焙毛发优化**：将多个短毛发 Groom 预烘焙为两张纹理，减少皮肤材质的纹理采样器数量

插件默认关闭（`EnabledByDefault=false`），当前处于 Beta 状态。

## 使用场景

- 你在使用 MetaHuman Creator（云端）创建了数字人角色，需要在 UE5 编辑器中**生成可打包的角色蓝图** → 使用本插件的 Build Collection 功能
- 你需要为 MetaHuman 角色配置**材质烘焙参数**（纹理分辨率、材质图表、输出文件夹）→ 使用 `UMetaHumanMaterialBakingSettings` 资产
- 你的 MetaHuman 角色穿着服装，需要**裁剪被遮挡的身体几何体**防止穿模 → 配置 `HeadHiddenFaceMapTexture` / `BodyHiddenFaceMapTexture`
- 你需要将 MetaHuman 导出到 **Fortnite Creative (UEFN)** 项目 → 使用 `UMetaHumanDefaultEditorPipelineUEFN` 管线
- 你需要将 MetaHuman 的 **RigLogic 动画数据解包**为标准动画资产以提升运行时性能 → 配置 `FMetaHumanBodyProperties.bUnpackRigLogic`
- 你在开发大型项目需要**优化骨骼数量**减少 GPU 开销 → 启用 `bOptimizeBoneCounts` 选项

## 蓝图用法

本模块主要通过编辑器资产配置驱动，直接暴露到蓝图的函数较少。以下是可用的蓝图接口：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BakeTangentNormals` | 将骨骼网格的法线烘焙为纹理（BlueprintImplementableEvent，需子类实现） | `ULODBakingUtility` |
| `GetTextureCategories` | 获取可用的纹理分类列表，用于纹理烘焙设置面板的选项 | `UMetaHumanMaterialBakingSettings` |
| `GetScalableNormalsTypeOptions` | 获取可缩放法线类型的可用选项列表 | `UMetaHumanDefaultEditorPipelineBase` |

### 编辑器预览 Actor 接口

`AMetaHumanDefaultEditorPipelineActor` 实现了 `IMetaHumanCharacterEditorActorInterface`，在编辑器中提供角色预览：

| 方法 | 说明 |
|---|---|
| `InitializeMetaHumanCharacterEditorActor` | 初始化预览 Actor，传入 MetaHuman 实例、角色资产、面部/身体网格和 LOD 映射 |
| `SetHairVisibilityState` | 控制毛发（头发、眉毛、胡须等）的显示/隐藏状态 |
| `SetClothingVisibilityState` | 控制服装的显示/隐藏状态，支持材质覆盖（如用半透明材质预览身体轮廓） |

### 配置属性（EditAnywhere）

以下是最常用的可配置属性，通过编辑器细节面板设置：

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `FaceLODs` | `TArray<int32>` | 要导出的面部 LOD 级别（为空则导出全部） | `FMetaHumanLODProperties` |
| `BodyLODs` | `TArray<int32>` | 要导出的身体 LOD 级别（为空则导出全部） | `FMetaHumanLODProperties` |
| `bOptimizeBoneCounts` | `bool` | 是否移除未使用权重的骨骼（默认开启） | `UMetaHumanDefaultEditorPipelineBase` |
| `bUnpackRigLogic` | `bool` | 是否将 RigLogic 解包为标准动画资产 | `FMetaHumanBodyProperties` |
| `bUsePreBakedGrooms` | `bool` | 是否预烘焙多毛发为两张纹理以优化采样器 | `FMetaHumanHairProperties` |
| `FollicleMapResolution` | `EMetaHumanBuildTextureResolution` | 毛囊图分辨率（256~8192） | `FMetaHumanHairProperties` |
| `UefnProjectFilePath` | `FFilePath` | UEFN 项目路径 | `UMetaHumanDefaultEditorPipelineUEFN` |

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanDefaultEditorPipelineBase.h"
#include "MetaHumanDefaultEditorPipelineActor.h"
#include "MetaHumanDefaultEditorPipelineUEFN.h"
#include "Item/MetaHumanOutfitEditorPipeline.h"
#include "Item/MetaHumanGroomEditorPipeline.h"
#include "Item/MetaHumanSkeletalMeshEditorPipeline.h"
```

### 基本用法 — 材质烘焙设置

材质烘焙通过 `UMetaHumanMaterialBakingSettings` 数据资产配置，指定 Texture Graph 和输出材质的映射关系。

```cpp
// 创建材质烘焙设置资产
UMetaHumanMaterialBakingSettings* BakingSettings = NewObject<UMetaHumanMaterialBakingSettings>();

// 添加纹理分类（用于面板分组显示）
BakingSettings->TextureCategories.Add(FName("Diffuse"));
BakingSettings->TextureCategories.Add(FName("Normal"));
BakingSettings->TextureCategories.Add(FName("Roughness"));

// 配置纹理图表输出
FMetaHumanTextureGraphOutputProperties TextureGraphProps;
TextureGraphProps.TextureGraphInstance = MyTextureGraphInstance; // 设置纹理图表实例
TextureGraphProps.InputValues.Add(FName("RoughnessMultiplier"), 1.0f);

// 配置输出纹理
FMetaHumanOutputTextureProperties OutputTexture;
OutputTexture.Category = FName("Diffuse");
OutputTexture.OutputTextureNameInGraph = FName("DiffuseOutput");
OutputTexture.OutputTextureFolder = TEXT("Characters/Textures");
OutputTexture.OutputTextureName = FName("T_MH_Diffuse");
OutputTexture.OutputMaterialSlotNames.Add(FName("Face"));
OutputTexture.OutputMaterialParameterName = FName("BaseColor");
OutputTexture.UsedInLODs = {0, 1, 2}; // 仅在 LOD 0-2 使用

TextureGraphProps.OutputTextures.Add(OutputTexture);
BakingSettings->TextureGraphs.Add(TextureGraphProps);
```

### 基本用法 — 服装隐藏面图

防止服装与头部/身体几何体穿模，通过 Hidden Face Map 控制被遮挡区域的处理方式。

```cpp
// 在服装管线中配置隐藏面图
UMetaHumanOutfitEditorPipeline* OutfitPipeline = NewObject<UMetaHumanOutfitEditorPipeline>();

// 设置头部隐藏面图（用于移除或缩小被帽子遮挡的头部几何体）
// 纹理的 RGB 通道中最高值决定处理方式
OutfitPipeline->HeadHiddenFaceMapTexture.Texture = MyHeadHiddenFaceMap;
OutfitPipeline->HeadHiddenFaceMapTexture.ShrinkThreshold = 0.5f; // 半透明区域缩小
OutfitPipeline->HeadHiddenFaceMapTexture.RemoveThreshold = 1.0f; // 完全遮挡区域移除

// 同样配置身体隐藏面图
OutfitPipeline->BodyHiddenFaceMapTexture.Texture = MyBodyHiddenFaceMap;
```

### 进阶用法 — RigLogic 解包配置

将 MetaHuman 身体的 RigLogic 数据解包为标准 UE 动画资产，提升运行时性能。

```cpp
// 配置身体属性以解包 RigLogic
FMetaHumanBodyProperties BodyProps;
BodyProps.bUnpackRigLogic = true;
BodyProps.PostProcessAnimBp = TSoftClassPtr<UAnimInstance>(
    FSoftObjectPath("/Game/Characters/ABP_MH_PostProcess"));

// RigLogic 解包细节
BodyProps.BodyRigLogicUnpackProperties.bUnpackRbfToPoseAssets = true;
BodyProps.BodyRigLogicUnpackProperties.bUnpackFingerHalfRotationsToControlRig = true;
BodyProps.BodyRigLogicUnpackProperties.bUnpackSwingTwistToControlRig = true;
BodyProps.BodyRigLogicUnpackProperties.ControlRig = MyControlRigBlueprint; // 可选：指定 ControlRig 蓝图
```

### 进阶用法 — 自定义编辑器管线

继承 `UMetaHumanDefaultEditorPipelineBase` 实现自定义管线：

```cpp
// Source/MetaHumanDefaultEditorPipeline/Public/MetaHumanDefaultEditorPipelineBase.h
// 基类定义了完整的管线框架，子类主要覆写以下方法：

UCLASS(EditInlineNew)
class UMyCustomPipeline : public UMetaHumanDefaultEditorPipelineBase
{
    GENERATED_BODY()

public:
    // 构造函数中配置管线规格
    UMyCustomPipeline();

    // 生成角色蓝图
    virtual UBlueprint* WriteActorBlueprint(
        const FWriteBlueprintSettings& InWriteBlueprintSettings) const override;

    // 更新已有蓝图
    virtual bool UpdateActorBlueprint(
        const UMetaHumanInstance* InCharacterInstance,
        UBlueprint* InBlueprint) const override;

    // 生成骨架资产（处理插件内置 vs 用户自定义骨架的逻辑）
    virtual TNotNull<USkeleton*> GenerateSkeleton(
        FMetaHumanCharacterGeneratedAssets& InGeneratedAssets,
        TNotNull<USkeleton*> InBaseSkeleton,
        const FString& InTargetFolderName,
        TNotNull<UObject*> InOuterForGeneratedAssets) const override;
};
```

## Demo 示例

以下展示如何自定义一个 MetaHuman 编辑器管线：

```cpp
// MyCustomMetaHumanPipeline.h
#pragma once

#include "MetaHumanDefaultEditorPipeline.h"
#include "MyCustomMetaHumanPipeline.generated.h"

UCLASS(EditInlineNew)
class MYMODULE_API UMyCustomMetaHumanPipeline : public UMetaHumanDefaultEditorPipeline
{
    GENERATED_BODY()

public:
    UMyCustomMetaHumanPipeline();

    virtual UBlueprint* WriteActorBlueprint(
        const FWriteBlueprintSettings& InWriteBlueprintSettings) const override;

    virtual bool UpdateActorBlueprint(
        const UMetaHumanInstance* InCharacterInstance,
        UBlueprint* InBlueprint) const override;
};
```

```cpp
// MyCustomMetaHumanPipeline.cpp
#include "MyCustomMetaHumanPipeline.h"
#include "MetaHumanInstance.h"
#include "Engine/Blueprint.h"

UMyCustomMetaHumanPipeline::UMyCustomMetaHumanPipeline()
{
    // 配置默认的面部/身体骨架
    FaceSkeleton = TSoftObjectPtr<USkeleton>(
        FSoftObjectPath("/MetaHuman/Common/Face/Face_Skeleton"));
    BodySkeleton = TSoftObjectPtr<USkeleton>(
        FSoftObjectPath("/MetaHuman/Common/Body/Body_Skeleton"));

    // 启用骨骼优化
    bOptimizeBoneCounts = true;
}

UBlueprint* UMyCustomMetaHumanPipeline::WriteActorBlueprint(
    const FWriteBlueprintSettings& InWriteBlueprintSettings) const
{
    // 自定义蓝图生成逻辑
    // 可以调用基类实现作为起点
    return Super::WriteActorBlueprint(InWriteBlueprintSettings);
}

bool UMyCustomMetaHumanPipeline::UpdateActorBlueprint(
    const UMetaHumanInstance* InCharacterInstance,
    UBlueprint* InBlueprint) const
{
    // 自定义蓝图更新逻辑
    // 例如：添加自定义组件、修改材质参数等
    if (!Super::UpdateActorBlueprint(InCharacterInstance, InBlueprint))
    {
        return false;
    }

    // 在此处添加自定义更新逻辑
    // ...

    return true;
}
```

## 模块依赖

从源码头文件中引用的类型推断，使用本模块需要以下依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanCharacter` | MetaHuman 角色核心数据类型（`UMetaHumanCharacter`、`UMetaHumanInstance`） |
| `MetaHumanCharacterPalette` | 角色调色板/物品系统（`UMetaHumanCollection`、`UMetaHumanWardrobeItem`） |
| `MetaHumanCharacterPaletteEditor` | 编辑器管线基类（`UMetaHumanCollectionEditorPipeline`） |
| `MetaHumanCharacterEditor` | 编辑器 Actor 基类和构建接口 |
| `TextureGraph` | 纹理图表执行引擎（`UTextureGraphInstance`） |
| `GeometryScript` | 几何体脚本工具（法线烘焙调试） |
| `ControlRig` | RigLogic 解包目标（`UControlRigBlueprint`） |
| `HairStrands` / `Groom` | 毛发组件（`UGroomComponent`） |
| `ChaosCloth` | 布料模拟组件（`UChaosClothComponent`） |
| `Dataflow` | 数据流资产（服装调整用 `UDataflow`） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `95d906ba` | [UEMHC] Checking for Asset Registry filter validity before using it | 使用前检查资产注册表过滤器有效性 |
| 2026-05-26 | `7f10fbf1` | [MetaHuman] Titan v9.0.8 | Titan 引擎版本更新至 v9.0.8 |
| 2026-05-26 | `efb27122` | [UEMHC] Duplicate face/body DNA when duplicating archetype skel meshes | 复制原型骨骼网格时同步复制面部/身体 DNA |
| 2026-05-26 | `909bc538` | [MHC] Use safer weak pointers for captured objects in MHC preview delegates | 预览委托中使用更安全的弱指针捕获对象 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | Titan 引擎版本更新至 v9.0.7 |

### 维护评价

- **活跃维护**：最近一次更新在 2026-05-26，距今不到 2 个月，且同一天有多次功能性提交
- **持续迭代**：Titan 引擎版本从 v9.0.7 快速迭代到 v9.0.8，说明核心依赖在频繁更新
- **代码质量改善**：近期提交涉及安全修复（弱指针）、健壮性改进（过滤器验证）、功能完善（DNA 复制）
- **Beta 状态**：`IsBetaVersion=true`，API 可能在后续版本中发生变化
- **默认关闭**：`EnabledByDefault=false`，需手动在插件管理器中启用
- **推荐使用**：适用于需要在引擎内构建和编辑 MetaHuman 角色的项目。作为 Beta 插件，建议关注后续版本的 API 变更，不建议在生产环境的关键路径中深度耦合

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter/Tests)
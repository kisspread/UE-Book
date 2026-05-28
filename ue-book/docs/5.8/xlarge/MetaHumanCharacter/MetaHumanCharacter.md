# MetaHuman Creator

> MetaHuman Character Asset Creator and Editor.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 角色编辑器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（角色资产、调色板、默认管线） |
| 模块 | `MetaHumanCharacter` (Runtime), `MetaHumanCharacterEditor` (Runtime), `MetaHumanCharacterMigrationEditor` (Runtime), `MetaHumanCharacterPalette` (Runtime), `MetaHumanCharacterPaletteEditor` (Runtime), `MetaHumanDefaultEditorPipeline` (Runtime), `MetaHumanDefaultPipeline` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter) | |

## 用途

MetaHuman Character 插件提供了一套完整的 MetaHuman 角色资产创建与编辑管线。它是 Unreal Engine 中 MetaHuman 系统的核心运行时模块，负责：

1. **角色资产数据容器**：`UMetaHumanCharacter` 是所有 MetaHuman 角色数据的中心容器，序列化并存储面部 DNA、身体 DNA、面部/身体状态数据、合成纹理等全部构建所需的资产信息。
2. **外观参数化系统**：通过结构化的参数体系（皮肤色调、眼睛虹膜/瞳孔/角膜/巩膜、化妆、牙齿、睫毛等）提供精细的角色外观自定义能力。
3. **纹理合成管线**：管理面部和身体纹理的合成、存储、异步加载和分辨率控制，支持从 2K 到 8K 的多级分辨率。
4. **目标网格适配**：支持将 MetaHuman 角色适配到外部目标网格（Target Mesh），包含关键点追踪和曲线追踪结果。
5. **衣橱与调色板系统**：管理角色的衣橱路径和资源分类，与 `UMetaHumanCollection` 内部调色板协作完成构建。

该插件之所以存在，是因为 MetaHuman 角色需要一种标准化的方式来序列化极其复杂的多层角色数据（DNA、状态、纹理、外观参数），并在编辑器和运行时之间一致地传递这些数据。

**注意**：此插件默认未启用（`EnabledByDefault: false`），且标记为 Beta 版本，需要手动在项目设置中启用。

## 使用场景

- 你在开发需要高保真数字人类的游戏或影视项目 → 使用 MetaHuman Character 创建和管理角色资产
- 你需要从 MetaHuman Creator 云端服务下载角色数据并在引擎中持久化 → 用 `UMetaHumanCharacter` 存储 DNA 和合成纹理
- 你需要调整角色的皮肤色调、眼睛颜色、化妆效果等外观参数 → 通过 `FMetaHumanCharacterSkinSettings`、`FMetaHumanCharacterEyesSettings`、`FMetaHumanCharacterMakeupSettings` 等结构体
- 你需要将 MetaHuman 适配到自定义身体网格 → 使用 Target Mesh 系统和关键点追踪
- 你需要为角色配置不同的构建管线（Cinematic / Optimized / UEFN）→ 通过 `FMetaHumanCharacterAssemblySettings`
- 你需要控制角色纹理的下载分辨率 → 通过 `FMetaHumanCharacterTextureSourceResolutions`

## 蓝图用法

本模块的大部分核心结构体都标记为 `BlueprintType`，属性标记为 `BlueprintReadWrite`，可以直接在蓝图中操作。`UMetaHumanCharacter` 的核心 DNA/纹理管理方法为 C++ API，蓝图中主要通过属性读写来配置角色参数。

### 核心数据结构

所有外观参数结构体均可在蓝图中实例化和编辑：

| 结构体 | 说明 | 关键属性 |
|---|---|---|
| `FMetaHumanCharacterFaceEvaluationSettings` | 面部评估设置 | `GlobalDelta`、`HighFrequencyDelta`、`HeadScale` |
| `FMetaHumanCharacterEyesSettings` | 眼睛设置（左右眼） | `EyeLeft`、`EyeRight`（各含 Iris/Pupil/Cornea/Sclera） |
| `FMetaHumanCharacterSkinSettings` | 皮肤设置 | `Skin`（色调）、`Freckles`（雀斑）、`Accents`（区域强调）、纹理覆盖 |
| `FMetaHumanCharacterMakeupSettings` | 化妆设置 | `Foundation`（粉底）、`Eyes`（眼妆）、`Blush`（腮红）、`Lips`（唇妆） |
| `FMetaHumanCharacterTeethProperties` | 牙齿设置 | 牙齿形状、颜色、牙龈颜色等 |
| `FMetaHumanCharacterEyelashesProperties` | 睫毛设置 | 类型、染色颜色、粗糙度等 |
| `FMetaHumanCharacterViewportSettings` | 视口设置 | 环境光、LOD、相机帧、渲染质量 |
| `FMetaHumanCharacterAssemblySettings` | 组装/构建设置 | 管线类型、质量级别、输出目录 |

### 使用示例（蓝图描述）

**修改角色皮肤色调**：
1. 获取 `UMetaHumanCharacter` 资产引用
2. 读取其 `SkinSettings` 属性
3. 修改 `SkinSettings.Skin.U` 和 `SkinSettings.Skin.V`（色调 UV 坐标）
4. 写回 `SkinSettings` 属性

**配置眼睛外观**：
1. 获取 `UMetaHumanCharacter` 资产引用
2. 读取 `EyesSettings.EyeLeft.Iris`
3. 设置 `IrisPattern`（虹膜图案）、`PrimaryColorU`/`PrimaryColorV`（主色色调）
4. 设置 `LimbalRingSize`、`LimbalRingColor` 等细节参数
5. 写回 `EyesSettings`

**调整化妆效果**：
1. 获取 `UMetaHumanCharacter` 资产引用
2. 读取 `MakeupSettings`
3. 设置 `Foundation.bApplyFoundation = true`，调整 `Foundation.Color` 和 `Foundation.Intensity`
4. 设置 `Eyes.Type` 为眼妆类型（如 `EMetaHumanCharacterEyeMakeupType::CatEye`）
5. 写回 `MakeupSettings`

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCharacter.h"
#include "MetaHumanCharacterSkin.h"
#include "MetaHumanCharacterEyes.h"
#include "MetaHumanCharacterMakeup.h"
#include "MetaHumanCharacterTeeth.h"
#include "MetaHumanCharacterViewport.h"
#include "MetaHumanCharacterAssemblySettings.h"
#include "MetaHumanCharacterGeneratedAssets.h"
```

### 基本用法

以下代码展示了 `UMetaHumanCharacter` 的核心数据存取 API：

```cpp
// 获取一个已有的 MetaHuman Character 资产
UMetaHumanCharacter* Character = LoadObject<UMetaHumanCharacter>(nullptr, TEXT("/Game/MyMetaHumans/MyCharacter.MyCharacter"));
if (!Character || !Character->IsCharacterValid())
{
    UE_LOG(LogMetaHumanCharacter, Error, TEXT("Character is not valid. Initialize it via UMetaHumanCharacterEditorSubsystem."));
    return;
}

// ---- 读取面部 DNA ----
if (Character->HasFaceDNA())
{
    TArray<uint8> FaceDNABuffer = Character->GetFaceDNABuffer();
    bool bHasBlendshapes = Character->HasFaceDNABlendshapes();
    // 使用 DNA buffer 进行后续处理...
}

// ---- 存储面部 DNA ----
TArray<uint8> NewFaceDNA = /* 从外部获取 DNA 数据 */;
Character->SetFaceDNABuffer(NewFaceDNA, /*bInHasFaceDNABlendshapes=*/ true);

// ---- 读取身体 DNA ----
if (Character->HasBodyDNA())
{
    TArray<uint8> BodyDNABuffer = Character->GetBodyDNABuffer();
    // 处理身体 DNA...
}

// ---- 管理合成纹理 ----
if (Character->HasSynthesizedTextures())
{
    // 获取面部纹理分辨率
    FInt32Point AlbedoRes = Character->GetSynthesizedFaceTexturesResolution(EFaceTextureType::Albedo);
    UE_LOG(LogMetaHumanCharacter, Log, TEXT("Face Albedo resolution: %dx%d"), AlbedoRes.X, AlbedoRes.Y);

    // 异步加载面部纹理数据
    TFuture<FSharedBuffer> FutureData = Character->GetSynthesizedFaceTextureDataAsync(EFaceTextureType::Albedo);
    FutureData.Then([](TFuture<FSharedBuffer> Result)
    {
        FSharedBuffer TextureData = Result.Get();
        // 处理纹理数据...
    });
}
```

### 进阶用法

以下示例展示更复杂的角色外观配置和纹理管理：

```cpp
// ---- 配置角色完整外观 ----
void ConfigureCharacterAppearance(UMetaHumanCharacter* Character)
{
    // 1. 调整面部评估参数
    Character->FaceEvaluationSettings.GlobalDelta = 0.8f;
    Character->FaceEvaluationSettings.HighFrequencyDelta = 0.6f;
    Character->FaceEvaluationSettings.HeadScale = 1.1f;

    // 2. 配置眼睛外观
    FMetaHumanCharacterEyesSettings& EyesSettings = Character->EyesSettings;

    // 左眼虹膜
    EyesSettings.EyeLeft.Iris.IrisPattern = EMetaHumanCharacterEyesIrisPattern::Iris003;
    EyesSettings.EyeLeft.Iris.PrimaryColorU = 0.7f;  // 棕色调
    EyesSettings.EyeLeft.Iris.PrimaryColorV = 0.3f;
    EyesSettings.EyeLeft.Iris.LimbalRingSize = 0.75f;
    EyesSettings.EyeLeft.Iris.LimbalRingColor = FLinearColor(0.1f, 0.1f, 0.1f);

    // 左眼巩膜
    EyesSettings.EyeLeft.Sclera.bUseCustomTint = true;
    EyesSettings.EyeLeft.Sclera.Tint = FLinearColor(0.95f, 0.9f, 0.85f);
    EyesSettings.EyeLeft.Sclera.VascularityIntensity = 1.2f;

    // 右眼镜像左眼（实际使用中可做细微差异）
    EyesSettings.EyeRight = EyesSettings.EyeLeft;

    // 3. 配置皮肤
    FMetaHumanCharacterSkinSettings& SkinSettings = Character->SkinSettings;
    SkinSettings.Skin.U = 0.6f;  // 暖色调
    SkinSettings.Skin.V = 0.4f;
    SkinSettings.Skin.Roughness = 1.0f;
    SkinSettings.Freckles.Mask = EMetaHumanCharacterFrecklesMask::Type2;
    SkinSettings.Freckles.Density = 0.3f;
    SkinSettings.Freckles.Strength = 0.4f;

    // 区域强调
    SkinSettings.Accents.Cheeks.Redness = 0.7f;
    SkinSettings.Accents.Cheeks.Saturation = 0.5f;

    // 4. 配置化妆
    FMetaHumanCharacterMakeupSettings& MakeupSettings = Character->MakeupSettings;
    MakeupSettings.Foundation.bApplyFoundation = true;
    MakeupSettings.Foundation.Color = FLinearColor(0.9f, 0.8f, 0.7f);
    MakeupSettings.Foundation.Intensity = 0.6f;
    MakeupSettings.Eyes.Type = EMetaHumanCharacterEyeMakeupType::CatEye;
    MakeupSettings.Eyes.PrimaryColor = FLinearColor(0.15f, 0.02f, 0.01f);
    MakeupSettings.Lips.Type = EMetaHumanCharacterLipsMakeupType::Natural;
    MakeupSettings.Lips.Color = FLinearColor(0.6f, 0.15f, 0.1f);

    // 5. 配置牙齿
    Character->HeadModelSettings.Teeth.ToothLength = 0.2f;
    Character->HeadModelSettings.Teeth.TeethColor = FLinearColor(0.95f, 0.95f, 0.9f);

    // 6. 配置睫毛
    Character->HeadModelSettings.Eyelashes.Type = EMetaHumanCharacterEyelashesType::LongSlightCurl;
    Character->HeadModelSettings.Eyelashes.Melanin = 0.5f;
    Character->HeadModelSettings.Eyelashes.bEnableGrooms = true;

    // 7. 设置高分辨率纹理
    SkinSettings.DesiredTextureSourcesResolutions.SetAllResolutionsTo(ERequestTextureResolution::Res4k);

    // 8. 配置视口预览
    Character->ViewportSettings.CharacterEnvironment = EMetaHumanCharacterEnvironment::Studio;
    Character->ViewportSettings.LevelOfDetail = EMetaHumanCharacterLOD::LOD0;
    Character->ViewportSettings.CameraFrame = EMetaHumanCharacterCameraFrame::Face;
}

// ---- 存储合成纹理到角色 ----
void StoreSynthesizedTexture(UMetaHumanCharacter* Character, EFaceTextureType TextureType, const FImage& ImageData)
{
    Character->StoreSynthesizedFaceTexture(TextureType, ImageData);

    FInt32Point Resolution = Character->GetSynthesizedFaceTexturesResolution(TextureType);
    UE_LOG(LogMetaHumanCharacter, Log, TEXT("Stored face texture %d, resolution: %dx%d"),
        (int32)TextureType, Resolution.X, Resolution.Y);
}

// ---- 管理纹理覆盖 ----
void ApplyTextureOverrides(UMetaHumanCharacter* Character)
{
    FMetaHumanCharacterSkinSettings& SkinSettings = Character->SkinSettings;

    // 启用纹理覆盖
    SkinSettings.TextureMaterialOverrides.bEnableTextureOverrides = true;

    // 设置自定义纹理引用
    UTexture2D* CustomAlbedo = LoadObject<UTexture2D>(nullptr, TEXT("/Game/Textures/CustomFaceAlbedo"));
    if (CustomAlbedo)
    {
        SkinSettings.TextureMaterialOverrides.TextureOverrides.Face.Add(
            EFaceTextureType::Albedo, CustomAlbedo);
    }

    // 获取最终纹理集（含覆盖）
    FMetaHumanCharacterSkinTextureSet BaseTextures; // 从其他来源获取
    FMetaHumanCharacterSkinTextureSet FinalTextures = SkinSettings.GetFinalSkinTextureSet(BaseTextures);
}

// ---- 使用 Target Mesh 系统 ----
void ConfigureTargetMesh(UMetaHumanCharacter* Character, UStaticMesh* BodyMesh, UStaticMesh* HeadMesh)
{
    FMetaHumanCharacterTargetMeshKey MeshKey;
    MeshKey.BodyMesh = BodyMesh;
    MeshKey.HeadMesh = HeadMesh;

    // 设置目标关键点
    FMetaHumanCharacterTargetKeyPoints KeyPoints;
    KeyPoints.CharacterBodyVertexIndexes.Add(TEXT("LeftShoulder"), 1234);
    KeyPoints.CharacterHeadVertexIndexes.Add(TEXT("NoseTip"), 567);
    KeyPoints.TargetBodyPositions.Add(TEXT("LeftShoulder"), FVector3f(10.0f, 5.0f, 150.0f));
    KeyPoints.TargetHeadPositions.Add(TEXT("NoseTip"), FVector3f(0.0f, 12.0f, 80.0f));

    Character->TargetMeshKeyPointsCollection.PerMeshTargetKeyPoints.Add(MeshKey, KeyPoints);
    Character->LastTargetMeshKey = MeshKey;
}
```

### 隐藏面移除（Geometry Removal）

```cpp
#include "MetaHumanGeometryRemovalTypes.h"

// 配置隐藏面移除设置
UE::MetaHuman::GeometryRemoval::FHiddenFaceMapSettings Settings;
Settings.MaxCullValue = 0.1f;      // 低于此值的三角形被移除
Settings.MinKeepValue = 0.9f;      // 高于此值的三角形保留
Settings.MaxShrinkDistance = 0.5f; // 中间区域的顶点收缩距离

// 使用纹理应用隐藏面移除
UE::MetaHuman::GeometryRemoval::FHiddenFaceMapTexture HiddenFaceMap;
HiddenFaceMap.Texture = LoadObject<UTexture2D>(nullptr, TEXT("/Game/Textures/HiddenFaceMask"));
HiddenFaceMap.Settings = Settings;
```

### 生成资产清单

```cpp
#include "MetaHumanCharacterGeneratedAssets.h"

// 构建后的生成资产清单
FMetaHumanCharacterGeneratedAssets GeneratedAssets;
if (GeneratedAssets.FaceMesh)
{
    UE_LOG(LogMetaHumanCharacter, Log, TEXT("Generated face mesh: %s"), *GeneratedAssets.FaceMesh->GetName());
}
if (GeneratedAssets.BodyMesh)
{
    UE_LOG(LogMetaHumanCharacter, Log, TEXT("Generated body mesh: %s"), *GeneratedAssets.BodyMesh->GetName());
}

// 遍历生成的纹理
for (const auto& Pair : GeneratedAssets.SynthesizedFaceTextures)
{
    UE_LOG(LogMetaHumanCharacter, Log, TEXT("Face texture type %d: %s"),
        (int32)Pair.Key, *Pair.Value->GetName());
}

// 移除某个资产的元数据
GeneratedAssets.RemoveAssetMetadata(GeneratedAssets.FaceMesh);
```

## Demo 示例

以下是一个完整的最小示例，展示如何创建一个 MetaHuman Character 资产并配置其外观：

```cpp
// MyMetaHumanCharacterHelper.h
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanCharacter.h"
#include "MetaHumanCharacterSkin.h"
#include "MetaHumanCharacterEyes.h"
#include "MetaHumanCharacterMakeup.h"

class FMyMetaHumanCharacterHelper
{
public:
    /** 创建并配置一个新的 MetaHuman 角色 */
    static UMetaHumanCharacter* CreateConfiguredCharacter(UObject* InOuter, const FString& InName);

    /** 打印角色当前外观配置摘要 */
    static void PrintCharacterSummary(const UMetaHumanCharacter* Character);
};
```

```cpp
// MyMetaHumanCharacterHelper.cpp
#include "MyMetaHumanCharacterHelper.h"
#include "MetaHumanCharacterViewport.h"
#include "MetaHumanCharacterTeeth.h"
#include "MetaHumanCharacterLog.h"

UMetaHumanCharacter* FMyMetaHumanCharacterHelper::CreateConfiguredCharacter(
    UObject* InOuter, const FString& InName)
{
    // 创建角色资产
    UMetaHumanCharacter* Character = NewObject<UMetaHumanCharacter>(
        InOuter, UMetaHumanCharacter::StaticClass(), FName(*InName));
    if (!Character)
    {
        UE_LOG(LogMetaHumanCharacter, Error, TEXT("Failed to create character"));
        return nullptr;
    }

    // 配置皮肤色调（深色皮肤）
    Character->SkinSettings.Skin.U = 0.75f;
    Character->SkinSettings.Skin.V = 0.25f;
    Character->SkinSettings.Skin.Roughness = 1.0f;

    // 配置雀斑
    Character->SkinSettings.Freckles.Mask = EMetaHumanCharacterFrecklesMask::Type1;
    Character->SkinSettings.Freckles.Density = 0.3f;

    // 配置眼睛 — 蓝绿色虹膜
    FMetaHumanCharacterEyeIrisProperties& LeftIris = Character->EyesSettings.EyeLeft.Iris;
    LeftIris.IrisPattern = EMetaHumanCharacterEyesIrisPattern::Iris005;
    LeftIris.PrimaryColorU = 0.4f;
    LeftIris.PrimaryColorV = 0.8f;
    LeftIris.ColorBlend = 0.6f;
    LeftIris.GlobalSaturation = 2.5f;

    // 右眼使用相同设置
    Character->EyesSettings.EyeRight.Iris = LeftIris;

    // 配置睫毛
    Character->HeadModelSettings.Eyelashes.Type = EMetaHumanCharacterEyelashesType::LongCurl;
    Character->HeadModelSettings.Eyelashes.Melanin = 0.6f;
    Character->HeadModelSettings.Eyelashes.bEnableGrooms = true;

    // 配置牙齿
    Character->HeadModelSettings.Teeth.ToothLength = 0.1f;
    Character->HeadModelSettings.Teeth.WornDown = 0.05f;

    // 配置化妆
    Character->MakeupSettings.Foundation.bApplyFoundation = false;
    Character->MakeupSettings.Lips.Type = EMetaHumanCharacterLipsMakeupType::Natural;
    Character->MakeupSettings.Lips.Color = FLinearColor(0.55f, 0.12f, 0.08f);
    Character->MakeupSettings.Lips.Opacity = 0.8f;

    // 配置视口
    Character->ViewportSettings.CharacterEnvironment = EMetaHumanCharacterEnvironment::Studio;
    Character->ViewportSettings.LevelOfDetail = EMetaHumanCharacterLOD::LOD0;
    Character->ViewportSettings.CameraFrame = EMetaHumanCharacterCameraFrame::Face;

    // 设置纹理分辨率
    Character->SkinSettings.DesiredTextureSourcesResolutions.SetAllResolutionsTo(
        ERequestTextureResolution::Res2k);

    UE_LOG(LogMetaHumanCharacter, Log, TEXT("Created character: %s"), *InName);
    return Character;
}

void FMyMetaHumanCharacterHelper::PrintCharacterSummary(const UMetaHumanCharacter* Character)
{
    if (!Character)
    {
        return;
    }

    UE_LOG(LogMetaHumanCharacter, Log, TEXT("=== Character Summary ==="));
    UE_LOG(LogMetaHumanCharacter, Log, TEXT("Template Type: %d"), (int32)Character->TemplateType);
    UE_LOG(LogMetaHumanCharacter, Log, TEXT("Has Face DNA: %s"), Character->HasFaceDNA() ? TEXT("Yes") : TEXT("No"));
    UE_LOG(LogMetaHumanCharacter, Log, TEXT("Has Body DNA: %s"), Character->HasBodyDNA() ? TEXT("Yes") : TEXT("No"));
    UE_LOG(LogMetaHumanCharacter, Log, TEXT("Has Synthesized Textures: %s"),
        Character->HasSynthesizedTextures() ? TEXT("Yes") : TEXT("No"));
    UE_LOG(LogMetaHumanCharacter, Log, TEXT("Has High-Res Textures: %s"),
        Character->HasHighResolutionTextures() ? TEXT("Yes") : TEXT("No"));

    // 皮肤信息
    const auto& Skin = Character->SkinSettings.Skin;
    UE_LOG(LogMetaHumanCharacter, Log, TEXT("Skin UV: (%.2f, %.2f), Roughness: %.2f"), Skin.U, Skin.V, Skin.Roughness);

    // 眼睛信息
    const auto& LeftIris = Character->EyesSettings.EyeLeft.Iris;
    UE_LOG(LogMetaHumanCharacter, Log, TEXT("Left Iris Pattern: %d, Color UV: (%.2f, %.2f)"),
        (int32)LeftIris.IrisPattern, LeftIris.PrimaryColorU, LeftIris.PrimaryColorV);

    // 化妆信息
    const auto& Makeup = Character->MakeupSettings;
    UE_LOG(LogMetaHumanCharacter, Log, TEXT("Foundation: %s, Eye Makeup: %d, Lip Type: %d"),
        Makeup.Foundation.bApplyFoundation ? TEXT("On") : TEXT("Off"),
        (int32)Makeup.Eyes.Type,
        (int32)Makeup.Lips.Type);
}
```

## 模块依赖

由于 Build.cs 的具体依赖列表未直接提供，以下基于源码头文件推断的独有依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | MetaHuman 核心运行时库（DNA 解析、基础数据类型） |
| `RigLogic` | RigLogic 绑定求解器，用于身体和面部动画驱动 |
| `Serialization` | UE 编辑器批量数据序列化（`FEditorBulkData`） |
| `ImageCore` / `ImageWrapper` | 图像数据处理和纹理合成 |
| `MeshConversion` | 网格数据转换（Body/Head mesh 适配） |

> 注：标准 Core/CoreUObject/Engine/Slate 等常见依赖已省略。实际依赖请查阅 `Source/MetaHumanCharacter/MetaHumanCharacter.Build.cs`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `95d906ba` | [UEMHC] Checking for Asset Registry filter validity before using it | 修复资产注册表过滤器使用前的合法性检查 |
| 2026-05-26 | `7f10fbf1` | [MetaHuman] Titan v9.0.8 | Titan 引擎升级到 v9.0.8 |
| 2026-05-26 | `efb27122` | [UEMHC] Duplicate face/body DNA when duplicating archetype skel meshes | 复制原型骨架网格时同步复制面部/身体 DNA |
| 2026-05-26 | `909bc538` | [MHC] Use safer weak pointers for captured objects in MHC preview delegates | 预览委托中改用更安全的弱指针避免悬垂引用 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | Titan 引擎升级到 v9.0.7 |

### 维护评价

- **活跃维护**：最近更新集中在 2026-05-26，当天有多次提交，涵盖 Bug 修复、安全改进和 Titan 引擎版本升级，表明该插件处于**高强度活跃开发**阶段。
- **Beta 状态**：插件标记为 `IsBetaVersion: true`，API 可能会发生变化。`FMetaHumanCharacterSkinSettings` 中已有多处 `UE_DEPRECATED(5.8, ...)` 标记，说明接口在快速迭代中。
- **创建时间**：2025-03-17 创建，约 1 年历史，相对较新。
- **模块规模**：394 个源文件，7 个子模块，属于大型插件。
- **建议**：该插件适合在 MetaHuman 相关项目中使用，但需注意 Beta 状态带来的 API 不稳定性。建议关注 Epic 的更新日志，及时适配废弃接口的迁移。对于生产环境，建议锁定特定引擎版本后再做深度集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter)
- [官方文档]()（暂无）
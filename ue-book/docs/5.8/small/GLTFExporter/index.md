# glTF Exporter

> An exporter for Khronos glTF 2.0.

| 属性 | 值 |
|---|---|
| 中文名 | glTF 导出器 |
| 分类 | Exporters |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质代理资产、材质代理蓝图资产） |
| 模块 | `GLTFExporter` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-07-19 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/GLTFExporter) | |

## 用途

GLTFExporter 是 UE5 内置的 glTF 2.0 格式导出插件，由 Epic Games 开发和维护。它解决了 **将 Unreal Engine 资产导出为国际通用 3D 交换格式** 的核心需求。

该插件将 UE 内部资产（静态网格、骨骼网格、材质、纹理、动画、灯光、摄像机、场景层级等）转换为符合 Khronos glTF 2.0 规范的 `.gltf`（JSON + 外部二进制/纹理文件）或 `.glb`（自包含二进制）文件。它支持多种 glTF 扩展，包括 PBR 材质的高级特性（ClearCoat、Sheen、Transmission、Iridescence、Anisotropy 等）、灯光（punctual lights、IES）、纹理变换、网格量化、材质变体等。

**为什么存在：** glTF 是当前 Web 和跨平台 3D 内容的行业标准格式。UE 内置该导出器，使得开发者可以将 UE 项目中的资产无缝导出到其他 DCC 工具、Web 应用、AR/VR 平台和 glTF 查看器中，无需依赖第三方插件。

## 使用场景

- 你需要将 UE 场景导出到 Web 端 3D 查看器（如 model-viewer、Babylon.js、Three.js）→ 用 GLTFExporter
- 你需要将 UE 中制作的资产传递给其他 DCC 工具（Blender、Maya）进行进一步编辑 → 用 GLTFExporter
- 你需要为 AR/VR 应用（WebXR、QuickLook、Scene Viewer）准备 3D 内容 → 用 GLTFExporter
- 你需要在运行时动态导出 3D 内容（如用户自定义模型分享）→ 用 GLTFExporter（Runtime 模块支持运行时调用）
- 你需要导出带动画的角色到 glTF 格式 → 用 GLTFExporter（支持骨骼动画和 Morph Targets）
- 你需要导出关卡序列动画 → 用 GLTFExporter（支持 Level Sequence 导出为 glTF 动画）

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExportToGLTF` | 将对象导出为 glTF/glb 文件，返回是否成功，输出导出消息 | `UGLTFExporter` |
| `ResetToDefault` (ExportOptions) | 将导出选项重置为默认值 | `UGLTFExportOptions` |
| `ResetToDefault` (ProxyOptions) | 将代理选项重置为默认值 | `UGLTFProxyOptions` |

### 导出选项（BlueprintReadWrite 属性）

`UGLTFExportOptions` 的主要可配置属性：

| 属性 | 类型 | 说明 |
|---|---|---|
| `ExportUniformScale` | float | 导出缩放因子（默认 0.01，厘米→米） |
| `bExportPreviewMesh` | bool | 是否导出独立动画/材质资产的预览网格 |
| `bExportProxyMaterials` | bool | 是否使用材质代理 |
| `bExportUnlitMaterials` | bool | 是否正确导出 Unlit 材质（KHR_materials_unlit） |
| `bExportClearCoatMaterials` | bool | 是否导出 ClearCoat 材质（KHR_materials_clearcoat） |
| `bExportClothMaterials` | bool | 是否导出布料材质（KHR_materials_sheen） |
| `bExportThinTranslucentMaterials` | bool | 是否导出薄半透明材质（KHR_materials_transmission） |
| `bExportSpecularGlossinessMaterials` | bool | 是否导出 SpecularGlossiness 材质 |
| `bExportEmissiveStrength` | bool | 是否支持超出标准范围的自发光强度 |
| `BakeMaterialInputs` | EGLTFMaterialBakeMode | 材质输入烘焙模式（Disabled/Simple/UseMeshData） |
| `DefaultMaterialBakeSize` | FGLTFMaterialBakeSize | 默认材质烘焙纹理尺寸 |
| `DefaultLevelOfDetail` | int32 | 默认导出 LOD 级别 |
| `bExportSourceModel` | bool | 是否导出源模型（vs 渲染数据） |
| `bExportVertexColors` | bool | 是否导出顶点颜色 |
| `bExportVertexSkinWeights` | bool | 是否导出骨骼蒙皮权重 |
| `bMakeSkinnedMeshesRoot` | bool | 是否将蒙皮网格设为根节点（严格遵循 glTF 规范） |
| `bUseMeshQuantization` | bool | 是否使用网格量化（KHR_mesh_quantization） |
| `bExportMorphTargets` | bool | 是否导出 Morph Targets |
| `bExportLevelSequences` | bool | 是否导出关卡序列 |
| `bExportAnimationSequences` | bool | 是否导出动画序列 |
| `TextureImageFormat` | EGLTFTextureImageFormat | 纹理导出格式（None/PNG/JPEG） |
| `TextureImageQuality` | int32 | JPEG 压缩质量（1-100） |
| `bExportTextureTransforms` | bool | 是否导出 UV 变换（KHR_texture_transform） |
| `bExportLightmaps` | bool | 是否导出光照贴图（EPIC_lightmap_textures） |
| `bAdjustNormalmaps` | bool | 是否翻转法线贴图绿色通道（UE→glTF 约定） |
| `bExportHiddenInGame` | bool | 是否导出游戏中隐藏的 Actor |
| `bExportLights` | bool | 是否导出灯光（KHR_lights_punctual + EXT_lights_ies） |
| `bExportCameras` | bool | 是否导出摄像机 |
| `ExportMaterialVariants` | EGLTFMaterialVariantMode | 材质变体导出模式 |

### 导出消息结构

```cpp
// FGLTFExportMessages 包含三个消息数组
Suggestions  // 建议信息
Warnings     // 警告信息
Errors       // 错误信息
```

### 使用示例（蓝图描述）

**基本场景导出：**
1. 创建一个 `ExportToGLTF` 节点
2. `Object` 引脚：连接要导出的 World 引用（或留空导出当前关卡）
3. `FilePath` 引脚：设置保存路径，如 `"C:/Export/MyScene.glb"`（.glb 为自包含二进制，.gltf 为 JSON+外部文件）
4. `Options` 引脚：连接一个 `UGLTFExportOptions` 实例（通过 "Make Literal GLTFExportOptions" 或从类默认对象获取），或留空使用项目默认设置
5. `SelectedActors` 引脚：如需只导出部分 Actor，通过 "Make Set" 节点构建 Actor 集合；留空则导出全部
6. `OutMessages` 引脚：输出变量，获取导出过程中的日志消息
7. 返回值 `bool`：导出是否成功

**材质/网格单独导出：**
- 将 `Object` 引脚连接到 `UStaticMesh`、`USkeletalMesh`、`UMaterialInterface`、`UAnimSequence` 或 `ULevelSequence` 引用，即可单独导出该资产为 glTF 文件

## C++ 用法

### 头文件引入

```cpp
#include "Exporters/GLTFExporter.h"
#include "Options/GLTFExportOptions.h"
```

### 基本用法

最简单的导出调用：

```cpp
// 导出当前世界为 .gltf 文件
// 来源：Source/GLTFExporter/Public/Exporters/GLTFExporter.h
bool bSuccess = UGLTFExporter::ExportToGLTF(
    nullptr,                    // Object（nullptr 表示当前活跃世界）
    TEXT("C:/Export/Scene.gltf"), // 输出文件路径
    nullptr,                    // Options（nullptr 使用项目默认设置）
    {}                          // SelectedActors（空集导出所有 Actor）
);
```

### 带选项的导出

```cpp
// 来源：Source/GLTFExporter/Public/Exporters/GLTFExporter.h
#include "Exporters/GLTFExporter.h"
#include "Options/GLTFExportOptions.h"

void ExportWithOptions()
{
    // 创建或获取导出选项
    UGLTFExportOptions* Options = GetMutableDefault<UGLTFExportOptions>();
    
    // 自定义导出选项
    Options->ExportUniformScale = 1.0f;           // 1:1 比例
    Options->TextureImageFormat = EGLTFTextureImageFormat::JPEG; // 使用 JPEG 压缩
    Options->TextureImageQuality = 85;             // JPEG 质量
    Options->bExportLights = true;                 // 导出灯光
    Options->bExportCameras = true;                // 导出摄像机
    Options->bExportAnimationSequences = true;     // 导出动画
    Options->bExportVertexSkinWeights = true;      // 导出蒙皮权重
    Options->bExportMorphTargets = true;           // 导出 Morph Targets
    Options->bExportLightmaps = true;              // 导出光照贴图
    
    // 只导出选中的 Actor
    TSet<AActor*> SelectedActors;
    // ... 填充选中的 Actor
    
    // 导出并获取消息
    FGLTFExportMessages Messages;
    bool bSuccess = UGLTFExporter::ExportToGLTF(
        nullptr,
        TEXT("C:/Export/Scene.glb"),  // .glb 格式（自包含二进制）
        Options,
        SelectedActors,
        Messages
    );
    
    // 处理消息
    for (const FString& Warning : Messages.Warnings)
    {
        UE_LOG(LogTemp, Warning, TEXT("GLTF Export Warning: %s"), *Warning);
    }
}
```

### 导出特定资产

```cpp
// 来源：Source/GLTFExporter/Public/Exporters/GLTFExporter.h
void ExportSpecificAssets()
{
    // 导出单个静态网格
    UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/MyMesh"));
    UGLTFExporter::ExportToGLTF(Mesh, TEXT("C:/Export/Mesh.glb"));
    
    // 导出单个骨骼网格
    USkeletalMesh* SkelMesh = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/Character"));
    UGLTFExporter::ExportToGLTF(SkelMesh, TEXT("C:/Export/Character.glb"));
    
    // 导出材质
    UMaterialInterface* Material = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/MyMaterial"));
    UGLTFExporter::ExportToGLTF(Material, TEXT("C:/Export/Material.gltf"));
    
    // 导出动画序列
    UAnimSequence* Anim = LoadObject<UAnimSequence>(nullptr, TEXT("/Game/IdleAnim"));
    UGLTFExporter::ExportToGLTF(Anim, TEXT("C:/Export/Idle.gltf"));
    
    // 导出关卡序列
    ULevelSequence* Seq = LoadObject<ULevelSequence>(nullptr, TEXT("/Game/Cutscene"));
    UGLTFExporter::ExportToGLTF(Seq, TEXT("C:/Export/Cutscene.gltf"));
}
```

### 坐标转换工具

```cpp
// 来源：Source/GLTFExporter/Public/Utilities/GLTFCoreUtilities.h
#include "Utilities/GLTFCoreUtilities.h"

// glTF 使用右手坐标系（Y 轴向上），UE 使用左手坐标系（Z 轴向上）
// FGLTFCoreUtilities 提供了各种坐标/数据转换函数

// 长度转换（默认从厘米到米，scale=0.01）
float Meters = FGLTFCoreUtilities::ConvertLength(100.0f); // 100cm → 1.0m

// 位置转换
FGLTFVector3 glTFPos = FGLTFCoreUtilities::ConvertPosition(FVector3f(100, 200, 300));

// 旋转转换
FGLTFQuaternion glTFQuat = FGLTFCoreUtilities::ConvertRotation(FQuat4f::Identity);

// 矩阵转换（带缩放）
FGLTFMatrix4 glTFMatrix = FGLTFCoreUtilities::ConvertTransform(FTransform3f::Identity);

// FOV 转换（度 → glTF 弧度）
float glTFFOV = FGLTFCoreUtilities::ConvertFieldOfView(90.0f, 16.0f / 9.0f);

// 材质着色模型转换
EGLTFJsonShadingModel Model = FGLTFCoreUtilities::ConvertShadingModel(EMaterialShadingModel::MSM_DefaultLit);

// Alpha 模式转换
EGLTFJsonAlphaMode Alpha = FGLTFCoreUtilities::ConvertAlphaMode(EBlendMode::BLEND_Translucent);
```

### 进阶用法：材质代理系统

```cpp
// 来源：Source/GLTFExporter/Public/Utilities/GLTFProxyMaterialUtilities.h
#include "Utilities/GLTFProxyMaterialUtilities.h"

// 材质代理允许为复杂材质指定简化的代理材质用于导出
void UseProxyMaterials()
{
    // 检查材质是否是代理材质
    UMaterial* Material = LoadObject<UMaterial>(nullptr, TEXT("/Game/MyProxyMat"));
    bool bIsProxy = FGLTFProxyMaterialUtilities::IsProxyMaterial(Material);
    
    // 获取或设置材质的代理
    UMaterialInterface* Original = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/ComplexMat"));
    UMaterialInterface* Proxy = FGLTFProxyMaterialUtilities::GetProxyMaterial(Original);
    
    // 获取材质参数值
    float MetallicValue;
    FHashedMaterialParameterInfo ParamInfo(FName("Metallic"));
    bool bFound = FGLTFProxyMaterialUtilities::GetParameterValue(Original, ParamInfo, MetallicValue);
}
```

### 材质用户数据覆盖

```cpp
// 来源：Source/GLTFExporter/Public/UserData/GLTFMaterialUserData.h
#include "UserData/GLTFMaterialUserData.h"

// 为材质资产添加 glTF 专用用户数据，覆盖导出设置
void ConfigureMaterialExport()
{
    UMaterial* Material = LoadObject<UMaterial>(nullptr, TEXT("/Game/MyMaterial"));
    
    // 添加 glTF 材质导出选项（作为 Asset User Data）
    UGLTFMaterialExportOptions* Options = NewObject<UGLTFMaterialExportOptions>(Material);
    Options->Proxy = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/MyProxyMat"));
    
    // 覆盖特定输入的烘焙设置
    FGLTFOverrideMaterialBakeSettings& NormalSettings = Options->Inputs.FindOrAdd(
        EGLTFMaterialPropertyGroup::Normal);
    NormalSettings.bOverrideSize = true;
    NormalSettings.Size.X = 2048;
    NormalSettings.Size.Y = 2048;
    NormalSettings.bOverrideFilter = true;
    NormalSettings.Filter = TextureFilter::TF_Trilinear;
    
    Material->AddAssetUserData(Options);
}
```

## Demo 示例

### 完整的 glTF 导出器类

**GLTFExportDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "GLTFExportDemo.generated.h"

UCLASS()
class UGLTFExportDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    /** 导出当前世界为 glb 文件 */
    UFUNCTION(BlueprintCallable, Category = "GLTF Demo")
    bool ExportCurrentWorld(const FString& FilePath);

    /** 导出指定 Actor 集合为 glb 文件 */
    UFUNCTION(BlueprintCallable, Category = "GLTF Demo")
    bool ExportActors(const FString& FilePath, const TArray<AActor*>& Actors);
};
```

**GLTFExportDemo.cpp**
```cpp
#include "GLTFExportDemo.h"
#include "Exporters/GLTFExporter.h"
#include "Options/GLTFExportOptions.h"
#include "Engine/World.h"

bool UGLTFExportDemoSubsystem::ExportCurrentWorld(const FString& FilePath)
{
    FGLTFExportMessages Messages;
    
    // 使用默认选项导出当前世界
    bool bSuccess = UGLTFExporter::ExportToGLTF(
        nullptr,           // 当前活跃世界
        FilePath,
        nullptr,           // 使用默认选项
        {},                // 导出所有 Actor
        Messages
    );
    
    // 输出日志
    for (const FString& Error : Messages.Errors)
    {
        UE_LOG(LogTemp, Error, TEXT("[GLTF] %s"), *Error);
    }
    for (const FString& Warning : Messages.Warnings)
    {
        UE_LOG(LogTemp, Warning, TEXT("[GLTF] %s"), *Warning);
    }
    
    return bSuccess;
}

bool UGLTFExportDemoSubsystem::ExportActors(const FString& FilePath, const TArray<AActor*>& Actors)
{
    // 创建自定义选项
    UGLTFExportOptions* Options = GetMutableDefault<UGLTFExportOptions>();
    Options->ExportUniformScale = 0.01f;
    Options->TextureImageFormat = EGLTFTextureImageFormat::PNG;
    Options->bExportVertexColors = false;
    Options->bExportCameras = true;
    Options->bExportLights = true;
    Options->bExportMorphTargets = true;
    
    // 构建选中 Actor 集合
    TSet<AActor*> SelectedActors;
    for (AActor* Actor : Actors)
    {
        if (IsValid(Actor))
        {
            SelectedActors.Add(Actor);
        }
    }
    
    FGLTFExportMessages Messages;
    bool bSuccess = UGLTFExporter::ExportToGLTF(
        GetWorld(),
        FilePath,
        Options,
        SelectedActors,
        Messages
    );
    
    return bSuccess;
}
```

## 模块依赖

从插件的代码分析，以下是使用者需要关注的非标准依赖：

| 模块 | 用途 |
|---|---|
| `MeshDescription` | 网格数据解析，用于 FMeshDescription 的三角形/顶点/多边形组处理 |
| `RenderCore` | 顶点缓冲区访问（FPositionVertexBuffer、FStaticMeshVertexBuffer、FSkinWeightVertexBuffer 等） |
| `Landscape` | 地形组件导出（ULandscapeComponent、ULandscapeLayerInfoObject） |
| `LevelSequence` | 关卡序列动画导出（ULevelSequence、ALevelSequenceActor） |
| `MovieScene` | MovieScene 框架支持，关卡序列依赖 |
| `VariantManagerContent` | 材质变体集导出（UVariant、UPropertyValue）——以插件依赖形式提供 |
| `Interchange` | 可选，Interchange-glTF 导入器的材质映射支持 |
| `InterchangeAssets` | Interchange 资产支持 |

无特殊依赖（仅标准 Core/Engine/Slate 等）：不适用，此插件有上述独特依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-20 | `4bd57e77` | Fixed crash when creating a GTLFMaterialProxy on a incomplete material | 修复在不完整材质上创建 glTF 材质代理时的崩溃 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移 UE_LOG 到 UE_LOGF 新日志宏 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理纹理属性修改代码，按要求包裹在 PreEditChange/PostEditChange 中 |
| 2026-03-03 | `373e8a9e` | Fixed build error of QA_ContentPipeline project introduced by CL 51336460 | 修复 QA_ContentPipeline 项目的编译错误 |

### 维护评价

- **活跃维护**：最近 6 个月内有实质性更新（bug 修复、代码质量改进），持续保持兼容性维护
- **创建时间**：2022 年 7 月，约 4 年历史，属于较新的 Enterprise 级插件
- **更新频率**：近期每 2-4 周有更新，主要集中在 bug 修复和编译器兼容性方面
- **成熟度**：功能完备，支持大量 glTF 扩展（KHR_lights_punctual、KHR_materials_clearcoat、KHR_materials_sheen、KHR_materials_transmission、KHR_materials_iridescence、KHR_materials_anisotropy、KHR_mesh_quantization、KHR_texture_transform、EPIC_lightmap_textures 等）
- **推荐使用**：✅ **强烈推荐**。作为 Epic 官方维护的企业级导出器，代码质量高，功能全面，积极维护，是 UE 项目导出 glTF 的首选方案。支持运行时调用（Runtime 模块），可用于服务器端或运行时导出场景。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/GLTFExporter)
- [官方文档](https://docs.unrealengine.com/en-US/working-with-media/supported-media/glTF-exporter/)（UE 官方 glTF 导出器文档）
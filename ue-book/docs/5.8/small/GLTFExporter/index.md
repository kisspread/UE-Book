# glTF Exporter

> An exporter for Khronos glTF 2.0.

| 属性 | 值 |
|---|---|
| 中文名 | glTF 导出器 |
| 分类 | Exporters |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质模板、代理材质等） |
| 模块 | `GLTFExporter` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-07-19 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/GLTFExporter) | |

## 用途

GLTFExporter 是 UE5 内置的 glTF 2.0 格式导出器，解决的是将 UE5 场景资产导出到行业标准 glTF 格式的问题。glTF（GL Transmission Format）是由 Khronos Group 制定的开放标准，被称为"3D 资产的 JPEG"，广泛用于 Web 3D、跨平台内容交换、AR/VR 应用等场景。

该插件的核心功能包括：
- **资产转换引擎**：将 UE 的静态网格、骨骼网格、材质、纹理、动画、灯光、相机等资产转换为 glTF JSON 结构和二进制缓冲区
- **材质代理系统**：将 UE 的复杂材质节点图转换为 glTF PBR 材质，支持烘焙复杂材质输入为纹理
- **坐标系统转换**：自动处理 UE（左手坐标系、厘米单位、Z 轴朝上）到 glTF（右手坐标系、米单位、Y 轴朝上）的转换
- **扩展支持**：通过 glTF 扩展（KHR_materials_clearcoat、KHR_lights_punctual 等）保留 UE 特有的材质效果和灯光信息
- **双向兼容**：与 Interchange-glTF 导入器配合，实现材质映射的导入-导出往返

## 使用场景

- 你需要将 UE 场景导出到 Web 浏览器中查看（WebGL/Three.js/Babylon.js）
- 你需要将 UE 制作的资产交换到 Blender、Maya 等其他 DCC 工具
- 你在开发 AR/VR 应用，需要将 UE 场景导入到 ARKit/ARCore/WebXR
- 你需要批量导出大量资产用于流水线处理
- 你需要将游戏资产转换为电商产品展示、建筑可视化等非游戏用途
- 你需要通过 Variant Manager 导出材质变体

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExportToGLTF` | 将对象导出为 .gltf 或 .glb 文件 | `UGLTFExporter` |
| `ResetToDefault` | 重置所有导出选项为默认值 | `UGLTFExportOptions` |
| `ResetToDefault` | 重置代理材质选项为默认值 | `UGLTFProxyOptions` |

### ExportToGLTF 参数说明

| 参数 | 类型 | 说明 |
|---|---|---|
| `Object` | `UObject*` | 导出对象，支持 `UWorld`、`UStaticMesh`、`USkeletalMesh`、`UMaterialInterface`、`UAnimSequence`、`ULevelSequence`、`ULevelVariantSets`。为空则导出当前活跃世界 |
| `FilePath` | `FString` | 输出文件路径。.gltf 生成 JSON + 外部二进制/纹理文件；.glb 生成自包含二进制文件 |
| `Options` | `UGLTFExportOptions*` | 导出选项。为空则使用项目用户级编辑器设置 |
| `SelectedActors` | `TSet<AActor*>` | 仅当 Object 为 UWorld 时有效。为空集则导出所有 Actor |
| `OutMessages` | `FGLTFExportMessages&` | 输出的建议、警告、错误信息 |
| 返回值 | `bool` | 是否成功导出 |

### 导出选项（UGLTFExportOptions）

所有选项均可在蓝图中读写，按类别分组：

**通用设置：**
- `ExportUniformScale`（float）：统一缩放因子，默认 0.01（厘米→米转换）
- `bExportPreviewMesh`（bool）：是否导出独立动画/材质资产的预览网格
- `bSkipNearDefaultValues`（bool）：跳过接近默认值的浮点属性以减小 JSON 体积
- `bIncludeCopyrightNotice`（bool）：是否包含项目设置中的版权声明

**材质设置：**
- `bExportProxyMaterials`：使用材质用户数据中定义的代理材质
- `bUseImporterMaterialMapping`：使用 Interchange-glTF 导入器的材质映射
- `bExportUnlitMaterials`：导出 Unlit 材质（KHR_materials_unlit）
- `bExportClearCoatMaterials`：导出 Clear Coat 材质（KHR_materials_clearcoat）
- `bExportClothMaterials`：导出 Cloth 材质（KHR_materials_sheen）
- `bExportThinTranslucentMaterials`：导出薄半透明材质（KHR_materials_transmission）
- `bExportSpecularGlossinessMaterials`：导出 Specular-Glossiness 工作流
- `bExportEmissiveStrength`：允许自发光强度超过标准范围（KHR_materials_emissive_strength）
- `BakeMaterialInputs`：材质输入烘焙模式（Disabled/Simple/UseMeshData）

**网格设置：**
- `DefaultLevelOfDetail`：默认 LOD 级别
- `bExportSourceModel`：导出源模型而非渲染数据
- `bExportVertexColors`：导出顶点颜色（不推荐，glTF 中顶点颜色总是乘以基础颜色）
- `bExportVertexSkinWeights`：导出骨骼蒙皮权重
- `bMakeSkinnedMeshesRoot`：使骨骼网格成为根节点以符合 glTF 规范
- `bUseMeshQuantization`：使用顶点量化压缩（KHR_mesh_quantization）
- `bExportMorphTargets`：导出变形目标

**动画设置：**
- `bExportLevelSequences`：导出关卡序列（仅支持变换轨道）
- `bExportAnimationSequences`：导出骨骼网格组件使用的动画序列

**纹理设置：**
- `TextureImageFormat`：纹理输出格式（None/PNG/JPEG）
- `TextureImageQuality`：JPEG 压缩质量（1-100）
- `bExportTextureTransforms`：导出 UV 偏移和缩放（KHR_texture_transform）
- `bExportLightmaps`：导出光照贴图（EPIC_lightmap_textures）
- `bAdjustNormalmaps`：翻转法线贴图绿色通道以匹配 glTF 约定

**场景设置：**
- `bExportHiddenInGame`：导出标记为游戏内隐藏的 Actor
- `bExportLights`：导出灯光组件（KHR_lights_punctual + EXT_lights_ies）
- `bExportCameras`：导出相机组件

**变体设置：**
- `ExportMaterialVariants`：材质变体导出模式（None/Simple/UseMeshData）

### 使用示例（蓝图描述）

**导出当前世界为 GLB：**
1. 获取当前世界（Get World）→ 作为 Object
2. 设置文件路径字符串，如 `"/Game/Export/MyScene.glb"`
3. 创建 UGLTFExportOptions 对象，设置所需选项
4. 调用 `ExportToGLTF`，连接返回值检查是否成功
5. 检查 `OutMessages` 中的 Warnings 和 Errors

**导出选中 Actor 子集：**
1. 获取当前世界
2. 获取编辑器中选中的 Actor 集合（通过编辑器工具蓝图或 C++ 扩展）
3. 设置文件路径为 `.gltf` 格式（生成独立文件便于调试）
4. 调用 `ExportToGLTF`，传入 Actor 集合到 `SelectedActors`

**导出单个静态网格：**
1. 引用 UStaticMesh 资产
2. 设置文件路径
3. 可选：设置 `DefaultLevelOfDetail` 控制导出的 LOD 级别
4. 调用 `ExportToGLTF`

## C++ 用法

### 头文件引入

```cpp
#include "Exporters/GLTFExporter.h"
#include "Options/GLTFExportOptions.h"
#include "GLTFExporterModule.h"
```

### 基本用法

```cpp
// 最简单的导出调用 —— 导出整个世界为 GLB
// 来源：Source/GLTFExporter/Public/Exporters/GLTFExporter.h

UWorld* World = GEditor->GetEditorWorldContext().World();
FString FilePath = FPaths::ProjectSavedDir() / TEXT("Exports/MyScene.glb");

bool bSuccess = UGLTFExporter::ExportToGLTF(World, FilePath);
if (!bSuccess)
{
    UE_LOG(LogGLTFExporter, Error, TEXT("Failed to export glTF"));
}
```

### 带自定义选项的导出

```cpp
// 配置导出选项并导出
// 来源：Source/GLTFExporter/Public/Options/GLTFExportOptions.h, Exporters/GLTFExporter.h

UWorld* World = GEditor->GetEditorWorldContext().World();
FString FilePath = FPaths::ProjectSavedDir() / TEXT("Exports/CustomScene.gltf");

// 创建并配置导出选项
UGLTFExportOptions* Options = NewObject<UGLTFExportOptions>();
Options->ExportUniformScale = 1.0f;  // 使用原始比例（米）
Options->bExportLights = true;
Options->bExportCameras = true;
Options->bExportVertexSkinWeights = true;
Options->bExportAnimationSequences = true;
Options->bExportMorphTargets = true;
Options->TextureImageFormat = EGLTFTextureImageFormat::JPEG;
Options->TextureImageQuality = 85;
Options->bExportTextureTransforms = true;
Options->bExportLightmaps = true;
Options->bExportLevelSequences = true;
Options->bExportHiddenInGame = false;
Options->DefaultLevelOfDetail = 0;

// 带消息反馈的导出
FGLTFExportMessages Messages;
bool bSuccess = UGLTFExporter::ExportToGLTF(World, FilePath, Options, {}, Messages);

// 处理消息
for (const FString& Warning : Messages.Warnings)
{
    UE_LOG(LogGLTFExporter, Warning, TEXT("%s"), *Warning);
}
for (const FString& Error : Messages.Errors)
{
    UE_LOG(LogGLTFExporter, Error, TEXT("%s"), *Error);
}
```

### 导出选中的 Actor 子集

```cpp
// 只导出场景中的部分 Actor
// 来源：Source/GLTFExporter/Public/Exporters/GLTFExporter.h

UWorld* World = GEditor->GetEditorWorldContext().World();

TSet<AActor*> SelectedActors;
// 获取编辑器选中的 Actor
for (FSelectionIterator It(GEditor->GetSelectedActorIterator()); It; ++It)
{
    AActor* Actor = Cast<AActor>(*It);
    if (Actor)
    {
        SelectedActors.Add(Actor);
    }
}

FString FilePath = FPaths::ProjectSavedDir() / TEXT("Exports/SelectedActors.glb");
UGLTFExporter::ExportToGLTF(World, FilePath, nullptr, SelectedActors);
```

### 导出单个资产

```cpp
// 导出静态网格
UStaticMesh* StaticMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/MyMesh.MyMesh"));
UGLTFExporter::ExportToGLTF(StaticMesh, TEXT("/Exports/MyMesh.glb"));

// 导出骨骼网格
USkeletalMesh* SkelMesh = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/MyChar.MyChar"));
UGLTFExporter::ExportToGLTF(SkelMesh, TEXT("/Exports/MyChar.glb"));

// 导出材质
UMaterialInterface* Material = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/MyMat.MyMat"));
UGLTFExporter::ExportToGLTF(Material, TEXT("/Exports/MyMat.glb"));
```

### 使用坐标转换工具

```cpp
// 坐标系统转换示例
// 来源：Source/GLTFExporter/Public/Utilities/GLTFCoreUtilities.h

// UE 坐标位置（厘米）→ glTF 坐标位置（米，右手系）
FVector3f UEPosition(100.0f, 200.0f, 50.0f);
FGLTFVector3 GLTFPosition = FGLTFCoreUtilities::ConvertPosition(UEPosition);
// 内部处理：单位转换（×0.01）和 Y/Z 轴交换

// UE 法线 → glTF 法线
FVector3f UENormal(0.0f, 0.0f, 1.0f);
FGLTFVector3 GLTFNormal = FGLTFCoreUtilities::ConvertNormal(UENormal);

// UE 旋转 → glTF 四元数
FRot32f UERotator(0.0f, 90.0f, 0.0f);
FGLTFQuaternion GLTFQuat = FGLTFCoreUtilities::ConvertRotation(UERotator);

// UE FOV → glTF FOV（glTF 使用 Y 轴 FOV）
float YFOV = FGLTFCoreUtilities::ConvertFieldOfView(UEFOVDegrees, AspectRatio);

// UE 材质混合模式 → glTF Alpha 模式
EGLTFJsonAlphaMode AlphaMode = FGLTFCoreUtilities::ConvertAlphaMode(EBlendMode::BLEND_Translucent);
```

### 材质代理系统

```cpp
// 使用代理材质优化导出
// 来源：Source/GLTFExporter/Public/Utilities/GLTFProxyMaterialUtilities.h

// 检查材质是否为代理材质
bool bIsProxy = FGLTFProxyMaterialUtilities::IsProxyMaterial(MyMaterial);

// 获取代理材质
UMaterialInterface* Proxy = FGLTFProxyMaterialUtilities::GetProxyMaterial(OriginalMaterial);
if (Proxy)
{
    // 代理材质存在，导出器将使用它
}

// 创建代理材质实例（编辑器中）
UMaterialInstanceConstant* ProxyMat = FGLTFProxyMaterialUtilities::CreateProxyMaterial(
    EGLTFJsonShadingModel::Default,
    GetTransientPackage(),
    FName("MyProxyMaterial")
);

// 设置代理材质参数
FHashedMaterialParameterInfo ParamInfo(FName("BaseColor"));
FLinearColor Color(1.0f, 0.0f, 0.0f, 1.0f);
FGLTFProxyMaterialUtilities::SetParameterValue(ProxyMat, ParamInfo, Color);

// 获取材质烘焙尺寸设置
FGLTFMaterialBakeSize BakeSize = FGLTFMaterialExportOptions::GetBakeSizeForPropertyGroup(
    MyMaterial,
    EGLTFMaterialPropertyGroup::BaseColorOpacity,
    FGLTFMaterialBakeSize::Default
);
```

## Demo 示例

### 自定义导出器子类

```cpp
// MyGLTFExporter.h
#pragma once

#include "CoreMinimal.h"
#include "Exporters/GLTFExporter.h"
#include "Options/GLTFExportOptions.h"
#include "MyGLTFExporter.generated.h"

UCLASS()
class UMyGLTFExporter : public UObject
{
    GENERATED_BODY()

public:
    // 批量导出场景中的所有静态网格
    UFUNCTION(BlueprintCallable, Category = "MyGLTF")
    static bool ExportAllStaticMeshes(UWorld* World, const FString& OutputDirectory);

    // 导出单个材质为 glTF（含烘焙纹理）
    UFUNCTION(BlueprintCallable, Category = "MyGLTF")
    static bool ExportMaterial(UMaterialInterface* Material, const FString& FilePath);
};
```

```cpp
// MyGLTFExporter.cpp
#include "MyGLTFExporter.h"
#include "Engine/StaticMeshActor.h"
#include "Exporters/GLTFExporter.h"
#include "Options/GLTFExportOptions.h"
#include "GLTFExporterModule.h"

bool UMyGLTFExporter::ExportAllStaticMeshes(UWorld* World, const FString& OutputDirectory)
{
    if (!World)
    {
        UE_LOG(LogGLTFExporter, Error, TEXT("World is null"));
        return false;
    }

    // 收集所有静态网格 Actor
    TSet<AActor*> StaticMeshActors;
    for (TActorIterator<AStaticMeshActor> It(World); It; ++It)
    {
        AStaticMeshActor* SMActor = *It;
        if (SMActor && SMActor->GetStaticMeshComponent())
        {
            StaticMeshActors.Add(SMActor);
        }
    }

    if (StaticMeshActors.Num() == 0)
    {
        UE_LOG(LogGLTFExporter, Warning, TEXT("No static mesh actors found"));
        return true;
    }

    // 配置导出选项
    UGLTFExportOptions* Options = NewObject<UGLTFExportOptions>();
    Options->ExportUniformScale = 1.0f;
    Options->DefaultLevelOfDetail = 0;
    Options->bExportVertexColors = false;
    Options->bExportHiddenInGame = false;
    Options->TextureImageFormat = EGLTFTextureImageFormat::PNG;

    // 导出为 GLB 格式
    FString FilePath = FPaths::Combine(OutputDirectory, TEXT("StaticMeshes.glb"));
    FGLTFExportMessages Messages;
    bool bSuccess = UGLTFExporter::ExportToGLTF(World, FilePath, Options, StaticMeshActors, Messages);

    // 输出结果
    for (const FString& Suggestion : Messages.Suggestions)
    {
        UE_LOG(LogGLTFExporter, Log, TEXT("Suggestion: %s"), *Suggestion);
    }
    for (const FString& Warning : Messages.Warnings)
    {
        UE_LOG(LogGLTFExporter, Warning, TEXT("Warning: %s"), *Warning);
    }

    return bSuccess;
}

bool UMyGLTFExporter::ExportMaterial(UMaterialInterface* Material, const FString& FilePath)
{
    if (!Material)
    {
        UE_LOG(LogGLTFExporter, Error, TEXT("Material is null"));
        return false;
    }

    // 配置材质导出选项 —— 启用烘焙和所有材质扩展
    UGLTFExportOptions* Options = NewObject<UGLTFExportOptions>();
    Options->BakeMaterialInputs = EGLTFMaterialBakeMode::Simple;
    Options->DefaultMaterialBakeSize = FGLTFMaterialBakeSize{512, 512, true};
    Options->DefaultMaterialBakeFilter = TF_Bilinear;
    Options->DefaultMaterialBakeTiling = TA_Wrap;
    Options->bExportUnlitMaterials = true;
    Options->bExportClearCoatMaterials = true;
    Options->bExportClothMaterials = true;
    Options->bExportEmissiveStrength = true;
    Options->bExportTextureTransforms = true;
    Options->TextureImageFormat = EGLTFTextureImageFormat::PNG;
    Options->bExportPreviewMesh = true;

    FGLTFExportMessages Messages;
    return UGLTFExporter::ExportToGLTF(Material, FilePath, Options, {}, Messages);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VariantManagerContent` | 变体管理器内容资产（材质变体导出支持） |
| `Interchange` | Interchange 框架（可选，用于材质导入映射） |
| `InterchangeAssets` | Interchange 资产定义 |

无特殊依赖（仅标准 Core/Engine/Slate 等），项目内使用时不需要额外依赖声明。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-20 | `4bd57e77` | Fixed crash when creating a GTLFMaterialProxy on a incomplete material | 修复在不完整材质上创建代理材质时的崩溃问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志系统至 UE_LOGF 宏 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理纹理属性修改代码，正确使用编辑器回调 |
| 2026-03-03 | `373e8a9e` | Fixed build error of QA_ContentPipeline project introduced by CL 51336460 | 修复由先前改动引起的 QA 内容管线项目构建错误 |

### 维护评价

**积极维护中。** 该插件创建于 2022 年 7 月，至今约 4 年，属于较新的 Enterprise 级插件。从 git 历史看，2026 年持续有实质性更新：

- **活跃度高**：最近 3 个月内有多次修复和改进提交
- **维护质量好**：提交涵盖崩溃修复、编译警告清理、代码规范化等，表明维护团队认真负责
- **功能成熟**：支持大量 glTF 扩展（13 种 KHR/EXT 扩展），材质代理系统、动画、灯光、相机等导出功能完善
- **企业级支持**：由 Epic Games 官方维护，位于 Enterprise 插件目录

**注意事项**：
- IES 灯光导出仅在编辑器中可用（运行时无法访问 AssetImportData）
- 顶点颜色导出不推荐启用（glTF 中顶点颜色总是作为基础颜色乘数）
- `bExportVertexColors` 默认关闭是合理的

**推荐使用。** 这是 UE5 官方推荐的 glTF 导出方案，功能全面、持续维护，适合生产环境使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/GLTFExporter)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/exporting-unreal-engine-assets-to-gltf/)（UE 官方 glTF 导出文档）
- [glTF 2.0 规范](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)（Khronos 官方规范）
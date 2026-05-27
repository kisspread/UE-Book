# glTF Exporter

> An exporter for Khronos glTF 2.0.

| 属性 | 值 |
|---|---|
| 中文名 | glTF 导出器 |
| 分类 | Exporters |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质模板） |
| 模块 | `GLTFExporter` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-07-19 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/GLTFExporter) | |

## 用途

GLTFExporter 将 Unreal Engine 中的资产（网格体、材质、纹理、动画、灯光、相机、关卡序列等）导出为 Khronos glTF 2.0 格式（`.gltf` 或 `.glb`）。该插件的核心价值在于：

- **跨平台资产交换**：glTF 是业界标准的 3D 传输格式，被 Blender、Three.js、Babylon.js、WebXR 等广泛支持
- **Web 可视化**：直接将 UE 场景导入 Web 端 3D 查看器
- **工作流桥接**：在 UE 与其他 DCC 工具之间传递资产

插件内部采用 **Builder + Converter** 架构：`FGLTFConvertBuilder` 管理 glTF JSON 树的构建，各类 Converter（网格体、材质、纹理、动画、灯光等）负责将 UE 对象转换为 glTF 结构体，最终由 `FGLTFJsonRoot` 序列化为标准 JSON。

插件还支持大量 glTF 扩展，包括 `KHR_materials_clearcoat`、`KHR_materials_unlit`、`KHR_lights_punctual`、`EXT_lights_ies`、`KHR_texture_transform`、`KHR_materials_transmission` 等。

## 使用场景

- 你在开发 Web 端 3D 产品展示 → 用 GLTFExporter 导出模型到 Three.js/Babylon.js
- 你需要将 UE 场景交给 Blender 美术精修 → 导出 glTF 后在 Blender 打开
- 你要做 AR/VR 内容发布到 WebXR → 导出 glb 自包含文件
- 你需要批量导出场景中的特定 Actor 子集 → 使用 `SelectedActors` 参数
- 你有复杂的材质需要烘焙后导出 → 配置 `BakeMaterialInputs` 选项
- 你需要导出骨骼动画和 Morph Target → 启用 `bExportVertexSkinWeights` 和 `bExportMorphTargets`
- 你要导出 Level Sequence 动画 → 启用 `bExportLevelSequences`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExportToGLTF` | 将对象导出为 glTF 文件，返回是否成功及日志消息 | `UGLTFExporter` (Static) |
| `ResetToDefault` | 将导出选项重置为默认值 | `UGLTFExportOptions` |
| `ResetToDefault` | 将代理选项重置为默认值 | `UGLTFProxyOptions` |

### 导出选项属性

`UGLTFExportOptions` 提供了丰富的可配置属性，均支持蓝图读写：

| 分类 | 关键属性 | 说明 |
|---|---|---|
| General | `ExportUniformScale` | 导出缩放因子（默认 0.01，厘米→米） |
| General | `bExportPreviewMesh` | 是否导出独立动画/材质资产的预览网格体 |
| Material | `BakeMaterialInputs` | 材质输入烘焙模式（Disabled/Simple/UseMeshData） |
| Material | `bExportProxyMaterials` | 是否使用代理材质导出 |
| Material | `bExportUnlitMaterials` | 是否导出 Unlit 材质 |
| Material | `bExportClearCoatMaterials` | 是否导出 Clear Coat 材质 |
| Mesh | `DefaultLevelOfDetail` | 默认 LOD 级别 |
| Mesh | `bExportVertexColors` | 是否导出顶点颜色 |
| Mesh | `bExportVertexSkinWeights` | 是否导出骨骼权重 |
| Mesh | `bExportMorphTargets` | 是否导出 Morph Target |
| Mesh | `bUseMeshQuantization` | 是否使用顶点量化压缩 |
| Animation | `bExportLevelSequences` | 是否导出 Level Sequence |
| Animation | `bExportAnimationSequences` | 是否导出动画序列 |
| Texture | `TextureImageFormat` | 纹理格式（None/PNG/JPEG） |
| Texture | `bExportLightmaps` | 是否导出光照贴图 |
| Texture | `bExportTextureTransforms` | 是否导出 UV 变换 |
| Scene | `bExportHiddenInGame` | 是否导出游戏内隐藏的 Actor |
| Scene | `bExportLights` | 是否导出灯光（使用 KHR_lights_punctual） |
| Scene | `bExportCameras` | 是否导出相机 |

### 使用示例（蓝图描述）

**基本导出流程**：

1. 创建 `UGLTFExportOptions` 对象（或使用默认值 `nullptr`）
2. 设置所需的导出选项属性（如 `ExportUniformScale`、`TextureImageFormat` 等）
3. 调用 `ExportToGLTF` 节点，传入要导出的对象（`UWorld`、`UStaticMesh`、`UMaterialInterface` 等）、文件路径和选项
4. 检查返回的 `FGLTFExportMessages` 中的 `Errors` 和 `Warnings`

**导出选定 Actor**：

1. 获取要导出的 Actor 集合（如通过 `Get All Actors Of Class`）
2. 构造 `TSet<AActor*>` 传入 `ExportToGLTF` 的 `SelectedActors` 参数
3. 未被选中的 Actor 不会包含在导出结果中

**材质覆盖设置**：

1. 在材质资产上添加 `UGLTFMaterialExportOptions` 用户数据
2. 设置 `Proxy` 字段指定代理材质
3. 为不同材质属性组（BaseColor、Normal 等）配置独立的烘焙尺寸和过滤模式

## C++ 用法

### 头文件引入

```cpp
#include "Exporters/GLTFExporter.h"
#include "Options/GLTFExportOptions.h"
#include "UserData/GLTFMaterialUserData.h"
```

### 基本用法

最简单的导出方式，使用默认选项：

```cpp
#include "Exporters/GLTFExporter.h"

// 导出当前世界到 glTF 文件（使用默认选项）
bool bSuccess = UGLTFExporter::ExportToGLTF(
    nullptr,                                          // nullptr = 当前活动世界
    TEXT("/path/to/output/scene.gltf"),               // 输出路径
    nullptr,                                          // nullptr = 使用项目默认选项
    {}                                                // 空集合 = 导出所有 Actor
);

// 导出为自包含的二进制 glb 文件
bool bSuccessGLB = UGLTFExporter::ExportToGLTF(
    GWorld,
    TEXT("/path/to/output/scene.glb"),
    nullptr,
    {}
);
```

来源：`Source/GLTFExporter/Public/Exporters/GLTFExporter.h`

### 配置选项导出

```cpp
#include "Exporters/GLTFExporter.h"
#include "Options/GLTFExportOptions.h"

// 创建导出选项
UGLTFExportOptions* Options = NewObject<UGLTFExportOptions>();
Options->ExportUniformScale = 1.0f;                  // 不缩放（保持厘米单位）
Options->TextureImageFormat = EGLTFTextureImageFormat::PNG;
Options->bExportVertexSkinWeights = true;
Options->bExportMorphTargets = true;
Options->bExportLights = true;
Options->bExportCameras = true;
Options->bExportLevelSequences = true;
Options->bExportTextureTransforms = true;
Options->BakeMaterialInputs = EGLTFMaterialBakeMode::UseMeshData;
Options->DefaultLevelOfDetail = 0;

// 仅导出选中的 Actor
TSet<AActor*> SelectedActors;
SelectedActors.Add(MyActor1);
SelectedActors.Add(MyActor2);

// 执行导出并获取消息
FGLTFExportMessages Messages;
bool bSuccess = UGLTFExporter::ExportToGLTF(
    GWorld,
    TEXT("/path/to/output/filtered_scene.gltf"),
    Options,
    SelectedActors,
    Messages
);

// 检查结果
for (const FString& Error : Messages.Errors)
{
    UE_LOG(LogGLTFExporter, Error, TEXT("Export Error: %s"), *Error);
}
for (const FString& Warning : Messages.Warnings)
{
    UE_LOG(LogGLTFExporter, Warning, TEXT("Export Warning: %s"), *Warning);
}
```

来源：`Source/GLTFExporter/Public/Exporters/GLTFExporter.h`、`Source/GLTFExporter/Public/Options/GLTFExportOptions.h`

### 材质覆盖设置

```cpp
#include "UserData/GLTFMaterialUserData.h"

// 在 C++ 中获取材质的 glTF 导出选项
UMaterialInterface* Material = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Materials/MyMaterial"));

// 解析代理材质
const UMaterialInterface* ResolvedMaterial = UGLTFMaterialExportOptions::ResolveProxy(Material);

// 获取特定属性组的烘焙设置
FGLTFMaterialBakeSize BakeSize = UGLTFMaterialExportOptions::GetBakeSizeForPropertyGroup(
    Material,
    EGLTFMaterialPropertyGroup::BaseColorOpacity,
    FGLTFMaterialBakeSize::Default
);

TextureFilter BakeFilter = UGLTFMaterialExportOptions::GetBakeFilterForPropertyGroup(
    Material,
    EGLTFMaterialPropertyGroup::Normal,
    TextureFilter::TF_Bilinear
);
```

来源：`Source/GLTFExporter/Public/UserData/GLTFMaterialUserData.h`

## Demo 示例

### 最小导出示例

```cpp
// MyGLTFExportComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyGLTFExportComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyGLTFExportComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "glTF Export")
    FString ExportFilePath = TEXT("Export/output.gltf");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "glTF Export")
    bool bExportSelectedOnly = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "glTF Export")
    bool bExportLights = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "glTF Export")
    bool bExportCameras = true;

    UFUNCTION(BlueprintCallable, Category = "glTF Export")
    bool ExportScene();
};
```

```cpp
// MyGLTFExportComponent.cpp
#include "MyGLTFExportComponent.h"
#include "Exporters/GLTFExporter.h"
#include "Options/GLTFExportOptions.h"

bool UMyGLTFExportComponent::ExportScene()
{
    UGLTFExportOptions* Options = NewObject<UGLTFExportOptions>();
    Options->bExportLights = bExportLights;
    Options->bExportCameras = bExportCameras;
    Options->bExportTextureTransforms = true;
    Options->bExportLightmaps = true;

    TSet<AActor*> SelectedActors;
    if (bExportSelectedOnly)
    {
        SelectedActors.Add(GetOwner());
    }

    FGLTFExportMessages Messages;
    bool bSuccess = UGLTFExporter::ExportToGLTF(
        GetWorld(),
        FPaths::ProjectDir() / ExportFilePath,
        Options,
        SelectedActors,
        Messages
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("glTF export succeeded: %s"), *ExportFilePath);
    }
    else
    {
        for (const FString& Error : Messages.Errors)
        {
            UE_LOG(LogTemp, Error, TEXT("glTF export error: %s"), *Error);
        }
    }

    return bSuccess;
}
```

## 模块依赖

插件依赖以下其他插件：

| 插件 | 用途 | 必需 |
|---|---|---|
| `VariantManagerContent` | 支持材质变体导出（Material Variants） | ✅ |
| `Interchange` | Interchange 导入器的材质映射（可选） | ❌ |
| `InterchangeAssets` | Interchange 资产支持 | ✅ |

无特殊模块依赖（仅标准 Core/Engine/RenderCore/MeshDescription 等）。

> **注意**：该插件的 Runtime 模块在 `PostConfigInit` 阶段加载，且仅支持 Win64、Mac、Linux 平台。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-20 | `4bd57e77` | Fixed crash when creating a GTLFMaterialProxy on a incomplete material | 修复在不完整材质上创建 glTF 材质代理时的崩溃 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到 UE_LOGF 新宏 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 整理纹理属性修改代码，使用正确的编辑器回调 |
| 2026-03-03 | `373e8a9e` | Fixed build error of QA_ContentPipeline project introduced by CL 51336460 | 修复 QA_ContentPipeline 项目的编译错误 |

### 维护评价

- **活跃维护**：最近 3 个月内有多次实质性更新（bug 修复、编译问题修复）
- **创建时间**：2022 年 7 月，约 4 年历史，属于成熟插件
- **更新频率**：稳定，持续有维护性更新
- **官方维护**：由 Epic Games 官方维护，纳入 Enterprise 分类
- **已知限制**：
  - Level Sequence 仅支持变换轨道
  - IES 灯光导出不支持运行时（依赖 AssetImportData）
  - Thin Translucent 材质导出仅为部分支持
  - 仅支持 Win64/Mac/Linux 平台
- **推荐程度**：⭐⭐⭐⭐⭐ 强烈推荐。这是 Epic 官方的 glTF 导出方案，支持广泛，维护活跃，是 UE 到 glTF 工作流的首选方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/GLTFExporter)
- [glTF 2.0 规范](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)
- [KHR_materials_clearcoat](https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_materials_clearcoat/README.md)
- [KHR_lights_punctual](https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_lights_punctual/README.md)
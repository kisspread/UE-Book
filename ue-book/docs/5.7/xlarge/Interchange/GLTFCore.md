# Interchange Framework - GLTFCore 模块

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | GLTF 核心模块 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无（纯代码模块） |
| 模块 | `GLTFCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime/Source/Parsers/GLTFCore) | |

## 用途

GLTFCore 是 Interchange 框架中专门用于解析 glTF/GLB 格式文件的底层核心模块。它负责：
- **加载和解析** glTF 的 JSON 描述及二进制数据（.glb 格式），提取场景、节点、网格、材质、动画、纹理等完整资产结构。
- **坐标系与单位转换**：将 glTF 右手系+Y 上方向转换为 Unreal 左手系+Z 上方向，并对齐单位（默认 glTF 单位米，Unreal 单位厘米）。
- **支持 glTF 扩展**：包括 KHR_materials_* 系列、KHR_lights_punctual、KHR_draco_mesh_compression、MSFT_* 打包纹理等。
- **提供工厂接口**：`FMaterialFactory`、`FMeshFactory`、`ITextureFactory`、`IMaterialElementFactory` 等，允许上层模块（如 InterchangeImport）将解析出的数据结构化为 Unreal 资产。

简言之，GLTFCore 是 Interchange 引入 glTF 的“翻译官”，将通用 glTF 数据解析成 Unreal 可理解的中间表示，为后续资产创建管线提供干净、类型化的数据。

## 使用场景

- 需要导入 .gltf 或 .glb 文件到 Unreal 项目（通过 Interchange 框架自动触发）。
- 在 C++ 插件中扩展 glTF 导入管线：例如自定义材质生成、网格优化、动画重映射。
- 手写 glTF 导入工具时直接复用 GLTFCore 的解析逻辑（`FFileReader`）。
- 测试 glTF 解析的正确性（单元测试可通过 `FAsset` 结构直接比对数据）。

## 蓝图用法

GLTFCore 模块不直接暴露任何蓝图可调用函数（`UFUNCTION(BlueprintCallable)`）或蓝图读写属性（`UPROPERTY(BlueprintReadWrite)`）。所有 API 均为 C++ 接口，由上层导入管线封装。因此蓝图中不可直接使用。

若需要在蓝图中控制 glTF 导入行为（如材质设置、网格合并选项），请使用 Interchange 的高层蓝图节点（位于 `InterchangeImport` 模块），例如：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Import Asset` | 通过 Interchange 导入文件（支持 glTF） | `UInterchangeManager` |
| `On Pre Import Pipeline` | 导入前自定义管线（可设置材质、网格等） | `UInterchangePipelineBase` |

## C++ 用法

### 头文件引入

```cpp
#include "GLTFAsset.h"
#include "GLTFReader.h"
#include "GLTFMaterialFactory.h"
#include "GLTFMeshFactory.h"
```

### 基本用法

以下代码演示如何使用 `FFileReader` 加载一个 .gltf 文件，并获取基本资产信息：

```cpp
// File: Source/Parsers/GLTFCore/Private/GLTFReader.cpp (简化)
#include "GLTFReader.h"
#include "GLTFAsset.h"

// 1. 创建阅读器
GLTF::FFileReader Reader;

// 2. 构造空的资产对象
GLTF::FAsset Asset;

// 3. 读取文件
Reader.ReadFile(TEXT("/Game/Models/MyModel.gltf"), false, false, Asset);
// 第二个参数 false：不加载图像像素数据（只保留引用和路径）
// 第三个参数 false：不加载额外元数据

// 4. 访问解析结果
UE_LOG(LogTemp, Log, TEXT("Asset has %d meshes, %d materials, %d nodes"),
       Asset.Meshes.Num(), Asset.Materials.Num(), Asset.Nodes.Num());

// 5. 检查错误
for (const GLTF::FLogMessage& Log : Reader.GetLogMessages())
{
    if (Log.Get<0>() == GLTF::EMessageSeverity::Error)
    {
        UE_LOG(LogTemp, Error, TEXT("glTF error: %s"), *Log.Get<1>().ToString());
    }
}
```

### 进阶用法

#### 自定义材质工厂

在 Interchange 导入管线中，可以注入自定义的 `IMaterialElementFactory` 和 `ITextureFactory` 来控制材质和纹理的生成方式：

```cpp
#include "GLTFMaterialFactory.h"

class FMyMaterialFactory : public GLTF::IMaterialElementFactory
{
public:
    virtual GLTF::FMaterialElement* CreateMaterial(const TCHAR* Name,
        UObject* ParentPackage, EObjectFlags Flags) override
    {
        // 创建自定义材质元素（例如基于 UMaterialInstanceDynamic）
        return new GLTF::FMaterialElement(Name);
    }
};

// 使用
FMyMaterialFactory MyFactory;
GLTF::ITextureFactory* MyTextureFactory = ...;
GLTF::FMaterialFactory MaterialFactory(&MyFactory, MyTextureFactory);

MaterialFactory.CreateMaterials(Asset, ParentPackage, Flags);
```

#### 网格坐标转换

GLTFCore 自动处理坐标转换，但也可手动使用 `ConversionUtilities.h` 中的函数：

```cpp
#include "GLTF/ConversionUtilities.h"

FVector UnrealPos = GLTF::ConvertVec3(glTFPos);      // glTF Y-up → Unreal Z-up
FQuat   UnrealRot = GLTF::ConvertQuat(glTFRot);       // 四元数转换
FMatrix UnrealMat = GLTF::ConvertMat(glTFSkinMatrix); // 矩阵转置
```

#### 扩展处理

通过 `FExtensionsHandler` 可以获取解析时处理的扩展信息：

```cpp
#include "GLTF/ExtensionsHandler.h"

GLTF::FExtensionsHandler ExtHandler(Messages);
ExtHandler.SetAsset(Asset);
// 启动扩展设置（在解析 JSON 时自动调用 Setup*Extensions 方法）
```

### 主要公开类速览

| 类 | 头文件 | 用途 |
|---|---|---|
| `GLTF::FFileReader` | `GLTFReader.h` | 解析 .gltf/.glb 文件，填充 `FAsset` |
| `GLTF::FAsset` | `GLTFAsset.h` | 整个 glTF 资产的容器（场景、网格、材质、动画等） |
| `GLTF::FMeshFactory` | `GLTFMeshFactory.h` | 将 `GLTF::FMesh` 转换为 `FMeshDescription` |
| `GLTF::FMaterialFactory` | `GLTFMaterialFactory.h` | 使用工厂创建 `FMaterialElement` |
| `GLTF::FTextureMap` | `GLTFMaterial.h` | 纹理映射（索引、坐标、变换） |
| `GLTF::FPrimitive` | `GLTFMesh.h` | 图元（三角形、多属性访问器、形态目标） |
| `GLTF::FNode` | `GLTFNode.h` | 节点（变换、网格引用、皮肤、相机、灯光） |
| `GLTF::FAnimation` | `GLTFAnimation.h` | 动画（采样器、通道、关键帧） |
| `GLTF::FMetadata` | `GLTFAsset.h` | 资产元数据（生成器、版本、额外数据） |

### 重要枚举和常量

| 枚举/常量 | 用途 |
|---|---|
| `GLTF::EMeshAttributeType` | 顶点属性类型（POSITION, NORMAL, TANGENT, TEXCOORD_*, COLOR_*, JOINTS_*, WEIGHTS_*） |
| `GLTF::EExtension` | 支持的 glTF 扩展（KHR_*、MSFT_*、EXT_*） |
| `GLTF::FAnimation::EInterpolation` | 动画插值类型（Linear, Step, CubicSpline） |
| `GLTF::FMaterial::EAlphaMode` | 材质 Alpha 模式（Opaque, Mask, Blend） |
| `GLTF::FMaterial::EShadingModel` | 着色模型（MetallicRoughness, SpecularGlossiness） |
| `GLTF::FMaterial::EPackingFlags` | 纹理打包标志（如 OcclusionRoughnessMetallic） |

## Demo 示例

以下是一个完整的最小 C++ 示例，演示如何使用 `FFileReader` 和 `FMeshFactory` 将一个简单 glTF 文件转换为 `FMeshDescription`：

```cpp
// MyMeshImporter.h
#pragma once

#include "CoreMinimal.h"
#include "GLTFReader.h"
#include "GLTFMeshFactory.h"
#include "MeshDescription.h"

class FMyMeshImporter
{
public:
    bool Import(const FString& FilePath, FMeshDescription& OutMeshDesc)
    {
        GLTF::FFileReader Reader;
        GLTF::FAsset Asset;

        Reader.ReadFile(FilePath, false, false, Asset);

        if (Asset.Meshes.Num() == 0)
        {
            return false;
        }

        // 只处理第一个网格
        const GLTF::FMesh& Mesh = Asset.Meshes[0];

        GLTF::FMeshFactory Factory;
        Factory.SetUniformScale(0.01f); // glTF 米 → UE 厘米

        // 创建临时 MeshDescription
        FMeshDescription* Desc = &OutMeshDesc;
        Factory.FillMeshDescription(Mesh, FTransform::Identity, Desc);

        return true;
    }
};
```

依赖模块：`GLTFCore`、`MeshDescription`、`MeshUtilities`（可选）。

## 模块依赖

从 `GLTFCore.Build.cs` 提取的独特依赖：

| 模块 | 用途 |
|---|---|
| `MeshDescription` | 网格表示结构（`FMeshDescription`, `FVertexID`, `FPolygonGroupID`） |
| `MeshUtilitiesCommon` | 网格工具辅助（如法兰西线生成） |
| `JsonUtilities` | JSON 对象操作（`FJsonObject`, `FJsonValue`） |
| `MaterialUtilities` | 材质生成辅助（`FMaterialProxySettings` 等） |
| `ImageCore` | 图像数据处理（`FImage`, `FImageUtils`） |

其他标准依赖（Core、CoreUObject、Engine、Projects）略。

## 维护状态

### 近期更新

- 2025-12-18 93cfc06 — Fixed editor hanging when level reimporting a file containing skeletal meshes
- 2025-10-23 0158cf6 — [Interchange] Removing unintended LOD specialization from named LOD Groups.
- 2025-10-21 63c630c0 — [Interchange] Fixing missing animation sequence import for LevelSequence on StaticMesh imported with
- 2025-10-17 765b3a10 — Fixed compilation error with NonUnity InterchangeWorker
- 2025-10-17 2c91170f — Replaced use of /InterchangeAssets/Materials/PhongSurfaceMaterial.PhongSurfaceMaterial with /Interch…

### 维护评价

GLTFCore 是 Interchange 框架的一部分，近期更新活跃（最近 2 个月内仍有提交）。主要围绕骨骼网格重导入、LOD 组、动画序列导入等修复。模块创建于 2025 年 10 月（约 2 个月前），属于“新模块”。目前处于积极开发中，推荐在新项目中使用 Interchange 配合 GLTFCore 进行 glTF 导入。无已知弃用警告。

## 相关链接

- [Interchange 插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange)
- [GLTFCore 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime/Source/Parsers/GLTFCore)
- [官方文档 (Interchange)](https://docs.unrealengine.com/5.7/en-US/importing-assets-using-interchange-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Tests)
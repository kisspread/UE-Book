# Interchange Framework

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | 交换框架 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、C++ 模块） |
| 模块 | `InterchangeCommon` (Runtime), `InterchangeDispatcher` (Runtime), `InterchangeExport` (Runtime), `InterchangeFactoryNodes` (Runtime), `InterchangeImport` (Runtime), `InterchangeMessages` (Runtime), `InterchangeNodes` (Runtime), `InterchangeCommonParser` (Runtime), `InterchangeFbxParser` (Runtime), `GLTFCore` (Runtime), `InterchangePipelines` (Runtime), `Draco` (External) |
| 实验性 | 否 |
| 创建时间 | 2025-10-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime) | |

## 用途

Interchange Framework 是 UE5 新一代的导入导出系统，旨在取代旧有的 FBX/Obj 导入器，提供统一、可扩展、并发的资源导入架构。核心特性包括：异步文件解析、基于管线的导入流程（Pipeline）、支持 FBX、USD、glTF、MaterialX 等多种格式、完善的错误和警告消息系统，以及工厂节点（Factory Node）机制用于生成 UE 资产。

`InterchangeCommon` 是框架的基础模块，定义了跨模块公用的数据结构、枚举和常量，主要包括：

- 材质导入相关的枚举（MaterialX、USD 材质类型、BSDF/EDF 等）
- USD 特定常量（Primvar 处理、骨骼命名、稀疏体积纹理等）
- 体积数据相关枚举（稀疏体积纹理格式）
- 版本信息和通用定义

任何使用 Interchange 框架的模块或自定义 Pipeline 都需要依赖此模块获取基础类型。

## 使用场景

- 你在制作一个需要批量导入大量 FBX 或 USD 模型并自动应用材质的工具 → 编写自定义 Import Pipeline，使用 `EInterchangeMaterialXShaders` 等枚举控制材质转换。
- 你需要扩展 Interchange 支持新的文件格式 → 在解析器模块中引用 `InterchangeCommon` 的类型定义。
- 你想在蓝图或 C++ 中判断导入的材质类型 → 使用 `EInterchangeMaterialXShaders`、`EInterchangeMaterialXBSDF` 等枚举。

## 蓝图用法

`InterchangeCommon` 模块主要提供蓝图可用的枚举类型，没有直接暴露的蓝图可调用函数或事件。以下枚举可在蓝图中作为变量或参数使用。

### 核心枚举

| 枚举 | 说明 | 所属命名空间 |
|---|---|---|
| `EInterchangeMaterialXShaders` | MaterialX 支持的 Shader 类型（OpenPBRSurface、StandardSurface、UsdPreviewSurface 等） | Global |
| `EInterchangeMaterialXBSDF` | 双向散射分布函数类型（OrenNayarDiffuse、Dielectric、Conductor、Sheen 等） | Global |
| `EInterchangeMaterialXEDF` | 辐射分布函数类型（Uniform、Conical） | Global |
| `EInterchangeMaterialXTexture` | 纹理映射类型（Image、TiledImage、Checkerboard 等） | Global |
| `EInterchangeUsdPrimvar` | USD Primvar 导入策略（Standard、Bake、All） | Global |
| `EInterchangeSparseVolumeTextureFormat` | 稀疏体积纹理格式（Unorm8、Float16、Float32） | Global |

### 使用示例（蓝图）

1. **在自定义 Pipeline 中判断 Shader 类型**  
   - 创建一个 `Get MaterialX Shaders` 节点（非实际节点，枚举用于条件分支）  
   - 将导入解析出的 Shader 类型转换为 `EInterchangeMaterialXShaders` 并比较

2. **配置 USD Primvar 导入方式**  
   - 在 `UInterchangeUSDImportProperties`（属于 InterchangePipelines 模块）中设置 `PrimvarImport` 为 `EInterchangeUsdPrimvar::All`

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeCommonModule.h" // 推荐统一引入
// 或按需引入：
#include "MaterialX/InterchangeMaterialXDefinitions.h"
#include "Usd/InterchangeUsdDefinitions.h"
#include "Volume/InterchangeVolumeDefinitions.h"
```

### 基本用法

```cpp
// 使用 MaterialX 枚举判断 shader 类型
EInterchangeMaterialXShaders ShaderType = EInterchangeMaterialXShaders::StandardSurface;
if (ShaderType == EInterchangeMaterialXShaders::OpenPBRSurface)
{
    // 处理 Open PBR Surface
}

// 使用 USD 命名空间常量获取骨骼前缀
FString BonePrefix = UE::Interchange::USD::BonePrefix;
FString RootUid = FString::Printf(TEXT("%s/%s"), *SkeletonPrimPath, *UE::Interchange::USD::RootBoneUidSuffix);

// 使用体积定义的结构
UE::Interchange::Volume::FComponentMapping Mapping;
Mapping.SourceGridIndex = 0;
Mapping.SourceComponentIndex = 1;
```

**来源：** `Engine/Plugins/Interchange/Runtime/Source/Common/Public/MaterialX/InterchangeMaterialXDefinitions.h`, `Public/Usd/InterchangeUsdDefinitions.h`, `Public/Volume/InterchangeVolumeDefinitions.h`

### 进阶用法

结合其他 Interchange 模块使用 `InterchangeCommon` 的类型：

```cpp
// 自定义 Pipeline 中获取材质节点并转换
UInterchangeShaderNode* ShaderNode = ...;
if (ShaderNode)
{
    // 假设 ShaderNode 有自定义属性存储材质类型
    FString SubType;
    if (ShaderNode->GetStringAttribute(UInterchangeShaderNode::GetSubTypeAttributeKey(), SubType))
    {
        // 将字符串映射到枚举
        static const TMap<FString, EInterchangeMaterialXShaders> ShaderMap = {
            { TEXT("StandardSurface"), EInterchangeMaterialXShaders::StandardSurface },
            // ...
        };
        if (const EInterchangeMaterialXShaders* Found = ShaderMap.Find(SubType))
        {
            // 使用枚举进行后续处理
        }
    }
}
```

## Demo 示例

以下是一个最小 C++ 模块，演示如何使用 `InterchangeCommon` 的枚举和常量。

**SInterchangeCommonDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "InterchangeCommonModule.h"   // 确保在模块依赖中加入了 InterchangeCommon

class FInterchangeCommonDemo
{
public:
    void RunDemo();
};
```

**SInterchangeCommonDemo.cpp**
```cpp
#include "SInterchangeCommonDemo.h"
#include "MaterialX/InterchangeMaterialXDefinitions.h"
#include "Usd/InterchangeUsdDefinitions.h"
#include "Volume/InterchangeVolumeDefinitions.h"

void FInterchangeCommonDemo::RunDemo()
{
    // 使用枚举
    EInterchangeMaterialXShaders ShaderType = EInterchangeMaterialXShaders::OpenPBRSurface;
    EInterchangeMaterialXBSDF BSDFType = EInterchangeMaterialXBSDF::Dielectric;
    EInterchangeSparseVolumeTextureFormat VolumeFormat = EInterchangeSparseVolumeTextureFormat::Float16;
    
    // 使用 USD 常量
    FString BonePrefix = UE::Interchange::USD::BonePrefix;
    FString RootBoneUid = FString::Printf(TEXT("%s/%s"), TEXT("/MySkel"), *UE::Interchange::USD::RootBoneUidSuffix);
    
    // 使用体积结构体
    UE::Interchange::Volume::FTextureInfo TexInfo;
    TexInfo.Mappings[0].SourceGridIndex = 0;
    TexInfo.Mappings[0].SourceComponentIndex = 0;
    TexInfo.Format = EInterchangeSparseVolumeTextureFormat::Float16;
    
    UE_LOG(LogTemp, Log, TEXT("InterchangeCommon Demo: Shader=%d, BSDF=%d, BonePrefix=%s"), 
           (int32)ShaderType, (int32)BSDFType, *BonePrefix);
}
```

## 模块依赖

`InterchangeCommon` 本身只依赖标准运行时库，不引入外部模块。依赖列表中：

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

其他 Interchange 模块（如 `InterchangeImport`、`InterchangePipelines`）在 Build.cs 中需添加 `PublicDependencyModuleNames.AddRange(new string[] { "InterchangeCommon" });`

## 维护状态

### 近期更新（最近 5 次提交）

从 `Engine/Plugins/Interchange/Runtime` 目录的 git 日志：

- 2025-12-18 `93cfc06e` Fixed editor hanging when level reimporting a file containing skeletal meshes
- 2025-10-23 `0158cf6a` [Interchange] Removing unintended LOD specialization from named LOD Groups.
- 2025-10-21 `63c630c0` [Interchange] Fixing missing animation sequence import for LevelSequence on StaticMesh imported with
- 2025-10-17 `765b3a10` Fixed compilation error with NonUnity InterchangeWorker
- 2025-10-17 `2c91170f` Replaced use of /InterchangeAssets/Materials/PhongSurfaceMaterial.PhongSurfaceMaterial with /Interch

### 维护评价

- **创建时间**：2025-10-17（首次提交）
- **最近更新**：2025-12-18（约 2 个月前），修复了编辑器卡死问题，说明仍在活跃维护。
- **更新频率**：平均每月有多次功能性修复和调整。
- **已知问题**：无特殊标记，但作为 UE5 核心导入框架，持续优化中。
- **推荐使用**：✅ 推荐使用。Interchange 是 UE5 官方最新的导入系统，功能完善，社区反馈良好。对于需要自定义导入流程的开发者尤为适合。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime)
- [官方文档](https://docs.unrealengine.com/5.4/zh-CN/interchange-framework/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Tests)
# Geometry Processing

> Data Structures and Algorithms for Processing 2D and 3D Geometry

| 属性 | 值 |
|---|---|
| 中文名 | 几何处理 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `GeometryAlgorithms` (Runtime), `DynamicMesh` (Runtime), `MeshFileUtils` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryProcessing) | |

## 用途

GeometryProcessing 是 UE5 的核心几何处理基础设施，提供用于操作 2D 和 3D 几何数据的底层数据结构和算法。该插件最初位于 `Engine/Plugins/Experimental` 目录下，于 2021 年迁移至 `Runtime`，是 Unreal Engine 中**程序化网格生成、编辑和分析**的基石。

该插件解决了以下核心问题：

- **动态网格操作**：通过 `FDynamicMesh3` 提供一种高效、可修改的网格表示（区别于 `UStaticMesh` 的不可变烘焙格式），支持实时增删改查顶点、三角形和属性层
- **几何算法库**：提供布尔运算、网格简化、细分曲面、UV 参数化、空间查询等通用几何算法
- **文件格式 I/O**：支持 OBJ 等标准网格文件格式的读写

该插件被 UE5 的 **Modeling Tools Editor**（建模工具编辑器插件）、**Geometry Script**（蓝图网格脚本）、**Chaos Visual Debugger** 等众多上层系统依赖，是 UE5 程序化内容创作（PCG）生态的关键底层组件。

## 模块结构

| 模块 | 类型 | 说明 |
|---|---|---|
| **GeometryAlgorithms** | Runtime | 几何算法库：空间查询、网格布尔运算、简化、细分、参数化等核心算法 |
| **DynamicMesh** | Runtime | 动态网格数据结构：`FDynamicMesh3` 及其属性层（法线、UV、颜色、自定义属性）系统 |
| **MeshFileUtils** | DeveloperTool | 网格文件工具：OBJ 格式的读写功能，主要用于开发和调试 |

## 使用场景

- 你需要在运行时动态生成或修改网格几何体（程序化地形、建筑、角色变形等）→ 用 **DynamicMesh** 模块的 `FDynamicMesh3`
- 你需要对网格执行布尔运算（并集、交集、差集）→ 用 **GeometryAlgorithms** 模块的 CSG/Boolean 算法
- 你需要在编辑器中构建自定义建模工具 → 这个插件提供底层几何操作支持
- 你需要在开发/测试阶段加载或导出 OBJ 网格文件 → 用 **MeshFileUtils** 模块
- 你需要对网格进行简化、细分、UV 展开等操作 → 用 **GeometryAlgorithms** 模块的对应算法

## 蓝图用法

本插件主要面向 C++ 开发者，核心类型 `FDynamicMesh3` 不直接暴露为蓝图类型。如需在蓝图中操作动态网格，应使用上层插件 **Geometry Script**（`GeometryScriptingCore`），它将 `FDynamicMesh3` 的操作封装为 `UGeometryScriptLibrary_*` 蓝图函数库。

本插件自身的蓝图可调用接口极少，大部分 API 为纯 C++。

## C++ 用法

### 头文件引入

```cpp
// 动态网格
#include "DynamicMesh/DynamicMesh3.h"
#include "DynamicMesh/DynamicMeshAttributeSet.h"

// OBJ 文件工具
#include "OBJMeshUtil.h"

// 几何算法（按需引入具体头文件）
#include "Spatial/SpatialInterfaces.h"
```

### 基本用法 — OBJ 文件读写

来源：`Source/MeshFileUtils/Public/OBJMeshUtil.h`

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "OBJMeshUtil.h"

using namespace UE::Geometry;
using namespace UE::MeshFileUtils;

// === 加载 OBJ 文件 ===
FDynamicMesh3 Mesh;

// 配置加载选项
FLoadOBJSettings LoadSettings;
LoadSettings.bLoadNormals = true;   // 加载法线信息
LoadSettings.bLoadUVs = true;       // 加载 UV 信息
LoadSettings.bReverseOrientation = false;  // 不反转面朝向
LoadSettings.bAddSeparatedTriForNonManifold = true;  // 非流形三角形独立添加

// 方式一：检查状态
ELoadOBJStatus Status = LoadOBJ("/path/to/mesh.obj", Mesh, LoadSettings);
if (Status == ELoadOBJStatus::Success)
{
    UE_LOG(LogTemp, Log, TEXT("OBJ loaded: %d vertices, %d triangles"),
        Mesh.VertexCount(), Mesh.TriangleCount());
}

// 方式二：加载失败则断言（适合确定文件一定存在的场景）
FDynamicMesh3 Mesh2 = LoadOBJChecked("/path/to/known_good.obj");

// === 写入 OBJ 文件 ===
FWriteOBJSettings WriteSettings;
WriteSettings.bReverseOrientation = false;
WriteSettings.bWritePerVertexValues = true;   // 写入逐顶点法线/UV
WriteSettings.bWritePerVertexColors = true;    // 写入逐顶点颜色

bool bSuccess = WriteOBJ("/path/to/output.obj", Mesh, WriteSettings);
```

### 基本用法 — DynamicMesh3 核心操作

```cpp
#include "DynamicMesh/DynamicMesh3.h"

using namespace UE::Geometry;

// 创建一个空的动态网格
FDynamicMesh3 Mesh;

// 设置网格为有索引模式（索引模式 vs 紧凑模式）
Mesh.EnableTriangleGroups();

// 添加顶点，返回顶点 ID
int32 V0 = Mesh.AppendVertex(FVector3d(0, 0, 0));
int32 V1 = Mesh.AppendVertex(FVector3d(100, 0, 0));
int32 V2 = Mesh.AppendVertex(FVector3d(0, 100, 0));
int32 V3 = Mesh.AppendVertex(FVector3d(100, 100, 0));

// 添加三角形，返回三角形 ID
int32 T0 = Mesh.AppendTriangle(V0, V1, V2);
int32 T1 = Mesh.AppendTriangle(V1, V3, V2);

// 查询信息
int32 NumVerts = Mesh.VertexCount();
int32 NumTris = Mesh.TriangleCount();

// 遍历所有三角形
for (int32 TID : Mesh.TriangleIndicesItr())
{
    FIndex3i Tri = Mesh.GetTriangle(TID);
    FVector3d Centroid = Mesh.GetTriCentroid(TID);
}

// 遍历所有顶点
for (int32 VID : Mesh.VertexIndicesItr())
{
    FVector3d Pos = Mesh.GetVertex(VID);
}
```

### 进阶用法 — 属性层系统

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "DynamicMesh/DynamicMeshAttributeSet.h"

using namespace UE::Geometry;

FDynamicMesh3 Mesh;

// 创建法线属性层
FDynamicMeshNormalOverlay* Normals = Mesh.Attributes()->PrimaryNormals();
if (Normals == nullptr)
{
    Mesh.Attributes()->EnableNormals();
    Normals = Mesh.Attributes()->PrimaryNormals();
}

// 创建 UV 属性层
FDynamicMeshUVOverlay* UVs = Mesh.Attributes()->PrimaryUV();
if (UVs == nullptr)
{
    Mesh.Attributes()->EnablePrimaryUVs();
    UVs = Mesh.Attributes()->PrimaryUV();
}

// 为三角形设置 UV
// UV overlay 的元素 ID 与三角形顶点一一对应
int32 ElemID = UVs->AppendElement(FVector2f(0.0f, 0.0f));
// 将 UV 元素关联到三角形 T0 的第 0 个顶点
UVs->SetTriangle(TriID, FIndex3i(ElemID, ElemID2, ElemID3));
```

## 模块依赖

从各模块 Build.cs 提取：

| 模块 | 用途 |
|---|---|
| `DynamicMesh` | 动态网格核心数据结构（FDynamicMesh3） |
| `GeometryAlgorithms` | 几何算法库（MeshFileUtils 依赖） |

无特殊外部依赖（仅标准 Core/CoreUObject 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `35f4c4a4` | Fix float overflow warning for arm64 build | 修复 ARM64 构建的浮点溢出警告 |
| 2026-05-15 | `35f66cf1` | Guard against INDEX_NONE / invalid edge id in hole fill util's fill color method | 填孔工具的填充颜色方法中防护无效边 ID |
| 2026-05-13 | `2c7d172e` | Clamp UV values to max float when invalid value is in returned as double (max double) | UV 值无效时钳制到 max float 而非 max double |
| 2026-05-12 | `64deb517` | Hook up AttributeAwareV2 simplifier in MeshTerrainStaticMeshTransformer | 网格地形变换器中接入属性感知 V2 简化器 |
| 2026-05-12 | `68fbe22e` | [SkeletalMeshModelingTools] clamp smooth strength to 0 - 1 | 骨骼网格建模工具中将平滑强度钳制到 0-1 |

### 维护评价

- **活跃维护**：该插件持续获得实质性更新（最新提交距今仅数天）
- 从 2021 年的 Experimental 迁移到 Runtime，表明已通过稳定性审查
- 仍标记为 `IsBetaVersion = true`，API 可能存在向后不兼容的变更
- 更新内容涵盖 bug 修复、新算法集成（如 AttributeAwareV2 简化器）、跨平台编译修复
- 被 Modeling Tools、Geometry Script、Chaos Visual Debugger 等核心系统依赖，属于**关键基础设施**
- **推荐使用**：对于需要 C++ 层面动态网格操作的项目，这是首选方案

---

# Mesh File Utils

> 网格文件工具：提供 OBJ 等标准网格文件格式的读写功能

| 属性 | 值 |
|---|---|
| 中文名 | 网格文件工具 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MeshFileUtils` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryProcessing/Source/MeshFileUtils) | |

## 用途

`MeshFileUtils` 是 GeometryProcessing 插件中的**开发工具模块**，专门提供 Wavefront OBJ 文件格式的读写功能。它在 `FDynamicMesh3` 与 OBJ 文件之间架起桥梁，让开发者可以在运行时（开发环境）中加载外部网格文件或将动态网格导出为 OBJ 格式。

该模块类型为 `DeveloperTool`，意味着它**仅在开发/编辑器环境中可用**，不会被打包到最终发布版本中。这一定位表明其主要用于：

- 开发阶段的网格资产导入/导出调试
- 自动化测试中的网格数据交换
- 原型验证时快速加载外部网格

注意：该模块支持的程序为 `ChaosVisualDebugger`，说明它也被 Chaos 物理调试工具使用。

## 使用场景

- 你在开发调试阶段需要快速导入一个 OBJ 文件到 `FDynamicMesh3` 中进行算法测试 → 用 `LoadOBJ`
- 你需要将程序化生成的网格导出为 OBJ 文件供外部工具（Blender、Maya 等）查看 → 用 `WriteOBJ`
- 你在编写自动化测试，需要从文件加载网格数据作为测试输入 → 用 `LoadOBJChecked`（失败直接断言）
- 你需要在 Chaos 物理调试器中加载外部网格几何体

## 蓝图用法

该模块没有暴露蓝图可调用接口。所有 API 均为纯 C++ 命名空间函数。

## C++ 用法

### 头文件引入

```cpp
#include "OBJMeshUtil.h"
```

### 基本用法 — 加载 OBJ 文件

来源：`Source/MeshFileUtils/Public/OBJMeshUtil.h`

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "OBJMeshUtil.h"

using namespace UE::Geometry;
using namespace UE::MeshFileUtils;

// 基本加载（使用默认设置）
FDynamicMesh3 Mesh;
ELoadOBJStatus Status = LoadOBJ("C:/Models/character.obj", Mesh);

if (Status == ELoadOBJStatus::Success)
{
    UE_LOG(LogTemp, Log, TEXT("Loaded mesh: %d verts, %d tris"),
        Mesh.VertexCount(), Mesh.TriangleCount());
}
else if (Status == ELoadOBJStatus::InvalidPath)
{
    UE_LOG(LogTemp, Error, TEXT("Invalid file path"));
}
```

### 基本用法 — 配置加载选项

```cpp
FLoadOBJSettings Settings;

// OBJ 支持非流形边（一条边属于超过两个三角形），但 FDynamicMesh3 不支持
// true = 非流形三角形作为独立三角形添加（顶点不共享，保证流形性）
// false = 跳过非流形三角形
Settings.bAddSeparatedTriForNonManifold = true;

// 是否反转面朝向（正面/背面翻转）
Settings.bReverseOrientation = true;

// 是否加载法线信息（如果 OBJ 文件中包含）
Settings.bLoadNormals = false;

// 是否加载 UV 信息（如果 OBJ 文件中包含）
Settings.bLoadUVs = false;

FDynamicMesh3 Mesh;
LoadOBJ("/path/to/model.obj", Mesh, Settings);
```

### 基本用法 — 写入 OBJ 文件

```cpp
FWriteOBJSettings WriteSettings;

// 是否反转面朝向
WriteSettings.bReverseOrientation = true;

// true = 尝试写入逐顶点的法线和 UV（更紧凑）
// false = 写入逐元素（per-face-vertex）的值（更精确但文件更大）
WriteSettings.bWritePerVertexValues = true;

// 是否写入逐顶点颜色（需要网格有颜色数据）
WriteSettings.bWritePerVertexColors = false;

FDynamicMesh3 Mesh;
// ... 填充网格数据 ...

bool bOK = WriteOBJ("/path/to/output.obj", Mesh, WriteSettings);
if (bOK)
{
    UE_LOG(LogTemp, Log, TEXT("OBJ written successfully"));
}
```

### 进阶用法 — 加载后处理

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "OBJMeshUtil.h"

using namespace UE::Geometry;
using namespace UE::MeshFileUtils;

// 加载时同时获取法线和 UV
FLoadOBJSettings Settings;
Settings.bLoadNormals = true;
Settings.bLoadUVs = true;
Settings.bReverseOrientation = false;
Settings.bAddSeparatedTriForNonManifold = true;

FDynamicMesh3 Mesh = LoadOBJChecked("/path/to/model.obj", Settings);

// 加载后可以检查属性层
if (Mesh.HasAttributes())
{
    UE_LOG(LogTemp, Log, TEXT("Normal layers: %d"),
        Mesh.Attributes()->NumNormalLayers());
    UE_LOG(LogTemp, Log, TEXT("UV layers: %d"),
        Mesh.Attributes()->NumUVLayers());
}

// 对加载的网格进行进一步处理...
// 例如遍历法线
if (Mesh.HasAttributes() && Mesh.Attributes()->PrimaryNormals())
{
    auto* Normals = Mesh.Attributes()->PrimaryNormals();
    for (int32 ElemID : Normals->ElementIndicesItr())
    {
        FVector3f Normal = Normals->GetElement(ElemID);
    }
}
```

## Demo 示例

```cpp
// OBJRoundTrip.h
#pragma once
#include "CoreMinimal.h"

class FOBJRoundTripDemo
{
public:
    /** 加载 OBJ → 打印信息 → 重新导出 */
    static void Run(const FString& InputPath, const FString& OutputPath);
};
```

```cpp
// OBJRoundTrip.cpp
#include "OBJRoundTrip.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "OBJMeshUtil.h"

using namespace UE::Geometry;
using namespace UE::MeshFileUtils;

void FOBJRoundTripDemo::Run(const FString& InputPath, const FString& OutputPath)
{
    // 转换路径为 char*
    FTCHARToUTF8 InputPathUTF8(*InputPath);
    FTCHARToUTF8 OutputPathUTF8(*OutputPath);

    // 配置：加载法线和 UV，保留原始朝向
    FLoadOBJSettings LoadSettings;
    LoadSettings.bLoadNormals = true;
    LoadSettings.bLoadUVs = true;
    LoadSettings.bReverseOrientation = false;
    LoadSettings.bAddSeparatedTriForNonManifold = true;

    // 加载
    FDynamicMesh3 Mesh;
    ELoadOBJStatus Status = LoadOBJ(InputPathUTF8.Get(), Mesh, LoadSettings);

    if (Status != ELoadOBJStatus::Success)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load OBJ from: %s"), *InputPath);
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("Loaded: %d vertices, %d triangles"),
        Mesh.VertexCount(), Mesh.TriangleCount());

    // 检查属性
    if (Mesh.HasAttributes())
    {
        auto* Normals = Mesh.Attributes()->PrimaryNormals();
        auto* UVs = Mesh.Attributes()->PrimaryUV();
        UE_LOG(LogTemp, Log, TEXT("Has normals: %s, Has UVs: %s"),
            Normals ? TEXT("Yes") : TEXT("No"),
            UVs ? TEXT("Yes") : TEXT("No"));
    }

    // 导出：逐顶点值，保留颜色
    FWriteOBJSettings WriteSettings;
    WriteSettings.bWritePerVertexValues = true;
    WriteSettings.bWritePerVertexColors = true;
    WriteSettings.bReverseOrientation = false;

    bool bExported = WriteOBJ(OutputPathUTF8.Get(), Mesh, WriteSettings);
    if (bExported)
    {
        UE_LOG(LogTemp, Log, TEXT("OBJ exported to: %s"), *OutputPath);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to export OBJ to: %s"), *OutputPath);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DynamicMesh` | FDynamicMesh3 动态网格数据结构 |
| `GeometryAlgorithms` | 几何算法基础设施 |

无特殊外部依赖（仅标准 Core/CoreUObject 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `35f4c4a4` | Fix float overflow warning for arm64 build | 修复 ARM64 构建的浮点溢出警告 |
| 2026-05-15 | `35f66cf1` | Guard against INDEX_NONE / invalid edge id in hole fill util's fill color method | 填孔工具中防护无效边 ID |
| 2026-05-13 | `2c7d172e` | Clamp UV values to max float when invalid value is in returned as double (max double) | UV 值无效时钳制到 max float |
| 2026-05-12 | `64deb517` | Hook up AttributeAwareV2 simplifier in MeshTerrainStaticMeshTransformer | 网格地形变换器中接入属性感知简化器 |
| 2026-05-12 | `68fbe22e` | [SkeletalMeshModelingTools] clamp smooth strength to 0 - 1 | 骨骼网格建模工具平滑强度钳制 |

### 维护评价

- **活跃维护**：作为 GeometryProcessing 插件的一部分，持续收到更新（最近一次提交仅数天前）
- 模块标记为 `DeveloperTool` 且父插件标记为 `IsBetaVersion = true`，API 可能存在变更
- OBJ 读写功能相对稳定，近期更新主要集中在上层算法模块（如属性感知简化器、填孔工具等）
- 该模块代码量较小（2 个头文件），功能聚焦，维护负担低
- **推荐使用**：适合开发阶段的网格 I/O 需求；生产环境中的网格导入建议使用 UE 的标准 FBX/OBJ 导入管线

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryProcessing/Source/MeshFileUtils)
- [GeometryProcessing 插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryProcessing)
- [Geometry Script 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryScript)（蓝图层网格脚本封装）
# GeometryScriptingEditor 模块

> Geometry Scripting plugin 的 Editor 模块，提供仅在编辑器环境中可用的网格资产创建、纹理通道打包、细分曲面以及程序化网格生成 Actor 支持。

| 属性 | 值 |
|---|---|
| 分类 | Runtime（Plugin 分类） |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图函数库、编辑器子系统、Actor 类） |
| 模块 | `GeometryScriptingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-09-12 |
| 年龄标签 | 🏛️ 文物（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryScripting/Source/GeometryScriptingEditor) | |

## 用途

GeometryScriptingEditor 是 GeometryScripting plugin 的编辑器专用模块，补充 `GeometryScriptingCore`（Runtime 模块）在编辑器环境下无法执行的功能。主要职责包括：

1. **资产创建与导出** — 将 `UDynamicMesh` 保存为 StaticMesh / SkeletalMesh / Texture2D / Volume 等持久化资产
2. **纹理通道打包 (Channel Pack)** — 从多张纹理的不同通道组合生成新纹理
3. **细分曲面 (OpenSubdiv)** — 基于 Polygroup 的 Catmull-Clark 和三角形 Loop 细分
4. **Undo/Redo 支持** — 蓝图中对 DynamicMesh 的修改可以正确纳入编辑器事务系统
5. **程序化网格生成 Actor** — `AGeneratedDynamicMeshActor` 与 `UEditorGeometryGenerationSubsystem` 协作，在编辑器中安全地执行耗时的程序化网格生成

## 使用场景

- **蓝图程序化建模**：你在编辑器中用蓝图程序化生成复杂几何体，但 Construction Script 阻塞编辑器 → 使用 `AGeneratedDynamicMeshActor` + `OnRebuildGeneratedMesh` 事件，通过生成子系统调度重建
- **运行时网格导出资产**：DynamicMesh 通过蓝图程序化生成后需要持久化 → 使用 `CreateNewStaticMeshAssetFromMesh` 系列节点
- **纹理处理管线**：需要将多张纹理的 R/G/B/A 通道组合成一张新纹理（如合并 Roughness、Metallic、AO 到单张贴图）→ 使用 `ChannelPack` 节点
- **模型细分**：对基于 Polygroup 的网格执行 Catmull-Clark 或 Loop 细分 → 使用 OpenSubdiv 节点

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create New Static Mesh Asset From Mesh` | 从 DynamicMesh 创建 StaticMesh 资产 | `UGeometryScriptLibrary_CreateNewAssetFunctions` |
| `Create New Static Mesh Asset From Mesh LODs` | 从多个 DynamicMesh LOD 创建 StaticMesh 资产 | `UGeometryScriptLibrary_CreateNewAssetFunctions` |
| `Create New Skeletal Mesh Asset From Mesh` | 从 DynamicMesh + Skeleton 创建 SkeletalMesh 资产 | `UGeometryScriptLibrary_CreateNewAssetFunctions` |
| `Create New Skeletal Mesh Asset From Mesh LODs` | 从多个 LOD DynamicMesh 创建 SkeletalMesh 资产 | `UGeometryScriptLibrary_CreateNewAssetFunctions` |
| `Create New Volume From Mesh` | 从 DynamicMesh 创建 Volume Actor（如 BlockingVolume） | `UGeometryScriptLibrary_CreateNewAssetFunctions` |
| `Create New Texture 2D Asset` | 从纹理复制创建新 Texture2D 资产 | `UGeometryScriptLibrary_CreateNewAssetFunctions` |
| `Create Unique New Asset Path Name` | 生成不冲突的资产路径/名称 | `UGeometryScriptLibrary_CreateNewAssetFunctions` |
| `Channel Pack` | 将多张纹理的指定通道组合为新纹理 | `UGeometryScriptLibrary_EditorTextureMapFunctions` |
| `Apply PolyGroup Catmull Clark SubD` | 基于 Polygroup 执行 Catmull-Clark 细分 | `UGeometryScriptLibrary_OpenSubdivFunctions` |
| `Apply Triangle Loop SubD` | 三角形网格执行 Loop 细分 | `UGeometryScriptLibrary_OpenSubdivFunctions` |
| `Begin Tracked Mesh Change` | 开始跟踪 DynamicMesh 变更（用于 Undo） | `UGeometryScriptLibrary_EditorDynamicMeshFunctions` |
| `Emit Tracked Mesh Change` | 提交已跟踪的 DynamicMesh 变更到 Undo 系统 | `UGeometryScriptLibrary_EditorDynamicMeshFunctions` |
| `Stash Debug Mesh` | 将 DynamicMesh 存储到全局调试存储 | `UGeometryScriptLibrary_EditorDynamicMeshFunctions` |
| `Fetch Debug Mesh` | 从全局调试存储取回 DynamicMesh | `UGeometryScriptLibrary_EditorDynamicMeshFunctions` |
| `Mark For Mesh Rebuild` | 标记 GeneratedDynamicMeshActor 需要重建 | `AGeneratedDynamicMeshActor` |
| `On Rebuild Generated Mesh` | 蓝图可实现事件，执行程序化网格重建 | `AGeneratedDynamicMeshActor` |
| `Increment Progress` | 更新重建进度对话框 | `AGeneratedDynamicMeshActor` |
| `Copy Properties To Static Mesh` | 将属性复制到 StaticMeshActor | `AGeneratedDynamicMeshActor` |
| `Copy Properties From Static Mesh` | 从 StaticMeshActor 复制属性 | `AGeneratedDynamicMeshActor` |

### 使用示例（蓝图描述）

**导出 DynamicMesh 为 StaticMesh 资产**：
1. 构建好 DynamicMesh 后，连接到 `Create New Static Mesh Asset From Mesh` 节点
2. 设置 `AssetPathAndName` 为 `"/Game/MyMeshes/GeneratedMesh"`
3. 配置 Options 结构体（启用 Nanite、碰撞等）
4. Success 引脚连接后续逻辑

**Channel Pack 合并纹理通道**：
1. 准备 4 张源纹理（如 Roughness、Metallic、AO、Height）
2. 分别配置每个 `FGeometryScriptChannelPackSource`，指定 Texture 和 Channel（R/G/B/A）
3. 未连接的通道使用 DefaultValue（默认 255）
4. 连接到 `ChannelPack` 节点，设置 `OutputSRGB`

**程序化网格生成 Actor**：
1. 创建 `AGeneratedDynamicMeshActor` 的蓝图子类
2. 实现 `OnRebuildGeneratedMesh` 事件，在其中构建 DynamicMesh
3. 设置 `bFrozen = false`，Actor 会在编辑器 Tick 中自动调用重建
4. 使用 `Mark For Mesh Rebuild` 手动触发重建

## C++ 用法

### 头文件引入

```cpp
// 资产创建
#include "GeometryScript/CreateNewAssetUtilityFunctions.h"

// 纹理通道打包
#include "GeometryScript/EditorTextureMapFunctions.h"

// OpenSubdiv 细分
#include "GeometryScript/OpenSubdivUtilityFunctions.h"

// 动态网格编辑器工具（Undo/Debug）
#include "GeometryScript/EditorDynamicMeshUtilityFunctions.h"

// 程序化生成 Actor
#include "GeometryActors/GeneratedDynamicMeshActor.h"
#include "GeometryActors/EditorGeometryGenerationSubsystem.h"
```

### 基本用法

**创建 StaticMesh 资产**（来源：`CreateNewAssetUtilityFunctions.cpp`）：

```cpp
UDynamicMesh* MyMesh = /* ... */;
FString AssetPath = TEXT("/Game/MyMeshes/ProceduralMesh");

FGeometryScriptCreateNewStaticMeshAssetOptions Options;
Options.bEnableNanite = true;
Options.bEnableCollision = true;
Options.bEnableRecomputeNormals = true;
Options.bEnableRecomputeTangents = true;

EGeometryScriptOutcomePins Outcome;
UStaticMesh* NewMesh = UGeometryScriptLibrary_CreateNewAssetFunctions::
    CreateNewStaticMeshAssetFromMesh(MyMesh, AssetPath, Options, Outcome);

if (Outcome == EGeometryScriptOutcomePins::Success)
{
    // 资产创建成功，NewMesh 可用于赋值给 StaticMeshComponent
}
```

**Undo/Redo 支持**（来源：`EditorDynamicMeshUtilityFunctions.cpp`）：

```cpp
UDynamicMesh* TargetMesh = /* ... */;

// 在修改网格之前
FDynamicMeshChangeContainer ChangeTracker;
UGeometryScriptLibrary_EditorDynamicMeshFunctions::BeginTrackedMeshChange(
    TargetMesh, ChangeTracker);

// 执行网格修改
TargetMesh->EditMesh([](FDynamicMesh3& Mesh) {
    // ... 修改操作
});

// 提交变更到 Undo 系统（必须在 Transaction 上下文中）
GEditor->BeginTransaction(FText::FromString(TEXT("Modify Mesh")));
UGeometryScriptLibrary_EditorDynamicMeshFunctions::EmitTrackedMeshChange(
    TargetMesh, ChangeTracker);
GEditor->EndTransaction();
```

**OpenSubdiv 细分**（来源：`OpenSubdivUtilityFunctions.cpp`）：

```cpp
UDynamicMesh* TargetMesh = /* ... */;
FGeometryScriptGroupLayer GroupLayer;
GroupLayer.bDefaultLayer = true;

// Catmull-Clark 细分，2 级
UGeometryScriptLibrary_OpenSubdivFunctions::ApplyPolygroupCatmullClarkSubD(
    TargetMesh, 2, GroupLayer);
```

### 进阶用法

**SkeletalMesh 多 LOD 创建**（来源：`CreateNewAssetUtilityFunctions.cpp`）：

```cpp
TArray<UDynamicMesh*> LODMeshes;
LODMeshes.Add(LOD0_Mesh);  // 需要有 SkinWeight 属性
LODMeshes.Add(LOD1_Mesh);

USkeleton* Skeleton = /* ... */;
FString AssetPath = TEXT("/Game/Characters/MySkeletalMesh");

FGeometryScriptCreateNewSkeletalMeshAssetOptions Options;
Options.bEnableRecomputeNormals = true;
Options.bEnableRecomputeTangents = true;
Options.bUseMeshBoneProportions = true;  // 使用网格中存储的骨骼比例
Options.Materials.Add(FName("Body"), BodyMaterial);
Options.Materials.Add(FName("Head"), HeadMaterial);

EGeometryScriptOutcomePins Outcome;
USkeletalMesh* SkeletalMesh =
    UGeometryScriptLibrary_CreateNewAssetFunctions::
        CreateNewSkeletalMeshAssetFromMeshLODs(
            LODMeshes, Skeleton, AssetPath, Options, Outcome);
```

## Demo 示例

### Asset Creation Options 结构体参考

```cpp
// StaticMesh 创建选项
FGeometryScriptCreateNewStaticMeshAssetOptions StaticMeshOptions;
StaticMeshOptions.bEnableRecomputeNormals = false;
StaticMeshOptions.bEnableRecomputeTangents = false;
StaticMeshOptions.bEnableNanite = false;
StaticMeshOptions.NaniteSettings = FMeshNaniteSettings();
StaticMeshOptions.bEnableCollision = true;
StaticMeshOptions.CollisionMode = ECollisionTraceFlag::CTF_UseDefault;
StaticMeshOptions.bUseOriginalVertexOrder = false;

// SkeletalMesh 创建选项
FGeometryScriptCreateNewSkeletalMeshAssetOptions SkelMeshOptions;
SkelMeshOptions.bEnableRecomputeNormals = false;
SkelMeshOptions.bEnableRecomputeTangents = false;
SkelMeshOptions.bUseMeshBoneProportions = false;
SkelMeshOptions.bApplyNaniteSettings = false;
SkelMeshOptions.bUseOriginalVertexOrder = false;

// Channel Pack 来源配置
FGeometryScriptChannelPackSource Source;
Source.Texture = SomeTexture2D;
Source.ReadGammaSpace = EGeometryScriptReadGammaSpace::FromTextureSettings;
Source.Channel = EGeometryScriptRGBAChannel::R;
Source.DefaultValue = 255.0f;  // Texture 为 null 时使用此默认值
```

## 模块依赖

### PublicDependencyModuleNames（你的模块需要依赖这些）

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `PhysicsCore` | 物理核心 |
| `RenderCore` | 渲染核心 |
| `GeometryCore` | 几何算法核心库 |
| `GeometryFramework` | DynamicMesh / DynamicMeshComponent 框架 |
| `DynamicMesh` | FDynamicMesh3 数据结构 |
| `GeometryScriptingCore` | Geometry Script Runtime 核心蓝图函数库 |
| `EditorSubsystem` | 编辑器子系统框架 |

### PrivateDependencyModuleNames（内部使用，不建议直接依赖）

| 模块 | 用途 |
|---|---|
| `Engine` | 引擎核心（Texture、StaticMesh、SkeletalMesh 等） |
| `MeshDescription` / `StaticMeshDescription` | 网格描述转换 |
| `MeshConversion` | 网格格式转换 |
| `GeometryAlgorithms` | 几何算法（细分等） |
| `ModelingOperators` | 建模操作算子 |
| `ModelingComponents` / `ModelingComponentsEditorOnly` | 建模组件 |
| `EditorFramework` / `UnrealEd` | 编辑器框架 |
| `BSPUtils` | BSP/Brush 工具（Volume 创建） |
| `ImageCore` | 图像处理核心 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-08-28 | `3fd4df77cad5` | 资产创建方法中验证新资产路径有效性 | 安全性增强：在创建资产前检查路径格式是否合法，避免运行时崩溃 |
| 2025-07-10 | `9803c443cfab` | 添加 UE_INLINE_GENERATED_CPP_BY_NAME | 代码质量改进：优化编译时间，减少冗余 .gen.cpp 文件生成 |
| 2025-05-30 | `2739c3d30ebc` | 更新头文件 DLL 导出声明 | 代码规范改进：确保 dllexport/dllimport 在方法/静态变量上而非类型上 |

### 维护评价

- **活跃程度**: 活跃维护。2025 年有多次实质性更新，包含安全增强、代码质量改进和功能完善
- **代码质量**: 代码结构清晰，职责分明（每个子功能一个 .h/.cpp 对），错误处理完善（使用 AppendError 系统）
- **注意点**:
  - Editor-only 模块，不可在打包运行时使用
  - ChannelPack 和资产创建功能需要 WITH_EDITOR 宏
  - OpenSubdiv 细分有硬限制（最多 6 级），防止内存爆炸
  - `NaniteProxyTrianglePercent` 属性已标记为 Deprecated，应使用 `NaniteSettings` 替代
- **推荐使用**: ✅ 推荐。作为 Geometry Scripting 的编辑器扩展，功能完善且持续维护

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryScripting/Source/GeometryScriptingEditor)
- [父模块 GeometryScriptingCore](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryScripting/Source/GeometryScriptingCore)
- [Plugin 根目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryScripting)

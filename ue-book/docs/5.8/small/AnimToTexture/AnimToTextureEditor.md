# AnimToTexture

> Converts SkeletalMesh Animations into Textures

| 属性 | 值 |
|---|---|
| 中文名 | 动画烘焙纹理 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `AnimToTexture` (Runtime), `AnimToTextureEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-03-09 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AnimToTexture) | |

## 用途

AnimToTexture 将骨骼网格体（SkeletalMesh）的动画数据烘焙到纹理中，生成顶点动画纹理（Vertex Animation Texture, VAT）。它支持两种模式：

1. **顶点模式（Vertex）**：烘焙每个动画帧的顶点位置偏移和法线，存储在纹理中
2. **骨骼模式（Bone）**：烘焙骨骼的位置和旋转数据，存储在纹理中

核心解决的问题是**大规模角色动画的性能瓶颈**。传统骨骼动画需要 GPU 对每个实例进行蒙皮计算，当场景中有成百上千个动画角色时，GPU 压力巨大。VAT 方案将动画预烘焙为纹理，运行时只需在顶点着色器中采样纹理即可还原动画姿态，将骨骼动画的开销转换为简单的纹理采样，极大降低批量渲染的性能消耗。

## 使用场景

- 你需要渲染大量带动画的角色（如 RTS 游戏的成千上万个士兵），且对性能要求苛刻 → 用 AnimToTexture 将动画烘焙为纹理
- 你在做开放世界游戏，远景有大量 NPC 走动但不需要骨骼精度 → 用 VAT 降低远景角色的 GPU 开销
- 你需要在 Niagara 粒子系统中驱动大量网格体动画 → 用烘焙后的静态网格体 + 纹理采样替代骨骼组件
- 你的项目中存在大量重复播放相同动画的角色实例 → 只需一份纹理数据即可驱动所有实例

## 蓝图用法

### 核心节点

所有蓝图节点均来自 `UAnimToTextureBPLibrary`，且仅在编辑器环境下可用（`WITH_EDITOR`）。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AnimationToTexture` | 将 DataAsset 中配置的动画数据烘焙为纹理，返回是否成功 | `UAnimToTextureBPLibrary` |
| `ConvertSkeletalMeshToStaticMesh` | 将骨骼网格体转换为静态网格体（指定 LOD 层级） | `UAnimToTextureBPLibrary` |
| `SetLightMapIndex` | 设置静态网格体的光照贴图 UV 通道索引 | `UAnimToTextureBPLibrary` |
| `UpdateMaterialInstanceFromDataAsset` | 根据 DataAsset 更新材质实例参数（纹理、边界盒等） | `UAnimToTextureBPLibrary` |

### 使用示例

完整的烘焙工作流如下：

1. **创建 DataAsset**：在内容浏览器中右键创建 `AnimToTextureDataAsset`，配置骨骼网格体源、动画序列列表、精度模式（8bit/16bit）等参数

2. **转换静态网格体**：调用 `ConvertSkeletalMeshToStaticMesh` 将原始骨骼网格体转为静态网格体。这会生成一个用于最终渲染的静态版本

3. **设置光照贴图**：对生成的静态网格体调用 `SetLightMapIndex`，指定 UV 通道并生成光照贴图 UV

4. **烘焙动画纹理**：调用 `AnimationToTexture` 传入配置好的 DataAsset。此操作会生成顶点偏移纹理、法线纹理（以及可选的蒙皮权重纹理），写回到 DataAsset 关联的纹理资产中

5. **更新材质**：调用 `UpdateMaterialInstanceFromDataAsset` 将烘焙好的纹理和参数自动设置到材质实例中

6. **运行时播放**：在场景中放置静态网格体组件，应用上述材质实例。材质中的顶点着色器会根据时间参数采样 VAT 纹理，还原动画姿态

## C++ 用法

### 头文件引入

```cpp
#include "AnimToTextureBPLibrary.h"
```

### 基本用法

将骨骼动画烘焙为纹理，基于 `AnimToTextureBPLibrary.h` 中的蓝图函数。

```cpp
// 确保在编辑器环境下使用（WITH_EDITOR）
#if WITH_EDITOR
#include "AnimToTextureBPLibrary.h"
#include "AnimToTextureDataAsset.h"

void BakeAnimationToTexture(UAnimToTextureDataAsset* DataAsset)
{
    // 步骤 1: 将骨骼网格体转换为静态网格体
    UStaticMesh* StaticMesh = UAnimToTextureBPLibrary::ConvertSkeletalMeshToStaticMesh(
        DataAsset->SkeletalMesh,              // 源骨骼网格体
        TEXT("/Game/Meshes/SM_Character"),     // 输出包路径
        0                                      // LOD 层级
    );

    // 步骤 2: 设置光照贴图 UV 通道
    UAnimToTextureBPLibrary::SetLightMapIndex(
        StaticMesh,
        0,    // LODIndex
        1,    // LightmapIndex（UV 通道）
        true  // 是否自动生成光照贴图 UV
    );

    // 步骤 3: 执行烘焙
    bool bSuccess = UAnimToTextureBPLibrary::AnimationToTexture(DataAsset);

    if (bSuccess)
    {
        // 步骤 4: 更新材质实例参数
        UAnimToTextureBPLibrary::UpdateMaterialInstanceFromDataAsset(
            DataAsset,
            MaterialInstance,
            EMaterialParameterAssociation::GlobalParameter
        );
    }
}
#endif
```

### 进阶用法

使用私有命名空间中的工具函数进行底层网格操作（非公开 API，可能随版本变化）：

```cpp
#include "AnimToTextureSkeletalMesh.h"
#include "AnimToTextureMeshMapping.h"

using namespace AnimToTexture_Private;

void CustomMeshProcessing()
{
    USkeletalMesh* SkeletalMesh = /* ... */;
    UStaticMesh* StaticMesh = /* ... */;

    // 获取静态网格体顶点位置和法线
    TArray<FVector3f> SourcePositions, SourceNormals;
    GetVertices(StaticMesh, /*LODIndex=*/0, SourcePositions, SourceNormals);

    // 获取骨骼网格体参考姿态顶点
    TArray<FVector3f> RefPositions;
    GetVertices(SkeletalMesh, /*LODIndex=*/0, RefPositions);

    // 获取骨骼蒙皮权重
    TArray<VertexSkinWeightMax> SkinWeights;
    GetSkinWeights(SkeletalMesh, /*LODIndex=*/0, SkinWeights);

    // 将最大影响力数减少到 4（用于纹理存储）
    TArray<VertexSkinWeightFour> ReducedWeights;
    ReduceSkinWeights(SkinWeights, ReducedWeights);

    // 创建静态网格体与骨骼网格体之间的映射关系
    // 用于将骨骼动画数据投影到静态网格体上
    FSourceMeshToDriverMesh MeshMapping;
    MeshMapping.Update(
        StaticMesh, 0,    // 源网格体（静态），LOD
        SkeletalMesh, 0,  // 驱动网格体（骨骼），LOD
        4,                 // 最大驱动三角形数
        1.0f               // 反距离权重 Sigma
    );

    // 获取源网格体顶点数
    int32 NumSourceVertices = MeshMapping.GetNumSourceVertices();

    // 使用驱动三角形数据变形源网格体顶点
    TArray<FVector3f> DriverVertices;  // 来自 CPU 蒙皮的驱动网格体顶点
    TArray<FVector3f> DeformedVertices, DeformedNormals;
    MeshMapping.DeformVerticesAndNormals(DriverVertices, DeformedVertices, DeformedNormals);

    // 投影蒙皮权重到静态网格体
    TArray<VertexSkinWeightMax> ProjectedWeights;
    MeshMapping.ProjectSkinWeights(ProjectedWeights);
}
```

## Demo 示例

一个完整的最小示例，展示如何通过 C++ 将动画烘焙为纹理：

```cpp
// AnimToTextureDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "AnimToTextureDemo.generated.h"

class UAnimToTextureDataAsset;
class UStaticMesh;
class UMaterialInstanceConstant;

UCLASS()
class UAnimToTextureDemoSubsystem : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    /**
     * 演示完整的动画烘焙流程
     * @param DataAsset 已配置好的 AnimToTexture 数据资产
     * @param OutputStaticMeshPath 输出静态网格体的包路径
     * @param MaterialInstance 要更新的材质实例
     * @return 烘焙是否成功
     */
    UFUNCTION(BlueprintCallable, Category = "Demo")
    bool RunBakeDemo(
        UAnimToTextureDataAsset* DataAsset,
        const FString& OutputStaticMeshPath,
        UMaterialInstanceConstant* MaterialInstance
    );
};
```

```cpp
// AnimToTextureDemo.cpp
#include "AnimToTextureDemo.h"
#include "AnimToTextureBPLibrary.h"
#include "AnimToTextureDataAsset.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInstanceConstant.h"

bool UAnimToTextureDemoSubsystem::RunBakeDemo(
    UAnimToTextureDataAsset* DataAsset,
    const FString& OutputStaticMeshPath,
    UMaterialInstanceConstant* MaterialInstance)
{
#if WITH_EDITOR
    if (!DataAsset || !DataAsset->SkeletalMesh)
    {
        UE_LOG(LogTemp, Error, TEXT("DataAsset 或 SkeletalMesh 为空"));
        return false;
    }

    // 1. 将骨骼网格体转换为静态网格体
    UStaticMesh* StaticMesh = UAnimToTextureBPLibrary::ConvertSkeletalMeshToStaticMesh(
        DataAsset->SkeletalMesh,
        OutputStaticMeshPath,
        0  // LOD 0
    );

    if (!StaticMesh)
    {
        UE_LOG(LogTemp, Error, TEXT("转换静态网格体失败"));
        return false;
    }

    // 2. 设置光照贴图
    UAnimToTextureBPLibrary::SetLightMapIndex(StaticMesh, 0, 1, true);

    // 3. 烘焙动画到纹理
    bool bSuccess = UAnimToTextureBPLibrary::AnimationToTexture(DataAsset);
    if (!bSuccess)
    {
        UE_LOG(LogTemp, Error, TEXT("动画烘焙失败"));
        return false;
    }

    // 4. 更新材质实例参数
    if (MaterialInstance)
    {
        UAnimToTextureBPLibrary::UpdateMaterialInstanceFromDataAsset(
            DataAsset,
            MaterialInstance,
            EMaterialParameterAssociation::GlobalParameter
        );
    }

    UE_LOG(LogTemp, Log, TEXT("动画烘焙完成"));
    return true;

#else
    UE_LOG(LogTemp, Warning, TEXT("AnimToTexture 仅在编辑器环境下可用"));
    return false;
#endif
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RenderCore` | 纹理平台数据（FTexturePlatformData）操作 |
| `MeshDescription` | 网格体描述数据处理（骨骼到静态转换） |
| `AssetDefinition` | 编辑器中资产定义（图标、分类显示） |
| `ToolWidgets` | 编辑器工具界面组件 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新的 UE_LOGF 格式 |
| 2025-10-07 | `dcc26116` | Fixed up plugins that have both Base and Default ini files... | 修复插件配置文件重复问题 |
| 2025-08-08 | `7213adb2` | [AnimToTexture] Added SkeletalMesh MeshDescription functions. (not used) | 新增 MeshDescription 相关函数（暂未启用） |
| 2025-08-07 | `1aee06f6` | [AnimToTexture] Fixed Baking RigidBodies | 修复刚体动画烘焙问题 |
| 2025-08-06 | `785cdd6d` | Fixup API macro usage | 修正 API 导出宏用法 |

### 维护评价

**评级：活跃维护中**

- 📅 **创建时间**：2023 年 3 月，约 3 年历史
- 🔄 **更新频率**：2025 年 8 月有密集的功能修复和改进（3 次 commit），2026 年 4 月仍有代码维护更新，保持活跃
- ⚠️ **实验性状态**：`IsExperimentalVersion=true`，尚未毕业为正式插件
- 🚫 **默认未启用**：`Installed=false`，需要手动在插件管理器中启用
- ✅ **推荐使用**：如果你的项目需要大规模动画角色的性能优化，该插件是 UE5 内置的官方 VAT 解决方案，功能完整且持续维护。但需注意其**实验性**状态，API 可能在未来版本中发生变化
- 📌 **注意**：私有命名空间 `AnimToTexture_Private` 中的工具函数（如 `FSourceMeshToDriverMesh`）不属于公开 API，升级引擎版本时可能出现不兼容

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AnimToTexture)
- [AnimToTextureDataAsset 定义](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/AnimToTexture/Source/AnimToTexture/Public/AnimToTextureDataAsset.h)（Runtime 模块中的数据资产定义）
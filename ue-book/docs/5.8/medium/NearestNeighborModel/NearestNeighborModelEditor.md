# ML Deformer Nearest Neighbor Model (DEPRECATED)

> Nearest Neighbor Model for the ML Deformer Framework. This model has been deprecated. Please use the Detail Pose Model instead.

| 属性 | 值 |
|---|---|
| 中文名 | 近邻模型（已废弃） |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `NearestNeighborModel` (Runtime), `NearestNeighborModelEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-17 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/NearestNeighborModel) | |

> ⚠️ **此插件已废弃（DEPRECATED）**。请使用 **Detail Pose Model** 替代。以下文档仅供参考历史实现。

## 用途

该插件为 ML Deformer 框架提供**最近邻变形模型**。核心思想是：在训练阶段对动画姿态进行 K-Means 聚类，为每个分区（Section）找到一组代表性姿态及其对应的几何缓存偏移；在运行时，对当前骨骼姿态查找最近邻的姿态簇，并将对应的 Morph Delta 混合应用到蒙皮网格上，从而实现机器学习驱动的高质量变形补偿。

该模型将网格顶点划分为多个 Section，每个 Section 独立管理顶点映射和最近邻数据，支持 GPU 加速的查找与混合。

由于版本 0.3 且已被官方标记为废弃，**新项目不应使用此模型**，应改用 Detail Pose Model。

## 使用场景

- 你使用 ML Deformer 框架对角色进行变形校正，并希望通过聚类代表性姿态来压缩/优化变形数据 → 原本使用本插件，现请改用 Detail Pose Model
- 你需要将复杂动画的变形误差分解为多个网格区域（Section），各自独立训练和推理 → 本插件的分区机制可作为参考
- 你在研究 UE5 ML Deformer 的演进历史，需要了解近邻模型的实现方式 → 本插件的源码仍有学习价值

## 蓝图用法

### 训练模型节点（Python 蓝图事件）

本插件的训练逻辑通过 `UNearestNeighborTrainingModel` 暴露为 BlueprintImplementableEvent，实际由 Python 脚本实现。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Train` | 触发训练流程（由 Python 实现） | `UNearestNeighborTrainingModel` |
| `UpdateNearestNeighborData` | 更新最近邻数据（由 Python 实现） | `UNearestNeighborTrainingModel` |
| `KmeansClusterPoses` | 对姿态执行 K-Means 聚类（由 Python 实现） | `UNearestNeighborTrainingModel` |
| `GetNeighborStats` | 获取最近邻统计信息（由 Python 实现） | `UNearestNeighborTrainingModel` |

### 采样工具节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCustomSamplerData` | 设置自定义采样器的动画和几何缓存 | `UNearestNeighborTrainingModel` |
| `CustomSample` | 在指定帧执行自定义采样 | `UNearestNeighborTrainingModel` |
| `SetCustomSamplerDataFromSection` | 从指定 Section 设置采样数据 | `UNearestNeighborTrainingModel` |
| `CreateModelInstance` | 创建模型实例用于推理测试 | `UNearestNeighborTrainingModel` |
| `DestroyModelInstance` | 销毁模型实例 | `UNearestNeighborTrainingModel` |
| `GetUnskinnedVertexPositions` | 获取未蒙皮顶点位置 | `UNearestNeighborTrainingModel` |
| `GetMeshIndexBuffer` | 获取网格索引缓冲区 | `UNearestNeighborTrainingModel` |

### 动画/几何缓存流工具

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Init` | 初始化动画流（需要传入 Skeleton） | `UNearestNeighborAnimStream` |
| `AppendFrames` | 追加指定帧的动画数据 | `UNearestNeighborAnimStream` |
| `ToAnim` | 将流数据导出为 AnimSequence | `UNearestNeighborAnimStream` |
| `Init` | 初始化几何缓存流（需要模板 Cache） | `UNearestNeighborGeometryCacheStream` |
| `AppendFrames` | 追加指定帧的几何缓存数据 | `UNearestNeighborGeometryCacheStream` |
| `ToGeometryCache` | 将流数据导出为 GeometryCache | `UNearestNeighborGeometryCacheStream` |

### 使用示例（蓝图描述）

**自定义采样流程：**
1. 创建 `UNearestNeighborTrainingModel` 实例
2. 调用 `SetCustomSamplerData`，传入目标 `UAnimSequence` 和可选的 `UGeometryCache`
3. 循环调用 `CustomSample(FrameIndex)` 逐帧采样
4. 采样数据存储在 `CustomSamplerBoneRotations` 和 `CustomSamplerDeltas` 属性中，供 Python 训练脚本读取

**K-Means 聚类流程：**
1. 创建 `UNearestNeighborKMeansData` 对象
2. 设置 `NearestNeighborModelAsset`、`SectionIndex`、`NumClusters`（聚类数，至少为 1）
3. 在 `Inputs` 数组中添加 `FNearestNeighborKMeansInputData`，每个条目包含一个 `UAnimSequence` 和可选的 `UGeometryCache`
4. 可选：勾选 `bExtractGeometryCache` 以同时提取几何缓存
5. 调用 `KmeansClusterPoses(KMeansData)`，结果输出到 `ExtractedPoses` 和 `ExtractedCache`

## C++ 用法

### 头文件引入

```cpp
#include "NearestNeighborTrainingModel.h"
#include "NearestNeighborEditorHelpers.h"
#include "NearestNeighborGeomCacheSampler.h"
```

### 基本用法

使用动画流收集多段动画的关键帧数据：

```cpp
// 来源: Public/NearestNeighborEditorHelpers.h - UNearestNeighborAnimStream

UNearestNeighborAnimStream* AnimStream = NewObject<UNearestNeighborAnimStream>();
AnimStream->Init(Skeleton);  // 初始化，传入 USkeleton

// 从多个动画中追加关键帧
AnimStream->AppendFrames(RunAnim, {0, 5, 10, 15, 20});
AnimStream->AppendFrames(WalkAnim, {0, 3, 6, 9, 12});

// 导出为单个 AnimSequence
UAnimSequence* CombinedAnim = NewObject<UAnimSequence>();
AnimStream->ToAnim(CombinedAnim);

if (AnimStream->IsValid())
{
    // 确认数据有效后可进行后续处理
}
```

### 进阶用法

自定义采样器用于手动提取骨骼旋转和变形增量：

```cpp
// 来源: Public/NearestNeighborTrainingModel.h - UNearestNeighborTrainingModel
// 来源: Public/NearestNeighborGeomCacheSampler.h - FNearestNeighborGeomCacheSampler

// 方式一：通过 TrainingModel 的蓝图可调用接口
UNearestNeighborTrainingModel* TrainingModel = GetTrainingModel();
TrainingModel->SetCustomSamplerData(TargetAnimSequence, OptionalGeometryCache);

for (int32 Frame = 0; Frame < NumFrames; ++Frame)
{
    TrainingModel->CustomSample(Frame);
    // 此时 CustomSamplerBoneRotations 和 CustomSamplerDeltas 已更新
}

// 方式二：通过采样器直接操作（C++ 层级）
FNearestNeighborGeomCacheSampler Sampler;
Sampler.Customize(TargetAnimSequence, OptionalGeometryCache);

bool bSuccess = Sampler.CustomSample(0);
TArray<uint32> IndexBuffer = Sampler.GetMeshIndexBuffer();
```

获取骨骼网格的索引缓冲区和未蒙皮顶点位置：

```cpp
// 来源: Public/NearestNeighborTrainingModel.h
TArray<uint32> IndexBuffer = Sampler.GetMeshIndexBuffer();

// 通过 TrainingModel 获取
TArray<float> UnskinnedPositions = TrainingModel->GetUnskinnedVertexPositions();
// 返回展平的 float 数组，每 3 个 float 代表一个顶点的 XYZ
```

创建和销毁模型实例（用于推理验证）：

```cpp
// 来源: Public/NearestNeighborTrainingModel.h
UNearestNeighborModelInstance* Instance = TrainingModel->CreateModelInstance();
// ... 使用 Instance 进行推理测试 ...
TrainingModel->DestroyModelInstance(Instance);
```

## Demo 示例

以下示例展示如何使用动画流工具收集帧数据并导出：

```cpp
// NearestNeighborDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NearestNeighborDemo.generated.h"

class UNearestNeighborAnimStream;
class UAnimSequence;
class USkeleton;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UNearestNeighborDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void CollectAnimationFrames();

private:
    TWeakObjectPtr<UNearestNeighborAnimStream> AnimStream;
};
```

```cpp
// NearestNeighborDemo.cpp
#include "NearestNeighborDemo.h"
#include "NearestNeighborEditorHelpers.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"

void UNearestNeighborDemoComponent::CollectAnimationFrames()
{
    AnimStream = NewObject<UNearestNeighborAnimStream>(this);

    USkeleton* Skeleton = /* 获取目标 Skeleton */;
    if (!Skeleton)
    {
        return;
    }

    AnimStream->Init(Skeleton);

    // 收集多段动画的帧
    UAnimSequence* IdleAnim = /* 加载或引用 Idle 动画 */;
    UAnimSequence* WalkAnim = /* 加载或引用 Walk 动画 */;

    if (IdleAnim && AnimStream->IsValid())
    {
        AnimStream->AppendFrames(IdleAnim, {0, 15, 30, 45});
    }
    if (WalkAnim && AnimStream->IsValid())
    {
        AnimStream->AppendFrames(WalkAnim, {0, 10, 20, 30, 40});
    }

    // 导出合并后的动画
    UAnimSequence* OutputAnim = NewObject<UAnimSequence>();
    if (AnimStream->ToAnim(OutputAnim))
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully exported %d frames to AnimSequence"), 
               OutputAnim->GetNumberOfSampledKeys());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MLDeformer` | ML Deformer 框架基类和接口 |
| `MLDeformerEditor` | ML Deformer 编辑器工具（详情自定义、编辑器模型等） |
| `GeometryCache` | 几何缓存资产支持 |
| `RenderCore` | 渲染核心（顶点缓冲区、蒙皮权重等） |
| `GeometryFramework` | 几何框架（Actor 和组件） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `1d7ad320` | UE 5.8 Animation deprecation clean up (CL 8/10): MLDeformer | UE 5.8 动画废弃清理，MLDeformer 相关代码清理 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 格式化日志宏 |
| 2026-04-02 | `138d5376` | [Deformer Graph] Multiple fixes for Optimus runtime | Deformer Graph 运行时多项修复 |
| 2026-03-26 | `1bbb77b5` | Optimization to avoid creating duplicate section buffers in Optimus. | 优化避免在 Optimus 中创建重复的 Section 缓冲区 |
| 2025-10-07 | `746137a4` | Resubmitted "Refactored skinned mesh system to enable GPU skin support for skinned meshes... | 重新提交蒙皮网格系统重构以支持 GPU 蒙皮 |

### 维护评价

⚠️ **此插件已被官方废弃，不推荐使用。**

- **创建时间**：2022 年 9 月，作为 ML Deformer 框架的早期实验性模型
- **废弃状态**：`.uplugin` 的 `FriendlyName` 和 `Description` 均明确标注 `DEPRECATED`，官方建议使用 **Detail Pose Model** 替代
- **版本号 0.3**：从未达到正式 1.0 版本，说明该模型在成熟前即被更好的方案取代
- **近期更新**：2026 年的更新仅涉及代码清理（deprecation clean up、日志迁移、构建修复），无功能性更新
- **替代方案**：**Detail Pose Model** 提供了更优的变形精度和性能，是该插件的直接继任者

**建议**：新项目不应使用此插件。已有使用该插件的项目应计划迁移到 Detail Pose Model。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/NearestNeighborModel)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)（ML Deformer 框架通用文档）
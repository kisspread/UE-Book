# Pose Search

> Framework for indexing and searching pose features. Used in techniques such as Motion Matching.

| 属性 | 值 |
|---|---|
| 中文名 | 姿态搜索 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产、蓝图接口） |
| 模块 | `PoseSearch` (Runtime), `PoseSearchEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-06-16 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PoseSearch) | |

## 用途

PoseSearch 是 UE5 的 **Motion Matching（运动匹配）** 核心框架。它解决的问题是：在大量动画数据库中，根据角色当前的姿态历史和运动轨迹，实时搜索出最匹配的动画片段并播放。

传统动画系统需要手工编写状态机或混合树来管理动画过渡，而 Motion Matching 通过离线索引动画数据、运行时构建查询向量、搜索最近匹配姿态的方式，自动选择最佳动画。这使得角色动画更加自然流畅，大幅减少动画师的手动过渡工作。

该插件包含以下核心能力：

- **姿态索引与搜索**：将动画数据离线索引为特征向量，运行时通过 PCA-KDTree 或暴力搜索找到最近匹配
- **特征通道系统**：可配置的特征提取（骨骼位置/速度/朝向、轨迹、曲线等）
- **轨迹预测**：基于角色移动意图生成未来轨迹，用于查询构建
- **多人交互匹配**：（实验性）支持多个角色间的协调动画搜索
- **Chooser 集成**：与 Chooser 系统集成，支持条件化动画选择

## 使用场景

- 你正在制作 3D 角色的流畅运动系统（跑步、行走、冲刺等）→ 用 PoseSearch + Motion Matching 节点
- 你有一个包含数百条动画的移动数据库，希望系统自动选择最匹配的动画 → 创建 PoseSearchDatabase + PoseSearchSchema
- 你需要角色根据实际移动速度自动调整动画播放速率 → Motion Matching 的 PlayRate 范围设置
- 你想要两个角色做交互动画（如握手、格斗）→ 使用 PoseSearchInteractionLibrary（实验性）
- 你需要自定义匹配特征（如脚部着地时间、特定骨骼位置）→ 自定义 UPoseSearchFeatureChannel 子类

## 蓝图用法

### 核心节点

#### Motion Matching 搜索

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MotionMatch` | 执行运动匹配搜索，返回最佳动画结果 | `UPoseSearchLibrary` |
| `GetMotionMatchingSearchResult` | 从 Motion Matching 节点获取当前搜索结果 | `UMotionMatchingAnimNodeLibrary` |
| `GetMotionMatchingBlendSettings` | 获取当前混合设置 | `UMotionMatchingAnimNodeLibrary` |
| `OverrideMotionMatchingBlendSettings` | 覆盖混合设置（如混合时间、曲线类型） | `UMotionMatchingAnimNodeLibrary` |
| `SetDatabaseToSearch` | 运行时切换搜索数据库 | `UMotionMatchingAnimNodeLibrary` |
| `SetDatabasesToSearch` | 运行时设置多个搜索数据库 | `UMotionMatchingAnimNodeLibrary` |
| `SetInterruptMode` | 控制当前动画是否被打断 | `UMotionMatchingAnimNodeLibrary` |

#### 轨迹生成

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PoseSearchGenerateTransformTrajectory` | 为角色生成运动匹配轨迹（历史+预测） | `UPoseSearchTrajectoryLibrary` |
| `PoseSearchGenerateWarpedTransformTrajectory` | 生成带 Motion Warping 的轨迹（实验性） | `UPoseSearchTrajectoryLibrary` |
| `HandleTransformTrajectoryWorldCollisions` | 处理轨迹的世界碰撞（重力+地面检测） | `UPoseSearchTrajectoryLibrary` |
| `GetTransformTrajectorySampleAtTime` | 获取轨迹上指定时间点的采样 | `UPoseSearchTrajectoryLibrary` |
| `GetTransformTrajectoryVelocity` | 获取轨迹上两点间的速度 | `UPoseSearchTrajectoryLibrary` |

#### 姿态历史

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPoseHistoryNodeTransformTrajectory` | 获取姿态历史节点的轨迹 | `UPoseSearchHistoryCollectorAnimNodeLibrary` |
| `SetPoseHistoryNodeTransformTrajectory` | 设置姿态历史节点的轨迹 | `UPoseSearchHistoryCollectorAnimNodeLibrary` |
| `GetPoseHistoryBoneWorldTransform` | 获取历史中某骨骼在指定时间的世界变换 | `UPoseSearchHistoryCollectorAnimNodeLibrary` |

#### 资产采样

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SamplePose` | 从动画资产中采样姿态（蓝图线程安全） | `UPoseSearchAssetSamplerLibrary` |
| `GetTransformByName` | 从采样姿态中按骨骼名获取变换 | `UPoseSearchAssetSamplerLibrary` |
| `Draw` | 调试绘制采样姿态 | `UPoseSearchAssetSamplerLibrary` |

#### 多人交互（实验性）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MotionMatchInteraction` | 执行多人交互运动匹配 | `UPoseSearchInteractionLibrary` |
| `MotionMatchMulti` | 执行多角色间的全组合运动匹配搜索 | `UPoseSearchInteractionLibrary` |
| `CalculateFullAlignedTransforms` | 计算交互对齐后的完整变换 | `UPoseSearchInteractionLibrary` |

### 使用示例（蓝图描述）

**基本 Motion Matching 设置：**

1. 在动画蓝图中添加 **Pose Search History Collector** 节点（在 Movement 链之前），配置骨骼收集列表和采样间隔
2. 添加 **Motion Matching** 节点，引用你创建的 `UPoseSearchDatabase` 资产
3. 在 History Collector 节点的 **Trajectory** 输入引脚连接你的轨迹数据
4. 调整 Motion Matching 节点的参数：BlendTime（混合时间）、PoseJumpThresholdTime（跳转阈值）、PlayRate（播放速率范围）
5. 如果需要使用惯性混合，在 Motion Matching 节点后添加 **Inertialization** 节点

**运行时切换数据库：**

1. 获取动画蓝图中的 Motion Matching 节点引用（通过 Anim Node Reference）
2. 调用 `ConvertToMotionMatchingNode` 转换节点引用
3. 调用 `SetDatabaseToSearch` 或 `SetDatabasesToSearch` 替换搜索目标
4. 设置 `InterruptMode` 为 `ForceInterrupt` 立即中断当前动画

**轨迹生成（角色类型）：**

1. 创建一个 `FPoseSearchTrajectoryData` 资产配置轨迹参数（转弯速度、最大控制器偏航率等）
2. 每帧调用 `PoseSearchGenerateTransformTrajectory`，传入 AnimInstance、轨迹数据、DeltaTime
3. 输出的 `FTransformTrajectory` 连接到 Pose History Collector 节点

## C++ 用法

### 头文件引入

```cpp
#include "PoseSearch/PoseSearchLibrary.h"
#include "PoseSearch/PoseSearchDatabase.h"
#include "PoseSearch/PoseSearchSchema.h"
#include "PoseSearch/AnimNode_MotionMatching.h"
#include "PoseSearch/PoseSearchTrajectoryLibrary.h"
```

### 基本用法

**Motion Matching 搜索（蓝图 API）**：

来源：`Public/PoseSearch/PoseSearchLibrary.h`

```cpp
// 在动画蓝图或任何蓝图可调用的地方执行运动匹配
UAnimInstance* AnimInstance = /* 获取动画实例 */;
TArray<UObject*> AssetsToSearch = { MyDatabase };
FName PoseHistoryName = TEXT("PoseHistory");

FPoseSearchContinuingProperties ContinuingProperties;
ContinuingProperties.PlayingAsset = CurrentAnimAsset;
ContinuingProperties.PlayingAssetAccumulatedTime = CurrentTime;
ContinuingProperties.bIsPlayingAssetMirrored = bIsMirrored;
ContinuingProperties.InterruptMode = EPoseSearchInterruptMode::DoNotInterrupt;

FPoseSearchFutureProperties Future;
Future.Animation = nullptr;
Future.AnimationTime = 0.f;
Future.IntervalTime = 0.f;

FPoseSearchBlueprintResult Result;
UPoseSearchLibrary::MotionMatch(AnimInstance, AssetsToSearch, PoseHistoryName, ContinuingProperties, Future, Result);

// 使用结果
if (Result.SelectedAnim)
{
    // 播放 Result.SelectedAnim 在 Result.SelectedTime 时间点
    // 使用 Result.WantedPlayRate 作为播放速率
    // 检查 Result.bLoop 和 Result.bIsMirrored
}
```

**C++ 级别运动匹配搜索**：

来源：`Public/PoseSearch/PoseSearchLibrary.h`

```cpp
// 高级 C++ API：多角色、多上下文搜索
TArray<const UObject*> AnimContexts = { AnimInstance1, AnimInstance2 };
TArray<UE::PoseSearch::FRole> Roles = { UE::PoseSearch::DefaultRole, TEXT("SecondaryRole") };
TArray<const UE::PoseSearch::IPoseHistory*> PoseHistories = { PoseHistory1, PoseHistory2 };
TArray<const UObject*> AssetsToSearch = { Database };

UE::PoseSearch::FSearchResult SearchResult = UPoseSearchLibrary::MotionMatch(
    AnimContexts,
    Roles,
    PoseHistories,
    AssetsToSearch,
    ContinuingProperties,
    Future,
    EventToSearch
);
```

### 进阶用法

**创建和配置 PoseSearchDatabase**：

来源：`Public/PoseSearch/PoseSearchDatabase.h`

```cpp
// 在编辑器中创建数据库资产，C++ 中可程序化添加动画资产
UPoseSearchDatabase* Database = NewObject<UPoseSearchDatabase>();
Database->Schema = MySchema;
Database->ContinuingPoseCostBias = -0.01f;  // 降低继续播放当前动画的成本
Database->BaseCostBias = 0.f;
Database->LoopingCostBias = -0.005f;       // 稍微倾向选择循环动画

// 添加动画资产到数据库
FPoseSearchDatabaseAnimationAsset AssetEntry;
AssetEntry.AnimAsset = MyAnimSequence;
AssetEntry.bEnabled = true;
AssetEntry.bDisableReselection = false;
AssetEntry.MirrorOption = EPoseSearchMirrorOption::UnmirroredAndMirrored;
AssetEntry.SamplingRange = FFloatInterval(0.f, 0.f); // 完整帧范围
```

**轨迹生成系统**：

来源：`Public/PoseSearch/PoseSearchTrajectoryLibrary.h`

```cpp
// 初始化轨迹
FPoseSearchTrajectoryData::FSampling Sampling;
Sampling.NumHistorySamples = 10;
Sampling.SecondsPerHistorySample = 0.04f;
Sampling.NumPredictionSamples = 8;
Sampling.SecondsPerPredictionSample = 0.2f;

FTransformTrajectory Trajectory;
UPoseSearchTrajectoryLibrary::InitTrajectorySamples(Trajectory, DefaultPosition, DefaultFacing, Sampling, DeltaTime);

// 每帧更新历史（基于角色移动意图）
FVector CurrentPosition = Character->GetActorLocation();
FVector CurrentVelocity = CharacterMovement->GetLastUpdateVelocity();
UPoseSearchTrajectoryLibrary::UpdateHistory_TransformHistory(Trajectory, CurrentPosition, CurrentVelocity, Sampling, DeltaTime);

// 生成预测（模拟角色运动物理）
FPoseSearchTrajectoryData TrajectoryData;
FPoseSearchTrajectoryData::FDerived Derived;
// ... 初始化 TrajectoryData 和 Derived
UPoseSearchTrajectoryLibrary::UpdatePrediction_SimulateCharacterMovement(Trajectory, TrajectoryData, Derived, Sampling, DeltaTime);

// 处理碰撞
FTransformTrajectory OutTrajectory;
FPoseSearchTrajectory_WorldCollisionResults CollisionResult;
UPoseSearchTrajectoryLibrary::HandleTransformTrajectoryWorldCollisions(
    WorldContext, AnimInstance, Trajectory,
    true,   // bApplyGravity
    50.f,   // FloorCollisionsOffset
    OutTrajectory, CollisionResult,
    TraceChannel, bTraceComplex, ActorsToIgnore, DrawDebugType
);
```

## 模块依赖

该插件的 Runtime 模块 (PoseSearch) 依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Chooser` | 与 Chooser 表格系统集成，支持条件化动画选择 |
| `GameplayTags` | 支持 GameplayTag 事件系统 |
| `AnimationCore` | 动画核心基础设施（骨骼容器、姿态数据等） |
| `AnimGraphRuntime` | 动画图运行时（动画节点基类） |
| `MotionWarping` | 支持 Motion Warping 功能集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `314d38e0` | Fixed crash when loading trace file with missing assets in project (specifically a USkinnedAsset) | 修复加载缺少资产的 trace 文件时崩溃的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-05-12 | `1222a3b1` | PoseSearch - fix for Motion Matching Database editor Preview viewport doesn't display static mesh at | 修复数据库编辑器预览视口不显示静态网格的问题 |
| 2026-05-12 | `eddf36ad` | PoseSearch - fix velocity channel debug visualization | 修复速度通道的调试可视化问题 |
| 2026-05-12 | `b57412ab` | PoseSearch - Expose preview-mesh cap in Pose Search Database editor | 在数据库编辑器中暴露预览网格上限设置 |

### 维护评价

- **活跃维护**：最近更新非常频繁（2026 年 5 月有多次提交），持续进行 bug 修复和功能完善
- **成熟度**：插件从 2020 年创建至今约 6 年，经历了大量 API 迭代（多个 5.7/5.8 版本的 deprecation），正在逐步稳定
- **实验性状态**：`.uplugin` 标记为实验性且 `EnabledByDefault=false`，许多 API 带有 `UE_EXPERIMENTAL` 标记
- **代码规模**：197 个源文件，是一个功能完整、架构复杂的系统
- **API 稳定性警告**：大量 API 在 5.7-5.8 版本被废弃/替换，说明 API 仍在快速演进中
- **推荐**：适合对 Motion Matching 有需求的项目，但需注意实验性标签意味着 API 可能随时变更。建议密切关注版本更新日志

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PoseSearch)
- 官方文档（无）
# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（神经网络模型、动画资产、编辑器工具） |
| 模块 | `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanPlatform` (Runtime), `MeshTrackerInterface` (Runtime) 等共 29 个模块 |
| 实验性 | 否 |
| 创建时间 | ~2022（估） |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic 官方的 MetaHuman 角色动画全流程工具包。本文档聚焦其中的 **Face Contour Tracker（面部轮廓追踪）** 模块。

Face Contour Tracker 模块的核心职责是：**通过多个预训练神经网络模型（NNE），对视频/照片中的面部进行检测和密集特征点追踪**。它管理了一组面向不同面部区域的追踪模型——包括人脸检测器、全脸追踪器，以及针对眉毛、眼睛、鼻唇沟、嘴巴、嘴唇、下巴、牙齿等区域的密集追踪器。

这些追踪器产生的面部特征数据会被 MetaHuman Identity 和 MetaHuman Performance 资产消费，用于驱动 MetaHuman 角色的面部动画。整个管线是：**原始画面 → 面部轮廓追踪 → 面部拟合/动画求解 → 驱动骨骼网格体**。

## 使用场景

- **从视频中捕捉面部动画**：你有一段演员表演的视频素材，需要提取面部动画数据 → 使用 Face Contour Tracker 追踪面部特征点，再通过 Face Animation Solver 生成动画
- **创建 MetaHuman 角色身份**：你在 MetaHuman Identity 流程中需要检测和定位面部特征 → 加载默认的 FaceContourTrackerAsset 来进行面部检测和轮廓追踪
- **批量处理性能捕捉数据**：你有大量表演数据需要批量处理 → 通过 MetaHumanBatchProcessor 配合 Face Contour Tracker 自动化处理
- **自定义追踪后端**：你需要切换 NNE 推理后端（如 CPU/GPU/不同运行时） → 通过 `SetNNEBackend` 配置

## 蓝图用法

FaceContourTracker 模块主要面向 C++ 使用场景，其核心资产类 `UMetaHumanFaceContourTrackerAsset` 标记为 `BlueprintType`，可在蓝图中引用。

### 核心资产

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadDefaultTracker` | 静态方法，加载默认的面部轮廓追踪器资产 | `UMetaHumanFaceContourTrackerAsset` |
| `CanProcess` | 检查追踪器是否已准备好进行处理 | `UMetaHumanFaceContourTrackerAsset` |
| `LoadTrackers` | 异步加载所有 NNE 追踪模型（带进度通知） | `UMetaHumanFaceContourTrackerAsset` |
| `LoadTrackersSynchronous` | 同步加载所有追踪模型，返回是否成功 | `UMetaHumanFaceContourTrackerAsset` |
| `IsLoadingTrackers` | 查询当前是否正在加载模型 | `UMetaHumanFaceContourTrackerAsset` |
| `CancelLoadTrackers` | 取消正在进行的模型加载 | `UMetaHumanFaceContourTrackerAsset` |
| `SetNNEBackend` | 设置 NNE 推理后端名称 | `UMetaHumanFaceContourTrackerAsset` |
| `GetNNEBackend` | 获取当前 NNE 推理后端名称 | `UMetaHumanFaceContourTrackerAsset` |

### 使用示例（蓝图描述）

1. 通过 `LoadDefaultTracker` 获取默认追踪器资产的引用
2. 调用 `SetNNEBackend` 设置所需的推理后端（如 "DirectML"、"CUDA" 等）
3. 调用 `LoadTrackers` 异步加载模型，或 `LoadTrackersSynchronous` 同步加载
4. 加载完成后通过 `CanProcess` 确认就绪状态
5. 将追踪器资产传递给 MetaHuman Identity 或 Performance 资产进行面部追踪

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanFaceContourTrackerAsset.h"
```

### 基本用法：加载和使用默认追踪器

```cpp
// 加载默认的面部轮廓追踪器资产
TObjectPtr<UMetaHumanFaceContourTrackerAsset> Tracker = UMetaHumanFaceContourTrackerAsset::LoadDefaultTracker();
if (!Tracker)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to load default face contour tracker"));
    return;
}

// 检查是否可以进行处理
if (Tracker->CanProcess())
{
    UE_LOG(LogTemp, Log, TEXT("Tracker is ready to process"));
}
```

来源：`Public/MetaHumanFaceContourTrackerAsset.h`

### 进阶用法：异步加载追踪模型并自定义后端

```cpp
// 获取追踪器后，先设置 NNE 推理后端
Tracker->SetNNEBackend(TEXT("DirectML"));

// 异步加载所有追踪模型（推荐方式，不会阻塞游戏线程）
Tracker->LoadTrackers(true /*bInShowProgressNotification*/, [Tracker](bool bSuccess)
{
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("All face contour trackers loaded successfully"));
        // 加载完成，可以开始使用追踪器进行面部检测和追踪
        // 追踪器会自动管理 FaceDetector、FullFaceTracker 及各区域密集追踪器
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load face contour trackers"));
    }
});

// 如果需要取消正在加载的模型
if (Tracker->IsLoadingTrackers())
{
    Tracker->CancelLoadTrackers();
}

// 也可以同步加载（会阻塞当前线程，适合编辑器场景或批处理）
bool bLoaded = Tracker->LoadTrackersSynchronous();
```

来源：`Public/MetaHumanFaceContourTrackerAsset.h`

### 自定义模型数据

```cpp
// 追踪器资产支持配置自定义的 NNE 模型数据
// 每个追踪模型都通过 TSoftObjectPtr<UNNEModelData> 进行引用：
// - FaceDetectorModelData        人脸检测器
// - FullFaceTrackerModelData     全脸追踪器
// - BrowsDenseTrackerModelData   眉毛密集追踪器
// - EyesDenseTrackerModelData    眼睛密集追踪器
// - NasioLabialsDenseTrackerModelData 鼻唇沟密集追踪器
// - MouthDenseTrackerModelData   嘴巴密集追踪器
// - LipzipDenseTrackerModelData  嘴唇密集追踪器
// - ChinDenseTrackerModelData    下巴密集追踪器
// - TeethDenseTrackerModelData   牙齿密集追踪器
// - TeethConfidenceTrackerModelData 牙齿置信度追踪器

// 在编辑器中修改模型数据后，追踪器会在 PostEditChangeProperty 中自动处理更新
```

来源：`Public/MetaHumanFaceContourTrackerAsset.h`

## Demo 示例

```cpp
// MyFaceTrackerHelper.h
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanFaceContourTrackerAsset.h"

class FMyFaceTrackerHelper
{
public:
    /** 初始化并加载面部追踪器 */
    static void InitializeTracker(TFunction<void(UMetaHumanFaceContourTrackerAsset*)> OnReady)
    {
        // 加载默认追踪器资产
        TObjectPtr<UMetaHumanFaceContourTrackerAsset> Tracker = 
            UMetaHumanFaceContourTrackerAsset::LoadDefaultTracker();
        
        if (!Tracker)
        {
            UE_LOG(LogTemp, Error, TEXT("Cannot load default tracker asset"));
            OnReady(nullptr);
            return;
        }

        // 设置推理后端
        Tracker->SetNNEBackend(TEXT("DirectML"));

        // 异步加载所有追踪模型
        Tracker->LoadTrackers(true, [Tracker, OnReady = MoveTemp(OnReady)](bool bSuccess)
        {
            if (bSuccess && Tracker->CanProcess())
            {
                UE_LOG(LogTemp, Log, TEXT("Face contour tracker ready with backend: %s"), 
                    *Tracker->GetNNEBackend());
                OnReady(Tracker);
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("Face contour tracker failed to load"));
                OnReady(nullptr);
            }
        });
    }
};
```

```cpp
// UsageExample.cpp
#include "MyFaceTrackerHelper.h"

void StartFaceTrackingWorkflow()
{
    FMyFaceTrackerHelper::InitializeTracker([](UMetaHumanFaceContourTrackerAsset* Tracker)
    {
        if (Tracker)
        {
            // 追踪器已就绪，包含以下子追踪模型：
            // - FaceDetector: 面部检测
            // - FullFaceTracker: 全脸追踪
            // - Brows/Eyes/Mouth/Chin/Teeth 等密集追踪器
            // 这些模型可配合 MetaHuman Identity 和 Performance 资产使用
            UE_LOG(LogTemp, Log, TEXT("Ready to perform face contour tracking"));
        }
    });
}
```

## 模块依赖

FaceContourTracker 模块的独特依赖（标准 Core/Engine/Slate 等已省略）：

| 模块 | 用途 |
|---|---|
| `NNE` | Neural Network Engine，提供 NNE 模型实例接口（`IModelInstanceRunSync`、`IModelInstanceGPU`）和 `UNNEModelData` |
| `MetaHumanConfig` | MetaHuman 配置管理，可能提供追踪器的默认配置数据 |
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库（通过 MetaHumanConfig 间接依赖） |

> 注：完整插件中的其他模块还额外依赖 `ControlRigDeveloper`、`SkeletalMeshUtilitiesCommon`、`MetaHumanSDKEditor`、`MetaHumanCaptureDataEditor` 等。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH | 修复 MetaHuman 渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持对已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

- **活跃维护**：近期更新频繁（2026 年 5 月有多次功能性提交），Epic 持续投入开发
- **核心产品**：MetaHuman 是 Epic 的旗舰角色技术，不太可能被废弃
- **代码成熟度**：544 个源文件、29 个模块，属于大型成熟插件
- **已知信息**：部分追踪器 API（如 `FaceDetector`、`FullFaceTracker` 等 GPU 版本）已在 5.8 标记为 `UE_DEPRECATED`，迁移到了同步 CPU 版本（`IModelInstanceRunSync`），升级时需注意 API 变更
- **推荐程度**：⭐⭐⭐⭐⭐ 强烈推荐，这是 Epic 官方维护的 MetaHuman 核心组件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [FaceContourTracker 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceContourTracker)
- [MetaHuman 官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-in-unreal-engine/)
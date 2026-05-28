# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟人动画 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaHuman资产/工具） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime) 等共 28 个模块 |
| 实验性 | 否 |
| 创建时间 | 2022-10-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色面部动画制作工具套件。它解决的核心问题是：**如何将真实演员的面部表演数据（如 iPhone 深度摄像头、Live Link Face 录制的视频片段）转化为高保真的 MetaHuman 角色动画**。

整个插件覆盖了从捕捉到最终动画输出的完整流水线：

1. **数据采集与导入**（MetaHumanCaptureSource, MetaHumanFootageIngest, MetaHumanCaptureProtocolStack）—— 导入来自各种设备（iPhone、立体相机等）的面部视频/深度数据
2. **面部特征追踪**（MetaHumanFaceContourTracker）—— 追踪视频中的人脸轮廓、关键点
3. **面部拟合求解**（MetaHumanFaceFittingSolver）—— 将追踪到的面部数据拟合到 MetaHuman 骨骼网格体上
4. **动画求解**（MetaHumanFaceAnimationSolver）—— 将拟合结果转化为骨骼动画驱动参数
5. **身份管理**（MetaHumanIdentity）—— 管理 MetaHuman 角色身份资产，包括姿势捕捉与配置
6. **音频驱动面部**（MetaHumanSpeech2Face）—— 从语音音频生成面部动画
7. **动画输出**（MetaHumanPerformance, MetaHumanSequencer）—— 将最终动画数据输出为关卡序列或动画资产

**当前聚焦模块 MetaHumanCaptureDataEditor** 是插件编辑器层的捕捉数据编辑工具，提供相机选择 UI 控件和捕捉数据预览组件创建功能，供内部各模块在编辑器中展示和编辑捕捉到的面部表演数据。

## 使用场景

- 你有一段 iPhone 录制的面部表演视频 → 导入为 FootageCaptureData，通过 MetaHuman Animator 流水线生成 MetaHuman 面部动画
- 你使用 Live Link Face 实时捕捉演员表演 → 通过 MetaHumanCaptureProtocolStack 实时接收并处理捕捉数据
- 你需要将 MetaHuman 角色与真实演员的面部表情同步 → 用 MetaHumanFaceFittingSolver 进行面部拟合
- 你需要从对话音频自动驱动面部动画 → 用 MetaHumanSpeech2Face 模块
- 你需要批量处理大量面部捕捉数据 → 用 MetaHumanBatchProcessor 模块
- 你需要在编辑器中预览和编辑捕捉数据 → 用 MetaHumanCaptureDataEditor 提供的预览组件和相机选择控件

## 蓝图用法

MetaHumanCaptureDataEditor 模块主要提供 C++/Slate 编辑器工具，无直接蓝图可调用节点。蓝图层面的 MetaHuman 动画工作流主要通过 MetaHumanPerformance 和 MetaHumanSequencer 等其他模块的资产驱动，而非直接调用蓝图函数。

### 编辑器工具

| 工具 | 说明 | 类型 |
|---|---|---|
| `SMetaHumanCameraCombo` | 捕捉数据相机选择下拉框控件 | Slate Widget |
| `CaptureDataUtils::CreatePreviewComponent` | 从捕捉数据创建预览场景组件 | C++ 工具函数 |

## C++ 用法

### 头文件引入

```cpp
#include "CaptureDataUtils.h"
#include "SMetaHumanCameraCombo.h"
```

### 基本用法

从捕捉数据创建预览组件（用于编辑器中的数据预览场景）：

```cpp
// 来源: Public/CaptureDataUtils.h
#include "CaptureDataUtils.h"
#include "CaptureData.h"

// 为捕捉数据创建一个预览场景组件，用于在编辑器视口中显示
UObject* Owner = GetOuter(); // 拥有者对象
UCaptureData* CaptureData = LoadObject<UCaptureData>(nullptr, TEXT("/Game/MyCaptureData"));

USceneComponent* PreviewComponent = MetaHumanCaptureDataUtils::CreatePreviewComponent(CaptureData, Owner);
if (PreviewComponent)
{
    // 预览组件已创建并附加到 Owner 上
    // 可以进一步设置位置、旋转等
}
```

### 进阶用法

在自定义编辑器面板中集成相机选择下拉框：

```cpp
// 来源: Public/SMetaHumanCameraCombo.h
// 在 Slate UI 中使用 SMetaHumanCameraCombo 选择捕捉数据的相机
TArray<TSharedPtr<FString>> CameraOptions;
CameraOptions.Add(MakeShared<FString>(TEXT("CameraA")));
CameraOptions.Add(MakeShared<FString>(TEXT("CameraB")));

FString SelectedCamera = TEXT("CameraA");

// 创建相机选择下拉框
SNew(SMetaHumanCameraCombo, &CameraOptions, &SelectedCamera, PropertyOwner, PropertyHandle)
```

当捕捉数据源发生变化时，通知控件更新：

```cpp
// 来源: Public/SMetaHumanCameraCombo.h
// 当 FootageCaptureData 或音频源变化时，通知相机下拉框刷新
CameraCombo->HandleSourceDataChanged(FootageCaptureData, SoundWave, /*bResetRanges=*/true);

// 仅重置范围，不重新加载数据源
CameraCombo->HandleSourceDataChanged(/*bResetRanges=*/false);
```

## Demo 示例

以下是 MetaHumanCaptureDataEditor 模块的最小可编译使用示例，展示如何创建预览组件并集成相机选择控件：

### MetaHumanCaptureDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MetaHumanCaptureDemo.generated.h"

class UCaptureData;
class USceneComponent;

UCLASS(BlueprintType)
class MYPROJECT_API UMetaHumanCaptureDemo : public UObject
{
    GENERATED_BODY()

public:
    /** 为指定捕捉数据创建预览组件 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman|CaptureDemo")
    USceneComponent* CreatePreview(UCaptureData* InCaptureData);

    /** 获取当前预览组件 */
    UFUNCTION(BlueprintPure, Category = "MetaHuman|CaptureDemo")
    USceneComponent* GetPreviewComponent() const { return PreviewComponent; }

private:
    UPROPERTY()
    TObjectPtr<USceneComponent> PreviewComponent;
};
```

### MetaHumanCaptureDemo.cpp

```cpp
#include "MetaHumanCaptureDemo.h"
#include "CaptureDataUtils.h"
#include "CaptureData.h"

USceneComponent* UMetaHumanCaptureDemo::CreatePreview(UCaptureData* InCaptureData)
{
    if (!InCaptureData)
    {
        UE_LOG(LogTemp, Warning, TEXT("CreatePreview: CaptureData is null"));
        return nullptr;
    }

    // 使用 MetaHumanCaptureDataEditor 模块的工具函数创建预览组件
    PreviewComponent = MetaHumanCaptureDataUtils::CreatePreviewComponent(InCaptureData, this);

    if (PreviewComponent)
    {
        UE_LOG(LogTemp, Log, TEXT("Preview component created for capture data: %s"),
            *InCaptureData->GetName());
    }

    return PreviewComponent;
}
```

## 模块依赖

以 MetaHumanCaptureDataEditor 模块为例，其 Build.cs 中声明的依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanImageViewerEditor` | 提供图像查看器编辑器功能，用于预览捕捉的视频帧 |

整个插件（28 个模块）的跨模块依赖关系：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，提供底层面部求解算法 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器工具 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体通用工具，用于面部网格处理 |
| `ControlRigDeveloper` | ControlRig 开发工具，用于面部动画驱动 |

其余均为标准 Core/Engine/Slate 等常见依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪模式下过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存导致的问题 |

### 维护评价

- **活跃维护**：最近更新集中在 2026-05-20 至 2026-05-22，短短 3 天内有 5 次提交，表明该插件处于高频活跃开发阶段
- **功能迭代中**：近期更新涉及身体追踪支持、动画序列导出、渲染修复等实质性功能改进，而非仅仅编译适配
- **已知限制**：身体追踪模式下部分功能（如关卡序列导出、可视化对象显示）存在限制，正在逐步解除
- **推荐使用**：作为 Epic Games 官方工具，MetaHuman Animator 是制作 MetaHuman 角色面部动画的首选方案，适合所有需要高质量面部动画的项目。该模块仍在积极迭代中，建议跟进最新版本

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [MetaHuman 官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-unreal-engine/)
- [MetaHumanCaptureDataEditor 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureDataEditor)
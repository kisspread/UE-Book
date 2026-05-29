# Live Link Camera

> Live Link plugin adding functionalities for camera handling

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接相机 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、资产） |
| 模块 | `LiveLinkCamera` (Runtime), `LiveLinkCameraEditor` (Runtime), `LiveLinkCameraRecording` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkCamera) | |

## 用途

LiveLinkCamera 是虚幻引擎中 **Live Link** 系统针对**相机设备**的专用扩展插件。它解决的核心问题是：在**虚拟制片**工作流中，将实体相机（如专业电影摄影机、工业相机、无人机云台相机等）的实时视频流、镜头参数（焦距、光圈等）和运动数据，无缝且精确地同步到虚幻引擎内的虚拟摄像机上。

它之所以存在，是因为通用的 Live Link 协议只定义了基础的变换和骨骼数据。为了实现电影级的相机同步，需要额外处理：
1.  **镜头元数据解析**：从相机或镜头通信协议中提取焦距、光圈、对焦距离、镜头失真参数等。
2.  **时间码同步**：确保视频帧与引擎渲染帧精确对齐。
3.  **电影摄影机控制**：支持如 Arri、RED、Sony 等专业摄影机的专有控制协议。
4.  **Sequencer 录制与回放**：将实时相机数据录制为 Sequencer 关键帧，用于后期编辑和回放。

## 使用场景

-   **虚拟制片（Virtual Production）**：在 LED 墙或绿幕前，使用实体摄影机拍摄演员，同时将其运动和镜头数据实时驱动场景中的虚拟摄像机，实现前后景的精准匹配与实时合成。
-   **运动捕捉（Motion Capture）**：利用带有跟踪系统的相机（如 OptiTrack， Vicon）拍摄演员，同步驱动虚拟摄像机，用于预览或实时合成。
-   **实时广播与体育赛事**：在体育场馆中，使用跟踪摄像机拍摄运动员，将其数据同步到虚幻引擎中，用于生成实时增强现实（AR）图形覆盖。
-   **工业检测与模拟**：将工业机器人的末端执行器或检测摄像头的数据同步到虚拟环境中，用于远程监控或模拟训练。

## 蓝图用法

该插件的核心功能通过 Live Link 框架和 Sequencer 轨道实现，未直接暴露独立的 `BlueprintCallable` 函数。其使用主要通过以下方式：

1.  **Live Link 预设配置**：在 Live Link 面板中创建或选择支持 “Camera” 主题的源，将实体相机数据映射到场景中的 `CineCameraActor` 或 `CameraComponent`。
2.  **Sequencer 录制**：在 Sequencer 中添加 “Live Link Camera Controller” 轨道，用于录制和回放相机数据。

## C++ 用法

该插件的 C++ 接口主要用于扩展 Sequencer 录制功能，以及自定义相机控制器的底层集成。

### 头文件引入

```cpp
#include "LiveLinkCameraRecording.h"
```

### 基本用法：理解录制组件

以下是插件核心的 Sequencer 录制类结构：

```cpp
// 来源：Private/MovieSceneLiveLinkCameraControllerSection.h
/** 用于录制 LiveLink Camera Controller 属性的 Movie Scene 片段 */
UCLASS()
class UMovieSceneLiveLinkCameraControllerSection : public UMovieSceneHookSection
{
    // ...
    /** 初始化，传入要录制的 LiveLink 控制器 */
    void Initialize(ULiveLinkControllerBase* InLiveLinkController);
    // ...
public:
    /** 是否从缓存的镜头文件应用节点偏移 */
    UPROPERTY(EditAnywhere, Category="Camera Calibration")
    bool bApplyNodalOffsetFromCachedLensFile = true;
private:
    /** 录制时使用的镜头文件资产缓存 */
    UPROPERTY(VisibleAnywhere, Category="Camera Calibration")
    TObjectPtr<ULensFile> CachedLensFile = nullptr;
};

// 来源：Private/MovieSceneLiveLinkCameraControllerTrack.h
/** 管理 LiveLink Camera Controller 属性片段的轨道 */
UCLASS()
class UMovieSceneLiveLinkCameraControllerTrack : public UMovieSceneNameableTrack
{
    // ... 标准 MovieSceneTrack 接口实现 ...
};

// 来源：Private/MovieSceneLiveLinkCameraControllerTrackRecorder.h
/** 负责执行实际录制逻辑的录制器 */
UCLASS(BlueprintType)
class UMovieSceneLiveLinkCameraControllerTrackRecorder : public UMovieSceneLiveLinkControllerTrackRecorder
{
    // ... 核心录制逻辑 ...
    virtual void RecordSampleImpl(const FQualifiedFrameTime& CurrentTime) override;
    // 判断给定的控制器类是否受支持
    virtual bool IsLiveLinkControllerSupported(const TSubclassOf<ULiveLinkControllerBase>& ControllerToSupport) const override;
};
```

### 进阶用法：集成 Sequencer 轨道编辑器

插件还提供了 Sequencer 编辑器集成：

```cpp
// 来源：Private/LiveLinkCameraControllerTrackEditor.h
/** Sequencer 中 LiveLink Camera Controller 轨道的编辑器 */
class FLiveLinkCameraControllerTrackEditor : public FKeyframeTrackEditor<UMovieSceneLiveLinkCameraControllerTrack>
{
public:
    // 工厂方法，由 Sequencer 调用以创建此编辑器
    static TSharedRef<ISequencerTrackEditor> CreateTrackEditor(TSharedRef<ISequencer> OwningSequencer);
    // ...
};
```

## Demo 示例

此插件功能深度集成于 Live Link 和 Sequencer，通常无需直接实例化。以下示例演示了如何在代码中检查一个 Live Link 控制器是否适用于该录制器：

```cpp
// MyCameraRecorderCheck.cpp
#include "LiveLinkCameraRecording.h"
#include "LiveLinkControllerBase.h"

void CheckCameraControllerCompatibility()
{
    // 假设我们有一个 Live Link 控制器类
    TSubclassOf<ULiveLinkControllerBase> MyControllerClass = /* ... */;
    
    // 创建录制器实例以进行查询
    UMovieSceneLiveLinkCameraControllerTrackRecorder* Recorder = NewObject<UMovieSceneLiveLinkCameraControllerTrackRecorder>();
    
    if (Recorder && Recorder->IsLiveLinkControllerSupported(MyControllerClass))
    {
        UE_LOG(LogTemp, Log, TEXT("控制器 %s 受 LiveLinkCameraRecording 插件支持。"), *MyControllerClass->GetName());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("控制器 %s 不支持。"), *MyControllerClass->GetName());
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 配置文件重命名以符合新规范 |
| 2025-04-22 | `92ef0a10` | - Update the LiveLinkCameraController to support dynamic filmback resolution from a frame data. | 相机控制器支持动态传感器分辨率 |
| 2025-01-27 | `ef0d3477` | [Sequencer] Update Tracks Names and Reorganize Tracks Order | Sequencer 轨道名称更新与顺序重排 |
| 2025-01-23 | `fa1c08d3` | [Backout] - CL39424548 | 回滚了一次提交 |
| 2025-01-23 | `c2e4648f` | [Sequencer] Update Tracks Names and Reorganize Tracks Order | (同上，可能是回滚前的一次提交) |

### 维护评价

LiveLinkCamera 是一个为虚幻引擎的**虚拟制片**工作流提供关键相机数据同步功能的插件。该插件**仍在活跃维护中**，最近一次功能性更新在 2025 年 4 月，增加了对动态传感器分辨率的支持，表明 Epic Games 持续为其添加新特性以适配更专业的硬件。最近的提交主要是重命名配置文件和 Sequencer 轨道的优化。

由于插件标记为 `IsBetaVersion: true`，表明其 API 和功能可能还未完全稳定。它适合在生产环境中谨慎使用，并关注后续版本的更新说明。总体而言，**推荐**在需要将实体摄影机集成到虚幻引擎工作流的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkCamera)
- 官方文档 (暂无)
- 测试用例 (未在插件目录内发现)
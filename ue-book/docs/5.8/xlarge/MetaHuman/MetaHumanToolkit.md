# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-04-05 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 动画制作完整工具链，用于将真实人类面部表演数据转换为 MetaHuman 角色的面部动画。

该插件解决的核心问题：**从视频素材（iPhone 深度摄像头、专业动捕设备或音频）驱动高保真 MetaHuman 面部动画**。它不是单一功能的插件，而是一个完整的面部动画制作管线，包含：

1. **面部追踪**（`MetaHumanFaceContourTracker`）：从视频帧中检测和追踪面部特征点/轮廓
2. **面部拟合求解器**（`MetaHumanFaceFittingSolver`）：将追踪数据拟合到 MetaHuman 面部骨骼
3. **动画求解器**（`MetaHumanFaceAnimationSolver`）：将面部追踪数据转换为动画曲线
4. **深度生成**（`MetaHumanDepthGenerator`）：从单目/深度摄像头生成深度图
5. **身份系统**（`MetaHumanIdentity`）：管理 MetaHuman 角色的身份数据，包括各表情姿态
6. **性能/表演**（`MetaHumanPerformance`）：管理面部表演的录制与播放
7. **语音驱动**（`MetaHumanSpeech2Face`）：从音频生成面部动画
8. **批量处理**（`MetaHumanBatchProcessor`）：批量处理多个动画序列
9. **序列器集成**（`MetaHumanSequencer`）：与 UE Sequencer 时间线深度集成

## 使用场景

- 你使用 iPhone TrueDepth 摄像头录制了面部表演 → 用 MetaHumanCaptureSource + MetaHumanFaceFittingSolver 将其转换为 MetaHuman 动画
- 你有一段对话音频 → 用 MetaHumanSpeech2Face 从音频生成口型动画
- 你需要创建一个 MetaHuman 角色并定义其各种表情姿态 → 用 MetaHumanIdentity 编辑身份资产
- 你已有一个已有的 MetaHuman 网格并想导出动画序列 → 用 MetaHumanBatchProcessor 批量导出
- 你需要在 Sequencer 中同时查看原始视频素材和 3D 动画结果进行对比 → 用 MetaHumanToolkit 的 AB 对比视图
- 你需要对接专业动捕设备（如 LiveLinkFace）→ 用 MetaHumanCaptureProtocolStack 处理捕获协议

## 蓝图用法

由于 MetaHuman Animator 主要是编辑器工具（Editor Tool），大部分高级功能通过编辑器 UI 操作。以下为可从源码中提取的运行时可用蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTrackerImageSize` | 获取追踪图像尺寸，用于在屏幕上定位轮廓数据 | `FMetaHumanEditorViewportClient` |
| `GetPointPositionOnImage` | 将屏幕坐标转换为图像坐标 | `FMetaHumanEditorViewportClient` |
| `GetFootageDepthData` | 获取素材深度数据（近/远平面） | `FMetaHumanEditorViewportClient` |
| `SetFootageDepthData` | 设置素材深度数据 | `FMetaHumanEditorViewportClient` |
| `GetMeshDepthData` | 获取网格深度数据 | `FMetaHumanEditorViewportClient` |
| `SetMeshDepthData` | 设置网格深度数据 | `FMetaHumanEditorViewportClient` |
| `IsShowingCurves` | 查询视图是否显示追踪曲线 | `FMetaHumanEditorViewportClient` |
| `IsShowingControlVertices` | 查询视图是否显示控制顶点 | `FMetaHumanEditorViewportClient` |
| `ToggleABViews` | 切换 A/B 视图显示 | `FMetaHumanEditorViewportClient` |

> **注意**：上述大部分 API 为 C++ 编辑器内部 API，标记为 `UE_API`。在蓝图层面，MetaHuman Animator 主要通过其编辑器面板（Asset Editor）进行操作，而非直接暴露蓝图节点。实际的面部追踪、拟合、动画求解等流程通过编辑器 UI 的工具面板触发。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanToolkitBase.h"
#include "MetaHumanEditorViewportClient.h"
#include "MetaHumanABCommandList.h"
```

### 基本用法：创建自定义 MetaHuman 编辑器 Toolkit

MetaHumanToolkit 模块提供了 `FMetaHumanToolkitBase` 基类，所有 MetaHuman 资产编辑器都继承自它。该基类内置了 Sequencer 时间线、带 AB 对比功能的 3D 视口和详情面板。

以下示例展示如何创建一个自定义的 MetaHuman 资产编辑器 Toolkit：

```cpp
// MyMetaHumanToolkit.h
#pragma once

#include "MetaHumanToolkitBase.h"

class FMyMetaHumanToolkit : public FMetaHumanToolkitBase
{
public:
    FMyMetaHumanToolkit(UAssetEditor* InOwningAssetEditor);

protected:
    // 绑定自定义快捷键命令
    virtual void BindCommands() override;

    // 在视口底部添加额外的自定义控件
    virtual TSharedRef<SWidget> GetViewportExtraContentWidget() override;

    // 自定义 A/B 视图的右键菜单内容
    virtual void HandleGetViewABMenuContents(
        EABImageViewMode InViewMode,
        FMenuBuilder& InMenuBuilder) override;

    // 控制时间线是否启用
    virtual bool IsTimelineEnabled() const override;

    // 处理撤销/重做事务
    virtual void HandleUndoOrRedoTransaction(
        const FTransaction* InTransaction) override;
};
```

```cpp
// MyMetaHumanToolkit.cpp
#include "MyMetaHumanToolkit.h"
#include "Widgets/Text/STextBlock.h"

FMyMetaHumanToolkit::FMyMetaHumanToolkit(UAssetEditor* InOwningAssetEditor)
    : FMetaHumanToolkitBase(InOwningAssetEditor)
{
}

void FMyMetaHumanToolkit::BindCommands()
{
    // 在此绑定自定义命令到 ABCommandList
    // ABCommandList.MapAction(MyCommand, SharedThis(this),
    //     &FMyMetaHumanToolkit::OnMyAction,
    //     &FMyMetaHumanToolkit::CanExecuteAction,
    //     &FMyMetaHumanToolkit::IsMyActionChecked);
}

TSharedRef<SWidget> FMyMetaHumanToolkit::GetViewportExtraContentWidget()
{
    return SNew(STextBlock).Text(FText::FromString(TEXT("My Custom Widget")));
}

void FMyMetaHumanToolkit::HandleGetViewABMenuContents(
    EABImageViewMode InViewMode,
    FMenuBuilder& InMenuBuilder)
{
    InMenuBuilder.BeginSection("MySection", FText::FromString(TEXT("My Custom Section")));
    // 添加自定义菜单项...
    InMenuBuilder.EndSection();
}

bool FMyMetaHumanToolkit::IsTimelineEnabled() const
{
    return true;
}

void FMyMetaHumanToolkit::HandleUndoOrRedoTransaction(
    const FTransaction* InTransaction)
{
    // 处理撤销/重做后的状态恢复
}
```

*来源: `Source/MetaHumanToolkit/Public/MetaHumanToolkitBase.h`*

### 进阶用法：自定义视口客户端与 AB 对比控制

`FMetaHumanEditorViewportClient` 提供了完整的 AB 对比视口功能，包括视图切换、深度数据管理、曲线编辑和相机控制：

```cpp
// 自定义视口客户端，扩展 AB 对比功能
class FMyViewportClient : public FMetaHumanEditorViewportClient
{
public:
    FMyViewportClient(FPreviewScene* InPreviewScene, UMetaHumanViewportSettings* InSettings)
        : FMetaHumanEditorViewportClient(InPreviewScene, InSettings)
    {
        // 绑定委托：获取预览场景中的所有组件
        OnGetAllPrimitiveComponentsDelegate.BindRaw(
            this, &FMyViewportClient::HandleGetAllPrimitiveComponents);

        // 绑定委托：获取选中的组件（用于视口高亮）
        OnGetSelectedPrimitivesComponentsDelegate.BindRaw(
            this, &FMyViewportClient::HandleGetSelectedComponents);

        // 绑定委托：相机移动时的回调
        OnCameraMovedDelegate.AddRaw(
            this, &FMyViewportClient::HandleCameraMoved);

        // 绑定深度数据变更委托
        OnUpdateFootageDepthDataDelegate.BindRaw(
            this, &FMyViewportClient::HandleFootageDepthChanged);
    }

    // 控制哪些组件在 A/B 视图中隐藏
    virtual TArray<UPrimitiveComponent*> GetHiddenComponentsForView(
        EABImageViewMode InViewMode) const override
    {
        TArray<UPrimitiveComponent*> HiddenComponents;
        // 根据视图模式决定隐藏哪些组件
        if (InViewMode == EABImageViewMode::A)
        {
            // View A 隐藏网格组件，只显示素材
        }
        else
        {
            // View B 隐藏素材组件，只显示网格
        }
        return HiddenComponents;
    }

    // 自定义 EV100 曝光值是否可变
    virtual bool CanChangeEV100(EABImageViewMode InViewMode) const override
    {
        return true;
    }

private:
    TArray<UPrimitiveComponent*> HandleGetAllPrimitiveComponents()
    {
        // 返回预览场景中的所有组件
        return {};
    }

    TArray<UPrimitiveComponent*> HandleGetSelectedComponents()
    {
        // 返回当前选中的组件
        return {};
    }

    void HandleCameraMoved()
    {
        // 相机移动时的自定义逻辑
    }

    void HandleFootageDepthChanged(float InNear, float InFar)
    {
        // 素材深度数据变更时的处理
    }
};
```

*来源: `Source/MetaHumanToolkit/Public/MetaHumanEditorViewportClient.h`*

### AB 对比命令绑定

使用 `FMetaHumanABCommandList` 为 A/B 两个视图分别绑定独立的命令：

```cpp
// 绑定一个 toggle 命令到 A 和 B 视图
TSharedRef<FMyViewportClient> ViewportClient = /* ... */;

ABCommandList.MapAction(
    FMetaHumanToolkitCommands::Get().ToggleCurves,
    ViewportClient,
    &FMyViewportClient::ToggleShowCurves,      // 执行动作
    &FMyViewportClient::CanToggleShowCurves,    // 是否可执行
    &FMyViewportClient::IsShowingCurves         // 是否选中
);

// 同一个命令会自动分别绑定到 ViewA 和 ViewB
// 当用户在 ViewA 菜单中点击时，InViewMode 自动为 EABImageViewMode::A
// 当用户在 ViewB 菜单中点击时，InViewMode 自动为 EABImageViewMode::B
```

*来源: `Source/MetaHumanToolkit/Public/MetaHumanABCommandList.h`*

## Demo 示例

以下为一个最小可编译的自定义 MetaHuman Toolkit 实现，展示如何继承基类创建自己的资产编辑器：

```cpp
// MyFacePerformanceToolkit.h
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanToolkitBase.h"

class FMyFacePerformanceToolkit : public FMetaHumanToolkitBase
{
public:
    FMyFacePerformanceToolkit(UAssetEditor* InOwningAssetEditor)
        : FMetaHumanToolkitBase(InOwningAssetEditor)
    {
    }

    virtual ~FMyFacePerformanceToolkit() = default;

protected:
    virtual void BindCommands() override;
    virtual TSharedRef<SWidget> GetViewportExtraContentWidget() override;
    virtual void HandleSequencerMovieSceneDataChanged(EMovieSceneDataChangeType InDataChangeType) override;
    virtual void HandleUndoOrRedoTransaction(const FTransaction* InTransaction) override;
    virtual bool IsTimelineEnabled() const override { return true; }

    // AB 视图菜单自定义
    virtual void HandleGetViewABMenuContents(EABImageViewMode InViewMode, FMenuBuilder& InMenuBuilder) override;

    // 序列器事件处理
    virtual void HandleSequencerKeyAdded(FMovieSceneChannel* InChannel, const TArray<FKeyAddOrDeleteEventItem>& InItems) override;
    virtual void HandleSequencerKeyRemoved(FMovieSceneChannel* InChannel, const TArray<FKeyAddOrDeleteEventItem>& InItems) override;
};
```

```cpp
// MyFacePerformanceToolkit.cpp
#include "MyFacePerformanceToolkit.h"
#include "MetaHumanToolkitCommands.h"
#include "Widgets/Text/STextBlock.h"

void FMyFacePerformanceToolkit::BindCommands()
{
    // 绑定内置的视图切换命令
    // 例如：绑定 RGB 通道切换
    ABCommandList.MapAction(
        FMetaHumanToolkitCommands::Get().ToggleRGBChannel,
        SharedThis(this),
        &FMyFacePerformanceToolkit::HandleToggleRGBChannel,
        &FMyFacePerformanceToolkit::CanToggleRGBChannel,
        &FMyFacePerformanceToolkit::IsRGBChannelChecked);
}

TSharedRef<SWidget> FMyFacePerformanceToolkit::GetViewportExtraContentWidget()
{
    // 在视口底部添加自定义信息面板
    return SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(4.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Performance Info Panel")))
        ];
}

void FMyFacePerformanceToolkit::HandleSequencerMovieSceneDataChanged(
    EMovieSceneDataChangeType InDataChangeType)
{
    // 当序列器数据变化时（例如添加/删除关键帧），更新视口显示
}

void FMyFacePerformanceToolkit::HandleUndoOrRedoTransaction(
    const FTransaction* InTransaction)
{
    // 撤销/重做后刷新视口和属性面板
}

void FMyFacePerformanceToolkit::HandleGetViewABMenuContents(
    EABImageViewMode InViewMode, FMenuBuilder& InMenuBuilder)
{
    // 为 A/B 视图菜单添加自定义条目
    InMenuBuilder.AddMenuEntry(
        FMetaHumanToolkitCommands::Get().ToggleDepthMesh);
}

void FMyFacePerformanceToolkit::HandleSequencerKeyAdded(
    FMovieSceneChannel* InChannel, const TArray<FKeyAddOrDeleteEventItem>& InItems)
{
    // 关键帧添加后的自定义处理逻辑
}

void FMyFacePerformanceToolkit::HandleSequencerKeyRemoved(
    FMovieSceneChannel* InChannel, const TArray<FKeyAddOrDeleteEventItem>& InItems)
{
    // 关键帧删除后的自定义处理逻辑
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SkeletalMeshUtilitiesCommon` | 骨骼网格工具（MetaHumanIdentity 依赖） |
| `ControlRigDeveloper` | ControlRig 开发工具（MetaHumanIdentity 依赖） |
| `MetaHumanCaptureDataEditor` | 捕获数据编辑器（MetaHumanIdentity 依赖） |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器扩展（MetaHumanIdentity 依赖） |
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库（MetaHumanConfig 依赖） |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器（MetaHumanCaptureDataEditor 依赖） |

> 由于该插件包含 28 个模块，各模块间存在复杂的内部依赖关系（如 Editor 模块依赖对应的 Runtime 模块），上表仅列出与外部模块的**非标准依赖**。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 身体追踪启用时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持对已有网格导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存问题 |

### 维护评价

MetaHuman Animator 是 Epic Games **核心重点维护**的插件之一，最近一次更新距今仅数天（2026-05-22），更新频率非常高。

**优点**：
- **持续活跃维护**：几乎每周都有功能性更新和 bug 修复，与 MetaHuman 技术栈的最新功能保持同步
- **功能完整**：覆盖了从视频捕获到动画求解再到序列器编辑的完整动画制作管线
- **模块化设计**：28 个独立模块分工明确，易于扩展和维护

**注意事项**：
- **不默认启用**：需在插件设置中手动启用
- **源码规模庞大**：544 个源文件，二次开发需要投入较多学习成本
- **无官方文档**：.uplugin 的 DocsURL 为空，主要依赖源码注释和 Epic 官方教程
- **依赖 MetaHuman 生态**：需要配合 MetaHuman Creator 生成的角色资产使用

**推荐程度**：如果你的项目需要 MetaHuman 面部动画能力，这是**唯一且必须**使用的官方插件，强烈推荐启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- 官方文档：.uplugin 中未提供（DocsURL 为空）
- [MetaHuman 官方教程](https://dev.epicgames.com/community/learning/courses/Z8y/meta-human-animator/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)
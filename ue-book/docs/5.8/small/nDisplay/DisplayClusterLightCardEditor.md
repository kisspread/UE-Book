# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 分布式显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、材质模板、编辑器工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterWarp` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterMonitor` (Runtime), `SharedMemoryMedia` (Runtime), `ScalableMPCDI` (External) 等 29 个模块 |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 的**集群渲染与虚拟制片核心插件**，解决以下问题：

1. **多 PC 同步渲染**：将一个 UE 场景通过局域网同步分发到多台 PC 上，每台 PC 负责渲染场景的一部分（如投影仪的某个投影区域），所有 PC 画面精确帧同步，组成一个完整的超大显示系统（CAVE、LED 墙、穹顶投影等）。
2. **虚拟制片 (ICVFX)**：为 LED Volume 拍摄提供完整的工具链——包括 Light Card（补光卡/旗板）编辑、投影变形校正（Warp）、色彩分级（Color Grading）、MPCDI 配置支持等。
3. **多屏立体渲染**：支持 mono 和 stereo（立体声/左右眼）两种渲染模式，适用于 VR 场景和立体投影。
4. **集群回放与录制**：通过 MoviePipeline 模块支持集群渲染的电影序列导出（EXR 多层输出等）。
5. **远程控制与多用户协作**：通过 RemoteControl 和 MultiUser 模块实现远程参数调整和多用户实时协作。

简言之：**如果你的项目需要多个投影仪/LED 屏幕拼接成一个超大画面，或者在虚拟制片 LED Volume 中拍摄，nDisplay 是必选插件。**

## 使用场景

- 你在搭建一个 **CAVE 沉浸式环境**（四面/六面投影） → 用 nDisplay 配置投影拓扑和变形校正
- 你在做 **LED Volume 虚拟制片**（ICVFX） → 用 nDisplay 的 Light Card Editor 补光 + MPCDI 投影映射
- 你需要将画面同步到 **多台 PC 分别驱动不同投影仪** → 用 nDisplay 集群同步渲染
- 你需要导出 **集群渲染的 EXR 多层序列帧** → 用 nDisplay MoviePipeline 模块
- 你需要 **多台 PC 画面帧同步、色彩一致** → 用 nDisplay 的 Warp、Color Grading、Monitor 模块

## 蓝图用法

> ⚠️ nDisplay 的大部分 API 位于运行时核心模块 `DisplayCluster`，本节仅展示当前文档聚焦的 `DisplayClusterLightCardEditor` 模块中可外部访问的接口。

### 模块接口（IDisplayClusterLightCardEditor）

| 函数 | 说明 | 所在类 |
|---|---|---|
| `Get()` | 获取 LightCardEditor 模块单例 | `IDisplayClusterLightCardEditor` |
| `IsAvailable()` | 检查模块是否已加载 | `IDisplayClusterLightCardEditor` |
| `ShowLabels(FLabelArgs)` | 为指定 RootActor 显示/隐藏 Light Card 标签并保存设置 | `IDisplayClusterLightCardEditor` |
| `GetDefaultLightCardTemplate()` | 获取创建新 Light Card 时的默认模板 | `IDisplayClusterLightCardEditor` |

### 编辑器设置（项目设置 / 用户设置）

**项目设置** (`UDisplayClusterLightCardEditorProjectSettings`)：

| 属性 | 类型 | 说明 |
|---|---|---|
| `LightCardTemplateDefaultPath` | `FDirectoryPath` | 新建 Light Card 模板的默认保存路径 |
| `DefaultLightCardTemplate` | `TSoftObjectPtr` | 新建 Light Card 时使用的默认模板 |
| `DefaultFlagTemplate` | `TSoftObjectPtr` | 新建 Flag 时使用的默认模板 |
| `LightCardLabelScale` | `float` | Light Card 标签显示缩放 |

**用户设置** (`UDisplayClusterLightCardEditorSettings`)：

| 属性 | 类型 | 说明 |
|---|---|---|
| `RecentlyPlacedItems` | `TArray<FDisplayClusterLightCardEditorRecentItem>` | 最近放置的 Light Card/Flag 历史记录 |
| `ProjectionMode` | `uint8` | 上次使用的投影模式 |
| `bDisplayIcons` | `bool` | 是否在编辑器中显示图标 |
| `IconScale` | `float` | 图标缩放比例 |

### 使用示例（蓝图描述）

1. **获取模块接口**：通过 `FModuleManager::Get().LoadModuleChecked<IDisplayClusterLightCardEditor>("DisplayClusterLightCardEditor")` 获取模块实例
2. **显示标签**：构造 `FLabelArgs` 结构体，设置目标 RootActor 和显示参数，调用 `ShowLabels()`
3. **获取默认模板**：调用 `GetDefaultLightCardTemplate()` 获取 Light Card 创建时的默认配置

## C++ 用法

### 头文件引入

```cpp
// 模块接口
#include "IDisplayClusterLightCardEditor.h"

// Light Card 编辑器核心类
#include "DisplayClusterLightCardEditor.h"

// 视口客户端
#include "DisplayClusterLightCardEditorViewportClient.h"

// Light Card 模板
#include "DisplayClusterLightCardTemplate.h"

// 编辑器设置
#include "DisplayClusterLightCardEditorSettings.h"
```

### 基本用法 — 访问 Light Card 编辑器模块

```cpp
// 来源: Private/DisplayClusterLightCardEditorModule.h
// 检查模块是否可用并获取实例
if (IDisplayClusterLightCardEditor::IsAvailable())
{
    IDisplayClusterLightCardEditor& LightCardEditorModule = IDisplayClusterLightCardEditor::Get();

    // 获取默认 Light Card 模板
    UDisplayClusterStageActorTemplate* DefaultTemplate = LightCardEditorModule.GetDefaultLightCardTemplate();

    // 显示 Light Card 标签
    IDisplayClusterLightCardEditor::FLabelArgs LabelArgs;
    // 配置 LabelArgs...
    LightCardEditorModule.ShowLabels(LabelArgs);
}
```

### 基本用法 — 创建 Light Card 编辑器实例

```cpp
// 来源: Private/DisplayClusterLightCardEditor.h
// 在 Operator 面板中创建 Light Card 编辑器实例
TSharedRef<IDisplayClusterOperatorApp> LightCardEditor =
    FDisplayClusterLightCardEditor::MakeInstance(InViewModel);

// 初始化编辑器
LightCardEditor->Initialize(InViewModel);
```

### 基本用法 — 添加和管理 Light Card

```cpp
// 来源: Private/DisplayClusterLightCardEditor.h
// 获取编辑器实例后，操作 Light Card
FDisplayClusterLightCardEditor* Editor = /* ... */;

// 新建一个 Light Card 并居中显示
ADisplayClusterLightCardActor* NewLightCard = Editor->AddNewLightCard();

// 新建一个 Flag（旗板）
ADisplayClusterLightCardActor* NewFlag = Editor->AddNewFlag();

// 从模板创建
ADisplayClusterLightCardActor* FromTemplate = Editor->SpawnActorAs<ADisplayClusterLightCardActor>(
    FName("MyLightCard"), Template);

// 选择和操作
TArray<AActor*> Actors;
Editor->GetSelectedActors(Actors);

// 复制、粘贴、删除
Editor->CopySelectedActors();
TArray<AActor*> PastedActors = Editor->PasteActors();
Editor->RemoveSelectedActors(/*bDeleteLightCardActor=*/true);

// 创建模板
Editor->CreateLightCardTemplate();

// 标签管理
Editor->ToggleLightCardLabels();
Editor->SetLightCardLabelScale(1.5f);
```

### 进阶用法 — 视口客户端操作

```cpp
// 来源: Private/Viewport/DisplayClusterLightCardEditorViewportClient.h
// 通过视口客户端进行更底层的 Light Card 操控
FDisplayClusterLightCardEditorViewportClient* ViewportClient = /* ... */;

// 更新预览场景中的代理 Actor
ViewportClient->UpdatePreviewActor(RootActor, true);

// 切换投影模式
ViewportClient->SetProjectionMode(
    EDisplayClusterMeshProjectionType::Azimuthal,
    LVT_Perspective
);

// 在球面坐标系中移动 Actor
FDisplayClusterLightCardEditorHelper::FSphericalCoordinates SphericalCoords;
SphericalCoords.Radius = 500.0f;
SphericalCoords.Azimuth = 45.0f;
SphericalCoords.Elevation = 30.0f;
ViewportClient->MoveActorTo(ActorPtr, SphericalCoords);

// 将 Actor 居中到视口
ViewportClient->CenterActorInView(ActorPtr);

// 进入绘制 Light Card 模式（用户在视口中画多边形生成 Light Card）
ViewportClient->EnterDrawingLightCardMode();
// ... 用户绘制完成后自动退出
```

### 进阶用法 — Light Card 模板管理

```cpp
// 来源: Private/LightCardTemplates/DisplayClusterLightCardTemplateHelpers.h
#include "DisplayClusterLightCardTemplateHelpers.h"

// 加载所有 Light Card 模板
TArray<UDisplayClusterLightCardTemplate*> AllTemplates =
    UE::DisplayClusterLightCardTemplateHelpers::GetLightCardTemplates();

// 仅加载收藏模板
TArray<UDisplayClusterLightCardTemplate*> FavoriteTemplates =
    UE::DisplayClusterLightCardTemplateHelpers::GetLightCardTemplates(/*bFavoritesOnly=*/true);

// 模板内部包含一个 Light Card Actor 的实例，用于存储外观设置
UDisplayClusterLightCardTemplate* Template = /* ... */;
AActor* TemplateActor = Template->GetTemplateActor();
```

### 进阶用法 — 判断 Actor 类型

```cpp
// 来源: Private/DisplayClusterLightCardEditorUtils.h
#include "DisplayClusterLightCardEditorUtils.h"

// 检查某个 Actor 是否是 Light Card 编辑器管理的类型
bool bManaged = UE::DisplayClusterLightCardEditorUtils::IsManagedActor(SomeActor);

// 检查某个 Actor 是否可在视口中选择
bool bSelectable = UE::DisplayClusterLightCardEditorUtils::IsProxySelectable(SomeActor);

// 发现所有实现了 Stage Actor 接口的类
TSet<UClass*> StageActorClasses = UE::DisplayClusterLightCardEditorUtils::GetAllStageActorClasses();
```

## Demo 示例

以下示例展示如何在自定义编辑器工具中创建 Light Card 并操作标签显示：

```cpp
// MyLightCardTool.h
#pragma once

#include "CoreMinimal.h"
#include "IDisplayClusterLightCardEditor.h"

class FMyLightCardTool
{
public:
    /** 初始化：检查模块可用性并注册标签 */
    void Initialize(ADisplayClusterRootActor* InRootActor);

    /** 创建一个来自默认模板的 Light Card */
    ADisplayClusterLightCardActor* CreateLightCardFromDefaultTemplate(
        FDisplayClusterLightCardEditor* InEditor);

    /** 切换所有 Light Card 标签的显示状态 */
    void ToggleAllLabels();

private:
    TWeakObjectPtr<ADisplayClusterRootActor> RootActor;
};
```

```cpp
// MyLightCardTool.cpp
#include "MyLightCardTool.h"
#include "IDisplayClusterLightCardEditor.h"
#include "DisplayClusterLightCardEditor.h"
#include "DisplayClusterRootActor.h"
#include "DisplayClusterLightCardActor.h"
#include "DisplayClusterLightCardTemplate.h"

void FMyLightCardTool::Initialize(ADisplayClusterRootActor* InRootActor)
{
    RootActor = InRootActor;

    if (IDisplayClusterLightCardEditor::IsAvailable())
    {
        // 注册标签显示
        IDisplayClusterLightCardEditor::FLabelArgs Args;
        IDisplayClusterLightCardEditor::Get().ShowLabels(Args);
    }
}

ADisplayClusterLightCardActor* FMyLightCardTool::CreateLightCardFromDefaultTemplate(
    FDisplayClusterLightCardEditor* InEditor)
{
    if (!InEditor || !RootActor.IsValid())
    {
        return nullptr;
    }

    // 获取默认模板
    UDisplayClusterStageActorTemplate* DefaultTemplate = nullptr;
    if (IDisplayClusterLightCardEditor::IsAvailable())
    {
        DefaultTemplate = IDisplayClusterLightCardEditor::Get().GetDefaultLightCardTemplate();
    }

    // 从模板创建 Light Card 并居中显示
    ADisplayClusterLightCardActor* NewLightCard = InEditor->AddNewLightCard();
    if (NewLightCard && DefaultTemplate)
    {
        // 可选：应用模板设置
    }

    return NewLightCard;
}

void FMyLightCardTool::ToggleAllLabels()
{
    if (!IDisplayClusterLightCardEditor::IsAvailable())
    {
        return;
    }

    IDisplayClusterLightCardEditor::FLabelArgs Args;
    IDisplayClusterLightCardEditor::Get().ShowLabels(Args);
}
```

## 模块依赖

nDisplay 插件体量庞大（29 个模块），以下列出**独特依赖**（不包括常见 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | Direct3D 12 渲染硬件接口，用于 SharedMemoryMedia 模块的 GPU 共享内存传输 |
| `LevelEditor` | 关卡编辑器集成，用于 LightCardEditor 的布局扩展和工具栏注册 |
| `EditorWidgets` | 编辑器控件，用于编辑器 UI 构建 |
| `UnrealEd` | 编辑器框架，用于属性自定义、场景预览、编辑器撤销/重做等 |
| `MPCDI` | MPCDI 投影校正格式支持（外部库 ScalableMPCDI） |

> 注：运行时核心模块 `DisplayCluster` 的具体依赖需查看 `DisplayCluster.Build.cs`，此处仅列出文档聚焦的 `DisplayClusterLightCardEditor` 模块相关依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 集成：支持 EXR 多层输出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 合并 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复拓扑感知相机命名和 MPCDI/ICVFX 着色器不透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复输出帧编码回退时未正确处理非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护 ✅**

nDisplay 是 Epic Games 的**战略级插件**，为虚拟制片（ICVFX / In-Camera VFX）和大型沉浸式显示提供核心支持。从近期提交记录看：

- **更新频率**：每周多次提交，持续活跃
- **更新内容**：涵盖功能新增（EXR 多层支持）、Bug 修复（着色器问题、闪烁）、集成改进（MovieGraph / MRG）
- **创建于 2018 年**，已持续维护 8 年，属于 UE 虚拟制片工具链的基石
- **非实验性**，`IsBetaVersion=false`，但 `EnabledByDefault=false` 需要手动启用
- **强烈推荐**：如果你的项目涉及虚拟制片或多屏投影，这是必备插件

**注意事项**：该插件体量巨大（29 个模块，1351 源文件），学习曲线较陡。建议先从 `DisplayClusterLightCardEditor` 和 `DisplayClusterConfiguration` 模块入手了解基础概念，再逐步深入投影校正和集群同步部分。

## 子模块索引

由于 nDisplay 是 xlarge 级插件（1351 源文件），以下按功能分组列出主要子模块：

| 模块 | 类型 | 用途 |
|---|---|---|
| `DisplayCluster` | Runtime | 核心运行时，集群同步渲染引擎 |
| `DisplayClusterConfiguration` | Runtime | 配置系统，解析 .ndisplay 配置文件 |
| `DisplayClusterProjection` | Runtime | 投影映射与变形校正 |
| `DisplayClusterWarp` | Runtime | Warp/Blend 变形网格处理 |
| `DisplayClusterShaders` | Runtime | 自定义着色器（ICVFX、WarpBlend 等） |
| `DisplayClusterColorGrading` | Runtime | 色彩分级 LUT 管理 |
| `DisplayClusterLightCardEditor` | Runtime | Light Card / Flag 编辑器（虚拟制片补光） |
| `DisplayClusterMedia` | Runtime | 媒体输入输出（视频捕获/输出） |
| `DisplayClusterMoviePipeline` | Runtime | 集群渲染的电影序列导出 |
| `DisplayClusterMultiUser` | Runtime | 多用户编辑协作 |
| `DisplayClusterReplication` | Runtime | 网络复制 |
| `DisplayClusterMonitor` | Runtime | 性能监控与诊断 |
| `DisplayClusterOperator` | Runtime | Operator 面板（远程操控 UI） |
| `DisplayClusterScenePreview` | Runtime | 场景预览渲染器 |
| `DisplayClusterStageMonitoring` | Runtime | 舞台/片场状态监控 |
| `SharedMemoryMedia` | Runtime | GPU 共享内存媒体传输 |
| `ScalableMPCDI` | External | 第三方 MPCDI 格式解析库 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/RenderingAndGraphics/nDisplay/)（nDisplay 官方文档）
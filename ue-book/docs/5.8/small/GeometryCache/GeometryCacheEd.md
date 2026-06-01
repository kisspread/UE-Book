# Geometry Cache

> Support for distilled Geometry animations

| 属性 | 值 |
|---|---|
| 中文名 | 几何缓存 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryCache` (Runtime), `GeometryCacheEd` (Runtime), `GeometryCacheSequencer` (Runtime), `GeometryCacheStreamer` (Runtime), `GeometryCacheTracks` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-01-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache) | |

## 用途

Geometry Cache 插件提供对**预烘焙网格动画**的完整支持，用于导入、回放和编辑来自外部 DCC 工具（如 Maya、Houdini、Blender）导出的 Alembic (.abc) 几何体动画序列。

核心问题：对于布料模拟、流体表面、角色面部变形等需要逐帧记录顶点位置的复杂网格动画，传统的骨骼动画系统无法胜任。Geometry Cache 将每一帧的顶点位置数据预先烘焙存储，在运行时直接回放，避免了实时计算的开销。

插件包含以下模块：
- **GeometryCache**：核心运行时模块，处理数据存储与回放
- **GeometryCacheEd**：编辑器模块，提供资产编辑器、时间轴、预览视口、缩略图渲染
- **GeometryCacheSequencer**：Sequencer 集成模块，支持在过场动画中控制几何缓存
- **GeometryCacheStreamer**：流式加载模块，支持大数据集的按需加载
- **GeometryCacheTracks**：动画轨道模块，提供 Sequencer 中的专用轨道类型

## 使用场景

- 你在导入 Alembic 文件并选择"Import as Geometry Cache"时 → 使用 GeometryCache
- 你需要在过场动画 Sequencer 中精确控制网格动画的播放和混合 → 使用 GeometryCacheSequencer
- 你的场景中有大量逐帧变形的网格（如波浪、爆炸碎片）且需要高效回放 → 使用 GeometryCacheStreamer
- 你在编辑器中需要预览和编辑几何缓存资产的时间范围、播放设置 → 使用 GeometryCacheEd

## 蓝图用法

GeometryCacheEd 是编辑器模块，主要提供编辑器 UI 功能，公开的蓝图 API 较少。核心蓝图交互通过 GeometryCache 运行时模块的 `UGeometryCacheComponent` 完成（不在本模块范围内）。

### 编辑器资产交互

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenAssets` | 在编辑器中打开 GeometryCache 资产进行编辑 | `UAssetDefinition_GeometryCache` |
| `CanCreateActorFrom` | 判断能否从 GeometryCache 资产创建 Actor | `UActorFactoryGeometryCache` |
| `PostSpawnActor` | 拖放资产到场景后设置 GeometryCacheComponent | `UActorFactoryGeometryCache` |
| `AssignAssetToComponent` | 将 GeometryCache 资产绑定到组件 | `FGeometryCacheAssetBroker` |
| `GetAssetFromComponent` | 从组件获取绑定的 GeometryCache 资产 | `FGeometryCacheAssetBroker` |

### 使用示例

在编辑器中操作 GeometryCache 资产的典型流程：

1. **导入**：通过 Content Browser 的 Import 按钮导入 Alembic 文件，选择 Import as Geometry Cache
2. **双击编辑**：双击 GeometryCache 资产 → 打开 `FGeometryCacheAssetEditorToolkit` 提供的专用编辑器
3. **编辑器布局**：包含预览视口（`SGeometryCacheEditorViewport`）、动画属性面板、资产属性面板
4. **时间轴操作**：通过 `SGeometryCacheTimeline` 控件拖拽 scrubber 查看不同帧，设置播放范围
5. **拖放到场景**：将资产从 Content Browser 拖放到场景中，自动创建带有预绑定组件的 GeometryCacheActor

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCacheEdModule.h"
```

### 基本用法：注册几何缓存资产编辑器

GeometryCacheEd 模块通过 `FGeometryCacheAssetEditorToolkit` 提供完整的资产编辑器支持。

```cpp
// 来源: Private/GeometryCacheAssetEditorToolkit.h

// 初始化资产编辑器
void FGeometryCacheAssetEditorToolkit::InitCustomAssetEditor(
    const EToolkitMode::Type Mode,
    const TSharedPtr<class IToolkitHost>& InitToolkitHost,
    UGeometryCache* InCustomAsset)
{
    // 创建编辑器界面：视口 + 属性面板 + 时间轴
    // 自动注册以下标签页:
    //   - Viewport: 3D 预览视口
    //   - AssetProperties: 资产属性编辑
    //   - AnimationProperties: 动画属性编辑
    //   - PreviewSceneProperties: 预览场景设置
}
```

### 基本用法：资产定义注册

```cpp
// 来源: Classes/AssetDefinition_GeometryCache.h

// 自定义 GeometryCache 资产在 Content Browser 中的表现
UCLASS()
class UAssetDefinition_GeometryCache : public UAssetDefinitionDefault
{
    GENERATED_BODY()

public:
    // 显示名称
    virtual FText GetAssetDisplayName() const override;
    // Content Browser 中的图标颜色
    virtual FLinearColor GetAssetColor() const override;
    // 对应的 UObject 类
    virtual TSoftClassPtr<UObject> GetAssetClass() const override;
    // 是否支持导入
    virtual bool CanImport() const override;
    // 资产分类
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override;
    // 双击打开行为
    virtual EAssetCommandResult OpenAssets(const FAssetOpenArgs& OpenArgs) const override;
};
```

### 进阶用法：自定义时间轴控制器

```cpp
// 来源: Private/GeometryCacheTimeSliderController.h

// 创建自定义时间轴控制器，支持缩放和平移视图
FTimeSliderArgs Args;
Args.DisplayRate = FFrameRate(24, 1);  // 24fps 显示
Args.TickResolution = FFrameRate(24000, 1001);
Args.ViewRange = MakeAttribute(...);
Args.ClampRange = MakeAttribute(...);
Args.PlaybackRange = MakeAttribute(...);
Args.ScrubPosition = MakeAttribute(...);

FGeometryCacheTimeSlideController Controller(Args, WeakTimeline);

// 缩放视图范围（鼠标滚轮缩放）
Controller.ZoomByDelta(-1.0f, 0.5f);  // 缩小，中心点

// 平移视图范围（鼠标拖拽平移）
Controller.PanByDelta(0.5f);  // 向前平移 0.5 秒

// 从鼠标位置计算帧时间
FFrameTime FrameTime = Controller.GetFrameTimeFromMouse(Geometry, ScreenPosition);
```

### 进阶用法：资产 Broker 组件绑定

```cpp
// 来源: Classes/GeometryCacheAssetBroker.h

// 资产 Broker 负责 GeometryCache 资产与 UGeometryCacheComponent 之间的绑定
class FGeometryCacheAssetBroker : public IComponentAssetBroker
{
public:
    // 获取支持的资产类型
    UClass* GetSupportedAssetClass() override;  // 返回 UGeometryCache::StaticClass()

    // 将资产分配给组件
    bool AssignAssetToComponent(UActorComponent* InComponent, UObject* InAsset) override;

    // 从组件获取已绑定的资产
    UObject* GetAssetFromComponent(UActorComponent* InComponent) override;
};
```

## Demo 示例

以下示例展示如何自定义扩展 GeometryCache 编辑器功能：

```cpp
// GeometryCacheCustomEditor.h
#pragma once

#include "CoreMinimal.h"
#include "GeometryCacheEdModule.h"
#include "GeometryCacheTimelineBindingAsset.h"

class FGeometryCacheCustomEditor
{
public:
    /** 初始化编辑器并创建预览组件 */
    void Initialize(UGeometryCache* InGeometryCache);

    /** 获取当前 scrub 时间 */
    float GetCurrentTime() const;

    /** 跳转到指定时间 */
    void SeekToTime(float TimeInSeconds);

    /** 获取时间轴绑定资产 */
    TSharedPtr<FGeometryCacheTimelineBindingAsset> GetBindingAsset() const { return BindingAsset; }

private:
    TWeakObjectPtr<UGeometryCache> GeometryCacheAsset;
    TSharedPtr<FGeometryCacheTimelineBindingAsset> BindingAsset;
    TWeakObjectPtr<UGeometryCacheComponent> PreviewComponent;
};
```

```cpp
// GeometryCacheCustomEditor.cpp
#include "GeometryCacheCustomEditor.h"

void FGeometryCacheCustomEditor::Initialize(UGeometryCache* InGeometryCache)
{
    GeometryCacheAsset = InGeometryCache;

    // 创建预览用的组件
    PreviewComponent = NewObject<UGeometryCacheComponent>();
    PreviewComponent->SetGeometryCache(InGeometryCache);

    // 创建时间轴绑定
    BindingAsset = MakeShared<FGeometryCacheTimelineBindingAsset>(PreviewComponent);
}

float FGeometryCacheCustomEditor::GetCurrentTime() const
{
    if (BindingAsset.IsValid())
    {
        // GetScrubTime 返回当前 scrub 位置对应的秒数
        return BindingAsset->GetScrubTime();
    }
    return 0.0f;
}

void FGeometryCacheCustomEditor::SeekToTime(float TimeInSeconds)
{
    if (BindingAsset.IsValid())
    {
        // 获取帧率并转换为 FFrameTime
        FFrameRate FrameRate = BindingAsset->GetFrameRate();
        FFrameTime FrameTime = FrameRate.AsFrameTime(TimeInSeconds);
        BindingAsset->SetScrubPosition(FrameTime);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MeshUtilitiesCommon` | 网格工具通用功能，用于几何数据处理 |
| `UnrealEd` | 编辑器框架（资产编辑器、Actor 工厂等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联逻辑，消除重复代码 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退一次变更提交 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口客户端关联通知重构（与回退的提交相关） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新格式 |
| 2026-04-08 | `f5e682af` | [Sequencer] Simple View with toolable timeline initial release | Sequencer 简化视图模式与可工具化时间轴初始版本 |

### 维护评价

**状态：活跃维护中**

- 该插件于 2022 年从 Experimental 迁移至正式 Runtime 目录，表明已通过 Epic 内部质量审核
- 近期（2026 年 4-5 月）有持续的功能更新和代码重构，包括 Sequencer 新特性和引擎级 API 迁移
- 作为 Alembic 几何体动画的核心支持插件，与引擎的资产导入管线深度集成
- 源码规模适中（106 个文件），结构清晰，分为 5 个模块各司其职
- 推荐在需要导入/回放 Alembic 网格动画的项目中使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)
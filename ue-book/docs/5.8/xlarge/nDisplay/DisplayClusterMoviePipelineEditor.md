# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个用于实现**多台计算机同步集群渲染**的框架。它允许您将一个 Unreal Engine 应用程序的渲染任务分布到多个 PC 上，每台 PC 负责渲染整个画面或立体画面的一部分，最终组合成一个大的、多通道的显示输出。这主要应用于：
- **LED 虚拟摄影棚 (Virtual Production)**：驱动 LED 墙幕。
- **多投影仪设置**：如穹顶投影、CAVE（洞穴自动虚拟环境）。
- **多显示器阵列**：如飞行模拟器、驾驶模拟器。

**当前模块 `DisplayClusterMoviePipelineEditor`** 是 nDisplay 插件的一部分，它专门**扩展了 Sequencer 电影渲染管线（Movie Render Pipeline）**，使其能够为 nDisplay 集群渲染作业提供用户界面定制。它解决了在电影渲染设置中，如何直观地配置 nDisplay 特有的视口（Viewport）和集群节点（Cluster Node）选择的问题。

## 使用场景

- 你正在使用 nDisplay 驱动一个大型 LED 墙幕进行虚拟拍摄 → 你需要在 Sequencer 中渲染出最终影片。
- 你希望通过 **电影渲染管线 (Movie Render Pipeline)** 高质量地输出影片，且渲染管线需要精确控制哪些 nDisplay 视口参与渲染。
- 你需要在电影渲染作业（Movie Pipeline）的细节面板中，方便地从下拉列表中选择 nDisplay 的集群节点或视口名称，而不是手动输入字符串。

## 蓝图用法

本模块的核心功能是**编辑器 UI 定制**，而非直接暴露给蓝图的运行时函数。它通过 `IPropertyTypeCustomization` 接口，深度定制了 `UMoviePipeline` 和相关配置资产在“细节”（Details）面板中的显示方式，特别是对于 nDisplay 相关的设置（如 `AllowedViewportNamesList`）。用户交互主要通过编辑器 UI 进行，而非蓝图节点。

## C++ 用法

### 头文件引入

由于此模块主要为编辑器提供内部支持，不直接暴露公共 C++ API。其主要接口定义在私有头文件中。

### 基本用法

该模块通过注册自定义的属性布局（Property Layout）来工作。其入口在模块启动时注册，关闭时注销。

```cpp
// 来自：Source/DisplayClusterMoviePipelineEditor/Private/DisplayClusterMoviePipelineEditorModule.h
class FDisplayClusterMoviePipelineEditorModule : public IDisplayClusterMoviePipelineEditor
{
    // ...
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void RegisterCustomLayouts();
    void UnregisterCustomLayouts();
    // ...
};
```

### 进阶用法

核心功能由一系列属性定制器（Type Customization）类实现，例如 `FDisplayClusterMoviePipelineEditorSettingsCustomization`。这些类继承自 `FDisplayClusterMoviePipelineEditorBaseTypeCustomization`，后者又实现了 `IPropertyTypeCustomization` 接口。开发者如果需要扩展 nDisplay 电影渲染管线的 UI，可以参考这些类的实现模式。

```cpp
// 来自：Source/DisplayClusterMoviePipelineEditor/Private/Details/DisplayClusterMoviePipelineEditorSettingsCustomization.h
class FDisplayClusterMoviePipelineEditorSettingsCustomization final
    : public FDisplayClusterMoviePipelineEditorBaseTypeCustomization
{
    // ...
    virtual void Initialize(const TSharedRef<IPropertyHandle>& InPropertyHandle, IPropertyTypeCustomizationUtils& CustomizationUtils) override;
    virtual void SetHeader(const TSharedRef<IPropertyHandle>& InPropertyHandle, FDetailWidgetRow& InHeaderRow, IPropertyTypeCustomizationUtils& CustomizationUtils) override;
    virtual void SetChildren(const TSharedRef<IPropertyHandle>& InPropertyHandle, IDetailChildrenBuilder& InChildBuilder, IPropertyTypeCustomizationUtils& CustomizationUtils) override;
    // ...
};
```

## Demo 示例

本模块不包含运行时逻辑或可直接编译的独立功能示例。其价值在于为 `DisplayClusterMoviePipeline` 模块提供的资产（如 `UDisplayClusterMoviePipelineSettings`）在编辑器中提供增强的细节面板 UI。

启用此插件后，在 Sequencer 的电影渲染设置中配置 nDisplay 相关属性时，会看到经过定制的、包含可搜索下拉列表的界面，而不是普通的文本输入框。

## 模块依赖

从 `Build.cs` 文件分析，当前模块 `DisplayClusterMoviePipelineEditor` 依赖于：

| 模块 | 用途 |
|---|---|
| `DisplayClusterConfiguration` | 访问 nDisplay 集群配置数据结构，以获取可用的视口和集群节点列表。 |
| `DisplayClusterMoviePipeline` | 它所扩展的电影渲染管线模块。 |
| `UnrealEd` | 提供编辑器框架、细节面板、属性处理等核心编辑器功能。 |
| `EditorWidgets` | 提供编辑器专用的 Slate 控件。 |
| `LevelEditor` | 与关卡编辑器集成。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 nDisplay 添加 EXR 多层输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 在电影渲染管线中，将独立的 WarpBlendAlpha 模式合并到 WarpBlend 模式中。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 Movie Render Graph 中拓扑感知摄像机的命名问题；修复 MPCDI/ICVFX 着色器中的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码的备用方案中，正确处理非默认的显示伽马值（DisplayGamma）。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复当 GUI 纹理尺寸小于视口尺寸时产生的闪烁问题。 |

### 维护评价

- **活跃维护**：该插件及其子模块仍在被 Epic Games 积极维护和更新。最近的提交记录（集中在 2026 年 5 月）显示了一系列功能增强和 bug 修复，表明它在虚拟制片工作流中仍然是核心组件。
- **创建时间**：自 2018 年随 UE4.20 发布，已有 8 年历史，是一个成熟的生产级解决方案。
- **模块状态**：`DisplayClusterMoviePipelineEditor` 模块类型标记为 `Runtime`，这通常意味着它包含在游戏运行时构建中，但其主要功能（UI 定制）仅在编辑器中生效。实际使用时，此插件**默认未启用**，需要在项目设置中手动开启。
- **推荐使用**：对于进行虚拟制片（Virtual Production）或多屏幕/投影同步渲染的项目，此插件是**必需**的。它持续获得支持，功能完善，是 Epic 官方推荐的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-unreal-engine/) (通常可在 UE 官网的“虚拟制片”或“nDisplay”部分找到)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)
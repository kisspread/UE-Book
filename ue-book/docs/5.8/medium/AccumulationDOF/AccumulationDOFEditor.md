# Accumulation Depth of Field

> Thin-lens aperture-sampled depth of field for production rendering

| 属性 | 值 |
|---|---|
| 中文名 | 累积景深 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AccumulationDOF` (Runtime), `AccumulationDOFEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-31 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AccumulationDOF) | |

## 用途

AccumulationDOF 是一个面向**影视级制作渲染**的景深插件，通过**薄透镜模型**从光圈上多个采样点分别渲染场景，然后累积叠加结果来实现高质量景深效果。

与 UE 内置的实时 DOF（通常基于 CoC 散圆模糊）不同，此插件采用**物理正确的多视角累积**方式，能真实还原视差缺失带来的伪影问题，同时保留延迟渲染的全部 LookDev（材质外观开发）效果。

**核心原理**：将光圈表面划分为多个采样点，每个采样点作为一个虚拟摄像机渲染一帧，最终将所有帧叠加平均。采样数越多质量越高，渲染时间线性增长。

**支持的光学特性**：
- **Petzval 涡旋散景**（Swirly Bokeh）
- **猫眼效应 / 桶形畸变**（Cat's Eye / Barrel）
- **变形压缩**（Anamorphic Squeeze）
- **多频段横向色差**（Lateral Chromatic Aberration）
- **多频段轴向色差**（Axial Chromatic Aberration）
- **球面像差**（Spherical Aberration）
- **自定义散景纹理**（User-customizable Bokeh Texture）

**重要限制**：此插件专为**离线/生产渲染**设计，不适合实时游戏场景。渲染时间随采样数线性增长。

## 使用场景

- 你在制作电影或广告镜头，需要电影级物理正确的景深散景效果 → 用 AccumulationDOF
- 你对内置 DOF 的散景质量不满意，需要真实猫眼效果和色差 → 用 AccumulationDOF
- 你在使用 Movie Render Graph（MRG）进行最终渲染，需要最高质量景深 → 在 MRG 中启用 AccumulationDOF Pass
- 你需要在编辑器中实时预览累积景深效果 → 通过视口 Scalability 菜单开启

## 编辑器用法

### 编辑器预览

此插件的编辑器集成通过**视口 Scalability 下拉菜单**访问：

1. 打开关卡编辑器视口
2. 点击视口左上角的 **Scalability** 下拉菜单
3. 找到 **Accumulation DOF** 区域
4. 勾选 **Toggle Accumulate** 开启累积预览

### 视口设置

| 设置 | 说明 | 默认值 |
|---|---|---|
| Enable Accumulation | 开启/关闭该视口的累积景深预览 | 关闭 |
| Use Camera Settings | 使用摄像机上 AccumulationDOFComponent 的设置 | 关闭 |
| Num Aperture Samples | 光圈采样数（越多质量越高，越慢） | 256 |
| DOF Splat Size | 散景填充尺寸（光圈直径的比例） | 0.125 |
| Samples Per Frame | 分摊模式下每帧渲染的采样数 | 2 |

### 快捷操作

- **One-shot Capture**：阻塞式一次性渲染所有采样，立即得到完整结果
- **Restart Accumulation**：重新开始累积
- **Freeze/Unfreeze**：冻结当前结果（防止场景变化后重新累积）/ 解冻

### MRG（Movie Render Graph）集成

在 Movie Render Graph 中添加 **Accumulation DOF** Pass：
- 将 Spatial Samples 设为 1
- 将 Temporal Samples 设为所需的高质量运动模糊值

> ⚠️ 注意：光圈渲染当前不会在时间样本间分摊。

## 蓝图用法

根据源码分析，此插件的核心逻辑通过编辑器视口集成和 MRG Pipeline Pass 暴露，编辑器模块中未发现 `BlueprintCallable` 函数。运行时模块中应存在 `UAccumulationDOFComponent`，可附加到 CineCameraActor 上。

## C++ 用法

### 核心架构

此插件由以下核心类组成：

| 类 | 作用 |
|---|---|
| `FAccumulationDOFViewportExtension` | 场景视图扩展，负责在特定视口中协调分摊渲染 |
| `FAccumulationDOFViewportManager` | 管理每个视口的 DOF 配置和视图扩展 |
| `FAccumulationDOFEditorModule` | 编辑器模块，提供视口菜单集成 |
| `UAccumulationDOFLevelViewportSettings` | 持久化每个视口的设置（Config 对象） |
| `UApertureSampler` | 光圈采样器实例（拥有渲染目标） |

### 摄像机参数快照（变更检测）

```cpp
// 来源: AccumulationDOFViewportExtension.h
// 用于检测摄像机参数变化，触发重新累积
struct FCameraParamsSnapshot
{
    FVector Location = FVector::ZeroVector;
    FRotator Rotation = FRotator::ZeroRotator;
    float FocusDistance = 0.0f;
    float Aperture = 0.0f;
    float FocalLength = 0.0f;

    bool Equals(const FCameraParamsSnapshot& Other, float Tolerance = 0.01f) const
    {
        return Location.Equals(Other.Location, Tolerance)
            && Rotation.Equals(Other.Rotation, Tolerance)
            && FMath::IsNearlyEqual(FocusDistance, Other.FocusDistance, Tolerance)
            && FMath::IsNearlyEqual(Aperture, Other.Aperture, 0.001f)
            && FMath::IsNearlyEqual(FocalLength, Other.FocalLength, Tolerance);
    }
};
```

### 场景视图扩展集成

```cpp
// 来源: AccumulationDOFViewportExtension.h
// FAccumulationDOFViewportExtension 继承 FSceneViewExtensionBase
// 通过 SubscribeToPostProcessingPass 在 Motion Blur Pass 后注入景深处理

class FAccumulationDOFViewportExtension : public FSceneViewExtensionBase, public FGCObject
{
public:
    // 优先级 -5，确保在其他扩展之后执行
    virtual int32 GetPriority() const override { return -5; }

    // 阻塞式一次性捕获所有采样
    void CaptureOneshot();

    // 获取累积进度 (0-1)
    float GetProgressFraction() const;

    // 检查累积是否完成
    bool IsComplete() const;

    // 冻结/解冻预览
    bool IsFrozen() const { return bIsFrozen; }
    void Unfreeze();
    void RestartAccumulation();
};
```

### 视口设置持久化

```cpp
// 来源: AccumulationDOFEditorSettings.h
// 配置自动保存到 AccumulationDOF.ini
UCLASS(config = AccumulationDOF)
class UAccumulationDOFLevelViewportSettings : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(config)
    TArray<FAccumulationDOFPerViewportSettingsPair> ViewportsSettings;

    TOptional<FAccumulationDOFViewportSettings> GetViewportSettings(FName ViewportIdentifier) const;
    void SetViewportSettings(FName ViewportIdentifier, const FAccumulationDOFViewportSettings& Settings);
};
```

### 视口管理器操作

```cpp
// 来源: AccumulationDOFViewportManager.h
// 通过 FAccumulationDOFViewportManager 管理各视口
FAccumulationDOFViewportManager& Manager = FAccumulationDOFEditorModule::Get().GetViewportManager();

// 查找或创建视口配置
FAccumulationDOFViewportSettings& Settings = Manager.FindOrAddViewportSettings(ViewportClient);

// 阻塞式一次性捕获
Manager.CaptureOneshot(ViewportClient);

// 重新开始累积
Manager.RestartAccumulation(ViewportClient);

// 解冻视口
Manager.Unfreeze(ViewportClient);
```

### 场景变更自动检测

视图扩展会自动监听以下事件并触发重新累积：
- Actor 移动 (`OnSceneActorMoved`)
- Level Actor 添加/删除 (`OnSceneLevelActorAdded` / `OnSceneLevelActorDeleted`)
- 组件 Transform 变更 (`OnSceneComponentTransformChanged`)
- 对象属性变更 (`OnSceneObjectPropertyChanged`)

当冻结状态下检测到摄像机参数变化时，会自动解冻并重新累积。

## Demo 示例

此插件为编辑器集成型渲染扩展，无独立可编译的最小 C++ 示例。推荐的使用方式是在编辑器中直接操作：

1. 启用插件：Edit → Plugins → 搜索 "Accumulation DOF" → 启用 → 重启编辑器
2. 打开关卡编辑器，确保视口中有 CineCameraActor
3. Piloting（驾驶）该 CineCameraActor
4. 点击视口 Scalability 下拉菜单 → Accumulation DOF → 勾选 Toggle Accumulate
5. 等待累积完成（视口左下角显示进度）
6. 调整 Num Aperture Samples 和 Splat Size 以平衡质量与速度

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieRenderPipeline` | Movie Render Graph (MRG) 集成，用于最终渲染输出 |

注意：运行时模块依赖了 `PropertyEditor`（对于 Runtime 类型模块较不寻常），可能用于编辑器内的属性自定义面板。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-19 | `6aedc10e` | MoviePipeline: Updated ADOF support within MRG to support high-res tiling. | MRG 中 ADOF 支持高分辨率分片渲染 |
| 2026-05-12 | `3af0fac2` | MoviePipeline: Added some telemetry for newly-added graph features, and existing MRQ/MRG features wh | 为新增的 MRG 图形功能及已有 MRQ/MRG 功能添加遥测数据 |
| 2026-05-12 | `67c6995d` | AccumulationDOF: Reduce default aperture NumSamples from 512 to 256 | 将默认光圈采样数从 512 降低至 256 |
| 2026-05-12 | `657a7d63` | MoviePipeline: Removed Accumulation Depth of Field support from MRQ. ADOF support in MRQ was tempora | 从 MRQ 中移除 ADOF 支持，MRQ 集成为临时方案，正式迁移至 MRG |
| 2026-05-12 | `bc8a105a` | MRG: Fix lens distortion renders being over-cropped due to MRG always cropping the overscan. | 修复 MRG 中镜头畸变渲染因过度裁剪 overscan 导致的画面被多裁问题 |

### 维护评价

- **状态**：🟢 **活跃开发中**
- 创建于 2026 年 1 月，至今约 4 个月，为全新实验性插件
- 近期（2026 年 5 月）有密集的功能更新，包括从 MRQ 迁移至 MRG、高分辨率分片支持、默认参数优化等
- 标记为 `IsExperimentalVersion = true`，且 `EnabledByDefault = false`，需手动启用
- 开发团队活跃（Epic Games 内部开发，有 Jira 追踪 UE-361334）
- 已知待完成工作：MRG 集成完善、抗锯齿改进、运动模糊改进
- **推荐使用**：适合需要电影级景深质量的虚拟制片工作流，但请注意其**实验性**状态，API 和行为可能在后续版本中发生变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AccumulationDOF)
- [测试用例]（暂未发现独立测试文件）
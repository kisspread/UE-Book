# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、编辑器工具） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design（原名 Avalanche）是一个面向**虚拟制作（Virtual Production）**领域的综合性动态图形设计工具链。它为 UE5 提供了类似 After Effects 的合成、设计和广播能力。

**核心解决的问题**：传统上，实时广播级动态图形（Motion Graphics）需要借助外部工具（如 After Effects、Cinema 4D）完成设计，再导入引擎播放。Motion Design 将整套流程搬入 Unreal Engine，让设计师可以直接在引擎内完成 2D/3D 图形设计、材质合成、场景编排、属性动画和播出控制。

该插件包含 43 个模块，覆盖以下子系统：

| 子系统 | 模块 | 说明 |
|---|---|---|
| **遮罩系统** | `AvalancheMask`, `AvalancheMaskEditor` | 2D 遮罩的读写、材质修改、通道管理 |
| **材质设计** | `AvalancheMaterial` | 动态材质（Dynamic Material Designer）集成 |
| **形状生成** | `AvalancheShapes`, `AvalancheShapesEditor` | 参数化 2D/3D 形状 |
| **文字排版** | `AvalancheText`, `AvalancheTextEditor` | 3D 文字渲染与排版 |
| **克隆/效果器** | `AvalancheEffectors`, `AvalancheEffectorsEditor` | Cloner & Effector 模式系统 |
| **属性动画** | `AvalanchePropertyAnimator` | 对象属性的关键帧动画（集成 Sequencer） |
| **修改器栈** | `AvalancheModifiers`, `AvalancheModifiersEditor` | Actor 排列、变换修改器 |
| **场景树** | `AvalancheSceneTree` | 场景层级管理 |
| **媒体集成** | `AvalancheMedia`, `AvalancheMediaEditor` | 媒体输入输出（Media IO） |
| **远程控制** | `AvalancheRemoteControl` | 远程控制面板集成 |
| **MRQ 集成** | `AvalancheMRQ`, `AvalancheMRQEditor` | Movie Render Queue 支持 |
| **过渡动画** | `AvalancheTransition` | 元素间的过渡效果 |
| **SVG 导入** | `AvalancheSVGEditor` | SVG 矢量图形导入 |

> **注意**：本插件于 2025 年 5 月从 `Engine/Plugins/Experimental` 迁移到 `Engine/Plugins/VirtualProduction`，标志着正式脱离实验阶段。但 `IsBetaVersion` 未设置，已标记为正式可用。

---

## 模块列表

由于该插件包含 43 个模块（2060+ 源文件），属于 **xlarge** 规模，按子系统分页文档化。

| 模块 | 类型 | 说明 | 文档链接 |
|---|---|---|---|
| `AvalancheMask` | Runtime | 2D 遮罩系统 | [AvalancheMask 文档](./AvalancheMask.md) |
| `AvalancheMaskEditor` | Runtime | 遮罩编辑器扩展 | 见 AvalancheMask 文档 |
| `AvalancheMaterial` | Runtime | 动态材质系统 | - |
| `AvalancheShapes` | Runtime | 参数化形状 | - |
| `AvalancheText` | Runtime | 3D 文字 | - |
| `AvalancheEffectors` | Runtime | 克隆/效果器 | - |
| `AvalancheModifiers` | Runtime | Actor 修改器 | - |
| `AvalanchePropertyAnimator` | Runtime | 属性动画 | - |
| `AvalancheSceneTree` | Runtime | 场景树 | - |
| `AvalancheMedia` | Runtime | 媒体集成 | - |
| `AvalancheMRQ` | Runtime | 渲染队列 | - |
| `AvalancheTransition` | Runtime | 过渡动画 | - |
| `AvalancheRemoteControl` | Runtime | 远程控制 | - |
| `AvalancheSequence` | Runtime | 序列集成 | - |
| `AvalancheViewport` | Runtime | 视口扩展 | - |
| `AvalancheTag` | Runtime | 标签系统 | - |
| `AvalancheSequencer` | Runtime | Sequencer 扩展 | - |
| `AvalancheSVGEditor` | Runtime | SVG 导入 | - |
| `AvalancheOutliner` | Runtime | 大纲视图 | - |
| `AvalancheCore` | Runtime | 核心基础 | - |
| `AvalancheCamera` | Runtime | 相机系统 | - |
| `AvalancheSceneRig` | Runtime | 场景装备 | - |

> 本文档重点覆盖 `AvalancheMask` 模块。其余模块文档待补充。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将场景设置和大纲面板从关卡编辑器中独立出来，分组优化布局 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 新增 MRQ 分析功能，用于追踪 Rundown 页面设置的使用情况 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在播出控制工具栏新增页面加载选项（全部/下一个/选中） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制关闭 Text3D 和形状的碰撞检测 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/取消关联的通知逻辑 |

### 维护评价

- **活跃维护**：最近提交密集（几乎每天都有更新），持续进行功能增强和 UI 优化
- **创建时间**：2025 年 5 月从 Experimental 迁移到 VirtualProduction，实际开发历史可能更长
- **模块规模**：43 个模块、2000+ 源文件，说明 Epic 对此投入大量工程资源
- **依赖众多**：依赖 Text3D、Geometry Scripting、Remote Control、Dynamic Material 等多个插件
- **推荐使用**：✅ 推荐用于虚拟制作/广播级动态图形场景。作为 Epic 官方维护的 Virtual Production 工具链，更新频率高、功能完善

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [AvalancheMask 模块文档](./AvalancheMask.md)

---

# AvalancheMask（子模块）

## 用途

AvalancheMask 是 Motion Design 的 **2D 遮罩（Mask）子系统**，用于实现基于场景 Actor 的 2D 遮罩效果。它的工作原理是：

1. **写入方（Write）**：将指定 Actor 的渲染结果写入一个遮罩通道（Mask Channel），生成遮罩纹理
2. **读取方（Read）**：将遮罩通道的纹理应用到目标 Actor 的材质上，实现可见/不可见区域控制

这类似于 After Effects 的 Track Matte 功能——一个图层（Source）的形状/透明度定义了另一个图层（Target）的可见区域。

### 架构概览

```
┌─────────────────────────────────────────────────────┐
│              UAvaMask2DBaseModifier                  │  抽象基类
│  ┌───────────────────────┐ ┌───────────────────────┐│
│  │ UAvaMask2DWriteModifier│ │ UAvaMask2DReadModifier││  Write: 写遮罩纹理
│  │ (Source 模式)          │ │ (Target 模式)         ││  Read: 应用遮罩
│  └───────────────────────┘ └───────────────────────┘│
└─────────────────────────────────────────────────────┘
         │                          │
         ▼                          ▼
┌─────────────────────┐   ┌─────────────────────────┐
│ GeometryMaskCanvas   │   │ Material Bridge         │  遮罩画布 ←→ 材质参数
│ (遮罩通道画布)       │   │ (材质实例管理)          │
└─────────────────────┘   └─────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
           Actor 材质句柄   Text3D 材质句柄   Shape 材质句柄
           (FAvaMaskActor  (FAvaMaskText3D   (FAvaMaskAvaShape
            MaterialColl-   ActorMaterial     MaterialColl-
            ectionHandle)   CollectionHandle) ectionHandle)
```

### 关键概念

| 概念 | 说明 |
|---|---|
| **Mask Channel（遮罩通道）** | 由 `FName` 标识的遮罩画布，可被多个 Read/Write 修饰器共享 |
| **Source（写入源）** | 设置为 Write 模式的 Actor，将其渲染结果写入通道 |
| **Target（目标）** | 设置为 Read 模式的 Actor，从通道读取遮罩并应用到材质 |
| **Canvas（画布）** | `UGeometryMaskCanvas` 实例，底层渲染遮罩纹理的载体 |
| **Material Bridge** | 负责将遮罩参数应用到不同类型的材质（标准材质、Text3D、Shape 等） |
| **Material Instance** | 通过子系统缓存和复用 `UMaterialInstanceDynamic`，避免材质实例膨胀 |

---

## 属性表

| 属性 | 值 |
|---|---|
| 中文名 | 遮罩模块 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheMask) | |

---

## 使用场景

- 你在做一个电视节目播出画面 → 用遮罩实现字幕/图形的裁剪效果
- 你需要让一个 3D 文字只在某个形状区域内可见 → Write 写形状遮罩，Read 应用到文字
- 你需要制作一个"聚光灯"效果，只照亮场景的一部分 → 用遮罩控制灯光/材质可见性
- 你要让多个元素共享同一个遮罩通道 → 使用同一个 Channel 名称
- 你需要模糊或羽化遮罩边缘 → 使用 Blur/Feathering 参数

---

## 蓝图用法

所有遮罩修饰器都作为 **Actor Modifier（Actor 修改器）** 使用，通过 Actor 的 Details 面板或蓝图添加。

### 核心节点

#### UAvaMask2DBaseModifier（基类属性）

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `bUseParentChannel` | bool | 是否从父级继承通道名 | `UAvaMask2DBaseModifier` |
| `Channel` | FName | 遮罩通道名称 | `UAvaMask2DBaseModifier` |
| `bInverted` | bool | 是否反转遮罩（可见↔不可见） | `UAvaMask2DBaseModifier` |
| `bUseBlur` | bool | 是否启用模糊 | `UAvaMask2DBaseModifier` |
| `BlurStrength` | float | 模糊强度（默认 16.0） | `UAvaMask2DBaseModifier` |
| `bUseFeathering` | bool | 是否启用羽化 | `UAvaMask2DBaseModifier` |
| `OuterFeatherRadius` | int32 | 外部羽化半径（默认 16） | `UAvaMask2DBaseModifier` |
| `InnerFeatherRadius` | int32 | 内部羽化半径（默认 16） | `UAvaMask2DBaseModifier` |

#### UAvaMask2DReadModifier（读取/Target 模式）

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `BaseOpacity` | float | 基础不透明度 0.0-1.0（默认 0.0） | `UAvaMask2DReadModifier` |
| `AdditionalChannels` | TArray\<FName\> | 附加读取通道列表 | `UAvaMask2DReadModifier` |

#### UAvaMask2DWriteModifier（写入/Source 模式）

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `WriteOperation` | EGeometryMaskCompositeOperation | 写入方式：Add（叠加）或 Subtract（减去） | `UAvaMask2DWriteModifier` |

#### UAvaMask2DBaseModifier（工具函数）

| 函数 | 说明 | 所在类 |
|---|---|---|
| `FindMaskModifierOnActor(AActor*)` | 查找 Actor 上的遮罩修饰器（静态） | `UAvaMask2DBaseModifier` |
| `GenerateUniqueMaskName()` | 基于 Actor 生成唯一遮罩名 | `UAvaMask2DBaseModifier` |
| `VisualizeMask()` | 可视化当前遮罩（仅编辑器） | `UAvaMask2DBaseModifier` |

### 使用示例（蓝图描述）

**基础遮罩效果：让形状 Actor 裁剪文字 Actor**

1. **设置写入源（Source）**：
   - 选中一个几何体 Actor（如一个平面）
   - 在 Details 面板 → Actor Modifiers → 添加 "Mask 2D Write Modifier"
   - 设置 `Channel` = "MyMask"
   - 设置 `WriteOperation` = Add

2. **设置读取目标（Target）**：
   - 选中一个 Text3D Actor
   - 添加 "Mask 2D Read Modifier"
   - 设置 `Channel` = "MyMask"（与 Source 相同）
   - 设置 `BaseOpacity` = 0.0（完全透明）或 0.5（半透明）
   - 可选：启用 `Blur` 和 `Feathering` 柔化边缘

3. **结果**：Text3D 只在几何体覆盖的区域内可见。

**蓝图运行时控制**：

```
// 获取 Actor 上的 Mask2D Read Modifier
UAvaMask2DReadModifier* ReadMod = UAvaMask2DBaseModifier::FindMaskModifierOnActor(MyTextActor);
if (ReadMod)
{
    ReadMod->SetIsInverted(true);    // 反转遮罩
    ReadMod->SetBaseOpacity(0.5f);   // 设置基础透明度
    ReadMod->UseBlur(true);          // 启用模糊
    ReadMod->SetBlurStrength(32.0f); // 设置模糊强度
}
```

---

## C++ 用法

### 头文件引入

```cpp
#include "Mask2D/AvaMask2DBaseModifier.h"
#include "Mask2D/AvaMask2DReadModifier.h"
#include "Mask2D/AvaMask2DWriteModifier.h"
#include "AvaMaskTypes.h"
```

### 基本用法

**查找 Actor 上的遮罩修饰器**

```cpp
// 在任意 Actor 上查找已添加的遮罩修饰器
// 来源：Public/Mask2D/AvaMask2DBaseModifier.h - FindMaskModifierOnActor
UAvaMask2DBaseModifier* MaskModifier = UAvaMask2DBaseModifier::FindMaskModifierOnActor(MyActor);
if (MaskModifier)
{
    // 获取当前通道名
    FName ChannelName = MaskModifier->GetChannel();
    
    // 检查是否使用父级通道
    bool bUsesParent = MaskModifier->UseParentChannel();
    
    // 设置反转
    MaskModifier->SetIsInverted(true);
}
```

**配置读取修饰器**

```cpp
// 来源：Public/Mask2D/AvaMask2DReadModifier.h
// 假设 ReadModifier 已通过修改器系统添加到 Actor
UAvaMask2DReadModifier* ReadModifier = Cast<UAvaMask2DReadModifier>(MaskModifier);
if (ReadModifier)
{
    // 设置基础不透明度（0.0 = 完全透明，1.0 = 完全不透明）
    ReadModifier->SetBaseOpacity(0.0f);
    
    // 配置通道
    ReadModifier->SetChannel(FName("MyChannel"));
    
    // 配置模糊
    ReadModifier->UseBlur(true);
    ReadModifier->SetBlurStrength(24.0f);
    
    // 配置羽化
    ReadModifier->UseFeathering(true);
    ReadModifier->SetOuterFeatherRadius(32);
    ReadModifier->SetInnerFeatherRadius(16);
}
```

**配置写入修饰器**

```cpp
// 来源：Public/Mask2D/AvaMask2DWriteModifier.h
UAvaMask2DWriteModifier* WriteModifier = Cast<UAvaMask2DWriteModifier>(MaskModifier);
if (WriteModifier)
{
    // 设置写入模式为叠加（Add）或减去（Subtract）
    WriteModifier->SetWriteOperation(EGeometryMaskCompositeOperation::Add);
}
```

### 进阶用法

**操作材质参数结构体**

```cpp
// 来源：Public/AvaMaskTypes.h - FAvaMask2DMaterialParameters
FAvaMask2DMaterialParameters MaterialParams;
MaterialParams.CanvasName = FName("MyChannel");
MaterialParams.bInvert = true;
MaterialParams.BaseOpacity = 0.5f;
MaterialParams.Padding = FVector2f(10.0f, 10.0f);
MaterialParams.bApplyFeathering = true;
MaterialParams.OuterFeatherRadius = 32.0f;
MaterialParams.InnerFeatherRadius = 16.0f;
MaterialParams.BlendMode = EBlendMode::BLEND_Masked;

// 将参数应用到材质实例
UMaterialInstanceDynamic* MID = /* 获取 MID */;
MaterialParams.ApplyToMID(MID);

// 从已有材质读取参数
FAvaMask2DMaterialParameters StoredParams;
StoredParams.StoreFromMaterial(MyMaterialInterface);

// 比较两组参数是否相同
bool bSame = MaterialParams.HasSameParameters(StoredParams);
```

**使用遮罩材质实例子系统缓存 MID**

```cpp
// 来源：Internal/Materials/AvaMaskMaterialInstanceSubsystem.h
// 获取引擎级子系统
UAvaMaskMaterialInstanceSubsystem* Subsystem = GEngine->GetEngineSubsystem<UAvaMaskMaterialInstanceSubsystem>();
UAvaMaskMaterialInstanceProvider* Provider = Subsystem->GetMaterialInstanceProvider();

// 根据材质和掩码键查找或创建 MID
uint32 InstanceKey = UE::AvaMask::Internal::MakeMaterialInstanceKey(
    ParentMaterial, ChannelName, EBlendMode::BLEND_Masked);
UMaterialInstanceDynamic* MID = Provider->FindOrAddMID(
    ParentMaterial, InstanceKey, EBlendMode::BLEND_Masked);
```

**管理遮罩状态（保存/恢复）**

```cpp
// 来源：Public/Mask2D/AvaMask2DMaskState.h
FAvaMask2DMaskState MaskState;

// 从材质实例保存状态
MaskState.Store(MyMID);

// 恢复到材质实例
MaskState.Apply(MyMID);

// 保存带材质槽标识的状态
FAvaMask2DMaterialSlotId SlotId(MaterialContainerPath, BridgeSlotId, BaseMaterial);
FAvaMask2DMaterialMaskState MaterialMaskState(SlotId);
MaterialMaskState.Store();  // 保存当前状态
MaterialMaskState.Apply();  // 恢复状态
```

---

## 模块依赖

以下为 AvalancheMask 模块的 **独特** 依赖项（不列出 Core/Engine/Slate 等标准模块）：

| 模块 | 用途 |
|---|---|
| `GeometryMask` | 底层几何遮罩引擎，提供 Canvas、MaskWriter 等核心渲染能力 |
| `GeometryMaskCore` | 遮罩核心类型定义 |
| `ActorModifierCore` | Actor 修改器框架基类 |
| `AvaMaterial` | 动态材质（Material Designer）集成，提供 `IAvaMaterialHandle` |
| `Text3D` | 3D 文字组件支持，用于 Text3D Actor 的遮罩材质处理 |
| `StructUtils` | `FInstancedStruct` / `FStructView` 结构体工具 |

---

## 核心类型参考

### 枚举

```cpp
// 来源：Public/Mask2D/AvaMask2DBaseModifier.h
UENUM(BlueprintType)
enum class EAvaMask2DMode : uint8
{
    Read,    // Target - 使用遮罩通道将遮罩应用到此几何体
    Write,   // Source - 使用遮罩通道将此几何体渲染到遮罩
};
```

### 结构体

| 结构体 | 说明 |
|---|---|
| `FAvaMask2DComponentMaterialPath` | 组件+材质槽索引对，用于标识特定材质槽 |
| `FAvaMask2DMaterialParameters` | 材质遮罩参数（画布名、翻转、透明度、羽化等） |
| `FAvaMask2DSubjectParameters` | 修饰器目标的完整参数集合 |
| `FAvaMask2DMaskState` | 材质遮罩状态，可保存/恢复 |
| `FAvaMask2DMaterialSlotId` | 带材质基础引用的槽标识 |
| `FAvaMask2DMaterialMaskState` | 材质实例及其遮罩状态的完整记录 |

### 材质句柄层级

```
IAvaObjectHandle (基础接口)
  └── IAvaMaterialHandle (材质句柄接口)
        ├── FAvaMaterialInstanceHandle (标准材质实例)
        │     ├── FAvaMaskMaterialInstanceHandle (遮罩用材质实例)
        │     │     └── FAvaMaskMediaPlateMaterialHandle (MediaPlate 材质)
        │     ├── FAvaDesignedMaterialHandle (Material Designer 材质)
        │     │     └── FAvaMaskDesignedMaterialHandle (遮罩用 Designer 材质)
        │     └── FAvaParametricMaterialHandle (参数化形状材质)
        │           └── FAvaMaskParametricMaterialHandle (遮罩用参数化材质)
        └── IAvaMaskMaterialHandle (遮罩材质句柄接口)
              └── TAvaMaskMaterialHandle<T> (模板基类)

IAvaMaskMaterialCollectionHandle (材质集合句柄接口)
  └── TAvaMaskMaterialCollectionHandle<T> (模板基类)
        ├── FAvaMaskActorMaterialCollectionHandle (标准 Actor)
        ├── FAvaMaskText3DActorMaterialCollectionHandle (Text3D Actor)
        └── FAvaMaskAvaShapeMaterialCollectionHandle (Shape Actor)
```

### 子系统

| 子系统 | 类型 | 说明 |
|---|---|---|
| `UAvaMaskSubsystem` | UEngineSubsystem | 管理默认遮罩材质、最近通道名 |
| `UAvaMaskMaterialInstanceSubsystem` | UEngineSubsystem | 全局 MID 缓存与工厂管理 |
| `UAvaMaskMaterialInstanceWorldSubsystem` | UWorldSubsystem | 关卡级 MID 副本管理 |
| `UAvaMaskMaterialInstanceProvider` | UObject | MID 查找/创建的具体实现 |

---

## Demo 示例

> **注意**：遮罩修饰器通过修改器系统（Actor Modifier）添加到 Actor，通常在编辑器 Details 面板操作。以下展示如何在 C++ 中程序化地查询和控制遮罩。

### 查找并配置遮罩修饰器

```cpp
// MyMaskController.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyMaskController.generated.h"

class UAvaMask2DBaseModifier;
class UAvaMask2DReadModifier;
class UAvaMask2DWriteModifier;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyMaskController : public UActorComponent
{
    GENERATED_BODY()

public:
    /** 在指定 Actor 上查找并配置遮罩修饰器 */
    UFUNCTION(BlueprintCallable, Category = "Mask")
    void ConfigureMask(AActor* TargetActor, FName ChannelName, bool bInvert);

    /** 切换遮罩的可见性（通过反转实现） */
    UFUNCTION(BlueprintCallable, Category = "Mask")
    void ToggleMaskVisibility(AActor* TargetActor);

    /** 设置模糊参数 */
    UFUNCTION(BlueprintCallable, Category = "Mask")
    void SetMaskBlur(AActor* TargetActor, bool bEnable, float Strength);

protected:
    /** 缓存的遮罩修饰器引用 */
    UPROPERTY()
    TWeakObjectPtr<UAvaMask2DBaseModifier> CachedModifier;
};
```

```cpp
// MyMaskController.cpp
#include "MyMaskController.h"
#include "Mask2D/AvaMask2DBaseModifier.h"
#include "Mask2D/AvaMask2DReadModifier.h"
#include "Mask2D/AvaMask2DWriteModifier.h"

void UMyMaskController::ConfigureMask(AActor* TargetActor, FName ChannelName, bool bInvert)
{
    if (!TargetActor)
    {
        return;
    }

    // 查找 Actor 上已有的遮罩修饰器
    UAvaMask2DBaseModifier* Modifier = UAvaMask2DBaseModifier::FindMaskModifierOnActor(TargetActor);
    if (!Modifier)
    {
        UE_LOG(LogTemp, Warning, TEXT("No mask modifier found on actor: %s"), *TargetActor->GetName());
        return;
    }

    // 配置通道
    Modifier->SetChannel(ChannelName);

    // 配置反转
    Modifier->SetIsInverted(bInvert);

    // 缓存引用
    CachedModifier = Modifier;
}

void UMyMaskController::ToggleMaskVisibility(AActor* TargetActor)
{
    UAvaMask2DBaseModifier* Modifier = UAvaMask2DBaseModifier::FindMaskModifierOnActor(TargetActor);
    if (Modifier)
    {
        Modifier->SetIsInverted(!Modifier->IsInverted());
    }
}

void UMyMaskController::SetMaskBlur(AActor* TargetActor, bool bEnable, float Strength)
{
    UAvaMask2DBaseModifier* Modifier = UAvaMask2DBaseModifier::FindMaskModifierOnActor(TargetActor);
    if (Modifier)
    {
        Modifier->UseBlur(bEnable);
        if (bEnable)
        {
            Modifier->SetBlurStrength(Strength);
        }
    }
}
```

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 编辑器面板布局重组，Motion Design 相关标签页独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 新增 MRQ 渲染队列的分析统计功能 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 播出控制工具栏增加页面加载选项 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增碰撞禁用项目设置 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联逻辑 |

### 维护评价

- **活跃维护**：AvalancheMask 作为 Motion Design 核心子系统之一，随主插件持续更新
- **近期变更重点**：5.8 版本对遮罩系统进行了大重构（大量 `_DEPRECATED` 标记），将材质处理从旧的 Handle 系统迁移到 Material Bridge 架构
- **已知废弃**：`FAvaMask2DActorData`、`ObjectHandleSubsystem`、`MaterialHandleData` 等已在 5.8 标记废弃
- **推荐使用**：✅ 推荐。该模块是 Motion Design 遮罩功能的唯一实现路径，无替代方案

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheMask)
- [主插件文档](./index.md)
# Animator Kit

> Utilities for Animating in Unreal with Sequencer

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ `EnabledByDefault: false` |
| 包含内容 | ✅ `CanContainContent: true` |
| 模块 | AnimatorKitSettings (Editor) |
| 创建时间 | 2024-09-03 |
| 年龄标签 | 🆕 (≤5年) |
| 实验性 | ⚠️ `IsBetaVersion: true` |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/AnimatorKit) | |

## 用途

AnimatorKit 是 Epic 为动画师（Animator）打造的一套**编辑器辅助工具集**，围绕 Sequencer 和 ControlRig 构建。它不是一个运行时插件，而是一个面向内容创作流程的 Asset 和设置集合。

核心价值在于提供：
1. **ControlRig 实用工具 Rig（CRU_）**：预置的 ControlRig 资产，用于快速执行常见的动画辅助操作，如样条驱动、模拟、变形目标驱动等。
2. **Deformer Graph 变形器（DG_）**：基于 DeformerGraph 的 GPU 变形器资产，包括晶格变形（Lattice）、雕刻变形（Sculpt）、摄像机空间晶格变形等，可直接在 Sequencer 中对动画结果进行非破坏性微调。
3. **Locator 系统**：用于在视口中放置辅助定位器，配合 ControlRig 进行动画定位。
4. **Focus Mode 设置**：通过 `AnimMode.PendingFocusMode` 控制台变量控制动画模式下的视口焦点行为。

本质上，AnimatorKit 是 **ControlRig + DeformerGraph + Sequencer** 三者结合的动画师工作流加速器。

## 使用场景

- 你在 Sequencer 中编辑角色动画，需要对特定部位进行局部变形修正 → 使用 Lattice Deformer 或 Sculpt Deformer
- 你需要用样条曲线驱动骨骼链的运动（如尾巴、绳索）→ 使用 `CRU_SplinePath`
- 你需要为角色添加基于物理的链式模拟（如头发、飘带）→ 使用 `CRU_ChainSim` 或 `CRU_SingleSim`
- 你需要快速驱动 Morph Target（表情混合变形）→ 使用 `CRU_MorphTargetDriver`
- 你需要在动画编辑时在视口中放置辅助定位器 → 使用 Locator 系统
- 你需要控制动画模式下视口焦点自动跟随 → 启用 Focus Mode

## 蓝图用法

AnimatorKit 的 C++ 代码中**没有暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 接口**。它的功能完全通过以下方式使用：

- **ControlRig 资产**：直接在 Sequencer 中作为 ControlRig Track 使用
- **DeformerGraph 资产**：在 Skeletal Mesh 的 Deformer 设置中引用
- **编辑器设置**：通过 Edit → Editor Preferences → Animation → Animator Kit Settings

## C++ 用法

### 头文件引入

```cpp
#include "AnimatorKitSettings.h"
```

### 访问设置

AnimatorKit 暴露了一个 `UDeveloperSettings` 子类，可通过标准方式访问：

```cpp
// 获取默认设置对象
const UAnimatorKitSettings* Settings = GetDefault<UAnimatorKitSettings>();

// 读取 Focus Mode 状态
bool bFocusEnabled = Settings->bEnableFocusMode;
```

### 监听设置变更

```cpp
// 订阅设置变更通知
UAnimatorKitSettings::OnSettingsChange.AddLambda([](const UAnimatorKitSettings* InSettings)
{
    bool bFocusMode = InSettings->bEnableFocusMode;
    // 处理设置变更...
});
```

### 控制台变量

Focus Mode 也可以通过控制台变量直接控制：

```cpp
// C++ 中设置
IConsoleManager::Get().FindConsoleVariable(TEXT("AnimMode.PendingFocusMode"))->Set(1);

// 或在编辑器控制台中
// AnimMode.PendingFocusMode 1
```

## Demo 示例

AnimatorKit 主要是内容资产 + 编辑器设置，没有传统的 C++ Demo。以下是典型的使用流程：

### 启用插件

```
Edit → Plugins → 搜索 "Animator Kit" → Enable → 重启编辑器
```

> ⚠️ 默认未启用（`EnabledByDefault: false`），需手动开启。

### 使用 ControlRig 工具

1. 启用插件后，Content Browser 中会出现 `AnimatorKit/Content/UtilityRigs/` 目录
2. 在 Sequencer 中为角色添加 ControlRig Track
3. 选择合适的 CRU 资产（如 `CRU_SplinePath`）应用到骨骼

### 使用 Deformer 变形器

1. 选择 Skeletal Mesh Component
2. 在 Details 面板中找到 Deformer 设置
3. 引用 `CRD_Lattice`、`CRD_SculptDeformer` 等资产
4. DeformerGraph 会在 GPU 上运行，对动画结果进行实时变形

### 配置 Focus Mode

```
Edit → Editor Preferences → 搜索 "Animator Kit Settings"
→ Animation Settings → Focus → Enable Focus Mode
```

或通过控制台：`AnimMode.PendingFocusMode 1`

## 模块依赖

### 插件依赖

| 插件 | 用途 |
|---|---|
| `ControlRig` | 核心骨骼控制系统，所有 CRU 资产的运行基础 |
| `ControlRigSpline` | 样条驱动功能，`CRU_SplinePath` 依赖 |
| `RigVM` | ControlRig 的虚拟机运行时 |
| `DeformerGraph` | GPU 变形器图，所有 DG/CRD 变形器资产的运行基础 |
| `GizmoFramework` | Gizmo 显示框架，Locator 系统依赖 |

### 模块依赖（Build.cs）

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `DeveloperSettings` | 设置类基类 |
| `Engine` | 引擎核心 |
| `ControlRigEditor` | ControlRig 编辑器支持（仅编辑器模块） |

## 内容资产一览

### UtilityRigs（实用 ControlRig）

| 资产 | 用途 |
|---|---|
| `CRU_SplinePath` | 样条路径驱动骨骼 |
| `CRU_MorphTargetDriver` | Morph Target（混合形状）驱动 |
| `CRU_SingleSim` | 单链物理模拟 |
| `CRU_ChainSim` | 多链物理模拟 |
| `CRU_BlendParent` | 父级混合 |
| `CRU_AddLocator` | 添加定位器 |
| `CRU_3Node` | 三节点辅助 Rig |

### DeformerRigs（变形器）

| 资产 | 用途 |
|---|---|
| `CRD_Lattice` | 晶格变形器（默认） |
| `CRD_Lattice_2x2x2` | 2×2×2 晶格变形器 |
| `CRD_Lattice_3x3x3` | 3×3×3 晶格变形器 |
| `CRD_Lattice_4x4x4` | 4×4×4 晶格变形器 |
| `CRD_SculptDeformer` | 雕刻变形器 |
| `DG_LatticeDeformer` | DeformerGraph 晶格变形器图 |
| `DG_SculptDeformer` | DeformerGraph 雕刻变形器图 |
| `DG_CameraSpaceLattice` | 摄像机空间晶格变形器图 |
| `CRD_CameraSpaceLattice_10x10` | 10×10 摄像机空间晶格 |

### Locator（定位器）

| 资产 | 用途 |
|---|---|
| `Locator` | 基础定位器 |
| `LocatorXYZ` | XYZ 轴定位器 |
| `ShapeControlLibLocator` | 形状控制库定位器 |
| `GreenLocatorMatX/Y/Z` | 绿色定位器材质（各轴） |
| `AxisRLocatorMatX` | 红色 X 轴定位器材质 |
| `AxisGLocatorMatY` | 绿色 Y 轴定位器材质 |
| `AxisBLocatorMatZ1` | 蓝色 Z 轴定位器材质 |

### Meshes（网格体）

| 资产 | 用途 |
|---|---|
| `SK_EmptyMesh` | 空骨骼网格体（用于 ControlRig 目标） |
| `SKM_EmptyMesh` | 空静态网格体 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-11 | `3413adf5ae37` | Ran UnrealCodeFixup to fix dll storage | 自动化代码修复，修正 DLL 导出宏 |
| 2025-07-10 | `9803c443cfab` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 自动化代码修复，添加内联生成宏 |
| 2025-01-16 | `dbb55c1beb24` | Animation mode & AnimatorKit: fixed focus mode value propagation | **实质性修复**：修复 Focus Mode 设置在不同优先级 CVar 之间的传播问题，防止设备配置覆盖项目设置 |

### 维护评价

- **创建时间**：2024-09-03，至今约 1.7 年，属于较新的插件
- **最近更新**：2025-07 有两次自动化工具修复，2025-01 有一次实质性 bug 修复
- **维护状态**：**维护中** — 仍有更新，但更新频率较低
- **实验性**：`IsBetaVersion: true`，属于 Beta 阶段，API 和功能可能变化
- **代码规模**：C++ 代码极小（仅 4 个源文件），核心价值在于 Content 资产
- **建议**：可以使用，但注意 Beta 标记。主要功能依赖 ControlRig 和 DeformerGraph，AnimatorKit 本身更多是资产打包和设置管理。适合对 ControlRig 动画工作流有需求的团队。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/AnimatorKit)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
- [ControlRig 文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/control-rig-in-unreal-engine)
- [DeformerGraph 文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/deformer-graph-in-unreal-engine)

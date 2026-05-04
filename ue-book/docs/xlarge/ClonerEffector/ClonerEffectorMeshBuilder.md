# Cloners and Effectors

> Niagara based cloner system with various layouts and effector affecting each clone instances

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、Niagara 系统） |
| 模块 | `ClonerEffector` (Runtime), `ClonerEffectorEditor` (Runtime), `ClonerEffectorMeshBuilder` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-06 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/ClonerEffector) | |

## 用途

ClonerEffector 是一个基于 Niagara 粒子系统的克隆器和效应器插件，专为虚拟制作和动态设计场景打造。它解决的核心问题是：**如何高效地创建和控制大量重复实例的布局与动画效果**。

插件提供两大核心功能：

1. **Cloner（克隆器）**：支持多种布局模式（网格、圆形、螺旋、线性等），将单个对象克隆为大量实例，并通过 Niagara 粒子系统进行高效渲染
2. **Effector（效应器）**：对克隆实例施加各种变换效果（缩放、旋转、位移、颜色等），支持衰减、噪声、序列等多种效果模式

与传统的 HISM（分层实例静态网格）方案相比，ClonerEffector 利用 Niagara 的计算管线，可以在运行时动态控制每个实例的变换、材质参数等属性，非常适合虚拟制作中的 LED 墙内容、动态背景、粒子特效等场景。

## 使用场景

- 你在做虚拟制作的 LED 墙内容，需要大量重复元素的动态布局 → 用 Cloner 配合 Effector
- 你需要创建复杂的粒子/实例动画效果，如波浪、螺旋、脉冲等 → 用 Effector 的各种效果模式
- 你需要在 Motion Design 工作流中快速搭建动态背景 → 用 ClonerEffector
- 你需要将多个网格合并为单个动态网格用于克隆 → 用 ClonerEffectorMeshBuilder

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [ClonerEffector](ClonerEffector.md) | Runtime | 核心运行时模块，包含 Cloner/Effector 的核心逻辑和 Niagara 集成 |
| [ClonerEffectorEditor](ClonerEffectorEditor.md) | Runtime | 编辑器扩展模块，提供自定义 UI、细节面板和编辑器工具 |
| [ClonerEffectorMeshBuilder](ClonerEffectorMeshBuilder.md) | Runtime | 网格构建工具，支持将多种组件类型转换/合并为动态网格 |

## 模块依赖

从各模块的 Build.cs 分析，该插件的依赖关系如下：

| 模块 | 用途 |
|---|---|
| `Niagara` | 核心依赖，用于粒子系统驱动克隆实例 |
| `GeometryFramework` | 动态网格组件支持 |
| `GeometryCore` | 几何数据处理 |
| `DynamicMesh` | 动态网格构建和操作 |
| `MeshConversion` | 网格格式转换 |
| `ModelingComponents` | 建模组件支持 |
| `MeshDescription` | 网格描述数据结构 |
| `StaticMeshDescription` | 静态网格描述 |
| `RenderCore` | 渲染核心 |
| `RHI` | 渲染硬件接口 |
| `MaterialShaderQualitySettings` | 材质着色器质量设置 |

## 维护状态

### 近期更新

```
- bafe5da2d8e4 Silence incorrect V1051 warnings
- f5ac91ebd9c8 Removing invalid appearances of U macros in places where they will be skipped.
- d53ec51b85c0 Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction: ActorModifier, ActorModifierCore, Motion Design, ClonerEffector, CustomDetailsView, Material Designer, GeometryMask, OperatorStack, PropertyAnimator, PropertyAnimatorCore, StormSync, StormSync Motion Design Bridge
```

- `d53ec51b85c0`：插件从 Experimental 迁移到 VirtualProduction 目录，标志着该插件已脱离实验阶段，成为正式支持的虚拟制作工具
- `f5ac91ebd9c8`：代码清理，移除无效的 U 宏使用
- `bafe5da2d8e4`：修复编译警告，提升代码质量

### 维护评价

**活跃维护**。该插件于 2024 年 2 月创建，约 1 年历史，是 Epic Motion Design 工具链的核心组件之一。从 Experimental 迁移到 VirtualProduction 表明已通过内部审核，进入正式支持阶段。作为虚拟制作工作流的关键插件，预计会持续获得更新和维护。

**推荐使用**：如果你的项目涉及虚拟制作、LED 墙内容或动态设计，这是一个官方支持的成熟方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/ClonerEffector)
- [官方文档]()（暂无）

---

# ClonerEffectorMeshBuilder

> 网格构建工具模块，支持将多种组件类型转换/合并为动态网格

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ClonerEffectorMeshBuilder` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-06 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/ClonerEffector/Source/ClonerEffectorMeshBuilder) | |

## 用途

ClonerEffectorMeshBuilder 是 ClonerEffector 插件的网格构建工具模块。它解决的核心问题是：**如何将场景中各种不同类型的网格组件统一转换为可被克隆器使用的动态网格格式**。

该模块提供了一个统一的网格构建器 `FCEMeshBuilder`，能够：

1. **支持多种组件类型**：StaticMesh、DynamicMesh、SkeletalMesh、ProceduralMesh、InstancedStaticMesh、SplineMesh、Brush、Niagara 等
2. **合并网格**：将多个组件的几何数据合并为单个动态网格
3. **保留材质信息**：在转换过程中保留材质槽位和材质引用
4. **支持实例数据**：记录每个实例的变换信息，用于后续的克隆布局

这是 ClonerEffector 工作流中的关键基础设施，使得用户可以将任意场景对象作为克隆源。

## 使用场景

- 你有一个包含多种网格组件的 Actor，想将其作为克隆源 → 用 `FCEMeshBuilder::AppendActor`
- 你需要将多个静态网格合并为一个动态网格用于克隆 → 用 `FCEMeshBuilder` 的构建流程
- 你需要检查某个组件是否支持网格提取 → 用 `FCEMeshBuilder::IsComponentSupported`

## C++ 用法

### 头文件引入

```cpp
#include "CEMeshBuilder.h"
```

### 基本用法

```cpp
// 检查组件是否支持网格提取
bool bSupported = FCEMeshBuilder::IsComponentSupported(MyStaticMeshComponent);

// 检查组件是否包含几何数据
bool bHasGeometry = FCEMeshBuilder::HasAnyGeometry(MyComponent);

// 检查 Actor 是否支持
bool bActorSupported = FCEMeshBuilder::IsActorSupported(MyActor);
```

### 进阶用法

```cpp
// 创建网格构建器实例
FCEMeshBuilder MeshBuilder;

// 配置追加参数
FCEMeshBuilder::FCEMeshBuilderAppendParams AppendParams;
AppendParams.ComponentTypes = ECEMeshBuilderComponentType::StaticMeshComponent | 
                               ECEMeshBuilderComponentType::DynamicMeshComponent;
AppendParams.ExcludeComponents.Add(SomeComponentToExclude); // 排除特定组件

// 从 Actor 追加网格数据
TArray<UPrimitiveComponent*> ProcessedComponents = MeshBuilder.AppendActor(
    SourceActor, 
    SourceActor->GetActorTransform(), 
    AppendParams
);

// 获取构建结果
int32 InstanceCount = MeshBuilder.GetMeshInstanceCount();
int32 MeshCount = MeshBuilder.GetMeshCount();
TArray<uint32> MeshIndexes = MeshBuilder.GetMeshIndexes();

// 配置构建参数
FCEMeshBuilder::FCEMeshBuilderParams BuildParams;
BuildParams.bMergeMaterials = true; // 合并相同材质槽位

// 重置构建器（清理数据以便重新使用）
MeshBuilder.Reset();
```

## 支持的组件类型

`ECEMeshBuilderComponentType` 枚举定义了所有可转换的组件类型：

| 枚举值 | 说明 |
|---|---|
| `DynamicMeshComponent` | 动态网格组件 |
| `SkeletalMeshComponent` | 骨骼网格组件 |
| `BrushComponent` | BSP 画刷组件 |
| `ProceduralMeshComponent` | 程序化网格组件 |
| `InstancedStaticMeshComponent` | 实例化静态网格组件 |
| `SplineMeshComponent` | 样条网格组件 |
| `StaticMeshComponent` | 静态网格组件 |
| `NiagaraComponent` | Niagara 粒子组件 |
| `All` | 所有类型（默认） |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DynamicMesh` | 动态网格数据结构 `FDynamicMesh3` |
| `GeometryCore` | 几何核心数据结构 |
| `MeshConversion` | 网格格式转换工具 |
| `MeshDescription` | 网格描述数据结构 |
| `StaticMeshDescription` | 静态网格描述扩展 |
| `GeometryFramework` | 动态网格组件 `UDynamicMeshComponent` |

## 维护状态

### 近期更新

```
- bafe5da2d8e4 Silence incorrect V1051 warnings
- f5ac91ebd9c8 Removing invalid appearances of U macros in places where they will be skipped.
- d53ec51b85c0 Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction
```

### 维护评价

**活跃维护**。作为 ClonerEffector 的子模块，随主插件一起维护。该模块是基础设施级别的工具，代码相对稳定，主要更新集中在编译兼容性和代码质量改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/ClonerEffector/Source/ClonerEffectorMeshBuilder)
- [头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/ClonerEffector/Source/ClonerEffectorMeshBuilder/Public/CEMeshBuilder.h)
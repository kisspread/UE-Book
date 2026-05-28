# Chaos Cloth

> Adds Chaos Cloth modules.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料系统 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosCloth` (Runtime), `ChaosClothEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth) | |

## 用途

Chaos Cloth 是 UE5 中基于 Chaos 物理引擎构建的**专业级布料模拟系统**。它解决了在大型开放世界和复杂角色动画中，对高性能、高保真度实时布料（如衣物、旗帜、窗帘、吊索等）进行物理模拟的需求。该插件从实验性模块迁移而来，提供了从物理模拟、碰撞处理到编辑器内资产创建与预览的完整工作流。

## 使用场景

- **游戏角色服饰**：为角色实现逼真的衣物、披风、裙摆、头发等动态效果。
- **环境动态织物**：模拟场景中的旗帜、窗帘、遮阳篷、帐篷等受到风力和角色互动影响的物体。
- **载具与道具**：模拟降落伞、帆船帆布、吊桥绳索等需要物理行为的特殊布料。
- **电影与过场动画**：在非实时渲染的场景中，追求电影级质量的布料动态。

## 蓝图用法

蓝图层面的功能主要围绕布料资产的创建、配置以及对运行时模拟行为的查询与控制。核心逻辑通常封装在 `ChaosCloth` 运行时模块中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Cloth Simulation` | 为骨骼网格体组件创建并初始化一个布料模拟实例。 | `UClothingSimulationFactory` |
| `Set Cloth Config` | 在运行时修改布料资产的配置参数（如风、重力缩放）。 | `UClothingSimulation` |

### 使用示例（蓝图描述）

1.  **创建与激活**：在角色的 `BeginPlay` 事件中，获取其骨骼网格体组件，然后调用 `Create Cloth Simulation` 节点，为其绑定的布料资产创建模拟实例。
2.  **运行时调整**：通过 `Set Cloth Config` 节点，根据游戏进程动态调整布料的物理属性。例如，在角色进入室内时，调低风力影响。

## C++ 用法

C++ 接口允许更深度地集成和定制布料模拟，例如自定义碰撞形状、影响模拟的材质属性等。

### 头文件引入

```cpp
#include "ClothSimulation.h"
#include "ClothConfig.h"
```

### 基本用法

以下代码演示如何获取布料模拟实例并设置基本参数。假设你已经有了一个带布料资产的 `USkeletalMeshComponent`。

```cpp
// 假设 SkeletalMeshComp 是带有布料资产的骨骼网格体组件
if (UClothingSimulation* ClothSim = SkeletalMeshComp->GetClothingSimulation())
{
    // 访问并修改布料配置
    if (FClothConfig* Config = ClothSim->GetClothConfig())
    {
        // 调整重力缩放
        Config->SetGravityScale(0.8f);
        // 开启风力影响
        Config->SetWindEnabled(true);
        Config->SetWindSpeed(50.0f);
    }
}
```
*此代码基于 `UClothingSimulation` 和 `FClothConfig` 的典型用法推断。*

### 进阶用法

对于需要精确控制的场景，如自定义碰撞胶囊体或影响布料模拟的蒙皮权重，需要深入使用 `ChaosCloth` 模块提供的底层接口。这通常涉及到与 `FClothingSystemRuntimeCommon` 模块交互，以及理解 `ClothVertData` 等结构。

## Demo 示例

由于布料模拟的设置高度依赖于具体的网格体、骨骼和资产，一个“最小可运行示例”需要复杂的场景搭建。核心步骤如下：

1.  **准备资产**：在编辑器中，使用 `ChaosClothEditor` 模块提供的工具，为一个骨骼网格体（如一个带袖子的上衣模型）创建并设置 `Cloth` 资产，定义哪些顶点参与模拟以及物理参数。
2.  **设置组件**：在场景中的角色蓝图上，将 `SkeletalMeshComponent` 的 Mesh 指向包含布料资产的骨骼网格体。
3.  **运行与观察**：运行游戏，布料部分（如袖子）应根据重力、角色运动和配置的物理属性自动开始模拟。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ClothingSystemRuntimeCommon` | 提供布料模拟的公共运行时基础框架和接口。 |
| `PhysicsCore` | 与 Chaos 物理引擎进行深度集成。 |
| `ChaosCaching` | 支持布料模拟状态的缓存，用于重播和优化。 |
| `Water` | 与水面系统交互，用于实现布料（如角色衣物）浸入水中的效果。 |
| `Buoyancy` | 提供浮力模拟，与 `Water` 模块配合处理布料与水的交互。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量转换为浮点数产生的编译器警告。 |
| 2026-04-23 | `85f3a947` | [Chaos Cloth] Clamp SolverLOD in ChaosClothingSimulationSolver to prevent out of bound crash when so | 限制解算器LOD级别以防止在特定情况下发生越界崩溃。 |
| 2026-04-21 | `9322be91` | Minor cloth debug draw improvements: | 对布料调试绘制进行了小幅改进。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到新的 `UE_LOGF` 格式。 |
| 2026-03-31 | `0d36bcd0` | Chaos Cloth : | 对布料系统进行了功能更新或修复（提交信息不完整）。 |

### 维护评价

**活跃维护**。该插件于2024年3月从实验性模块转为正式插件，至今仍处于积极的开发和维护中。从最近的Git提交记录可以看出，Epic Games 团队持续为其进行**稳定性修复**（如防止崩溃）、**性能优化**和**代码现代化**（如日志系统迁移）。最近3个月内有持续的更新，表明该系统是UE5物理模拟栈中的关键且受支持的组成部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth)
- [ChaosCloth 子模块文档](./ChaosCloth.md)
- [ChaosClothEditor 子模块文档](./ChaosClothEditor.md)
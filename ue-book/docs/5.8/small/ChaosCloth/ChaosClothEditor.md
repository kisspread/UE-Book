# Chaos Cloth

> Adds Chaos Cloth modules.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosCloth` (Runtime), `ChaosClothEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth) | |

## 用途

ChaosCloth 是 Unreal Engine 中用于高级衣物和布料物理模拟的核心插件，基于 Chaos 物理系统。它的存在是为了提供高性能、高保真的布料模拟解决方案，取代或补充旧有的布料系统。该插件不仅包含运行时模拟引擎，还整合了专门的编辑器工具，方便美术和开发者在编辑器内对布料资产进行调试、预览和参数调整。

**核心功能**：
1.  **运行时模拟**：负责在游戏运行时计算角色衣物、旗帜、窗帘等布料对象的物理运动。
2.  **编辑器集成**：提供了在 Skeletal Mesh Editor（骨骼网格体编辑器）中预览和调试布料模拟的扩展工具。
3.  **模块化架构**：将运行时模拟逻辑 (`ChaosCloth`) 和编辑器支持 (`ChaosClothEditor`) 分离，便于维护和按需加载。

## 使用场景

-   **角色服装模拟**：为 RPG、MMO 或任何带角色的 3D 游戏制作动态飘动的斗篷、披风、裙摆。
-   **环境布料**：模拟游戏场景中飘动的旗帜、窗帘、帐篷等环境物体。
-   **高品质过场动画**：在电影级品质的过场动画中，制作衣物与角色骨骼动画结合的真实感运动。
-   **物理驱动的玩法**：利用布料物理创造基于物理的玩法元素，例如在风中飞舞的线索或可撕扯的织物。

## 蓝图用法

此插件主要通过编辑器界面进行配置和调试，不直接提供可蓝图化的函数节点。其核心使用流程是在 **Skeletal Mesh Editor** 中为骨骼网格体（Skeletal Mesh）的 Cloth 数据资产配置模拟参数，并通过 `FSimulationEditorExtender` 提供的可视化工具进行预览。

## C++ 用法

### 头文件引入

```cpp
// 若需扩展编辑器功能
#include "ChaosClothEditorModule.h"
#include "ChaosSimulationEditorExtender.h"
```

### 基本用法（编辑器模块注册）

该插件的编辑器模块负责注册其编辑器扩展功能。
```cpp
// 文件路径：Engine/Plugins/ChaosCloth/Source/ChaosClothEditor/Private/ChaosClothEditorModule.cpp
void FChaosClothEditorModule::StartupModule()
{
    // ChaosEditorExtender 是一个 FSimulationEditorExtender 实例
    // 它在启动时自动将自身注册为布料模拟的编辑器扩展
}
```

### 进阶用法（扩展编辑器可视化）

`FSimulationEditorExtender` 允许开发者扩展布料模拟在编辑器视口中的调试绘制功能。
```cpp
// 文件路径：Engine/Plugins/ChaosCloth/Source/ChaosClothEditor/Public/ChaosSimulationEditorExtender.h
// FSimulationEditorExtender 继承自 ISimulationEditorExtender
// 它重写了关键的虚函数来为 Chaos Cloth 提供定制的调试视图
virtual void DebugDrawSimulation(const IClothingSimulationInterface* Simulation, USkeletalMeshComponent* OwnerComponent, FPrimitiveDrawInterface* PDI) override;
virtual void DebugDrawSimulationTexts(const IClothingSimulationInterface* Simulation, USkeletalMeshComponent* OwnerComponent, FCanvas* Canvas, const FSceneView* SceneView) override;
```

## Demo 示例

ChaosCloth 插件本身不提供独立的可运行项目 Demo。其使用方式是作为 Unreal Engine 布料系统的后端。一个最小的“使用”示例如下：

1.  **启用插件**：在项目的 `.uproject` 文件或编辑器插件设置中确保 “Chaos Cloth” 插件已启用。
2.  **创建 Cloth 数据**：在 Skeletal Mesh Editor 中，为一个骨骼网格体添加 Cloth 属性并绘制权重图。
3.  **配置模拟**：在 Cloth 属性面板（由 ChaosCloth 运行时模块驱动）中设置风力、重力、碰撞等参数。
4.  **预览**：在编辑器的 Persona 预览场景中，利用 `FSimulationEditorExtender` 提供的菜单选项来开启各种调试可视化（如碰撞体、速度场等）。

## 模块依赖

从 `.uplugin` 的 `Plugins` 依赖和模块类型推断，使用此插件或进行开发时，主要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `ChaosCaching` | 用于物理状态缓存，可能服务于布料模拟的某些高级特性或回放。 |
| `Buoyancy` | 提供流体浮力模拟，可能与布料在水面的行为有关。 |
| `Water` | 提供水体系统，与 `Buoyancy` 模块配合，支持布料与水体的交互。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数产生的编译警告。 |
| 2026-04-23 | `85f3a947` | [Chaos Cloth] Clamp SolverLOD in ChaosClothingSimulationSolver to prevent out of bound crash when so | 钳制求解器LOD级别，防止因LOD层级过低导致的越界崩溃。 |
| 2026-04-21 | `9322be91` | Minor cloth debug draw improvements: | 对布料调试绘制进行了小幅改进。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-03-31 | `0d36bcd0` | Chaos Cloth : | （信息不完整，推测为与 Chaos Cloth 相关的提交） |

### 维护评价

-   **活跃度**：插件创建于 2024 年初，是一个较新的系统。从 Git 历史看，在 2026 年仍有多次实质性更新，包括 Bug 修复、稳定性提升（防止崩溃）和代码现代化（日志宏迁移），表明处于 **活跃维护** 状态。
-   **稳定性**：最近的提交专注于修复崩溃和警告，显示团队正在积极提升系统的稳定性。
-   **推荐度**：作为 Epic 官方主推的 Chaos 物理系统的一部分，且在持续迭代中，**强烈推荐** 新项目和需要高质量布料模拟的项目使用此插件，而非旧的布料系统。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth)
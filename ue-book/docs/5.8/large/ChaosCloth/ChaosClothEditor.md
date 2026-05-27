# Chaos Cloth

> Adds Chaos Cloth modules.

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 布料 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosCloth` (Runtime), `ChaosClothEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth) | |

## 用途

ChaosCloth 是基于 Chaos 物理引擎的布料模拟系统插件。它为 SkeletalMesh 提供高性能的实时布料物理模拟，支持布料的动力学求解、碰撞检测、LOD 优化以及调试可视化。该插件于 2024 年从 Experimental 阶段正式迁移到正式目录，标志着 Chaos 布料模拟已达到生产可用状态。

插件还集成了浮力（Buoyancy）和水面（Water）系统，可实现布料在水面环境中的交互模拟。

## 使用场景

- 你需要为角色的衣物、披风、旗帜等创建逼真的物理布料动画 → 用 ChaosCloth
- 你需要在编辑器中预览和调试布料模拟效果 → 用 ChaosClothEditor
- 你的场景涉及水面与布料交互（如漂浮物、湿衣效果）→ 启用 ChaosCloth + Water + Buoyancy
- 你需要对布料模拟进行 LOD 优化以保证性能 → ChaosCloth 内置 SolverLOD 支持

## 蓝图用法

ChaosCloth 的核心功能主要通过 SkeletalMeshComponent 的布料资产配置完成，而非直接暴露大量蓝图节点。布料资产（Cloth Asset）的配置在编辑器中完成，运行时由 Chaos 物理引擎自动求解。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 布料模拟由引擎自动驱动 | 设置 Cloth 资产后，SkeletalMeshComponent 会在模拟阶段自动应用 Chaos 布料求解 | `USkeletalMeshComponent` |

> ChaosCloth 作为底层物理求解器插件，用户主要通过 SkeletalMesh 编辑器中的 Cloth 工作流使用，而非直接通过蓝图节点操控。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosClothEditor/ChaosSimulationEditorExtender.h"
```

### 基本用法

ChaosClothEditor 模块主要提供编辑器扩展，核心类是 `Chaos::FSimulationEditorExtender`，用于在布料编辑器中添加调试绘制和可视化菜单。

```cpp
// ChaosSimulationEditorExtender.h — 编辑器扩展接口
namespace Chaos
{
    class FSimulationEditorExtender : public ISimulationEditorExtender
    {
    public:
        // 获取支持的模拟工厂类
        virtual UClass* GetSupportedSimulationFactoryClass() override;

        // 扩展视口 Show 菜单，添加布料调试选项
        virtual void ExtendViewportShowMenu(
            FMenuBuilder& MenuBuilder,
            TSharedRef<IPersonaPreviewScene> PreviewScene) override;

        // 在场景中绘制布料模拟的调试信息
        virtual void DebugDrawSimulation(
            const IClothingSimulationInterface* Simulation,
            USkeletalMeshComponent* OwnerComponent,
            FPrimitiveDrawInterface* PDI) override;

        // 在视口上绘制布料模拟的文本调试信息
        virtual void DebugDrawSimulationTexts(
            const IClothingSimulationInterface* Simulation,
            USkeletalMeshComponent* OwnerComponent,
            FCanvas* Canvas,
            const FSceneView* SceneView) override;
    };
}
```

### 进阶用法

ChaosClothEditor 还提供了自定义属性编辑器，用于在 Details 面板中显示带有权重贴图（Weight Map）的布料参数：

```cpp
// FChaosClothWeightedValueCustomization — 布料加权值属性自定义
// 继承自 FMathStructCustomization，在头部行显示结构体成员的短名称
class FChaosClothWeightedValueCustomization : public FMathStructCustomization
{
public:
    // 静态工厂方法，用于注册到属性自定义系统
    static TSharedRef<IPropertyTypeCustomization> MakeInstance();
};
```

## Demo 示例

### 最小示例：注册布料编辑器扩展

```cpp
// MyClothEditorModule.h
#pragma once
#include "Modules/ModuleManager.h"
#include "ChaosSimulationEditorExtender.h"

class FMyClothEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    Chaos::FSimulationEditorExtender ChaosEditorExtender;
};
```

```cpp
// MyClothEditorModule.cpp
#include "MyClothEditorModule.h"

void FMyClothEditorModule::StartupModule()
{
    // FSimulationEditorExtender 构造时自动注册到 Persona 编辑器
    // Shutdown 时自动注销
}

void FMyClothEditorModule::ShutdownModule()
{
}

IMPLEMENT_MODULE(FMyClothEditorModule, MyClothEditor)
```

> 注：通常不需要手动创建 `FSimulationEditorExtender`，ChaosClothEditor 模块在启动时已自动注册。此示例仅展示其生命周期管理方式。

## 模块依赖

从插件声明的依赖关系及模块用途推断：

| 模块 | 用途 |
|---|---|
| `ChaosCaching` | Chaos 物理缓存系统，用于布料模拟数据的缓存和回放 |
| `Buoyancy` | 浮力模拟，支持布料与水面的浮力交互 |
| `Water` | 水面系统，提供水面环境用于布料水交互 |

> ChaosClothEditor 模块额外依赖编辑器类模块（如 UnrealEd、Persona 等）用于布料属性自定义和调试可视化。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 截断的编译警告 |
| 2026-04-23 | `85f3a947` | [Chaos Cloth] Clamp SolverLOD in ChaosClothingSimulationSolver to prevent out of bound crash when so | 限制 SolverLOD 范围防止数组越界崩溃 |
| 2026-04-21 | `9322be91` | Minor cloth debug draw improvements: | 布料调试绘制的细微改进 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到 UE_LOGF 格式 |
| 2026-03-31 | `0d36bcd0` | Chaos Cloth : | Chaos 布料相关更新 |

### 维护评价

- **创建时间**：2024-03-22，从 Experimental 正式迁移
- **活跃程度**：🟢 **活跃维护**。最近 2 个月内有多次实质性更新，包括 crash 修复、编译警告修复和调试功能改进
- **稳定性**：最近更新以 bug 修复和稳定性改进为主，表明系统已进入成熟稳定阶段
- **注意事项**：该插件于 2024 年才从 Experimental 迁移，相对较新，可能仍在快速迭代中
- **推荐使用**：✅ 推荐。作为 UE5 官方 Chaos 布料解决方案，处于积极维护状态，是 Cloth Simulation 的首选方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth)
- [创建提交](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/ChaosCloth) (`f55988ce` — 从 Experimental 迁移正式化)
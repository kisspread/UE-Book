# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（功能测试、编辑器工具、材质模板） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheMedia` (Runtime), `AvalancheSequencer` (Runtime) 等共 42 个模块 |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design 是 UE5 虚拟制片流程中的**实时运动图形设计与播出工具套件**。它在编辑器内提供了一套完整的 2D/3D 动态图形创作环境，涵盖文字排版、形状绘制、材质设计、克隆/效果器系统、场景编排、时间线控制、远程控制以及广播播出管理。

该插件的核心价值在于：**将 After Effects / Cinema 4D 级别的运动图形工作流搬进 UE5 的实时渲染管线中**，使设计师可以在引擎内直接完成从设计到播出的全流程，无需在多个 DCC 工具间切换。

从架构上看，插件由 42 个模块组成，每个功能域（文字、形状、材质、媒体、特效器等）都遵循 Runtime + Editor 模块分离的设计模式，保证运行时逻辑与编辑器工具的解耦。

## 使用场景

- 你在制作电视节目的**动态片头/片花**，需要实时调整并播出 → 用 Motion Design 的 SceneRig + Sequencer + Rundown 播出管理
- 你需要在虚拟制片 LED 墙上叠加**实时运动图形** → 用 Motion Design 的 Media 输出 + MRQ 渲染
- 你要设计复杂的**克隆/散布动画**（如粒子阵列、文字矩阵）→ 用 ClonerEffector + AvalancheEffectors
- 你需要**远程控制**舞台上的图形元素 → 用 AvalancheRemoteControl 配合 Remote Control 插件
- 你要导入 SVG 矢量图并转为 3D 形状 → 用 AvalancheSVGEditor + AvalancheShapes

## 蓝图用法

> ⚠️ 由于插件规模极大（2060 源文件、42 模块），本文档仅展示已分析模块的蓝图 API。完整蓝图节点清单需查阅各子模块文档。

### 截图功能测试（AvalancheFunctionalTest）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `bWaitForActorReady` | 是否等待指定 Actor 完全初始化后再截图 | `AScreenshotFunctionalTestAvalanche` |
| `ActorToWaitFor` | 需要等待就绪的目标 Actor（软引用） | `AScreenshotFunctionalTestAvalanche` |
| `MaxActorWaitTime` | 最大等待时间（秒），超时后强制继续 | `AScreenshotFunctionalTestAvalanche` |

### 使用示例（蓝图描述）

在功能测试关卡中放置 `Screenshot Functional Test Motion Design` Actor：

1. 在蓝图 Details 面板中，勾选 **Wait For Actor Ready**
2. 设置 **Actor To Wait For** 指向场景中包含 Niagara 特效的目标 Actor
3. 设置 **Max Actor Wait Time** 为 `5.0`（默认值）
4. 测试执行时，会自动解决 CVar 优先级冲突并等待 Actor 就绪后再截图

## C++ 用法

### 头文件引入

```cpp
#include "ScreenshotFunctionalTestAvalanche.h"
```

### 基本用法

基于 `Public/ScreenshotFunctionalTestAvalanche.h` 的功能测试使用：

```cpp
// 在自定义功能测试中继承 AScreenshotFunctionalTestAvalanche
// 用于 Motion Design 关卡的自动化截图测试
UCLASS()
class UMyMotionDesignScreenshotTest : public UAutomationEditorFunctionalTest
{
    GENERATED_BODY()

public:
    // AScreenshotFunctionalTestAvalanche 已解决以下问题：
    // 1. UAvaGameViewportClient 在 Constructor 优先级设置的 CVar 无法被覆盖
    //    → 本类使用 ECVF_SetByConsole 优先级强制覆盖 12 个渲染 CVar
    // 2. PIE 模式下截图委托不匹配
    //    → 本类同时注册实例级和静态截图委托
};
```

**来源**: `Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest/Public/ScreenshotFunctionalTestAvalanche.h`

### 进阶用法 — CVar 优先级管理

Avalanche 的自定义视口客户端 `UAvaGameViewportClient` 在构造时设置了渲染 CVar（Constructor/Code 优先级），导致普通 `SetWithCurrentPriority()` 无法覆盖。`AScreenshotFunctionalTestAvalanche` 内部使用模板辅助类处理此问题：

```cpp
// 模板辅助结构体，以 Console 优先级覆盖 CVar
template<typename T>
struct FScreenshotTestAvalancheCVarOverride
{
    void SetOverride(T NewValue)
    {
        IConsoleVariable* CVar = IConsoleManager::Get().FindConsoleVariable(*CVarName);
        if (CVar)
        {
            // 使用 ECVF_SetByConsole 优先级覆盖 Scalability/Constructor/Code 设置
            // 测试完成后不恢复，以避免优先级粘滞问题
            CVar->Set(NewValue, ECVF_SetByConsole);
        }
    }
};

// 测试中被覆盖的 12 个 CVar 包括：
// - AntiAliasing, AutoExposure, MotionBlur, MotionBlurQuality
// - ContactShadows, ScreenSpaceReflectionQuality, EyeAdaptationQuality
// - TonemapperGamma, ScreenPercentage, DynamicRes 等
```

**关键设计决策**：测试完成后 CVar **不恢复**原始值。测试友好的值（AA=0, ScreenPercentage=100, MotionBlur=0）会保留，以避免 Console 优先级的粘滞问题阻止后续低优先级设置生效。

**来源**: `Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest/Public/ScreenshotFunctionalTestAvalanche.h`

### 进阶用法 — Actor 就绪等待机制

对于包含 Niagara 系统、异步加载资源或复杂初始化逻辑的 Actor，可以启用等待机制确保截图时一切就绪：

```cpp
// IsActorFullyInitialized() 检查以下条件：
// 1. Actor 是否已完成 BeginPlay
// 2. 所有 Niagara 组件是否激活且拥有有效的系统实例
// 3. 所有 Primitive 组件是否已注册
// 4. Niagara 系统是否有至少 0.1 秒的粒子存活时间

// 在 FinishTest() 中，NiagaraSystem 资产会被临时 root 以防 GC 提前回收
// 在 BeginDestroy() 中解除 root
```

## Demo 示例

以下是一个最小化的 Motion Design 功能测试示例：

```cpp
// MyMotionDesignTest.h
#pragma once

#include "ScreenshotFunctionalTestAvalanche.h"
#include "MyMotionDesignTest.generated.h"

UCLASS()
class AMyMotionDesignTest : public AScreenshotFunctionalTestAvalanche
{
    GENERATED_BODY()

public:
    AMyMotionDesignTest(const FObjectInitializer& ObjectInitializer)
        : Super(ObjectInitializer)
    {
        // 启用 Actor 就绪等待，确保 Niagara 粒子系统完全初始化
        bWaitForActorReady = true;
        MaxActorWaitTime = 10.0f;
    }

    virtual void PrepareTest() override
    {
        Super::PrepareTest();
        // 可在此添加自定义测试前置逻辑
    }

    virtual void FinishTest(EFunctionalTestResult TestResult, const FString& Message) override
    {
        // Super 会处理 NiagaraSystem 的 root 保护
        Super::FinishTest(TestResult, Message);
    }
};
```

```cpp
// MyMotionDesignTest.cpp
#include "MyMotionDesignTest.h"

// 构造函数已在 .h 中内联实现
// 此文件用于放置可能的 .cpp 实现逻辑
```

## 模块依赖

### 运行时模块依赖

Avalanche 模块数量极多（42 个），核心公共依赖从 Build.cs 提取。**省略了常见的 Core/Engine/Slate 等标准依赖**。

| 模块 | 用途 |
|---|---|
| `Sequencer` | 序列器集成（AvalanchePropertyAnimator 依赖） |
| `GeometryCache` | 几何缓存支持，用于网格动画 |
| `GeometryScriptingCore` | 几何脚本，用于程序化网格操作 |
| `MediaCompositing` | 媒体合成，视频/图像混合 |
| `MediaIOFramework` | 媒体 I/O 框架，输入输出设备管理 |
| `MeshModelingToolsetExp` | 网格建模工具集 |
| `RemoteControlAPI` / `RemoteControl` | 远程控制协议支持 |
| `SVGImporter` | SVG 矢量图导入 |
| `Text3D` | 3D 文字渲染 |
| `ActorModifierCore` | Actor 修改器核心框架 |
| `PropertyAnimatorCore` | 属性动画核心 |
| `Niagara` | 粒子系统（功能测试模块依赖） |

### 插件级依赖

根据 .uplugin 声明，Avalanche 还依赖以下 UE5 插件：

- **Advanced Renamer** — 批量重命名工具
- **Custom Details View** — 自定义详情面板
- **Dynamic Material** — 动态材质系统

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将场景设置和大纲视图标签页移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用 Rundown 页面设置时新增 MRQ 分析统计 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and added | 播出控制工具栏新增页面加载选项（全部/下一个/已选） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes | 新增项目设置可强制禁用 3D 文字和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with viewport | 重构视口关联/解除关联时的客户端通知逻辑 |

### 维护评价

**活跃维护中** ✅

- **创建时间**：2025 年 5 月从 Experimental 目录迁移到 VirtualProduction，标志着从实验阶段毕业
- **更新频率**：近期（2026 年 5 月）有密集的功能迭代，一周内 5 次提交，涵盖新功能（MRQ 分析、页面加载选项）、UI 优化（标签页分组）和底层重构（视口通知）
- **维护团队**：由 Epic Games 官方团队维护，Jira 工单跟踪（UE-207892）
- **代码规模**：2060 源文件、42 模块，是 UE5 中规模最大的插件之一
- **推荐度**：适合虚拟制片和广播播出场景使用。作为官方插件，有持续的维护和功能迭代保障

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [功能测试源码](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest/Public/ScreenshotFunctionalTestAvalanche.h)
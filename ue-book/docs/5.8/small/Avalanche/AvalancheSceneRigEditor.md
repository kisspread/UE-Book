# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器资产、材质模板、蓝图资产） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime) 等共 44 个模块（见模块列表章节） |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design（原名 Avalanche）是 UE5 虚拟制作用途的**动态图形设计与合成工具**，专为广播级实时视觉内容制作而构建。它解决的核心问题是：在虚幻引擎中提供一套完整的 Motion Graphics 设计工作流，包括：

- **场景模板管理（Scene Rig）**：将场景配置封装为可复用的流式关卡模板，支持快速切换和批量管理
- **图形元素设计**：提供 2D/3D 文本、几何形状、SVG 导入、材质设计器等图形原语
- **动画与特效系统**：属性动画器（Property Animator）、克隆/效果器（ClonerEffector）、过渡效果（Transition）
- **修改器管线（Modifier Stack）**：类似 DCC 软件的非破坏性修改器堆栈，通过 ActorModifier 对 Actor 进行链式变换
- **广播集成**：媒体合成（Media Compositing）、远程控制（Remote Control）、节目控制工具栏（Rundown Page）
- **渲染输出**：集成 Movie Render Queue (MRQ) 进行最终帧输出

该插件从 2025 年由 `/Engine/Plugins/Experimental` 迁移到 `/Engine/Plugins/VirtualProduction`，标志着 Epic 将其作为虚拟制作管线的核心工具正式推出。

## 模块列表

Motion Design 是一个**超大型插件**（2060+ 源文件），按功能域拆分为 44 个模块：

### 核心模块
| 模块 | 类型 | 说明 |
|---|---|---|
| `Avalanche` | Runtime | 插件入口模块 |
| `AvalancheCore` | Runtime | 核心类型定义与基础服务 |
| `AvalancheEditor` | Runtime | 编辑器扩展主模块 |
| `AvalancheEditorCore` | Runtime | 编辑器核心工具 |

### 场景管理
| 模块 | 类型 | 说明 |
|---|---|---|
| `AvalancheSceneRig` | Runtime | 场景模板（Scene Rig）运行时逻辑 |
| `AvalancheSceneRigEditor` | Runtime | Scene Rig 编辑器工具与 Outliner 集成 |
| `AvalancheSceneTree` | Runtime | 场景树结构管理 |
| `AvalancheOutliner` | Runtime | Motion Design 专用 Outliner |

### 图形与形状
| 模块 | 类型 | 说明 |
|---|---|---|
| `AvalancheShapes` | Runtime | 几何形状原语 |
| `AvalancheShapesEditor` | Runtime | 形状编辑器工具 |
| `AvalancheText` | Runtime | 3D 文本支持 |
| `AvalancheTextEditor` | Runtime | 文本编辑器工具 |
| `AvalancheSVGEditor` | Runtime | SVG 导入编辑器 |

### 材质与遮罩
| 模块 | 类型 | 说明 |
|---|---|---|
| `AvalancheMaterial` | Runtime | 动态材质系统 |
| `AvalancheMask` | Runtime | 遮罩系统运行时 |
| `AvalancheMaskEditor` | Runtime | 遮罩编辑器 |

### 动画与修改器
| 模块 | 类型 | 说明 |
|---|---|---|
| `AvalanchePropertyAnimator` | Runtime | 属性动画器（集成 Sequencer） |
| `AvalanchePropertyAnimatorEditor` | Runtime | 属性动画器编辑器 |
| `AvalancheModifiers` | Runtime | 修改器堆栈 |
| `AvalancheModifiersEditor` | Runtime | 修改器编辑器 |
| `AvalancheTransition` | Runtime | 过渡效果 |
| `AvalancheTransitionEditor` | Runtime | 过渡效果编辑器 |
| `AvalancheEffectors` | Runtime | 效果器系统 |
| `AvalancheEffectorsEditor` | Runtime | 效果器编辑器 |

### 属性与标签
| 模块 | 类型 | 说明 |
|---|---|---|
| `AvalancheAttribute` | Runtime | 属性系统 |
| `AvalancheAttributeEditor` | Runtime | 属性编辑器 |
| `AvalancheTag` | Runtime | 标签系统 |
| `AvalancheTagEditor` | Runtime | 标签编辑器 |

### 媒体与广播
| 模块 | 类型 | 说明 |
|---|---|---|
| `AvalancheMedia` | Runtime | 媒体合成运行时 |
| `AvalancheMediaEditor` | Runtime | 媒体合成编辑器 |
| `AvalancheRemoteControl` | Runtime | 远程控制集成 |
| `AvalancheRemoteControlEditor` | Runtime | 远程控制编辑器 |

### 序列器与时间线
| 模块 | 类型 | 说明 |
|---|---|---|
| `AvalancheSequence` | Runtime | 序列器集成运行时 |
| `AvalancheSequencer` | Runtime | Sequencer 自定义扩展 |

### 视口与相机
| 模块 | 类型 | 说明 |
|---|---|---|
| `AvalancheViewport` | Runtime | 自定义视口覆盖 |
| `AvalancheLevelViewport` | Runtime | 关卡编辑器视口集成 |
| `AvalancheCamera` | Runtime | 相机管理 |

### 工具与测试
| 模块 | 类型 | 说明 |
|---|---|---|
| `AvalancheInteractiveTools` | Runtime | 交互式编辑器工具 |
| `AvalancheInteractiveToolsRuntime` | Runtime | 交互工具运行时部分 |
| `AvalancheComponentVisualizers` | Runtime | 组件可视化器 |
| `AvalancheMRQ` | Runtime | Movie Render Queue 集成 |
| `AvalancheMRQEditor` | Runtime | MRQ 编辑器工具 |
| `AvalancheFunctionalTest` | Runtime | 功能测试 |

## 使用场景

- 你在做虚拟制片（Virtual Production）中的实时图形合成 → 用 Motion Design 设计广播级图形叠加
- 你需要为大型活动/直播创建可快速切换的场景模板 → 用 Scene Rig 管理场景配置
- 你需要非破坏性的 Actor 修改器管线（类似 Houdini SOP） → 用 Modifier Stack
- 你需要在 Sequencer 时间线中驱动属性动画 → 用 Property Animator
- 你需要将多个 3D 元素（文本、形状、SVG）组合成动态图形 → 用 Motion Design 的形状/文本/SVG 工具集
- 你需要通过远程控制面板操控虚拟制片参数 → 用 Remote Control 集成

## C++ 用法

Motion Design 是高度面向编辑器的插件，大部分功能通过编辑器 UI 和蓝图暴露。C++ 层面主要提供**接口（Interface）**供其他模块扩展。

### Scene Rig 管理（AvalancheSceneRigEditor 模块）

#### 头文件引入

```cpp
#include "IAvaSceneRigEditorModule.h"
```

#### 基本用法 — 获取模块并操控 Scene Rig

```cpp
// 确保模块已加载
if (IAvaSceneRigEditorModule::IsLoaded())
{
    IAvaSceneRigEditorModule& SceneRigModule = IAvaSceneRigEditorModule::Get();
    
    UWorld* World = GetWorld();
    
    // 设置当前活跃的 Scene Rig
    FSoftObjectPath SceneRigPath(TEXT("/Game/MotionDesign/SceneRigs/BroadcastTemplate.BroadcastTemplate"));
    ULevelStreaming* StreamingLevel = SceneRigModule.SetActiveSceneRig(World, SceneRigPath);
    
    // 获取当前活跃的 Scene Rig 路径
    FSoftObjectPath ActiveRig = SceneRigModule.GetActiveSceneRig(World);
    
    // 检查某个 Actor 是否属于活跃 Scene Rig
    AActor* SomeActor = /* ... */;
    bool bIsPartOfRig = SceneRigModule.IsActiveSceneRigActor(World, SomeActor);
}
```

#### 进阶用法 — 监听 Scene Rig 变化事件

```cpp
// 来源: IAvaSceneRigEditorModule.h — 事件声明

// 监听 Scene Rig 切换
SceneRigModule.OnSceneRigChanged().AddLambda(
    [](UWorld* InWorld, ULevelStreaming* InNewSceneRig)
    {
        UE_LOG(LogTemp, Log, TEXT("Scene Rig changed in world: %s"), *InWorld->GetName());
        // 更新 UI 或重新配置管线...
    }
);

// 监听 Actor 加入 Scene Rig
SceneRigModule.OnSceneRigActorsAdded().AddLambda(
    [](UWorld* InWorld, const TArray<AActor*>& InAddedActors)
    {
        for (AActor* Actor : InAddedActors)
        {
            UE_LOG(LogTemp, Log, TEXT("Actor added to Scene Rig: %s"), *Actor->GetName());
        }
    }
);

// 监听 Actor 从 Scene Rig 移除
SceneRigModule.OnSceneRigActorsRemoved().AddLambda(
    [](UWorld* InWorld, const TArray<AActor*>& InRemovedActors)
    {
        // 清理相关资源...
    }
);
```

#### 批量操作 Scene Rig 中的 Actor

```cpp
// 将一组 Actor 加入活跃 Scene Rig
TArray<AActor*> ActorsToMove;
ActorsToMove.Add(Actor1);
ActorsToMove.Add(Actor2);
SceneRigModule.AddActiveSceneRigActors(World, ActorsToMove);

// 从活跃 Scene Rig 移除 Actor
SceneRigModule.RemoveActiveSceneRigActors(World, ActorsToMove);

// 移除世界中所有 Scene Rig
SceneRigModule.RemoveAllSceneRigs(World);

// 弹出对话框创建新 Scene Rig 资产
FSoftObjectPath NewRigPath = SceneRigModule.CreateSceneRigAssetWithDialog();
```

#### 编辑器命令注册（AvalancheSceneRigEditor 模块）

```cpp
// 来源: AvaSceneRigEditorCommands.h
// 注册自定义 Scene Rig 编辑器命令
FAvaSceneRigEditorCommands::Register();

const FAvaSceneRigEditorCommands& Commands = FAvaSceneRigEditorCommands::GetExternal();

// 可用命令:
// Commands.PromptToSaveSceneRigFromOutlinerItems — 从 Outliner 项保存为 Scene Rig
// Commands.AddOutlinerItemsToSceneRig            — 将 Outliner 项添加到 Scene Rig
// Commands.RemoveOutlinerItemsToSceneRig         — 从 Scene Rig 移除 Outliner 项
```

## 模块依赖

Motion Design 插件声明了以下外部插件依赖（来自 .uplugin Description）：

| 插件 | 用途 |
|---|---|
| Advanced Renamer | 高级批量重命名工具 |
| Custom Details View | 自定义 Details 面板视图 |
| Dynamic Material | 动态材质运行时修改 |
| Geometry Cache | 几何缓存支持 |
| Geometry Scripting | 几何脚本化操作 |
| Media Compositing | 媒体合成管线 |
| Media IO Framework | 媒体输入输出框架 |
| Mesh Modeling Toolset Exp | 网格建模工具集（实验性） |
| Remote Control | 远程控制 API |
| SVG Importer | SVG 文件导入 |
| Text3D | 3D 文本渲染 |
| ActorModifierCore | Actor 修改器核心框架 |

对于使用者的模块依赖，无特殊依赖（仅标准 Core/Engine/Slate 等），除非你需要直接操作 Scene Rig（需依赖 `AvalancheSceneRigEditor` 模块）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 的场景设置和 Outliner 选项卡迁移到独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用节目页设置时新增 MRQ 渲染分析数据收集 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏新增页面加载选项（全部/下一个/选中） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置强制禁用 3D 文本和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口关联/解除关联时的客户端通知逻辑 |

### 维护评价

**🟢 活跃维护中**

Motion Design 是 Epic Games 正在**积极开发的核心虚拟制片工具**：

- **更新频率**：每 2-5 天有功能性提交，处于高速迭代期
- **开发方向**：持续完善广播工作流（Rundown Page、MRQ 集成）、优化编辑器 UX（选项卡布局、碰撞设置）
- **成熟度**：2025 年 5 月从 Experimental 毕业迁移至 VirtualProduction 目录，已进入正式支持阶段
- **团队规模**：由 Epic 内部虚拟制片团队维护，有多位活跃贡献者
- **适用建议**：✅ **强烈推荐**用于虚拟制片和广播级动态图形工作流。该插件功能全面、迭代活跃，是 UE5 虚拟制作管线的重要组成部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/en-US/AnimatingObjects/MotionDesign/index.html)（虚幻引擎文档 — Motion Design 概述）
# Motion Design

> Compositing, designer and broadcasting tool.
> 
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具、媒体资源） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

---

## 用途

Motion Design（原名 Avalanche）是 UE5 中面向**虚拟制片和广播级实时图形**的综合设计工具集。它不是一个简单的功能插件，而是一个完整的**动态图形（Motion Graphics）制作环境**，整合了以下核心能力：

- **2D/3D 图形合成**：形状（AvalancheShapes）、文本（AvalancheText）、SVG 导入（AvalancheSVGEditor）等元素的创建与编排
- **属性动画**：通过 PropertyAnimator 和 Sequencer 集成，为任意 Actor 属性制作关键帧动画
- **克隆器与效应器**：通过 AvalancheEffectors 实现阵列克隆与程序化效果
- **材质设计**：AvalancheMaterial 提供专用的材质编辑工作流
- **遮罩系统**：AvalancheMask 提供几何遮罩和蒙版能力
- **场景管理**：SceneTree、SceneRig、Outliner 提供专业的场景层级管理
- **远程控制集成**：AvalancheRemoteControl 桥接 Remote Control 插件，支持通过 Web 界面或外部系统操控参数
- **媒体输出**：AvalancheMedia + AvalancheMRQ 支持媒体合成和 Movie Render Queue 输出
- **广播工作流**：支持 Rundown（节目单）管理、页面切换、演出控制工具栏

该插件最初在 `Engine/Plugins/Experimental/` 下开发，2025 年 5 月正式迁移至 `Engine/Plugins/VirtualProduction/`，标志着从实验性质升级为官方支持的虚拟制片核心工具。

## 使用场景

- 你在制作**电视/网络直播的实时动态图形**（新闻标题、体育比分、天气图表等）→ 使用 Motion Design 的全套图形元素和远程控制
- 你需要为**虚拟制片**（LED 墙、虚拟场景）创建可实时编辑的 2D/3D 动画 → 使用 Shapes、Text、Sequencer 集成
- 你要制作**广播级节目包装**（片头、过场、下三分之一字幕条）→ 使用 Transition、Effectors、SceneRig
- 你需要通过**外部控制台或 Web 界面**远程切换场景页面和参数 → 使用 AvalancheRemoteControl + Rundown
- 你要将设计内容渲染为**高质量视频文件** → 使用 AvalancheMRQ（Movie Render Queue 集成）

## 模块架构总览

Motion Design 采用高度模块化的架构，43 个模块按功能域划分：

```
Avalanche (根模块)
├── 核心层
│   ├── AvalancheCore          — 核心基础类和类型定义
│   ├── AvalancheEditorCore    — 编辑器核心工具和通用 UI
│   └── AvalancheTag           — 标签/标记系统
│
├── 图形元素
│   ├── AvalancheShapes        — 基础形状（矩形、圆形等）
│   ├── AvalancheText          — 文本元素
│   └── AvalancheSVGEditor     — SVG 导入支持
│
├── 动画与效果
│   ├── AvalanchePropertyAnimator — 属性动画引擎
│   ├── AvalancheSequencer      — Sequencer 深度集成
│   ├── AvalancheSequence       — 序列数据管理
│   ├── AvalancheTransition     — 过渡/转场效果
│   ├── AvalancheEffectors      — 克隆器与效应器
│   └── AvalancheModifiers      — Actor 修改器
│
├── 材质与遮罩
│   ├── AvalancheMaterial       — 动态材质设计
│   └── AvalancheMask           — 几何遮罩系统
│
├── 场景管理
│   ├── AvalancheSceneTree      — 场景树结构
│   ├── AvalancheSceneRig       — 场景装备/预设
│   ├── AvalancheOutliner       — 专用大纲视图
│   └── AvalancheCamera         — 摄像机管理
│
├── 媒体与输出
│   ├── AvalancheMedia          — 媒体合成运行时
│   ├── AvalancheMRQ            — Movie Render Queue 集成
│   └── AvalancheLevelViewport  — 关卡视口集成
│
├── 连接与控制
│   ├── AvalancheRemoteControl  — 远程控制桥接（本文档重点）
│   ├── AvalancheAttribute      — 属性系统
│   └── AvalancheTag            — 标签系统
│
└── 编辑器 UI（每个功能域均有对应的 *Editor 模块）
    ├── AvalancheEditor
    ├── AvalancheShapesEditor
    ├── AvalancheTextEditor
    ├── ... (共 15 个 Editor 模块)
```

---

# AvalancheRemoteControl 模块

本文档重点介绍 **AvalancheRemoteControl** 子模块——Motion Design 与 Remote Control 插件之间的桥接层。

## 用途

AvalancheRemoteControl 解决的核心问题是：**让 Motion Design 的场景参数能够通过 Remote Control 框架被外部系统（Web 界面、控制台、自定义应用程序）实时操控**。

具体职责：
1. **预设注册/注销**：将 Motion Design 嵌入关卡的 RemoteControlPreset 注册到 Remote Control 模块，使其对外可见
2. **绑定解析**：处理瞬态对象（Transient）的绑定，确保远程控制字段路径在关卡加载后能正确解析
3. **受控 Actor 查询**：提供查询某个远程控制器实际控制了哪些 Actor 的能力
4. **事件接口**：定义当远程控制值被应用时的回调接口

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetControlledActors` | 获取指定远程控制器实际控制的所有 Actor 列表 | `UAvaRCLibrary` |
| `OnValuesApplied` | 当远程控制值被应用时触发的事件（需要实现接口） | `IAvaRemoteControlInterface` |
| `FindController` | 在指定预设中根据名称查找远程控制器 | `FAvaRCControllerId` |

### 使用示例

**查询受控 Actor：**
1. 获取当前关卡中的 RemoteControlPreset 引用
2. 找到目标 RCVirtualPropertyBase 控制器
3. 调用 `GetControlledActors`（传入 World Context 和控制器对象）
4. 返回的 TArray\<AActor*\> 即为该控制器绑定的所有 Actor

**响应远程控制值变化：**
1. 在你的 Actor 类蓝图中，实现 `Motion Design Remote Control Interface` 接口
2. 覆写 `OnValuesApplied` 事件
3. 当远程控制值被 Web 界面或其他系统修改后，该事件自动触发

## C++ 用法

### 头文件引入

```cpp
#include "AvaRemoteControlUtils.h"
#include "AvaRemoteControlRebind.h"
#include "AvaRCLibrary.h"
#include "AvaRCControllerId.h"
#include "IAvaRemoteControlInterface.h"
```

### 基本用法：注册远程控制预设

```cpp
#include "AvaRemoteControlUtils.h"
#include "RemoteControlPreset.h"

// 注册一个 RemoteControlPreset，使其对外部系统可见（如 Web UI）
void RegisterMyPreset(URemoteControlPreset* InPreset)
{
    // bInEnsureUniqueId=true 确保注册时获得唯一 ID，避免与已注册的预设实例冲突
    bool bSuccess = FAvaRemoteControlUtils::RegisterRemoteControlPreset(InPreset, true);
    
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Remote Control Preset registered successfully."));
    }
}

// 当不再需要时注销预设
void UnregisterMyPreset(URemoteControlPreset* InPreset)
{
    FAvaRemoteControlUtils::UnregisterRemoteControlPreset(InPreset);
}

// 在关卡中查找嵌入的 RemoteControlPreset
URemoteControlPreset* FindPresetInLevel(ULevel* InLevel)
{
    // 仅查找已注册的预设；未注册的预设（即使 Outer 是该关卡）不会被找到
    return FAvaRemoteControlUtils::FindEmbeddedPresetInLevel(InLevel);
}
```

### 进阶用法：重新绑定与事件响应

```cpp
#include "AvaRemoteControlRebind.h"
#include "RemoteControlPreset.h"
#include "RCVirtualPropertyBase.h"

// 在关卡加载后重新绑定未解析的远程控制实体
// 这对瞬态对象（Transient Objects）特别重要——它们在序列化时无法被绑定
void RebindAfterLevelLoad(URemoteControlPreset* InPreset, ULevel* InLevel)
{
    // 第一步：重新绑定未解析的实体，允许瞬态对象参与绑定
    FAvaRemoteControlRebind::RebindUnboundEntities(InPreset, InLevel);
    
    // 第二步：确保所有 FieldPathInfo 被正确解析（必须在 Rebind 之后调用）
    FAvaRemoteControlRebind::ResolveAllFieldPathInfos(InPreset);
}

// 使用控制器 ID 查找控制器
void FindControllerByName(URemoteControlPreset* InPreset)
{
    FAvaRCControllerId ControllerId;
    ControllerId.Name = FName(TEXT("MyController"));
    
    URCVirtualPropertyBase* Controller = ControllerId.FindController(InPreset);
    if (Controller)
    {
        FText DisplayText = ControllerId.ToText();
        UE_LOG(LogTemp, Log, TEXT("Found controller: %s"), *DisplayText.ToString());
    }
}
```

## Demo 示例

```cpp
// MyRemoteControlledActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IAvaRemoteControlInterface.h"
#include "MyRemoteControlledActor.generated.h"

UCLASS()
class AMyRemoteControlledActor : public AActor, public IAvaRemoteControlInterface
{
    GENERATED_BODY()

public:
    AMyRemoteControlledActor();

    // 实现 Motion Design Remote Control Interface
    virtual void OnValuesApplied_Implementation() override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Display")
    FText DisplayText;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Display")
    FLinearColor TextColor;
};
```

```cpp
// MyRemoteControlledActor.cpp
#include "MyRemoteControlledActor.h"
#include "AvaRemoteControlUtils.h"
#include "RemoteControlPreset.h"

AMyRemoteControlledActor::AMyRemoteControlledActor()
{
    PrimaryActorTick.bCanEverTick = false;
    DisplayText = FText::FromString(TEXT("Hello Motion Design"));
    TextColor = FLinearColor::White;
}

void AMyRemoteControlledActor::OnValuesApplied_Implementation()
{
    // 远程控制值被应用后执行自定义逻辑
    // 例如：更新 UI、触发动画、发送网络消息等
    UE_LOG(LogTemp, Log, TEXT("Remote control values applied! Text: %s"), *DisplayText.ToString());
    
    // 在这里可以访问 DisplayText 和 TextColor，
    // 它们可能已经被远程控制系统修改
}
```

## 模块依赖

从 Build.cs 分析，AvalancheRemoteControl 的独特依赖：

| 模块 | 用途 |
|---|---|
| `RemoteControl` | Remote Control 核心框架，提供 Preset、VirtualProperty 等基础类型 |
| `RemoteControlAPI` | Remote Control 的 API 层，提供实体绑定和字段路径解析 |
| `AvalancheCore` | Motion Design 核心模块，提供基础类型和工具 |

无特殊依赖（仅标准 Core/Engine/Slate 等）——以上为该模块独特的依赖项。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 的场景设置和大纲标签页移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为节目单页面设置添加 Movie Render Queue 分析统计 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在演出控制工具栏中添加页面加载选项（全部/下一个/选中） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加项目设置以强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/断开的通知机制 |

### 维护评价

- **创建时间**：2025-05-09，从 Experimental 迁移至 VirtualProduction
- **最近更新频率**：**非常活跃**——截至 2026 年 5 月仍有持续的功能性更新（每周多次提交）
- **更新内容**：涵盖功能新增（MRQ 分析、页面加载选项）、UI 优化（标签页分组）、项目设置扩展、底层重构等
- **已知限制**：该插件依赖多个外部插件（Remote Control、Text3D、Geometry Scripting 等），启用前需确保所有依赖已就绪
- **推荐使用**：✅ **强烈推荐**用于虚拟制片和广播级实时图形制作。该插件由 Epic Games 官方维护，持续获得实质性更新，且已从实验阶段毕业为正式虚拟制片工具

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [源码 (AvalancheRemoteControl)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheRemoteControl)
- [Remote Control 插件文档](https://docs.unrealengine.com/en-US/remote-control-in-unreal-engine/)
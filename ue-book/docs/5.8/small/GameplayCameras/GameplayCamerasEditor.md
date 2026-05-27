# Gameplay Cameras

> A modular and data-driven camera system for Unreal

| 属性 | 值 |
|---|---|
| 中文名 | 游戏相机系统 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具、图表系统） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

---

## 文档结构

本文档为 **xlarge** 规模插件（729 源文件），按子模块拆分为以下文档：

| 文档 | 内容 |
|---|---|
| **[index.md](index.md)** (本页) | 总览、用途、使用场景、蓝图用法、C++ 用法、维护状态 |
| [CoreRuntime.md](CoreRuntime.md) | 核心运行时：相机资产、相机钻机、相机节点、相机变量、相机摇晃、过渡系统 |
| [ObjectTreeGraph.md](ObjectTreeGraph.md) | 对象树图表框架：通用数据驱动可视化图表编辑器基础设施 |
| [EditorToolkits.md](EditorToolkits.md) | 编辑器工具包：资产编辑器、模式管理、搜索、工具箱、曲线编辑器 |
| [CustomizationsAndSequencer.md](CustomizationsAndSequencer.md) | 属性自定义、细节面板、Sequencer 集成、调试器 |

---

## 用途

GameplayCameras 是 UE5 中**下一代模块化相机系统**，旨在替代传统的 `UCameraShake` 和 `UCameraComponent` 体系。它提供了一套**数据驱动**的可视化节点编辑器，让设计师和开发者能够通过连接节点来定义复杂的相机行为，而不是编写硬编码的 C++ 逻辑。

**核心解决的问题**：

- **相机行为的可视化编辑**：传统相机逻辑分散在多个 C++ 类和蓝图中，难以维护和理解。GameplayCameras 通过**对象树图表（Object Tree Graph）** 让相机行为以节点图的方式呈现
- **模块化相机组合**：通过"相机钻机（Camera Rig）"概念，将相机行为封装为可重用、可嵌套的资产
- **运行时动态过渡**：内建过渡（Transition）图系统，支持相机钻机之间的条件切换和混合
- **相机变量系统**：类似蓝图变量，但专为相机参数设计，支持在运行时动态读写
- **编辑器内实时预览**：LiveEdit 系统支持在编辑器中实时预览相机效果

**为什么存在**：

Epic 在 UE5 开发中意识到现有的相机系统缺乏足够的灵活性和可维护性，尤其是在复杂游戏（如 Fortnite、竞技游戏）中需要频繁迭代相机设计。GameplayCameras 作为 Epic 内部开发的实验性系统，目标是成为 UE5 的标准相机解决方案。

---

## 使用场景

- **你需要设计复杂的第三人称相机**：用 Camera Rig 节点图定义跟踪逻辑、弹簧臂、碰撞检测等
- **你的游戏需要多种相机状态切换**：用过渡（Transition）系统定义进入/退出条件
- **你需要设计师可以独立调整相机参数**：用 Camera Variable 让设计师在编辑器中调整参数而不改代码
- **你需要相机摇晃效果与动画混合**：用 Camera Shake Asset 定义可数据驱动的抖动效果
- **你需要 Sequencer 中控制相机**：插件集成了 Sequencer 轨道编辑器，支持对相机参数做关键帧动画
- **你在做竞技/MOBA 类游戏**：需要多角色、多视角的灵活相机控制

---

## 蓝图用法

### 核心节点

GameplayCameras 的运行时模块提供了以下核心蓝图 API：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateCameraAssetEditor` | 创建相机资产编辑器 | `IGameplayCamerasEditorModule` |
| `CreateCameraRigEditor` | 创建相机钻机编辑器 | `IGameplayCamerasEditorModule` |
| `CreateCameraShakeEditor` | 创建相机摇晃编辑器 | `IGameplayCamerasEditorModule` |
| `CreateCameraVariableCollectionEditor` | 创建相机变量集合编辑器 | `IGameplayCamerasEditorModule` |
| `CreateCameraVariablePicker` | 创建相机变量选择器控件 | `IGameplayCamerasEditorModule` |
| `RegisterDebugCategory` | 注册自定义调试类别 | `IGameplayCamerasEditorModule` |

> **注意**：当前 GameplayCameras 的蓝图 API 主要面向**编辑器扩展**。运行时核心逻辑通过 Camera Rig 资产以数据驱动方式执行，不需要手动调用蓝图节点。相机组件（GameplayCameraComponent）在蓝图中挂载后，其行为完全由 Camera Asset 节点图定义。

### 使用示例（编辑器扩展蓝图）

要创建自定义编辑器工具，可以获取 `IGameplayCamerasEditorModule` 接口：

1. 获取编辑器模块实例：`IGameplayCamerasEditorModule::Get()`
2. 注册自定义相机导演编辑器：调用 `RegisterCameraDirectorEditor` 传入创建委托
3. 注册调试类别：调用 `RegisterDebugCategory` 并提供 `FCameraDebugCategoryInfo`

---

## C++ 用法

### 头文件引入

```cpp
// 编辑器模块接口
#include "IGameplayCamerasEditorModule.h"

// 对象树图表框架
#include "ObjectTreeGraphConfig.h"
#include "ObjectTreeGraphSchema.h"
#include "ObjectTreeGraphNode.h"

// 编辑器工具包
#include "CameraRigAssetEditorToolkitBase.h"
#include "CameraAssetEditorToolkit.h"
#include "AssetEditorModeManagerToolkit.h"
```

### 基本用法：注册自定义调试类别

```cpp
#include "IGameplayCamerasEditorModule.h"

// 在你的编辑器模块启动时注册调试类别
void FMyEditorModule::StartupModule()
{
    UE::Cameras::FCameraDebugCategoryInfo CategoryInfo;
    CategoryInfo.Name = TEXT("MyCustomCategory");
    CategoryInfo.DisplayText = NSLOCTEXT("MyModule", "DebugCategory", "My Custom Debug");
    CategoryInfo.ToolTipText = NSLOCTEXT("MyModule", "DebugTooltip", "Shows custom debug info");
    CategoryInfo.IconImage = FSlateIcon(FAppStyle::GetAppStyleSetName(), "ClassIcon.Actor");
    
    IGameplayCamerasEditorModule& EditorModule = IGameplayCamerasEditorModule::Get();
    EditorModule.RegisterDebugCategory(CategoryInfo);
}
```

### 基本用法：注册自定义相机导演编辑器

```cpp
#include "IGameplayCamerasEditorModule.h"

// 注册自定义的相机导演编辑模式
void FMyEditorModule::RegisterCameraDirectorEditor()
{
    IGameplayCamerasEditorModule& EditorModule = IGameplayCamerasEditorModule::Get();
    
    CameraDirectorDelegateHandle = EditorModule.RegisterCameraDirectorEditor(
        FOnCreateCameraDirectorAssetEditorMode::CreateLambda(
            [](UCameraAsset* CameraAsset) -> TSharedPtr<UE::Cameras::FCameraDirectorAssetEditorMode>
            {
                // 创建自定义导演编辑器模式
                return MakeShared<FMyCameraDirectorAssetEditorMode>(CameraAsset);
            }
        )
    );
}
```

### 进阶用法：使用对象树图表系统

对象树图表是 GameplayCameras 的核心编辑器基础设施，用于将 UObject 对象以节点图的形式可视化编辑：

```cpp
#include "ObjectTreeGraphConfig.h"

// 配置一个对象树图表
void SetupCameraGraphConfig(FObjectTreeGraphConfig& GraphConfig)
{
    // 设置图表名称
    GraphConfig.GraphName = FName("CameraRigGraph");
    
    // 注册可连接的对象类（这些类的实例将成为图表中的节点）
    GraphConfig.ConnectableObjectClasses.Add(UMyCameraNode::StaticClass());
    GraphConfig.ConnectableObjectClasses.Add(UMyBlendNode::StaticClass());
    
    // 排除某些类（不作为节点显示）
    GraphConfig.NonConnectableObjectClasses.Add(UMyInternalNode::StaticClass());
    
    // 设置默认节点外观
    GraphConfig.DefaultGraphNodeTitleColor = FLinearColor(0.1f, 0.2f, 0.3f);
    
    // 设置自定义显示名称格式化
    GraphConfig.OnFormatObjectDisplayName = FOnFormatObjectDisplayName::CreateLambda(
        [](const UObject* InObject, FText& InOutName)
        {
            InOutName = FText::FromString(InObject->GetName().Replace(TEXT("CameraNode_"), TEXT("")));
        }
    );
    
    // 配置特定类的图表节点外观
    FObjectTreeGraphClassConfig BlendNodeConfig;
    BlendNodeConfig.NodeTitleColor(FLinearColor(0.8f, 0.4f, 0.1f));
    BlendNodeConfig.CanCreateNew(true).CanDelete(true);
    BlendNodeConfig.StripDisplayNameSuffix(TEXT("BlendNode"));
    GraphConfig.ObjectClassConfigs.Add(UMyBlendNode::StaticClass(), BlendNodeConfig);
}
```

### 进阶用法：使用 LiveEdit 管理器

```cpp
#include "GameplayCamerasLiveEditManager.h"

// 实现 IGameplayCamerasLiveEditListener 接口
class FMyLiveEditListener : public UE::Cameras::IGameplayCamerasLiveEditListener
{
public:
    virtual void OnPostBuildAsset(const UPackage* AssetPackage) override
    {
        // 相机资产被重新构建时触发
        UE_LOG(LogTemp, Log, TEXT("Camera asset rebuilt: %s"), *AssetPackage->GetName());
    }
    
    virtual void OnPostEditChangeProperty(const UCameraNode* CameraNode, 
        const FPropertyChangedEvent& PropertyChangedEvent) override
    {
        // 相机节点属性被修改时触发
        UE_LOG(LogTemp, Log, TEXT("Camera node property changed"));
    }
};

// 注册监听器
void RegisterLiveEditListener(IGameplayCamerasLiveEditManager* LiveEditManager, 
    const UPackage* Package, FMyLiveEditListener* Listener)
{
    LiveEditManager->AddListener(Package, Listener);
}
```

---

## 模块依赖

### GameplayCameras (Runtime)

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 增强输入系统集成 |
| `CommonUI` | 通用 UI 框架 |
| `GameplayTags` | Gameplay Tag 系统 |
| `MovieScene`, `MovieSceneTracks` | Sequencer 集成 |

### GameplayCamerasEditor (Runtime)

| 模块 | 用途 |
|---|---|
| `GameplayCameras` | 核心运行时模块 |
| `SequencerCore` | Sequencer 核心 |
| `ToolWidgets` | 编辑器工具控件 |
| `WorkspaceMenuStructure` | 工作区菜单结构 |
| `TraceAnalysis`, `TraceServices` | 追踪分析（用于相机调试器） |

### GameplayCamerasUncookedOnly (Runtime)

无特殊依赖（仅标准 Core/Engine/Slate 等）。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复 PIE 模式下相机变量覆盖不生效的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 更新部分追踪通道的描述信息 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | GameplayCameras 常规更新（具体改动未详述） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版 UE_LOG 迁移到新版 UE_LOGF 宏 |

### 维护评价

**活跃维护** ★★★★★

GameplayCameras 是 Epic 正在积极开发的下一代相机系统：

- **创建于 2020 年**，作为 UE5 实验性功能引入，至今已有约 6 年历史
- **最近 1 个月内有多次更新**（2026 年 4-5 月），包括 bug 修复、编译警告清理、追踪系统完善
- **标记为实验性**（`IsExperimentalVersion=true`），说明 Epic 仍在迭代，但接口可能变化
- **代码量庞大**（729 源文件），表明这是一个成熟且功能丰富的系统
- **Epic 官方维护**，由 Epic Games 直接开发，有长期维护保障
- **推荐使用**：如果你的项目需要复杂的相机系统，强烈建议使用。但需注意它是实验性功能，API 可能在未来版本变化。在正式项目中建议密切关注版本更新日志

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [官方文档]()（暂无）

---

## 子文档

- **[CoreRuntime.md](CoreRuntime.md)** — 核心运行时系统：相机资产、钻机、节点、变量、摇晃、过渡
- **[ObjectTreeGraph.md](ObjectTreeGraph.md)** — 对象树图表框架：通用可视化节点编辑器基础设施
- **[EditorToolkits.md](EditorToolkits.md)** — 编辑器工具包：资产编辑器、模式管理、搜索、工具箱
- **[CustomizationsAndSequencer.md](CustomizationsAndSequencer.md)** — 属性自定义、Sequencer 集成、调试器
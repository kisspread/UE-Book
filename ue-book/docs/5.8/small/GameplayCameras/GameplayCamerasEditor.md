# Gameplay Cameras

> A modular and data-driven camera system for Unreal

| 属性 | 值 |
|---|---|
| 中文名 | 数据驱动相机 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（相机资产类型定义） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Editor), `GameplayCamerasUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 是一套**模块化、数据驱动**的相机系统，旨在取代传统基于蓝图/代码硬编码的相机行为方式。它通过**节点图（Node Graph）**的方式，让策划和开发者以可视化方式构建相机行为逻辑，而无需编写代码。

该插件的核心设计理念：

1. **数据驱动**：相机行为以资产（Asset）形式保存，可以在编辑器中可视化编辑，支持运行时热重载
2. **模块化**：相机行为由可复用的 Camera Rig（相机组件）组合而成，支持嵌套和参数化
3. **可覆盖的参数系统**：通过 Camera Variable 机制，支持在不同层级覆盖相机参数（例如关卡级别覆盖角色级别）
4. **过渡系统**：内置相机状态间的过渡逻辑（Transitions），支持条件驱动的自动切换
5. **内置相机震动（Shake）**：以数据资产形式定义震动效果，无需 C++ 或蓝图

该插件解决的核心问题是：传统 UE 相机系统（如 `UCameraComponent` + `USpringArmComponent`）在复杂项目中容易变得难以维护——多个系统竞争控制相机、逻辑分散在各处。GameplayCameras 通过统一的资产编辑器将所有相机逻辑集中管理。

## 使用场景

- 你在一个**第三人称动作游戏**中需要复杂的相机行为（战斗相机、探索相机、过场相机等不同模式的切换）→ 用 GameplayCameras 的 Camera Asset + Camera Rig + Transitions 系统
- 你需要**让策划独立调整相机参数**而不修改代码 → 用数据驱动的 Camera Variable 和参数覆盖系统
- 你需要**可复用的相机模板**（如所有近战敌人的攻击特写相机） → 将相机逻辑封装为 Camera Rig Asset
- 你需要**复杂的相机震动效果**（屏幕震动、FOV 变化、颜色偏移组合）→ 用 Camera Shake Asset
- 你希望相机在编辑器中即可**实时预览**而无需运行游戏 → 使用 Live Edit 功能

## 蓝图用法

### 核心资产类型

| 资产类型 | 说明 |
|---|---|
| `UCameraAsset` | 主相机资产，包含完整的相机行为定义（节点图 + 导演逻辑） |
| `UCameraRigAsset` | 可复用的相机组件，定义具体的相机行为（如跟随、固定、轨道等） |
| `UCameraShakeAsset` | 数据驱动的相机震动资产 |
| `UCameraRigProxyAsset` | Camera Rig 的代理资产，用于间接引用 |
| `UCameraVariableCollection` | 相机变量集合，管理共享的可覆盖参数 |
| `UCameraVariableAsset` | 单个相机变量，支持多种值类型（Float、Vector、Rotator 等） |

### 编辑器 API（C++ 模块接口）

由于 GameplayCameras 的核心运行时 API 在 `GameplayCameras` 模块中（本次分析聚焦于 `GameplayCamerasEditor` 模块），蓝图可调用的节点主要通过运行时模块暴露。编辑器模块提供的核心接口用于：

| 接口 | 说明 |
|---|---|
| `IGameplayCamerasEditorModule::CreateCameraAssetEditor()` | 打开相机资产编辑器 |
| `IGameplayCamerasEditorModule::CreateCameraRigEditor()` | 打开相机 Rig 编辑器 |
| `IGameplayCamerasEditorModule::CreateCameraShakeEditor()` | 打开相机震动编辑器 |
| `IGameplayCamerasEditorModule::CreateCameraVariableCollectionEditor()` | 打开变量集合编辑器 |
| `IGameplayCamerasEditorModule::CreateCameraVariablePicker()` | 创建变量选择器控件 |
| `IGameplayCamerasEditorModule::RegisterDebugCategory()` | 注册自定义调试类别 |

## C++ 用法

### 头文件引入

```cpp
// 运行时模块
#include "GameplayCamerasModule.h"

// 编辑器模块（仅在编辑器中可用）
#include "IGameplayCamerasEditorModule.h"
```

### 基本用法 - 打开资产编辑器

通过编辑器模块接口创建和打开各类相机资产编辑器。

```cpp
// 打开一个 Camera Rig 编辑器
#include "IGameplayCamerasEditorModule.h"

void OpenCameraRigEditor(UCameraRigAsset* CameraRig)
{
    IGameplayCamerasEditorModule& EditorModule = IGameplayCamerasEditorModule::Get();
    EditorModule.CreateCameraRigEditor(
        EToolkitMode::Standalone,
        TSharedPtr<IToolkitHost>(),
        CameraRig
    );
}
```

### 进阶用法 - 注册自定义相机导演编辑器和调试类别

```cpp
// 注册自定义相机导演的编辑器模式
#include "IGameplayCamerasEditorModule.h"

void RegisterCustomDirectorEditor()
{
    IGameplayCamerasEditorModule& EditorModule = IGameplayCamerasEditorModule::Get();
    
    FOnCreateCameraDirectorAssetEditorMode CreateMode;
    CreateMode.BindLambda([](UCameraAsset* CameraAsset) -> TSharedPtr<FCameraDirectorAssetEditorMode>
    {
        // 创建自定义的导演编辑器模式
        return MakeShared<FMyCustomDirectorEditorMode>(CameraAsset);
    });
    
    EditorModule.RegisterCameraDirectorEditor(CreateMode);
}

// 注册自定义调试类别
void RegisterCustomDebugCategory()
{
    IGameplayCamerasEditorModule& EditorModule = IGameplayCamerasEditorModule::Get();
    
    FCameraDebugCategoryInfo CategoryInfo;
    CategoryInfo.Name = TEXT("MyCustomCategory");
    CategoryInfo.DisplayText = NSLOCTEXT("MyModule", "DebugCat", "自定义类别");
    CategoryInfo.ToolTipText = NSLOCTEXT("MyModule", "DebugTooltip", "显示自定义相机调试信息");
    CategoryInfo.IconImage = FSlateIcon(FAppStyle::GetAppStyleSetName(), "ClassIcon.Actor");
    
    EditorModule.RegisterDebugCategory(CategoryInfo);
    
    // 注册自定义面板
    EditorModule.RegisterDebugCategoryPanel(
        TEXT("MyCustomCategory"),
        FOnCreateDebugCategoryPanel::CreateLambda([](const FString& CategoryName) -> TSharedRef<SWidget>
        {
            return SNew(STextBlock).Text(FText::FromString(TEXT("自定义调试面板")));
        })
    );
}
```

## 编辑器架构概览

该插件的编辑器模块实现了完整的资产编辑工作流：

### 节点图系统（ObjectTreeGraph）

整个相机编辑器基于通用的 **ObjectTreeGraph** 图形编辑框架：

| 类 | 说明 |
|---|---|
| `UObjectTreeGraph` | 图数据对象，管理节点和连接 |
| `UObjectTreeGraphNode` | 图节点，每个节点对应一个 UObject 实例 |
| `UObjectTreeGraphSchema` | 图的连接规则和行为定义 |
| `FObjectTreeGraphConfig` | 图的配置（可连接类、节点样式、显示名称等） |
| `SObjectTreeGraphEditor` | 图编辑器 Slate 控件 |
| `SObjectTreeGraphToolbox` | 节点工具箱，列出所有可创建的节点类型 |

### 专用图 Schema

| Schema 类 | 用途 |
|---|---|
| `UCameraObjectGraphSchemaBase` | 所有相机节点图的基础 Schema，定义了相机参数 Pin、变量引用 Pin、上下文数据 Pin 等类型 |
| `UCameraRigTransitionGraphSchemaBase` | 相机过渡图的 Schema |

### 编辑器 Toolkit

| Toolkit 类 | 管理的资产 |
|---|---|
| `FCameraAssetEditorToolkit` | `UCameraAsset` 编辑器（支持多模式切换） |
| `FCameraRigAssetEditorToolkitBase` | `UCameraRigAsset` 编辑器（节点图 + 过渡图） |
| `FCameraShakeAssetEditorToolkit` | `UCameraShakeAsset` 编辑器 |
| `FCameraRigTransitionEditorToolkitBase` | 相机过渡逻辑编辑器 |
| `FCameraVariableCollectionEditorToolkit` | 相机变量集合编辑器 |
| `FAssetEditorModeManagerToolkit` | 支持多编辑模式切换的通用编辑器基类 |

### 细节面板自定义

| 自定义类 | 说明 |
|---|---|
| `FCameraParameterDetailsCustomization` | 相机参数的属性编辑器，支持变量浏览器和覆盖切换 |
| `FCameraVariableReferenceDetailsCustomization` | 相机变量引用的属性编辑器 |
| `TCameraObjectInterfaceParameterOverrideDataDetails<>` | 接口参数覆盖数据的属性编辑器模板 |
| `FCameraObjectInterfaceParameterDetailsCustomization` | 相机对象接口参数的属性编辑器 |
| `FRichCurveDetailsCustomization` | 富曲线的属性编辑器，内嵌曲线编辑器视口 |

## 模块依赖

该插件依赖 `EnhancedInput` 插件（在 .uplugin 中声明）。编辑器模块额外依赖标准的编辑器框架模块。

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 增强输入系统，用于相机输入绑定 |
| `ObjectTreeGraph` | 通用对象树图编辑框架（被相机节点图系统使用） |

> 编辑器模块额外依赖 UnrealEd、PropertyEditor、EditorStyle 等标准编辑器模块（已省略）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复 PIE 模式下相机变量覆盖不生效的 bug |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的 double-to-float 截断警告 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 补充和更新追踪通道的描述信息 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | 通用更新（commit message 为模块名） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 格式化日志 |

### 维护评价

**活跃维护中**。该插件虽然已存在约 6 年，但近期（2026年4-5月）仍有持续的功能修复和代码质量改进。最近的更新涵盖了：

- **功能性 bug 修复**（PIE 中相机变量覆盖失效）
- **编译器警告修复**（严格浮点模式兼容）
- **代码现代化**（UE_LOG → UE_LOGF 迁移）
- **文档/追踪改进**（trace channel 描述）

**值得注意**：该插件至今仍标记为 `IsExperimentalVersion=true`（实验性），这意味着：
- API 可能在未来版本中发生变化
- 不建议在生产环境中完全依赖该系统，除非你准备好跟踪 API 变化
- 但持续 6 年的维护和 Epic Games 官方维护说明其重要性

**推荐使用**：如果你的项目需要复杂的、可配置的相机系统，且团队能够接受实验性 API 的潜在变化风险，GameplayCameras 是一个强大的选择。它的数据驱动设计特别适合策划团队独立调整相机行为。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)